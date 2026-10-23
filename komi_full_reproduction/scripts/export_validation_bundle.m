%% export_validation_bundle.m
% Exports a compact validation_bundle.mat containing exact processed arrays
% used to produce Figures 3-5 of the Komi et al. (2026) reproduction suite.
% Excludes massive raw rate matrices (>500 MB) to keep file compact (<30 MB).
%
% Contents:
% 1. neuron_metadata: Position, Types, Segment, Latera, MnID, FlexExtID, ConnMat (sparse)
% 2. fig3_data: eigenspectrum, spatial eigenmodes, input drive, activation curve,
%               spatial heatmap, EMG traces, segmental neurograms, polar phases,
%               phase distribution, PCA scores (PC1, PC3), frequency.
% 3. fig4_data: target masks (LPGi, Raphe), innervation percentages, drive/gain profiles,
%               effective projectomes (Walk, Trot, Bound), 12s nerve & EMG traces,
%               binned spatial raster, gait metrics.
% 4. fig5_data: target masks (V1, V0), projectome profiles (intact & perturbed),
%               8s nerve traces (Control, Silenced, Ablated for V1 and V0),
%               perturbation metrics (frequency, amplitude, polar phase).

clear; clc;
t_start = tic;

scriptDir = fileparts(mfilename('fullpath'));
rootDir = fullfile(scriptDir, '..');
sourceDir = fullfile(rootDir, 'source');
resultsDir = fullfile(rootDir, 'results');

cd(sourceDir);
addpath(genpath(sourceDir));

fprintf('=================================================================\n');
fprintf('EXPORT VALIDATION BUNDLE (Compact MAT Archive)\n');
fprintf('Timestamp: %s\n', datestr(now));
fprintf('=================================================================\n');

%% 1. Load Baseline Network and Extract Metadata
fprintf('Loading baseline network from results/baseline_network.mat...\n');
load(fullfile(resultsDir, 'baseline_network.mat'), 'N');
N_neurons = size(N.ConnMat, 1);

neuron_metadata = struct();
neuron_metadata.N_neurons = N_neurons;
neuron_metadata.Position = N.Position; % [4934 x 3] (ML, RC, DV)
neuron_metadata.Types = string(N.Types);
neuron_metadata.Segment = string(N.Segment);
neuron_metadata.Latera = N.Latera;
neuron_metadata.MnID = string(N.MnID);
neuron_metadata.FlexExtID = string(N.FlexExtID);
neuron_metadata.ConnMat = sparse(N.ConnMat); % Compact sparse matrix
neuron_metadata.Sparsity = full(N.Sparsity);

%% 2. Figure 3 Processed Arrays
fprintf('\nProcessing Figure 3 Arrays...\n');
fig3_data = struct();

% Eigenspectrum & Spatial Eigenmodes
W_full = full(N.ConnMat);
[~, bevr] = eig(W_full, 'vector');
fig3_data.eigenvalues = bevr;
fig3_data.eigenvalues_real = real(bevr);
fig3_data.eigenvalues_imag = imag(bevr);
fig3_data.dominant_modes_mask = real(bevr) > 1.0;
fig3_data.dominant_count = sum(fig3_data.dominant_modes_mask);

N.ComputeEigenModesandNullSpace('Verbose', 0);
fig3_data.spatial_mode1 = real(N.EigenModes(1, :))';
fig3_data.spatial_mode2 = real(N.EigenModes(2, :))';

% Input drive & Activation curve
fig3_data.t_drive_ms = 0:10:4000;
fig3_data.I_drive_pA = 30.0 * ones(size(fig3_data.t_drive_ms));

V_range = linspace(0, 150, 500);
fig3_data.V_range = V_range;
fig3_data.gains = [0.5, 1.0, 1.5];
fig3_data.activation_curves = zeros(3, 500);
threshold = 5; f_max = 50;
for g_idx = 1:3
    gn = fig3_data.gains(g_idx);
    f = zeros(size(V_range));
    neg = (V_range - threshold) <= 0;
    pos = (V_range - threshold) > 0;
    f(neg) = threshold .* tanh(gn .* (V_range(neg) - threshold) ./ threshold);
    f(pos) = f_max .* tanh(gn .* (V_range(pos) - threshold) ./ f_max);
    val = f + threshold;
    val(val < 0) = 0;
    fig3_data.activation_curves(g_idx, :) = val;
