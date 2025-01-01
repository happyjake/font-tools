from fontTools.ttLib import TTFont
import sys
import os

NAME_ID_MEANINGS = {
    0: "Copyright",
    1: "Font Family",
    2: "Font Subfamily",
    3: "Unique Identifier",
    4: "Full Font Name",
    5: "Version",
    6: "PostScript Name",
    7: "Trademark",
    8: "Manufacturer",
    9: "Designer",
    10: "Description",
    11: "Vendor URL",
    12: "Designer URL",
    13: "License Description",
    14: "License URL",
    16: "Preferred Family",
    17: "Preferred Subfamily",
    18: "Compatible Full",
    19: "Sample Text"
}

def list_name_records(font):
    """List all name records in the font with their meanings"""
    print("\n现有名称记录：")
    records = []
    for i, record in enumerate(font['name'].names):
        try:
            name = record.toUnicode()
            meaning = NAME_ID_MEANINGS.get(record.nameID, "Unknown")
            if record.nameID == 4:
                print(f"{i+1}.*ID {record.nameID} ({meaning}) [Full Font Name]")
            else:
                print(f"{i+1}. ID {record.nameID} ({meaning})")
            print(f"   Platform ID: {record.platformID}, Encoding ID: {record.platEncID}")
            print(f"   Language ID: {record.langID}")
            print(f"   Current value: {name}\n")
            records.append(record)
        except UnicodeDecodeError:
            print(f"{i+1}. ID {record.nameID} - Unable to decode value\n")
    return records

def modify_font_info(input_path):
    """Modify font name records"""
    # Load font
    font = TTFont(input_path)
    
    while True:
        # List current records
        records = list_name_records(font)
        
        # Get user selection
        print("\n选项：")
        print("1-N: 选择要修改的记录编号")
        print("0: 保存并退出")
        print("-1: 不保存退出")
        print("-2: 清理名称记录(仅保留默认语言)")
        
        try:
            choice = int(input("\n请选择: "))
            
            if choice == -1:
                print("退出而不保存")
                return
            elif choice == -2:
                # Required name IDs for valid font
                REQUIRED_NAME_IDS = {1, 2, 3, 4, 5, 6}
                DEFAULT_LANG_ID = 0x0409  # English (United States)
                original_count = len(font['name'].names)
                
                # First pass: collect English records
                new_names = []
                seen_nameIDs = set()
                
                # Keep English records first
                for record in font['name'].names:
                    if record.langID == DEFAULT_LANG_ID:
                        if record.nameID not in seen_nameIDs:
                            new_names.append(record)
                            seen_nameIDs.add(record.nameID)
                
                # Second pass: fill in missing required records from other languages
                for nameID in REQUIRED_NAME_IDS:
                    if nameID not in seen_nameIDs:
                        for record in font['name'].names:
                            if record.nameID == nameID:
                                new_names.append(record)
                                seen_nameIDs.add(nameID)
                                break
                
                # Replace name table
                font['name'].names = new_names
                print(f"\n已清理名称记录：")
                print(f"原始记录数：{original_count}")
                print(f"保留记录数：{len(new_names)}")
                continue
            elif choice == 0:
                # Save modified font
                base_name = os.path.basename(input_path).replace('.ttf', '').replace('.otf', '')
                dir_name = os.path.dirname(input_path)
                output_path = os.path.join(dir_name, f"信息修改_{base_name}.ttf")
                font.save(output_path)
                print(f"\n字体已保存为: {output_path}")
                return
            elif 1 <= choice <= len(records):
                # Modify selected record
                record = records[choice-1]
                print(f"\n当前值: {record.toUnicode()}")
                new_value = input("输入新值: ")
                record.string = new_value.encode('utf-16-be')
            else:
                print("\n无效选择，请重试")
        
        except ValueError:
            print("\n无效输入，请输入数字")
        except Exception as e:
            print(f"\n错误: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python modify_font_info.py <字体文件.ttf>")
        sys.exit(1)
    
    modify_font_info(sys.argv[1])