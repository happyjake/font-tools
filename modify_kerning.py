import sys
import os
import tempfile
from fontTools.ttLib import TTFont
from fontTools.feaLib.builder import Builder

if len(sys.argv) != 3:
    print("用法: python modify_kerning.py <输入TTF文件> <输出TTF文件>")
    sys.exit(1)

input_ttf = sys.argv[1]
output_ttf = sys.argv[2]

font = TTFont(input_ttf)

feature_code = """
feature kern {
    # 标点符号与字母的字距调整
    @LETTERS = [A B C D E F G H I J K L M N O P Q R S T U V W X Y Z 
                a b c d e f g h i j k l m n o p q r s t u v w x y z];
    @QUOTES = [quotesingle quotedbl quoteleft quoteright quotedblleft quotedblright];
    
    # 为所有引号类字符添加字距调整
    pos @QUOTES @LETTERS -20;
} kern;
"""

with tempfile.NamedTemporaryFile("w", suffix=".fea", delete=False) as tmp:
    tmp.write(feature_code)
    fea_path = tmp.name

try:
    builder = Builder(font, fea_path)
    builder.build()

    font.save(output_ttf)
    print(f"字体'{input_ttf}'已添加字距调整，并保存为'{output_ttf}'。")
finally:
    os.remove(fea_path)