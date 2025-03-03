import os
import sys
import xml.etree.ElementTree as ET
from fontTools.ttLib import TTFont, TTCollection

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
    19: "Sample Text",
    20: "PostScript CID",
    21: "WWS Family Name",
    22: "WWS Subfamily Name"
}

def get_tt_object(font_path, font_index=0):
    """Return a TTFont object from TTC or TTF."""
    with open(font_path, 'rb') as f:
        signature = f.read(4)
    if signature == b'ttcf':
        ttc = TTCollection(font_path)
        return ttc.fonts[font_index]
    else:
        return TTFont(font_path)

def get_name_record(tt, name_id):
    """Return the string for nameID if found, otherwise empty."""
    if 'name' in tt:
        for record in tt['name'].names:
            if record.nameID == name_id:
                try:
                    return record.toUnicode().strip()
                except:
                    return ""
    return ""

def get_font_weight_range(tt):
    """Retrieve supported weights from fvar table or return defaults."""
    if 'fvar' in tt:
        for axis in tt['fvar'].axes:
            if axis.axisTag == 'wght':
                return ",".join(str(x) for x in range(int(axis.minValue), int(axis.maxValue)+100, 100))
    return "150,200,250,300,350,400,450,500,550,600,650,700"

def generate_description_xml(font_path, output_file="description.xml", font_index=0):
    """Generate description.xml for a given TTF/TTC, saving to 'output_file'."""
    tt = get_tt_object(font_path, font_index)

    version_str = get_name_record(tt, 5) or "1.00"
    author_str = get_name_record(tt, 9) or "UnknownAuthor"
    designer_str = get_name_record(tt, 8) or "UnknownDesigner"
    full_name_str = get_name_record(tt, 4) or os.path.splitext(os.path.basename(font_path))[0]

    if version_str.lower().startswith("version "):
        version_str = version_str[8:].strip()

    font_weights = get_font_weight_range(tt)

    theme = ET.Element("theme")
    version_el = ET.SubElement(theme, "version")
    version_el.text = version_str

    ui_version_el = ET.SubElement(theme, "uiVersion")
    ui_version_el.text = "10"

    author_el = ET.SubElement(theme, "author")
    author_el.text = author_str

    designer_el = ET.SubElement(theme, "designer")
    designer_el.text = designer_str

    title_el = ET.SubElement(theme, "title")
    title_el.text = full_name_str

    desc_el = ET.SubElement(theme, "description")
    desc_el.text = full_name_str

    weight_el = ET.SubElement(theme, "fontWeight")
    weight_el.text = font_weights

    authors_el = ET.SubElement(theme, "authors")
    author_zh_el = ET.SubElement(authors_el, "author", locale="zh_CN")
    author_zh_el.text = author_str

    designers_el = ET.SubElement(theme, "designers")
    designer_zh_el = ET.SubElement(designers_el, "designer", locale="zh_CN")
    designer_zh_el.text = designer_str

    titles_el = ET.SubElement(theme, "titles")
    title_zh_el = ET.SubElement(titles_el, "title", locale="zh_CN")
    title_zh_el.text = full_name_str

    descriptions_el = ET.SubElement(theme, "descriptions")
    desc_zh_el = ET.SubElement(descriptions_el, "description", locale="zh_CN")
    desc_zh_el.text = full_name_str

    if hasattr(ET, "indent"):
        # Pretty-print for Python 3.9+
        ET.indent(theme, space="    ")

    tree = ET.ElementTree(theme)
    tree.write(output_file, encoding="UTF-8", xml_declaration=True)
    print(f"Generated description XML: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python mtz_description.py <font_file.ttf or font_file.ttc> [subfont_index]")
        sys.exit(1)

    font_file = sys.argv[1]
    index = 0
    if len(sys.argv) == 3:
        index = int(sys.argv[2])

    # Print TTF/TTC meta info 
    tt = get_tt_object(font_file, font_index=index)
    print(f"Font: {font_file}, Subfont Index: {index}")
    for record in tt['name'].names:
        meaning = NAME_ID_MEANINGS.get(record.nameID, "Unknown")
        print(f"NameID {record.nameID} ({meaning}): {record.toUnicode().strip()}")
    print(f"Weight Range: {get_font_weight_range(tt)}\n")

    generate_description_xml(font_file, "description.xml", font_index=index)
    print("Generated 'description.xml' with properly escaped XML (no CDATA).")