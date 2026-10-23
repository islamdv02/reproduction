%% scripts/analyze_all_anatomical_waves.m
% Exhaustive anatomical wave test across:
% - Right and left motoneurons
% - Right and left interneurons
% - Each individual interneuron class (V2a-1, V2a-2, V1, V2b, V0v, V0d, DI6, V3)
% - 18 anatomical motoneuron pools
% - 11 spinal segments (T13 - S4)
% - Multi-resolution physical binning: 250 um, 500 um, 1000 um, and 50 bins (277 um)
% - Continuity quantification: neighboring vs skipped, physical jump distances,
%   CoM and peak trajectories, adjacent phase delays, circular-linear R^2,
%   and objective kinematic classification.
%
% Output: results/all_anatomical_wave_metrics.json and results/all_anatomical_wave_metrics.mat

clear; clc; close all;
t_start = tic;

scriptDir = fileparts(mfilename('fullpath'));
if isempty(scriptDir), scriptDir = pwd; end
rootDir = fullfile(scriptDir, '..');
sourceDir = fullfile(rootDir, 'source');
resultsDir = fullfile(rootDir, 'results');
compatDir = fullfile(rootDir, 'scripts', 'compat');

addpath(genpath(sourceDir));
addpath(compatDir);

fprintf('=================================================================\n');
fprintf('EXHAUSTIVE ANATOMICAL WAVE TEST & MULTI-POPULATION AUDIT\n');
fprintf('Timestamp: %s\n', datestr(now));
fprintf('=================================================================\n');

%% 1. Load Simulated Network
simFile = fullfile(resultsDir, 'simulated_network.mat');
fprintf('Loading: %s ...\n', simFile);
data_sim = load(simFile, 'N');
N = data_sim.N;

%% 2. Define Analysis Intervals and Reference
t_steps = size(N.Rates, 1);
steady_idx = 2000:t_steps; % 20,001 ms steady-state interval
n_t = length(steady_idx);
t_ms = (0:(n_t-1));

% Reference signal for cycle detection: Right L2 Motoneurons
l2_r_mask = (N.Segment == "L2") & (N.Types == "MN") & (N.Latera > 0);
ref_signal = mean(N.Rates(steady_idx, l2_r_mask), 2);

% Robust peak finder
ref_smooth = movmean(ref_signal, 20);
d_ref = diff(ref_smooth);
raw_peaks = find(d_ref(1:end-1) > 0 & d_ref(2:end) <= 0) + 1;
raw_peaks = raw_peaks(ref_smooth(raw_peaks) > (mean(ref_smooth) + 0.3*std(ref_smooth)));

% Enforce min distance ~500 ms
l2_peaks = [];
for pi = 1:length(raw_peaks)
    if isempty(l2_peaks)
        l2_peaks(end+1) = raw_peaks(pi);
    else
        if raw_peaks(pi) - l2_peaks(end) >= 400
            l2_peaks(end+1) = raw_peaks(pi);
        else
            if ref_smooth(raw_peaks(pi)) > ref_smooth(l2_peaks(end))
                l2_peaks(end) = raw_peaks(pi);
            end
        end
    end
end

n_cycles = length(l2_peaks) - 1;
cycle_period_ms = mean(diff(l2_peaks));
freq_hz = 1000 / cycle_period_ms;
fprintf('Detected %d full cycles | Mean period: %.1f ms | Frequency: %.3f Hz\n', ...
    n_cycles, cycle_period_ms, freq_hz);

%% 3. Population Definitions
rc_all = N.Position(:, 2);
rc_min = 0; rc_max = 14000;

% Master struct of populations to audit
pops = struct();

% 1 & 2: All Motoneurons (Right and Left)
pops.MN_Right.mask = (N.Types == "MN") & (N.Latera > 0);
pops.MN_Right.name = 'Right Motoneurons';
pops.MN_Right.type = 'MN';
pops.MN_Right.side = 'Right';

pops.MN_Left.mask  = (N.Types == "MN") & (N.Latera < 0);
pops.MN_Left.name  = 'Left Motoneurons';
pops.MN_Left.type  = 'MN';
pops.MN_Left.side  = 'Left';

