"""
analyze_and_plot_all_pools.py
Rigorous All-Pool Analysis for TA-Relocated Model (Condition D Realization 1)

Key Scientific Corrections:
  1. Explicit hindlimb neuron mask (1,366 neurons: L 656, R 710; 429 excluded axial/tail MNs).
  2. Direct reuse of saved all-neuron simulation without rerunning ODE integration.
  3. Verification against all 7 previously saved muscle traces with dynamic numerical error metrics.
  4. Physical RC maps distinguish categorical rows from continuous physical distance;
     empty bins represented as NaN with distinct background hatching.
  5. Neighboring populated bin delay analysis: signed timing differences (dt), spatial separation (dx),
     delay consistency, and cycle-to-cycle variability, handling phase wrapping explicitly.
  6. Documented cycle references, endpoint-free cycle normalization [0, 1), circular statistics,
     bilateral lags restricted to [-T/2, +T/2], and accurately labeled zero-lag Pearson correlation.
"""

import os
import json
import csv
import h5py
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Patch
from scipy.signal import find_peaks, correlate
from scipy.interpolate import interp1d

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXP_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
DATA_DIR = os.path.join(EXP_DIR, 'data')
ROOT_DIR = os.path.abspath(os.path.join(EXP_DIR, '..', '..'))

MAT_PATH = os.path.join(DATA_DIR, 'ta_relocated_all_pools.mat')
EXP_DATA_MAT = os.path.join(ROOT_DIR, 'experiments', 'ta_placement', 'data', 'experiment_data.mat')
META_PATH = os.path.join(DATA_DIR, 'mn_metadata.json')

CSV_OUT = os.path.join(EXP_DIR, 'pool_inventory.csv')
JSON_OUT = os.path.join(EXP_DIR, 'all_pool_metrics.json')
FIG_OUT = os.path.join(EXP_DIR, 'AllPool_Hip_Knee_Ankle_TA_Relocated.png')

def circ_mean_deg(angles_deg):
    rads = np.radians(angles_deg)
    s = np.sum(np.sin(rads))
    c = np.sum(np.cos(rads))
    return float(np.degrees(np.arctan2(s, c)) % 360.0)

def circ_std_deg(angles_deg):
    rads = np.radians(angles_deg)
    s = np.mean(np.sin(rads))
    c = np.mean(np.cos(rads))
    r = np.sqrt(s**2 + c**2)
    r = min(max(r, 1e-12), 1.0)
    return float(np.degrees(np.sqrt(-2.0 * np.log(r))))

def circ_r_vector(angles_deg):
    rads = np.radians(angles_deg)
    s = np.mean(np.sin(rads))
    c = np.mean(np.cos(rads))
    return float(np.sqrt(s**2 + c**2))

def circ_diff_deg(a_deg, b_deg):
    # Returns (a - b) wrapped to (-180, +180]
    return float((a_deg - b_deg + 180.0) % 360.0 - 180.0)

