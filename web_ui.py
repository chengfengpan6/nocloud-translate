import html
import os
import time
import traceback
from pathlib import Path

import gradio as gr

from document_io import has_meaningful_text, read_document, validate_file_extension, write_translated_document
from text_splitter import reconstruct_blocks, split_text_blocks
from translator import LANGUAGE_CODES, NllbTranslator, detect_language_simple


APP_TITLE = "NoCloud Translate"
DEFAULT_UI_LANGUAGE = "ENG"
DEFAULT_PREFS = {
    "ui_language": "ENG",
    "runtime": "cpu",
    "source_language": "auto",
    "target_language": "simplified_chinese",
}

LANGUAGE_OPTIONS = {
    "auto": {"code": None, "en": "Auto Detect", "zh": "自动检测"},
    "english": {"code": LANGUAGE_CODES["english"], "en": "English", "zh": "English"},
    "simplified_chinese": {"code": LANGUAGE_CODES["simplified_chinese"], "en": "Simplified Chinese", "zh": "简体中文"},
    "traditional_chinese": {"code": LANGUAGE_CODES["traditional_chinese"], "en": "Traditional Chinese", "zh": "繁体中文"},
    "filipino_tagalog": {"code": LANGUAGE_CODES["filipino_tagalog"], "en": "Filipino / Tagalog", "zh": "菲律宾语 / Tagalog"},
}

TARGET_LANGUAGE_KEYS = ["english", "simplified_chinese", "traditional_chinese", "filipino_tagalog"]
SOURCE_LANGUAGE_KEYS = ["auto", *TARGET_LANGUAGE_KEYS]

TEXTS = {
    "ENG": {
        "title": "## NoCloud Translate",
        "intro": "Private, GPU-ready document translation on your laptop. Upload TXT, MD, or DOCX, choose CPU or GPU, then translate locally with NLLB.",
        "ui_language": "Interface",
        "runtime_label": "Runtime Mode",
        "runtime_info": "Choose CPU for compatibility or GPU for NVIDIA CUDA acceleration. CPU remains available even when CUDA is detected.",
        "cpu_option": "CPU",
        "gpu_option": "GPU",
        "runtime_status": "Runtime Status",
        "active": "Active",
        "inactive": "Inactive",
        "cuda_detected": "CUDA GPU detected",
        "cuda_missing": "No CUDA GPU detected",
        "selected_runtime": "Selected runtime: {runtime}.",
        "gpu_unavailable": "GPU selected, but CUDA is not available. Please choose CPU mode.",
        "file_label": "Upload document",
        "file_hint": "Supported formats: TXT, MD, DOCX",
        "source_label": "Source language",
        "target_label": "Target language",
        "start": "Start Translation",
        "progress_title": "Translation Status",
        "idle": "Waiting to start translation...",
        "missing_file": "Please upload a document first.",
        "unsupported": "Unsupported File Format. Click OK to upload again.",
        "empty_document": "The uploaded document is empty.",
        "manual_source_needed": "Auto Detect could not identify the source language. Please choose the source language manually.",
        "same_language": "Source and target languages are the same. Please choose a different target language.",
        "reading": "Reading document{dots}",
        "loading": "Loading local NLLB model on {runtime}{dots}",
        "translating": "Translating chunk {current} / {total}. Elapsed time: {elapsed}{dots}",
        "writing": "Saving translated document{dots}",
        "done": "Translation complete. Elapsed time: {elapsed}.",
        "error": "Translation failed: {message}",
        "preview_label": "Translated Text Preview",
        "download_label": "⬇ Download Translated Document",
        "ok": "OK",
        "chunk_count": "Prepared {count} chunks from {blocks} document blocks.",
    },
    "中文": {
        "title": "## NoCloud Translate",
        "intro": "在你的笔记本本地运行、支持 GPU 的私有文档翻译工具。上传 TXT、MD 或 DOCX，选择 CPU 或 GPU，然后使用 NLLB 本地翻译。",
        "ui_language": "界面语言",
        "runtime_label": "运行模式",
        "runtime_info": "CPU 适合兼容模式；GPU 使用 NVIDIA CUDA 加速。即使检测到 CUDA，也可以手动选择 CPU。",
        "cpu_option": "CPU",
        "gpu_option": "GPU",
        "runtime_status": "运行状态",
        "active": "已选择",
        "inactive": "未选择",
        "cuda_detected": "已检测到 CUDA GPU",
        "cuda_missing": "未检测到 CUDA GPU",
        "selected_runtime": "当前选择：{runtime}。",
        "gpu_unavailable": "当前选择 GPU，但 CUDA 不可用。请改选 CPU 模式。",
        "file_label": "上传文档",
        "file_hint": "支持格式：TXT, MD, DOCX",
        "source_label": "源语言",
        "target_label": "目标语言",
        "start": "开始翻译",
        "progress_title": "翻译状态",
        "idle": "等待开始翻译...",
        "missing_file": "请先上传文档。",
        "unsupported": "Unsupported File Format. Click OK to upload again.",
        "empty_document": "上传的文档是空的。",
        "manual_source_needed": "自动检测暂时无法判断源语言，请手动选择源语言。",
        "same_language": "源语言和目标语言相同，请选择不同的目标语言。",
        "reading": "正在读取文档{dots}",
        "loading": "正在将本地 NLLB 模型加载到 {runtime}{dots}",
        "translating": "正在翻译 chunk {current} / {total}。已用时间：{elapsed}{dots}",
        "writing": "正在保存翻译后的文档{dots}",
        "done": "翻译完成。总耗时：{elapsed}。",
        "error": "翻译失败：{message}",
        "preview_label": "翻译文本预览",
        "download_label": "⬇ 下载翻译后的文档",
        "ok": "OK",
        "chunk_count": "已从 {blocks} 个文档段落生成 {count} 个 chunks。",
    },
}


