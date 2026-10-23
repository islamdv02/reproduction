#!/usr/bin/env python3
"""
generate_figure2_3_comparisons.py
Generates side-by-side comparison images for each panel of Figures 2 and 3:
Places Published panel (left) and Reproduction panel (right) with clear headers.
Saves comparison images to figures/comparisons/:
  - fig2a_comparison.png ... fig2g_comparison.png
  - fig3a_comparison.png ... fig3h_comparison.png
"""

import os
from PIL import Image, ImageDraw, ImageFont

def make_side_by_side(pub_crop, rep_img, title, output_path, target_h=900):
    # Determine width preserving aspect ratio to target_h
    h_target = target_h
    w_pub = int(pub_crop.width * (h_target / pub_crop.height))
    w_rep = int(rep_img.width * (h_target / rep_img.height))
    
    pub_resized = pub_crop.resize((w_pub, h_target), Image.Resampling.LANCZOS)
    rep_resized = rep_img.resize((w_rep, h_target), Image.Resampling.LANCZOS)
    
    pad = 30
    header_h = 90
    total_w = w_pub + w_rep + pad * 3
    total_h = h_target + header_h + pad * 2
    
    canvas = Image.new('RGB', (total_w, total_h), (255, 255, 255))
    draw = ImageDraw.Draw(canvas)
    
    # Fonts
    font_paths = [
        "C:\\Windows\\Fonts\\arialbd.ttf",
        "C:\\Windows\\Fonts\\calibrib.ttf",
        "C:\\Windows\\Fonts\\seguiemj.ttf"
    ]
    font_file = None
    for p in font_paths:
        if os.path.exists(p):
            font_file = p
            break
            
    font_title = ImageFont.truetype(font_file, 34) if font_file else ImageFont.load_default()
    font_label = ImageFont.truetype(font_file, 26) if font_file else ImageFont.load_default()
    
    # Title
    draw.text((pad, 20), title, fill=(20, 20, 20), font=font_title)
    
    # Sub-headers
    draw.text((pad, 65), "PUBLISHED PANEL (Komi et al., 2026)", fill=(180, 40, 40), font=font_label)
    draw.text((w_pub + pad * 2, 65), "REPRODUCTION (Author Data & MATLAB Model)", fill=(20, 100, 180), font=font_label)
    
    # Paste panels
    canvas.paste(pub_resized, (pad, header_h + pad))
    canvas.paste(rep_resized, (w_pub + pad * 2, header_h + pad))
    
    # Divider line
    draw.line([(w_pub + int(pad * 1.5), header_h), (w_pub + int(pad * 1.5), total_h - pad)], fill=(200, 200, 200), width=2)
    
    canvas.save(output_path, 'PNG', quality=95)
    print(f"Saved comparison: {output_path}")

