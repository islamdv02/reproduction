%% run_figure5_reproduction.m
% Faithful scientific reproduction of Figure 5 (Genetic Perturbations of V1 and V0 Interneurons).
%
% Generates modular subpanels in figures/subpanels_fig5/:
%   5A: Transverse spinal cord with V1 neurons (Ablation X vs Modulation arrow) + Projectome
%   5B: Ongoing V1 modulation (silencing window) & ablation traces with burst envelopes & shading
%   5C: V1 quantification: Frequency (Hz), Amplitude (a.u), and Polar phase (iL2-cL2 & iL2-iL5)
%   5D: Transverse spinal cord with V0 neurons (Ablation X vs Modulation arrow) + Projectome
%   5E: Ongoing V0 modulation (synchronous hopping during silencing) & ablation traces
%   5F: V0 quantification: Frequency speedup, Amplitude, and Polar phase switch (alternation -> synchrony)
%
% Preserves upstream source code unchanged.

clear;
clc;
close all;

t_start = tic;
scriptDir = fileparts(mfilename('fullpath'));
rootDir = fullfile(scriptDir, '..');
sourceDir = fullfile(rootDir, 'source');
resultsDir = fullfile(rootDir, 'results');
subpanelDir = fullfile(rootDir, 'figures', 'subpanels_fig5');
logsDir = fullfile(rootDir, 'logs');

if ~exist(subpanelDir, 'dir'), mkdir(subpanelDir); end
if ~exist(resultsDir, 'dir'), mkdir(resultsDir); end
if ~exist(logsDir, 'dir'), mkdir(logsDir); end

logFile = fullfile(logsDir, 'step6_figure5_reproduction.log');
diary(logFile);
diary on;

fprintf('=================================================================\n');
fprintf('STAGE 6: Figure 5 Reproduction (Komi et al., 2026)\n');
fprintf('Timestamp: %s\n', datestr(now));
fprintf('MATLAB Version: %s\n', version);
fprintf('=================================================================\n');

cd(sourceDir);
addpath(fullfile(rootDir, 'scripts', 'compat'));
addpath(genpath(sourceDir));

%% 1. Load Baseline Network
baselinePath = fullfile(resultsDir, 'baseline_network.mat');
fprintf('Loading baseline network from: %s ...\n', baselinePath);
load(baselinePath, 'N');
N_neurons = size(N.ConnMat, 1);
fprintf('Loaded network: N = %d neurons.\n', N_neurons);

v1_mask = (N.Types == 'V1');
v0_mask = (N.Types == 'V0d') | (N.Types == 'V0v');
l2_l_mask = (N.Types == 'MN') & (N.Segment == 'L2') & (N.Latera < 0);
l2_r_mask = (N.Types == 'MN') & (N.Segment == 'L2') & (N.Latera > 0);
l5_r_mask = (N.Types == 'MN') & (N.Segment == 'L5') & (N.Latera > 0);

%% 2. Run or Load Simulations
simCacheFile = fullfile(resultsDir, 'figure5_simulations.mat');
t_sim = 8000;
t_vec = 1:t_sim;

win_ctrl = 500:2400;
win_v1_sil = 3000:5400;
win_v1_abl = 2000:7500;
win_v0_sil = 3000:5400;
win_v0_abl = 2000:7500;

if exist(simCacheFile, 'file')
    fprintf('\nLoading cached Figure 5 simulations from: %s ...\n', simCacheFile);
    load(simCacheFile);
else
    fprintf('\nRunning Figure 5 Simulations (Baseline, V1 Silencing, V1 Ablation, V0 Silencing, V0 Ablation)...\n');
    
    % 1. Baseline Control Simulation
    fprintf('  1/5 Simulating Baseline Control (8,000 ms, 30 pA tonic)...\n');
    N_base = copy(N);
    I_base = ones(N_neurons, t_sim) * 30.0;
    h_dummy = figure('Visible', 'off');
    tic_sim = tic;
    N_base.Simulate(t_sim, 'I_e', I_base, 'seed', 42);
    if isvalid(h_dummy), close(h_dummy); end
    fprintf('      Baseline finished in %.2f s.\n', toc(tic_sim));
    
    r_r_l2_base = mean(N_base.Rates(:, l2_r_mask), 2);
    r_l_l2_base = mean(N_base.Rates(:, l2_l_mask), 2);
    r_r_l5_base = mean(N_base.Rates(:, l5_r_mask), 2);
    
    % 2. V1 Silencing Simulation (Hyperpolarize V1 to -10 pA between 2501 and 5500 ms)
    fprintf('  2/5 Simulating V1 Silencing (8,000 ms)...\n');
    N_v1_sil = copy(N);
    I_v1_sil = ones(N_neurons, t_sim) * 30.0;
    I_v1_sil(v1_mask, 2501:5500) = -10.0;
    h_dummy = figure('Visible', 'off');
    tic_sim = tic;
    N_v1_sil.Simulate(t_sim, 'I_e', I_v1_sil, 'seed', 42);
    if isvalid(h_dummy), close(h_dummy); end
    fprintf('      V1 Silencing finished in %.2f s.\n', toc(tic_sim));
    
    r_r_l2_v1_sil = mean(N_v1_sil.Rates(:, l2_r_mask), 2);
    r_l_l2_v1_sil = mean(N_v1_sil.Rates(:, l2_l_mask), 2);
    r_r_l5_v1_sil = mean(N_v1_sil.Rates(:, l5_r_mask), 2);
    
    % 3. V1 Ablation Simulation (Full 8,000 ms with V1 weights removed)
    fprintf('  3/5 Simulating V1 Ablation (8,000 ms)...\n');
    N_v1_abl = copy(N);
    N_v1_abl.ConnMat(:, v1_mask) = 0;
    N_v1_abl.ConnMat(v1_mask, :) = 0;
    h_dummy = figure('Visible', 'off');
    tic_sim = tic;
    N_v1_abl.Simulate(t_sim, 'I_e', I_base, 'seed', 42);
    if isvalid(h_dummy), close(h_dummy); end
    fprintf('      V1 Ablation finished in %.2f s.\n', toc(tic_sim));
    
    r_r_l2_v1_abl = mean(N_v1_abl.Rates(:, l2_r_mask), 2);
    r_l_l2_v1_abl = mean(N_v1_abl.Rates(:, l2_l_mask), 2);
    r_r_l5_v1_abl = mean(N_v1_abl.Rates(:, l5_r_mask), 2);
    
    % 4. V0 Silencing Simulation (Hyperpolarize V0 to -10 pA between 2501 and 5500 ms)
    fprintf('  4/5 Simulating V0 Silencing (8,000 ms)...\n');
    N_v0_sil = copy(N);
    I_v0_sil = ones(N_neurons, t_sim) * 30.0;
    I_v0_sil(v0_mask, 2501:5500) = -10.0;
    h_dummy = figure('Visible', 'off');
    tic_sim = tic;
    N_v0_sil.Simulate(t_sim, 'I_e', I_v0_sil, 'seed', 42);
    if isvalid(h_dummy), close(h_dummy); end
    fprintf('      V0 Silencing finished in %.2f s.\n', toc(tic_sim));
    
    r_r_l2_v0_sil = mean(N_v0_sil.Rates(:, l2_r_mask), 2);
    r_l_l2_v0_sil = mean(N_v0_sil.Rates(:, l2_l_mask), 2);
    r_r_l5_v0_sil = mean(N_v0_sil.Rates(:, l5_r_mask), 2);
    
    % 5. V0 Ablation Simulation (Full 8,000 ms with V0 weights removed)
    fprintf('  5/5 Simulating V0 Ablation (8,000 ms)...\n');
    N_v0_abl = copy(N);
    N_v0_abl.ConnMat(:, v0_mask) = 0;
    N_v0_abl.ConnMat(v0_mask, :) = 0;
    h_dummy = figure('Visible', 'off');
    tic_sim = tic;
    N_v0_abl.Simulate(t_sim, 'I_e', I_base, 'seed', 42);
    if isvalid(h_dummy), close(h_dummy); end
    fprintf('      V0 Ablation finished in %.2f s.\n', toc(tic_sim));
    
    r_r_l2_v0_abl = mean(N_v0_abl.Rates(:, l2_r_mask), 2);
    r_l_l2_v0_abl = mean(N_v0_abl.Rates(:, l2_l_mask), 2);
    r_r_l5_v0_abl = mean(N_v0_abl.Rates(:, l5_r_mask), 2);
    
    save(simCacheFile, 'r_r_l2_base', 'r_l_l2_base', 'r_r_l5_base', ...
        'r_r_l2_v1_sil', 'r_l_l2_v1_sil', 'r_r_l5_v1_sil', ...
        'r_r_l2_v1_abl', 'r_l_l2_v1_abl', 'r_r_l5_v1_abl', ...
        'r_r_l2_v0_sil', 'r_l_l2_v0_sil', 'r_r_l5_v0_sil', ...
        'r_r_l2_v0_abl', 'r_l_l2_v0_abl', 'r_r_l5_v0_abl', '-v7.3');
    fprintf('Saved Figure 5 simulations to: %s\n', simCacheFile);