translator = NllbTranslator()


def normalize_ui_language(ui_language: str | None) -> str:
    return ui_language if ui_language in TEXTS else DEFAULT_UI_LANGUAGE


def normalize_runtime(runtime: str | None) -> str:
    return runtime if runtime in {"cpu", "gpu"} else "cpu"


def normalize_language_key(language_key: str | None, allow_auto: bool = True) -> str:
    allowed = SOURCE_LANGUAGE_KEYS if allow_auto else TARGET_LANGUAGE_KEYS
    return language_key if language_key in allowed else allowed[0]


def t(ui_language: str | None, key: str) -> str:
    return TEXTS[normalize_ui_language(ui_language)][key]


def language_choices(ui_language: str | None, source: bool):
    label_key = "zh" if normalize_ui_language(ui_language) == "中文" else "en"
    keys = SOURCE_LANGUAGE_KEYS if source else TARGET_LANGUAGE_KEYS
    return [(LANGUAGE_OPTIONS[key][label_key], key) for key in keys]


def runtime_choices(ui_language: str | None):
    return [(t(ui_language, "cpu_option"), "cpu"), (t(ui_language, "gpu_option"), "gpu")]


def format_elapsed(seconds: float) -> str:
    seconds = max(0, int(seconds))
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def spinner(elapsed: float, ui_language: str | None) -> str:
    frames = ["。", "。。", "。。。", "。。。。", "。。。。。"] if normalize_ui_language(ui_language) == "中文" else [".", "..", "...", "....", "....."]
    return frames[int(elapsed * 3) % len(frames)]


