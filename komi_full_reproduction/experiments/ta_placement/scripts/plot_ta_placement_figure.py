#!/usr/bin/env python3
"""
plot_ta_placement_figure.py
Generates the composite experimental figure: TA_Placement_Experiment.png
Investigating the anatomical appearance, motor coordination, and network dynamics
of relocating Tibialis Anterior (TA) motoneuron pool from baseline L2-L4 to anatomical L4-L5
across 5 paired network realizations under identical simulation drive and seeds.

Deliverable: komi_full_reproduction/experiments/ta_placement/TA_Placement_Experiment.png
Clearly labeled: "NEW EXPERIMENT — NOT A REPRODUCED PUBLICATION FIGURE."
"""

import os
import json
import h5py
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle, FancyBboxPatch

def load_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exp_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(exp_dir, 'data')
    
    json_path = os.path.join(exp_dir, 'experiment_results.json')
    with open(json_path, 'r') as f:
        json_data = json.load(f)
        
    mat_path = os.path.join(data_dir, 'plot_export.mat')
    f_mat = h5py.File(mat_path, 'r')
    pe = f_mat['pe']
    
    return json_data, pe, exp_dir

def main():
    json_data, pe, exp_dir = load_data()
    summary = json_data['summary_statistics']
    seeds = json_data['realization_seeds']
    n_real = len(seeds)
    
    # Setup Figure Layout (4 Rows + Header)
    fig = plt.figure(figsize=(20, 25), dpi=300)
    fig.patch.set_facecolor('#ffffff')
    
    # Outer layout: Header banner + 4 rows
    gs_main = gridspec.GridSpec(5, 1, height_ratios=[0.04, 0.20, 0.24, 0.24, 0.28], hspace=0.32,
                                left=0.06, right=0.96, top=0.97, bottom=0.03)
    
    # =========================================================================
    # HEADER BANNER
    # =========================================================================
    ax_hdr = fig.add_subplot(gs_main[0])
    ax_hdr.axis('off')
    
    rect = FancyBboxPatch((0.0, 0.05), 1.0, 0.90, transform=ax_hdr.transAxes,
                          facecolor='#b71c1c', edgecolor='#7f0000', linewidth=2.0,
                          boxstyle='round,pad=0.02', zorder=1)
    ax_hdr.add_patch(rect)
    
    ax_hdr.text(0.5, 0.60, "NEW EXPERIMENT — NOT A REPRODUCED PUBLICATION FIGURE",
                transform=ax_hdr.transAxes, ha='center', va='center',
                fontsize=16, fontweight='heavy', color='#ffffff', zorder=2)
    ax_hdr.text(0.5, 0.22, "First Controlled Experiment: Tibialis Anterior (TA) Motoneuron Placement (L2–L4 Baseline vs. L4–L5 Anatomical Target; Bácskai et al., 2014)",
                transform=ax_hdr.transAxes, ha='center', va='center',
                fontsize=11.5, fontweight='bold', color='#ffcdd2', zorder=2)
    
    # =========================================================================
    # ROW 1: ANATOMICAL TARGET & MOTOR POOL DISTRIBUTIONS
    # =========================================================================
    gs_row1 = gridspec.GridSpecFromSubplotSpec(1, 2, subplot_spec=gs_main[1], wspace=0.16)
    
    # ONE Verified Segment Table from matGeometry.mat
    seg_names = ['T13', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'S1', 'S2', 'S3', 'S4']
    seg_bounds = np.array([0.0, 1.3, 2.5, 4.0, 5.5, 6.8, 8.0, 9.4, 10.8, 12.0, 12.9, 13.9]) # in mm
    
    ax_anat_A = fig.add_subplot(gs_row1[0])
    ax_anat_D = fig.add_subplot(gs_row1[1])
    
    pools_base = [
        ('Iliopsoas (Hip Flex)', 7, 1.0, 3.8, '#bcbd22'),
        ('Rectus Femoris (Knee Ext)', 6, 2.5, 5.5, '#17becf'),
        ('Vastus Medialis (Knee Ext)', 5, 2.5, 5.5, '#9467bd'),
        ('Tibialis Anterior [L2–L4 Baseline]', 4, 2.77, 6.73, '#1f77b4'),
        ('Biceps Femoris (Knee Flex / Hip Ext)', 3, 3.8, 7.0, '#ff7f0e'),
        ('Gastrocnemius (Ankle Ext)', 2, 5.5, 8.2, '#d62728'),
        ('Soleus (Ankle Ext)', 1, 5.5, 8.2, '#2ca02c')
    ]
    
    pools_reloc = [
        ('Iliopsoas (Hip Flex)', 7, 1.0, 3.8, '#bcbd22'),
        ('Rectus Femoris (Knee Ext)', 6, 2.5, 5.5, '#17becf'),
        ('Vastus Medialis (Knee Ext)', 5, 2.5, 5.5, '#9467bd'),
        ('Relocated TA [L4–L5 Target]', 4, 5.60, 7.90, '#0288d1'),
        ('Biceps Femoris (Knee Flex / Hip Ext)', 3, 3.8, 7.0, '#ff7f0e'),
        ('Gastrocnemius (Ankle Ext)', 2, 5.5, 8.2, '#d62728'),
        ('Soleus (Ankle Ext)', 1, 5.5, 8.2, '#2ca02c')
    ]
    
    for ax, p_list, title, is_reloc in [
        (ax_anat_A, pools_base, "A. Baseline Motoneuron Pools (Komi et al., 2026)\nTA erroneously mapped across L2–L4 (span 3962 µm, centroid 4549 µm)", False),
        (ax_anat_D, pools_reloc, "B. Biological Relocation Target (Bácskai et al., 2014; Mus musculus)\nTA mapped to L4–L5 (span 2300 µm, compressed 41.9%, centroid 6750 µm)", True)
    ]:
        ax.set_facecolor('#fafafa')
        ax.set_title(title, fontsize=11, fontweight='bold', pad=10, color='#212121')
        ax.set_xlim(0, 13.9)
        ax.set_ylim(0.2, 8.0)
        ax.set_yticks([])
        ax.set_xlabel('Rostrocaudal Position along Spinal Cord (mm)', fontsize=10, fontweight='bold')
        
        # Draw segment bands
        for s in range(len(seg_bounds)-1):
            x0 = seg_bounds[s]
            x1 = seg_bounds[s+1]
            c = '#ffffff' if s % 2 == 0 else '#f5f5f5'
            ax.axvspan(x0, x1, color=c, alpha=0.9, zorder=0)
            ax.text((x0 + x1)/2.0, 7.6, seg_names[s], ha='center', va='center',
                    fontsize=8.5, fontweight='bold', color='#555555')
            if s > 0:
                ax.axvline(x0, color='#bdbdbd', linestyle=':', linewidth=0.8, zorder=1)
                
        # If relocated panel, draw dashed ghost of baseline TA
        if is_reloc:
            ghost_rect = Rectangle((2.77, 4 - 0.28), 6.73 - 2.77, 0.56, fill=False,
                                   edgecolor='#9e9e9e', linestyle=':', linewidth=1.5, zorder=2)
            ax.add_patch(ghost_rect)
            ax.text((2.77 + 5.5) / 2.0, 4.45, "Baseline L2–L4 position (ghost)", ha='center', va='center',
                    fontsize=7.5, fontstyle='italic', color='#616161', zorder=2)
                
        # Draw pool bars
        for name, y, x0, x1, col in p_list:
            is_ta = 'Tibialis' in name or 'TA' in name
            alpha = 1.0 if is_ta else 0.8
            lw = 2.2 if is_ta else 1.0
            ec = '#0d47a1' if (is_ta and not is_reloc) else ('#01579b' if (is_ta and is_reloc) else '#424242')
            
            rect = Rectangle((x0, y - 0.28), x1 - x0, 0.56, facecolor=col, edgecolor=ec,
                             linewidth=lw, alpha=alpha, zorder=3)
            ax.add_patch(rect)
            
            fontw = 'bold' if is_ta else 'normal'
            txt_col = '#ffffff' if (is_ta or col in ['#d62728', '#2ca02c', '#9467bd', '#1f77b4', '#0288d1']) else '#212121'
            ax.text((x0 + x1)/2.0, y, name, ha='center', va='center',
                    fontsize=8.0, fontweight=fontw, color=txt_col, zorder=4)
                    
        # Highlight Lumbar Enlargement (L2-L6: 2.5 to 9.4 mm)
        rect_le = Rectangle((2.5, 0.3), 9.4 - 2.5, 7.2, fill=False, edgecolor='#b71c1c', linestyle='--', linewidth=1.4, zorder=5)
        ax.add_patch(rect_le)
        ax.text(5.95, 0.55, "Lumbar Enlargement (L2–L6)", ha='center', va='center',
                fontsize=8.5, fontweight='bold', color='#b71c1c', backgroundcolor='#ffffff')
                
    # =========================================================================
    # ROW 2: MOTONEURON ROSTROCAUDAL ACTIVITY MAPS (CONDITIONS A, B, C, D)
    # =========================================================================
    gs_row2 = gridspec.GridSpecFromSubplotSpec(1, 4, subplot_spec=gs_main[2], wspace=0.18)
    
    t_plot_s = np.array(pe['t_rel_s']).flatten()
    y_centers = np.array(pe['b500_lumb_centers']).flatten() / 1000.0 # mm
    
    maps = [
        (np.array(pe['condA_mean_map']).T, "Condition A: Original Baseline\n(L2–L4 TA, Frozen Weights & Rates)"),
        (np.array(pe['condB_mean_map']).T, "Condition B: Coordinate-Only Control\n(L4–L5 Display, Identical W & Rates)"),
        (np.array(pe['condC_mean_map']).T, "Condition C: Same-Location Rebuild\n(L2–L4 TA, Rebuilt Connections Control)"),
        (np.array(pe['condD_mean_map']).T, "Condition D: Relocated TA Rebuilt\n(L4–L5 TA, Rebuilt Location Connections)")
    ]
    
    cmax = float(np.array(pe['common_mean_cmax']).flatten()[0]) * 0.95
    cmin = 0.0
    
    for i, (act_map, m_title) in enumerate(maps):
        ax = fig.add_subplot(gs_row2[i])
        ax.set_facecolor('#e0e0e0') # Grey for physical gaps
        
        # Plot masked heatmap
        masked_act = np.ma.masked_invalid(act_map)
        im = ax.imshow(masked_act, aspect='auto', origin='lower',
                       extent=[t_plot_s[0], t_plot_s[-1], y_centers[0] - 0.25, y_centers[-1] + 0.25],
                       cmap='viridis', vmin=cmin, vmax=cmax)
        
        ax.set_title(m_title, fontsize=10, fontweight='bold', pad=8, color='#212121')
        ax.set_xlabel('Time (s)', fontsize=9.5, fontweight='bold')
        if i == 0:
            ax.set_ylabel('Left MN RC Position (mm)', fontsize=10, fontweight='bold')
        else:
            ax.set_yticklabels([])
            
        # Draw segment horizontal lines
        for b in [4.0, 5.5, 6.8, 8.0]:
            ax.axhline(b, color='#ffffff', linestyle='--', linewidth=0.8, alpha=0.7)
        if i == 0:
            ax.text(0.05, 4.75, "L3", color='#ffffff', fontsize=8, fontweight='bold')
            ax.text(0.05, 6.15, "L4", color='#ffffff', fontsize=8, fontweight='bold')
            ax.text(0.05, 7.40, "L5", color='#ffffff', fontsize=8, fontweight='bold')
            
    # Add Colorbar for Row 2
    cbar_ax = fig.add_axes([0.965, 0.525, 0.012, 0.18])
    cb = fig.colorbar(im, cax=cbar_ax)
    cb.set_label('Mean Rate per Motoneuron (Hz)', fontsize=9.5, fontweight='bold')
    
    # =========================================================================
    # ROW 3: MOTOR POOL FIRING TRACES (CONDITIONS A, B, C, D)
    # =========================================================================
    gs_row3 = gridspec.GridSpecFromSubplotSpec(1, 4, subplot_spec=gs_main[3], wspace=0.18)
    
    traces = [
        (pe['condA_traces'], "Condition A Firing Traces\n(Baseline L2–L4 TA)"),
        (pe['condB_traces'], "Condition B Firing Traces\n(Identical Rates to A)"),
        (pe['condC_traces'], "Condition C Firing Traces\n(Same-Location Rebuilt Control)"),
        (pe['condD_traces'], "Condition D Firing Traces\n(Relocated L4–L5 Rebuilt TA)")
    ]
    
    max_trace = 0.0
    for tr, _ in traces:
        for m_name in ['ta', 'gm', 'sol', 'vm', 'bf']:
            arr = np.array(tr[m_name]).flatten()
            max_trace = max(max_trace, np.max(arr))
    max_trace *= 1.10
    
    for i, (tr, tr_title) in enumerate(traces):
        ax = fig.add_subplot(gs_row3[i])
        ax.set_facecolor('#ffffff')
        ax.set_title(tr_title, fontsize=10, fontweight='bold', pad=8, color='#212121')
        ax.set_xlim(t_plot_s[0], t_plot_s[-1])
        ax.set_ylim(0, max_trace)
        ax.set_xlabel('Time (s)', fontsize=9.5, fontweight='bold')
        if i == 0:
            ax.set_ylabel('Pool Mean Firing Rate (Hz)', fontsize=10, fontweight='bold')
        else:
            ax.set_yticklabels([])
            
        ax.plot(t_plot_s, np.array(tr['gm']).flatten(), color='#d62728', linewidth=1.6, label='GM (Ankle Ext)')
        ax.plot(t_plot_s, np.array(tr['sol']).flatten(), color='#2ca02c', linewidth=1.4, linestyle='--', label='Soleus (Ankle Ext)')
        ax.plot(t_plot_s, np.array(tr['vm']).flatten(), color='#9467bd', linewidth=1.3, alpha=0.8, label='VM (Knee Ext)')
        ax.plot(t_plot_s, np.array(tr['bf']).flatten(), color='#ff7f0e', linewidth=1.2, alpha=0.8, label='BF (Knee Flex)')
        ax.plot(t_plot_s, np.array(tr['ta']).flatten(), color='#1f77b4' if i in [0, 1, 2] else '#0288d1',
                linewidth=2.4, label='TA (Ankle Flex)')
                
        ax.grid(True, linestyle=':', alpha=0.5)
        if i == 0:
            ax.legend(loc='upper right', fontsize=7.5, framealpha=0.9)
            
    # =========================================================================
    # ROW 4: QUANTITATIVE PAIRED REALIZATION COMPARISONS (N=5)
    # =========================================================================
    gs_row4 = gridspec.GridSpecFromSubplotSpec(1, 4, subplot_spec=gs_main[4], wspace=0.22)
    
    # Panel 4A: Inter-Pool Correlation (C vs D primary, A and B shown)
    ax_4a = fig.add_subplot(gs_row4[0])
    ax_4a.set_facecolor('#ffffff')
    ax_4a.set_title("A. Muscle Pool Correlations (r)\nPrimary: C vs D (N=5 paired)", fontsize=10, fontweight='bold', pad=8)
    
    pairs = ['TA–GM', 'TA–Sol', 'TA–VM', 'TA–BF']
    x_idx = np.arange(len(pairs))
    w = 0.20
    
    r_A = [summary['condA']['ta_gm_corr']['mean'], summary['condA']['ta_sol_corr']['mean'],
           summary['condA']['ta_vm_corr']['mean'], summary['condA']['ta_bf_corr']['mean']]
    r_C = [summary['condC']['ta_gm_corr']['mean'], summary['condC']['ta_sol_corr']['mean'],
           summary['condC']['ta_vm_corr']['mean'], summary['condC']['ta_bf_corr']['mean']]
    r_D = [summary['condD']['ta_gm_corr']['mean'], summary['condD']['ta_sol_corr']['mean'],
           summary['condD']['ta_vm_corr']['mean'], summary['condD']['ta_bf_corr']['mean']]
    sem_C = [summary['condC']['ta_gm_corr']['sem'], summary['condC']['ta_sol_corr']['sem'],
             summary['condC']['ta_vm_corr']['sem'], summary['condC']['ta_bf_corr']['sem']]
    sem_D = [summary['condD']['ta_gm_corr']['sem'], summary['condD']['ta_sol_corr']['sem'],
             summary['condD']['ta_vm_corr']['sem'], summary['condD']['ta_bf_corr']['sem']]
             
    ax_4a.bar(x_idx - w, r_A, width=w, color='#757575', alpha=0.7, label='Cond A (Baseline)')
    ax_4a.bar(x_idx, r_C, width=w, yerr=sem_C, capsize=3, color='#4caf50', alpha=0.85, label='Cond C (Same-Loc Rebuild)')
    ax_4a.bar(x_idx + w, r_D, width=w, yerr=sem_D, capsize=3, color='#0288d1', alpha=0.85, label='Cond D (Relocated Rebuild)')
    
    ax_4a.axhline(0, color='#212121', linewidth=0.8)
    ax_4a.set_xticks(x_idx)
    ax_4a.set_xticklabels(pairs, fontsize=8.5, fontweight='bold')
    ax_4a.set_ylabel('Pearson Correlation Coefficient (r)', fontsize=9.5, fontweight='bold')
    ax_4a.set_ylim(-1.05, 1.05)
    ax_4a.grid(True, linestyle=':', alpha=0.5)
    ax_4a.legend(loc='lower left', fontsize=7.0, framealpha=0.9)
    
    # Panel 4B: Circular Phase Differences
    ax_4b = fig.add_subplot(gs_row4[1])
    ax_4b.set_facecolor('#ffffff')
    ax_4b.set_title("B. Circular Phase Differences (Δφ)\nRelative to TA Peak (deg)", fontsize=10, fontweight='bold', pad=8)
    
    p_C = [summary['condC']['ta_gm_phase_deg']['mean'], summary['condC']['ta_sol_phase_deg']['mean'],
           summary['condC']['ta_vm_phase_deg']['mean'], summary['condC']['ta_bf_phase_deg']['mean']]
    p_D = [summary['condD']['ta_gm_phase_deg']['mean'], summary['condD']['ta_sol_phase_deg']['mean'],
           summary['condD']['ta_vm_phase_deg']['mean'], summary['condD']['ta_bf_phase_deg']['mean']]
    sem_pC = [summary['condC']['ta_gm_phase_deg']['sem'], summary['condC']['ta_sol_phase_deg']['sem'],
              summary['condC']['ta_vm_phase_deg']['sem'], summary['condC']['ta_bf_phase_deg']['sem']]
    sem_pD = [summary['condD']['ta_gm_phase_deg']['sem'], summary['condD']['ta_sol_phase_deg']['sem'],
              summary['condD']['ta_vm_phase_deg']['sem'], summary['condD']['ta_bf_phase_deg']['sem']]
              
    ax_4b.bar(x_idx - w/2.0, p_C, width=w, yerr=sem_pC, capsize=3, color='#4caf50', alpha=0.85, label='Cond C')
    ax_4b.bar(x_idx + w/2.0, p_D, width=w, yerr=sem_pD, capsize=3, color='#0288d1', alpha=0.85, label='Cond D')
    
    ax_4b.set_xticks(x_idx)
    ax_4b.set_xticklabels(pairs, fontsize=8.5, fontweight='bold')
    ax_4b.set_ylabel('Mean Phase Difference (degrees)', fontsize=9.5, fontweight='bold')
    ax_4b.set_ylim(0, 360)
    ax_4b.axhline(180, color='#e53935', linestyle='--', linewidth=0.8, alpha=0.7, label='Antiphase (180°)')
    ax_4b.grid(True, linestyle=':', alpha=0.5)
    ax_4b.legend(loc='upper right', fontsize=7.0, framealpha=0.9)
    
    # Panel 4C: Burst Jaccard Overlap
    ax_4c = fig.add_subplot(gs_row4[2])
    ax_4c.set_facecolor('#ffffff')
    ax_4c.set_title("C. Burst Jaccard Overlap\n(|A ∩ B| / |A ∪ B| at 20% Peak)", fontsize=10, fontweight='bold', pad=8)
    
    ov_C = [summary['condC']['ta_gm_jaccard_20']['mean'], summary['condC']['ta_sol_jaccard_20']['mean'],
            summary['condC']['ta_vm_jaccard_20']['mean'], summary['condC']['ta_bf_jaccard_20']['mean']]
    ov_D = [summary['condD']['ta_gm_jaccard_20']['mean'], summary['condD']['ta_sol_jaccard_20']['mean'],
            summary['condD']['ta_vm_jaccard_20']['mean'], summary['condD']['ta_bf_jaccard_20']['mean']]
    sem_ovC = [summary['condC']['ta_gm_jaccard_20']['sem'], summary['condC']['ta_sol_jaccard_20']['sem'],
               summary['condC']['ta_vm_jaccard_20']['sem'], summary['condC']['ta_bf_jaccard_20']['sem']]
    sem_ovD = [summary['condD']['ta_gm_jaccard_20']['sem'], summary['condD']['ta_sol_jaccard_20']['sem'],
               summary['condD']['ta_vm_jaccard_20']['sem'], summary['condD']['ta_bf_jaccard_20']['sem']]
               
    ax_4c.bar(x_idx - w/2.0, ov_C, width=w, yerr=sem_ovC, capsize=3, color='#4caf50', alpha=0.85, label='Cond C')
    ax_4c.bar(x_idx + w/2.0, ov_D, width=w, yerr=sem_ovD, capsize=3, color='#0288d1', alpha=0.85, label='Cond D')
    
    ax_4c.set_xticks(x_idx)
    ax_4c.set_xticklabels(pairs, fontsize=8.5, fontweight='bold')
    ax_4c.set_ylabel('Jaccard Overlap Index', fontsize=9.5, fontweight='bold')
    ax_4c.set_ylim(0, 1.0)
    ax_4c.grid(True, linestyle=':', alpha=0.5)
    ax_4c.legend(loc='upper right', fontsize=7.0, framealpha=0.9)
    
    # Panel 4D: Wave Kinematics & Spatial Progression Diagnostics
    ax_4d = fig.add_subplot(gs_row4[3])
    ax_4d.set_facecolor('#ffffff')
    ax_4d.set_title("D. Wave Progression Diagnostics\n(500 µm Bins; Lumbar Enlargement)", fontsize=10, fontweight='bold', pad=8)
    
    x_k = np.arange(4)
    k_labels = ['Caudal Delay\nFraction', 'Dwell\nFraction', 'Local Step\nFraction', 'Jump\nFraction']
    
    v_C = [summary['condC']['b500']['caudal_delay_frac']['mean'],
           summary['condC']['b500']['dwell_fraction']['mean'],
           summary['condC']['b500']['step_fraction']['mean'],
           summary['condC']['b500']['jump_fraction']['mean']]
    v_D = [summary['condD']['b500']['caudal_delay_frac']['mean'],
           summary['condD']['b500']['dwell_fraction']['mean'],
           summary['condD']['b500']['step_fraction']['mean'],
           summary['condD']['b500']['jump_fraction']['mean']]
           
    # Synthetic continuous wave control reference values
    v_synth = [json_data['synthetic_controls']['continuous']['b500']['caudal_delay_frac'],
               json_data['synthetic_controls']['continuous']['b500']['dwell_fraction'],
               json_data['synthetic_controls']['continuous']['b500']['step_fraction'],
               json_data['synthetic_controls']['continuous']['b500']['jump_fraction']]
               
    ax_4d.bar(x_k - w, v_C, width=w, color='#4caf50', alpha=0.85, label='Cond C')
    ax_4d.bar(x_k, v_D, width=w, color='#0288d1', alpha=0.85, label='Cond D')
    ax_4d.scatter(x_k + w/2.0, v_synth, color='#e91e63', marker='D', s=40, zorder=5, label='Smooth Wave Synth')
    
    ax_4d.set_xticks(x_k)
    ax_4d.set_xticklabels(k_labels, fontsize=8.0, fontweight='bold')
    ax_4d.set_ylabel('Fraction of Events / Transitions', fontsize=9.5, fontweight='bold')
    ax_4d.set_ylim(0, 1.05)
    ax_4d.grid(True, linestyle=':', alpha=0.5)
    ax_4d.legend(loc='upper right', fontsize=7.0, framealpha=0.9)
    
    # Save composite figure
    out_png = os.path.join(exp_dir, 'TA_Placement_Experiment.png')
    plt.savefig(out_png, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Generated experimental composite figure successfully: {out_png}")

if __name__ == '__main__':
    main()
