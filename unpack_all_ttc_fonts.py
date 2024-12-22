from fontTools.ttLib import TTCollection
import os
import sys

# 从命令行参数获取TTC文件路径
ttc_file_path = sys.argv[1]

# 加载TTC文件
ttc_collection = TTCollection(ttc_file_path)

# 获取TTC文件名（不含扩展名）
ttc_filename = os.path.splitext(os.path.basename(ttc_file_path))[0]

# 遍历TTC中的每个字体并保存为TTF文件
for index, font in enumerate(ttc_collection.fonts):
    ttf_file_path = f"{ttc_filename}_font_{index}.ttf"
    font.save(ttf_file_path)
    print(f"字体另存为 {ttf_file_path}")