def render_runtime_status(runtime: str | None, ui_language: str | None) -> str:
    ui_language = normalize_ui_language(ui_language)
    runtime = normalize_runtime(runtime)
    cuda_available = translator.cuda_available()
    cuda_text = t(ui_language, "cuda_detected") if cuda_available else t(ui_language, "cuda_missing")

    cpu_color = "#16a34a" if runtime == "cpu" else "#dc2626"
    gpu_color = "#16a34a" if runtime == "gpu" else "#dc2626"
    cpu_state = t(ui_language, "active") if runtime == "cpu" else t(ui_language, "inactive")
    gpu_state = t(ui_language, "active") if runtime == "gpu" else t(ui_language, "inactive")
    selected_text = t(ui_language, "gpu_unavailable") if runtime == "gpu" and not cuda_available else t(ui_language, "selected_runtime").format(runtime=runtime.upper())
    selected_color = "#b45309" if runtime == "gpu" and not cuda_available else "#166534"

    def light(label: str, color: str, state: str) -> str:
        return f"""
        <div class="status-light" style="border-color:{color};">
            <span class="status-dot" style="background:{color};"></span>
            <strong>{html.escape(label)}</strong>
            <span style="color:{color};">{html.escape(state)}</span>
        </div>
        """

    return f"""
    <div class="status-panel">
        <div class="status-title">{html.escape(t(ui_language, "runtime_status"))}</div>
        <div class="status-row">
            {light("CPU", cpu_color, cpu_state)}
            {light("GPU", gpu_color, gpu_state)}
        </div>
        <div>{html.escape(cuda_text)}</div>
        <div style="color:{selected_color};margin-top:6px;">{html.escape(selected_text)}</div>
    </div>
    """


def render_progress(status_text: str, ui_language: str | None, state: str = "idle", elapsed_seconds: float = 0.0) -> str:
    colors = {"idle": "#64748b", "running": "#2563eb", "done": "#16a34a", "error": "#dc2626"}
    color = colors.get(state, colors["idle"])
    return f"""
    <div class="progress-panel">
        <div class="progress-header">
            <strong>{html.escape(t(ui_language, "progress_title"))}</strong>
            <span style="color:{color};">{html.escape(format_elapsed(elapsed_seconds))}</span>
        </div>
        <div class="progress-message" style="border-left-color:{color};">{html.escape(status_text)}</div>
    </div>
    """


def get_preferences(ui_language, runtime, source_language, target_language):
    return {
        "ui_language": normalize_ui_language(ui_language),
        "runtime": normalize_runtime(runtime),
        "source_language": normalize_language_key(source_language, allow_auto=True),
        "target_language": normalize_language_key(target_language, allow_auto=False),
    }


def restore_preferences(prefs):
    prefs = {**DEFAULT_PREFS, **(prefs or {})}
    ui_language = normalize_ui_language(prefs.get("ui_language"))
    runtime = normalize_runtime(prefs.get("runtime"))
    source_language = normalize_language_key(prefs.get("source_language"), allow_auto=True)
    target_language = normalize_language_key(prefs.get("target_language"), allow_auto=False)

    return (
        ui_language,
        gr.update(choices=runtime_choices(ui_language), value=runtime, label=t(ui_language, "runtime_label"), info=t(ui_language, "runtime_info")),
        render_runtime_status(runtime, ui_language),
        gr.update(label=t(ui_language, "file_label")),
        t(ui_language, "file_hint"),
        gr.update(choices=language_choices(ui_language, True), value=source_language, label=t(ui_language, "source_label")),
        gr.update(choices=language_choices(ui_language, False), value=target_language, label=t(ui_language, "target_label")),
        gr.update(value=t(ui_language, "start")),
        render_progress(t(ui_language, "idle"), ui_language),
        gr.update(label=t(ui_language, "preview_label")),
        gr.update(label=t(ui_language, "download_label"), visible=True, value=None),
        gr.update(value=t(ui_language, "title")),
        gr.update(value=t(ui_language, "intro")),
        gr.update(value=t(ui_language, "ok")),
        get_preferences(ui_language, runtime, source_language, target_language),
    )


def update_ui_language(ui_language, runtime, source_language, target_language):
    ui_language = normalize_ui_language(ui_language)
    runtime = normalize_runtime(runtime)
    source_language = normalize_language_key(source_language, allow_auto=True)
    target_language = normalize_language_key(target_language, allow_auto=False)
    return restore_preferences(get_preferences(ui_language, runtime, source_language, target_language))


def update_runtime(runtime, ui_language, source_language, target_language):
    runtime = normalize_runtime(runtime)
    return render_runtime_status(runtime, ui_language), get_preferences(ui_language, runtime, source_language, target_language)


def update_language_preferences(ui_language, runtime, source_language, target_language):
    return get_preferences(ui_language, runtime, source_language, target_language)


