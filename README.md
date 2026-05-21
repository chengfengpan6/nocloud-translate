# NoCloud Translate

[中文说明](README_zh.md)

**Private, GPU-ready document translation on your laptop. No cloud. No API keys. No third-party translation service.**

NoCloud Translate is a local Gradio WebUI for translating text documents with `facebook/nllb-200-distilled-600M`. It runs on CPU for maximum compatibility and on NVIDIA CUDA GPUs for faster local inference.

## Highlights

- **Local privacy**: documents stay on your machine.
- **No translation APIs**: no Google Cloud, AWS, DeepL, OpenAI API, or other online translation service.
- **CUDA acceleration**: tested on an NVIDIA RTX 3060 Laptop GPU with 6 GB VRAM.
- **CPU fallback**: CPU mode is always available.
- **Simple WebUI**: upload a document, choose languages, translate, download.
- **Long-document handling**: paragraph-based chunking keeps long inputs within model limits.

## Supported Languages

| Language | NLLB code |
| --- | --- |
| English | `eng_Latn` |
| Simplified Chinese | `zho_Hans` |
| Traditional Chinese | `zho_Hant` |
| Filipino / Tagalog | `tgl_Latn` |

## Features

- CPU / GPU runtime selector at the top of the WebUI.
- Green/red CPU and GPU status lights.
- Manual CPU mode even when CUDA is detected.
- Clear error when GPU is selected but CUDA is unavailable.
- Bilingual interface: `ENG / 中文`.
- Upload support for `TXT`, `MD`, and `DOCX`.
- Fixed unsupported-format message: `Unsupported File Format. Click OK to upload again.`
- Source language selector with `Auto Detect`.
- Target language selector for all supported languages.
- Lazy model loading when `Start Translation` is clicked.
- Model cache reuse for the same runtime.
- Paragraph-first chunking with long-paragraph splitting.
- Chunk status with elapsed time and animated dots.
- No inaccurate percentage progress bar.
- Preview and download of the translated document.
- Windows `run.bat` launcher.
- CUDA setup helper: `install_gpu_cuda.bat`.

## Requirements

- OS: Windows 10 / 11
- Python: 3.10+
- RAM: 16 GB minimum, 32 GB for large documents
- CPU mode: Intel Core i7 class CPU or better
- GPU mode: NVIDIA CUDA GPU, tested on RTX 3060 Laptop GPU 6 GB VRAM

## Supported File Formats

- `.txt`
- `.md`
- `.docx`

TXT and MD output is saved as TXT. DOCX output is saved as DOCX with paragraph structure preserved.

## Quick Start

Clone or download the repository, then open the project folder:

```bat
cd nocloud-translate
```

Start the WebUI:

```bat
run.bat
```

Open:

```text
http://127.0.0.1:7860
```

The app binds to `127.0.0.1` and does not create a public share URL.

## Manual Installation

```bat
python -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe web_ui.py
```

## CPU Mode

Choose `CPU` for the broadest compatibility. CPU mode uses standard PyTorch CPU inference and runs without CUDA.

## GPU Mode

Choose `GPU` after PyTorch detects your NVIDIA CUDA GPU.

For Windows CUDA setup, run:

```bat
install_gpu_cuda.bat
```

The helper installs the CUDA-enabled PyTorch wheel into this project’s `venv` and prints a CUDA check.

Expected CUDA check:

```text
cuda available: True
device: NVIDIA GeForce RTX 3060 Laptop GPU
```

Manual CUDA check:

```bat
.\venv\Scripts\python.exe -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.version.cuda); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

## Example

A sample input file is included:

```text
examples/sample_en.txt
```

Upload it in the WebUI, choose `English` to `Simplified Chinese`, then click `Start Translation`.

## Project Structure

```text
nocloud-translate/
├── examples/
│   └── sample_en.txt
├── .gitignore
├── document_io.py
├── install_gpu_cuda.bat
├── LICENSE
├── README.md
├── README_zh.md
├── requirements.txt
├── run.bat
├── text_splitter.py
├── translator.py
└── web_ui.py
```

## Model Download

The first run downloads `facebook/nllb-200-distilled-600M` from Hugging Face when the model is not already present in the local cache. After the files are cached, translation runs locally from the cached model files.

## FAQ

### Does NoCloud Translate use online translation APIs?

No. Translation is performed locally with `facebook/nllb-200-distilled-600M`.

### Why does GPU mode show an error?

PyTorch cannot see a CUDA GPU. Run `install_gpu_cuda.bat`, restart the WebUI, and choose GPU again.

### How does Auto Detect work?

Auto Detect uses local character rules. Chinese-heavy text is treated as Simplified Chinese. English-heavy ASCII text is treated as English. Ambiguous text requires manual source language selection.

### Why not translate the whole document at once?

NLLB has sequence length limits. NoCloud Translate splits documents into ordered chunks and recombines the translated output.

## License

MIT License. See [LICENSE](LICENSE).
