import os
from fontTools.ttLib import TTFont

def get_variable_font_axes(ttf_file):
    """获取可变字体的轴信息"""
    font = TTFont(ttf_file)
    axes = font['fvar'].axes if 'fvar' in font else None
    return axes

def modify_font_axes(font, axis_tag, new_min, new_max, new_default):
    """修改字体的轴信息"""
    if 'fvar' in font:
        for axis in font['fvar'].axes:
            if axis.axisTag == axis_tag:
                axis.minValue = new_min  # 使用minValue代替minimum
                axis.maxValue = new_max  # 使用maxValue代替maximum
                axis.defaultValue = new_default  # defaultValue保持不变
                print(f"已修改母版轴 '{axis_tag}' 的值为: 最小值 {new_min}, 最大值 {new_max}, 默认值 {new_default}")

def list_ttf_files():
    """列出当前文件夹内的所有 TTF 文件"""
    ttf_files = [f for f in os.listdir('.') if f.endswith('.ttf')]
    return ttf_files

def main():
    ttf_files = list_ttf_files()
    
    if not ttf_files:
        print("当前文件夹内没有找到 TTF 文件。")
        return

    while True:
        print("当前文件夹内的 TTF 文件:")
        for index, file in enumerate(ttf_files):
            print(f"{index + 1}: {file}")

        choice = input("请选择要修改的字体 (输入数字 1-{}, 或按 Enter 返回): ".format(len(ttf_files)))
        if not choice:
            return
        try:
            choice = int(choice) - 1
            if choice < 0 or choice >= len(ttf_files):
                print("无效的选择。")
                continue
        except ValueError:
            print("无效的输入。")
            continue

        ttf_file = ttf_files[choice]
        font = TTFont(ttf_file)

        # 获取可变字体的轴信息
        axes = get_variable_font_axes(ttf_file)

        if axes:
            print("当前字体的轴信息:")
            for axis in axes:
                print(f"母版轴名称: {axis.axisTag}, 最小值: {axis.minValue}, 最大值: {axis.maxValue}, 默认值: {axis.defaultValue}")

            # 直接选择第一个轴进行修改
            axis_tag_to_modify = axes[0].axisTag  
            
            # 输入新的最小值、最大值和默认值
            new_min_value = input(f"请输入新的最小值 (当前值: {axes[0].minValue}): ") or axes[0].minValue
            new_max_value = input(f"请输入新的最大值 (当前值: {axes[0].maxValue}): ") or axes[0].maxValue
            new_default_value = input(f"请输入新的默认值 (当前值: {axes[0].defaultValue}): ") or axes[0].defaultValue

            modify_font_axes(font, axis_tag_to_modify, int(new_min_value), int(new_max_value), int(new_default_value))

            # 保存修改后的字体
            modified_file_name = '修改母版度量_' + ttf_file
            font.save(modified_file_name)
            print(f"已保存修改后的字体为: {modified_file_name}")
        else:
            print("该字体不是可变字体,无法进行修改。")

if __name__ == '__main__':
    main()
