"""
render_fig2a.py
Strictly reproduces Figure 2A of Komi et al. (Nature Communications, 2026):
  Left: scRNA-seq & spatial transcriptomics (Visium spots with Rora, V2a, V1, Mn)
  Right: 2D Probability distributions (continuous glowing density fields for Rora, V2a, V1, Mn)
  Right side colorbar: 4-strip 0-to-max gradient (Rora, V2a, V1, Mn)
"""

import os
import numpy as np
import scipy.io as sio
import scipy.ndimage as ndi
from scipy.interpolate import RegularGridInterpolator
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from PIL import Image

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.abspath(os.path.join(script_dir, '..'))
    data_file = os.path.join(root_dir, 'scratch', 'fig2a_extracted_data.mat')
    subpanel_dir = os.path.join(root_dir, 'figures', 'subpanels_fig2')
    comparison_dir = os.path.join(root_dir, 'figures', 'comparisons')
    os.makedirs(subpanel_dir, exist_ok=True)
    os.makedirs(comparison_dir, exist_ok=True)

    print("Loading extracted geometry and transcriptomics data...")
    data = sio.loadmat(data_file)
    x = data['x'].flatten()
    y = data['y'].flatten()
    lowres = np.array([str(s[0]) if len(s) > 0 and len(s[0]) > 0 else '' for s in data['lowres'].flatten()])
    cell_types = np.array([str(s[0]) if len(s) > 0 and len(s[0]) > 0 else '' for s in data['cell_types'].flatten()])
    weights = data['weights']

    gm_mask = (lowres == 'grey')
    wm_mask = (lowres == 'white')
    cord_mask = (lowres != 'DRG')
    mid_x = (x[cord_mask].min() + x[cord_mask].max()) / 2.0
    print(f"Cord spots: {np.sum(cord_mask)}, GM: {np.sum(gm_mask)}, WM: {np.sum(wm_mask)}, mid_x: {mid_x:.2f}")

    # 1. Author Spot Attribution Logic (from SpinalCordGeometry.m lines 74-100)
    gm_indices = np.where(gm_mask)[0]
    w_gm = weights[gm_mask, :]
    w_min = np.min(w_gm[w_gm > 0])
    w_gm_pos = np.where(w_gm > 0, w_gm, w_min)
    log_w = np.log(w_gm_pos)
    col_min = log_w.min(axis=0)
    col_max = log_w.max(axis=0)
    wn = (log_w - col_min) / (col_max - col_min + 1e-12)

    unique_types = []
    seen = set()
    for t in cell_types:
        if t not in seen:
            seen.add(t)
            unique_types.append(t)
    unique_types = np.array(unique_types)

    def get_spots(type_names):
        spots = set()
        for tname in type_names:
            cols = np.where(unique_types == tname)[0]
            for c in cols:
                col_vals = wn[:, c]
                order = np.argsort(col_vals)
                swno = col_vals[order]
                csum = np.cumsum(swno)
                cdwn = np.diff(csum)
                ix = np.where(cdwn > 0.4)[0] + 1
                if len(ix) == 0:
                    continue
                swn = swno[ix]
                swn_z = (swn - np.mean(swn)) / (np.std(swn) + 1e-12)
                indx = (swn_z > 1.0)
                selected_gm_sub = order[ix[indx]]
                for s in gm_indices[selected_gm_sub]:
                    spots.add(s)
        return np.array(sorted(list(spots)))

    # Exact Published Classes (from CellTypesCensus)
    s_mn = get_spots(['MN-alpha', 'MN-gamma'])
    s_v1 = get_spots(['Inhib-23', 'Inhib-24', 'Inhib-26'])
    s_v2a = get_spots(['Excit-35', 'Excit-36'])
    s_rora = get_spots(['Excit-06'])

    left_rora = [s for s in s_rora if x[s] <= mid_x]
    left_v2a = [s for s in s_v2a if x[s] <= mid_x]
    left_v1 = [s for s in s_v1 if x[s] <= mid_x]
    left_mn = [s for s in s_mn if x[s] <= mid_x]

    print(f"Left spots: Rora={len(left_rora)}, V2a={len(left_v2a)}, V1={len(left_v1)}, Mn={len(left_mn)}")

    # 2. Symmetrized Spinal Cord and Grey Matter Anatomy on Explicit Meshgrid
    H_grid, W_grid = 360, 520
    X_grid, Y_grid = np.meshgrid(np.arange(W_grid), np.arange(H_grid))

    occ_cord = np.zeros((H_grid, W_grid), dtype=float)
    occ_gm = np.zeros((H_grid, W_grid), dtype=float)

    for xi, yi in zip(x[cord_mask], y[cord_mask]):
        r, c = int(round(yi)), int(round(xi))
        if 0 <= r < H_grid and 0 <= c < W_grid:
            occ_cord[r, c] = 1.0

    for xi, yi in zip(x[gm_mask], y[gm_mask]):
        r, c = int(round(yi)), int(round(xi))
        if 0 <= r < H_grid and 0 <= c < W_grid:
            occ_gm[r, c] = 1.0

    # Symmetrize about mid_x
    sym_cord = np.zeros_like(occ_cord)
    sym_gm = np.zeros_like(occ_gm)
    for c in range(W_grid):
        c_flip = int(round(2 * mid_x - c))
        if 0 <= c_flip < W_grid:
            sym_cord[:, c] = 0.5 * (occ_cord[:, c] + occ_cord[:, c_flip])
            sym_gm[:, c] = 0.5 * (occ_gm[:, c] + occ_gm[:, c_flip])
        else:
            sym_cord[:, c] = occ_cord[:, c]
            sym_gm[:, c] = occ_gm[:, c]

    # Smooth Cord Boundary (ensures entire tissue is enclosed)
    disk_cord = (np.ogrid[-15:16, -15:16][0]**2 + np.ogrid[-15:16, -15:16][1]**2 <= 225)
    closed_cord = ndi.binary_closing(sym_cord > 0.03, structure=disk_cord)
    filled_cord = ndi.binary_fill_holes(closed_cord)
    smoothed_cord = ndi.gaussian_filter(filled_cord.astype(float), sigma=4.2)

    # Smooth Grey Matter Boundary
    disk_gm = (np.ogrid[-10:11, -10:11][0]**2 + np.ogrid[-10:11, -10:11][1]**2 <= 100)
    closed_gm = ndi.binary_closing(sym_gm > 0.05, structure=disk_gm)
    filled_gm = ndi.binary_fill_holes(closed_gm)
    smoothed_gm = ndi.gaussian_filter(filled_gm.astype(float), sigma=3.2)

    interp_cord = RegularGridInterpolator((np.arange(H_grid), np.arange(W_grid)), smoothed_cord, bounds_error=False, fill_value=0.0)
    interp_gm = RegularGridInterpolator((np.arange(H_grid), np.arange(W_grid)), smoothed_gm, bounds_error=False, fill_value=0.0)

    # 3. Continuous 2D Probability Fields on Right Hemicord
    gw, gh = 420, 500
    gx = np.linspace(mid_x, 485, gw)
    gy = np.linspace(15, 345, gh)
    GX, GY = np.meshgrid(gx, gy)

    pts_grid = np.stack([GY.ravel(), GX.ravel()], axis=-1)
    gm_vals_grid = interp_gm(pts_grid).reshape(GX.shape)
    in_gm_vals = gm_vals_grid > 0.38

    # Density computation from mirrored left spots
    def compute_continuous_density(s_idx, sigma=21.0):
        px = 2 * mid_x - x[s_idx]
        py = y[s_idx]
        d = np.zeros(GX.shape, dtype=float)
        for pxi, pyi in zip(px, py):
            d += np.exp(-0.5 * (((GX - pxi)**2 + (GY - pyi)**2) / (sigma**2)))
        d_max = d[in_gm_vals].max() if np.any(in_gm_vals) else d.max()
        if d_max > 0:
            d /= d_max
        edge_fade = np.clip((gm_vals_grid - 0.35) / 0.15, 0.0, 1.0)
        d *= edge_fade
        d[~in_gm_vals] = 0.0
        return d

    dens_rora = compute_continuous_density(left_rora, 18.0)
    dens_v2a  = compute_continuous_density(left_v2a,  24.0)
    dens_v1   = compute_continuous_density(left_v1,   20.0)
    dens_mn   = compute_continuous_density(left_mn,   18.0)

    # Published colors (from native pixel analysis)
    color_rora = np.array([235, 14, 144]) / 255.0   # #EB0E90 Hot Pink
    color_v2a  = np.array([242, 134, 184]) / 255.0  # #F286B8 Pink/Salmon
    color_v1   = np.array([109, 44, 146]) / 255.0   # #6D2C92 Deep Purple
    color_mn   = np.array([24, 148, 210]) / 255.0   # #1894D2 Ocean/Sky Blue

    # Continuous glowing RGBA composition
    rgba_right = np.zeros((gh, gw, 4), dtype=float)
    # Background fill inside right GM
    rgba_right[in_gm_vals, 0:3] = [0.935, 0.935, 0.945]
    rgba_right[in_gm_vals, 3] = 1.0

    # Layer blending: Mn, V1, V2a, Rora
    def blend_layer(base_rgba, d, color, max_alpha):
        alpha = np.clip((d - 0.05) / 0.95, 0.0, 1.0) * max_alpha
        for ch in range(3):
            base_rgba[..., ch] = base_rgba[..., ch] * (1.0 - alpha) + color[ch] * alpha

    blend_layer(rgba_right, dens_mn,   color_mn,   0.88)
    blend_layer(rgba_right, dens_v1,   color_v1,   0.85)
    blend_layer(rgba_right, dens_v2a,  color_v2a,  0.80)
    blend_layer(rgba_right, dens_rora, color_rora, 0.88)

    # 4. Matplotlib Subpanel Layout
    fig = plt.figure(figsize=(10.5, 7.6), dpi=300, facecolor='white')
    ax = fig.add_axes([0.05, 0.07, 0.82, 0.84])
    ax.set_facecolor('white')

    # Shading inside cord
    ax.contourf(X_grid, Y_grid, smoothed_cord > 0.42, levels=[0.42, 1.5], colors=['#F8F8FA'])

    # Left Grey Matter Background Shading (smooth continuous shaded butterfly)
    left_gm_grid = (smoothed_gm > 0.38) & (X_grid <= mid_x)
    ax.contourf(X_grid, Y_grid, left_gm_grid, levels=[0.5, 1.5], colors=['#DCDCE2'], zorder=1)

    # Left Background Capture Spots (strictly clipped inside the cord boundary)
    cord_vals_spots = interp_cord(np.stack([y, x], axis=-1))

    left_valid_wm = wm_mask & (x <= mid_x) & (cord_vals_spots > 0.45)
    left_valid_gm = gm_mask & (x <= mid_x) & (cord_vals_spots > 0.45)

    # White matter stippling (light grey semi-transparent circles)
    ax.scatter(x[left_valid_wm], y[left_valid_wm], s=26, c='#D4D4DC', alpha=0.55, edgecolors='none', zorder=2)

    # Grey matter spot cloud (textured semi-transparent spots over grey shading)
    ax.scatter(x[left_valid_gm], y[left_valid_gm], s=30, c='#777780', alpha=0.35, edgecolors='none', zorder=3)

    # Left Cell Population Dots (crisp, solid circles)
    dot_s = 22
    ax.scatter(x[left_mn], y[left_mn], s=dot_s, c=[color_mn], alpha=0.95, edgecolors='none', zorder=5)
    ax.scatter(x[left_v1], y[left_v1], s=dot_s, c=[color_v1], alpha=0.95, edgecolors='none', zorder=6)
    ax.scatter(x[left_v2a], y[left_v2a], s=dot_s, c=[color_v2a], alpha=0.95, edgecolors='none', zorder=7)
    ax.scatter(x[left_rora], y[left_rora], s=dot_s, c=[color_rora], alpha=0.95, edgecolors='none', zorder=8)

    # Right Smooth Continuous RGBA Probability Image
    ax.imshow(rgba_right, extent=[gx[0], gx[-1], gy[-1], gy[0]], zorder=10, interpolation='bicubic')

    # Outlines:
    # 1. Outer cord contour (smooth continuous black line)
    ax.contour(X_grid, Y_grid, smoothed_cord, levels=[0.42], colors=['#111111'], linewidths=[1.8], zorder=20)

    # 2. Grey matter contour:
    # Left & Right GM outline (soft light grey border)
    ax.contour(X_grid, Y_grid, smoothed_gm, levels=[0.38], colors=['#B5B5BD'], linewidths=[1.4], zorder=18)

    # Midline divider (dashed vertical line)
    ax.plot([mid_x, mid_x], [10, 345], '--', color='#999999', lw=1.2, dashes=(5, 5), zorder=25)

    # Text Labels on Right Probability Fields (bold white sans-serif)
    txt_eff = [path_effects.withStroke(linewidth=1.2, foreground='#333333', alpha=0.4)]
    ax.text(350, 82, r"$\mathbf{Ror\alpha}$", color='white', fontsize=16, fontweight='bold',
            ha='center', va='center', zorder=30, path_effects=txt_eff)
    ax.text(318, 175, r"$\mathbf{V2a}$", color='white', fontsize=16, fontweight='bold',
            ha='center', va='center', zorder=30, path_effects=txt_eff)
    ax.text(368, 222, r"$\mathbf{V1}$", color='white', fontsize=16, fontweight='bold',
            ha='center', va='center', zorder=30, path_effects=txt_eff)
    ax.text(412, 268, r"$\mathbf{Mn}$", color='white', fontsize=16, fontweight='bold',
            ha='center', va='center', zorder=30, path_effects=txt_eff)

    # Subpanel Headings (matching published typography)
    ax.text(25, -28, "scRNA seq. & spatial\ntranscriptomics", color='#111111', fontsize=15,
            fontweight='bold', linespacing=1.12, ha='left', va='top')
    ax.text(mid_x + 55, -28, "2D Probability", color='#111111', fontsize=15,
            fontweight='bold', ha='left', va='top')

    # Coordinate boundaries
    ax.set_xlim(5, 495)
    ax.set_ylim(350, -40)
    ax.axis('off')

    # 5. Right Side Colorbar (4 parallel vertical strips)
    cb_ax = fig.add_axes([0.89, 0.32, 0.026, 0.35])
    cb_ax.set_facecolor('white')

    N_grad = 120
    t = np.linspace(1.0, 0.0, N_grad)[:, None]

    cb_img = np.zeros((N_grad, 4, 3), dtype=float)
    for col_i, col_color in enumerate([color_rora, color_v2a, color_v1, color_mn]):
        cb_img[:, col_i, :] = t * col_color + (1.0 - t) * np.array([1.0, 1.0, 1.0])

    cb_ax.imshow(cb_img, aspect='auto', origin='upper', interpolation='bicubic')
    cb_ax.set_xticks([])
    cb_ax.set_yticks([0, N_grad - 1])
    cb_ax.set_yticklabels(['max', '0'], fontsize=11, fontweight='bold', color='#111111')
    cb_ax.yaxis.tick_right()
    cb_ax.tick_params(axis='y', length=0, pad=5)
    for spine in cb_ax.spines.values():
        spine.set_visible(False)

    # Save subpanel image
    out_subpanel = os.path.join(subpanel_dir, 'fig2a_spatial_transcriptomics.png')
    fig.savefig(out_subpanel, dpi=300, facecolor='white', bbox_inches='tight', pad_inches=0.1)
    plt.close(fig)
    print(f"Saved subpanel: {out_subpanel}")

    # Generate Side-by-Side Comparison
    pub_img_path = os.path.join(root_dir, 'scratch', 'pub_2a_native.png')
    if os.path.exists(pub_img_path):
        pub_img = Image.open(pub_img_path).convert('RGB')
        rec_img = Image.open(out_subpanel).convert('RGB')

        H_target = pub_img.height
        rec_w = int(rec_img.width * (H_target / rec_img.height))
        rec_resized = rec_img.resize((rec_w, H_target), Image.Resampling.LANCZOS)

        pad = 30
        comp_w = pub_img.width + rec_resized.width + pad
        comp_img = Image.new('RGB', (comp_w, H_target + 50), 'white')
        comp_img.paste(pub_img, (0, 40))
        comp_img.paste(rec_resized, (pub_img.width + pad, 40))

        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(comp_img)
        font = ImageFont.load_default()
        draw.text((20, 10), "PUBLISHED FIGURE 2A (Komi et al., 2026)", fill=(50, 50, 50), font=font)
        draw.text((pub_img.width + pad + 20, 10), "REPRODUCED FIGURE 2A (Author Data & Exact Methods)", fill=(50, 50, 50), font=font)

        comp_path = os.path.join(comparison_dir, 'fig2a_comparison.png')
        comp_img.save(comp_path, 'PNG')
        print(f"Saved comparison: {comp_path}")

if __name__ == '__main__':
    main()
