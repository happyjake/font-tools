#!/data/data/com.termux/files/usr/bin/bash

# Store current shebang modifications
git diff > temp_changes.patch

# Restore all tracked files to their original state
git restore .

# Pull changes
echo "Pulling latest changes..."
git pull
pull_status=$?

# Reapply Termux shebang
termux-fix-shebang *.sh