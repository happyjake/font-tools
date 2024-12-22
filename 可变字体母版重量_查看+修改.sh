#!/bin/bash

while true; do
    echo "请选择要执行的操作:"
    echo "1) 显示可变字体母版、实例信息"
    echo "2) 修改可变字体母版信息"
    echo "3) 退出"

    read -p "请输入您的选择 (1-3): " choice

    case $choice in
        1)
            echo "加载字体列表，执行脚本..."
            python3 list_fonts.py
            ;;
        2)
            echo "加载字体列表，执行脚本..."
            python3 modify_axis.py
            ;;
        3)
            echo "退出程序。"
            exit 0
            ;;
        *)
            echo "无效的选择，请输入 1、2 或 3。"
            ;;
    esac

    # 提示用户是否继续
    read -p "是否继续执行其他操作？(按 Enter 继续，按 x 退出): " continue_choice
    if [[ "$continue_choice" == "x" ]]; then
        echo "退出程序。"
        exit 0
    fi
done
