#!/data/data/com.termux/files/usr/bin/bash

# Store current shebang modifications
git diff > temp_changes.patch

# Restore all tracked files to their original state
git restore .

echo "更新代码到最新版本..."

# Fetch latest
git fetch origin master || { echo "获取远程更新失败"; exit 1; }

# Force reset to origin/master
git reset --hard origin/master || { echo "重置分支失败"; exit 1; }

echo "更新完成，已重置到最新版本"

# Show current commit
echo "当前版本:"
git log --oneline -1

# if not in venv, source it
if [[ -d ".venv" && -z "$VIRTUAL_ENV" ]]; then
    source .venv/bin/activate
fi
pip install -r requirements.txt

# Reapply Termux shebang
termux-fix-shebang *.sh