#!/usr/bin/env python3
"""
build_figure4_composite.py
Assemble the reproduced Figure 4 subpanels into the final candidate composite
matching the exact published layout, dimensions (5080 x 4509), and proportions of Komi et al. (2026).

Layout:
  - Top-Left:     4A (Activation function curves)
  - Top-Right:    4C (Descending drive & gain profiles + modulated effective projectomes)
  - Middle-Left:  4B (Descending tracts anatomy & target receptor radar plots)
  - Middle-Right: 4D (Multi-gait continuous raster, EMGs, and motor outputs across Walk -> Trot -> Bound)
  - Bottom-Left:  4E (Polar phase transitions)
  - Bottom-Mid:   4F (Locomotor frequency across gaits)
  - Bottom-Right: 4G (Nerve and muscle amplitudes across gaits)
"""

import os
from PIL import Image, ImageDraw, ImageFont

def build_composite():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sub_dir = os.path.join(base_dir, 'figures', 'subpanels_fig4')
    out_dir = os.path.join(base_dir, 'figures', 'main_figures')
    os.makedirs(out_dir, exist_ok=True)
    
    out_figure = os.path.join(out_dir, 'Figure4.png')
    
    # Target canvas dimensions matching published figure 4
    canvas_w = 5080
    canvas_h = 4509
    
    canvas = Image.new('RGB', (canvas_w, canvas_h), color=(255, 255, 255))
    
    # Paths to subpanels
    p_4a = os.path.join(sub_dir, 'fig4a_activation_functions.png')
    p_4b = os.path.join(sub_dir, 'fig4b_descending_tracts.png')
    p_4c = os.path.join(sub_dir, 'fig4c_modulated_projectome.png')
    p_4d = os.path.join(sub_dir, 'fig4d_gait_patterns.png')
    p_4e = os.path.join(sub_dir, 'fig4e_polar_phase_transitions.png')
    p_4f = os.path.join(sub_dir, 'fig4f_frequency.png')
    p_4g = os.path.join(sub_dir, 'fig4g_amplitudes.png')
    
    # Helper to paste with aspect ratio preservation
    def paste_subpanel(path, box):
        if not os.path.exists(path):
            print(f"Warning: subpanel missing: {path}")
            return
        im = Image.open(path).convert('RGB')
        bx, by, bw, bh = box
        # Scale to fit box while preserving aspect ratio
        im_w, im_h = im.size
        scale = min(bw / im_w, bh / im_h)
        nw, nh = int(im_w * scale), int(im_h * scale)
        im_resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
        # Center in box
        px = bx + (bw - nw) // 2
        py = by + (bh - nh) // 2
        canvas.paste(im_resized, (px, py))
        print(f"Pasted {os.path.basename(path)} at ({px}, {py}), size ({nw}, {nh})")
    
    # Coordinates matching published Figure 4
    # 4A: Top Left (x: 80, y: 80, w: 1600, h: 1150)
    paste_subpanel(p_4a, (80, 80, 1600, 1150))
    
    # 4C: Top Right (x: 1750, y: 80, w: 3250, h: 1150)
    paste_subpanel(p_4c, (1750, 80, 3250, 1150))
    
    # 4B: Middle Left (x: 80, y: 1260, w: 1650, h: 2000)
    paste_subpanel(p_4b, (80, 1260, 1650, 2000))
    
    # 4D: Middle Right (x: 1750, y: 1260, w: 3250, h: 2000)
    paste_subpanel(p_4d, (1750, 1260, 3250, 2000))
    
    # 4E: Bottom Left (x: 80, y: 3300, w: 1750, h: 1120)
    paste_subpanel(p_4e, (80, 3300, 1750, 1120))
    
    # 4F: Bottom Mid (x: 1880, y: 3300, w: 750, h: 1120)
    paste_subpanel(p_4f, (1880, 3300, 750, 1120))
    
    # 4G: Bottom Right (x: 2650, y: 3300, w: 2350, h: 1120)
    paste_subpanel(p_4g, (2650, 3300, 2350, 1120))
    
    canvas.save(out_figure, quality=95)
    print(f"Successfully generated Figure 4 composite: {out_figure}")

if __name__ == '__main__':
    build_composite()
