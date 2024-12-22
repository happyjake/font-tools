#!/bin/sh

# 遍历当前目录下的所有 .ttf, .ttc 和 .otf 文件
for font in *.ttf *.ttc *.otf; do
    # 检查文件是否存在
    if [ -e "$font" ]; then
        # 修改文件权限为 777
        chmod 777 "$font"
        
        # 修改文件所有者为 root
        chown root:root "$font"
        
        echo "已修改: $font"
    fi
done

echo "所有字体文件权限和所有者已更新。"