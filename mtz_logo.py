from PIL import Image, ImageDraw, ImageFont
import sys
import os

def create_logo(text, font_path, output_filename="preview_fonts_small_0.png"):
    # Fixed dimensions
    WIDTH = 1080
    HEIGHT = 155
    FONT_SIZE = int(HEIGHT * 0.8)  # 80% of height for larger words
    
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font not found: {font_path}")
    
    # Create transparent canvas
    img = Image.new('RGBA', (WIDTH, HEIGHT), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, FONT_SIZE)
    
    # Calculate positions
    text_width = font.getlength(text)
    vf_width = font.getlength("VF")
    total_width = text_width + vf_width + 20  # 20px spacing
    
    # Center text
    start_x = (WIDTH - total_width) // 2
    y_position = (HEIGHT - FONT_SIZE) // 2
    
    # Draw text
    draw.text((start_x, y_position), text, fill='black', font=font)
    draw.text((start_x + text_width + 20, y_position), "VF", fill='red', font=font)
    
    img.save(output_filename, "PNG")
    return output_filename

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python text_to_png.py <text> <font_path>")
        sys.exit(1)
    
    try:
        output_file = create_logo(sys.argv[1], sys.argv[2])
        print(f"Generated: {output_file}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)