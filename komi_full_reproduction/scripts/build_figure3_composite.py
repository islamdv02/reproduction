#!/usr/bin/env python3
"""
build_figure3_composite.py
Assembles Figure 3 of Komi et al. (Nature Communications, 2026):
  Panel B: Eigenspectrum in complex plane with stability line Re=1, Mode 1/2 markers,
           and longitudinal Mode 1 ("Walking") vs Mode 2 ("Bounding") spatial profiles
           with motoneuron pools VM, BF, TA, Sol beside Mode 2.
  Panel E: Spatiotemporal dynamics:
           - Segmental spatial-rate image across time (T13 to S4, min to max rate [a.u.])
           - VM, BF, TA, Sol EMG traces with alternating grey phase shading (Right)
           - Right L2 and Right L5 motor outputs
           - Left L2 motor output
           - 1s time scale bar
  Panel F: Polar representation of cycle phase relationships (iL2-iL5 black, iL2-cL2 cyan)
  Panel G: Restored neuronal phase distribution (polar histogram across rhythmic neurons, R = 400)
           Labeled: METHODS-BASED RECONSTRUCTION — EXACT PHASE SUBSET UNAVAILABLE
  Panel H: Low-dimensional rotational dynamics in PC1-PC3 space (author pipeline single-loop limit cycle)

Non-published custom panels (3A connectivity matrix, 3C global input, 3D activation function)
are excluded from this reproduction composite per published panel inventory.
Canvas layout matches published Figure 3 proportions (2400 x 1940 at 300 DPI).
"""

import os
import sys
from PIL import Image, ImageDraw, ImageFont

def build_composite():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, '..'))
    sub_dir = os.path.join(root_dir, 'figures', 'subpanels_fig3')
    out_dir = os.path.join(root_dir, 'figures', 'main_figures')
    os.makedirs(out_dir, exist_ok=True)
    
    final_path = os.path.join(out_dir, 'Figure3.png')

    # Canvas dimensions: 2400 x 1940 at 300 DPI
    cw, ch = 2400, 1940
    canvas = Image.new('RGB', (cw, ch), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)

    # Fonts
    try:
        font_panel = ImageFont.truetype("arialbd.ttf", 52)
        font_sub = ImageFont.truetype("arialbd.ttf", 26)
        font_text = ImageFont.truetype("arial.ttf", 24)
    except Exception:
        font_panel = ImageFont.load_default()
        font_sub = font_panel
        font_text = font_panel

    def draw_panel_label(x, y, label):
        draw.text((x, y), label, fill=(0, 0, 0), font=font_panel)

    # =========================================================================
    # 1. Left column: Panel B (Eigenspectrum & Spatial Modes)
    # =========================================================================
    # Panel B spans the full left column: x: 50 to 790, y: 70 to 1890
    p3b_file = os.path.join(sub_dir, 'fig3b_eigenspectrum_and_modes.png')
    if os.path.exists(p3b_file):
        im3b = Image.open(p3b_file)
        w3b, h3b = 740, 1820
        im3b_resized = im3b.resize((w3b, h3b), Image.Resampling.LANCZOS)
        canvas.paste(im3b_resized, (50, 70))
        draw_panel_label(25, 30, "B")

    # =========================================================================
    # 2. Right side - Top row: Panel E (Spatiotemporal dynamics)
    # =========================================================================
    # Panel E spans: x: 840 to 2360 (width 1520), y: 70 to 1230 (height 1160)
    p3e_file = os.path.join(sub_dir, 'fig3e_spatiotemporal_dynamics.png')
    if os.path.exists(p3e_file):
        im3e = Image.open(p3e_file)
        w3e, h3e = 1520, 1160
        im3e_resized = im3e.resize((w3e, h3e), Image.Resampling.LANCZOS)
        canvas.paste(im3e_resized, (840, 70))
        draw_panel_label(815, 30, "E")

    # =========================================================================
    # 3. Right side - Bottom row: Panels F, G, H
    # =========================================================================
    # y: 1270 to 1890 (height 620). 3 panels with width 480 and 40px gaps
    y_bot = 1270
    h_bot = 620

    # Panel F: Polar phase plot (x: 840 to 1320)
    p3f_file = os.path.join(sub_dir, 'fig3f_polar_phase.png')
    if os.path.exists(p3f_file):
        im3f = Image.open(p3f_file)
        w3f, h3f = 480, 520
        im3f_resized = im3f.resize((w3f, h3f), Image.Resampling.LANCZOS)
        canvas.paste(im3f_resized, (840, y_bot))
        draw_panel_label(815, y_bot - 30, "F")

        # Legend below Panel F matching published paper
        draw.ellipse([(1080, y_bot + 530), (1098, y_bot + 548)], fill=(40, 40, 40))
        draw.text((1108, y_bot + 527), "iL2-iL5", fill=(0, 0, 0), font=font_sub)
        draw.ellipse([(1080, y_bot + 565), (1098, y_bot + 583)], fill=(64, 192, 242))
        draw.text((1108, y_bot + 562), "iL2-cL2", fill=(0, 0, 0), font=font_sub)

    # Panel G: Neuronal phase histogram (x: 1360 to 1840)
    p3g_file = os.path.join(sub_dir, 'fig3g_neuronal_phase_hist.png')
    if os.path.exists(p3g_file):
        im3g = Image.open(p3g_file)
        w3g, h3g = 480, 600
        im3g_resized = im3g.resize((w3g, h3g), Image.Resampling.LANCZOS)
        canvas.paste(im3g_resized, (1360, y_bot))
        draw_panel_label(1335, y_bot - 30, "G")

    # Panel H: PCA rotational dynamics (x: 1880 to 2360)
    p3h_file = os.path.join(sub_dir, 'fig3h_pca_limit_cycle.png')
    if os.path.exists(p3h_file):
        im3h = Image.open(p3h_file)
        w3h, h3h = 480, 580
        im3h_resized = im3h.resize((w3h, h3h), Image.Resampling.LANCZOS)
        canvas.paste(im3h_resized, (1880, y_bot + 10))
        draw_panel_label(1855, y_bot - 30, "H")

    canvas.save(final_path, "PNG", dpi=(300, 300))
    print(f"Generated Figure 3 composite: {final_path}")
    return final_path

if __name__ == '__main__':
    build_composite()

