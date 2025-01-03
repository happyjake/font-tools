#!/data/data/com.termux/files/usr/bin/bash

# Store current shebang modifications
git diff > temp_changes.patch

# Restore all tracked files to their original state
git restore .

# Pull changes
echo "Pulling latest changes..."
git pull
pull_status=$?

# if not in venv, source it
if [[ -d ".venv" && -z "$VIRTUAL_ENV" ]]; then
    source .venv/bin/activate
fi
pip install -r requirements.txt

# Reapply Termux shebang
termux-fix-shebang *.sh