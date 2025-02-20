#!/data/data/com.termux/files/usr/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Create the shortcuts directory if it doesn't exist
mkdir -p ~/.shortcuts

# Create the shortcut script that Termux will execute
cat >~/.shortcuts/font-tools <<EOF
#!/data/data/com.termux/files/usr/bin/bash

# Change to the project directory
cd "${SCRIPT_DIR}"
source venv/bin/activate
./脚本选择.sh
EOF

# Make the shortcut script executable
chmod +x ~/.shortcuts/font-tools

echo "Font-tools shortcut has been created in ~/.shortcuts"
echo "You can now access it through Termux widget or run it directly with '~/.shortcuts/font-tools'"