end

% Load Simulated Network for Figure 3 Traces & Dynamics
fprintf('Loading simulated network from results/simulated_network.mat...\n');
load(fullfile(resultsDir, 'simulated_network.mat'), 'N');
t_win = 1500:3500;
t_axis = (t_win - t_win(1));

% Spatial Heatmap (Right hemicord along RC axis)
right_mask = (N.Latera > 0);
y_right = N.Position(right_mask, 2);
[y_sorted, sort_rc] = sort(y_right, 'ascend');
rates_right = N.Rates(t_win, right_mask);
rates_sorted = rates_right(:, sort_rc)';

y_bins = linspace(min(y_sorted), max(y_sorted), 80);
binned_rates = zeros(length(y_bins)-1, length(t_axis));
for b = 1:(length(y_bins)-1)
    in_bin = (y_sorted >= y_bins(b)) & (y_sorted < y_bins(b+1));
    if any(in_bin)
        binned_rates(b, :) = mean(rates_sorted(in_bin, :), 1);
    end
end
fig3_data.spatial_heatmap_y_bins = y_bins;
fig3_data.spatial_heatmap_t_axis_ms = t_axis;
fig3_data.spatial_heatmap_binned_rates = binned_rates;

% Muscle EMGs
noiselevel = 0.1;
rng(42);
muscles_plot = {'Vastus Medialis', 'Biceps Femoris', 'Tibialis Anterior', 'Soleus'};
fig3_data.emg_t_axis_ms = t_axis;
fig3_data.emg_traces = struct();

for m = 1:length(muscles_plot)
    m_name = muscles_plot{m};
    m_field = matlab.lang.makeValidName(m_name);
    ix_m = (N.MnID == m_name) & (N.Latera > 0);
    if any(ix_m)
        prob = sum(N.Rates(t_win, ix_m), 2);
        sig = randn(size(prob)) * noiselevel .* binornd(1, normcdf(normalize(prob, 'zscore')));
        sig = sig .* prob + (randn(size(prob)) * noiselevel);
        env = movmean(abs(sig), 20);
        fig3_data.emg_traces.(m_field).raw = sig;
        fig3_data.emg_traces.(m_field).envelope = env;
    end
end

% Segmental Neurograms (L1 to L6)
fig3_data.neurogram_traces = struct();
for s = 1:6
    s_name = sprintf('L%d', s);
    ix_s = (N.Segment == s_name) & (N.Types == 'MN') & (N.Latera > 0);
    if any(ix_s)
        prob = sum(N.Rates(t_win, ix_s), 2);
        sig = randn(size(prob)) * noiselevel .* binornd(1, normcdf(normalize(prob, 'zscore')));
        sig = sig .* prob + (randn(size(prob)) * noiselevel);
        env = movmean(abs(sig), 20);
        fig3_data.neurogram_traces.(s_name).raw = sig;
        fig3_data.neurogram_traces.(s_name).envelope = env;
    end
end

% Polar Phase Relationships
l2_l_mask = (N.Types == 'MN') & (N.Segment == 'L2') & (N.Latera < 0);
l2_r_mask = (N.Types == 'MN') & (N.Segment == 'L2') & (N.Latera > 0);
l5_l_mask = (N.Types == 'MN') & (N.Segment == 'L5') & (N.Latera < 0);

r_l2_l = mean(N.Rates(t_win, l2_l_mask), 2);
r_l2_r = mean(N.Rates(t_win, l2_r_mask), 2);
r_l5_l = mean(N.Rates(t_win, l5_l_mask), 2);

min_prom = 0.20 * (max(r_l2_l) - min(r_l2_l));
[~, locs_l2_l] = findpeaks(r_l2_l, 'MinPeakDistance', 80, 'MinPeakProminence', min_prom);
[~, locs_l2_r] = findpeaks(r_l2_r, 'MinPeakDistance', 80, 'MinPeakProminence', min_prom);
[~, locs_l5_l] = findpeaks(r_l5_l, 'MinPeakDistance', 80, 'MinPeakProminence', min_prom);