def generate_all_comparisons():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, '..'))
    pub_dir = os.path.join(root_dir, 'figures', 'published_figures')
    sub2_dir = os.path.join(root_dir, 'figures', 'subpanels_fig2')
    sub3_dir = os.path.join(root_dir, 'figures', 'subpanels_fig3')
    comp_dir = os.path.join(root_dir, 'figures', 'comparisons')
    os.makedirs(comp_dir, exist_ok=True)
    
    p2 = Image.open(os.path.join(pub_dir, 'published_figure2.jpeg'))
    p3 = Image.open(os.path.join(pub_dir, 'published_figure3.jpeg'))
    
    # Published crops for Figure 2 (size: 2082 x 1823)
    crops_fig2 = {
        '2A': (p2.crop((0, 0, 760, 560)), 'fig2a_spatial_transcriptomics.png', 'Figure 2A: Spatial Transcriptomics & Probability Fields', 'fig2a_comparison.png'),
        '2B': (p2.crop((760, 0, 2082, 560)), 'fig2b_sampling_reference.png', 'Figure 2B: Sampling & Reference Comparison (Modeled vs Histology)', 'fig2b_comparison.png'),
        '2C': (p2.crop((0, 560, 1420, 1100)), 'fig2c_directional_kernels.png', 'Figure 2C: 3D Directional Projection Kernels', 'fig2c_comparison.png'),
        '2D': (p2.crop((1420, 560, 2082, 1100)), 'fig2d_motoneuron_topography.png', 'Figure 2D: Motoneuron Pool Topography (13 Pools, T13-S4)', 'fig2d_comparison.png'),
        '2E': (p2.crop((0, 1100, 760, 1823)), 'fig2e_connectivity_matrix.png', 'Figure 2E: Connectivity Matrix W & Ipsi/Contra Split', 'fig2e_comparison.png'),
        '2F': (p2.crop((760, 1100, 1340, 1823)), 'fig2f_celltype_matrix.png', 'Figure 2F: Cell Type Interaction Matrix (9x9)', 'fig2f_comparison.png'),
        '2G': (p2.crop((1340, 1100, 2082, 1823)), 'fig2g_net_projectome.png', 'Figure 2G: Net Spinal Projectome (Ipsi & Contra)', 'fig2g_comparison.png'),
    }
    
    for panel_id, (pub_crop, rep_file, title, out_file) in crops_fig2.items():
        rep_path = os.path.join(sub2_dir, rep_file)
        if os.path.exists(rep_path):
            rep_img = Image.open(rep_path)
            out_path = os.path.join(comp_dir, out_file)
            make_side_by_side(pub_crop, rep_img, title, out_path)
        else:
            print(f"Warning: {rep_path} not found!")

    # Published crops for Figure 3 (B, E, F, G, H only - excluding non-published A, C, D)
    crops_fig3 = {
        '3B': (p3.crop((0, 380, 420, 1323)), 'fig3b_eigenspectrum_and_modes.png', 'Figure 3B: Eigenspectrum & Dominant Spatial Modes (Walking vs Bounding)', 'fig3b_comparison.png'),
        '3E': (p3.crop((390, 320, 1200, 950)), 'fig3e_spatiotemporal_dynamics.png', 'Figure 3E: Traveling Waves, EMGs & Motor Outputs', 'fig3e_comparison.png'),
        '3F': (p3.crop((390, 950, 660, 1323)), 'fig3f_polar_phase.png', 'Figure 3F: Polar Phase Relationships (27 Cycles)', 'fig3f_comparison.png'),
        '3G': (p3.crop((660, 950, 930, 1323)), 'fig3g_neuronal_phase_hist.png', 'Figure 3G: Neuronal Phase Distribution Polar Histogram', 'fig3g_comparison.png'),
        '3H': (p3.crop((930, 950, 1200, 1323)), 'fig3h_pca_limit_cycle.png', 'Figure 3H: PCA Low-Dimensional Rotational Dynamics (PC1 vs PC3)', 'fig3h_comparison.png'),
    }

    for panel_id, (pub_crop, rep_file, title, out_file) in crops_fig3.items():
        rep_path = os.path.join(sub3_dir, rep_file)
        if os.path.exists(rep_path):
            rep_img = Image.open(rep_path)
            out_path = os.path.join(comp_dir, out_file)
            make_side_by_side(pub_crop, rep_img, title, out_path)
        else:
            print(f"Warning: {rep_path} not found!")

    # Generate full Figure 3 composite comparison
    main_dir = os.path.join(root_dir, 'figures', 'main_figures')
    rep_fig3_path = os.path.join(main_dir, 'Figure3.png')
    if os.path.exists(rep_fig3_path):
        pub_crop_fig3 = p3.crop((0, 360, 1200, 1323))
        rep_fig3_img = Image.open(rep_fig3_path)
        fig3_comp_path = os.path.join(comp_dir, 'Figure3_published_vs_reproduction.png')
        make_side_by_side(pub_crop_fig3, rep_fig3_img,
                          'Figure 3: Mouse Locomotion: Emergent Spatio-Temporal Dynamics (Panels B, E, F, G, H)',
                          fig3_comp_path, target_h=1400)
        print(f"Generated Figure 3 composite comparison: {fig3_comp_path}")

if __name__ == '__main__':
    generate_all_comparisons()