end

%% 3. Quantitative Dynamic Measurements
fprintf('\nQuantifying Dynamics Across Conditions...\n');

% V1 Windows
r_r_l2_ctrl_w = r_r_l2_base(win_ctrl);
r_l_l2_ctrl_w = r_l_l2_base(win_ctrl);
r_r_l5_ctrl_w = r_r_l5_base(win_ctrl);

r_r_l2_v1sil_w = r_r_l2_v1_sil(win_v1_sil);
r_l_l2_v1sil_w = r_l_l2_v1_sil(win_v1_sil);
r_r_l5_v1sil_w = r_r_l5_v1_sil(win_v1_sil);

r_r_l2_v1abl_w = r_r_l2_v1_abl(win_v1_abl);
r_l_l2_v1abl_w = r_l_l2_v1_abl(win_v1_abl);
r_r_l5_v1abl_w = r_r_l5_v1_abl(win_v1_abl);

[freq_base, lr_phase_base, l2l5_phase_base, cyc_lr_base, cyc_l2l5_base, pks_amp_base] = measure_dynamics_cycles(r_l_l2_ctrl_w, r_r_l2_ctrl_w, r_r_l5_ctrl_w);
[freq_v1_sil, lr_phase_v1_sil, l2l5_phase_v1_sil, cyc_lr_v1_sil, cyc_l2l5_v1_sil, pks_amp_v1_sil] = measure_dynamics_cycles(r_l_l2_v1sil_w, r_r_l2_v1sil_w, r_r_l5_v1sil_w);
[freq_v1_abl, lr_phase_v1_abl, l2l5_phase_v1_abl, cyc_lr_v1_abl, cyc_l2l5_v1_abl, pks_amp_v1_abl] = measure_dynamics_cycles(r_l_l2_v1abl_w, r_r_l2_v1abl_w, r_r_l5_v1abl_w);

amp_base = mean(pks_amp_base);
amp_v1_sil = mean(pks_amp_v1_sil);
amp_v1_abl = mean(pks_amp_v1_abl);

fprintf('  V1 Results:\n');
fprintf('    Freq: Ctrl = %.2f Hz, Silenced = %.2f Hz, Ablated = %.2f Hz\n', freq_base, freq_v1_sil, freq_v1_abl);
fprintf('    Amp:  Ctrl = %.1f, Silenced = %.1f, Ablated = %.1f\n', amp_base, amp_v1_sil, amp_v1_abl);
fprintf('    LR Phase: Ctrl = %.1f°, Sil = %.1f°, Abl = %.1f°\n', rad2deg(lr_phase_base), rad2deg(lr_phase_v1_sil), rad2deg(lr_phase_v1_abl));

% V0 Windows
r_r_l2_v0sil_w = r_r_l2_v0_sil(win_v0_sil);
r_l_l2_v0sil_w = r_l_l2_v0_sil(win_v0_sil);
r_r_l5_v0sil_w = r_r_l5_v0_sil(win_v0_sil);

r_r_l2_v0abl_w = r_r_l2_v0_abl(win_v0_abl);
r_l_l2_v0abl_w = r_l_l2_v0_abl(win_v0_abl);
r_r_l5_v0abl_w = r_r_l5_v0_abl(win_v0_abl);

[freq_v0_sil, lr_phase_v0_sil, l2l5_phase_v0_sil, cyc_lr_v0_sil, cyc_l2l5_v0_sil, pks_amp_v0_sil] = measure_dynamics_cycles(r_l_l2_v0sil_w, r_r_l2_v0sil_w, r_r_l5_v0sil_w);
[freq_v0_abl, lr_phase_v0_abl, l2l5_phase_v0_abl, cyc_lr_v0_abl, cyc_l2l5_v0_abl, pks_amp_v0_abl] = measure_dynamics_cycles(r_l_l2_v0abl_w, r_r_l2_v0abl_w, r_r_l5_v0abl_w);

amp_v0_sil = mean(pks_amp_v0_sil);
amp_v0_abl = mean(pks_amp_v0_abl);

fprintf('  V0 Results:\n');
fprintf('    Freq: Ctrl = %.2f Hz, Silenced = %.2f Hz, Ablated = %.2f Hz\n', freq_base, freq_v0_sil, freq_v0_abl);
fprintf('    Amp:  Ctrl = %.1f, Silenced = %.1f, Ablated = %.1f\n', amp_base, amp_v0_sil, amp_v0_abl);
fprintf('    LR Phase: Ctrl = %.1f°, Sil = %.1f°, Abl = %.1f°\n', rad2deg(lr_phase_base), rad2deg(lr_phase_v0_sil), rad2deg(lr_phase_v0_abl));

%% 4. Geometry and Projectome Precomputations for 5A & 5D
geo = load("01_SpinalGeometryFiles\matGeometry.mat");
RCTDCoord = geo.RCTDCoord;
mid_x = mean(RCTDCoord.x);

lat = N.Latera;
W_ipsi = full(N.ConnMat);
W_ipsi(lat < 0, lat > 0) = 0;
W_ipsi(lat > 0, lat < 0) = 0;

W_v1_abl = W_ipsi;
W_v1_abl(:, v1_mask) = 0;
W_v1_abl(v1_mask, :) = 0;

L_rc = round(max(N.Position(:, 2)) - min(N.Position(:, 2)), -2);
edges = -L_rc:250:L_rc;
x_c = edges(1:end-1) + diff(edges)/2;

diff_base = GeneratePlot_local(N, W_ipsi, edges);
diff_v1 = GeneratePlot_local(N, W_v1_abl, edges);

W_contra = full(N.ConnMat);
W_contra(lat > 0, lat > 0) = 0;
W_contra(lat < 0, lat < 0) = 0;

W_v0_abl = W_contra;
W_v0_abl(:, v0_mask) = 0;
W_v0_abl(v0_mask, :) = 0;

diff_contra_base = GeneratePlot_local(N, W_contra, edges);
diff_contra_v0 = GeneratePlot_local(N, W_v0_abl, edges);

%% 5. Generate Figure 5A (V1 Anatomy & Projectome)
fprintf('\nGenerating Figure 5A (V1 Anatomy & Projectome)...\n');
fig5a = figure('Color', 'white', 'Position', [100 100 1100 680], 'Visible', 'off');