def validate_upload(file_obj, ui_language):
    if file_obj is None:
        return gr.update(visible=False), gr.update(value=None), gr.update(value=None)

    file_path = getattr(file_obj, "name", None) or str(file_obj)
    if validate_file_extension(file_path):
        return gr.update(visible=False), gr.update(), gr.update(value=None)

    return gr.update(visible=True), gr.update(value=None), gr.update(value=None)


def clear_unsupported_modal():
    return gr.update(visible=False), gr.update(value=None)


def resolve_source_language(source_language_key: str, blocks: list[str], ui_language: str) -> str:
    source_language_key = normalize_language_key(source_language_key, allow_auto=True)
    if source_language_key != "auto":
        return LANGUAGE_OPTIONS[source_language_key]["code"]

    detected = detect_language_simple("\n".join(blocks))
    if not detected:
        raise ValueError(t(ui_language, "manual_source_needed"))
    return detected


def translate_document(file_obj, runtime, source_language, target_language, ui_language):
    ui_language = normalize_ui_language(ui_language)
    runtime = normalize_runtime(runtime)
    target_language = normalize_language_key(target_language, allow_auto=False)
    start_time = time.time()
    empty_file = gr.update(value=None)

    try:
        if file_obj is None:
            raise ValueError(t(ui_language, "missing_file"))

        source_path = Path(getattr(file_obj, "name", None) or str(file_obj))
        if not validate_file_extension(source_path):
            yield (
                render_progress(t(ui_language, "unsupported"), ui_language, "error", time.time() - start_time),
                "",
                empty_file,
                gr.update(visible=True),
                get_preferences(ui_language, runtime, source_language, target_language),
            )
            return

        if runtime == "gpu" and not translator.cuda_available():
            raise RuntimeError(t(ui_language, "gpu_unavailable"))

        yield (
            render_progress(t(ui_language, "reading").format(dots=spinner(time.time() - start_time, ui_language)), ui_language, "running", time.time() - start_time),
            "",
            empty_file,
            gr.update(visible=False),
            get_preferences(ui_language, runtime, source_language, target_language),
        )

        blocks, _ = read_document(source_path)
        if not has_meaningful_text(blocks):
            raise ValueError(t(ui_language, "empty_document"))

        source_code = resolve_source_language(source_language, blocks, ui_language)
        target_code = LANGUAGE_OPTIONS[target_language]["code"]
        if source_code == target_code:
            raise ValueError(t(ui_language, "same_language"))

        chunks = split_text_blocks(blocks, max_chars=1000)
        translatable_chunks = [chunk.text for chunk in chunks]
        total_chunks = len(chunks)
        status = t(ui_language, "chunk_count").format(count=total_chunks, blocks=len(blocks))
        yield (
            render_progress(status, ui_language, "running", time.time() - start_time),
            "",
            empty_file,
            gr.update(visible=False),
            get_preferences(ui_language, runtime, source_language, target_language),
        )

        translated_texts: list[str] = []

        def on_progress(current: int, total: int, elapsed: float):
            return None

        yield (
            render_progress(t(ui_language, "loading").format(runtime=runtime.upper(), dots=spinner(time.time() - start_time, ui_language)), ui_language, "running", time.time() - start_time),
            "",
            empty_file,
            gr.update(visible=False),
            get_preferences(ui_language, runtime, source_language, target_language),
        )

        tokenizer_model_device = translator.load_model(runtime)
        tokenizer, model, device = tokenizer_model_device
        tokenizer.src_lang = source_code
        model.generation_config.max_length = None
        forced_bos_token_id = tokenizer.convert_tokens_to_ids(target_code)

        for index, chunk in enumerate(translatable_chunks, start=1):
            elapsed = time.time() - start_time
            yield (
                render_progress(
                    t(ui_language, "translating").format(
                        current=index,
                        total=total_chunks,
                        elapsed=format_elapsed(elapsed),
                        dots=spinner(elapsed, ui_language),
                    ),
                    ui_language,
                    "running",
                    elapsed,
                ),
                "\n".join(translated_texts),
                empty_file,
                gr.update(visible=False),
                get_preferences(ui_language, runtime, source_language, target_language),
            )

            if not chunk.strip():
                translated_texts.append("")
                continue

            import torch

            inputs = tokenizer(chunk, return_tensors="pt", truncation=True, max_length=512)
            inputs = {key: value.to(device) for key, value in inputs.items()}
            with torch.inference_mode():
                output_tokens = model.generate(
                    **inputs,
                    forced_bos_token_id=forced_bos_token_id,
                    max_new_tokens=512,
                    num_beams=4,
                )
            translated_texts.append(tokenizer.batch_decode(output_tokens, skip_special_tokens=True)[0])

        yield (
            render_progress(t(ui_language, "writing").format(dots=spinner(time.time() - start_time, ui_language)), ui_language, "running", time.time() - start_time),
            "\n".join(translated_texts),
            empty_file,
            gr.update(visible=False),
            get_preferences(ui_language, runtime, source_language, target_language),
        )

        translated_blocks = reconstruct_blocks(chunks, translated_texts)
        output_path = write_translated_document(source_path, translated_blocks, target_code)
        preview = "\n".join(translated_blocks)
        elapsed = time.time() - start_time

        yield (
            render_progress(t(ui_language, "done").format(elapsed=format_elapsed(elapsed)), ui_language, "done", elapsed),
            preview,
            gr.update(value=str(output_path), visible=True, label=t(ui_language, "download_label")),
            gr.update(visible=False),
            get_preferences(ui_language, runtime, source_language, target_language),
        )

    except Exception as exc:
        traceback.print_exc()
        elapsed = time.time() - start_time
        yield (
            render_progress(t(ui_language, "error").format(message=str(exc)), ui_language, "error", elapsed),
            "",
            empty_file,
            gr.update(visible=False),
            get_preferences(ui_language, runtime, source_language, target_language),
        )