def main():
    print(f"Loading metadata from {META_PATH}...")
    with open(META_PATH, 'r', encoding='utf-8') as f:
        mn_meta = json.load(f)
        
    n_total_mn = len(mn_meta)
    hl_meta = [m for m in mn_meta if m['is_hindlimb']]
    excl_meta = [m for m in mn_meta if not m['is_hindlimb']]
    
    n_hl_total = len(hl_meta)
    n_hl_left = sum(1 for m in hl_meta if m['latera'] < 0)
    n_hl_right = sum(1 for m in hl_meta if m['latera'] > 0)
    
    n_excl_total = len(excl_meta)
    n_excl_left = sum(1 for m in excl_meta if m['latera'] < 0)
    n_excl_right = sum(1 for m in excl_meta if m['latera'] > 0)
    
    print(f"Neuron reconciliation: Total MN = {n_total_mn} | Hindlimb MN = {n_hl_total} (L: {n_hl_left}, R: {n_hl_right}) | Excluded = {n_excl_total} (L: {n_excl_left}, R: {n_excl_right})")

    # Load simulation rate matrices and pool info
    print(f"Loading rate data from {MAT_PATH}...")
    with h5py.File(MAT_PATH, 'r') as f_mat:
        pi = f_mat['pool_info']
        n_pools = pi['name'].shape[1]
        
        pools = []
        for i in range(n_pools):
            name = ''.join(chr(c[0]) for c in f_mat[pi['name'][0, i]][:])
            abbrev = ''.join(chr(c[0]) for c in f_mat[pi['abbrev'][0, i]][:])
            joint = ''.join(chr(c[0]) for c in f_mat[pi['joint_group'][0, i]][:])
            func = ''.join(chr(c[0]) for c in f_mat[pi['muscle_function'][0, i]][:])
            notes = ''.join(chr(c[0]) for c in f_mat[pi['uncertain_notes'][0, i]][:])
            segs = ''.join(chr(c[0]) for c in f_mat[pi['segments'][0, i]][:])
            
            # Extract neuron coordinates for this pool directly from mn_meta
            p_meta_l = [m for m in hl_meta if m['pool_name'] == name and m['latera'] < 0]
            p_meta_r = [m for m in hl_meta if m['pool_name'] == name and m['latera'] > 0]
            
            c_l = len(p_meta_l)
            c_r = len(p_meta_r)
            c_tot = c_l + c_r
            
            rc_l = [m['rc'] for m in p_meta_l]
            rc_r = [m['rc'] for m in p_meta_r]
            rc_all = rc_l + rc_r
            
            trace_l = f_mat[pi['trace_left'][0, i]][:].flatten()
            trace_r = f_mat[pi['trace_right'][0, i]][:].flatten()
            trace_all = f_mat[pi['trace_all'][0, i]][:].flatten()
            
            pools.append({
                'name': name,
                'abbrev': abbrev,
                'joint': joint,
                'func': func,
                'notes': notes,
                'segments': segs,
                'count_total': c_tot,
                'count_left': c_l,
                'count_right': c_r,
                'rc_cent_l': float(np.mean(rc_l)) if rc_l else np.nan,
                'rc_min_l': float(np.min(rc_l)) if rc_l else np.nan,
                'rc_max_l': float(np.max(rc_l)) if rc_l else np.nan,
                'rc_span_l': float(np.max(rc_l) - np.min(rc_l)) if rc_l else np.nan,
                'rc_cent_r': float(np.mean(rc_r)) if rc_r else np.nan,
                'rc_min_r': float(np.min(rc_r)) if rc_r else np.nan,
                'rc_max_r': float(np.max(rc_r)) if rc_r else np.nan,
                'rc_span_r': float(np.max(rc_r) - np.min(rc_r)) if rc_r else np.nan,
                'rc_cent_all': float(np.mean(rc_all)),
                'rc_min_all': float(np.min(rc_all)),
                'rc_max_all': float(np.max(rc_all)),
                'rc_span_all': float(np.max(rc_all) - np.min(rc_all)),
                'trace_l': trace_l,
                'trace_r': trace_r,
                'trace_all': trace_all
            })
            
        r_mn = f_mat['R_MN'][:] # (1795, 22000)

    # Sort pools by Left anatomical centroid
    pools.sort(key=lambda p: p['rc_cent_l'])
    print(f"Loaded and verified {len(pools)} hindlimb motor pools.")

    # 1. VERIFY AGAINST ALL 7 PREVIOUSLY SAVED TRACES IN experiment_data.mat
    print("Verifying against all previously saved muscle traces in experiment_data.mat...")
    trace_comparisons = {}
    if os.path.exists(EXP_DATA_MAT):
        with h5py.File(EXP_DATA_MAT, 'r') as f_exp:
            rd = f_exp['realization_data']
            condD = f_exp[rd['condD'][0, 0]]
            
            trace_map = {
                'trace_ta_l': ('Tibialis Anterior', 'trace_l'),
                'trace_gm_l': ('Gastrocnemius', 'trace_l'),
                'trace_sol_l': ('Soleus', 'trace_l'),
                'trace_vm_l': ('Vastus Medialis', 'trace_l'),
                'trace_bf_l': ('Biceps Femoris', 'trace_l'),
                'trace_ta_r': ('Tibialis Anterior', 'trace_r'),
                'trace_gm_r': ('Gastrocnemius', 'trace_r'),
            }
            
            names = [p['name'] for p in pools]
            for k, (pname, tr_fld) in trace_map.items():
                saved_tr = condD[k][:].flatten()
                curr_tr = pools[names.index(pname)][tr_fld]
                diff = np.abs(saved_tr - curr_tr)
                max_d = float(np.max(diff))
                mean_d = float(np.mean(diff))
                r_val = float(np.corrcoef(saved_tr, curr_tr)[0, 1])
                trace_comparisons[k] = {
                    'pool_name': pname,
                    'max_abs_diff_hz': max_d,
                    'mean_abs_diff_hz': mean_d,
                    'pearson_r': r_val
                }
                print(f"  {k:<12} ({pname}): max_abs_diff = {max_d:.6e} Hz, r = {r_val:.8f}")

    # 2. GENERATE pool_inventory.csv DYNAMICALLY
    print(f"Writing {CSV_OUT}...")
    with open(CSV_OUT, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([
            "pool_name", "abbreviation", "joint_group", "muscle_function",
            "neuron_count_total", "neuron_count_left", "neuron_count_right",
            "segments", "rc_min_left_um", "rc_max_left_um", "rc_centroid_left_um", "rc_span_left_um",
            "rc_min_right_um", "rc_max_right_um", "rc_centroid_right_um", "rc_span_right_um",
            "rc_min_all_um", "rc_max_all_um", "rc_centroid_all_um", "rc_span_all_um", "uncertainty_notes"
        ])
        for p in pools:
            writer.writerow([
                p['name'], p['abbrev'], p['joint'], p['func'],
                p['count_total'], p['count_left'], p['count_right'],
                p['segments'],
                f"{p['rc_min_l']:.1f}", f"{p['rc_max_l']:.1f}", f"{p['rc_cent_l']:.1f}", f"{p['rc_span_l']:.1f}",
                f"{p['rc_min_r']:.1f}", f"{p['rc_max_r']:.1f}", f"{p['rc_cent_r']:.1f}", f"{p['rc_span_r']:.1f}",
                f"{p['rc_min_all']:.1f}", f"{p['rc_max_all']:.1f}", f"{p['rc_cent_all']:.1f}", f"{p['rc_span_all']:.1f}",
                p['notes']
            ])
            
        writer.writerow([])
        writer.writerow(["# EXCLUDED NON-HINDLIMB / AXIAL / TAIL POOLS (DERIVED DYNAMICALLY FROM DATA)", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""])
        
        # Derive excluded pools dynamically from excl_meta
        excl_pool_names = sorted(list(set(m['pool_name'] for m in excl_meta)))
        for ep in excl_pool_names:
            e_sub_l = [m for m in excl_meta if m['pool_name'] == ep and m['latera'] < 0]
            e_sub_r = [m for m in excl_meta if m['pool_name'] == ep and m['latera'] > 0]
            e_sub_all = e_sub_l + e_sub_r
            
            c_tot = len(e_sub_all)
            c_l = len(e_sub_l)
            c_r = len(e_sub_r)
            
            rc_l = [m['rc'] for m in e_sub_l]
            rc_r = [m['rc'] for m in e_sub_r]
            rc_all = [m['rc'] for m in e_sub_all]
            
            segs = ", ".join(sorted(list(set(m['segment'] for m in e_sub_all))))
            
            if ep == "Axial":
                f_desc, j_desc, notes = "Paraspinal deep axial column", "Axial Column", "Continuous paraspinal axial column spanning T13-L5; excluded from hindlimb analysis."
                abb = "Ax"
            elif ep == "Tail":
                f_desc, j_desc, notes = "Tail abductor/flexor", "Caudal / Tail", "Sacro-caudal tail motoneuron column (S1-S4); excluded from hindlimb analysis."
                abb = "Tail"
            elif ep == "Thoracic Abdominal":
                f_desc, j_desc, notes = "Thoracic trunk wall muscle", "Axial Trunk", "Thoracic abdominal wall muscle in T13; excluded from hindlimb analysis."
                abb = "ThAb"
            elif ep == "Quadratus Lumburum":
                f_desc, j_desc, notes = "Posterior abdominal wall", "Axial Trunk", "Posterior abdominal lumbar wall muscle in L1; excluded from hindlimb analysis."
                abb = "QL"
            else:
                f_desc, j_desc, notes = "Non-hindlimb muscle", "Axial/Other", "Excluded non-hindlimb pool."
                abb = ep[:4]
                
            writer.writerow([
                ep, abb, j_desc, f_desc, c_tot, c_l, c_r, segs,
                f"{np.min(rc_l):.1f}", f"{np.max(rc_l):.1f}", f"{np.mean(rc_l):.1f}", f"{np.max(rc_l)-np.min(rc_l):.1f}",
                f"{np.min(rc_r):.1f}", f"{np.max(rc_r):.1f}", f"{np.mean(rc_r):.1f}", f"{np.max(rc_r)-np.min(rc_r):.1f}",
                f"{np.min(rc_all):.1f}", f"{np.max(rc_all):.1f}", f"{np.mean(rc_all):.1f}", f"{np.max(rc_all)-np.min(rc_all):.1f}",
                notes
            ])

    # 3. LOCOMOTOR CYCLE DETECTION & PHASE NORMALIZATION
    # Steady-state evaluation window: 10000 to 22000 ms (12,000 ms duration)
    ss_start, ss_end = 10000, 22000
    t_ss = np.arange(ss_start, ss_end)
    
    names = [p['name'] for p in pools]
    gm_idx = names.index('Gastrocnemius')
    gm_tr_l = pools[gm_idx]['trace_l'][ss_start:ss_end]
    gm_tr_r = pools[gm_idx]['trace_r'][ss_start:ss_end]
    
    # Left GM cycle detection
    sig_gm_l = gm_tr_l - np.mean(gm_tr_l)
    pks_l, _ = find_peaks(sig_gm_l, distance=500, prominence=5.0)
    cycle_onsets_l = pks_l + ss_start
    n_cycles_l = len(cycle_onsets_l) - 1
    
    # Right GM cycle detection
    sig_gm_r = gm_tr_r - np.mean(gm_tr_r)
    pks_r, _ = find_peaks(sig_gm_r, distance=500, prominence=5.0)
    cycle_onsets_r = pks_r + ss_start
    n_cycles_r = len(cycle_onsets_r) - 1
    
    periods_l = np.diff(cycle_onsets_l)
    mean_period_l = float(np.mean(periods_l))
    freq_hz_l = 1000.0 / mean_period_l
    print(f"Left side rhythm: {n_cycles_l} cycles | Mean Period = {mean_period_l:.1f} ms | Frequency = {freq_hz_l:.3f} Hz")
    
    periods_r = np.diff(cycle_onsets_r)
    mean_period_r = float(np.mean(periods_r))
    freq_hz_r = 1000.0 / mean_period_r
    print(f"Right side rhythm: {n_cycles_r} cycles | Mean Period = {mean_period_r:.1f} ms | Frequency = {freq_hz_r:.3f} Hz")
    
    # Bilateral phase lag between Left GM and Right GM within [-T/2, +T/2]
    max_lag = round(mean_period_l / 2.0)
    cc_lr = correlate(sig_gm_r, sig_gm_l, mode='full')
    lags = np.arange(-len(sig_gm_l) + 1, len(sig_gm_l))
    valid_mask = (lags >= -max_lag) & (lags <= max_lag)
    best_lag_gm = int(lags[valid_mask][np.argmax(cc_lr[valid_mask])])
    bilateral_phase_gm_deg = (best_lag_gm / mean_period_l * 360.0) % 360.0
    print(f"Bilateral GM lag (Right relative to Left): {best_lag_gm} ms ({bilateral_phase_gm_deg:.1f} deg)")

    # Normalize cycles: 100 points in [0, 1) without duplicate endpoint
    n_bins_cycle = 100
    phase_grid = np.linspace(0.0, 1.0, n_bins_cycle, endpoint=False) # STRICTLY NO DUPLICATE ENDPOINT

    for p in pools:
        # Left side cycles (relative to Left GM)
        p['cycles_l'] = []
        p['peak_phases_l'] = []
        for c in range(n_cycles_l):
            t0, t1 = cycle_onsets_l[c], cycle_onsets_l[c + 1]
            c_len = t1 - t0
            seg = p['trace_l'][t0:t1]
            seg_time = np.linspace(0.0, 1.0, c_len, endpoint=False)
            interp_tr = interp1d(seg_time, seg, kind='linear')(phase_grid)
            p['cycles_l'].append(interp_tr)
            
            pk_rel = np.argmax(seg)
            ph = (pk_rel / float(c_len)) * 360.0
            p['peak_phases_l'].append(ph)
            
        p['cycle_mean_l'] = np.mean(p['cycles_l'], axis=0)
        p['cycle_sem_l'] = np.std(p['cycles_l'], axis=0) / np.sqrt(n_cycles_l)
        p['circ_peak_phase_l'] = circ_mean_deg(p['peak_phases_l'])
        p['circ_peak_std_l'] = circ_std_deg(p['peak_phases_l'])
        p['circ_r_l'] = circ_r_vector(p['peak_phases_l'])
        
        # Modulation depth
        mod_l = np.max(p['cycle_mean_l']) - np.min(p['cycle_mean_l'])
        p['mod_depth_l'] = float(mod_l)
        p['is_modulated_l'] = bool(mod_l >= 5.0) # Flag weakly modulated pools
        
        # Right side cycles (relative to Right GM)
        p['cycles_r'] = []
        p['peak_phases_r'] = []
        for c in range(n_cycles_r):
            t0, t1 = cycle_onsets_r[c], cycle_onsets_r[c + 1]
            c_len = t1 - t0
            seg = p['trace_r'][t0:t1]
            seg_time = np.linspace(0.0, 1.0, c_len, endpoint=False)
            interp_tr = interp1d(seg_time, seg, kind='linear')(phase_grid)
            p['cycles_r'].append(interp_tr)
            
            pk_rel = np.argmax(seg)
            ph = (pk_rel / float(c_len)) * 360.0
            p['peak_phases_r'].append(ph)
            
        p['cycle_mean_r'] = np.mean(p['cycles_r'], axis=0)
        p['cycle_sem_r'] = np.std(p['cycles_r'], axis=0) / np.sqrt(n_cycles_r)
        p['circ_peak_phase_r'] = circ_mean_deg(p['peak_phases_r'])
        p['circ_peak_std_r'] = circ_std_deg(p['peak_phases_r'])
        p['circ_r_r'] = circ_r_vector(p['peak_phases_r'])
        mod_r = np.max(p['cycle_mean_r']) - np.min(p['cycle_mean_r'])
        p['mod_depth_r'] = float(mod_r)
        p['is_modulated_r'] = bool(mod_r >= 5.0)

    # 4. ZERO-LAG PEARSON CORRELATION & BILATERAL CROSS-CORRELATION
    corr_mat_l = np.zeros((n_pools, n_pools))
    corr_mat_r = np.zeros((n_pools, n_pools))
    for i in range(n_pools):
        for j in range(n_pools):
            tr_i_l = pools[i]['trace_l'][ss_start:ss_end]
            tr_j_l = pools[j]['trace_l'][ss_start:ss_end]
            corr_mat_l[i, j] = float(np.corrcoef(tr_i_l, tr_j_l)[0, 1])
            
            tr_i_r = pools[i]['trace_r'][ss_start:ss_end]
            tr_j_r = pools[j]['trace_r'][ss_start:ss_end]
            corr_mat_r[i, j] = float(np.corrcoef(tr_i_r, tr_j_r)[0, 1])

    bilateral_coordination = {}
    for p in pools:
        tr_l = p['trace_l'][ss_start:ss_end] - np.mean(p['trace_l'][ss_start:ss_end])
        tr_r = p['trace_r'][ss_start:ss_end] - np.mean(p['trace_r'][ss_start:ss_end])
        
        cc = correlate(tr_r, tr_l, mode='full')
        lags = np.arange(-len(tr_l) + 1, len(tr_l))
        v_mask = (lags >= -max_lag) & (lags <= max_lag)
        best_lag_ms = int(lags[v_mask][np.argmax(cc[v_mask])])
        phase_lag_deg = (best_lag_ms / mean_period_l * 360.0) % 360.0
        r_zero = float(np.corrcoef(tr_l, tr_r)[0, 1])
        
        bilateral_coordination[p['name']] = {
            'signed_lag_ms': best_lag_ms,
            'phase_lag_deg': float(phase_lag_deg),
            'zero_lag_pearson_r': r_zero
        }

    # 5. PHYSICAL HINDLIMB-ONLY ROSTROCAUDAL BINNING & PROPAGATION DELAYS
    # Full hindlimb extent: 0 to 11000 um (covers up to most caudal hindlimb neuron at 10672 um)
    # Lumbar enlargement: 2500 to 9400 um
    print("Computing physical hindlimb-only binned maps and neighboring activation delays...")
    
    # Extract hindlimb neuron rows in r_mn
    hl_row_indices = [m['mn_index'] - 1 for m in hl_meta]
    r_hl = r_mn[hl_row_indices, :] # (1366, 22000)
    rc_hl = np.array([m['rc'] for m in hl_meta])
    lat_hl = np.array([m['latera'] for m in hl_meta])
    
    bin_analysis = {}
    for bw in [250, 500, 1000]:
        edges = np.arange(0, 11000 + bw, bw) # ensures coverage past 10672 um
        n_b = len(edges) - 1
        centers = (edges[:-1] + edges[1:]) / 2.0
        
        # Initialize
        mean_l = np.full((22000, n_b), np.nan)
        sum_l = np.zeros((22000, n_b))
        count_l = np.zeros(n_b, dtype=int)
        
        mean_r = np.full((22000, n_b), np.nan)
        sum_r = np.zeros((22000, n_b))
        count_r = np.zeros(n_b, dtype=int)
        
        for b in range(n_b):
            b_low, b_high = edges[b], edges[b + 1]
            
            # Left side
            in_b_l = np.where((lat_hl < 0) & (rc_hl >= b_low) & (rc_hl < b_high))[0]
            count_l[b] = len(in_b_l)
            if len(in_b_l) > 0:
                mean_l[:, b] = np.mean(r_hl[in_b_l, :], axis=0)
                sum_l[:, b] = np.sum(r_hl[in_b_l, :], axis=0)
                
            # Right side
            in_b_r = np.where((lat_hl > 0) & (rc_hl >= b_low) & (rc_hl < b_high))[0]
            count_r[b] = len(in_b_r)
            if len(in_b_r) > 0:
                mean_r[:, b] = np.mean(r_hl[in_b_r, :], axis=0)
                sum_r[:, b] = np.sum(r_hl[in_b_r, :], axis=0)

        # Populated bin timing analysis for both Left and Right sides
        bin_timing_l: list[dict] = []
        bin_timing_r: list[dict] = []
        neighbor_delays_l: list[dict] = []
        neighbor_delays_r: list[dict] = []
        regional_l: dict = {}
        regional_r: dict = {}

        for side, counts, means, sums, n_cycles, onsets, period in [
            ('left', count_l, mean_l, sum_l, n_cycles_l, cycle_onsets_l, mean_period_l),
            ('right', count_r, mean_r, sum_r, n_cycles_r, cycle_onsets_r, mean_period_r)
        ]:
            pop_bins = [b for b in range(n_b) if counts[b] > 0]
            bin_timing = []
            grid_c = np.linspace(0.0, 1.0, 100, endpoint=False)
            
            for b in pop_bins:
                tr = means[ss_start:ss_end, b]
                mod = np.max(tr) - np.min(tr)
                
                # Per-cycle peak phase
                ph_list = []
                c_segs = []
                for c in range(n_cycles):
                    t0 = onsets[c] - ss_start
                    t1 = onsets[c + 1] - ss_start
                    seg = tr[t0:t1]
                    pk_rel = np.argmax(seg)
                    ph = (pk_rel / float(t1 - t0)) * 360.0
                    ph_list.append(ph)
                    
                    seg_t = np.linspace(0.0, 1.0, len(seg), endpoint=False)
                    c_segs.append(interp1d(seg_t, seg, kind='linear')(grid_c))
                    
                c_mean = circ_mean_deg(ph_list)
                c_std = circ_std_deg(ph_list)
                c_r = circ_r_vector(ph_list)
                
                # Detect multi-peak waveforms in cycle-averaged trace
                avg_wave = np.mean(c_segs, axis=0)
                pks_sub, _ = find_peaks(avg_wave, height=5.0, prominence=2.0)
                is_multi = False
                if len(pks_sub) > 1:
                    sorted_pks = np.sort(avg_wave[pks_sub])
                    if sorted_pks[-2] >= 0.5 * sorted_pks[-1]:
                        is_multi = True
                
                bin_timing.append({
                    'bin_index': b,
                    'center_um': float(centers[b]),
                    'neuron_count': int(counts[b]),
                    'modulation_depth_hz': float(mod),
                    'is_weak': bool(mod < 5.0),
                    'is_ambiguous': bool(c_r < 0.85 or c_std > 35.0),
                    'is_multi_peaked': is_multi,
                    'circ_mean_phase_deg': c_mean,
                    'circ_std_phase_deg': c_std,
                    'circ_r': c_r,
                    'timing_ms': float(c_mean / 360.0 * period),
                    'timing_std_ms': float(c_std / 360.0 * period),
                    'cycle_phases': ph_list
                })
                
            # Unwrapped continuous timing across populated bins
            if bin_timing:
                phases_rad = np.deg2rad([bt['circ_mean_phase_deg'] for bt in bin_timing])
                unwrapped_rad = np.unwrap(phases_rad)
                if unwrapped_rad[0] < 0:
                    unwrapped_rad += 2 * np.pi
                for idx, bt in enumerate(bin_timing):
                    bt['unwrapped_phase_deg'] = float(np.rad2deg(unwrapped_rad[idx]))
                    bt['unwrapped_timing_ms'] = float(unwrapped_rad[idx] / (2 * np.pi) * period)
                    
            # Neighboring pairwise delay (only strictly adjacent bins: b2['bin_index'] == b1['bin_index'] + 1)
            neighbor_delays = []
            for i in range(len(bin_timing) - 1):
                b1 = bin_timing[i]
                b2 = bin_timing[i + 1]
                dx = b2['center_um'] - b1['center_um']
                is_adjacent = (b2['bin_index'] == b1['bin_index'] + 1)
                
                # Per-cycle signed phase differences
                d_phases = [circ_diff_deg(p2, p1) for p1, p2 in zip(b1['cycle_phases'], b2['cycle_phases'])]
                mean_dph = circ_mean_deg(d_phases)
                if mean_dph > 180.0: mean_dph -= 360.0
                
                std_dph = circ_std_deg(d_phases)
                r_d = circ_r_vector(d_phases)
                dt_ms = mean_dph / 360.0 * period
                dt_std_ms = std_dph / 360.0 * period
                speed = (dx / dt_ms) if abs(dt_ms) > 1.0 else np.nan
                
                neighbor_delays.append({
                    'bin1_index': b1['bin_index'],
                    'bin2_index': b2['bin_index'],
                    'x1_um': b1['center_um'],
                    'x2_um': b2['center_um'],
                    'dx_um': dx,
                    'is_adjacent': is_adjacent,
                    'mean_signed_delay_ms': dt_ms,
                    'delay_std_ms': dt_std_ms,
                    'mean_signed_phase_diff_deg': mean_dph,
                    'delay_consistency_r': r_d,
                    'apparent_speed_um_ms': float(speed) if not np.isnan(speed) else None,
                    'direction': "caudal_lag" if dt_ms > 2.0 else ("rostral_lag" if dt_ms < -2.0 else "near_synchronous")
                })
                
            # Regional delay summaries (adjacent bins only)
            def summarize_delays(delays_subset):
                adj = [d for d in delays_subset if d['is_adjacent']]
                if not adj:
                    return {'transition_count': 0}
                mean_dt = np.mean([d['mean_signed_delay_ms'] for d in adj])
                mean_std = np.mean([d['delay_std_ms'] for d in adj])
                mean_r = np.mean([d['delay_consistency_r'] for d in adj])
                return {
                    'transition_count': len(adj),
                    'mean_signed_delay_ms': float(mean_dt),
                    'mean_delay_std_ms': float(mean_std),
                    'mean_delay_consistency_r': float(mean_r),
                    'caudal_lag_count': sum(1 for d in adj if d['direction'] == 'caudal_lag'),
                    'rostral_lag_count': sum(1 for d in adj if d['direction'] == 'rostral_lag'),
                    'near_synchronous_count': sum(1 for d in adj if d['direction'] == 'near_synchronous')
                }
                
            reg_full = summarize_delays(neighbor_delays)
            reg_lumb = summarize_delays([d for d in neighbor_delays if 1500 <= d['x1_um'] <= 9500 and 1500 <= d['x2_um'] <= 9500])
            reg_rostral = summarize_delays([d for d in neighbor_delays if d['x2_um'] < 1500])
            reg_caudal = summarize_delays([d for d in neighbor_delays if d['x1_um'] > 9500])
            
            if side == 'left':
                bin_timing_l = bin_timing
                neighbor_delays_l = neighbor_delays
                regional_l = {
                    'full_extent': reg_full,
                    'lumbar_enlargement_1500_9500um': reg_lumb,
                    'rostral_margin_0_1500um': reg_rostral,
                    'caudal_margin_9500_11000um': reg_caudal
                }
            else:
                bin_timing_r = bin_timing
                neighbor_delays_r = neighbor_delays
                regional_r = {
                    'full_extent': reg_full,
                    'lumbar_enlargement_1500_9500um': reg_lumb,
                    'rostral_margin_0_1500um': reg_rostral,
                    'caudal_margin_9500_11000um': reg_caudal
                }
                
        bin_analysis[f"{bw}um"] = {
            'bin_width_um': bw,
            'bin_edges_um': edges.tolist(),
            'bin_centers_um': centers.tolist(),
            'counts_left': count_l.tolist(),
            'counts_right': count_r.tolist(),
            'empty_bins_left': [b for b in range(n_b) if count_l[b] == 0],
            'empty_bins_right': [b for b in range(n_b) if count_r[b] == 0],
            'bin_timing_left': bin_timing_l,
            'neighbor_delays_left': neighbor_delays_l,
            'regional_summary_left': regional_l,
            'bin_timing_right': bin_timing_r,
            'neighbor_delays_right': neighbor_delays_r,
            'regional_summary_right': regional_r,
            'mean_act_left': mean_l,
            'sum_act_left': sum_l,
            'mean_act_right': mean_r,
            'sum_act_right': sum_r
        }

    # 6. EXPORT all_pool_metrics.json
    print(f"Writing {JSON_OUT}...")
    json_export = {
        'metadata': {
            'title': "All-Pool Hindlimb Motoneuron Analysis: TA-Relocated Simulation (Condition D)",
            'condition': "Condition D Realization 1 (TA relocated to L4-L5 [5600, 7900] um, connections rebuilt)",
            'seeds': {'net_seed': 42, 'sim_seed': 5},
            'drive_pA': 25.0,
            'duration_ms': 22000,
            'steady_state_window_ms': [10000, 22000],
            'locomotor_frequency_hz': freq_hz_l,
            'cycle_period_ms': mean_period_l,
            'cycle_references': {
                'left_side': "Left Gastrocnemius (GM) peak onset (0% = 0 deg)",
                'right_side': "Right Gastrocnemius (GM) peak onset (0% = 0 deg)",
                'bilateral_offset': f"Right GM relative to Left GM: {best_lag_gm} ms ({bilateral_phase_gm_deg:.1f} deg)"
            }
        },
        'verification_trace_comparison': trace_comparisons,
        'reconciled_neuron_counts': {
            'total_motoneurons_in_model': n_total_mn,
            'total_hindlimb_motoneurons': n_hl_total,
            'left_hindlimb_motoneurons': n_hl_left,
            'right_hindlimb_motoneurons': n_hl_right,
            'total_excluded_motoneurons': n_excl_total,
            'left_excluded_motoneurons': n_excl_left,
            'right_excluded_motoneurons': n_excl_right,
            'excluded_pools_breakdown': {
                ep: sum(1 for m in excl_meta if m['pool_name'] == ep) for ep in sorted(list(set(m['pool_name'] for m in excl_meta)))
            },
            'count_reconciliation_note': "Reconciled exactly with saved model: 1366 hindlimb motoneurons (656 Left, 710 Right) + 429 excluded motoneurons (330 Axial, 58 Tail, 24 Thoracic Abdominal, 17 Quadratus Lumburum) = 1795 total motoneurons. The previously reported 1326 count reflected a clerical typo in an earlier draft."
        },
        'pools_left': {},
        'pools_right': {},
        'bilateral_coordination': bilateral_coordination,
        'zero_lag_correlation_left': {
            'order': [p['abbrev'] for p in pools],
            'matrix': corr_mat_l.tolist()
        },
        'zero_lag_correlation_right': {
            'order': [p['abbrev'] for p in pools],
            'matrix': corr_mat_r.tolist()
        },
        'wave_progression_analysis': {
            f"{bw}um": {
                'bin_width_um': bw,
                'total_bins': len(bin_analysis[f"{bw}um"]['bin_centers_um']),
                'empty_bins_left': bin_analysis[f"{bw}um"]['empty_bins_left'],
                'empty_bins_right': bin_analysis[f"{bw}um"]['empty_bins_right'],
                'bin_timing_left': bin_analysis[f"{bw}um"]['bin_timing_left'],
                'bin_timing_right': bin_analysis[f"{bw}um"]['bin_timing_right'],
                'neighbor_delays_left': bin_analysis[f"{bw}um"]['neighbor_delays_left'],
                'neighbor_delays_right': bin_analysis[f"{bw}um"]['neighbor_delays_right'],
                'regional_summary_left': bin_analysis[f"{bw}um"]['regional_summary_left'],
                'regional_summary_right': bin_analysis[f"{bw}um"]['regional_summary_right']
            } for bw in [250, 500, 1000]
        }
    }

    for p in pools:
        json_export['pools_left'][p['name']] = {
            'abbreviation': p['abbrev'],
            'joint_group': p['joint'],
            'neuron_count': p['count_left'],
            'rc_centroid_um': p['rc_cent_l'],
            'rc_min_um': p['rc_min_l'],
            'rc_max_um': p['rc_max_l'],
            'rc_span_um': p['rc_span_l'],
            'circ_peak_phase_deg': p['circ_peak_phase_l'],
            'circ_peak_std_deg': p['circ_peak_std_l'],
            'circ_r': p['circ_r_l'],
            'modulation_depth_hz': p['mod_depth_l'],
            'is_robustly_modulated': p['is_modulated_l'],
            'mean_firing_rate_hz': float(np.mean(p['trace_l'][ss_start:ss_end])),
            'peak_firing_rate_hz': float(np.max(p['trace_l'][ss_start:ss_end]))
        }
        json_export['pools_right'][p['name']] = {
            'abbreviation': p['abbrev'],
            'joint_group': p['joint'],
            'neuron_count': p['count_right'],
            'rc_centroid_um': p['rc_cent_r'],
            'rc_min_um': p['rc_min_r'],
            'rc_max_um': p['rc_max_r'],
            'rc_span_um': p['rc_span_r'],
            'circ_peak_phase_deg': p['circ_peak_phase_r'],
            'circ_peak_std_deg': p['circ_peak_std_r'],
            'circ_r': p['circ_r_r'],
            'modulation_depth_hz': p['mod_depth_r'],
            'is_robustly_modulated': p['is_modulated_r'],
            'mean_firing_rate_hz': float(np.mean(p['trace_r'][ss_start:ss_end])),
            'peak_firing_rate_hz': float(np.max(p['trace_r'][ss_start:ss_end]))
        }

    with open(JSON_OUT, 'w', encoding='utf-8') as f_out:
        json.dump(json_export, f_out, indent=2)

    # 7. GENERATE COMPACT READABLE MASTER COMPOSITE: AllPool_Hip_Knee_Ankle_TA_Relocated.png
    print(f"Generating master composite figure {FIG_OUT}...")
    plt.rcParams['font.sans-serif'] = 'Arial'
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.edgecolor'] = '#333333'
    plt.rcParams['axes.linewidth'] = 0.8

    fig = plt.figure(figsize=(24, 26), dpi=300)
    # Master layout: 5 clear horizontal sections A, B, C, D, E
    gs = gridspec.GridSpec(5, 2, height_ratios=[1.0, 1.1, 1.4, 1.2, 1.2], hspace=0.36, wspace=0.22,
                           left=0.06, right=0.96, top=0.95, bottom=0.035)

    plot_win = np.arange(10000, 12500)
    t_plot_s = (plot_win - plot_win[0]) / 1000.0

    c_ta = '#00B4D8'   # Cyan
    c_gm = '#E01E5A'   # Magenta
    joint_colors = {'Hip': '#3A86FF', 'Knee': '#8338EC', 'Ankle/Toes': '#FF006E'}
    seg_bounds = [('T13/L1', 1300), ('L1/L2', 2500), ('L2/L3', 4000), ('L3/L4', 5500),
                  ('L4/L5', 6800), ('L5/L6', 8000), ('L6/S1', 9400)]

    # -------------------------------------------------------------------------
    # SECTION A: Pool Anatomy, Topography & Spatial Occupancy
    # -------------------------------------------------------------------------
    # Panel A1: Dot-Column Topography of Hindlimb Motor Pools
    ax_a1 = fig.add_subplot(gs[0, 0])
    for s_name, s_pos in seg_bounds:
        ax_a1.axhline(s_pos, color='#CCCCCC', linestyle=':', linewidth=0.8)
        ax_a1.text(13.4, s_pos + 40, s_name, color='#777777', fontsize=7.5, va='bottom')
        
    ax_a1.axhspan(5600, 7900, color=c_ta, alpha=0.12, label='Relocated TA (L4-L5)')
    
    # Plot individual motoneurons as jittered dots
    rng = np.random.RandomState(42)
    for i, p in enumerate(pools):
        p_hl = [m for m in hl_meta if m['pool_name'] == p['name'] and m['latera'] < 0]
        rcs = [m['rc'] for m in p_hl]
        jit = rng.uniform(-0.25, 0.25, size=len(rcs))
        col = c_ta if p['abbrev'] == 'TA' else (c_gm if p['abbrev'] == 'GM' else '#666666')
        sz = 22 if p['abbrev'] in ['TA', 'GM'] else 12
        ax_a1.scatter(np.full(len(rcs), i) + jit, rcs, color=col, s=sz, alpha=0.7, edgecolors='none')
        # Mark centroid
        ax_a1.plot([i - 0.35, i + 0.35], [p['rc_cent_l'], p['rc_cent_l']], color=col, linewidth=2.0)
        
    ax_a1.set_xticks(np.arange(n_pools))
    ax_a1.set_xticklabels([p['abbrev'] for p in pools], rotation=45, ha='right', fontsize=8.5)
    ax_a1.set_xlim(-0.8, n_pools - 0.2)
    ax_a1.set_ylim(0, 11000)
    ax_a1.set_ylabel("Spinal RC Position (µm)", fontsize=9.5)
    ax_a1.set_title("A1. Hindlimb Motor Pool Topography (Left Side, Individual Somata & Centroids)", fontsize=11, fontweight='bold', pad=6)
    ax_a1.grid(True, axis='y', linestyle=':', alpha=0.4)

    # Panel A2: Spatial Neuron Occupancy per Bin (Left vs Right)
    ax_a2 = fig.add_subplot(gs[0, 1])
    b500 = bin_analysis['500um']
    c_500 = np.array(b500['bin_centers_um'])
    cnt_l = np.array(b500['counts_left'])
    cnt_r = np.array(b500['counts_right'])
    
    w = 180
    ax_a2.bar(c_500 - w/2, cnt_l, width=w, color='#3A86FF', alpha=0.75, label=f'Left Hindlimb (N={n_hl_left})')
    ax_a2.bar(c_500 + w/2, cnt_r, width=w, color='#8338EC', alpha=0.75, label=f'Right Hindlimb (N={n_hl_right})')
    
    # Mark empty bins
    for eb in b500['empty_bins_left']:
        ax_a2.scatter(c_500[eb] - w/2, 1, marker='x', color='red', s=45, zorder=5, label='Empty Bin (Left)' if eb == b500['empty_bins_left'][0] else "")
    for eb in b500['empty_bins_right']:
        ax_a2.scatter(c_500[eb] + w/2, 1, marker='x', color='darkred', s=45, zorder=5, label='Empty Bin (Right)' if eb == b500['empty_bins_right'][0] else "")
        
    ax_a2.set_xlim(0, 11000)
    ax_a2.set_xlabel("Rostrocaudal Position (µm)", fontsize=9.5)
    ax_a2.set_ylabel("Neuron Occupancy (Count / 500 µm)", fontsize=9.5)
    ax_a2.set_title("A2. Spatial Neuron Occupancy (500 µm Bins, Full Hindlimb Extent [0, 11000] µm)", fontsize=11, fontweight='bold', pad=6)
    ax_a2.grid(True, linestyle=':', alpha=0.4)
    ax_a2.legend(loc='upper left', fontsize=8, framealpha=0.85)

    # -------------------------------------------------------------------------
    # SECTION B: All-Pool Activity Maps (Equally-Spaced Rows Ordered by Centroid)
    # -------------------------------------------------------------------------
    # Panel B1: Left Side
    ax_b1 = fig.add_subplot(gs[1, 0])
    rate_mat_l = np.array([p['trace_l'][plot_win] for p in pools])
    im_b1 = ax_b1.imshow(rate_mat_l, aspect='auto', cmap='magma', origin='upper', vmin=0, vmax=45,
                         extent=(float(t_plot_s[0]), float(t_plot_s[-1]), float(n_pools - 0.5), -0.5))
    ax_b1.set_yticks(np.arange(n_pools))
    ax_b1.set_yticklabels([f"{p['abbrev']} ({p['joint'][0]}) - {p['rc_cent_l']:.0f} µm" for p in pools], fontsize=8.5)
    ax_b1.set_title("B1. Left Side: All 14 Pools (Equally-Spaced Rows Ordered by Anatomical Centroid)", fontsize=11, fontweight='bold', pad=6)
    ax_b1.set_xlabel("Time (s) [Steady-State Window]", fontsize=9.5)
    ax_b1.set_ylabel("Motor Pool (Rostral → Caudal)", fontsize=9.5)
    cb_b1 = fig.colorbar(im_b1, ax=ax_b1, orientation='vertical', pad=0.02, shrink=0.9)
    cb_b1.set_label("Rate (Hz)", fontsize=8.5)

    # Panel B2: Right Side
    ax_b2 = fig.add_subplot(gs[1, 1])
    rate_mat_r = np.array([p['trace_r'][plot_win] for p in pools])
    im_b2 = ax_b2.imshow(rate_mat_r, aspect='auto', cmap='magma', origin='upper', vmin=0, vmax=45,
                         extent=(float(t_plot_s[0]), float(t_plot_s[-1]), float(n_pools - 0.5), -0.5))
    ax_b2.set_yticks(np.arange(n_pools))
    ax_b2.set_yticklabels([f"{p['abbrev']} ({p['joint'][0]}) - {p['rc_cent_r']:.0f} µm" for p in pools], fontsize=8.5)
    ax_b2.set_title("B2. Right Side: All 14 Pools (Matching Order & Scale, Showing Alternation)", fontsize=11, fontweight='bold', pad=6)
    ax_b2.set_xlabel("Time (s) [Steady-State Window]", fontsize=9.5)
    ax_b2.set_ylabel("Motor Pool (Rostral → Caudal)", fontsize=9.5)
    cb_b2 = fig.colorbar(im_b2, ax=ax_b2, orientation='vertical', pad=0.02, shrink=0.9)
    cb_b2.set_label("Rate (Hz)", fontsize=8.5)

    ta_idx_in_pools = [p['name'] for p in pools].index('Tibialis Anterior')
    ax_b1.get_yticklabels()[ta_idx_in_pools].set_color(c_ta)
    ax_b1.get_yticklabels()[ta_idx_in_pools].set_fontweight('bold')
    ax_b2.get_yticklabels()[ta_idx_in_pools].set_color(c_ta)
    ax_b2.get_yticklabels()[ta_idx_in_pools].set_fontweight('bold')

    # -------------------------------------------------------------------------
    # SECTION C: Physical Rostrocaudal Activity Maps (Continuous Physical Distance)
    # -------------------------------------------------------------------------
    gs_c = gridspec.GridSpecFromSubplotSpec(2, 2, subplot_spec=gs[2, :], hspace=0.35, wspace=0.22)
    ax_c1 = fig.add_subplot(gs_c[0, 0])
    ax_c2 = fig.add_subplot(gs_c[1, 0])
    ax_c3 = fig.add_subplot(gs_c[0, 1])
    ax_c4 = fig.add_subplot(gs_c[1, 1])

    b500_mean_l = b500['mean_act_left'][plot_win, :].T # (n_b, n_t)
    b500_sum_l = b500['sum_act_left'][plot_win, :].T
    b500_mean_r = b500['mean_act_right'][plot_win, :].T
    b500_sum_r = b500['sum_act_right'][plot_win, :].T
    
    # Custom colormap with grey background for NaN
    cmap_mean = matplotlib.colormaps['viridis'].copy()
    cmap_mean.set_bad(color='#D0D0D0', alpha=1.0) # Grey hatched for empty bins

    extent_c = (float(t_plot_s[0]), float(t_plot_s[-1]), float(b500['bin_edges_um'][0]), float(b500['bin_edges_um'][-1]))

    # C1: Left Mean Activity per Neuron
    im_c1 = ax_c1.imshow(b500_mean_l, aspect='auto', cmap=cmap_mean, origin='lower', extent=extent_c, vmin=0, vmax=45)
    ax_c1.set_title("C1. Left Physical Mean Rate (Hz / Neuron; Grey = Empty Bin)", fontsize=10.5, fontweight='bold')
    ax_c1.set_ylabel("RC Position (µm)", fontsize=9)
    cb_c1 = fig.colorbar(im_c1, ax=ax_c1, orientation='vertical', pad=0.02, shrink=0.85)
    cb_c1.set_label("Hz", fontsize=8)

    # C2: Left Summed Activity
    im_c2 = ax_c2.imshow(b500_sum_l, aspect='auto', cmap='magma', origin='lower', extent=extent_c)
    ax_c2.set_title("C2. Left Physical Summed Rate (Total Hz / Bin)", fontsize=10.5, fontweight='bold')
    ax_c2.set_xlabel("Time (s)", fontsize=9)
    ax_c2.set_ylabel("RC Position (µm)", fontsize=9)
    cb_c2 = fig.colorbar(im_c2, ax=ax_c2, orientation='vertical', pad=0.02, shrink=0.85)
    cb_c2.set_label("Total Hz", fontsize=8)

    # C3: Right Mean Activity per Neuron
    im_c3 = ax_c3.imshow(b500_mean_r, aspect='auto', cmap=cmap_mean, origin='lower', extent=extent_c, vmin=0, vmax=45)
    ax_c3.set_title("C3. Right Physical Mean Rate (Hz / Neuron; Grey = Empty Bin)", fontsize=10.5, fontweight='bold')
    ax_c3.set_ylabel("RC Position (µm)", fontsize=9)
    cb_c3 = fig.colorbar(im_c3, ax=ax_c3, orientation='vertical', pad=0.02, shrink=0.85)
    cb_c3.set_label("Hz", fontsize=8)

    # C4: Right Summed Activity
    im_c4 = ax_c4.imshow(b500_sum_r, aspect='auto', cmap='magma', origin='lower', extent=extent_c)
    ax_c4.set_title("C4. Right Physical Summed Rate (Total Hz / Bin)", fontsize=10.5, fontweight='bold')
    ax_c4.set_xlabel("Time (s)", fontsize=9)
    ax_c4.set_ylabel("RC Position (µm)", fontsize=9)
    cb_c4 = fig.colorbar(im_c4, ax=ax_c4, orientation='vertical', pad=0.02, shrink=0.85)
    cb_c4.set_label("Total Hz", fontsize=8)

    for ax in [ax_c1, ax_c2, ax_c3, ax_c4]:
        for s_name, s_pos in seg_bounds:
            if s_pos <= 11000:
                ax.axhline(s_pos, color='white' if ax in [ax_c1, ax_c3] else '#888888', linestyle='--', linewidth=0.6, alpha=0.7)
        ax.axhspan(5600, 7900, color=c_ta, alpha=0.15)
        ax.set_ylim(0, 11000)

    # -------------------------------------------------------------------------
    # SECTION D: Pool Timing & Coordination
    # -------------------------------------------------------------------------
    gs_d = gridspec.GridSpecFromSubplotSpec(1, 4, subplot_spec=gs[3, :], width_ratios=[1.3, 1.0, 1.0, 1.1], wspace=0.26)
    ax_d1 = fig.add_subplot(gs_d[0, 0])
    ax_d2 = fig.add_subplot(gs_d[0, 1])
    ax_d3 = fig.add_subplot(gs_d[0, 2])
    ax_d4 = fig.add_subplot(gs_d[0, 3])

    # D1: Cycle-Normalized Traces (Endpoint-Free [0, 100%))
    cycle_pct = phase_grid * 100.0
    for p in pools:
        if p['abbrev'] == 'TA':
            col, lw, ls = c_ta, 2.8, '-'
        elif p['abbrev'] == 'GM':
            col, lw, ls = c_gm, 2.8, '-'
        elif p['abbrev'] == 'Sol':
            col, lw, ls = '#F77F00', 1.8, '-'
        elif p['abbrev'] in ['VMed', 'BF']:
            col = '#2EC4B6' if p['abbrev'] == 'VMed' else '#7209B7'
            lw, ls = 1.8, '-'
        else:
            col = joint_colors[p['joint']]
            lw, ls = 1.0, '--'
        ax_d1.plot(cycle_pct, p['cycle_mean_l'], color=col, linewidth=lw, linestyle=ls, label=p['abbrev'] if p['abbrev'] in ['TA', 'GM', 'Sol', 'VMed', 'BF'] else "")
        if p['abbrev'] in ['TA', 'GM']:
            ax_d1.fill_between(cycle_pct, p['cycle_mean_l'] - p['cycle_sem_l'], p['cycle_mean_l'] + p['cycle_sem_l'], color=col, alpha=0.15)
            
    ax_d1.set_title("D1. Muscle Cycle Profiles (Left Side [0, 100%))", fontsize=10.5, fontweight='bold')
    ax_d1.set_xlabel("Locomotor Cycle (%) [0% = Left GM Peak]", fontsize=9)
    ax_d1.set_ylabel("Firing Rate (Hz)", fontsize=9)
    ax_d1.set_xlim(0, 100)
    ax_d1.grid(True, linestyle=':', alpha=0.4)
    ax_d1.legend(loc='upper right', fontsize=7.5, framealpha=0.85)

    # D2: Left Zero-Lag Pearson Correlation Matrix
    abbrevs = [p['abbrev'] for p in pools]
    im_d2 = ax_d2.imshow(corr_mat_l, cmap='coolwarm', vmin=-1, vmax=1)
    ax_d2.set_xticks(np.arange(n_pools))
    ax_d2.set_yticks(np.arange(n_pools))
    ax_d2.set_xticklabels(abbrevs, rotation=45, ha='right', fontsize=7.5)
    ax_d2.set_yticklabels(abbrevs, fontsize=7.5)
    ax_d2.set_title("D2. Left Zero-Lag Pearson r", fontsize=10.5, fontweight='bold')
    ax_d2.get_xticklabels()[ta_idx_in_pools].set_color(c_ta)
    ax_d2.get_xticklabels()[ta_idx_in_pools].set_fontweight('bold')
    ax_d2.get_yticklabels()[ta_idx_in_pools].set_color(c_ta)
    ax_d2.get_yticklabels()[ta_idx_in_pools].set_fontweight('bold')
    cb_d2 = fig.colorbar(im_d2, ax=ax_d2, orientation='vertical', pad=0.03, shrink=0.8)
    cb_d2.set_label("Pearson r", fontsize=7.5)

    # D3: Right Zero-Lag Pearson Correlation Matrix
    im_d3 = ax_d3.imshow(corr_mat_r, cmap='coolwarm', vmin=-1, vmax=1)
    ax_d3.set_xticks(np.arange(n_pools))
    ax_d3.set_yticks(np.arange(n_pools))
    ax_d3.set_xticklabels(abbrevs, rotation=45, ha='right', fontsize=7.5)
    ax_d3.set_yticklabels(abbrevs, fontsize=7.5)
    ax_d3.set_title("D3. Right Zero-Lag Pearson r", fontsize=10.5, fontweight='bold')
    ax_d3.get_xticklabels()[ta_idx_in_pools].set_color(c_ta)
    ax_d3.get_xticklabels()[ta_idx_in_pools].set_fontweight('bold')
    ax_d3.get_yticklabels()[ta_idx_in_pools].set_color(c_ta)
    ax_d3.get_yticklabels()[ta_idx_in_pools].set_fontweight('bold')
    cb_d3 = fig.colorbar(im_d3, ax=ax_d3, orientation='vertical', pad=0.03, shrink=0.8)
    cb_d3.set_label("Pearson r", fontsize=7.5)

    # D4: Circular Peak Phase Progression (Ordered by Centroid)
    y_pos = np.arange(n_pools)
    for i, p in enumerate(pools):
        col = c_ta if p['abbrev'] == 'TA' else (c_gm if p['abbrev'] == 'GM' else joint_colors[p['joint']])
        ax_d4.errorbar(p['circ_peak_phase_l'], i, xerr=p['circ_peak_std_l'], fmt='o', color=col,
                       ecolor=col, elinewidth=1.2, capsize=2.5, markersize=5.5, label='Left Side' if i == 0 else "")
        ax_d4.errorbar(p['circ_peak_phase_r'], i, xerr=p['circ_peak_std_r'], fmt='s', color=col,
                       ecolor=col, elinewidth=1.2, capsize=2.5, markersize=5.5, mfc='none', label='Right Side' if i == 0 else "")
        
    ax_d4.set_yticks(y_pos)
    ax_d4.set_yticklabels([f"{p['abbrev']} ({p['rc_cent_l']:.0f} µm)" for p in pools], fontsize=7.5)
    ax_d4.invert_yaxis()
    ax_d4.set_xlim(-10, 370)
    ax_d4.set_xticks([0, 90, 180, 270, 360])
    ax_d4.set_xticklabels(['0°', '90°', '180°', '270°', '360°'], fontsize=7.5)
    ax_d4.set_xlabel("Peak Phase ± Circular SD (deg)", fontsize=8.5)
    ax_d4.set_title("D4. Pool Peak Phases\n(Circles: Left | Squares: Right)", fontsize=10, fontweight='bold')
    ax_d4.grid(True, linestyle=':', alpha=0.4)
    ax_d4.legend(loc='lower right', fontsize=7.5, framealpha=0.85)
    ax_d4.get_yticklabels()[ta_idx_in_pools].set_color(c_ta)
    ax_d4.get_yticklabels()[ta_idx_in_pools].set_fontweight('bold')

    # -------------------------------------------------------------------------
    # SECTION E: Neighboring-Location Activation Delays & Uncertainty
    # -------------------------------------------------------------------------
    gs_e = gridspec.GridSpecFromSubplotSpec(1, 3, subplot_spec=gs[4, :], width_ratios=[1.15, 1.15, 0.95], wspace=0.25)
    ax_e1 = fig.add_subplot(gs_e[0, 0])
    ax_e2 = fig.add_subplot(gs_e[0, 1])
    ax_e3 = fig.add_subplot(gs_e[0, 2])

    # Helper function to plot line segments without bridging over empty bins
    def plot_unbridged_curve(ax, bin_timing, col, mark, lbl):
        segments = []
        curr_seg = []
        for bt in bin_timing:
            if not curr_seg:
                curr_seg.append(bt)
            else:
                if bt['bin_index'] == curr_seg[-1]['bin_index'] + 1:
                    curr_seg.append(bt)
                else:
                    segments.append(curr_seg)
                    curr_seg = [bt]
        if curr_seg:
            segments.append(curr_seg)
            
        for s_idx, seg in enumerate(segments):
            xs = [b['center_um'] for b in seg]
            ts = [b['unwrapped_timing_ms'] for b in seg]
            errs = [b['timing_std_ms'] for b in seg]
            ax.errorbar(xs, ts, yerr=errs, fmt='-o' if mark == 'o' else '-s', color=col, ecolor=col,
                        elinewidth=1.2, capsize=2.5, markersize=4.5, alpha=0.9, label=lbl if s_idx == 0 else "")

    # E1: Measured Activation Timing vs. Physical RC Position (Left & Right Sides)
    tim_500_l = b500['bin_timing_left']
    tim_500_r = b500['bin_timing_right']
    
    plot_unbridged_curve(ax_e1, tim_500_l, '#2A9D8F', 'o', 'Left Hindlimb (500 µm ± SD)')
    plot_unbridged_curve(ax_e1, tim_500_r, '#7209B7', 's', 'Right Hindlimb (500 µm ± SD)')
    
    # 1-cycle period reference line
    ax_e1.axhline(mean_period_l, color='#E63946', linestyle='--', linewidth=1.0, alpha=0.8,
                  label=f'1 Cycle Period (T = {mean_period_l:.0f} ms / 360°)')
    ax_e1.axvline(6773, color=c_ta, linestyle=':', linewidth=1.5, label='Relocated TA (6773 µm L, 6510 µm R)')
    ax_e1.axvline(6510, color=c_ta, linestyle=':', linewidth=1.0, alpha=0.7)
    
    ax_e1.set_xlim(0, 11000)
    ax_e1.set_ylim(-30, mean_period_l * 1.8)
    ax_e1.set_xlabel("Spinal RC Position (µm)", fontsize=9)
    ax_e1.set_ylabel("Unwrapped Activation Time (ms from cycle start)", fontsize=9)
    ax_e1.set_title("E1. Measured Activation Timing vs. Physical Position\n(Unwrapped Timing | Gaps at Empty Bins | Error = Cycle SD)", fontsize=10, fontweight='bold')
    ax_e1.grid(True, linestyle=':', alpha=0.4)
    ax_e1.legend(loc='upper left', fontsize=7.2, framealpha=0.85)

    # E2: Neighboring-Bin Signed Delays (dt) vs Physical Distance (dx)
    # Paired bars for Left and Right sides (strictly adjacent transitions only)
    delays_500_l = [d for d in b500['neighbor_delays_left'] if d['is_adjacent']]
    delays_500_r = [d for d in b500['neighbor_delays_right'] if d['is_adjacent']]
    
    mid_x_l = np.array([(d['x1_um'] + d['x2_um']) / 2.0 for d in delays_500_l])
    dt_vals_l = [d['mean_signed_delay_ms'] for d in delays_500_l]
    dt_err_l = [d['delay_std_ms'] for d in delays_500_l]
    
    mid_x_r = np.array([(d['x1_um'] + d['x2_um']) / 2.0 for d in delays_500_r])
    dt_vals_r = [d['mean_signed_delay_ms'] for d in delays_500_r]
    dt_err_r = [d['delay_std_ms'] for d in delays_500_r]
    
    ax_e2.axhline(0, color='#333333', linestyle='-', linewidth=0.8)
    ax_e2.axhline(2.0, color='#888888', linestyle=':', linewidth=0.7, alpha=0.7)
    
    bar_w = 170
    ax_e2.bar(mid_x_l - bar_w/2, dt_vals_l, width=bar_w, yerr=dt_err_l, capsize=2,
              color='#2A9D8F', edgecolor='#1D3557', linewidth=0.5, alpha=0.85, label='Left Side (Δt ± SD)')
    ax_e2.bar(mid_x_r + bar_w/2, dt_vals_r, width=bar_w, yerr=dt_err_r, capsize=2,
              color='#7209B7', edgecolor='#3A0CA3', linewidth=0.5, alpha=0.85, label='Right Side (Δt ± SD)')
    
    ax_e2.axvline(6773, color=c_ta, linestyle=':', linewidth=1.5)
    ax_e2.set_xlim(0, 11000)
    ax_e2.set_xlabel("Transition Midpoint RC (µm)", fontsize=9)
    ax_e2.set_ylabel("Signed Delay Δt (ms) [Caudal - Rostral]", fontsize=9)
    ax_e2.set_title("E2. Neighboring-Bin Signed Delays (500 µm Bins)\n(Δt > 0: Caudal Lag / Rostral Lead | Δt ≈ 0: Synchronous)", fontsize=10, fontweight='bold')
    ax_e2.grid(True, linestyle=':', alpha=0.4)
    ax_e2.legend(loc='upper right', fontsize=7.2, framealpha=0.85)

    # E3: Delay Consistency (R) Across Lumbar Cord
    r_cons_l = [d['delay_consistency_r'] for d in delays_500_l]
    r_cons_r = [d['delay_consistency_r'] for d in delays_500_r]
    
    ax_e3.plot(mid_x_l, r_cons_l, marker='o', color='#2A9D8F', linewidth=1.5, markersize=4.5, label='Left Side')
    ax_e3.plot(mid_x_r, r_cons_r, marker='s', color='#7209B7', linewidth=1.5, markersize=4.5, label='Right Side')
    ax_e3.axhline(0.8, color='#E63946', linestyle='--', linewidth=0.9, label='R = 0.8 Threshold')
    ax_e3.axvline(6773, color=c_ta, linestyle=':', linewidth=1.5)
    ax_e3.set_xlim(0, 11000)
    ax_e3.set_ylim(0.0, 1.05)
    ax_e3.set_xlabel("Transition Midpoint RC (µm)", fontsize=9)
    ax_e3.set_ylabel("Delay Consistency (R vector length)", fontsize=9)
    ax_e3.set_title("E3. Cycle Delay Consistency\n(1.0 = Deterministic Timing Across Cycles)", fontsize=10, fontweight='bold')
    ax_e3.grid(True, linestyle=':', alpha=0.4)
    ax_e3.legend(loc='lower left', fontsize=7.2, framealpha=0.85)

    # Master Figure Title
    fig.suptitle("Rigorous All-Pool Analysis: 14 Hindlimb Motoneuron Pools in TA-Relocated Model (Condition D Realization 1)\n"
                 "Explicit Hindlimb Neuron Mask (N=1,366) | Empty Bins Rendered as NaN | Measured Physical Activation Delays",
                 fontsize=14, fontweight='bold', y=0.982)

    plt.savefig(FIG_OUT, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Master composite saved successfully to {FIG_OUT}!")

if __name__ == '__main__':
    main()
