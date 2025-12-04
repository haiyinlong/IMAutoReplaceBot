#!/bin/bash

echo "[+] 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "[-] 错误：未找到 python3"
    exit 1
fi

echo "[+] 安装依赖..."
pip3 install -r requirements.txt

echo "[+] 开始打包..."

# 判断是否提供图标（仅 macOS 支持 .icns，Linux 通常忽略）
ICON_ARG=""
if [ -f "icon.icns" ]; then
    ICON_ARG="--icon=icon.icns"
elif [ -f "icon.ico" ]; then
    # Linux 下 .ico 可能被忽略，但无害
    ICON_ARG="--icon=icon.ico"
fi

pyinstaller \
    --onefile \
    --add-data="config.json:." \
    --add-data="screenshots:screenshots" \
    --add-data="logs:logs" \
    --name="IMAutoReplyBot" \
    $ICON_ARG \
    main.py

echo "[+] 打包完成！"
echo "    输出路径: dist/IMAutoReplyBot"