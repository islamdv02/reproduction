#!/usr/bin/env python3
"""
plot_ta_emg_comparison.py
Generates the synthetic EMG before/after comparison figure:
TA_EMG_Before_After.png

Shows before/after traces for TA, VM, BF, GM, and Soleus from Conditions C and D:
- Identical time windows (10.0 to 12.5 s, 2500 ms steady-state, 3 locomotor cycles)
- Identical muscle order (VM, BF, TA, GM, Soleus)
- Identical scales per muscle across conditions
- Matched EMG-generation randomness (identical random seeds for noise carrier)
- Clearly distinguishes synthetic EMG (raw interference + smoothed envelope) from raw pool firing rates R(t)
- Reports measured timing changes without normative value judgments
- Saved to komi_full_reproduction/experiments/ta_placement/TA_EMG_Before_After.png
"""

import os
import scipy.io as sio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    exp_dir = os.path.dirname(script_dir)
    data_dir = os.path.join(exp_dir, 'data')
    mat_path = os.path.join(data_dir, 'emg_export.mat')
    
    if not os.path.exists(mat_path):
        raise FileNotFoundError(f"EMG export file not found: {mat_path}")
        
    mat = sio.loadmat(mat_path)
    emg_data = mat['emg_data']
    
    t_rel = emg_data['t_rel_s'][0, 0].flatten() # 0 to 2.5 s
    t_ms = emg_data['time_ms'][0, 0].flatten()   # 10000 to 12500 ms
    
    # Muscle order: VM, BF, TA, GM, Sol
    muscle_keys = ['VM', 'BF', 'TA', 'GM', 'Sol']
    muscle_meta = {
        'VM':  {'name': 'Vastus Medialis',     'role': 'Knee Extensor',               'color': '#1565C0', 'n_mn': 55},
        'BF':  {'name': 'Biceps Femoris',      'role': 'Knee Flexor / Hip Extensor',  'color': '#E65100', 'n_mn': 43},
        'TA':  {'name': 'Tibialis Anterior',   'role': 'Ankle Dorsiflexor',           'color': '#00BCD4', 'n_mn': 36},
        'GM':  {'name': 'Gastrocnemius',       'role': 'Ankle Plantarflexor',         'color': '#AB47BC', 'n_mn': 34},
        'Sol': {'name': 'Soleus',              'role': 'Ankle Plantarflexor',         'color': '#2E7D32', 'n_mn': 67}
    }
    
    # Timing statistics from 5-realization analysis
    timing_stats = {
        'VM':  {'r_C': '+0.472', 'r_D': '-0.826', 'delta_r': '-1.298', 'note': 'Inverts to reciprocal timing'},
        'BF':  {'r_C': '-0.479', 'r_D': '+0.880', 'delta_r': '+1.359', 'note': 'Inverts to in-phase coupling'},
        'TA':  {'r_C': '— (ref)', 'r_D': '— (ref)', 'delta_r': '—',    'note': 'Locks in-phase with GM extensor'},
        'GM':  {'r_C': '+0.526', 'r_D': '+0.785', 'delta_r': '+0.259', 'note': 'Locks in-phase with GM'},
        'Sol': {'r_C': '-0.922', 'r_D': '+0.386', 'delta_r': '+1.308', 'note': 'Reciprocal antagonism collapses'}
    }
    
    # Cycle detection from reference Soleus signal (to shade locomotor cycles)
    sol_ref_C = emg_data['Sol'][0, 0]['rate_condC'][0, 0].flatten()
    # Simple threshold-based cycle phase detection for alternating background shading
    med_val = np.median(sol_ref_C)
    active_mask = (sol_ref_C > med_val)
    # Detect transitions
    diff_mask = np.diff(active_mask.astype(int))
    trans_idx = np.where(diff_mask != 0)[0]
    
    # Setup Figure (17 x 15 inches, 300 dpi)
    fig = plt.figure(figsize=(17, 15), dpi=300)
    fig.patch.set_facecolor('#ffffff')
    
    # Layout: Header Banner (row 0), 5 Muscle Rows (rows 1-5), Footer Card (row 6)
    gs = fig.add_gridspec(7, 2, height_ratios=[0.055, 0.175, 0.175, 0.175, 0.175, 0.175, 0.07],
                         hspace=0.28, wspace=0.18,
                         left=0.07, right=0.92, top=0.98, bottom=0.04)
    
    # -------------------------------------------------------------------------
    # HEADER BANNER
    # -------------------------------------------------------------------------
    ax_hdr = fig.add_subplot(gs[0, :])
    ax_hdr.axis('off')
    
    hdr_box = FancyBboxPatch((0.0, 0.05), 1.0, 0.90, transform=ax_hdr.transAxes,
                             facecolor='#b71c1c', edgecolor='#7f0000', linewidth=2.0,
                             boxstyle='round,pad=0.02', zorder=1)
    ax_hdr.add_patch(hdr_box)
    
    ax_hdr.text(0.5, 0.65, "NEW EXPERIMENT — NOT A REPRODUCED PUBLICATION FIGURE",
                transform=ax_hdr.transAxes, ha='center', va='center',
                fontsize=14.5, fontweight='bold', color='#ffffff', zorder=2)
    ax_hdr.text(0.5, 0.25,
                "Synthetic Electromyography (EMG) vs. Raw Pool Firing Rates: Before (Condition C) vs. After (Condition D) TA Relocation",
                transform=ax_hdr.transAxes, ha='center', va='center',
                fontsize=11.0, fontweight='bold', color='#ffcdd2', zorder=2)
    
    # Top Column Titles
    ax_col_C = fig.add_subplot(gs[0, 0])
    ax_col_C.axis('off')
    ax_col_D = fig.add_subplot(gs[0, 1])
    ax_col_D.axis('off')
    
    # -------------------------------------------------------------------------
    # 5 MUSCLE ROWS
    # -------------------------------------------------------------------------
    for m_idx, m_abbr in enumerate(muscle_keys):
        row_idx = m_idx + 1
        m_info = muscle_meta[m_abbr]
        t_info = timing_stats[m_abbr]
        m_struct = emg_data[m_abbr][0, 0]
        
        rate_C = m_struct['rate_condC'][0, 0].flatten()
        rate_D = m_struct['rate_condD'][0, 0].flatten()
        
        sig_C = m_struct['sig_condC'][0, 0].flatten()
        sig_D = m_struct['sig_condD'][0, 0].flatten()
        
        env_C = m_struct['env_condC'][0, 0].flatten()
        env_D = m_struct['env_condD'][0, 0].flatten()
        
        # Determine shared y-limits for synthetic EMG
        max_sig = max(np.max(np.abs(sig_C)), np.max(np.abs(sig_D)))
        max_env = max(np.max(env_C), np.max(env_D))
        emg_ylim = (-max_sig * 1.05, max_sig * 1.05)
        
        # Determine shared y-limits for firing rates
        max_rate = max(np.max(rate_C), np.max(rate_D))
        rate_ylim = (0.0, max(50.0, max_rate * 1.15))
        
        for cond_idx, (cond_name, cond_tag, sig_val, env_val, rate_val, is_reloc) in enumerate([
            ('Condition C', 'Baseline L2–L4 TA', sig_C, env_C, rate_C, False),
            ('Condition D', 'Relocated L4–L5 TA', sig_D, env_D, rate_D, True)
        ]):
            ax = fig.add_subplot(gs[row_idx, cond_idx])
            ax.set_facecolor('#fafafa')
            
            # Alternating cycle background shading
            for k in range(0, len(trans_idx) - 1, 2):
                t1 = t_rel[trans_idx[k]]
                t2 = t_rel[trans_idx[k+1]]
                ax.axvspan(t1, t2, facecolor='#f0f0f0', alpha=0.7, zorder=0)
            
            # 1. Plot Raw Synthetic EMG (bipolar interference pattern, grey semi-transparent)
            ax.plot(t_rel, sig_val, color='#757575', alpha=0.45, linewidth=0.55,
                    label='Synthetic Raw EMG', zorder=2)
            
            # 2. Plot Rectified & Smoothed Envelope (positive and inverted negative envelope, Fig 3E style)
            ax.plot(t_rel, env_val, color=m_info['color'], linewidth=2.0,
                    label='EMG Envelope', zorder=4)
            ax.plot(t_rel, -env_val, color=m_info['color'], linewidth=1.2,
                    linestyle='-', alpha=0.75, zorder=4)
            
            # 3. Plot Raw Motoneuron Pool Firing Rate R(t) on secondary twin axis
            ax_twin = ax.twinx()
            ax_twin.plot(t_rel, rate_val, color='#212121', linestyle='--', linewidth=1.5,
                         label='Raw Rate R(t)', zorder=5)
            ax_twin.set_ylim(rate_ylim)
            ax_twin.set_ylabel('Rate [Hz]' if cond_idx == 1 else '', fontsize=8.5,
                               fontweight='bold', color='#424242')
            ax_twin.tick_params(axis='y', labelsize=8.0, colors='#424242')
            
            # Axis styling
            ax.set_xlim(t_rel[0], t_rel[-1])
            ax.set_ylim(emg_ylim)
            ax.tick_params(axis='x', labelsize=8.5)
            ax.tick_params(axis='y', labelsize=8.0)
            
            if cond_idx == 0:
                ax.set_ylabel('EMG [a.u.]', fontsize=8.5, fontweight='bold', color='#424242')
            
            # Row title / Panel header on top row
            if row_idx == 1:
                title_text = f"{cond_name}: Same-Location Control\n({cond_tag})" if not is_reloc else f"{cond_name}: Relocated Experimental\n({cond_tag})"
                title_color = '#37474f' if not is_reloc else '#006064'
                ax.set_title(title_text, fontsize=11.5, fontweight='bold', color=title_color, pad=10)
            
            # Bottom row X labels
            if row_idx == 5:
                ax.set_xlabel('Time t [s]  (Simulation: 10.0 to 12.5 s)', fontsize=9.5, fontweight='bold')
            else:
                ax.set_xticklabels([])
                
            # Muscle badge on left panel (cond_idx == 0)
            if cond_idx == 0:
                is_ta_row = (m_abbr == 'TA')
                is_gm_row = (m_abbr == 'GM')
                badge_bg = '#e0f7fa' if is_ta_row else ('#f3e5f5' if is_gm_row else '#ffffff')
                badge_edge = '#00acc1' if is_ta_row else ('#ab47bc' if is_gm_row else '#b0bec5')
                ax.text(0.015, 0.94, f"{m_abbr} ({m_info['name']})\n{m_info['role']} (Left n={m_info['n_mn']})",
                        transform=ax.transAxes, fontsize=8.5, fontweight='bold',
                        color=m_info['color'], va='top', ha='left',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor=badge_bg, edgecolor=badge_edge, linewidth=1.2, alpha=0.92),
                        zorder=10)
            
            # Timing badge on right panel (cond_idx == 1)
            if cond_idx == 1:
                corr_val = t_info['r_D']
                delta_val = t_info['delta_r']
                t_badge_text = f"TA corr: {corr_val} (Δr = {delta_val})\n{t_info['note']}"
                if m_abbr == 'TA':
                    t_badge_text = f"Phase Shift: +100.0° (+207 ms)\n{t_info['note']}"
                ax.text(0.985, 0.94, t_badge_text,
                        transform=ax.transAxes, fontsize=8.0, fontweight='bold',
                        color='#006064' if is_reloc else '#37474f', va='top', ha='right',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='#e0f2f1', edgecolor='#80cbc4', linewidth=1.0, alpha=0.92),
                        zorder=10)
                
            for spine in ax.spines.values():
                spine.set_color('#b0bec5')
                spine.set_linewidth(1.0)
                
    # -------------------------------------------------------------------------
    # FOOTER SUMMARY CARD & LEGEND
    # -------------------------------------------------------------------------
    ax_ftr = fig.add_subplot(gs[6, :])
    ax_ftr.axis('off')
    
    # Legend elements box (left side of footer)
    leg_box = FancyBboxPatch((0.0, 0.05), 0.40, 0.90, transform=ax_ftr.transAxes,
                             facecolor='#f5f5f5', edgecolor='#b0bec5', linewidth=1.2,
                             boxstyle='round,pad=0.02', zorder=1)
    ax_ftr.add_patch(leg_box)
    
    ax_ftr.text(0.02, 0.78, "VISUAL SIGNAL DISTINCTIONS:", transform=ax_ftr.transAxes,
                fontsize=8.5, fontweight='bold', color='#212121')
    
    # Legend items
    ax_ftr.plot([0.02, 0.07], [0.55, 0.55], transform=ax_ftr.transAxes, color='#757575', linewidth=1.2)
    ax_ftr.text(0.08, 0.55, "Raw Synthetic EMG (Poisson carrier modulated by pool sum activation)",
                transform=ax_ftr.transAxes, fontsize=8.0, va='center', color='#424242')
    
    ax_ftr.plot([0.02, 0.07], [0.35, 0.35], transform=ax_ftr.transAxes, color='#00BCD4', linewidth=2.5)
    ax_ftr.text(0.08, 0.35, "Rectified & Smoothed Envelope (movmean 20 ms, matched random streams)",
                transform=ax_ftr.transAxes, fontsize=8.0, va='center', color='#424242')
    
    ax_ftr.plot([0.02, 0.07], [0.15, 0.15], transform=ax_ftr.transAxes, color='#212121', linestyle='--', linewidth=1.8)
    ax_ftr.text(0.08, 0.15, "Raw Motoneuron Mean Firing Rate R(t) [Hz] (smooth ODE firing rate)",
                transform=ax_ftr.transAxes, fontsize=8.0, va='center', color='#424242')
    
    # Quantitative Results Box (right side of footer)
    quant_box = FancyBboxPatch((0.42, 0.05), 0.58, 0.90, transform=ax_ftr.transAxes,
                              facecolor='#e8f5e9', edgecolor='#81c784', linewidth=1.5,
                              boxstyle='round,pad=0.02', zorder=1)
    ax_ftr.add_patch(quant_box)
    
    quant_text = (
        "MEASURED TIMING & COORDINATION OUTCOMES (Condition C vs Condition D, N=5 Paired Realizations):\n"
        "• TA Phase Shift: +100.0° ± 5.6° (+207.4 ± 11.6 ms advance) locking into phase with Gastrocnemius (GM r: +0.526 → +0.785).\n"
        "• Soleus Antagonism Collapses: Inverts from reciprocal antagonist (r = -0.922) to co-active (r = +0.386, Δr = +1.308 ± 0.055).\n"
        "• Thigh Muscle Coupling: TA–VM correlation inverts to negative (r = +0.472 → -0.826); TA–BF inverts to positive (r = -0.479 → +0.880).\n"
        "• Network Rhythm Invariance: Overall rhythm frequency (1.338 ± 0.029 Hz) and left-right alternation (163.0° ± 7.7°) remain invariant."
    )
    ax_ftr.text(0.44, 0.50, quant_text, transform=ax_ftr.transAxes,
                fontsize=8.0, color='#1b5e20', va='center', ha='left', zorder=2)
    
    # Caption Note
    caption_text = (
        "Figure Note: Synthetic EMG traces generated using the authors' exact algorithm (normcdf(zscore(prob)) carrier modulation, movmean 20 ms envelope). "
        "Condition C (Before) vs Condition D (After) computed with identical random carrier seeds (rng(1000 + m*37)) to isolate neural activation changes. "
        "Muscle order: VM, BF, TA, GM, Soleus. Shared y-scales per muscle. Alternating grey vertical shading denotes locomotor half-cycles."
    )
    fig.text(0.5, 0.010, caption_text, ha='center', va='bottom', fontsize=8.0, color='#455a64', style='italic', wrap=True)
    
    out_png = os.path.join(exp_dir, 'TA_EMG_Before_After.png')
    plt.savefig(out_png, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    
    print(f"Successfully generated: {out_png}")
    print(f"File size: {os.path.getsize(out_png):,} bytes")

if __name__ == '__main__':
    main()
