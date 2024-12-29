#!/data/data/com.termux/files/usr/bin/bash

# Get list of tracked .sh files that have shebang changes
modified_files=$(git status -s | grep "\.sh$" | awk '{print $2}')

# Revert Termux shebang to standard in modified files
for file in $modified_files; do
    sed -i 's|#!/data/data/com.termux/files/usr/bin/bash|#!/bin/bash|g' "$file"
done

# Pull changes
echo "Pulling latest changes..."
git pull
pull_status=$?

# Reapply Termux shebang
termux-fix-shebang *.sh