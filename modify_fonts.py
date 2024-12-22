import os
from fontTools.ttLib import TTFont

def list_ttf_files():
    """列出当前文件夹内所有 TTF 文件"""
    return [f for f in os.listdir() if f.lower().endswith('.ttf')]

def modify_font_info(file_path, new_version, new_subfamily):
    """修改字体文件中的版本信息和唯一子家族标识"""
    font = TTFont(file_path)
    
    # 修改 namerecord 中的版本信息
    for name_record in font['name'].names:
        if name_record.nameID == 5:
            name_record.string = f"Version {new_version}".encode('utf-16-be')
        elif name_record.nameID == 3:
            name_record.string = new_subfamily.encode('utf-16-be')

    # 保存为新文件
    new_file_name = f"改字体信息_{os.path.basename(file_path)}"
    font.save(new_file_name)
    print(f"已保存为: {new_file_name}")

def main():
    ttf_files = list_ttf_files()
    
    if not ttf_files:
        print("当前文件夹内没有 TTF 文件。")
        return
    
    print("可用的 TTF 文件:")
    for idx, file_name in enumerate(ttf_files):
        print(f"{idx}: {file_name}")
    
    # 让用户选择文件
    choice = int(input("请输入要修改的字体文件序号: "))
    if choice < 0 or choice >= len(ttf_files):
        print("无效的选择。")
        return
    
    selected_file = ttf_files[choice]
    
    # 获取新的版本号和 Unique Subfamily Identification
    new_version = input("请输入新的版本号Version: ")
    new_subfamily = input("请输入新的 唯一子家族标识Unique Subfamily Identification: ")

    # 修改字体信息
    modify_font_info(selected_file, new_version, new_subfamily)

if __name__ == "__main__":
    main()