T_cyc = mean(diff(locs_l2_l));
fig3_data.cycle_period_ms = T_cyc;
fig3_data.frequency_hz = 1000 / T_cyc;

lr_phases = [];
for k = 1:length(locs_l2_l)
    if ~isempty(locs_l2_r)
        [~, nearest] = min(abs(locs_l2_r - locs_l2_l(k)));
        dt = locs_l2_r(nearest) - locs_l2_l(k);
        phi = mod(dt / T_cyc * 2 * pi, 2 * pi);
        lr_phases(end+1) = phi;
    end
end

l2_l5_phases = [];
for k = 1:length(locs_l2_l)
    if ~isempty(locs_l5_l)
        [~, nearest] = min(abs(locs_l5_l - locs_l2_l(k)));
        dt = locs_l5_l(nearest) - locs_l2_l(k);
        phi = mod(dt / T_cyc * 2 * pi, 2 * pi);
        l2_l5_phases(end+1) = phi;
    end
end

fig3_data.lr_phases_rad = lr_phases;
fig3_data.l2_l5_phases_rad = l2_l5_phases;
fig3_data.mean_lr_phase_rad = circ_mean_local(lr_phases');
fig3_data.mean_lr_phase_deg = rad2deg(fig3_data.mean_lr_phase_rad);
fig3_data.mean_l2l5_phase_rad = circ_mean_local(l2_l5_phases');
fig3_data.mean_l2l5_phase_deg = rad2deg(fig3_data.mean_l2l5_phase_rad);

% Neuronal Phase Distribution
[sort_idx, scores, corrs] = ComputeFiringPhaseSorting(N.Rates(t_win, :));
fig3_data.phase_scores = scores;
fig3_data.phase_corrs = corrs;
fig3_data.rhythmic_neuron_count = sum(corrs > 0.3);

% PCA Rotational Dynamics (PC1 vs PC3)
[~, score_pca] = pca(N.Rates(500:3500, :));
fig3_data.pca_pc1 = score_pca(:, 1);
fig3_data.pca_pc3 = score_pca(:, 3);

%% 3. Figure 4 Processed Arrays & Traces
fprintf('\nProcessing Figure 4 Arrays & Continuous Simulation Traces...\n');
fig4_data = struct();

% Reload baseline network for pristine state
load(fullfile(resultsDir, 'baseline_network.mat'), 'N');
desc = load(fullfile(sourceDir, '01_SpinalGeometryFiles', 'matDescending.mat'));

is_lpgi_target = inROI(desc.LPGIVglutL, N.Position(:,1), N.Position(:,3)) | ...
                 inROI(desc.LPGIVglutR, N.Position(:,1), N.Position(:,3));
is_raphe_target = inROI(desc.RapheObsL, N.Position(:,1), N.Position(:,3)) | ...
                  inROI(desc.RapheObsR, N.Position(:,1), N.Position(:,3));

target_types = {'dI6', 'V0d', 'V2b', 'V1', 'V2a-1', 'V2a-2', 'V0v', 'V3', 'MN'};
target_labels = {'dI6', 'V0d', 'V2b', 'V1', 'V2a_{Vsx2+}', 'V2a_{Vsx2-}', 'V0v', 'V3', 'MN'};
n_tg = length(target_types);
lpgi_pct = zeros(n_tg, 1);
raphe_pct = zeros(n_tg, 1);
for i = 1:n_tg
    c_mask = (N.Types == target_types{i});
    n_c = sum(c_mask);
    if n_c > 0
        lpgi_pct(i) = sum(is_lpgi_target & c_mask) / n_c * 100;
        raphe_pct(i) = sum(is_raphe_target & c_mask) / n_c * 100;
    end
end

fig4_data.target_masks.is_lpgi_target = is_lpgi_target;
fig4_data.target_masks.is_raphe_target = is_raphe_target;
fig4_data.target_masks.target_types = target_types;
fig4_data.target_masks.target_labels = target_labels;
fig4_data.target_masks.lpgi_pct = lpgi_pct;
fig4_data.target_masks.raphe_pct = raphe_pct;

% Input & Gain Modulation Profiles (12,000 ms)
t_total = 12000;
t_vec = 1:t_total;
drive_profile = zeros(1, t_total);
gain_profile = zeros(1, t_total);

drive_profile(1:4000) = 15.0;
gain_profile(1:4000) = 0.7;

ramp1_idx = 4001:5000;
drive_profile(ramp1_idx) = linspace(15.0, 22.0, length(ramp1_idx));
gain_profile(ramp1_idx) = linspace(0.7, 1.0, length(ramp1_idx));

drive_profile(5001:8000) = 22.0;
gain_profile(5001:8000) = 1.0;

ramp2_idx = 8001:9000;
drive_profile(ramp2_idx) = linspace(22.0, 30.0, length(ramp2_idx));
gain_profile(ramp2_idx) = linspace(1.0, 1.8, length(ramp2_idx));

drive_profile(9001:12000) = 30.0;
gain_profile(9001:12000) = 1.8;

fig4_data.input_gain_profiles.t_vec_ms = t_vec;
fig4_data.input_gain_profiles.drive_profile_pA = drive_profile;
fig4_data.input_gain_profiles.gain_profile = gain_profile;

% Compound Hyperbolic Tangent Curves
gains_4a = [0.5, 1.0, 2.0];
fig4_data.activation_curves = zeros(3, 500);
for g_idx = 1:3
    g = gains_4a(g_idx);
    rates_g = zeros(size(V_range));
    neg = (V_range - threshold) <= 0;
    pos = (V_range - threshold) > 0;
    rates_g(neg) = threshold .* tanh(g .* (V_range(neg) - threshold) ./ threshold);
    rates_g(pos) = f_max .* tanh(g .* (V_range(pos) - threshold) ./ f_max);
    rates_g = rates_g + threshold;
    rates_g(rates_g < 0) = 0;
    fig4_data.activation_curves(g_idx, :) = rates_g;
end

% Execute Continuous 12,000 ms Simulation
I_input = zeros(N_neurons, t_total);
I_input(is_lpgi_target, :) = repmat(drive_profile, [sum(is_lpgi_target), 1]);
I_input(~is_lpgi_target, :) = 10.0;

[~, IxT] = ismember(N.Types, N.Parameters.Types);
base_gains = reshape(N.Parameters.Gains(IxT), [N_neurons, 1]);
gain_input = repmat(base_gains, [1, t_total]);
for t = 1:t_total
    gain_input(is_raphe_target, t) = base_gains(is_raphe_target) * gain_profile(t);
end

fprintf('Simulating continuous 12,000 ms protocol (seed 42)...\n');
N_sim = copy(N);
h_dummy = figure('Visible', 'off');
N_sim.Simulate(t_total, 'I_e', I_input, 'gain', gain_input, 'seed', 42);
if isvalid(h_dummy), close(h_dummy); end

% Extract Modulated Effective Projectomes
lat = N.Latera;
W_raw = full(N.ConnMat);
W_ipsi_base = W_raw;
W_ipsi_base(lat < 0, lat > 0) = 0;
W_ipsi_base(lat > 0, lat < 0) = 0;

W_contra_base = W_raw;
W_contra_base(lat > 0, lat > 0) = 0;
W_contra_base(lat < 0, lat < 0) = 0;

edges = -10000:100:10000;
edges_c = edges(1:end-1) + diff(edges)/2;
fig4_data.effective_projectomes.edges_c = edges_c;

gait_windows = {1500:3800, 5500:7800, 9500:11800};
gait_names = {'Walking', 'Trotting', 'Bounding'};

for g = 1:3
    r_mean = mean(N_sim.Rates(gait_windows{g}, :), 1)';
    r_scale = r_mean / max(eps, mean(r_mean));
    W_eff_ipsi = W_ipsi_base .* repmat(r_scale', [N_neurons, 1]);
    W_eff_contra = W_contra_base .* repmat(r_scale', [N_neurons, 1]);
    
    diff_ipsi = GeneratePlot_local(N, W_eff_ipsi, edges);
    diff_contra = GeneratePlot_local(N, W_eff_contra, edges);
    
    win = gausswin_local(9); win = win / sum(win);
    diff_ipsi = conv(diff_ipsi, win, 'same');
    diff_contra = conv(diff_contra, win, 'same');
    
    g_key = lower(gait_names{g});
    fig4_data.effective_projectomes.(sprintf('%s_ipsi', g_key)) = diff_ipsi;
    fig4_data.effective_projectomes.(sprintf('%s_contra', g_key)) = diff_contra;
end

% Extract Continuous Motor Nerve & Muscle Traces
l2_r_mask = (N.Types == 'MN') & (N.Segment == 'L2') & (N.Latera > 0);
l5_r_mask = (N.Types == 'MN') & (N.Segment == 'L5') & (N.Latera > 0);
l2_l_mask = (N.Types == 'MN') & (N.Segment == 'L2') & (N.Latera < 0);

fig4_data.traces.t_vec_s = t_vec / 1000;
fig4_data.traces.nerve_rL2 = mean(N_sim.Rates(:, l2_r_mask), 2);
fig4_data.traces.nerve_rL5 = mean(N_sim.Rates(:, l5_r_mask), 2);
fig4_data.traces.nerve_lL2 = mean(N_sim.Rates(:, l2_l_mask), 2);

% Extract Right Synthetic Muscle Envelopes
rng(42);
fig4_data.traces.muscle_emg = struct();
for m = 1:length(muscles_plot)
    m_name = muscles_plot{m};
    m_field = matlab.lang.makeValidName(m_name);
    ix_m = (N.MnID == m_name) & (N.Latera > 0);
    if any(ix_m)
        prob = sum(N_sim.Rates(:, ix_m), 2);
        sig = randn(size(prob)) * noiselevel .* binornd(1, normcdf(normalize(prob, 'zscore')));
        sig = sig .* prob + (randn(size(prob)) * noiselevel);
        env = movmean(abs(sig), 20);
        fig4_data.traces.muscle_emg.(m_field) = env;
    end
end

% Binned Spatial Raster (downsampled to 100 ms bins for compactness)
y_all = N.Position(:, 2);
[y_sorted_all, sort_all] = sort(y_all, 'ascend');
rates_all_sorted = N_sim.Rates(:, sort_all)';
t_bins_s = 0.05:0.1:11.95;
binned_raster = zeros(length(y_bins)-1, length(t_bins_s));
for tb = 1:length(t_bins_s)
    idx_t = round((t_bins_s(tb)-0.05)*1000 + 1) : round((t_bins_s(tb)+0.05)*1000);
    idx_t = idx_t(idx_t >= 1 & idx_t <= t_total);
    r_sub = mean(rates_all_sorted(:, idx_t), 2);
    for b = 1:(length(y_bins)-1)
        in_bin = (y_sorted_all >= y_bins(b)) & (y_sorted_all < y_bins(b+1));
        if any(in_bin)
            binned_raster(b, tb) = mean(r_sub(in_bin));
        end
    end
end
fig4_data.spatial_raster_y_bins = y_bins;
fig4_data.spatial_raster_t_s = t_bins_s;
fig4_data.spatial_raster_binned = binned_raster;

% Load Figure 4 Central Metrics
fig4_json = jsondecode(fileread(fullfile(resultsDir, 'figure4_metrics.json')));
fig4_data.metrics = fig4_json;

%% 4. Figure 5 Processed Arrays & Traces
fprintf('\nProcessing Figure 5 Arrays & Perturbation Simulation Traces...\n');
fig5_data = struct();

v1_mask = (N.Types == 'V1');
v0_mask = (N.Types == 'V0d') | (N.Types == 'V0v');
fig5_data.target_masks.v1_mask = v1_mask;
fig5_data.target_masks.v0_mask = v0_mask;

% Projectome Profiles
L = round(range(N.Position(:, 2)), -2);
edges_5 = -L:250:L;
x_c_5 = edges_5(1:end-1) + diff(edges_5)/2;
fig5_data.projectomes.edges_c = x_c_5;

W_ipsi = full(N.ConnMat);
W_ipsi(lat < 0, lat > 0) = 0;
W_ipsi(lat > 0, lat < 0) = 0;
W_v1_abl = W_ipsi;
W_v1_abl(:, v1_mask) = 0;
W_v1_abl(v1_mask, :) = 0;

fig5_data.projectomes.diff_base_ipsi = GeneratePlot_local(N, W_ipsi, edges_5);
fig5_data.projectomes.diff_v1_ipsi = GeneratePlot_local(N, W_v1_abl, edges_5);

W_contra = full(N.ConnMat);
W_contra(lat > 0, lat > 0) = 0;
W_contra(lat < 0, lat < 0) = 0;
W_v0_abl = W_contra;
W_v0_abl(:, v0_mask) = 0;
W_v0_abl(v0_mask, :) = 0;

fig5_data.projectomes.diff_base_contra = GeneratePlot_local(N, W_contra, edges_5);
fig5_data.projectomes.diff_v0_contra = GeneratePlot_local(N, W_v0_abl, edges_5);

% Simulate Perturbations (8,000 ms each)
t_sim_5 = 8000;
t_vec_5 = 1:t_sim_5;
fig5_data.traces.t_vec_s = t_vec_5 / 1000;

% V1 Silencing
fprintf('  Simulating V1 Silencing (seed 101)...\n');
N_v1_sil = copy(N);
I_v1_sil = ones(N_neurons, t_sim_5) * 30.0;
I_v1_sil(v1_mask, 2501:5500) = -10.0;
h_dummy = figure('Visible', 'off');
N_v1_sil.Simulate(t_sim_5, 'I_e', I_v1_sil, 'seed', 101);
if isvalid(h_dummy), close(h_dummy); end
fig5_data.traces.v1_sil_rL2 = mean(N_v1_sil.Rates(:, l2_r_mask), 2);
fig5_data.traces.v1_sil_rL5 = mean(N_v1_sil.Rates(:, l5_r_mask), 2);
fig5_data.traces.v1_sil_lL2 = mean(N_v1_sil.Rates(:, l2_l_mask), 2);

% V1 Ablation
fprintf('  Simulating V1 Ablation (seed 102)...\n');
N_v1_abl = copy(N);
N_v1_abl.ConnMat(:, v1_mask) = 0;
N_v1_abl.ConnMat(v1_mask, :) = 0;
I_base = ones(N_neurons, t_sim_5) * 30.0;
h_dummy = figure('Visible', 'off');
N_v1_abl.Simulate(t_sim_5, 'I_e', I_base, 'seed', 102);
if isvalid(h_dummy), close(h_dummy); end
fig5_data.traces.v1_abl_rL2 = mean(N_v1_abl.Rates(:, l2_r_mask), 2);
fig5_data.traces.v1_abl_rL5 = mean(N_v1_abl.Rates(:, l5_r_mask), 2);
fig5_data.traces.v1_abl_lL2 = mean(N_v1_abl.Rates(:, l2_l_mask), 2);

% Baseline Control Simulation (8,000 ms, seed 42)
fprintf('  Simulating Baseline Control (seed 42)...\n');
N_base = copy(N);
h_dummy = figure('Visible', 'off');
N_base.Simulate(t_sim_5, 'I_e', I_base, 'seed', 42);
if isvalid(h_dummy), close(h_dummy); end
fig5_data.traces.control_rL2 = mean(N_base.Rates(:, l2_r_mask), 2);
fig5_data.traces.control_rL5 = mean(N_base.Rates(:, l5_r_mask), 2);
fig5_data.traces.control_lL2 = mean(N_base.Rates(:, l2_l_mask), 2);

% V0 Silencing
fprintf('  Simulating V0 Silencing (seed 201)...\n');
N_v0_sil = copy(N);
I_v0_sil = ones(N_neurons, t_sim_5) * 30.0;
I_v0_sil(v0_mask, 2501:5500) = -10.0;
h_dummy = figure('Visible', 'off');
N_v0_sil.Simulate(t_sim_5, 'I_e', I_v0_sil, 'seed', 201);
if isvalid(h_dummy), close(h_dummy); end
fig5_data.traces.v0_sil_rL2 = mean(N_v0_sil.Rates(:, l2_r_mask), 2);
fig5_data.traces.v0_sil_rL5 = mean(N_v0_sil.Rates(:, l5_r_mask), 2);
fig5_data.traces.v0_sil_lL2 = mean(N_v0_sil.Rates(:, l2_l_mask), 2);

% V0 Ablation
fprintf('  Simulating V0 Ablation (seed 202)...\n');
N_v0_abl = copy(N);
N_v0_abl.ConnMat(:, v0_mask) = 0;
N_v0_abl.ConnMat(v0_mask, :) = 0;
h_dummy = figure('Visible', 'off');
N_v0_abl.Simulate(t_sim_5, 'I_e', I_base, 'seed', 202);
if isvalid(h_dummy), close(h_dummy); end
fig5_data.traces.v0_abl_rL2 = mean(N_v0_abl.Rates(:, l2_r_mask), 2);
fig5_data.traces.v0_abl_rL5 = mean(N_v0_abl.Rates(:, l5_r_mask), 2);
fig5_data.traces.v0_abl_lL2 = mean(N_v0_abl.Rates(:, l2_l_mask), 2);

% Load Figure 5 Central Metrics
fig5_json = jsondecode(fileread(fullfile(resultsDir, 'figure5_metrics.json')));
fig5_data.metrics = fig5_json;

%% 5. Save Compact validation_bundle.mat
outFile = fullfile(resultsDir, 'validation_bundle.mat');
fprintf('\nSaving compact validation bundle to: %s ...\n', outFile);

save(outFile, 'neuron_metadata', 'fig3_data', 'fig4_data', 'fig5_data', '-v7');

f_info = dir(outFile);
fprintf('Validation bundle successfully created! File size: %.2f MB\n', f_info.bytes / (1024*1024));

t_elapsed = toc(t_start);
fprintf('Total export time: %.2f seconds.\n', t_elapsed);

diary off;
exit(0);

%% Local Helper Functions
function difference = GeneratePlot_local(N, ConnMat, edges)
    Ex = (N.Transmit > 0);
    In = (N.Transmit < 0);
    Dist = bsxfun(@minus, N.Position(:, 2), N.Position(:, 2)');
    ProjEx = ConnMat(:, Ex); 
    ProjIn = ConnMat(:, In);
    DistEx = Dist(:, Ex);
    DistIn = Dist(:, In);
    
    yin = discretize(DistIn(ProjIn ~= 0), edges);
    yex = discretize(DistEx(ProjEx ~= 0), edges);
    
    val_in = ProjIn(ProjIn ~= 0);
    val_ex = ProjEx(ProjEx ~= 0);
    
    num_bins = length(edges) - 1;
    MInZ = zeros(num_bins, 1);
    MExZ = zeros(num_bins, 1);
    CInZ = zeros(num_bins, 1);
    CExZ = zeros(num_bins, 1);
    
    for b = 1:num_bins
        idx_in = (yin == b);
        if any(idx_in)
            CInZ(b) = sum(idx_in);
            MInZ(b) = mean(val_in(idx_in));
        end
        idx_ex = (yex == b);
        if any(idx_ex)
            CExZ(b) = sum(idx_ex);
            MExZ(b) = mean(val_ex(idx_ex));
        end
    end
    
    difference = abs(MExZ .* CExZ) - abs(MInZ .* CInZ);
end

function w = gausswin_local(L)
    alpha = 2.5;
    n = -(L-1)/2 : (L-1)/2;
    w = exp(-0.5 * (alpha * n / ((L-1)/2)).^2)';
end

function mean_angle = circ_mean_local(angles)
    sin_sum = sum(sin(angles));
    cos_sum = sum(cos(angles));
    mean_angle = atan2(sin_sum, cos_sum);
    if mean_angle < 0
        mean_angle = mean_angle + 2*pi;
    end
end
