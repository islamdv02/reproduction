"""
build_figure2_composite.py
Assembles Figure 2 reproduction from the generated subpanels in figures/subpanels_fig2/
Target layout closely matches published Figure 2 (Komi et al., 2026, Nature Communications):
- 2A: Split transverse spinal cord (scRNA-seq spots & 2D probability)
- 2B: Sampling & comparison to reference markers (Mn/Chat, V2a/Vsx2)
- 2C: 3D Directional projection kernels for 9 cardinal ventral classes
- 2D: Motoneuron pool segmental topography (13 pools, vertical T13 to S4)
- 2E: Connectivity matrix W & ipsilateral / contralateral decomposition
- 2F: Cell type-to-cell type interaction matrix (9x9 normalized)
- 2G: Net spinal projectome (ipsilateral & contralateral Mexican hat curves)
"""

import os
from PIL import Image, ImageDraw, ImageFont

def build_composite():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, '..'))
    sub_dir = os.path.join(root_dir, 'figures', 'subpanels_fig2')
    main_dir = os.path.join(root_dir, 'figures', 'main_figures')
    os.makedirs(main_dir, exist_ok=True)

    # Canvas size matching high-res published proportions
    # published is 2082 x 1823. We build at 2x resolution: 4164 x 3646
    W, H = 4164, 3646
    canvas = Image.new('RGB', (W, H), 'white')
    draw = ImageDraw.Draw(canvas)

    # Font setup
    font_paths = [
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\calibrib.ttf",
        "C:\\Windows\\Fonts\\seguiemj.ttf",
    ]
    font_file = None
    for p in font_paths:
        if os.path.exists(p):
            font_file = p
            break
    
    font_label = ImageFont.truetype(font_file, 56) if font_file else ImageFont.load_default()

    def load_and_fit(filename, target_w, target_h, pad=True):
        p = os.path.join(sub_dir, filename)
        if not os.path.exists(p):
            print(f"Warning: {p} does not exist!")
            return Image.new('RGB', (target_w, target_h), 'white')
        im = Image.open(p).convert('RGBA')
        
        # Crop any excessive white border
        bg = Image.new('RGBA', im.size, (255, 255, 255, 255))
        diff = Image.fromarray(((255 - np.array(im.convert('L'))) > 5).astype('uint8') * 255)
        bbox = diff.getbbox()
        if bbox:
            im = im.crop((max(0, bbox[0]-10), max(0, bbox[1]-10), min(im.width, bbox[2]+10), min(im.height, bbox[3]+10)))
        
        # Aspect fit into target_w, target_h
        im.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
        
        # Center in white background
        res = Image.new('RGB', (target_w, target_h), 'white')
        offset_x = (target_w - im.width) // 2
        offset_y = (target_h - im.height) // 2
        res.paste(im, (offset_x, offset_y), im)
        return res

    import numpy as np

    # Layout geometry (scaled 2x from 2082x1823):
    # Row 1 (y: 60 to 1100):
    #   A: x: 100 to 1250, y: 60 to 1100 (w=1150, h=1040)
    #   B: x: 1280 to 4100, y: 60 to 1100 (w=2820, h=1040)
    # Row 2 (y: 1140 to 2200):
    #   C: x: 100 to 2850, y: 1140 to 2200 (w=2750, h=1060)
    #   D: x: 2880 to 4100, y: 1140 to 2200 (w=1220, h=1060)
    # Row 3 (y: 2240 to 3580):
    #   E: x: 100 to 1350, y: 2240 to 3580 (w=1250, h=1340)
    #   F: x: 1380 to 2650, y: 2240 to 3580 (w=1270, h=1340)
    #   G: x: 2680 to 4100, y: 2240 to 3580 (w=1420, h=1340)

    # 1. Panel A
    im_a = load_and_fit('fig2a_spatial_transcriptomics.png', 1150, 1040)
    canvas.paste(im_a, (100, 60))
    draw.text((40, 40), "A", fill="black", font=font_label)

    # 2. Panel B
    im_b = load_and_fit('fig2b_sampling_reference.png', 2820, 1040)
    canvas.paste(im_b, (1280, 60))
    draw.text((1240, 40), "B", fill="black", font=font_label)

    # 3. Panel C
    im_c = load_and_fit('fig2c_directional_kernels.png', 2750, 1060)
    canvas.paste(im_c, (100, 1140))
    draw.text((40, 1120), "C", fill="black", font=font_label)

    # 4. Panel D
    im_d = load_and_fit('fig2d_motoneuron_topography.png', 1220, 1060)
    canvas.paste(im_d, (2880, 1140))
    draw.text((2840, 1120), "D", fill="black", font=font_label)

    # 5. Panel E
    im_e = load_and_fit('fig2e_connectivity_matrix.png', 1250, 1340)
    canvas.paste(im_e, (100, 2240))
    draw.text((40, 2220), "E", fill="black", font=font_label)

    # 6. Panel F
    im_f = load_and_fit('fig2f_celltype_matrix.png', 1270, 1340)
    canvas.paste(im_f, (1380, 2240))
    draw.text((1340, 2220), "F", fill="black", font=font_label)

    # 7. Panel G
    im_g = load_and_fit('fig2g_net_projectome.png', 1420, 1340)
    canvas.paste(im_g, (2680, 2240))
    draw.text((2640, 2220), "G", fill="black", font=font_label)

    # Status footer banner (clean, matching published style)
    font_footer = ImageFont.truetype(font_file, 26) if font_file else ImageFont.load_default()
    status_text = "Figure 2: Computational Reproduction (Komi et al., Nature Communications 2026) | Method: Author Spatial Coordinates & Projectome Pipeline | MATLAB R2024b"
    draw.text((100, H - 45), status_text, fill=(120, 120, 120), font=font_footer)

    out_figure = os.path.join(main_dir, 'Figure2.png')
    canvas.save(out_figure, 'PNG', quality=95)
    print(f"Saved Figure 2: {out_figure}")

if __name__ == '__main__':
    build_composite()
