import os
from fontTools.ttLib import TTFont

def list_ttf_files():
    """列出当前文件夹内的所有TTF文件"""
    ttf_files = [f for f in os.listdir('.') if f.endswith('.ttf')]
    return ttf_files

def get_variable_font_axes(ttf_file):
    """获取可变字体的轴信息"""
    font = TTFont(ttf_file)
    axes = font['fvar'].axes if 'fvar' in font else None
    return axes

def get_font_instances(ttf_file):
    """获取字体实例信息"""
    font = TTFont(ttf_file)
    instances = font['fvar'].instances if 'fvar' in font else None
    return instances

def display_axes_info(axes):
    """显示字体轴信息"""
    if axes:
        for axis in axes:
            print(f"母版轴名称: {axis.axisTag}, 最小值: {axis.minValue}, 最大值: {axis.maxValue}, 默认值: {axis.defaultValue}")
    else:
        print("该字体不是可变字体，或没有轴信息。")

def display_instances_info(instances):
    """显示字体实例信息"""
    if instances:
        weights = []
        for instance in instances:
            weight = instance.coordinates['wght']
            # 检查是否是整数
            if weight.is_integer():
                weights.append(str(int(weight)))  # 只保留整数部分
            else:
                weights.append(str(weight))  # 保留小数
        print("实例：", " ".join(weights))  # 用空格连接并输出，前面加上“实例：”
    else:
        print("该字体没有实例信息。")

def main():
    ttf_files = list_ttf_files()
    
    if not ttf_files:
        print("当前文件夹内没有TTF文件。")
        return
    
    print("可用的TTF文件列表:")
    for index, file in enumerate(ttf_files):
        print(f"{index + 1}: {file}")
    
    choice = input("请输入文件序号来选择字体: ")
    
    try:
        choice_index = int(choice) - 1
        if choice_index < 0 or choice_index >= len(ttf_files):
            raise ValueError("无效的序号")
        
        selected_file = ttf_files[choice_index]
        print(f"您选择的字体: {selected_file}")
        
        axes = get_variable_font_axes(selected_file)
        display_axes_info(axes)

        instances = get_font_instances(selected_file)
        display_instances_info(instances)
        
    except ValueError as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()