CUSTOM_CSS = """
.gradio-container { max-width: 1120px !important; margin: 0 auto; }
.top-row { align-items: flex-start; }
.status-panel, .progress-panel {
    border: 1px solid #dbe3ec;
    border-radius: 8px;
    padding: 14px 16px;
    background: #f8fafc;
    color: #0f172a;
}
.status-title { font-weight: 700; margin-bottom: 10px; }
.status-row { display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 10px; }
.status-light {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 132px;
    border: 1px solid;
    border-radius: 8px;
    padding: 8px 10px;
    background: white;
}
.status-dot {
    display: inline-block;
    width: 12px;
    height: 12px;
    border-radius: 999px;
}
.progress-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}
.progress-message {
    border-left: 4px solid #64748b;
    background: white;
    padding: 10px 12px;
    line-height: 1.5;
}
#unsupported_modal {
    border: 1px solid #fecaca;
    border-radius: 8px;
    background: #fff7f7;
    padding: 14px 16px;
}
"""


with gr.Blocks(title=APP_TITLE) as demo:
    browser_preferences = gr.BrowserState(
        default_value=DEFAULT_PREFS,
        storage_key="local_document_translator_preferences_v1",
        secret="local_document_translator_preferences_secret",
    )

    title_md = gr.Markdown(t(DEFAULT_UI_LANGUAGE, "title"))

    with gr.Row(elem_classes=["top-row"]):
        with gr.Column(scale=4):
            intro_md = gr.Markdown(t(DEFAULT_UI_LANGUAGE, "intro"))
        with gr.Column(scale=1, min_width=160):
            ui_language_selector = gr.Radio(
                choices=["ENG", "中文"],
                value=DEFAULT_UI_LANGUAGE,
                label=t(DEFAULT_UI_LANGUAGE, "ui_language"),
                interactive=True,
            )

    with gr.Row():
        with gr.Column(scale=1):
            runtime_selector = gr.Radio(
                choices=runtime_choices(DEFAULT_UI_LANGUAGE),
                value="cpu",
                label=t(DEFAULT_UI_LANGUAGE, "runtime_label"),
                info=t(DEFAULT_UI_LANGUAGE, "runtime_info"),
                interactive=True,
            )
            runtime_status = gr.HTML(render_runtime_status("cpu", DEFAULT_UI_LANGUAGE))
        with gr.Column(scale=1):
            upload_file = gr.File(
                label=t(DEFAULT_UI_LANGUAGE, "file_label"),
                file_types=[".txt", ".md", ".docx"],
                type="filepath",
            )
            file_hint = gr.Markdown(t(DEFAULT_UI_LANGUAGE, "file_hint"))
            with gr.Column(visible=False, elem_id="unsupported_modal") as unsupported_modal:
                gr.Markdown("Unsupported File Format. Click OK to upload again.")
                unsupported_ok = gr.Button("OK")

    with gr.Row():
        source_dropdown = gr.Dropdown(
            choices=language_choices(DEFAULT_UI_LANGUAGE, True),
            value="auto",
            label=t(DEFAULT_UI_LANGUAGE, "source_label"),
            interactive=True,
        )
        target_dropdown = gr.Dropdown(
            choices=language_choices(DEFAULT_UI_LANGUAGE, False),
            value="simplified_chinese",
            label=t(DEFAULT_UI_LANGUAGE, "target_label"),
            interactive=True,
        )

    start_button = gr.Button(t(DEFAULT_UI_LANGUAGE, "start"), variant="primary")
    progress_html = gr.HTML(render_progress(t(DEFAULT_UI_LANGUAGE, "idle"), DEFAULT_UI_LANGUAGE))
    preview_output = gr.Textbox(label=t(DEFAULT_UI_LANGUAGE, "preview_label"), lines=14)
    download_output = gr.DownloadButton(label=t(DEFAULT_UI_LANGUAGE, "download_label"), value=None, visible=True)

    demo.load(
        fn=restore_preferences,
        inputs=[browser_preferences],
        outputs=[
            ui_language_selector,
            runtime_selector,
            runtime_status,
            upload_file,
            file_hint,
            source_dropdown,
            target_dropdown,
            start_button,
            progress_html,
            preview_output,
            download_output,
            title_md,
            intro_md,
            unsupported_ok,
            browser_preferences,
        ],
    )

    ui_language_selector.change(
        fn=update_ui_language,
        inputs=[ui_language_selector, runtime_selector, source_dropdown, target_dropdown],
        outputs=[
            ui_language_selector,
            runtime_selector,
            runtime_status,
            upload_file,
            file_hint,
            source_dropdown,
            target_dropdown,
            start_button,
            progress_html,
            preview_output,
            download_output,
            title_md,
            intro_md,
            unsupported_ok,
            browser_preferences,
        ],
    )

    runtime_selector.change(
        fn=update_runtime,
        inputs=[runtime_selector, ui_language_selector, source_dropdown, target_dropdown],
        outputs=[runtime_status, browser_preferences],
    )
    source_dropdown.change(
        fn=update_language_preferences,
        inputs=[ui_language_selector, runtime_selector, source_dropdown, target_dropdown],
        outputs=[browser_preferences],
    )
    target_dropdown.change(
        fn=update_language_preferences,
        inputs=[ui_language_selector, runtime_selector, source_dropdown, target_dropdown],
        outputs=[browser_preferences],
    )

    upload_file.change(
        fn=validate_upload,
        inputs=[upload_file, ui_language_selector],
        outputs=[unsupported_modal, upload_file, download_output],
    )
    unsupported_ok.click(fn=clear_unsupported_modal, outputs=[unsupported_modal, upload_file])

    start_button.click(
        fn=translate_document,
        inputs=[upload_file, runtime_selector, source_dropdown, target_dropdown, ui_language_selector],
        outputs=[progress_html, preview_output, download_output, unsupported_modal, browser_preferences],
    )


if __name__ == "__main__":
    os.environ.setdefault("GRADIO_ANALYTICS_ENABLED", "False")
    server_port = int(os.environ.get("TRANSLATOR_PORT", "7860"))
    inbrowser = os.environ.get("TRANSLATOR_INBROWSER", "1").lower() not in {"0", "false", "no"}
    demo.queue()
    demo.launch(server_name="127.0.0.1", server_port=server_port, inbrowser=inbrowser, share=False, css=CUSTOM_CSS)
