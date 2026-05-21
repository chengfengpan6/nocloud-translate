# NoCloud Translate

[English](README.md)

**在你的笔记本本地运行、支持 GPU 的私有文档翻译工具。不走云端，不需要 API Key，不接入第三方翻译服务。**

NoCloud Translate 是一个本地 Gradio 文档翻译 WebUI，使用 `facebook/nllb-200-distilled-600M`。它支持 CPU 兼容模式，也支持 NVIDIA CUDA GPU 加速。

## 项目亮点

- **本地隐私**：文档留在你的电脑上。
- **不使用翻译 API**：不依赖 Google Cloud、AWS、DeepL、OpenAI API 或其他在线翻译服务。
- **CUDA 加速**：已在 NVIDIA RTX 3060 Laptop GPU 6GB VRAM 上测试。
- **CPU fallback**：CPU 模式始终可用。
- **简单 WebUI**：上传文档、选择语言、翻译、下载。
- **长文档处理**：按段落切分，让长文本保持在模型输入限制内。

## 支持语言

| 语言 | NLLB code |
| --- | --- |
| English | `eng_Latn` |
| 简体中文 | `zho_Hans` |
| 繁体中文 | `zho_Hant` |
| Filipino / Tagalog | `tgl_Latn` |

## 功能列表

- 顶部 CPU / GPU 运行模式选择。
- CPU 和 GPU 红绿状态灯。
- 即使检测到 CUDA，也允许手动选择 CPU。
- 如果选择 GPU 但 CUDA 不可用，会显示明确错误。
- WebUI 界面语言切换：`ENG / 中文`。
- 支持上传 `TXT`、`MD`、`DOCX`。
- 不支持格式固定提示：`Unsupported File Format. Click OK to upload again.`
- 源语言支持 `Auto Detect`。
- 目标语言支持全部已列语言。
- 点击 `Start Translation / 开始翻译` 后才加载模型。
- 相同 runtime/model 组合会缓存复用，避免重复加载。
- 按段落优先切分，长段落继续切成更小 chunk。
- 显示当前 chunk / 总 chunk、已用时间和动态点。
- 不显示不准确的百分比进度条。
- 翻译完成后显示文本预览，并提供下载按钮。
- Windows 双击启动脚本：`run.bat`。
- CUDA 安装辅助脚本：`install_gpu_cuda.bat`。

## 环境要求

- OS：Windows 10 / 11
- Python：3.10+
- RAM：最低 16 GB，推荐 32 GB
- CPU 模式：Intel Core i7 级别 CPU 或更高
- GPU 模式：NVIDIA CUDA GPU，已测试 RTX 3060 Laptop GPU 6GB VRAM

## 支持的文件格式

- `.txt`
- `.md`
- `.docx`

TXT 和 MD 输入会输出 TXT。DOCX 输入会输出 DOCX，并保留段落结构。

## 快速开始

克隆或下载仓库后，进入项目目录：

```bat
cd nocloud-translate
```

启动 WebUI：

```bat
run.bat
```

访问：

```text
http://127.0.0.1:7860
```

应用绑定到 `127.0.0.1`，不会创建公网分享链接。

## 手动安装

```bat
python -m venv venv
.\venv\Scripts\python.exe -m pip install --upgrade pip
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe web_ui.py
```

## CPU 模式

选择 `CPU` 可获得最广泛的兼容性。CPU 模式使用标准 PyTorch CPU 推理，不依赖 CUDA。

## GPU 模式

当 PyTorch 检测到 NVIDIA CUDA GPU 后，选择 `GPU`。

Windows CUDA 安装运行：

```bat
install_gpu_cuda.bat
```

该脚本会把 CUDA 版 PyTorch 安装到本项目的 `venv`，并打印 CUDA 检查结果。

预期 CUDA 检查：

```text
cuda available: True
device: NVIDIA GeForce RTX 3060 Laptop GPU
```

手动 CUDA 检查：

```bat
.\venv\Scripts\python.exe -c "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.version.cuda); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
```

## 示例

项目包含示例输入文件：

```text
examples/sample_en.txt
```

在 WebUI 中上传它，选择 `English` 到 `Simplified Chinese`，然后点击 `Start Translation / 开始翻译`。

## 项目结构

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

## 模型下载

首次运行时，如果本地 Hugging Face cache 中没有 `facebook/nllb-200-distilled-600M`，程序会下载模型文件。模型文件缓存完成后，翻译使用本地缓存模型运行。

## 常见问题

### 是否使用在线翻译 API？

不使用。翻译由本地的 `facebook/nllb-200-distilled-600M` 模型完成。

### 为什么 GPU 模式报错？

说明 PyTorch 当前无法检测到 CUDA GPU。运行 `install_gpu_cuda.bat`，重启 WebUI 后再选择 GPU。

### Auto Detect 如何工作？

Auto Detect 使用本地字符规则。中文字符占比高的文本会识别为简体中文；ASCII 英文占比高的文本会识别为 English；模糊文本需要手动选择源语言。

### 为什么不能整篇文档一次性翻译？

NLLB 存在输入长度限制。NoCloud Translate 会把文档切成有序 chunk，再按顺序合并翻译结果。

## License

MIT License。见 [LICENSE](LICENSE)。