% 3 & 4: All Interneurons (Right and Left)
pops.IN_Right.mask = (N.Types ~= "MN") & (N.Latera > 0);
pops.IN_Right.name = 'Right Interneurons (All)';
pops.IN_Right.type = 'IN';
pops.IN_Right.side = 'Right';

pops.IN_Left.mask  = (N.Types ~= "MN") & (N.Latera < 0);
pops.IN_Left.name  = 'Left Interneurons (All)';
pops.IN_Left.type  = 'IN';
pops.IN_Left.side  = 'Left';

% 5 - 20: Individual Interneuron Classes (Right and Left for each)
in_classes = {'V2a_1', 'V2a_2', 'V1', 'V2b', 'V0v', 'V0d', 'DI6', 'V3'};
class_type_labels = {'V2a-1', 'V2a-2', 'V1', 'V2b', 'V0v', 'V0d', 'DI6', 'V3'};

for c = 1:length(in_classes)
    cn = in_classes{c};
    clabel = class_type_labels{c};
    
    % Right
    f_r = sprintf('IN_%s_R', cn);
    pops.(f_r).mask = (N.Types == clabel) & (N.Latera > 0);
    pops.(f_r).name = sprintf('%s (Right)', clabel);
    pops.(f_r).type = 'IN_Class';
    pops.(f_r).class = clabel;
    pops.(f_r).side = 'Right';
    
    % Left
    f_l = sprintf('IN_%s_L', cn);
    pops.(f_l).mask = (N.Types == clabel) & (N.Latera < 0);
    pops.(f_l).name = sprintf('%s (Left)', clabel);
    pops.(f_l).type = 'IN_Class';
    pops.(f_l).class = clabel;
    pops.(f_l).side = 'Left';
end

pop_keys = fieldnames(pops);
fprintf('\nConfigured %d populations for exhaustive wave testing.\n', length(pop_keys));

%% 4. Execute Physical RC Bin Analysis Across Populations
bin_configs = [250, 500, 1000, 280]; % 280 represents 50 bins across 14,000 um (~277-280 um)
config_names = {'bins_250um', 'bins_500um', 'bins_1000um', 'bins_50bins'};

all_results = struct();
all_results.meta.timestamp = datestr(now);
all_results.meta.total_neurons = length(rc_all);
all_results.meta.steady_duration_ms = n_t;
all_results.meta.n_cycles = n_cycles;
all_results.meta.cycle_period_ms = cycle_period_ms;
all_results.meta.frequency_hz = freq_hz;

fprintf('\n--- EXECUTING PHYSICAL RC BIN ANALYSIS ACROSS POPULATIONS ---\n');

for k = 1:length(pop_keys)
    pk = pop_keys{k};
    p_mask = pops.(pk).mask;
    n_somas = nnz(p_mask);
    
    all_results.populations.(pk).name = pops.(pk).name;
    all_results.populations.(pk).soma_count = n_somas;
    all_results.populations.(pk).side = pops.(pk).side;
    
    if n_somas < 5
        fprintf('Skipping %s (only %d somas)...\n', pk, n_somas);
        continue;
    end
    
    rc_p = rc_all(p_mask);
    rates_p = N.Rates(steady_idx, p_mask)'; % (N_p, n_t)
    
    % Test each binning resolution
    for bc = 1:length(bin_configs)
        bw = bin_configs(bc);
        cname = config_names{bc};
        
        if bw == 280
            % 50 bins
            n_bins = 50;
            bin_edges = linspace(rc_min, rc_max, n_bins + 1);
            act_bw = (rc_max - rc_min) / n_bins;
        else
            bin_edges = rc_min:bw:rc_max;
            n_bins = length(bin_edges) - 1;
            act_bw = bw;
        end
        bin_centers = bin_edges(1:end-1) + act_bw / 2;
        
        % Compute Binned Rates: (n_bins, n_t)
        binned_r = zeros(n_bins, n_t);
        bin_counts = zeros(n_bins, 1);
        for b = 1:n_bins
            in_b = (rc_p >= bin_edges(b)) & (rc_p < bin_edges(b+1));
            bin_counts(b) = sum(in_b);
            if bin_counts(b) > 0
                binned_r(b, :) = mean(rates_p(in_b, :), 1);
            end
        end
        
        % Metrics calculation
        res = compute_kinematic_metrics(binned_r, bin_centers, act_bw, cycle_period_ms, ref_signal);
        res.bin_width_um = act_bw;
        res.bin_count = n_bins;
        res.active_bins = sum(bin_counts > 0);
        
        all_results.populations.(pk).(cname) = res;
    end
    
    % Print primary summary (using 500 um bins)
    r500 = all_results.populations.(pk).bins_500um;
    fprintf('%-15s (N=%4d) | Dwell: %5.1f%% | Neigh: %5.1f%% | Skip: %5.1f%% | MedJump: %6.1f um | R2: %.3f (p=%.3f) -> %s\n', ...
        pk, n_somas, r500.dwell_fraction*100, r500.neighboring_fraction*100, r500.skipped_fraction*100, ...
        r500.within_cycle_jump_median_um, r500.circular_linear_R2, r500.circular_linear_p, r500.classification);
