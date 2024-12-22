import os
from fontTools.ttLib import TTFont

def get_upm_values(directory):
    upm_list = []
    for filename in os.listdir(directory):
        if filename.endswith('.ttf'):
            font_path = os.path.join(directory, filename)
            try:
                font = TTFont(font_path)
                upm = font['head'].unitsPerEm
                upm_list.append(f"{filename}    UPM {upm}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    return upm_list

if __name__ == "__main__":
    current_directory = os.getcwd()
    upm_values = get_upm_values(current_directory)
    for item in upm_values:
        print(item)
