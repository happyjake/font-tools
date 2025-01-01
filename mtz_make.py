import sys
import os
import zipfile
import tempfile
import shutil
from mtz_description import generate_description_xml
from mtz_logo import create_logo
from mtz_preview import create_preview
from fontTools.ttLib import TTFont

def get_full_font_name(font_path):
    tt = TTFont(font_path)
    full_name = os.path.splitext(os.path.basename(font_path))[0]
    if 'name' in tt:
        for record in tt['name'].names:
            if record.nameID == 4:
                try:
                    full_name = record.toUnicode()
                    break
                except:
                    pass
    return full_name

def make_mtz(ttf_path, debug=False):
    # Convert to absolute path
    ttf_path = os.path.abspath(ttf_path)
    
    if not os.path.exists(ttf_path):
        print(f"Font file not found: {ttf_path}")
        sys.exit(1)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        if debug:
            print(f"Working in temporary directory: {temp_dir}")
        
        # 1. Get font name
        font_name = get_full_font_name(ttf_path)
        
        # 2. Copy font to temp dir
        temp_font = os.path.join(temp_dir, "Roboto-Regular.ttf")
        shutil.copy2(ttf_path, temp_font)
        
        # 3. Generate files in temp directory
        description_xml = os.path.join(temp_dir, "description.xml")
        generate_description_xml(temp_font, description_xml)
        
        # 4. Change to temp dir for preview generation
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        # 5. Create preview images using local font copy
        create_logo("Sample", temp_font)
        create_preview(temp_font)
        
        # 6. Create .mtz in original directory
        mtz_filename = os.path.join(original_dir, f"{font_name}.mtz")
        with zipfile.ZipFile(mtz_filename, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write("description.xml", "description.xml")
            zf.write("Roboto-Regular.ttf", "fonts/Roboto-Regular.ttf")
            if os.path.exists("preview_fonts_0.jpg"):
                zf.write("preview_fonts_0.jpg", "preview/preview_fonts_0.jpg")
            if os.path.exists("preview_fonts_small_0.png"):
                zf.write("preview_fonts_small_0.png", "preview/preview_fonts_small_0.png")
        
        os.chdir(original_dir)
        print(f"Created {mtz_filename}")
        
        if debug:
            print("Debug mode: Temporary files preserved in:", temp_dir)
            temp_dir = None


if __name__ == "__main__":
    if len(sys.argv) not in [2, 3]:
        print("Usage: python mtz_make.py <path/to/font.ttf> [--debug]")
        sys.exit(1)
    
    debug_mode = "--debug" in sys.argv
    ttf_path = sys.argv[1]
    make_mtz(ttf_path, debug=debug_mode)