% Cord outline + V1 neurons
ax5a_cord = axes('Position', [0.10 0.40 0.80 0.50]);
hold(ax5a_cord, 'on');
axis(ax5a_cord, 'equal');
axis(ax5a_cord, 'off');

% Grey matter & White matter points and outlines
gm_mask = strcmpi(geo.matLayers.lowres, 'grey');
wm_mask = strcmpi(geo.matLayers.lowres, 'white');
left_gm = gm_mask & (RCTDCoord.x <= mid_x);
right_gm = gm_mask & (RCTDCoord.x >= mid_x);

pts_wm = [RCTDCoord.x, RCTDCoord.y];
k_wm = convhull(pts_wm(:,1), pts_wm(:,2));

pts_gm_l = [RCTDCoord.x(left_gm), RCTDCoord.y(left_gm)];
k_gm_l = convhull(pts_gm_l(:,1), pts_gm_l(:,2));

pts_gm_r = [RCTDCoord.x(right_gm), RCTDCoord.y(right_gm)];
k_gm_r = convhull(pts_gm_r(:,1), pts_gm_r(:,2));

% 3D cylinder perspective back rim
dx_3d = 95; dy_3d = 45;
plot(ax5a_cord, pts_wm(k_wm, 1) + dx_3d, pts_wm(k_wm, 2) + dy_3d, 'Color', [0.82 0.82 0.82], 'LineWidth', 1.2);
[~, top_idx] = max(pts_wm(k_wm, 2));
[~, bot_idx] = min(pts_wm(k_wm, 2));
plot(ax5a_cord, [pts_wm(k_wm(top_idx), 1), pts_wm(k_wm(top_idx), 1) + dx_3d], ...
    [pts_wm(k_wm(top_idx), 2), pts_wm(k_wm(top_idx), 2) + dy_3d], 'Color', [0.82 0.82 0.82], 'LineWidth', 1.2);
plot(ax5a_cord, [pts_wm(k_wm(bot_idx), 1), pts_wm(k_wm(bot_idx), 1) + dx_3d], ...
    [pts_wm(k_wm(bot_idx), 2), pts_wm(k_wm(bot_idx), 2) + dy_3d], 'Color', [0.82 0.82 0.82], 'LineWidth', 1.2);

% Front cord slice
scatter(ax5a_cord, RCTDCoord.x(wm_mask), RCTDCoord.y(wm_mask), 5, [0.90 0.90 0.90], 'filled', 'MarkerFaceAlpha', 0.4);
scatter(ax5a_cord, RCTDCoord.x(gm_mask), RCTDCoord.y(gm_mask), 7, [0.80 0.80 0.80], 'filled', 'MarkerFaceAlpha', 0.5);

plot(ax5a_cord, pts_wm(k_wm, 1), pts_wm(k_wm, 2), 'Color', [0.35 0.35 0.35], 'LineWidth', 1.4);
plot(ax5a_cord, pts_gm_l(k_gm_l, 1), pts_gm_l(k_gm_l, 2), 'Color', [0.55 0.55 0.55], 'LineWidth', 1.1);
plot(ax5a_cord, pts_gm_r(k_gm_r, 1), pts_gm_r(k_gm_r, 2), 'Color', [0.55 0.55 0.55], 'LineWidth', 1.1);

% Vertical dashed midline
plot(ax5a_cord, [mid_x mid_x], [min(RCTDCoord.y)-20, max(RCTDCoord.y)+20], '--k', 'Color', [0.4 0.4 0.4], 'LineWidth', 1.2);

% V1 neurons: Left and Right hemicord
rctd_types = string(geo.RCTDCellTypes.type);
v1_cols = ismember(rctd_types, ["Inhib-23", "Inhib-24", "Inhib-26"]);
w_v1 = sum(geo.weights(:, v1_cols), 2);
s_v1 = gm_mask & (w_v1 > 0.08);
v1_x = RCTDCoord.x(s_v1);
v1_y = RCTDCoord.y(s_v1);

v1_purple = [0.55 0.22 0.65];
scatter(ax5a_cord, v1_x, v1_y, 18, v1_purple, 'filled', 'MarkerFaceAlpha', 0.85);

% Left hemicord: Red Ablation Cross 'X'
cross_x = mid_x - 140; cross_y = mean(v1_y);
plot(ax5a_cord, cross_x + [-45 45], cross_y + [-45 45], 'Color', [0.85 0.15 0.15], 'LineWidth', 4.0);
plot(ax5a_cord, cross_x + [-45 45], cross_y + [45 -45], 'Color', [0.85 0.15 0.15], 'LineWidth', 4.0);

% Right hemicord: Black Modulation Arrow pointing into V1 cluster
arrow_target_x = mid_x + 120; arrow_target_y = mean(v1_y);
plot(ax5a_cord, [arrow_target_x + 165, arrow_target_x + 18], [arrow_target_y + 75, arrow_target_y + 10], 'k-', 'LineWidth', 2.6);
th_arr = atan2(-65, -147);
h_len = 24; h_ang = 0.35;
p1 = [arrow_target_x, arrow_target_y];
p2 = p1 - [h_len*cos(th_arr - h_ang), h_len*sin(th_arr - h_ang)];
p3 = p1 - [h_len*cos(th_arr + h_ang), h_len*sin(th_arr + h_ang)];
fill(ax5a_cord, [p1(1) p2(1) p3(1)], [p1(2) p2(2) p3(2)], 'k', 'EdgeColor', 'none');

% Top Labels (Above cord, matching publication)
y_lbl_top = max(RCTDCoord.y) + 40;
text(ax5a_cord, mid_x - 300, y_lbl_top, '{\bf V}{\color[rgb]{0.55,0.22,0.65}\bf 1}', 'FontSize', 22);
text(ax5a_cord, mid_x - 140, y_lbl_top, 'Ablation', 'FontWeight', 'bold', 'FontSize', 15, 'HorizontalAlignment', 'center');
text(ax5a_cord, mid_x + 160, y_lbl_top, 'Modulation', 'FontWeight', 'bold', 'FontSize', 15, 'HorizontalAlignment', 'center');

% Below cord: Projectome Rostrocaudal profile
ax5a_proj = axes('Position', [0.12 0.08 0.76 0.28]);
hold(ax5a_proj, 'on');

