import re
from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class TextChunk:
    block_index: int
    text: str
    is_blank: bool = False


_SENTENCE_BOUNDARY_RE = re.compile(r"(?<=[.!?。！？；;])\s+|(?<=[。！？；;])")


def _split_long_text(text: str, max_chars: int) -> List[str]:
    text = text.strip()
    if len(text) <= max_chars:
        return [text]

    pieces = [piece.strip() for piece in _SENTENCE_BOUNDARY_RE.split(text) if piece.strip()]
    chunks: List[str] = []
    current = ""

    for piece in pieces:
        if len(piece) > max_chars:
            if current:
                chunks.append(current)
                current = ""
            chunks.extend(piece[i : i + max_chars] for i in range(0, len(piece), max_chars))
            continue

        candidate = f"{current} {piece}".strip() if current else piece
        if len(candidate) <= max_chars:
            current = candidate
        else:
            chunks.append(current)
            current = piece

    if current:
        chunks.append(current)

    if not chunks:
        chunks = [text[i : i + max_chars] for i in range(0, len(text), max_chars)]

    return chunks


def split_text_blocks(blocks: Iterable[str], max_chars: int = 1000) -> List[TextChunk]:
    chunks: List[TextChunk] = []
    safe_max_chars = max(200, int(max_chars))

    for block_index, block in enumerate(blocks):
        block = "" if block is None else str(block)
        if not block.strip():
            chunks.append(TextChunk(block_index=block_index, text="", is_blank=True))
            continue

        for piece in _split_long_text(block, safe_max_chars):
            chunks.append(TextChunk(block_index=block_index, text=piece, is_blank=False))

    return chunks


def reconstruct_blocks(chunks: Iterable[TextChunk], translated_texts: Iterable[str]) -> List[str]:
    grouped: dict[int, List[str]] = {}

    for chunk, translated_text in zip(chunks, translated_texts):
        grouped.setdefault(chunk.block_index, [])
        if chunk.is_blank:
            grouped[chunk.block_index].append("")
        else:
            grouped[chunk.block_index].append(translated_text.strip())

    if not grouped:
        return []

    return [" ".join(part for part in grouped[index] if part).strip() for index in range(max(grouped) + 1)]
