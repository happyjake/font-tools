#!/bin/bash

# 获取当前脚本的文件名
current_script=$(basename "$0")
# 定义要排除的文件
exclude=("修改字体权限.sh" "$current_script")

# 创建一个文件列表
files=()
metric_files=()

# 遍历当前目录下的.sh文件
for script in *.sh; do
    # 检查文件是否在排除列表中
    if [[ ! " ${exclude[@]} " =~ " ${script} " ]] && [[ "$script" != *"度量"* ]]; then
        files+=("$script")
    elif [[ "$script" == *"度量"* ]]; then
        metric_files+=("$script")
    fi
done

# 自定义排序（保持原有序号）
sorted_files=("字体百分比缩放" "字体字符合并" "修改ttf信息" "生成mtz" "查看字体upm值" "修改字体upm为1000+手动选择改度_量" "修改英文标点间距" "可变字体母版重量_查看+修改" "ttf解包ttx" "ttx打包ttf" "分解ttc" "提取VF字体指定字重" "修改字体版本信息" "update_code" "checkout_history")

while true; do
    # Show current commit
    echo "当前版本:"
    git log -1 --pretty=format:"%h (%ad, %ar) %s" --date=local
    # 打印可执行的脚本列表
    echo -e "\n可执行的脚本列表:"
    for i in "${!sorted_files[@]}"; do
        for j in "${!files[@]}"; do
            if [[ "${files[j]%.sh}" == "${sorted_files[i]}" ]]; then
                echo "$((i + 1))) ${files[j]%.sh}"  # 去掉 .sh 后缀
                break
            fi
        done
    done

    # 添加选项
    echo "$(( ${#files[@]} + 1 ))) 更改字体度量(解决上浮下沉问题，仅支持1000单位字体)"
    echo "0) 退出"

    # 让用户输入选择
    read -p "请选择要执行的序号: " choice

    # 检查输入是否为空
    if [[ -z "$choice" ]]; then
        echo "无效的选择，请输入一个序号。"
        continue
    fi

    # 根据用户选择执行相应的脚本
    if [[ $choice -ge 1 && $choice -le ${#sorted_files[@]} ]]; then
        selected_script="${sorted_files[$((choice - 1))]}"
        for j in "${!files[@]}"; do
            if [[ "${files[j]%.sh}" == "$selected_script" ]]; then
                ./${files[j]}
                break
            fi
        done
    elif [[ $choice -eq $(( ${#files[@]} + 1 )) ]]; then
        # 处理 “更改度量” 选项
        for i in "${!metric_files[@]}"; do
            echo "$((i + 1))) ${metric_files[$i]%.sh}"  # 去掉 .sh 后缀
        done

        read -p "请选择你想修改的度量序号: " metric_choice

        if [[ -z "$metric_choice" ]]; then
            echo "无效的选择，请输入一个序号。"
            continue
        fi

        if [[ $metric_choice -ge 1 && $metric_choice -le ${#metric_files[@]} ]]; then
            ./${metric_files[$((metric_choice - 1))]}
        else
            echo "无效选择‼️‼️‼️‼️‼️"
        fi
    elif [[ $choice -eq 0 ]]; then
        echo "退出脚本。"
        exit 0
    else
        echo "无效选择‼️‼️‼️‼️‼️"
    fi

    # 提示用户返回主菜单
    echo -e "\n任务已完成。按 Enter 返回主菜单，或按其他任意键退出脚本..."
    read -n 1 -s key  # 等待用户按键
    if [[ -n "$key" ]]; then
        echo -e "\n退出脚本。"
        exit 0
    fi
done
