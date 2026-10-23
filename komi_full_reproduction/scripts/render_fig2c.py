"""
scripts/render_fig2c.py
Renders Figure 2C: Projection Architecture and Directional Kernels for 9 Ventral Classes.
Faithfully reproduces published Komi et al. (Nature Communications, 2026) Fig 2C:
1. Left Legend: 9 cardinal classes (MN, V0v, V0d, V1, V2a_Vsx2-, V2a_Vsx2+, V2b, V3, dI6)
   with excitatory (arrow) and inhibitory (circle) symbols.
2. Dorsoventral ribbon and DV synaptic probability profile.
3. Transverse spinal cord cross-section (front slice) with empirical soma locations and
   directional projection arrows (ipsilateral and commissural/contralateral).
4. 3D perspective spinal cord cylinder representing segments T13-S4 with rear slice
   showing longitudinal axonal projection reaches and midline dot column.
5. Ipsilateral-Contralateral ribbon and ML/CI synaptic probability profile.
6. Longitudinal (Rostro-Caudal) analytical Gaussian projection probability kernels
   along the 3D perspective floor aligned with the rear midline drop line.
"""

import os
import numpy as np
import scipy.io as sio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
import matplotlib.patches as mpatches

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    anat_file = os.path.join(root_dir, 'scratch', 'fig2c_anatomy_data.mat')
    if not os.path.exists(anat_file):
        raise FileNotFoundError(f"Missing {anat_file}")
    
    data = sio.loadmat(anat_file)
    poly_cord = data['poly_cord'].astype(float)
    poly_gm = data['poly_gm'].astype(float)
    
    # Class order matching published Fig 2C legend (top to bottom):
    # MN, V0v, V0d, V1, V2a_Vsx2-, V2a_Vsx2+, V2b, V3, dI6
    classes_leg = ['MN', 'V0v', 'V0d', 'V1', 'V2a_1', 'V2a_2', 'V2b', 'V3', 'DI6']
    labels_leg = [
        'MN',
        'V0v',
        'V0d',
        'V1',
        r'$\mathrm{V2a}_{\mathrm{Vsx2-}}$',
        r'$\mathrm{V2a}_{\mathrm{Vsx2+}}$',
        'V2b',
        'V3',
        'dI6'
    ]
    
    # Colors matching published figure & Colors.m
    colors = {
        'MN':    np.array([102, 165, 206]) / 255.0, # Blue
        'V0v':   np.array([180, 226, 224]) / 255.0, # Mint / cyan
        'V0d':   np.array([ 89, 194, 187]) / 255.0, # Teal
        'V1':    np.array([148, 108, 178]) / 255.0, # Purple
        'V2a_1': np.array([248, 199, 220]) / 255.0, # Light pink (Vsx2-)
        'V2a_2': np.array([243,  77, 175]) / 255.0, # Hot magenta (Vsx2+)
        'V2b':   np.array([228,  97, 141]) / 255.0, # Coral pink
        'V3':    np.array([227, 233,  99]) / 255.0, # Yellow-green
        'DI6':   np.array([ 91, 117, 152]) / 255.0  # Slate blue
    }
    
    # Canvas size: 15.0 x 6.02 inches at 300 DPI
    fig = plt.figure(figsize=(15.0, 6.02), dpi=300, facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1500)
    ax.set_ylim(0, 602)
    ax.axis('off')
    
    # -------------------------------------------------------------
    # 1. LEFT LEGEND
    # -------------------------------------------------------------
    
    leg_x = 68
    leg_y_start = 530
    leg_dy = 28
    
    for i, ct in enumerate(classes_leg):
        y = leg_y_start - i * leg_dy
        ax.text(leg_x, y, labels_leg[i], fontsize=12.5, va='center', ha='right', color='#222222', fontweight='bold')
        chip = Rectangle((leg_x + 10, y - 8), 16, 17, facecolor=colors[ct], edgecolor='none')
        ax.add_patch(chip)
        
    # Excitatory / Inhibitory symbols
    sym_y = leg_y_start - 9 * leg_dy - 18
    # Excitatory: line with arrow
    ax.plot([leg_x - 30, leg_x + 10], [sym_y + 10, sym_y + 10], '-', color='#555555', lw=1.5)
    ax.plot(leg_x + 10, sym_y + 10, '>', color='#555555', ms=7)
    ax.text(leg_x - 10, sym_y - 5, 'excitatory', fontsize=11, va='center', ha='center', color='#333333')
    
    # Inhibitory: line with circle
    ax.plot([leg_x - 30, leg_x + 10], [sym_y - 34, sym_y - 34], '-', color='#555555', lw=1.5)
    ax.plot(leg_x + 10, sym_y - 34, 'o', color='#555555', ms=6)
    ax.text(leg_x - 10, sym_y - 49, 'inhibitory', fontsize=11, va='center', ha='center', color='#333333')

    # -------------------------------------------------------------
    # 2. DORSOVENTRAL (DV) SCALE & PROBABILITY RIBBON
    # -------------------------------------------------------------
    dv_x = 188
    dv_y_bot = 145
    dv_y_top = 445
    dv_w = 20
    
    # Double-headed arrow: Dorsal <---> Ventral
    ax.annotate('', xy=(dv_x - 26, dv_y_top - 5), xytext=(dv_x - 26, dv_y_bot + 10),
                arrowprops=dict(arrowstyle='<->', color='#666666', lw=1.3))
    ax.text(dv_x - 38, (dv_y_top + dv_y_bot)/2 + 55, 'Dorsal', fontsize=11.5, rotation=90, va='center', ha='center', color='#222222')
    ax.text(dv_x - 38, (dv_y_top + dv_y_bot)/2 - 55, 'Ventral', fontsize=11.5, rotation=90, va='center', ha='center', color='#222222')
    
    # Scale bar: 200um
    ax.plot([dv_x - 16, dv_x - 16], [dv_y_bot, dv_y_bot + 60], '-k', lw=2.0)
    ax.text(dv_x - 14, dv_y_bot + 30, '200um', fontsize=10, rotation=90, va='center', ha='right', fontweight='bold')
    
    # Multi-color texture gradient ribbon in ventral region
    n_pts = 100
    y_vals = np.linspace(dv_y_bot, dv_y_top, n_pts)
    grad_img = np.zeros((n_pts, 15, 3))
    for idx in range(n_pts):
        frac = idx / (n_pts - 1)
        if frac < 0.35:
            col = (1 - frac/0.35) * colors['MN'] + (frac/0.35) * colors['V2b']
        elif frac < 0.70:
            f2 = (frac - 0.35) / 0.35
            col = (1 - f2) * colors['V2b'] + f2 * colors['V2a_2']
        else:
            f3 = (frac - 0.70) / 0.30
            col = (1 - f3) * colors['V2a_2'] + f3 * colors['V2a_1']
        grad_img[idx, :, :] = col
    ax.imshow(grad_img, extent=[dv_x, dv_x + dv_w, dv_y_bot, dv_y_bot + (dv_y_top - dv_y_bot)*0.55],
              origin='lower', aspect='auto', zorder=4)
    
    # Probability distribution curve along DV axis
    p_x_base = dv_x + dv_w
    p_curve = np.zeros(n_pts)
    for idx, yv in enumerate(y_vals):
        norm_y = (yv - dv_y_bot) / (dv_y_top - dv_y_bot)
        if norm_y < 0.52:
            p_curve[idx] = 1.0 - 0.08 * norm_y
        else:
            p_curve[idx] = np.exp(-0.5 * ((norm_y - 0.52) / 0.06)**2)
    
    curve_x = p_x_base + (1.0 - p_curve) * 32
    ax.plot(curve_x, y_vals, '-', color='#777777', lw=1.2, zorder=5)
    ax.plot([p_x_base + 32, p_x_base + 32], [dv_y_bot, dv_y_top], '-', color='#777777', lw=1.0, zorder=5)
    
    # Probability axis labels at top (1 on left, 0 on right)
    ax.plot([p_x_base, p_x_base + 32], [dv_y_top + 10, dv_y_top + 10], '-k', lw=1.2)
    ax.plot([p_x_base, p_x_base], [dv_y_top + 10, dv_y_top + 16], '-k', lw=1.2)
    ax.plot([p_x_base + 32, p_x_base + 32], [dv_y_top + 10, dv_y_top + 16], '-k', lw=1.2)
    ax.text(p_x_base, dv_y_top + 19, '1', fontsize=9.5, ha='center', va='bottom')
    ax.text(p_x_base + 32, dv_y_top + 19, '0', fontsize=9.5, ha='center', va='bottom')
    ax.text(p_x_base + 16, dv_y_top + 32, 'Prob. of syn.', fontsize=10.5, ha='center', va='bottom', color='#222222')

    # -------------------------------------------------------------
    # 3. TRANSVERSE SPINAL CORD ANATOMY (FRONT & REAR 3D PERSPECTIVE)
    # -------------------------------------------------------------
    orig_mid_x = (np.min(poly_cord[:, 0]) + np.max(poly_cord[:, 0])) / 2.0
    orig_min_y = np.min(poly_cord[:, 1])
    orig_max_y = np.max(poly_cord[:, 1])
    
    scale_w = 440.0 / (np.max(poly_cord[:, 0]) - np.min(poly_cord[:, 0]))
    scale_h = 295.0 / (orig_max_y - orig_min_y)
    front_cx = 450
    front_cy = 310
    
    def transform_pt(x, y, offset_x=0, offset_y=0, scale=1.0):
        tx = front_cx + (x - orig_mid_x) * scale_w * scale + offset_x
        ty = front_cy - (y - (orig_min_y + orig_max_y)/2.0) * scale_h * scale + offset_y
        return tx, ty
    
    front_cord_pts = np.array([transform_pt(pt[0], pt[1]) for pt in poly_cord])
    front_gm_pts = np.array([transform_pt(pt[0], pt[1]) for pt in poly_gm])
    
    # Rear slice in 3D perspective: shifted right (+460) and slightly up (+85), scale 0.86
    rear_dx = 460
    rear_dy = 85
    rear_scale = 0.86
    rear_cord_pts = np.array([transform_pt(pt[0], pt[1], rear_dx, rear_dy, rear_scale) for pt in poly_cord])
    rear_gm_pts = np.array([transform_pt(pt[0], pt[1], rear_dx, rear_dy, rear_scale) for pt in poly_gm])
    
    # Cylinder title centered above cylinder
    ax.text((front_cx + front_cx + rear_dx)/2, front_cy + 252, 'Segments T13-S4',
            fontsize=15, fontweight='bold', ha='center', va='bottom', color='#222222')
    
    # 3.1 3D Perspective Connecting Cylinder Hull
    top_front_idx = np.argmax(front_cord_pts[:, 1])
    top_rear_idx = np.argmax(rear_cord_pts[:, 1])
    bot_front_idx = np.argmin(front_cord_pts[:, 1])
    bot_rear_idx = np.argmin(rear_cord_pts[:, 1])
    right_front_idx = np.argmax(front_cord_pts[:, 0])
    right_rear_idx = np.argmax(rear_cord_pts[:, 0])
    
    # Shaded volume between front and rear slices
    hull_pts = [
        (front_cord_pts[top_front_idx, 0], front_cord_pts[top_front_idx, 1]),
        (rear_cord_pts[top_rear_idx, 0], rear_cord_pts[top_rear_idx, 1]),
        (rear_cord_pts[right_rear_idx, 0], rear_cord_pts[right_rear_idx, 1]),
        (rear_cord_pts[bot_rear_idx, 0], rear_cord_pts[bot_rear_idx, 1]),
        (front_cord_pts[bot_front_idx, 0], front_cord_pts[bot_front_idx, 1]),
    ]
    ax.add_patch(Polygon(hull_pts, facecolor='#F7F8FA', edgecolor='none', zorder=1))
    
    # Perspective connecting tangent lines
    ax.plot([front_cord_pts[top_front_idx, 0], rear_cord_pts[top_rear_idx, 0]],
            [front_cord_pts[top_front_idx, 1], rear_cord_pts[top_rear_idx, 1]], '-', color='#999999', lw=1.2, zorder=2)
    ax.plot([front_cord_pts[bot_front_idx, 0], rear_cord_pts[bot_rear_idx, 0]],
            [front_cord_pts[bot_front_idx, 1], rear_cord_pts[bot_rear_idx, 1]], '-', color='#999999', lw=1.2, zorder=2)
    
    # 3.2 Rear Slice
    ax.add_patch(Polygon(rear_cord_pts, facecolor='#FFFFFF', edgecolor='#A5AAB2', lw=1.2, zorder=2))
    ax.add_patch(Polygon(rear_gm_pts, facecolor='#E3E6EA', edgecolor='none', zorder=3))
    
    # Rear midline
    rear_mid_x = front_cx + rear_dx
    ax.plot([rear_mid_x, rear_mid_x], [rear_cord_pts[:, 1].min() - 8, rear_cord_pts[:, 1].max() + 8],
            '--', color='#B0B5BD', lw=1.1, zorder=3)
            
    # Connecting longitudinal center axis
    ax.plot([front_cx, rear_mid_x], [front_cy, front_cy + rear_dy],
            '--', color='#C0C4CB', lw=1.0, zorder=3)
    
    # 3.3 Rear Slice Vertical Column of Somas & Directional Projections (Exact Author Layout)
    rear_soma_x = rear_mid_x
    rear_soma_y_start = rear_dy + front_cy + 52
    rear_classes = ['V2a_1', 'V2a_2', 'V0d', 'V0v', 'V1', 'V2b', 'DI6', 'V3', 'MN']
    
    for k, ct in enumerate(rear_classes):
        sy = rear_soma_y_start - k * 14.2
        ax.plot(rear_soma_x, sy, 'o', color=colors[ct], ms=8.5, markeredgewidth=0, zorder=12)
        
        # Exact directional arrows matching published rear face:
        if ct == 'V2a_1': # Pink (Vsx2-): long bilateral line with triangles on both sides
            ax.plot([rear_soma_x - 170, rear_soma_x + 175], [sy - 10, sy + 10], '-', color='#777777', lw=1.2, zorder=11)
            ax.plot(rear_soma_x - 170, sy - 10, '<', color='#777777', ms=5.5, zorder=12)
            ax.plot(rear_soma_x + 175, sy + 10, '>', color='#777777', ms=5.5, zorder=12)
        elif ct == 'V2a_2': # Hot magenta (Vsx2+): local bilateral arrows
            ax.plot([rear_soma_x - 14, rear_soma_x + 14], [sy, sy], '-', color='#777777', lw=1.2, zorder=11)
            ax.plot(rear_soma_x - 14, sy, '<', color='#777777', ms=5.0, zorder=12)
            ax.plot(rear_soma_x + 14, sy, '>', color='#777777', ms=5.0, zorder=12)
        elif ct == 'V0d': # Teal: dots on both sides
            ax.plot([rear_soma_x - 10, rear_soma_x + 10], [sy, sy], '-', color='#777777', lw=1.2, zorder=11)
            ax.plot(rear_soma_x - 10, sy, 'o', color='#777777', ms=4.5, zorder=12)
            ax.plot(rear_soma_x + 10, sy, 'o', color='#777777', ms=4.5, zorder=12)
        elif ct == 'V0v': # Cyan: long line left with triangle, dot on right
            ax.plot([rear_soma_x - 85, rear_soma_x + 10], [sy - 5, sy], '-', color='#777777', lw=1.2, zorder=11)
            ax.plot(rear_soma_x - 85, sy - 5, '<', color='#777777', ms=5.5, zorder=12)
            ax.plot(rear_soma_x + 10, sy, 'o', color='#777777', ms=4.5, zorder=12)
        elif ct == 'V1': # Purple: medium line left with circle, dot on right
            ax.plot([rear_soma_x - 45, rear_soma_x + 10], [sy - 2, sy], '-', color='#777777', lw=1.2, zorder=11)
            ax.plot(rear_soma_x - 45, sy - 2, 'o', color='#777777', ms=5.0, zorder=12)
            ax.plot(rear_soma_x + 10, sy, 'o', color='#777777', ms=4.5, zorder=12)
        elif ct == 'V2b': # Coral: dot on left, long line right with circle
            ax.plot([rear_soma_x - 10, rear_soma_x + 100], [sy, sy + 6], '-', color='#777777', lw=1.2, zorder=11)
            ax.plot(rear_soma_x - 10, sy, 'o', color='#777777', ms=4.5, zorder=12)
            ax.plot(rear_soma_x + 100, sy + 6, 'o', color='#777777', ms=5.0, zorder=12)
        elif ct == 'DI6': # Slate blue: dot on left, long line right with circle
            ax.plot([rear_soma_x - 10, rear_soma_x + 120], [sy, sy + 8], '-', color='#777777', lw=1.2, zorder=11)
            ax.plot(rear_soma_x - 10, sy, 'o', color='#777777', ms=4.5, zorder=12)
            ax.plot(rear_soma_x + 120, sy + 8, 'o', color='#777777', ms=5.0, zorder=12)
        elif ct == 'V3': # Yellow: triangles on both sides
            ax.plot([rear_soma_x - 14, rear_soma_x + 14], [sy, sy], '-', color='#777777', lw=1.2, zorder=11)
            ax.plot(rear_soma_x - 14, sy, '<', color='#777777', ms=5.0, zorder=12)
            ax.plot(rear_soma_x + 14, sy, '>', color='#777777', ms=5.0, zorder=12)
        elif ct == 'MN': # Blue: triangles on both sides
            ax.plot([rear_soma_x - 14, rear_soma_x + 14], [sy, sy], '-', color='#777777', lw=1.2, zorder=11)
            ax.plot(rear_soma_x - 14, sy, '<', color='#777777', ms=5.0, zorder=12)
            ax.plot(rear_soma_x + 14, sy, '>', color='#777777', ms=5.0, zorder=12)

    # 3.4 Front Slice (Crisp White Foreground with Grey Matter Butterfly)
    ax.add_patch(Polygon(front_cord_pts, facecolor='#FFFFFF', edgecolor='#111111', lw=1.8, zorder=6))
    ax.add_patch(Polygon(front_gm_pts, facecolor='#DFE2E6', edgecolor='none', zorder=7))
    
    # Front vertical midline
    ax.plot([front_cx, front_cx], [front_cord_pts[:, 1].min() - 10, front_cord_pts[:, 1].max() + 10],
            '--', color='#777777', lw=1.2, zorder=8)
            
    # Front horizontal slanted midline connecting to DV ribbon
    ax.plot([front_cx - 280, front_cx + 250], [front_cy + 18, front_cy - 12],
            '--', color='#888888', lw=1.0, zorder=8)
            
    # 3.5 Somas and Projection Arrows on Left Hemicord
    soma_coords = {
        'V2a_1': (front_cx - 90, front_cy + 52),   # Pink (Vsx2-): dorsal
        'V2a_2': (front_cx - 34, front_cy + 30),   # Magenta (Vsx2+): medial
        'V2b':   (front_cx - 60, front_cy - 10),   # Coral: intermediate
        'V1':    (front_cx - 105, front_cy - 30),  # Purple: lateral
        'V0d':   (front_cx - 24, front_cy + 8),    # Teal: medial
        'V0v':   (front_cx - 24, front_cy - 18),   # Cyan: medial
        'DI6':   (front_cx - 48, front_cy - 52),   # Slate blue: medial
        'V3':    (front_cx - 45, front_cy - 85),   # Yellow: ventral
        'MN':    (front_cx - 130, front_cy - 95),  # Motor column: ventrolateral
    }
    
    # Projections on front face matching published layout
    for ct, (sx, sy) in soma_coords.items():
        ax.plot(sx, sy, 'o', color=colors[ct], ms=11.5, markeredgewidth=0, zorder=11)
        
        if ct == 'V2a_1': # Pink: stem down with excitatory triangle
            ax.plot([sx, sx], [sy - 8, sy - 35], '-', color='#555555', lw=1.3, zorder=10)
            ax.plot(sx, sy - 35, '^', color='#555555', ms=5.5, zorder=10)
        elif ct == 'V2a_2': # Magenta: stem down with excitatory triangle
            ax.plot([sx, sx], [sy - 8, sy - 38], '-', color='#555555', lw=1.3, zorder=10)
            ax.plot(sx, sy - 38, '^', color='#555555', ms=5.5, zorder=10)
        elif ct == 'V2b': # Coral: stem down with inhibitory circle
            ax.plot([sx, sx], [sy - 8, sy - 34], '-', color='#555555', lw=1.3, zorder=10)
            ax.plot(sx, sy - 34, 'o', color='#555555', ms=5.0, zorder=10)
        elif ct == 'V1': # Purple: stem down with inhibitory circle
            ax.plot([sx, sx], [sy - 8, sy - 34], '-', color='#555555', lw=1.3, zorder=10)
            ax.plot(sx, sy - 34, 'o', color='#555555', ms=5.0, zorder=10)
        elif ct == 'MN': # Blue: lateral collaterals on both sides
            ax.plot([sx - 18, sx + 18], [sy, sy], '-', color='#555555', lw=1.3, zorder=10)
            ax.plot(sx - 18, sy, '<', color='#555555', ms=5.5, zorder=10)
            ax.plot(sx + 18, sy, '>', color='#555555', ms=5.5, zorder=10)
        elif ct == 'V0d': # Teal: commissural crossing to right, circle
            ax.plot([sx + 8, front_cx + 72], [sy, sy - 4], '-', color='#555555', lw=1.3, zorder=10)
            ax.plot(front_cx + 72, sy - 4, 'o', color='#555555', ms=5.0, zorder=10)
        elif ct == 'V0v': # Cyan: commissural crossing to right, triangle
            ax.plot([sx + 8, front_cx + 76], [sy, sy - 5], '-', color='#555555', lw=1.3, zorder=10)
            ax.plot(front_cx + 76, sy - 5, '>', color='#555555', ms=5.5, zorder=10)
        elif ct == 'DI6': # Slate blue: commissural crossing to right, circle
            ax.plot([sx + 8, front_cx + 105], [sy, sy - 8], '-', color='#555555', lw=1.3, zorder=10)
            ax.plot(front_cx + 105, sy - 8, 'o', color='#555555', ms=5.0, zorder=10)
        elif ct == 'V3': # Yellow: commissural crossing to right, triangle
            ax.plot([sx + 8, front_cx + 115], [sy, sy - 10], '-', color='#555555', lw=1.3, zorder=10)
            ax.plot(front_cx + 115, sy - 10, '>', color='#555555', ms=5.5, zorder=10)

    # -------------------------------------------------------------
    # 4. IPSILATERAL-CONTRALATERAL (ML/CI) SCALE & RIBBON
    # -------------------------------------------------------------
    ci_y = 52
    ci_w_half = 110
    ci_h = 24
    ci_x_mid = front_cx
    
    # Double-headed arrow: Ipsilateral <---> Contralateral
    ax.annotate('', xy=(ci_x_mid - ci_w_half + 10, ci_y + ci_h + 18),
                xytext=(ci_x_mid + ci_w_half - 10, ci_y + ci_h + 18),
                arrowprops=dict(arrowstyle='<->', color='#666666', lw=1.3))
    ax.text(ci_x_mid - ci_w_half/2, ci_y + ci_h + 24, 'Ipsilateral', fontsize=12, ha='center', va='bottom', color='#222222')
    ax.text(ci_x_mid + ci_w_half/2, ci_y + ci_h + 24, 'Contralateral', fontsize=12, ha='center', va='bottom', color='#222222')
    
    # Scale bar: 200um
    ax.plot([ci_x_mid - ci_w_half, ci_x_mid - ci_w_half + 45], [ci_y - 12, ci_y - 12], '-k', lw=2.0)
    ax.text(ci_x_mid - ci_w_half + 22, ci_y - 24, '200um', fontsize=10, ha='center', va='top', fontweight='bold')
    
    # Horizontal gradient ribbons
    n_ci = 100
    ci_img_l = np.zeros((15, n_ci, 3))
    for idx in range(n_ci):
        frac = idx / (n_ci - 1)
        ci_img_l[:, idx, :] = (1 - frac) * colors['V1'] + frac * colors['V2a_2']
    ax.imshow(ci_img_l, extent=[ci_x_mid - ci_w_half, ci_x_mid - 2, ci_y, ci_y + ci_h], origin='lower', aspect='auto')
    
    ci_img_r = np.zeros((15, n_ci, 3))
    for idx in range(n_ci):
        frac = idx / (n_ci - 1)
        ci_img_r[:, idx, :] = (1 - frac) * colors['V0d'] + frac * colors['V3']
    ax.imshow(ci_img_r, extent=[ci_x_mid + 2, ci_x_mid + ci_w_half, ci_y, ci_y + ci_h], origin='lower', aspect='auto')
    
    # Axis for Prob. of syn. on CI ribbon
    p_ci_x = ci_x_mid - ci_w_half - 12
    ax.plot([p_ci_x, p_ci_x], [ci_y, ci_y + ci_h], '-k', lw=1.2)
    ax.plot([p_ci_x - 6, p_ci_x], [ci_y, ci_y], '-k', lw=1.2)
    ax.plot([p_ci_x - 6, p_ci_x], [ci_y + ci_h, ci_y + ci_h], '-k', lw=1.2)
    ax.text(p_ci_x - 10, ci_y, '0', fontsize=9.5, ha='right', va='center')
    ax.text(p_ci_x - 10, ci_y + ci_h, '1', fontsize=9.5, ha='right', va='center')
    ax.text(p_ci_x - 22, ci_y + ci_h/2, 'Prob. of syn.', fontsize=10.5, rotation=90, ha='center', va='center', color='#222222')

    # -------------------------------------------------------------
    # 5. LONGITUDINAL (ROSTROCAUDAL, RC) GAUSSIAN KERNELS ALONG 3D FLOOR
    # -------------------------------------------------------------
    # Centered directly under the rear slice midline drop line!
    rc_mid_x = rear_mid_x
    rc_base_y = 52
    rc_slope = 0.082
    rc_w_half = 255
    rc_h_max = 75
    
    # Vertical drop line from rear slice midline to RC axis center (0 um)
    ax.plot([rear_mid_x, rear_mid_x], [rear_cord_pts[:, 1].min() - 8, rc_base_y],
            '--', color='#B0B5BD', lw=1.1, zorder=2)
    
    # Double-headed arrow: Rostro <---> Caudal
    ax.annotate('', xy=(rc_mid_x - 120, rc_base_y + rc_slope*(-120) + rc_h_max + 22),
                xytext=(rc_mid_x + 120, rc_base_y + rc_slope*(120) + rc_h_max + 22),
                arrowprops=dict(arrowstyle='<->', color='#666666', lw=1.3))
    ax.text(rc_mid_x - 145, rc_base_y + rc_slope*(-145) + rc_h_max + 22, 'Rostro', fontsize=13, ha='right', va='center', color='#222222')
    ax.text(rc_mid_x + 145, rc_base_y + rc_slope*(145) + rc_h_max + 22, 'Caudal', fontsize=13, ha='left', va='center', color='#222222')
    
    # 2000 um scale bar along tilted baseline
    scale_len = 65
    scale_x0 = rc_mid_x - 180
    scale_x1 = scale_x0 + scale_len
    scale_y0 = rc_base_y + rc_slope * (scale_x0 - rc_mid_x) - 16
    scale_y1 = rc_base_y + rc_slope * (scale_x1 - rc_mid_x) - 16
    ax.plot([scale_x0, scale_x1], [scale_y0, scale_y1], '-k', lw=2.0)
    ax.text((scale_x0 + scale_x1)/2, (scale_y0 + scale_y1)/2 - 12, '2000um', fontsize=10, ha='center', va='top', fontweight='bold')
    
    # Vertical axis for Prob. of syn. (0 to 1) at right end
    p_rc_x = rc_mid_x + rc_w_half + 25
    p_rc_y0 = rc_base_y + rc_slope * (p_rc_x - rc_mid_x)
    p_rc_y1 = p_rc_y0 + rc_h_max
    ax.plot([p_rc_x, p_rc_x], [p_rc_y0, p_rc_y1], '-k', lw=1.2)
    ax.plot([p_rc_x, p_rc_x + 6], [p_rc_y0, p_rc_y0], '-k', lw=1.2)
    ax.plot([p_rc_x, p_rc_x + 6], [p_rc_y1, p_rc_y1], '-k', lw=1.2)
    ax.text(p_rc_x + 10, p_rc_y0, '0', fontsize=11, ha='left', va='center')
    ax.text(p_rc_x + 10, p_rc_y1, '1', fontsize=11, ha='left', va='center')
    
    # Ground baseline line
    x_line = np.linspace(rc_mid_x - rc_w_half - 15, rc_mid_x + rc_w_half + 15, 300)
    y_line = rc_base_y + rc_slope * (x_line - rc_mid_x)
    ax.plot(x_line, y_line, '-', color='#333333', lw=1.2, zorder=5)
            
    # Gaussian projection kernels
    d_rc = np.linspace(-8000, 8000, 800)
    sigma_spatial = 500.0 # um (projwidth)
    
    def eval_gaussian(L, bias_type):
        if bias_type == 'ro':
            return np.exp(-0.5 * ((d_rc + L) / sigma_spatial)**2)
        elif bias_type == 'cau':
            return np.exp(-0.5 * ((d_rc - L) / sigma_spatial)**2)
        elif bias_type == 'bi':
            return np.exp(-0.5 * ((np.abs(d_rc) - L) / sigma_spatial)**2)
        else: # 'loc'
            return np.exp(-0.5 * (d_rc / L)**2)
            
    x_coords = rc_mid_x + (d_rc / 8000.0) * rc_w_half
    y_base = rc_base_y + rc_slope * (x_coords - rc_mid_x)
    
    # Kernel specifications matching InstantiateModel.m:
    # 1. Bilateral V2a-2 (pink, +/- 7000 um)
    # 2. V0v (cyan, -3400 um)
    # 3. V1 (purple, -2000 um)
    # 4. V0d (teal, local 500 um)
    # 5. V3 (yellow, +500 um)
    # 6. V2a-1 (magenta, +500 um)
    # 7. V2b (coral, +4000 um)
    # 8. dI6 (slate blue, +5000 um)
    kernel_specs = [
        ('V2a_1', 7000, 'bi',  colors['V2a_1']), # Bilateral (pink)
        ('V0v',   3400, 'ro',  colors['V0v']),   # Rostral (cyan)
        ('V1',    2000, 'ro',  colors['V1']),    # Rostral (purple)
        ('V0d',    500, 'loc', colors['V0d']),   # Local (teal)
        ('V3',     500, 'cau', colors['V3']),    # Caudal (yellow)
        ('V2a_2',  500, 'cau', colors['V2a_2']), # Caudal (magenta)
        ('V2b',   4000, 'cau', colors['V2b']),   # Caudal (coral)
        ('DI6',   5000, 'cau', colors['DI6']),   # Caudal (slate blue)
    ]
    
    for ct, L, b_type, col in kernel_specs:
        p_val = eval_gaussian(L, b_type)
        y_coords = y_base + p_val * rc_h_max
        ax.fill_between(x_coords, y_base, y_coords, facecolor=col, alpha=0.45, edgecolor='none', zorder=6)
        ax.plot(x_coords, y_coords, '-', color=col, lw=1.3, zorder=7)
        
    # -------------------------------------------------------------
    # 6. SCIENTIFIC CLASSIFICATION LABEL
    # -------------------------------------------------------------
    ax.text(750, 8,
            'METHODS-BASED RECONSTRUCTION (ROSTROCAUDAL PROJECTIONS) / CONCEPTUAL REDRAWING (SCHEMATIC)',
            fontsize=8.5, ha='center', va='bottom', color='#888888', style='italic', family='sans-serif')

    out_png = os.path.join(root_dir, 'figures', 'subpanels_fig2', 'fig2c_directional_kernels.png')
    fig.savefig(out_png, dpi=300, facecolor='white')
    plt.close(fig)
    print(f"Saved corrected Figure 2C to: {out_png}")

if __name__ == '__main__':
    main()
