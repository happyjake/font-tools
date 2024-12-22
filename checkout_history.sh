#!/bin/bash

# Config
COMMITS_PER_PAGE=20
page=0

# Store commits with date
mapfile -t commits < <(git log --pretty=format:"%h|%cr|%s")
total_commits=${#commits[@]}
total_pages=$(( (total_commits + COMMITS_PER_PAGE - 1) / COMMITS_PER_PAGE ))
current=$(git rev-parse HEAD)

while true; do
    clear
    echo "提交历史 (第 $((page + 1))/$total_pages 页)"
    echo "------------------------"

    # Calculate page bounds
    start=$((page * COMMITS_PER_PAGE))
    end=$((start + COMMITS_PER_PAGE))
    [[ $end -gt $total_commits ]] && end=$total_commits

    # Display commits
    for ((i = start; i < end; i++)); do
        commit=${commits[$i]}
        hash=${commit%%|*}
        rest=${commit#*|}
        date=${rest%%|*}
        msg=${rest#*|}
        
        if [[ $hash = $(echo $current | cut -c1-7) ]]; then
            echo "$i $hash ($date) * $msg"
        else
            echo "$i $hash ($date) $msg"
        fi
    done

    echo -e "\n操作选项:"
    echo "-2: 上一页"
    echo "-1: 下一页"
    echo " 0: 退出"
    echo -e "请输入版本编号或操作选项:"
    read -r choice

    # Handle navigation
    if [[ $choice == "-1" ]]; then
        if ((page < total_pages - 1)); then
            ((page++))
        fi
        continue
    elif [[ $choice == "-2" ]]; then
        if ((page > 0)); then
            ((page--))
        fi
        continue
    elif [[ $choice == "0" ]]; then
        exit 0
    fi

    # Handle checkout
    if [[ $choice =~ ^[0-9]+$ ]] && ((choice < total_commits)); then
        # Extract only hash part from stored commit
        commit=${commits[$choice]}
        commit_hash=${commit%%|*}

        # Store current shebang modifications
        git diff > temp_changes.patch

        # Restore all tracked files to their original state
        git restore .
        
        if git checkout "$commit_hash"; then
            echo "已切换到版本 $commit_hash"
            # Show current commit
            echo "当前版本:"
            git log --oneline -1

            # if not in venv, source it
            if [[ -d ".venv" && -z "$VIRTUAL_ENV" ]]; then
                source .venv/bin/activate
            fi
            pip install -r requirements.txt
            
            exit 0
        else
            echo "切换版本失败"
            read -n 1 -s -r -p "按任意键继续..."
        fi

        # Reapply Termux shebang
        termux-fix-shebang *.sh
    else
        echo "无效的选择"
        read -n 1 -s -r -p "按任意键继续..."
    fi
done