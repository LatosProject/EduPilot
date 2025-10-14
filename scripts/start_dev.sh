#!/bin/bash
export LC_ALL=en_US.UTF-8
export LANG=en_US.UTF-8

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 前端启动
osascript -e 'tell app "Terminal"
    do script "cd '"$PROJECT_ROOT/frontend/src"' && npm run dev"
end tell'

# 后端启动
osascript -e 'tell app "Terminal"
    do script "cd '"$PROJECT_ROOT/backend/app"' && source '"$PROJECT_ROOT/backend/app/.venv/bin/activate"' && python3 app.py"
end tell'

# 执行 warmup.py
cd "$PROJECT_ROOT/scripts"
python3 warmup.py

# 关闭脚本所在终端窗口
osascript -e 'tell application "Terminal" to do script "exit" in front window'
