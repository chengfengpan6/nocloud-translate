@echo off
title Install CUDA PyTorch for NoCloud Translate
color 0B

echo ========================================================
echo   Installing CUDA-enabled PyTorch for NoCloud Translate
echo   Target: Windows + NVIDIA GPU + PyTorch CUDA 11.8 wheel
echo ========================================================

cd /d "%~dp0"

if not exist ".\venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    py -3.10 -m venv venv 2>nul
    if not exist ".\venv\Scripts\python.exe" python -m venv venv
)

".\venv\Scripts\python.exe" -m pip install --upgrade pip
".\venv\Scripts\python.exe" -m pip install -r requirements.txt
".\venv\Scripts\python.exe" -m pip install --force-reinstall torch --index-url https://download.pytorch.org/whl/cu118

echo.
echo ========================================================
echo   CUDA check
echo ========================================================
".\venv\Scripts\python.exe" -c "import torch; print('torch:', torch.__version__); print('cuda available:', torch.cuda.is_available()); print('torch cuda runtime:', torch.version.cuda); print('device count:', torch.cuda.device_count()); print('device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

echo.
echo When cuda available is True, start run.bat and choose GPU in the WebUI.
pause
