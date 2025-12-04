@echo off
setlocal

echo [+] 检查 Python 环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [-] 错误：未找到 Python。请先安装 Python 并加入 PATH。
    pause
    exit /b 1
)

echo [+] 安装依赖...
pip install -r requirements.txt

echo [+] 开始打包（静默模式，无控制台窗口）...

if exist "icon.ico" (
    pyinstaller ^
        --onefile ^
        --windowed ^
        --add-data "config.json;." ^
        --add-data "screenshots;screenshots" ^
        --add-data "logs;logs" ^
        --icon="icon.ico" ^
        --name="AutoReplyBot" ^
        main.py
) else (
    pyinstaller ^
        --onefile ^
        --windowed ^
        --add-data "config.json;." ^
        --add-data "screenshots;screenshots" ^
        --add-data "logs;logs" ^
        --name="IMAutoReplyBot" ^
        main.py
)

echo [+] 打包完成！
echo     输出路径: dist\IMAutoReplyBot.exe
pause