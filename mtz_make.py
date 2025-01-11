import sys
import os
import zipfile
import tempfile
import shutil
from mtz_description import generate_description_xml
from mtz_logo import create_logo
from mtz_preview import create_preview
from fontTools.ttLib import TTFont, TTCollection

def get_full_font_name(font_path, font_index=0):
    """Detect if font_path is TTC or TTF by reading its file header, then return the font's full name."""
    with open(font_path, 'rb') as f:
        signature = f.read(4)
    
    # If signature is b'ttcf', treat as a TrueType collection
    if signature == b'ttcf':
        ttc = TTCollection(font_path)  # remove fontNumber usage
        font = ttc.fonts[font_index]   # pick the subfont from the collection
    else:
        font = TTFont(font_path)

    # Attempt to read name table to get full name
    name_table = font['name']
    for record in name_table.names:
        if record.nameID == 4:  # Full font name
            if record.isUnicode():
                return str(record.string, 'utf-16-be').strip()
            else:
                return record.string.decode('utf-8', errors='ignore').strip()
    return "UnknownFontName"

def make_mtz(ttf_path, preview_text_path="preview.txt", debug=False):
    # Convert to absolute paths
    ttf_path = os.path.abspath(ttf_path)
    preview_text_path = os.path.abspath(preview_text_path)
    
    # Verify input files exist
    if not os.path.exists(ttf_path):
        print(f"Font file not found: {ttf_path}")
        sys.exit(1)
    if not os.path.exists(preview_text_path):
        print(f"Preview text file not found: {preview_text_path}")
        sys.exit(1)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        if debug:
            print(f"Working in temporary directory: {temp_dir}")
        
        # Copy required files to temp dir
        temp_font = os.path.join(temp_dir, "Roboto-Regular.ttf")
        temp_preview_text = os.path.join(temp_dir, "preview.txt")
        shutil.copy2(ttf_path, temp_font)
        shutil.copy2(preview_text_path, temp_preview_text)
        
        # Generate files in temp directory
        font_name = get_full_font_name(temp_font)
        description_xml = os.path.join(temp_dir, "description.xml")
        generate_description_xml(temp_font, description_xml)
        
        # Change to temp dir for preview generation
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        # Create preview images
        create_logo(font_name, temp_font)
        create_preview(temp_font)
        
        # Create .mtz in original directory
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
    if len(sys.argv) not in [2, 3, 4]:
        print("Usage: python mtz_make.py <font.ttf> [preview.txt] [--debug]")
        sys.exit(1)
    
    debug_mode = "--debug" in sys.argv
    ttf_path = sys.argv[1]
    preview_text_path = "preview.txt"
    
    if len(sys.argv) >= 3 and sys.argv[2] != "--debug":
        preview_text_path = sys.argv[2]
    
    make_mtz(ttf_path, preview_text_path, debug_mode)