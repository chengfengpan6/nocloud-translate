import os
import re
import threading
import time
from typing import Callable, Iterable, List

import torch
from huggingface_hub.utils import logging as hf_logging
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from transformers.utils import logging as transformers_logging


os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
hf_logging.set_verbosity_error()
transformers_logging.set_verbosity_error()
transformers_logging.disable_progress_bar()


MODEL_NAME = "facebook/nllb-200-distilled-600M"

LANGUAGE_CODES = {
    "english": "eng_Latn",
    "simplified_chinese": "zho_Hans",
    "traditional_chinese": "zho_Hant",
    "filipino_tagalog": "tgl_Latn",
}


class NllbTranslator:
    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self._cache = {}
        self._lock = threading.Lock()

    @staticmethod
    def cuda_available() -> bool:
        return bool(torch.cuda.is_available())

    def load_model(self, device_mode: str):
        normalized_mode = (device_mode or "").lower()
        if normalized_mode not in {"cpu", "gpu"}:
            raise ValueError("Please choose CPU or GPU mode.")

        if normalized_mode == "gpu" and not self.cuda_available():
            raise RuntimeError("CUDA GPU is not available. Please choose CPU mode.")

        device = "cuda" if normalized_mode == "gpu" else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32
        cache_key = (self.model_name, device, str(dtype))

        with self._lock:
            cached = self._cache.get(cache_key)
            if cached is not None:
                return cached

            tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name, dtype=dtype)
            model.generation_config.max_length = None
            model.to(device)
            model.eval()
            self._cache[cache_key] = (tokenizer, model, device)
            return self._cache[cache_key]

    def translate_chunks(
        self,
        chunks: Iterable[str],
        source_lang: str,
        target_lang: str,
        device_mode: str,
        progress_callback: Callable[[int, int, float], None] | None = None,
    ) -> List[str]:
        tokenizer, model, device = self.load_model(device_mode)
        tokenizer.src_lang = source_lang
        forced_bos_token_id = tokenizer.convert_tokens_to_ids(target_lang)
        if forced_bos_token_id is None or forced_bos_token_id == tokenizer.unk_token_id:
            raise ValueError(f"Unsupported target language code: {target_lang}")

        chunk_list = list(chunks)
        total = len(chunk_list)
        start_time = time.time()
        translated: List[str] = []

        for index, chunk in enumerate(chunk_list, start=1):
            if not chunk.strip():
                translated.append("")
                if progress_callback:
                    progress_callback(index, total, time.time() - start_time)
                continue

            inputs = tokenizer(chunk, return_tensors="pt", truncation=True, max_length=512)
            inputs = {key: value.to(device) for key, value in inputs.items()}

            with torch.inference_mode():
                output_tokens = model.generate(
                    **inputs,
                    forced_bos_token_id=forced_bos_token_id,
                    max_new_tokens=512,
                    num_beams=4,
                )

            translated.append(tokenizer.batch_decode(output_tokens, skip_special_tokens=True)[0])

            if progress_callback:
                progress_callback(index, total, time.time() - start_time)

        return translated


_CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
_ASCII_LETTER_RE = re.compile(r"[A-Za-z]")


def detect_language_simple(text: str) -> str | None:
    sample = (text or "")[:5000]
    meaningful = [char for char in sample if not char.isspace()]
    if not meaningful:
        return None

    cjk_count = len(_CJK_RE.findall(sample))
    ascii_count = len(_ASCII_LETTER_RE.findall(sample))
    total = max(1, len(meaningful))

    if cjk_count / total > 0.2:
        return LANGUAGE_CODES["simplified_chinese"]

    if ascii_count / total > 0.55:
        return LANGUAGE_CODES["english"]

    return None