% Shaded intact outline in background
fill(ax5a_proj, [x_c, fliplr(x_c)], [diff_base', zeros(1, length(diff_base))], [0.90 0.90 0.90], ...
    'FaceAlpha', 0.45, 'EdgeColor', [0.75 0.75 0.75], 'LineWidth', 1.0);

% Shaded missing rostral inhibition lobe in purple
rostral_lobe_mask = (x_c < 0) & (diff_base' < 0);
fill(ax5a_proj, [x_c(rostral_lobe_mask), fliplr(x_c(rostral_lobe_mask))], ...
    [diff_base(rostral_lobe_mask)', diff_v1(rostral_lobe_mask)'], v1_purple, ...
    'FaceAlpha', 0.50, 'EdgeColor', 'none');

plot(ax5a_proj, x_c, diff_base, 'Color', [0.4 0.4 0.4], 'LineWidth', 1.8);
plot(ax5a_proj, x_c, diff_v1, '--', 'Color', v1_purple, 'LineWidth', 2.2);

yline(ax5a_proj, 0, 'Color', [0.6 0.6 0.6], 'LineWidth', 1.0);
xline(ax5a_proj, 0, ':', 'Color', [0.6 0.6 0.6], 'LineWidth', 1.0);

% Rostral <---> Caudal axis annotation
plot(ax5a_proj, [-500 -1600], [-820 -820], 'k-', 'LineWidth', 1.6);
plot(ax5a_proj, [-2800 -3800], [-820 -820], 'k-', 'LineWidth', 1.6);
fill(ax5a_proj, [-4000 -3780 -3780], [-820 -770 -870], 'k', 'EdgeColor', 'none');
plot(ax5a_proj, [500 1600], [-820 -820], 'k-', 'LineWidth', 1.6);
plot(ax5a_proj, [2800 3800], [-820 -820], 'k-', 'LineWidth', 1.6);
fill(ax5a_proj, [4000 3780 3780], [-820 -770 -870], 'k', 'EdgeColor', 'none');
text(ax5a_proj, -2200, -820, 'Rostral', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');
text(ax5a_proj, 2200, -820, 'Caudal', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');

xlim(ax5a_proj, [-8000 8000]);
ylim(ax5a_proj, [-900 850]);
axis(ax5a_proj, 'off');

p_5a = fullfile(subpanelDir, 'fig5a_v1_anatomy_projectome.png');
exportgraphics(fig5a, p_5a, 'Resolution', 300);
fprintf('Saved Figure 5A: %s\n', p_5a);

%% 6. Generate Figure 5B (V1 Continuous Modulation & Ablation Traces)
fprintf('\nGenerating Figure 5B (V1 Continuous Modulation & Ablation Traces)...\n');
fig5b = figure('Color', 'white', 'Position', [100 100 1100 720], 'Visible', 'off');

% 5B Top: Modulation
ax5b_mod = axes('Position', [0.12 0.53 0.84 0.41]);
hold(ax5b_mod, 'on');

% Silencing window shading
patch(ax5b_mod, [2.5 5.5 5.5 2.5], [-15 -15 85 85], [0.93 0.88 0.96], 'EdgeColor', 'none', 'FaceAlpha', 0.95);
text(ax5b_mod, 4.0, -8, 'Silencing (Hyperpolarisation)', 'Color', [0.35 0.15 0.45], ...
    'FontWeight', 'bold', 'FontSize', 11, 'HorizontalAlignment', 'center');

% Top label
text(ax5b_mod, 0.05, 80, 'Modulation', 'FontWeight', 'bold', 'FontSize', 14);
plot(ax5b_mod, [1.35 1.65], [80 80], '-k', 'LineWidth', 2.0);
fill(ax5b_mod, [1.75 1.63 1.63], [80 84 76], 'k', 'EdgeColor', 'none');

plot_nerve_panel(ax5b_mod, t_vec, r_r_l2_v1_sil, r_r_l5_v1_sil, r_l_l2_v1_sil, 101);

% 1s scale bar
plot(ax5b_mod, [6.8 7.8], [-12 -12], '-k', 'LineWidth', 3.0);
text(ax5b_mod, 7.3, -5, '1s', 'FontWeight', 'bold', 'FontSize', 11, 'HorizontalAlignment', 'center');

xlim(ax5b_mod, [0 8.0]);
ylim(ax5b_mod, [-16 88]);
axis(ax5b_mod, 'off');

% 5B Bottom: Ablation
ax5b_abl = axes('Position', [0.12 0.06 0.84 0.41]);
hold(ax5b_abl, 'on');

text(ax5b_abl, 0.05, 80, 'Ablation', 'FontWeight', 'bold', 'FontSize', 14);
plot(ax5b_abl, 1.25 + [-0.08 0.08], 80 + [-3.5 3.5], 'Color', [0.85 0.15 0.15], 'LineWidth', 2.5);
plot(ax5b_abl, 1.25 + [-0.08 0.08], 80 + [3.5 -3.5], 'Color', [0.85 0.15 0.15], 'LineWidth', 2.5);

plot_nerve_panel(ax5b_abl, t_vec, r_r_l2_v1_abl, r_r_l5_v1_abl, r_l_l2_v1_abl, 102);

% 1s scale bar
plot(ax5b_abl, [6.8 7.8], [-12 -12], '-k', 'LineWidth', 3.0);
text(ax5b_abl, 7.3, -5, '1s', 'FontWeight', 'bold', 'FontSize', 11, 'HorizontalAlignment', 'center');

xlim(ax5b_abl, [0 8.0]);
ylim(ax5b_abl, [-16 88]);
axis(ax5b_abl, 'off');

p_5b = fullfile(subpanelDir, 'fig5b_v1_continuous_traces.png');
exportgraphics(fig5b, p_5b, 'Resolution', 300);
fprintf('Saved Figure 5B: %s\n', p_5b);

%% 7. Generate Figure 5C (V1 Quantification)
fprintf('\nGenerating Figure 5C (V1 Quantification: Frequency, Amplitude, Polar Phase)...\n');
fig5c = figure('Color', 'white', 'Position', [100 100 1100 450], 'Visible', 'off');

% 1. Frequency Bar Graph
ax5c_f = axes('Position', [0.06 0.18 0.10 0.70]);
hold(ax5c_f, 'on');
b_f = bar(ax5c_f, [1, 2, 3], [freq_base, freq_v1_sil, freq_v1_abl], 0.55);
b_f.FaceColor = 'flat';
b_f.CData(1, :) = [0.35 0.35 0.35];
b_f.CData(2, :) = [0.60 0.40 0.65];
b_f.CData(3, :) = [0.85 0.40 0.40];
set(ax5c_f, 'XTick', [1 2 3], 'XTickLabel', {'Control', 'Silencing', 'Ablation'}, ...
    'XTickLabelRotation', 45, 'FontWeight', 'bold', 'FontSize', 9.5, 'Box', 'off', 'TickDir', 'out');
ylabel(ax5c_f, 'Frequency Hz', 'FontWeight', 'bold', 'FontSize', 10);
ylim(ax5c_f, [0 3.5]); set(ax5c_f, 'YTick', [0.5 1.5 2.5 3.5]);

% 2. Burst Amplitude Bar Graph with Replicates
ax5c_a = axes('Position', [0.22 0.18 0.12 0.70]);
hold(ax5c_a, 'on');
b_a = bar(ax5c_a, [1, 2, 3], [amp_base, amp_v1_sil, amp_v1_abl], 0.55);
b_a.FaceColor = 'flat';
b_a.CData(1, :) = [0.35 0.35 0.35];
b_a.CData(2, :) = [0.60 0.40 0.65];
b_a.CData(3, :) = [0.85 0.40 0.40];

% Scatter real individual cycle peak amplitudes (no randn noise)
n_b = length(pks_amp_base);
if n_b > 1
    x_b = 1 + linspace(-0.07, 0.07, n_b)';
else
    x_b = 1;
end
scatter(ax5c_a, x_b, pks_amp_base, 14, [0.2 0.2 0.2], 'filled', 'MarkerFaceAlpha', 0.6);

n_s = length(pks_amp_v1_sil);
if n_s > 1
    x_s = 2 + linspace(-0.07, 0.07, n_s)';
else
    x_s = 2;
end
scatter(ax5c_a, x_s, pks_amp_v1_sil, 14, [0.5 0.25 0.6], 'filled', 'MarkerFaceAlpha', 0.6);

n_a = length(pks_amp_v1_abl);
if n_a > 1
    x_a = 3 + linspace(-0.07, 0.07, n_a)';
else
    x_a = 3;
end
scatter(ax5c_a, x_a, pks_amp_v1_abl, 14, [0.8 0.3 0.3], 'filled', 'MarkerFaceAlpha', 0.6);

set(ax5c_a, 'XTick', [1 2 3], 'XTickLabel', {'Control', 'Silencing', 'Ablation'}, ...
    'XTickLabelRotation', 45, 'FontWeight', 'bold', 'FontSize', 9.5, 'Box', 'off', 'TickDir', 'out');
ylabel(ax5c_a, 'Amplitude a.u', 'FontWeight', 'bold', 'FontSize', 10);
max_amp_5c = max([max(pks_amp_base), max(pks_amp_v1_sil), max(pks_amp_v1_abl)]);
y_top_5c = max(35, ceil((max_amp_5c * 1.15) / 5) * 5);
ylim(ax5c_a, [0 y_top_5c]);

% 3. Polar Plot: iL2-cL2
ax5c_p1 = axes('Position', [0.42 0.12 0.26 0.78]);
plot_paper_polar(ax5c_p1, 'iL2-cL2', [lr_phase_base, lr_phase_v1_sil, lr_phase_v1_abl], ...
    cyc_lr_base, cyc_lr_v1_sil, cyc_lr_v1_abl, {[0.2 0.2 0.2], [0.60 0.40 0.65], [0.85 0.40 0.40]});

% 4. Polar Plot: iL2-iL5
ax5c_p2 = axes('Position', [0.72 0.12 0.26 0.78]);
plot_paper_polar(ax5c_p2, 'iL2-iL5', [l2l5_phase_base, l2l5_phase_v1_sil, l2l5_phase_v1_abl], ...
    cyc_l2l5_base, cyc_l2l5_v1_sil, cyc_l2l5_v1_abl, {[0.2 0.2 0.2], [0.60 0.40 0.65], [0.85 0.40 0.40]});

p_5c = fullfile(subpanelDir, 'fig5c_v1_quantification.png');
exportgraphics(fig5c, p_5c, 'Resolution', 300);
fprintf('Saved Figure 5C: %s\n', p_5c);

%% 8. Generate Figure 5D (V0 Anatomy & Projectome)
fprintf('\nGenerating Figure 5D (V0 Anatomy & Projectome)...\n');
fig5d = figure('Color', 'white', 'Position', [100 100 1100 680], 'Visible', 'off');

% Cord outline + V0 neurons
ax5d_cord = axes('Position', [0.10 0.40 0.80 0.50]);
hold(ax5d_cord, 'on');
axis(ax5d_cord, 'equal');
axis(ax5d_cord, 'off');

% Grey matter & White matter points and outlines
scatter(ax5d_cord, RCTDCoord.x(wm_mask), RCTDCoord.y(wm_mask), 5, [0.90 0.90 0.90], 'filled', 'MarkerFaceAlpha', 0.4);
scatter(ax5d_cord, RCTDCoord.x(gm_mask), RCTDCoord.y(gm_mask), 7, [0.80 0.80 0.80], 'filled', 'MarkerFaceAlpha', 0.5);

% 3D cylinder perspective back rim
plot(ax5d_cord, pts_wm(k_wm, 1) + dx_3d, pts_wm(k_wm, 2) + dy_3d, 'Color', [0.82 0.82 0.82], 'LineWidth', 1.2);
plot(ax5d_cord, [pts_wm(k_wm(top_idx), 1), pts_wm(k_wm(top_idx), 1) + dx_3d], ...
    [pts_wm(k_wm(top_idx), 2), pts_wm(k_wm(top_idx), 2) + dy_3d], 'Color', [0.82 0.82 0.82], 'LineWidth', 1.2);
plot(ax5d_cord, [pts_wm(k_wm(bot_idx), 1), pts_wm(k_wm(bot_idx), 1) + dx_3d], ...
    [pts_wm(k_wm(bot_idx), 2), pts_wm(k_wm(bot_idx), 2) + dy_3d], 'Color', [0.82 0.82 0.82], 'LineWidth', 1.2);

plot(ax5d_cord, pts_wm(k_wm, 1), pts_wm(k_wm, 2), 'Color', [0.35 0.35 0.35], 'LineWidth', 1.4);
plot(ax5d_cord, pts_gm_l(k_gm_l, 1), pts_gm_l(k_gm_l, 2), 'Color', [0.55 0.55 0.55], 'LineWidth', 1.1);
plot(ax5d_cord, pts_gm_r(k_gm_r, 1), pts_gm_r(k_gm_r, 2), 'Color', [0.55 0.55 0.55], 'LineWidth', 1.1);

plot(ax5d_cord, [mid_x mid_x], [min(RCTDCoord.y)-20, max(RCTDCoord.y)+20], '--k', 'Color', [0.4 0.4 0.4], 'LineWidth', 1.2);

% V0 neurons: Medial/ventral commissural cluster around central canal
s_v0 = gm_mask & (RCTDCoord.x >= mid_x - 140 & RCTDCoord.x <= mid_x + 140 & ...
                  RCTDCoord.y >= min(RCTDCoord.y) + 120 & RCTDCoord.y <= max(RCTDCoord.y) - 100);
v0_x = RCTDCoord.x(s_v0);
v0_y = RCTDCoord.y(s_v0);

v0_teal = [0.10 0.65 0.65];
scatter(ax5d_cord, v0_x, v0_y, 18, v0_teal, 'filled', 'MarkerFaceAlpha', 0.85);

% Left hemicord: Red Ablation Cross 'X'
cross_x_v0 = mid_x - 65; cross_y_v0 = mean(v0_y);
plot(ax5d_cord, cross_x_v0 + [-40 40], cross_y_v0 + [-40 40], 'Color', [0.85 0.15 0.15], 'LineWidth', 4.0);
plot(ax5d_cord, cross_x_v0 + [-40 40], cross_y_v0 + [40 -40], 'Color', [0.85 0.15 0.15], 'LineWidth', 4.0);

% Right hemicord: Black Modulation Arrow pointing into V0 cluster
arrow_target_x_v0 = mid_x + 65; arrow_target_y_v0 = mean(v0_y);
plot(ax5d_cord, [arrow_target_x_v0 + 155, arrow_target_x_v0 + 16], [arrow_target_y_v0 + 50, arrow_target_y_v0 + 8], 'k-', 'LineWidth', 2.6);
th_arr_v0 = atan2(-42, -139);
p1_v0 = [arrow_target_x_v0, arrow_target_y_v0];
p2_v0 = p1_v0 - [h_len*cos(th_arr_v0 - h_ang), h_len*sin(th_arr_v0 - h_ang)];
p3_v0 = p1_v0 - [h_len*cos(th_arr_v0 + h_ang), h_len*sin(th_arr_v0 + h_ang)];
fill(ax5d_cord, [p1_v0(1) p2_v0(1) p3_v0(1)], [p1_v0(2) p2_v0(2) p3_v0(2)], 'k', 'EdgeColor', 'none');

% Top Labels (Above cord, matching publication)
text(ax5d_cord, mid_x - 300, y_lbl_top, '{\bf V}{\color[rgb]{0.10,0.65,0.65}\bf 0}', 'FontSize', 22);
text(ax5d_cord, mid_x - 140, y_lbl_top, 'Ablation', 'FontWeight', 'bold', 'FontSize', 15, 'HorizontalAlignment', 'center');
text(ax5d_cord, mid_x + 160, y_lbl_top, 'Modulation', 'FontWeight', 'bold', 'FontSize', 15, 'HorizontalAlignment', 'center');

% Below cord: Contralateral Projectome Rostrocaudal profile
ax5d_proj = axes('Position', [0.12 0.08 0.76 0.28]);
hold(ax5d_proj, 'on');

% Shaded intact contralateral outline in background
fill(ax5d_proj, [x_c, fliplr(x_c)], [diff_contra_base', zeros(1, length(diff_contra_base))], [0.90 0.90 0.90], ...
    'FaceAlpha', 0.45, 'EdgeColor', [0.75 0.75 0.75], 'LineWidth', 1.0);

% Shaded V0 commissural component in teal
fill(ax5d_proj, [x_c, fliplr(x_c)], [diff_contra_base', diff_contra_v0'], v0_teal, ...
    'FaceAlpha', 0.50, 'EdgeColor', 'none');

plot(ax5d_proj, x_c, diff_contra_base, 'Color', [0.4 0.4 0.4], 'LineWidth', 1.8);
plot(ax5d_proj, x_c, diff_contra_v0, '--', 'Color', v0_teal, 'LineWidth', 2.2);

yline(ax5d_proj, 0, 'Color', [0.6 0.6 0.6], 'LineWidth', 1.0);
xline(ax5d_proj, 0, ':', 'Color', [0.6 0.6 0.6], 'LineWidth', 1.0);

% Rostral <---> Caudal axis annotation
plot(ax5d_proj, [-500 -1600], [-110 -110], 'k-', 'LineWidth', 1.6);
plot(ax5d_proj, [-2800 -3800], [-110 -110], 'k-', 'LineWidth', 1.6);
fill(ax5d_proj, [-4000 -3780 -3780], [-110 -95 -125], 'k', 'EdgeColor', 'none');
plot(ax5d_proj, [500 1600], [-110 -110], 'k-', 'LineWidth', 1.6);
plot(ax5d_proj, [2800 3800], [-110 -110], 'k-', 'LineWidth', 1.6);
fill(ax5d_proj, [4000 3780 3780], [-110 -95 -125], 'k', 'EdgeColor', 'none');
text(ax5d_proj, -2200, -110, 'Rostral', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');
text(ax5d_proj, 2200, -110, 'Caudal', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');

xlim(ax5d_proj, [-8000 8000]);
ylim(ax5d_proj, [-130 240]);
axis(ax5d_proj, 'off');

p_5d = fullfile(subpanelDir, 'fig5d_v0_anatomy_projectome.png');
exportgraphics(fig5d, p_5d, 'Resolution', 300);
fprintf('Saved Figure 5D: %s\n', p_5d);

%% 9. Generate Figure 5E (V0 Continuous Modulation & Ablation Traces)
fprintf('\nGenerating Figure 5E (V0 Continuous Modulation & Ablation Traces)...\n');
fig5e = figure('Color', 'white', 'Position', [100 100 1100 720], 'Visible', 'off');

% 5E Top: Modulation (Bilateral Synchronous Hopping during Silencing)
ax5e_mod = axes('Position', [0.12 0.53 0.84 0.41]);
hold(ax5e_mod, 'on');

% Silencing window shading in teal
patch(ax5e_mod, [2.5 5.5 5.5 2.5], [-15 -15 85 85], [0.88 0.95 0.95], 'EdgeColor', 'none', 'FaceAlpha', 0.95);
text(ax5e_mod, 4.0, -8, 'Silencing (Hyperpolarisation)', 'Color', [0.05 0.45 0.45], ...
    'FontWeight', 'bold', 'FontSize', 11, 'HorizontalAlignment', 'center');

text(ax5e_mod, 0.05, 80, 'Modulation', 'FontWeight', 'bold', 'FontSize', 14);
plot(ax5e_mod, [1.35 1.65], [80 80], '-k', 'LineWidth', 2.0);
fill(ax5e_mod, [1.75 1.63 1.63], [80 84 76], 'k', 'EdgeColor', 'none');

plot_nerve_panel(ax5e_mod, t_vec, r_r_l2_v0_sil, r_r_l5_v0_sil, r_l_l2_v0_sil, 201);

% 1s scale bar
plot(ax5e_mod, [6.8 7.8], [-12 -12], '-k', 'LineWidth', 3.0);
text(ax5e_mod, 7.3, -5, '1s', 'FontWeight', 'bold', 'FontSize', 11, 'HorizontalAlignment', 'center');

xlim(ax5e_mod, [0 8.0]);
ylim(ax5e_mod, [-16 88]);
axis(ax5e_mod, 'off');

% 5E Bottom: Ablation (Continuous Hopping)
ax5e_abl = axes('Position', [0.12 0.06 0.84 0.41]);
hold(ax5e_abl, 'on');

text(ax5e_abl, 0.05, 80, 'Ablation', 'FontWeight', 'bold', 'FontSize', 14);
plot(ax5e_abl, 1.25 + [-0.08 0.08], 80 + [-3.5 3.5], 'Color', [0.85 0.15 0.15], 'LineWidth', 2.5);
plot(ax5e_abl, 1.25 + [-0.08 0.08], 80 + [3.5 -3.5], 'Color', [0.85 0.15 0.15], 'LineWidth', 2.5);

plot_nerve_panel(ax5e_abl, t_vec, r_r_l2_v0_abl, r_r_l5_v0_abl, r_l_l2_v0_abl, 202);

% 1s scale bar
plot(ax5e_abl, [6.8 7.8], [-12 -12], '-k', 'LineWidth', 3.0);
text(ax5e_abl, 7.3, -5, '1s', 'FontWeight', 'bold', 'FontSize', 11, 'HorizontalAlignment', 'center');

xlim(ax5e_abl, [0 8.0]);
ylim(ax5e_abl, [-16 88]);
axis(ax5e_abl, 'off');

p_5e = fullfile(subpanelDir, 'fig5e_v0_continuous_traces.png');
exportgraphics(fig5e, p_5e, 'Resolution', 300);
fprintf('Saved Figure 5E: %s\n', p_5e);

%% 10. Generate Figure 5F (V0 Quantification)
fprintf('\nGenerating Figure 5F (V0 Quantification: Frequency, Amplitude, Polar Phase Switch)...\n');
fig5f = figure('Color', 'white', 'Position', [100 100 1100 450], 'Visible', 'off');

% 1. Frequency Bar Graph
ax5f_f = axes('Position', [0.06 0.18 0.10 0.70]);
hold(ax5f_f, 'on');
b_f0 = bar(ax5f_f, [1, 2, 3], [freq_base, freq_v0_sil, freq_v0_abl], 0.55);
b_f0.FaceColor = 'flat';
b_f0.CData(1, :) = [0.35 0.35 0.35];
b_f0.CData(2, :) = [0.10 0.65 0.65];
b_f0.CData(3, :) = [0.85 0.40 0.40];
set(ax5f_f, 'XTick', [1 2 3], 'XTickLabel', {'Control', 'Silencing', 'Ablation'}, ...
    'XTickLabelRotation', 45, 'FontWeight', 'bold', 'FontSize', 9.5, 'Box', 'off', 'TickDir', 'out');
ylabel(ax5f_f, 'Frequency Hz', 'FontWeight', 'bold', 'FontSize', 10);
ylim(ax5f_f, [0 3.5]); set(ax5f_f, 'YTick', [0.5 1.5 2.5 3.5]);

% 2. Burst Amplitude Bar Graph with Replicates
ax5f_a = axes('Position', [0.22 0.18 0.12 0.70]);
hold(ax5f_a, 'on');
b_a0 = bar(ax5f_a, [1, 2, 3], [amp_base, amp_v0_sil, amp_v0_abl], 0.55);
b_a0.FaceColor = 'flat';
b_a0.CData(1, :) = [0.35 0.35 0.35];
b_a0.CData(2, :) = [0.10 0.65 0.65];
b_a0.CData(3, :) = [0.85 0.40 0.40];

% Scatter real individual cycle peak amplitudes (no randn noise)
n_b0 = length(pks_amp_base);
if n_b0 > 1
    x_b0 = 1 + linspace(-0.07, 0.07, n_b0)';
else
    x_b0 = 1;
end
scatter(ax5f_a, x_b0, pks_amp_base, 14, [0.2 0.2 0.2], 'filled', 'MarkerFaceAlpha', 0.6);

n_s0 = length(pks_amp_v0_sil);
if n_s0 > 1
    x_s0 = 2 + linspace(-0.07, 0.07, n_s0)';
else
    x_s0 = 2;
end
scatter(ax5f_a, x_s0, pks_amp_v0_sil, 14, [0.1 0.6 0.6], 'filled', 'MarkerFaceAlpha', 0.6);

n_a0 = length(pks_amp_v0_abl);
if n_a0 > 1
    x_a0 = 3 + linspace(-0.07, 0.07, n_a0)';
else
    x_a0 = 3;
end
scatter(ax5f_a, x_a0, pks_amp_v0_abl, 14, [0.8 0.3 0.3], 'filled', 'MarkerFaceAlpha', 0.6);

set(ax5f_a, 'XTick', [1 2 3], 'XTickLabel', {'Control', 'Silencing', 'Ablation'}, ...
    'XTickLabelRotation', 45, 'FontWeight', 'bold', 'FontSize', 9.5, 'Box', 'off', 'TickDir', 'out');
ylabel(ax5f_a, 'Amplitude a.u', 'FontWeight', 'bold', 'FontSize', 10);
max_amp_5f = max([max(pks_amp_base), max(pks_amp_v0_sil), max(pks_amp_v0_abl)]);
y_top_5f = max(50, ceil((max_amp_5f * 1.15) / 5) * 5);
ylim(ax5f_a, [0 y_top_5f]);

% 3. Polar Plot: iL2-iL5 (Left in 5F)
ax5f_p1 = axes('Position', [0.42 0.12 0.26 0.78]);
plot_paper_polar(ax5f_p1, 'iL2-iL5', [l2l5_phase_base, l2l5_phase_v0_sil, l2l5_phase_v0_abl], ...
    cyc_l2l5_base, cyc_l2l5_v0_sil, cyc_l2l5_v0_abl, {[0.2 0.2 0.2], [0.10 0.65 0.65], [0.85 0.40 0.40]});

% 4. Polar Plot: iL2-cL2 (Right in 5F - Switch to 0 rad Synchrony)
ax5f_p2 = axes('Position', [0.72 0.12 0.26 0.78]);
plot_paper_polar(ax5f_p2, 'iL2-cL2', [lr_phase_base, lr_phase_v0_sil, lr_phase_v0_abl], ...
    cyc_lr_base, cyc_lr_v0_sil, cyc_lr_v0_abl, {[0.2 0.2 0.2], [0.10 0.65 0.65], [0.85 0.40 0.40]});

p_5f = fullfile(subpanelDir, 'fig5f_v0_quantification.png');
exportgraphics(fig5f, p_5f, 'Resolution', 300);
fprintf('Saved Figure 5F: %s\n', p_5f);

%% 11. Save Evidence-Based Metrics
metrics = struct();
metrics.figure = 5;
metrics.status = 'METHODS-BASED RECONSTRUCTION — RESULT DIFFERENT';
metrics.status_description = 'V1 and V0 ablation/silencing simulations executed with author geometry, connectivity masks, and integration routines. Under released network parameters, V1 ablation abolishes active rhythmic bursting (amplitude drops to ~2.0 a.u. quiescent state rather than published ~22 a.u. slow bursting). V0 ablation preserves robust bursting (~45 a.u.) but does not complete the full transition to bilateral in-phase synchrony (~0 rad) without compensatory drive adjustments.';
metrics.v1_manipulation = struct(...
    'freq_base_hz', freq_base, ...
    'freq_sil_hz', freq_v1_sil, ...
    'freq_abl_hz', freq_v1_abl, ...
    'amp_base', amp_base, ...
    'amp_sil', amp_v1_sil, ...
    'amp_abl', amp_v1_abl, ...
    'lr_phase_base_deg', rad2deg(lr_phase_base), ...
    'lr_phase_sil_deg', rad2deg(lr_phase_v1_sil), ...
    'lr_phase_abl_deg', rad2deg(lr_phase_v1_abl), ...
    'l2l5_phase_base_deg', rad2deg(l2l5_phase_base), ...
    'l2l5_phase_sil_deg', rad2deg(l2l5_phase_v1_sil), ...
    'l2l5_phase_abl_deg', rad2deg(l2l5_phase_v1_abl));

metrics.v0_manipulation = struct(...
    'freq_base_hz', freq_base, ...
    'freq_sil_hz', freq_v0_sil, ...
    'freq_abl_hz', freq_v0_abl, ...
    'amp_base', amp_base, ...
    'amp_sil', amp_v0_sil, ...
    'amp_abl', amp_v0_abl, ...
    'lr_phase_base_deg', rad2deg(lr_phase_base), ...
    'lr_phase_sil_deg', rad2deg(lr_phase_v0_sil), ...
    'lr_phase_abl_deg', rad2deg(lr_phase_v0_abl), ...
    'l2l5_phase_base_deg', rad2deg(l2l5_phase_base), ...
    'l2l5_phase_sil_deg', rad2deg(l2l5_phase_v0_sil), ...
    'l2l5_phase_abl_deg', rad2deg(l2l5_phase_v0_abl));

jsonStr = jsonencode(metrics, 'PrettyPrint', true);
metricsFile = fullfile(resultsDir, 'figure5_metrics.json');
fid = fopen(metricsFile, 'w');
fwrite(fid, jsonStr, 'char');
fclose(fid);
fprintf('Saved Figure 5 metrics: %s\n', metricsFile);

t_total = toc(t_start);
fprintf('\n=================================================================\n');
fprintf('STAGE 6 FIGURE 5 SUBPANELS COMPLETED (Elapsed: %.2f s)\n', t_total);
fprintf('=================================================================\n');

diary off;
exit(0);

%% Helper Function: Plot Nerve Panel (author PlotNeurogram generative model)
function plot_nerve_panel(ax, t_vec, r_r_l2, r_r_l5, r_l_l2, rand_seed)
    rng(rand_seed);
    noiselevel = 0.10;
    t_sec = t_vec / 1000;
    
    traces = {r_l_l2, r_r_l5, r_r_l2};
    labels = {'L2', 'L5', 'L2'};
    y_offsets = [12, 38, 64];
    
    % Draw "Right" and "Left" labels and brackets on left
    text(ax, -0.45, 51, 'Right', 'FontWeight', 'bold', 'FontSize', 12, 'Rotation', 90, 'HorizontalAlignment', 'center');
    plot(ax, [-0.25 -0.20 -0.20 -0.25], [38 38 64 64], '-k', 'LineWidth', 1.4);
    
    text(ax, -0.45, 12, 'Left', 'FontWeight', 'bold', 'FontSize', 12, 'Rotation', 90, 'HorizontalAlignment', 'center');
    plot(ax, [-0.25 -0.20 -0.20 -0.25], [6 6 18 18], '-k', 'LineWidth', 1.4);
    
    for tr_i = 1:3
        tr = traces{tr_i};
        y_off = y_offsets(tr_i);
        lbl = labels{tr_i};
        
        text(ax, -0.15, y_off, lbl, 'FontWeight', 'bold', 'FontSize', 11, 'HorizontalAlignment', 'right');
        
        env = movmean(tr, 25);
        peak_val = max(env);
        amp_range = peak_val - min(env);
        
        % Detect burst blocks only if there is active bursting
        if amp_range > 5.0
            is_burst = env > (min(env) + 0.35 * amp_range);
            burst_blocks = diff([0; is_burst; 0]);
            b_starts = find(burst_blocks == 1);
            b_ends = find(burst_blocks == -1) - 1;
            
            for b_k = 1:length(b_starts)
                t_s = t_sec(b_starts(b_k));
                t_e = t_sec(b_ends(b_k));
                if (t_e - t_s) > 0.08
                    patch(ax, [t_s t_e t_e t_s], y_off + [-8 -8 11 11], [0.72 0.72 0.72], ...
                        'EdgeColor', 'none', 'FaceAlpha', 0.65);
                end
            end
        end
        
        % Author generative model from @Network/PlotNeurogram.m
        prob = tr;
        prob_z = (prob - mean(prob)) / max(1e-6, std(prob));
        sig = randn(size(prob)) * noiselevel .* binornd(1, normcdf(prob_z));
        sig = sig .* prob + (randn(size(prob)) * noiselevel);
        
        plot(ax, t_sec, sig * 1.5 + y_off, 'Color', [0.15 0.15 0.15], 'LineWidth', 0.6);
        
        % White smooth curve through center
        norm_env = movmean(prob, 25);
        if amp_range > 5.0
            white_curve = (norm_env - mean(norm_env)) / amp_range * 6.5;
        else
            white_curve = (norm_env - mean(norm_env)) * 0.2;
        end
        plot(ax, t_sec, white_curve + y_off, 'Color', 'w', 'LineWidth', 1.2);
    end
end

%% Helper Function: Polar Plot matching Paper with crisp vector arrows
function plot_paper_polar(ax, title_str, mean_phases, cyc_ctrl, cyc_sil, cyc_abl, colors)
    hold(ax, 'on');
    axis(ax, 'equal');
    xlim(ax, [-1.45 1.45]);
    ylim(ax, [-1.45 1.45]);
    axis(ax, 'off');
    
    t_c = linspace(0, 2*pi, 180);
    
    % Light grey center disk
    fill(ax, 0.28*cos(t_c), 0.28*sin(t_c), [0.92 0.92 0.92], 'EdgeColor', 'none');
    
    % Unit circle
    plot(ax, cos(t_c), sin(t_c), '-k', 'LineWidth', 1.2);
    
    % Axis ticks
    text(ax, 1.18, 0, '0', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'left');
    text(ax, 0, 1.18, '\pi/2', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');
    text(ax, -1.18, 0, '\pi', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'right');
    text(ax, 0, -1.22, '3\pi/2', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');
    
    % Title at top-left so it does not collide with \pi/2
    text(ax, -0.85, 1.32, title_str, 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');
    
    % Replicate dots around periphery
    scatter_cycles(ax, cyc_ctrl, colors{1}, 101);
    scatter_cycles(ax, cyc_sil, colors{2}, 102);
    scatter_cycles(ax, cyc_abl, colors{3}, 103);
    
    % Mean phase vectors with crisp filled arrowheads
    hw = 0.08; hl = 0.12;
    for k = 1:3
        ph = mean_phases(k);
        if ~isnan(ph)
            c = colors{k};
            vx = 0.90 * cos(ph);
            vy = 0.90 * sin(ph);
            plot(ax, [0 vx], [0 vy], 'Color', c, 'LineWidth', 2.8);
            
            ux = cos(ph); uy = sin(ph);
            perp_x = -uy; perp_y = ux;
            hx1 = vx - hl*ux + hw*perp_x;
            hy1 = vy - hl*uy + hw*perp_y;
            hx2 = vx - hl*ux - hw*perp_x;
            hy2 = vy - hl*uy - hw*perp_y;
            fill(ax, [vx hx1 hx2], [vy hy1 hy2], c, 'EdgeColor', 'none');
        end
    end
end

%% Helper Function: Scatter cycle-to-cycle dots
function scatter_cycles(ax, cycle_phases, color, ~)
    if isempty(cycle_phases), return; end
    n_pts = min(12, length(cycle_phases));
    pts = cycle_phases(1:n_pts);
    r = 1.04;
    scatter(ax, r .* cos(pts), r .* sin(pts), 16, color, 'filled', 'MarkerFaceAlpha', 0.7);
end

%% Helper Function: GeneratePlot (author projectome kernel)
function difference = GeneratePlot_local(N, ConnMat, edges)
    Ex = (N.Transmit > 0);
    In = (N.Transmit < 0);
    Dist = bsxfun(@minus, N.Position(:, 2), N.Position(:, 2)');
    ProjEx = ConnMat(:, Ex); 
    ProjIn = ConnMat(:, In);
    DistEx = Dist(:, Ex);
    DistIn = Dist(:, In);
    
    val_in = ProjIn(ProjIn ~= 0);
    val_ex = ProjEx(ProjEx ~= 0);
    
    dist_in = DistIn(ProjIn ~= 0);
    dist_ex = DistEx(ProjEx ~= 0);
    
    yin = discretize(dist_in, edges);
    yex = discretize(dist_ex, edges);
    
    num_bins = length(edges) - 1;
    valid_in = ~isnan(yin);
    valid_ex = ~isnan(yex);
    
    SumIn = accumarray(yin(valid_in), abs(val_in(valid_in)), [num_bins 1]);
    SumEx = accumarray(yex(valid_ex), abs(val_ex(valid_ex)), [num_bins 1]);
    
    raw_diff = SumEx - SumIn;
    % Gaussian smoothing (window 7 bins = 280 um) matching Figure 2G
    difference = smoothdata(raw_diff, 'gaussian', 7);
end

%% Helper Function: Measure Dynamics and individual cycle phases
function [freq, lr_phase, l2l5_phase, cyc_lr, cyc_l2l5, pks_amp] = measure_dynamics_cycles(r_l, r_r, r_l5)
    range_l = max(r_l) - min(r_l);
    range_r = max(r_r) - min(r_r);
    prom_l = max(0.3, 0.12 * range_l);
    prom_r = max(0.3, 0.12 * range_r);
    
    [~, locs_l] = findpeaks(r_l, 'MinPeakDistance', 60, 'MinPeakProminence', prom_l);
    [pks_r, locs_r] = findpeaks(r_r, 'MinPeakDistance', 60, 'MinPeakProminence', prom_r);
    [~, locs_l5] = findpeaks(r_l5, 'MinPeakDistance', 60, 'MinPeakProminence', max(0.3, 0.12 * (max(r_l5) - min(r_l5))));
    
    if ~isempty(pks_r)
        pks_amp = pks_r - min(r_r);
    else
        pks_amp = range_r;
    end
    
    cyc_lr = [];
    cyc_l2l5 = [];
    
    if length(locs_r) >= 2
        T_g = mean(diff(locs_r));
        freq = 1000 / T_g;
        
        for k = 1:length(locs_r)
            if ~isempty(locs_l)
                [~, near_l] = min(abs(locs_l - locs_r(k)));
                dt_l = locs_l(near_l) - locs_r(k);
                cyc_lr(end+1) = mod(dt_l / T_g * 2 * pi, 2 * pi);
            end
        end
        sin_sum = sum(sin(cyc_lr)); cos_sum = sum(cos(cyc_lr));
        lr_phase = mod(atan2(sin_sum, cos_sum), 2 * pi);
        
        for k = 1:length(locs_r)
            if ~isempty(locs_l5)
                [~, near_l5] = min(abs(locs_l5 - locs_r(k)));
                dt_l5 = locs_l5(near_l5) - locs_r(k);
                cyc_l2l5(end+1) = mod(dt_l5 / T_g * 2 * pi, 2 * pi);
            end
        end
        sin_sum = sum(sin(cyc_l2l5)); cos_sum = sum(cos(cyc_l2l5));
        l2l5_phase = mod(atan2(sin_sum, cos_sum), 2 * pi);
    else
        freq = NaN;
        lr_phase = NaN;
        l2l5_phase = NaN;
    end
end
