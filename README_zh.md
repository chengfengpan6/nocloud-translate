# NoCloud Translate

[English](README.md)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Gradio](https://img.shields.io/badge/UI-Gradio-orange)
![Model](https://img.shields.io/badge/Model-NLLB--200--600M-green)
![CUDA](https://img.shields.io/badge/CUDA-Ready-76B900)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

**🔒 把私人文档留在自己的电脑上翻译。不走云端，不需要 API Key，不接入第三方翻译服务。**

NoCloud Translate 是一个本地文档翻译 WebUI，使用 `facebook/nllb-200-distilled-600M`，支持 TXT、MD、DOCX。它提供清爽的浏览器界面、CPU/GPU 切换、长文档分块处理、双语界面，以及可下载的翻译结果。

## ✦ 为什么做它

大多数翻译工具默认把文本交给远端服务。NoCloud Translate 选择相反的路径：文档留在本地，模型在本地运行，同时保留一个简单好用的 WebUI。

适合这些场景：

- 📝 笔记、草稿、学习资料、内部文档。
- 🌏 English、简体中文、繁体中文、Filipino / Tagalog 翻译。
- 🔐 需要本地隐私的笔记本工作流。
- ⚡ NVIDIA GPU CUDA 加速，也可随时切换 CPU 模式。

## ✦ 你会得到什么

- 🔒 **本地隐私**：翻译在你的电脑上完成。
- 🖥️ **一键 WebUI**：双击 `run.bat`，打开 `127.0.0.1:7860`，开始翻译。
- 🎛️ **CPU / GPU 可控**：翻译前手动选择兼容模式或 CUDA 加速。
- 🟢 **清楚的状态灯**：绿色代表启用，红色代表未启用。
- 📄 **文档感知分块**：段落顺序保留，长段落自动拆分。
- 🚀 **Lazy loading**：点击开始翻译后才加载模型。
- ⏱️ **有用的进度文字**：当前 chunk、总 chunk、已用时间和动态点。
- ⬇️ **直接下载结果**：TXT/MD 输入输出 TXT，DOCX 输入输出 DOCX。

## 🌐 支持语言

| 语言 | NLLB code |
| --- | --- |
| English | `eng_Latn` |
| 简体中文 | `zho_Hans` |
| 繁体中文 | `zho_Hant` |
| Filipino / Tagalog | `tgl_Latn` |

## 📁 支持文件

| 输入 | 输出 |
| --- | --- |
| `.txt` | `.txt` |
| `.md` | `.txt` |
| `.docx` | `.docx` |

DOCX 输出保留段落结构。

## ⚡ 快速开始

```bat
cd nocloud-translate
run.bat
```

访问：

```text
http://127.0.0.1:7860
```

应用绑定到 `127.0.0.1`，不会创建公网分享链接。

## 🧰 手动安装

```bat
python -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe web_ui.py
```

## 🚀 CUDA 安装

Windows 上使用 NVIDIA GPU 加速：

```bat
install_gpu_cuda.bat
```

预期检查结果：

```text
cuda available: True
device: NVIDIA GeForce RTX 3060 Laptop GPU
```

手动检查：

```bat
.\venv\Scripts\python.exe -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.version.cuda); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

## 🖥️ 硬件目标

- OS：Windows 10 / 11
- Python：3.10+
- RAM：最低 16 GB，长文档使用 32 GB
- CPU 模式：Intel Core i7 级别 CPU 或更高
- GPU 模式：NVIDIA CUDA GPU，已测试 RTX 3060 Laptop GPU 6GB VRAM

## ✅ 第一次翻译

项目包含示例文件：

```text
examples/sample_en.txt
```

在 WebUI 中：

1. 🎛️ 选择 `CPU` 或 `GPU`。
2. 📄 上传 `examples/sample_en.txt`。
3. 🌐 源语言选择 `English`。
4. 🌐 目标语言选择 `Simplified Chinese`。
5. ▶️ 点击 `Start Translation / 开始翻译`。
6. ⬇️ 下载翻译后的文档。

## 🧱 项目结构

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

## 📦 模型下载

首次使用时，如果本地缓存中没有 `facebook/nllb-200-distilled-600M`，应用会从 Hugging Face 下载模型。模型文件缓存完成后，翻译会使用本地缓存文件。

## ❓ 常见问题

### 是否使用在线翻译 API？

不使用。翻译由本地的 `facebook/nllb-200-distilled-600M` 模型完成。

### GPU 模式不可用时会怎样？

WebUI 会显示明确的 CUDA 错误，CPU 模式仍然可用。

### Auto Detect 如何工作？

Auto Detect 使用本地字符规则。中文字符占比高的文本会识别为简体中文；ASCII 英文占比高的文本会识别为 English；模糊文本需要手动选择源语言。

### 为什么要把文档切成 chunks？

NLLB 存在输入长度限制。NoCloud Translate 会把文档切成有序 chunk，再按顺序合并翻译结果。

## 📜 License

MIT License。见 [LICENSE](LICENSE)。