end

%% 5. Anatomical Motoneuron Pools Analysis (18 Pools)
fprintf('\n--- EXECUTING ANATOMICAL MOTONEURON POOLS ANALYSIS (18 POOLS) ---\n');
pool_csv = fullfile(resultsDir, 'wave_baseline', 'motoneuron_pool_anatomy.csv');
pool_tab = readtable(pool_csv);
[~, pool_order] = sort(pool_tab.rc_mean_um, 'ascend');
sorted_pools = pool_tab(pool_order, :);
n_pools = height(sorted_pools);

sides = {'Right', 'Left'};
for s = 1:2
    side_str = sides{s};
    if s == 1
        s_mask = (N.Types == "MN") & (N.Latera > 0);
    else
        s_mask = (N.Types == "MN") & (N.Latera < 0);
    end
    
    pool_rates = zeros(n_pools, n_t);
    pool_somata_counts = zeros(n_pools, 1);
    pool_centroids = sorted_pools.rc_mean_um;
    
    for p = 1:n_pools
        p_name = sorted_pools.pool_name{p};
        p_idx = s_mask & (string(N.MnID) == string(p_name));
        pool_somata_counts(p) = nnz(p_idx);
        if pool_somata_counts(p) > 0
            pool_rates(p, :) = mean(N.Rates(steady_idx, p_idx), 2)';
        end
    end
    
    % Track dominant pool identity
    [~, dom_pool] = max(pool_rates, [], 1);
    dom_pool_filt = movmedian(dom_pool, 5);
    
    % Pool transitions
    pool_changes = find(diff(dom_pool_filt) ~= 0);
    total_pool_trans = length(pool_changes);
    dwell_fr = 1 - (total_pool_trans / n_t);
    
    pool_step_indices = [];
    pool_jump_distances_um = [];
    pool_rostral_caudal_switches = 0;
    
    for ch = 1:total_pool_trans
        idx1 = dom_pool_filt(pool_changes(ch));
        idx2 = dom_pool_filt(pool_changes(ch) + 1);
        step_idx = abs(idx2 - idx1);
        jump_dist = abs(pool_centroids(idx2) - pool_centroids(idx1));
        
        % Detect caudal->rostral resets across cycle boundary
        is_reset = (idx1 >= 12 && idx2 <= 6);
        if ~is_reset
            pool_step_indices(end+1) = step_idx;
            pool_jump_distances_um(end+1) = jump_dist;
            if jump_dist > 3000
                pool_rostral_caudal_switches = pool_rostral_caudal_switches + 1;
            end
        end
    end
    
    neigh_fr = mean(pool_step_indices == 1);
    skip_fr = mean(pool_step_indices >= 2);
    med_jump = median(pool_jump_distances_um);
    
    % Phase correlation across pools
    pool_phases = zeros(n_pools, 1);
    for p = 1:n_pools
        if pool_somata_counts(p) > 0
            [c_sig, lags] = xcorr(ref_signal, pool_rates(p, :)');
            [~, m_idx] = max(c_sig);
            lag_ms = lags(m_idx);
            pool_phases(p) = mod(rem(lag_ms * 2*pi / cycle_period_ms, 2*pi), 2*pi);
        else
            pool_phases(p) = nan;
        end
    end
    valid_pools = ~isnan(pool_phases);
    [R2_pool, p_val_pool] = circular_linear_corr(pool_centroids(valid_pools), pool_phases(valid_pools));
    
    pool_res = struct();
    pool_res.name = sprintf('%s Motoneuron Pools (18 Pools)', side_str);
    pool_res.total_transitions = total_pool_trans;
    pool_res.dwell_fraction = dwell_fr;
    pool_res.neighboring_fraction = neigh_fr;
    pool_res.skipped_fraction = skip_fr;
    pool_res.within_cycle_jump_median_um = med_jump;
    pool_res.rostral_caudal_switches_count = pool_rostral_caudal_switches;
    pool_res.circular_linear_R2 = R2_pool;
    pool_res.circular_linear_p = p_val_pool;
    
    if skip_fr >= 0.60
        pool_res.classification = 'JUMP-LIKE / MODULAR';
    elseif neigh_fr >= 0.70
        pool_res.classification = 'SMOOTH';
    else
        pool_res.classification = 'MIXED';
    end
    
    all_results.pools.(sprintf('%s_Pools', side_str)) = pool_res;
    fprintf('%-15s (18 Pools) | Dwell: %5.1f%% | Neigh: %5.1f%% | Skip: %5.1f%% | MedJump: %6.1f um | R2: %.3f (p=%.3f) -> %s\n', ...
        sprintf('%s_Pools', side_str), dwell_fr*100, neigh_fr*100, skip_fr*100, med_jump, R2_pool, p_val_pool, pool_res.classification);
end

%% 6. Spinal Segments Analysis (11 Segments: T13 to S4)
fprintf('\n--- EXECUTING SPINAL SEGMENTAL ANALYSIS (11 SEGMENTS) ---\n');
segments_list = {'T13', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'S1', 'S2', 'S3', 'S4'};
n_segs = length(segments_list);
seg_lengths = [1180, 1180, 1180, 1180, 1180, 1180, 1180, 1180, 1180, 1180, 1180];
seg_centroids = cumsum(seg_lengths) - seg_lengths/2;

for s = 1:2
    side_str = sides{s};
    if s == 1
        s_mask = (N.Latera > 0);
    else
        s_mask = (N.Latera < 0);
    end
    
    seg_rates = zeros(n_segs, n_t);
    seg_somata_counts = zeros(n_segs, 1);
    
    for seg_i = 1:n_segs
        s_name = segments_list{seg_i};
        seg_idx = s_mask & (string(N.Segment) == string(s_name));
        seg_somata_counts(seg_i) = nnz(seg_idx);
        if seg_somata_counts(seg_i) > 0
            seg_rates(seg_i, :) = mean(N.Rates(steady_idx, seg_idx), 2)';
        end
    end
    
    % Dominant segment tracking
    [~, dom_seg] = max(seg_rates, [], 1);
    dom_seg_filt = movmedian(dom_seg, 5);
    
    seg_changes = find(diff(dom_seg_filt) ~= 0);
    total_seg_trans = length(seg_changes);
    dwell_fr_seg = 1 - (total_seg_trans / n_t);
    
    seg_step_indices = [];
    seg_jump_distances_um = [];
    seg_switches = 0;
    
    for ch = 1:total_seg_trans
        idx1 = dom_seg_filt(seg_changes(ch));
        idx2 = dom_seg_filt(seg_changes(ch) + 1);
        step_idx = abs(idx2 - idx1);
        jump_dist = abs(seg_centroids(idx2) - seg_centroids(idx1));
        
        is_reset = (idx1 >= 8 && idx2 <= 4);
        if ~is_reset
            seg_step_indices(end+1) = step_idx;
            seg_jump_distances_um(end+1) = jump_dist;
            if jump_dist > 3000
                seg_switches = seg_switches + 1;
            end
        end
    end
    
    neigh_fr_seg = mean(seg_step_indices == 1);
    skip_fr_seg = mean(seg_step_indices >= 2);
    med_jump_seg = median(seg_jump_distances_um);
    
    % Phase correlation across segments
    seg_phases = zeros(n_segs, 1);
    for seg_i = 1:n_segs
        [c_sig, lags] = xcorr(ref_signal, seg_rates(seg_i, :)');
        [~, m_idx] = max(c_sig);
        lag_ms = lags(m_idx);
        seg_phases(seg_i) = mod(rem(lag_ms * 2*pi / cycle_period_ms, 2*pi), 2*pi);
    end
    [R2_seg, p_val_seg] = circular_linear_corr(seg_centroids', seg_phases);
    
    seg_res = struct();
    seg_res.name = sprintf('%s Spinal Segments (11 Segments)', side_str);
    seg_res.total_transitions = total_seg_trans;
    seg_res.dwell_fraction = dwell_fr_seg;
    seg_res.neighboring_fraction = neigh_fr_seg;
    seg_res.skipped_fraction = skip_fr_seg;
    seg_res.within_cycle_jump_median_um = med_jump_seg;
    seg_res.rostral_caudal_switches_count = seg_switches;
    seg_res.circular_linear_R2 = R2_seg;
    seg_res.circular_linear_p = p_val_seg;
    
    if neigh_fr_seg >= 0.70
        seg_res.classification = 'SMOOTH';
    elseif skip_fr_seg >= 0.60
        seg_res.classification = 'JUMP-LIKE';
    else
        seg_res.classification = 'MIXED';
    end
    
    all_results.segments.(sprintf('%s_Segments', side_str)) = seg_res;
    fprintf('%-15s (11 Segs)  | Dwell: %5.1f%% | Neigh: %5.1f%% | Skip: %5.1f%% | MedJump: %6.1f um | R2: %.3f (p=%.3f) -> %s\n', ...
        sprintf('%s_Segments', side_str), dwell_fr_seg*100, neigh_fr_seg*100, skip_fr_seg*100, med_jump_seg, R2_seg, p_val_seg, seg_res.classification);
end

%% 7. Export Metrics to JSON and MAT
outMat = fullfile(resultsDir, 'all_anatomical_wave_metrics.mat');
save(outMat, 'all_results', '-v7');
fprintf('\nSaved MAT: %s\n', outMat);

outJson = fullfile(resultsDir, 'all_anatomical_wave_metrics.json');
json_text = jsonencode(all_results, 'PrettyPrint', true);
fid = fopen(outJson, 'w');
fwrite(fid, json_text, 'char');
fclose(fid);
fprintf('Saved JSON: %s (%d bytes)\n', outJson, length(json_text));

fprintf('Exhaustive wave testing completed in %.2f seconds.\n', toc(t_start));

%% Helper Functions
function res = compute_kinematic_metrics(binned_rates, bin_centers, bin_width, cycle_period, ref_sig)
    n_bins = size(binned_rates, 1);
    n_t = size(binned_rates, 2);
    
    % 1. Activity-Weighted Center of Mass
    com_traj = zeros(1, n_t);
    for t = 1:n_t
        col = binned_rates(:, t);
        s_col = sum(col);
        if s_col > 0
            com_traj(t) = sum(bin_centers(:) .* col) / s_col;
        else
            com_traj(t) = 7000;
        end
    end
    
    % 2. Peak Location (Filtered with 5 ms temporal moving median)
    [~, raw_peak_bins] = max(binned_rates, [], 1);
    filt_peak_bins = round(movmedian(raw_peak_bins, 5));
    filt_peak_bins = max(1, min(n_bins, filt_peak_bins));
    peak_traj = bin_centers(filt_peak_bins);
    
    % 3. Transition Events
    trans_locs = find(diff(filt_peak_bins) ~= 0);
    total_trans = length(trans_locs);
    dwell_fraction = 1 - (total_trans / n_t);
    
    step_bins = [];
    step_distances_um = [];
    rostral_caudal_switches = 0;
    
    for tr = 1:total_trans
        b1 = filt_peak_bins(trans_locs(tr));
        b2 = filt_peak_bins(trans_locs(tr) + 1);
        sb = abs(b2 - b1);
        dist_um = abs(bin_centers(b2) - bin_centers(b1));
        
        % Detect intercycle resets (caudal third -> rostral third)
        is_reset = (b1 >= round(n_bins * 0.65)) && (b2 <= round(n_bins * 0.35));
        if ~is_reset
            step_bins(end+1) = sb;
            step_distances_um(end+1) = dist_um;
            if dist_um > 3000
                rostral_caudal_switches = rostral_caudal_switches + 1;
            end
        end
    end
    
    if isempty(step_bins)
        step_bins = 0;
        step_distances_um = 0;
    end
    
    neigh_fr = mean(step_bins == 1);
    skip_fr = mean(step_bins >= 2);
    med_jump = median(step_distances_um);
    iqr_jump = iqr(step_distances_um);
    p95_jump = prctile(step_distances_um, 95);
    
    % 4. Circular-Linear Phase Analysis
    bin_phases = zeros(n_bins, 1);
    for b = 1:n_bins
        if max(binned_rates(b, :)) > 0.1
            [c_sig, lags] = xcorr(ref_sig, binned_rates(b, :)');
            [~, m_idx] = max(c_sig);
            lag_ms = lags(m_idx);
            bin_phases(b) = mod(rem(lag_ms * 2*pi / cycle_period, 2*pi), 2*pi);
        else
            bin_phases(b) = nan;
        end
    end
    valid_b = ~isnan(bin_phases);
    if sum(valid_b) >= 4
        [R2, p_val] = circular_linear_corr(bin_centers(valid_b), bin_phases(valid_b));
        p_fit = polyfit(bin_centers(valid_b), unwrap(bin_phases(valid_b)), 1);
        phase_slope = p_fit(1);
    else
        R2 = 0; p_val = 1.0; phase_slope = 0;
    end
    
    % 5. Adjacent-Bin Phase Delays
    valid_idx = find(valid_b);
    adj_delays = [];
    for vi = 1:(length(valid_idx)-1)
        if valid_idx(vi+1) == valid_idx(vi) + 1
            d_phi = angle(exp(1i * (bin_phases(valid_idx(vi+1)) - bin_phases(valid_idx(vi)))));
            adj_delays(end+1) = d_phi;
        end
    end
    if isempty(adj_delays), adj_delays = 0; end
    
    % 6. Classification
    if skip_fr >= 0.60
        classification = 'JUMP-LIKE / MODULAR';
    elseif neigh_fr >= 0.70 && R2 >= 0.50
        classification = 'SMOOTH';
    elseif dwell_fraction > 0.95 && rostral_caudal_switches > 0
        classification = 'SWITCHING / MODULAR';
    else
        classification = 'MIXED';
    end
    
    res = struct();
    res.total_transitions = total_trans;
    res.dwell_fraction = dwell_fraction;
    res.neighboring_fraction = neigh_fr;
    res.skipped_fraction = skip_fr;
    res.within_cycle_jump_median_um = med_jump;
    res.within_cycle_jump_iqr_um = iqr_jump;
    res.within_cycle_jump_p95_um = p95_jump;
    res.rostral_caudal_switches_count = rostral_caudal_switches;
    res.circular_linear_R2 = R2;
    res.circular_linear_p = p_val;
    res.local_phase_slope = phase_slope;
    res.mean_adjacent_phase_delay_rad = mean(adj_delays);
    res.classification = classification;
end

function [R2, p_val] = circular_linear_corr(x, theta)
    x = x(:); theta = theta(:);
    n = length(x);
    if n < 4, R2 = 0; p_val = 1.0; return; end
    
    r_xc = p_corr(x, cos(theta));
    r_xs = p_corr(x, sin(theta));
    r_cs = p_corr(cos(theta), sin(theta));
    
    denom = 1 - r_cs^2;
    if abs(denom) < 1e-12
        R2 = 0;
    else
        R2 = (r_xc^2 + r_xs^2 - 2 * r_xc * r_xs * r_cs) / denom;
    end
    R2 = max(0, min(1, R2));
    
    n_perm = 200;
    count = 0;
    for p = 1:n_perm
        perm_theta = theta(randperm(n));
        r_xc_p = p_corr(x, cos(perm_theta));
        r_xs_p = p_corr(x, sin(perm_theta));
        r_cs_p = p_corr(cos(perm_theta), sin(perm_theta));
        denom_p = 1 - r_cs_p^2;
        if abs(denom_p) < 1e-12
            R2_p = 0;
        else
            R2_p = (r_xc_p^2 + r_xs_p^2 - 2 * r_xc_p * r_xs_p * r_cs_p) / denom_p;
        end
        if R2_p >= R2
            count = count + 1;
        end
    end
    p_val = count / n_perm;
end

function r = p_corr(a, b)
    a = a - mean(a);
    b = b - mean(b);
    sa = norm(a);
    sb = norm(b);
    if sa == 0 || sb == 0
        r = 0;
    else
        r = sum(a .* b) / (sa * sb);
    end
end
