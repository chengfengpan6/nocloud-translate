# NoCloud Translate

[中文说明](README_zh.md)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Gradio](https://img.shields.io/badge/UI-Gradio-orange)
![Model](https://img.shields.io/badge/Model-NLLB--200--600M-green)
![CUDA](https://img.shields.io/badge/CUDA-Ready-76B900)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**🔒 Translate private documents on your own laptop. No cloud handoff. No API keys. No third-party translation service.**

NoCloud Translate is a local WebUI for translating TXT, MD, and DOCX files with `facebook/nllb-200-distilled-600M`. It gives you a clean browser workflow, CPU/GPU switching, chunked long-document handling, bilingual UI, and downloadable translated files.

## ✦ Why It Exists

Most translation tools are built around sending text somewhere else. NoCloud Translate is built for the opposite workflow: keep the document local, run the model locally, and still get a simple WebUI instead of a command-line maze.

Use it for:

- 📝 Notes, drafts, study material, and internal documents.
- 🌏 English, Simplified Chinese, Traditional Chinese, and Filipino / Tagalog translation.
- 🔐 Local laptop workflows where privacy matters.
- ⚡ CUDA acceleration on NVIDIA GPUs, with CPU mode always available.

## ✦ What You Get

- 🔒 **Private by design**: translation runs on your machine.
- 🖥️ **One-click WebUI**: double-click `run.bat`, open `127.0.0.1:7860`, translate.
- 🎛️ **CPU / GPU control**: choose compatibility or CUDA speed before translation starts.
- 🟢 **Clear runtime lights**: green means active, red means inactive.
- 📄 **Document-aware chunking**: paragraphs stay in order, long blocks are split safely.
- 🚀 **Lazy model loading**: the model loads only when translation starts.
- ⏱️ **Useful progress text**: current chunk, total chunks, elapsed time, and animated dots.
- ⬇️ **Download-ready output**: TXT/MD inputs produce TXT; DOCX inputs produce DOCX.

## 🌐 Supported Languages

| Language | NLLB code |
| --- | --- |
| English | `eng_Latn` |
| Simplified Chinese | `zho_Hans` |
| Traditional Chinese | `zho_Hant` |
| Filipino / Tagalog | `tgl_Latn` |

## 📁 Supported Files

| Input | Output |
| --- | --- |
| `.txt` | `.txt` |
| `.md` | `.txt` |
| `.docx` | `.docx` |

DOCX output preserves paragraph structure.

## ⚡ Quick Start

```bat
cd nocloud-translate
run.bat
```

Open:

```text
http://127.0.0.1:7860
```

The app binds to `127.0.0.1` and does not create a public share URL.

## 🧰 Manual Setup

```bat
python -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe web_ui.py
```

## 🚀 CUDA Setup

For NVIDIA GPU acceleration on Windows:

```bat
install_gpu_cuda.bat
```

Expected check:

```text
cuda available: True
device: NVIDIA GeForce RTX 3060 Laptop GPU
```

Manual check:

```bat
.\venv\Scripts\python.exe -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.version.cuda); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

## 🖥️ Hardware Target

- OS: Windows 10 / 11
- Python: 3.10+
- RAM: 16 GB minimum, 32 GB for large documents
- CPU mode: Intel Core i7 class CPU or better
- GPU mode: NVIDIA CUDA GPU, tested on RTX 3060 Laptop GPU 6 GB VRAM

## ✅ First Translation

Try the included sample:

```text
examples/sample_en.txt
```

In the WebUI:

1. 🎛️ Choose `CPU` or `GPU`.
2. 📄 Upload `examples/sample_en.txt`.
3. 🌐 Set source to `English`.
4. 🌐 Set target to `Simplified Chinese`.
5. ▶️ Click `Start Translation`.
6. ⬇️ Download the translated document.

## 🧱 Project Structure

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

## 📦 Model Download

On first use, the app downloads `facebook/nllb-200-distilled-600M` from Hugging Face when the model is not already in the local cache. After the model files are cached, translation uses the local cached files.

## ❓ FAQ

### Does NoCloud Translate use online translation APIs?

No. Translation runs locally with `facebook/nllb-200-distilled-600M`.

### What happens when GPU mode is unavailable?

The WebUI shows a clear CUDA error and CPU mode remains available.

### How does Auto Detect work?

Auto Detect uses local character rules. Chinese-heavy text is treated as Simplified Chinese. English-heavy ASCII text is treated as English. Ambiguous text requires manual source language selection.

### Why split documents into chunks?

NLLB has sequence length limits. NoCloud Translate splits documents into ordered chunks and recombines the translated output.

## 📜 License

MIT License. See [LICENSE](LICENSE).
