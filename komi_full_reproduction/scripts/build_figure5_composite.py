"""
build_figure5_composite.py
Assembles Figure 5 subpanels (5A-5F) into a publication-grade composite matching
the exact 2-column, 3-row layout and dimensions of Komi et al. (2026), Figure 5.
Canvas size: 3504 x 2821 px.
"""

import os
from PIL import Image, ImageDraw, ImageFont

def autocrop(im, bg_color=(255, 255, 255), tolerance=10, pad=10):
    bg = Image.new(im.mode, im.size, bg_color)
    diff = Image.eval(im, lambda x: 255 if x > 255 - tolerance else 0)
    # Convert to grayscale
    gray = im.convert('L')
    bw = gray.point(lambda x: 0 if x > 255 - tolerance else 255, '1')
    bbox = bw.getbbox()
    if bbox:
        x0 = max(0, bbox[0] - pad)
        y0 = max(0, bbox[1] - pad)
        x1 = min(im.width, bbox[2] + pad)
        y1 = min(im.height, bbox[3] + pad)
        return im.crop((x0, y0, x1, y1))
    return im

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sub_dir = os.path.join(base_dir, 'figures', 'subpanels_fig5')
    out_dir = os.path.join(base_dir, 'figures', 'main_figures')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'Figure5.png')
    
    canvas_w = 3504
    canvas_h = 2821
    canvas = Image.new('RGB', (canvas_w, canvas_h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    
    try:
        font_letter = ImageFont.truetype("arialbd.ttf", 44)
    except:
        font_letter = ImageFont.load_default()
        
    panels_info = [
        # (panel_letter, filename, letter_pos, box_rect)
        ('A', 'fig5a_v1_anatomy_projectome.png', (45, 20), (50, 70, 1700, 950)),
        ('B', 'fig5b_v1_continuous_traces.png',   (45, 1030), (50, 1070, 1700, 1000)),
        ('C', 'fig5c_v1_quantification.png',     (45, 2100), (50, 2140, 1700, 640)),
        
        ('D', 'fig5d_v0_anatomy_projectome.png', (1785, 20), (1790, 70, 1680, 950)),
        ('E', 'fig5e_v0_continuous_traces.png',   (1785, 1030), (1790, 1070, 1680, 1000)),
        ('F', 'fig5f_v0_quantification.png',     (1785, 2100), (1790, 2140, 1680, 640)),
    ]
    
    for letter, fn, let_pos, (bx, by, bw, bh) in panels_info:
        p_path = os.path.join(sub_dir, fn)
        if not os.path.exists(p_path):
            print(f"Warning: subpanel {fn} not found in {sub_dir}")
            continue
            
        im = Image.open(p_path).convert('RGB')
        im_crop = autocrop(im, pad=8)
        
        # Fit inside bounding box preserving aspect ratio
        scale = min(bw / im_crop.width, bh / im_crop.height)
        new_w = int(im_crop.width * scale)
        new_h = int(im_crop.height * scale)
        im_resized = im_crop.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Center inside target box
        paste_x = bx + (bw - new_w) // 2
        paste_y = by + (bh - new_h) // 2
        canvas.paste(im_resized, (paste_x, paste_y))
        
        # Draw bold panel letter
        draw.text(let_pos, letter, font=font_letter, fill=(0, 0, 0))
        print(f"Pasted {fn} as Panel {letter} at ({paste_x}, {paste_y}), size ({new_w}, {new_h})")
        
    canvas.save(out_path, quality=95)
    print(f"Successfully assembled Figure 5 composite: {out_path}")

if __name__ == '__main__':
    main()
