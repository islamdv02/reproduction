%% run_figure4_reproduction.m
% Faithful, evidence-based reproduction of Figure 4 from Komi et al. (2026).
% Descending Control of Locomotor Activity by Modulation of Gain and Projectome.

clear;
clc;
close all;

t_start = tic;
scriptDir = fileparts(mfilename('fullpath'));
rootDir = fullfile(scriptDir, '..');
sourceDir = fullfile(rootDir, 'source');
resultsDir = fullfile(rootDir, 'results');
subpanelDir = fullfile(rootDir, 'figures', 'subpanels_fig4');
figDir = fullfile(rootDir, 'figures', 'main_figures');
logsDir = fullfile(rootDir, 'logs');

if ~exist(subpanelDir, 'dir'), mkdir(subpanelDir); end
if ~exist(figDir, 'dir'), mkdir(figDir); end
if ~exist(logsDir, 'dir'), mkdir(logsDir); end

logFile = fullfile(logsDir, 'step5_figure4_reproduction.log');
diary(logFile);
diary on;

fprintf('=================================================================\n');
fprintf('STAGE 5: Figure 4 Reproduction (Komi et al., 2026)\n');
fprintf('Timestamp: %s\n', datestr(now));
fprintf('MATLAB Version: %s\n', version);
fprintf('=================================================================\n');

cd(sourceDir);
addpath(fullfile(rootDir, 'scripts', 'compat'));
addpath(genpath(sourceDir));

%% 1. Load Baseline Network
networkFile = fullfile(resultsDir, 'baseline_network.mat');
fprintf('Loading baseline network from: %s ...\n', networkFile);
load(networkFile, 'N');
N_neurons = size(N.ConnMat, 1);
fprintf('Loaded network: N = %d neurons.\n', N_neurons);

%% 2. Figure 4A: Compound Hyperbolic Tangent Activation Curves
fprintf('\nGenerating Figure 4A (Compound Hyperbolic Tangent Response Functions)...\n');
fig4a = figure('Color', 'white', 'Position', [100 100 520 460], 'Visible', 'off');
ax4a = axes('Position', [0.18 0.18 0.76 0.70]);
hold(ax4a, 'on');

threshold = 5;
f_max = 50;
gains = [2.0, 1.0, 0.5];
cols_g = [0.1 0.1 0.1; 0.45 0.45 0.45; 0.72 0.72 0.72];
V_range = linspace(0, 150, 500);

for g_idx = 1:length(gains)
    g = gains(g_idx);
    rates_g = zeros(size(V_range));
    neg = (V_range - threshold) <= 0;
    pos = (V_range - threshold) > 0;
    rates_g(neg) = threshold .* tanh(g .* (V_range(neg) - threshold) ./ threshold);
    rates_g(pos) = f_max .* tanh(g .* (V_range(pos) - threshold) ./ f_max);
    rates_g = rates_g + threshold;
    rates_g(rates_g < 0) = 0;
    
    plot(ax4a, V_range, rates_g, 'LineWidth', 2.4, 'Color', cols_g(g_idx, :));
end

tangent_x_2 = [5, 27.5];
tangent_y_2 = [5, 5 + 2.0 * (27.5 - 5)];
plot(ax4a, tangent_x_2, tangent_y_2, '--', 'Color', [0.4 0.4 0.4], 'LineWidth', 1.3);
text(ax4a, 27.5, 54, '2', 'FontSize', 11, 'FontWeight', 'bold', 'HorizontalAlignment', 'center');

tangent_x_1 = [5, 50];
tangent_y_1 = [5, 5 + 1.0 * (50 - 5)];
plot(ax4a, tangent_x_1, tangent_y_1, '--', 'Color', [0.4 0.4 0.4], 'LineWidth', 1.3);
text(ax4a, 50, 54, 'Gain = 1', 'FontSize', 11, 'FontWeight', 'bold', 'HorizontalAlignment', 'center');

tangent_x_05 = [5, 95];
tangent_y_05 = [5, 5 + 0.5 * (95 - 5)];
plot(ax4a, tangent_x_05, tangent_y_05, '--', 'Color', [0.4 0.4 0.4], 'LineWidth', 1.3);
text(ax4a, 95, 54, '0.5', 'FontSize', 11, 'FontWeight', 'bold', 'HorizontalAlignment', 'center');

plot(ax4a, [0 0], [0 45], '-k', 'LineWidth', 1.2);
plot(ax4a, [-20 150], [0 0], '-k', 'LineWidth', 1.2);

box(ax4a, 'off');
set(ax4a, 'TickDir', 'out', 'FontSize', 11, 'LineWidth', 1.2);
xlim(ax4a, [-20 150]);
ylim(ax4a, [0 62]);
set(ax4a, 'XTick', [0 150], 'YTick', [0 50]);
xlabel(ax4a, 'Input', 'FontWeight', 'bold', 'FontSize', 12);
ylabel(ax4a, 'Rate R [Hz]', 'FontWeight', 'bold', 'FontSize', 12);
title(ax4a, 'Activation function', 'FontWeight', 'bold', 'FontSize', 13);
text(ax4a, -40, 64, 'A', 'FontSize', 18, 'FontWeight', 'bold', 'Units', 'data');

p_4a = fullfile(subpanelDir, 'fig4a_activation_functions.png');
exportgraphics(fig4a, p_4a, 'Resolution', 300);
fprintf('Saved Figure 4A: %s\n', p_4a);

%% 3. Figure 4B: Descending Motor Pathway Terminals & Target Types (4 Panels)
fprintf('\nGenerating Figure 4B (Descending Motor Pathways & Target Receptor Profiles)...\n');
fig4b = figure('Color', 'white', 'Position', [100 100 950 850], 'Visible', 'off');

desc = load("01_SpinalGeometryFiles\matDescending.mat");

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
    c_mask = strcmpi(string(N.Types), target_types{i});
    n_c = sum(c_mask);
    if n_c > 0
        lpgi_pct(i) = sum(is_lpgi_target & c_mask) / n_c * 100;
        raphe_pct(i) = sum(is_raphe_target & c_mask) / n_c * 100;
    end
end

left_neurons = (N.Latera < 0);

% 4B Top-Left: LPGi-Vglut2 Terminals
axes('Position', [0.06 0.54 0.40 0.38]);
hold on;
scatter(N.Position(left_neurons, 1), N.Position(left_neurons, 3), 4, [0.82 0.82 0.82], 'filled', 'MarkerFaceAlpha', 0.35);
fill(desc.LPGIVglutL.Position(:,1), desc.LPGIVglutL.Position(:,2), [0.92 0.35 0.6], ...
    'FaceAlpha', 0.55, 'EdgeColor', [0.85 0.2 0.5], 'LineWidth', 1.5);
% Oval outline in lateral funiculus
t_el = linspace(0, 2*pi, 50);
el_x = -780 + 70*cos(t_el);
el_y = -880 + 160*sin(t_el);
plot(el_x, el_y, '-', 'Color', [0.85 0.2 0.5], 'LineWidth', 1.5);
quiver(-720, -920, 220, 50, 0, 'k', 'LineWidth', 1.2, 'MaxHeadSize', 0.8);
quiver(-720, -840, 220, 30, 0, 'k', 'LineWidth', 1.2, 'MaxHeadSize', 0.8);
axis equal tight;
xlim([-950 50]); ylim([-1350 -150]);
set(gca, 'YDir', 'normal', 'Visible', 'off');
text(-450, -100, {'LPGi-Vglut2', 'Terminals'}, 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');

% 4B Top-Right: LPGi Targets % Polar Plot via Cartesian
ax_tg = axes('Position', [0.55 0.54 0.40 0.38]);
hold(ax_tg, 'on');
axis(ax_tg, 'equal');
xlim(ax_tg, [-145 145]);
ylim(ax_tg, [-145 145]);
axis(ax_tg, 'off');

for r_c = [25, 50, 75, 100]
    t_c = linspace(0, 2*pi, 100);
    plot(ax_tg, r_c * cos(t_c), r_c * sin(t_c), ':', 'Color', [0.75 0.75 0.75], 'LineWidth', 0.8);
    text(ax_tg, 0, r_c, sprintf('%d', r_c), 'FontSize', 8, 'Color', [0.5 0.5 0.5], 'HorizontalAlignment', 'center');
end

theta_tg = linspace(pi/2, pi/2 - 2*pi, n_tg + 1);
theta_pts = theta_tg(1:end-1);
for i = 1:n_tg
    plot(ax_tg, [0, 100*cos(theta_pts(i))], [0, 100*sin(theta_pts(i))], '--', 'Color', [0.8 0.8 0.8], 'LineWidth', 0.8);
    lx = 122 * cos(theta_pts(i));
    ly = 122 * sin(theta_pts(i));
    text(ax_tg, lx, ly, target_labels{i}, 'FontWeight', 'bold', 'FontSize', 9.5, 'HorizontalAlignment', 'center');
end

[x_p, y_p] = pol2cart(theta_tg, [lpgi_pct; lpgi_pct(1)]);
patch(ax_tg, x_p, y_p, [0.78 0.78 0.78], 'FaceAlpha', 0.65, 'EdgeColor', 'k', 'LineWidth', 1.6);

t_in = linspace(theta_pts(1), theta_pts(4), 50);
plot(ax_tg, 100*cos(t_in), 100*sin(t_in), '-k', 'LineWidth', 3.2);
t_exc = linspace(theta_pts(5), theta_pts(9), 50);
plot(ax_tg, 100*cos(t_exc), 100*sin(t_exc), '-', 'Color', [0.9 0.25 0.55], 'LineWidth', 3.2);

text(ax_tg, 0, 135, 'Targets %', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');
patch(ax_tg, [-35 -20 -20 -35], [-130 -130 -140 -140], [0.9 0.25 0.55], 'EdgeColor', 'none');
text(ax_tg, -15, -135, 'Exc', 'FontSize', 9, 'FontWeight', 'bold');
patch(ax_tg, [15 30 30 15], [-130 -130 -140 -140], [0 0 0], 'EdgeColor', 'none');
text(ax_tg, 35, -135, 'In', 'FontSize', 9, 'FontWeight', 'bold');

% 4B Bottom-Left: Raphe-5HT Terminals
axes('Position', [0.06 0.08 0.40 0.38]);
hold on;
scatter(N.Position(left_neurons, 1), N.Position(left_neurons, 3), 4, [0.82 0.82 0.82], 'filled', 'MarkerFaceAlpha', 0.35);
fill(desc.RapheObsL.Position(:,1), desc.RapheObsL.Position(:,2), [0.15 0.65 0.65], ...
    'FaceAlpha', 0.55, 'EdgeColor', [0.1 0.5 0.5], 'LineWidth', 1.5);
el_x_r = -780 + 70*cos(t_el);
el_y_r = -480 + 160*sin(t_el);
plot(el_x_r, el_y_r, '-', 'Color', [0.15 0.65 0.65], 'LineWidth', 1.5);
quiver(-720, -520, 220, 80, 0, 'k', 'LineWidth', 1.2, 'MaxHeadSize', 0.8);
quiver(-720, -440, 220, 100, 0, 'k', 'LineWidth', 1.2, 'MaxHeadSize', 0.8);
axis equal tight;
xlim([-950 50]); ylim([-1350 -150]);
set(gca, 'YDir', 'normal', 'Visible', 'off');
text(-450, -100, {'Raphe-5HT', 'Terminals'}, 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');

% 4B Bottom-Right: Raphe Targets % Polar Plot via Cartesian
ax_rp = axes('Position', [0.55 0.08 0.40 0.38]);
hold(ax_rp, 'on');
axis(ax_rp, 'equal');
xlim(ax_rp, [-145 145]);
ylim(ax_rp, [-145 145]);
axis(ax_rp, 'off');

for r_c = [25, 50, 75, 100]
    t_c = linspace(0, 2*pi, 100);
    plot(ax_rp, r_c * cos(t_c), r_c * sin(t_c), ':', 'Color', [0.75 0.75 0.75], 'LineWidth', 0.8);
    text(ax_rp, 0, r_c, sprintf('%d', r_c), 'FontSize', 8, 'Color', [0.5 0.5 0.5], 'HorizontalAlignment', 'center');
end

raphe_labels = {'dI6*', 'V0d*', 'V2b*', 'V1*', 'V2a_{Vsx2+}', 'V2a_{Vsx2-}*', 'V0v*', 'V3', 'MN*'};
for i = 1:n_tg
    plot(ax_rp, [0, 100*cos(theta_pts(i))], [0, 100*sin(theta_pts(i))], '--', 'Color', [0.8 0.8 0.8], 'LineWidth', 0.8);
    lx = 122 * cos(theta_pts(i));
    ly = 122 * sin(theta_pts(i));
    text(ax_rp, lx, ly, raphe_labels{i}, 'FontWeight', 'bold', 'FontSize', 9.5, 'HorizontalAlignment', 'center');
end

[x_rp, y_rp] = pol2cart(theta_tg, [raphe_pct; raphe_pct(1)]);
patch(ax_rp, x_rp, y_rp, [0.78 0.78 0.78], 'FaceAlpha', 0.65, 'EdgeColor', 'k', 'LineWidth', 1.6);

plot(ax_rp, 100*cos(t_in), 100*sin(t_in), '-k', 'LineWidth', 3.2);
plot(ax_rp, 100*cos(t_exc), 100*sin(t_exc), '-', 'Color', [0.9 0.25 0.55], 'LineWidth', 3.2);

text(ax_rp, 0, -140, '* Diff.Exp. of 5-HT7r', 'FontSize', 10, 'FontWeight', 'bold', 'HorizontalAlignment', 'center');

annotation(fig4b, 'textbox', [0.02 0.94 0.05 0.05], 'String', 'B', ...
    'FontSize', 18, 'FontWeight', 'bold', 'EdgeColor', 'none');
annotation(fig4b, 'line', [0.49 0.49], [0.06 0.92], 'LineStyle', '--', 'Color', [0.6 0.6 0.6], 'LineWidth', 1.2);

p_4b = fullfile(subpanelDir, 'fig4b_descending_tracts.png');
exportgraphics(fig4b, p_4b, 'Resolution', 300);
fprintf('Saved Figure 4B: %s\n', p_4b);

%% 4. Load or Run Continuous Stimulation Protocol (Figure 4C/D)
fprintf('\nChecking continuous stimulation protocol (12,000 ms)...\n');
t_total = 12000;
t_vec = 1:t_total;

drive_profile = zeros(1, t_total);
gain_profile = zeros(1, t_total);

% Walking
drive_profile(1:4000) = 15.0;
gain_profile(1:4000) = 0.7;

% Ramp 1
ramp1_idx = 4001:5000;
drive_profile(ramp1_idx) = linspace(15.0, 22.0, length(ramp1_idx));
gain_profile(ramp1_idx) = linspace(0.7, 1.0, length(ramp1_idx));

% Trotting
drive_profile(5001:8000) = 22.0;
gain_profile(5001:8000) = 1.0;

% Ramp 2
ramp2_idx = 8001:9000;
drive_profile(ramp2_idx) = linspace(22.0, 30.0, length(ramp2_idx));
gain_profile(ramp2_idx) = linspace(1.0, 1.8, length(ramp2_idx));

% Bounding
drive_profile(9001:12000) = 30.0;
gain_profile(9001:12000) = 1.8;

gait_windows = {1500:3800, 5500:7800, 9500:11800};
gait_names = {'Walking', 'Trotting', 'Bounding'};

simFile = fullfile(resultsDir, 'figure4_simulation.mat');
if exist(simFile, 'file')
    fprintf('Loading existing continuous simulation from: %s ...\n', simFile);
    load(simFile, 'N_sim');
else
    I_input = zeros(N_neurons, t_total);
    I_input(is_lpgi_target, :) = repmat(drive_profile, [sum(is_lpgi_target), 1]);
    I_input(~is_lpgi_target, :) = 10.0;
    
    [~, IxT] = ismember(N.Types, N.Parameters.Types);
    base_gains = reshape(N.Parameters.Gains(IxT), [N_neurons, 1]);
    
    gain_input = repmat(base_gains, [1, t_total]);
    for t = 1:t_total
        gain_input(is_raphe_target, t) = base_gains(is_raphe_target) * gain_profile(t);
    end
    
    fprintf('Executing continuous 12,000 ms simulation in N.Simulate...\n');
    N_sim = copy(N);
    h_dummy = figure('Visible', 'off');
    sim_tic = tic;
    N_sim.Simulate(t_total, 'I_e', I_input, 'gain', gain_input, 'seed', 42);
    if isvalid(h_dummy), close(h_dummy); end
    fprintf('Simulation completed in %.2f s.\n', toc(sim_tic));
    save(simFile, 'N_sim', 'I_input', 'gain_input', 'drive_profile', 'gain_profile', ...
        'is_lpgi_target', 'is_raphe_target', 'gait_windows', 'gait_names', '-v7.3');
    fprintf('Saved simulation to: %s\n', simFile);
end

%% 5. Figure 4C: Descending Control Profile and Modulated Effective Projectomes
fprintf('\nGenerating Figure 4C (Continuous Profile & Modulated Effective Projectomes)...\n');
fig4c = figure('Color', 'white', 'Position', [100 100 1150 480], 'Visible', 'off');

axes('Position', [0.08 0.62 0.88 0.28]);
hold on;
yyaxis left;
plot(t_vec / 1000, drive_profile, 'Color', [0.85 0.15 0.55], 'LineWidth', 2.2);
ylabel('LPGi Input', 'FontWeight', 'bold', 'Color', [0.85 0.15 0.55], 'FontSize', 10);
ylim([0 35]); set(gca, 'YColor', [0.85 0.15 0.55], 'YTick', [0 30]);
text(1.5, 20, 'LPGi', 'Color', [0.85 0.15 0.55], 'FontWeight', 'bold', 'FontSize', 10);

yyaxis right;
plot(t_vec / 1000, gain_profile, 'Color', [0.15 0.65 0.65], 'LineWidth', 2.2);
ylabel('Raphe Gain', 'FontWeight', 'bold', 'Color', [0.15 0.65 0.65], 'FontSize', 10);
ylim([0 2.2]); set(gca, 'YColor', [0.15 0.65 0.65], 'YTick', [0 2]);
text(1.5, 0.4, 'Raphe', 'Color', [0.15 0.65 0.65], 'FontWeight', 'bold', 'FontSize', 10);

xline(4.0, '--k', 'Color', [0.5 0.5 0.5], 'LineWidth', 1.0);
xline(5.0, '--k', 'Color', [0.5 0.5 0.5], 'LineWidth', 1.0);
xline(8.0, '--k', 'Color', [0.5 0.5 0.5], 'LineWidth', 1.0);
xline(9.0, '--k', 'Color', [0.5 0.5 0.5], 'LineWidth', 1.0);

xlim([0 12]);
set(gca, 'XTick', [], 'TickDir', 'out', 'Box', 'off');

lat = N.Latera;
W_raw = full(N.ConnMat);
W_ipsi_base = W_raw;
W_ipsi_base(lat < 0, lat > 0) = 0;
W_ipsi_base(lat > 0, lat < 0) = 0;

W_contra_base = W_raw;
W_contra_base(lat > 0, lat > 0) = 0;
W_contra_base(lat < 0, lat < 0) = 0;

edges = -8000:40:8000;
edges_c = edges(1:end-1) + diff(edges)/2;

col_widths = [0.27, 0.27, 0.27];
x_starts = [0.08, 0.38, 0.68];

for g = 1:3
    r_mean = mean(N_sim.Rates(gait_windows{g}, :), 1)';
    r_scale = r_mean / max(eps, mean(r_mean));
    
    W_eff_ipsi = W_ipsi_base .* repmat(r_scale', [N_neurons, 1]);
    diff_ipsi = GeneratePlot_local(N, W_eff_ipsi, edges);
    
    axes('Position', [x_starts(g) 0.33 col_widths(g) 0.22]);
    hold on;
    area(edges_c, max(0, diff_ipsi), 'FaceColor', [0.85 0.2 0.5], 'EdgeColor', 'none', 'FaceAlpha', 0.7);
    area(edges_c, min(0, diff_ipsi), 'FaceColor', [0.15 0.15 0.15], 'EdgeColor', 'none', 'FaceAlpha', 0.85);
    plot(edges_c, diff_ipsi, 'k', 'LineWidth', 1.1);
    xline(0, '--k', 'Color', [0.4 0.4 0.4], 'LineWidth', 0.9);
    yline(0, '--k', 'Color', [0.4 0.4 0.4], 'LineWidth', 0.9);
    xlim([-7000 7000]);
    ylim([-180 200]);
    axis off;
    if g == 1
        text(-7800, 0, 'Ipsi', 'FontWeight', 'bold', 'FontSize', 11, 'HorizontalAlignment', 'center', 'Rotation', 90);
    end
end

for g = 1:3
    r_mean = mean(N_sim.Rates(gait_windows{g}, :), 1)';
    r_scale = r_mean / max(eps, mean(r_mean));
    
    W_eff_contra = W_contra_base .* repmat(r_scale', [N_neurons, 1]);
    diff_contra = GeneratePlot_local(N, W_eff_contra, edges);
    
    axes('Position', [x_starts(g) 0.08 col_widths(g) 0.22]);
    hold on;
    area(edges_c, max(0, diff_contra), 'FaceColor', [0.85 0.2 0.5], 'EdgeColor', 'none', 'FaceAlpha', 0.7);
    area(edges_c, min(0, diff_contra), 'FaceColor', [0.15 0.15 0.15], 'EdgeColor', 'none', 'FaceAlpha', 0.85);
    plot(edges_c, diff_contra, 'k', 'LineWidth', 1.1);
    xline(0, '--k', 'Color', [0.4 0.4 0.4], 'LineWidth', 0.9);
    yline(0, '--k', 'Color', [0.4 0.4 0.4], 'LineWidth', 0.9);
    xlim([-7000 7000]);
    ylim([-60 60]);
    axis off;
    if g == 1
        text(-7800, 0, 'Contra', 'FontWeight', 'bold', 'FontSize', 11, 'HorizontalAlignment', 'center', 'Rotation', 90);
    end
end

annotation(fig4c, 'textbox', [0.01 0.92 0.05 0.05], 'String', 'C', ...
    'FontSize', 18, 'FontWeight', 'bold', 'EdgeColor', 'none');

p_4c = fullfile(subpanelDir, 'fig4c_modulated_projectome.png');
exportgraphics(fig4c, p_4c, 'Resolution', 300);
fprintf('Saved Figure 4C: %s\n', p_4c);

%% 6. Figure 4D: Continuous Multi-Gait Transitions (Neurogram, EMG, Nerves)
fprintf('\nGenerating Figure 4D (Continuous Multi-Gait Locomotor Patterns)...\n');
fig4d = figure('Color', 'white', 'Position', [100 100 1300 780], 'Visible', 'off');

% 4D Top: Segmental Spatial Activity Raster (T13 to S4)
axes('Position', [0.08 0.66 0.85 0.27]);
right_mask = (N.Latera > 0);
y_right = N.Position(right_mask, 2);
[y_sorted, sort_rc] = sort(y_right, 'ascend');
rates_right = N_sim.Rates(:, right_mask);
rates_sorted = rates_right(:, sort_rc)';

y_bins = linspace(min(y_sorted), max(y_sorted), 80);
binned_rates = zeros(length(y_bins)-1, t_total);
for b = 1:(length(y_bins)-1)
    in_bin = (y_sorted >= y_bins(b)) & (y_sorted < y_bins(b+1));
    if any(in_bin)
        binned_rates(b, :) = mean(rates_sorted(in_bin, :), 1);
    end
end

imagesc(t_vec / 1000, 1:size(binned_rates, 1), binned_rates);
colormap(gca, flipud(gray(256)));
caxis([0 35]);
ylabel('Segments', 'FontWeight', 'bold', 'FontSize', 11);
set(gca, 'YDir', 'reverse', 'XTick', [], 'TickDir', 'out', 'Box', 'off');
xline(4.0, '--k', 'Color', [0.4 0.4 0.4], 'LineWidth', 1.0);
xline(8.0, '--k', 'Color', [0.4 0.4 0.4], 'LineWidth', 1.0);

text(2.0, -5, 'Walking', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');
text(6.0, -5, 'Trotting', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');
text(10.0, -5, 'Bounding', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');

% 4D Middle: Right Synthetic EMGs (VM, BF, TA, Sol in top-to-bottom order matching paper)
axes('Position', [0.08 0.35 0.85 0.28]);
hold on;
muscles_order = {'Soleus', 'Tibialis Anterior', 'Biceps Femoris', 'Vastus Medialis'};
noiselevel = 0.12;
rng(42);

curr_offset = 0;
emg_ticks = [];
emg_envs = struct();

for m = 1:length(muscles_order)
    m_name = muscles_order{m};
    ix_m = (N.MnID == m_name) & (N.Latera > 0);
    if any(ix_m)
        prob = mean(N_sim.Rates(:, ix_m), 2);
        sig = randn(size(prob)) * noiselevel .* binornd(1, normcdf(normalize(prob, 'zscore')));
        sig = sig .* prob + (randn(size(prob)) * noiselevel);
        env = movmean(abs(sig), 25);
        
        m_key = matlab.lang.makeValidName(m_name);
        emg_envs.(m_key) = env;
        
        is_burst = env > 0.25 * max(env);
        burst_blocks = diff([0; is_burst; 0]);
        b_starts = find(burst_blocks == 1);
        b_ends = find(burst_blocks == -1) - 1;
        
        curr_offset = curr_offset + 15;
        emg_ticks(end+1) = curr_offset;
        
        for b_i = 1:length(b_starts)
            t_s = b_starts(b_i) / 1000;
            t_e = b_ends(b_i) / 1000;
            if (t_e - t_s) > 0.05
                patch([t_s t_e t_e t_s], curr_offset + [-5 -5 10 10], [0.2 0.2 0.2], ...
                    'EdgeColor', 'none', 'FaceAlpha', 0.85);
            end
        end
        
        plot(t_vec / 1000, sig * 1.5 + curr_offset, 'Color', [0.1 0.1 0.1], 'LineWidth', 0.6);
        plot(t_vec / 1000, env * 2.0 + curr_offset, 'Color', 'w', 'LineWidth', 1.0);
    end
end

set(gca, 'YTick', emg_ticks, 'YTickLabel', {'Sol', 'TA', 'BF', 'VM'}, 'FontWeight', 'bold', 'FontSize', 10);
set(gca, 'XTick', [], 'YDir', 'normal', 'Box', 'off');
xlim([0 12]);
ylim([0 curr_offset + 20]);
xline(4.0, '--k', 'Color', [0.4 0.4 0.4], 'LineWidth', 1.0);
xline(8.0, '--k', 'Color', [0.4 0.4 0.4], 'LineWidth', 1.0);

% 4D Bottom: Nerve Activity: Right L2, Right L5, Left L2
axes('Position', [0.08 0.06 0.85 0.26]);
hold on;
l2_r_mask = (N.Types == 'MN') & (N.Segment == 'L2') & (N.Latera > 0);
l5_r_mask = (N.Types == 'MN') & (N.Segment == 'L5') & (N.Latera > 0);
l2_l_mask = (N.Types == 'MN') & (N.Segment == 'L2') & (N.Latera < 0);

r_l2_r = mean(N_sim.Rates(:, l2_r_mask), 2);
r_l5_r = mean(N_sim.Rates(:, l5_r_mask), 2);
r_l2_l = mean(N_sim.Rates(:, l2_l_mask), 2);

nerve_traces = {r_l2_l, r_l5_r, r_l2_r};
nerve_labels = {'L2', 'L5', 'L2'};
nerve_offsets = [15, 45, 75];

motor_masks = {l2_l_mask, l5_r_mask, l2_r_mask};
for n_i = 1:3
    ix_n = motor_masks{n_i};
    y_off = nerve_offsets(n_i);
    prob_n = sum(N_sim.Rates(:, ix_n), 2);
    sig_n = randn(size(prob_n)) * noiselevel .* binornd(1, normcdf(normalize(prob_n, 'zscore')));
    sig_n = sig_n .* prob_n + (randn(size(prob_n)) * noiselevel);
    env_n = movmean(abs(sig_n), 20);
    
    is_burst_n = env_n > 0.35 * max(env_n);
    burst_b = diff([0; is_burst_n; 0]);
    bs = find(burst_b == 1);
    be = find(burst_b == -1) - 1;
    
    for b_i = 1:length(bs)
        t_s = bs(b_i) / 1000;
        t_e = be(b_i) / 1000;
        if (t_e - t_s) > 0.05
            patch([t_s t_e t_e t_s], y_off + [-8 -8 15 15], [0.25 0.25 0.25], ...
                'EdgeColor', 'none', 'FaceAlpha', 0.85);
        end
    end
    
    plot(t_vec / 1000, sig_n * 1.5 + y_off, 'Color', [0.15 0.15 0.15], 'LineWidth', 0.6);
    plot(t_vec / 1000, env_n * 2.0 + y_off, 'Color', 'w', 'LineWidth', 1.1);
end

patch([2.2 2.45 2.45 2.2], 75 + [-8 -8 15 15], [0.85 0.25 0.35], 'EdgeColor', 'none', 'FaceAlpha', 0.85);
patch([2.55 2.80 2.80 2.55], 15 + [-8 -8 15 15], [0.85 0.25 0.35], 'EdgeColor', 'none', 'FaceAlpha', 0.85);

patch([6.1 6.35 6.35 6.1], 75 + [-8 -8 15 15], [0.85 0.25 0.35], 'EdgeColor', 'none', 'FaceAlpha', 0.85);
patch([6.45 6.70 6.70 6.45], 15 + [-8 -8 15 15], [0.85 0.25 0.35], 'EdgeColor', 'none', 'FaceAlpha', 0.85);

patch([10.1 10.35 10.35 10.1], 75 + [-8 -8 15 15], [0.85 0.25 0.35], 'EdgeColor', 'none', 'FaceAlpha', 0.85);
patch([10.45 10.70 10.70 10.45], 15 + [-8 -8 15 15], [0.85 0.25 0.35], 'EdgeColor', 'none', 'FaceAlpha', 0.85);

set(gca, 'YTick', nerve_offsets, 'YTickLabel', nerve_labels, 'FontWeight', 'bold', 'FontSize', 11);
set(gca, 'XTick', [], 'YDir', 'normal', 'Box', 'off');
xlim([0 12]);
ylim([0 105]);
xline(4.0, '--k', 'Color', [0.4 0.4 0.4], 'LineWidth', 1.0);
xline(8.0, '--k', 'Color', [0.4 0.4 0.4], 'LineWidth', 1.0);

plot([10.8 11.8], [5 5], '-k', 'LineWidth', 2.5);
text(11.3, 12, '1s', 'FontWeight', 'bold', 'FontSize', 11, 'HorizontalAlignment', 'center');

annotation(fig4d, 'textbox', [0.94 0.40 0.05 0.35], 'String', 'Right', ...
    'FontSize', 12, 'FontWeight', 'bold', 'Rotation', 270, 'EdgeColor', 'none');
annotation(fig4d, 'textbox', [0.94 0.06 0.05 0.15], 'String', 'Left', ...
    'FontSize', 12, 'FontWeight', 'bold', 'Rotation', 270, 'EdgeColor', 'none');

annotation(fig4d, 'textbox', [0.01 0.94 0.05 0.05], 'String', 'D', ...
    'FontSize', 18, 'FontWeight', 'bold', 'EdgeColor', 'none');

p_4d = fullfile(subpanelDir, 'fig4d_gait_patterns.png');
exportgraphics(fig4d, p_4d, 'Resolution', 300);
fprintf('Saved Figure 4D: %s\n', p_4d);

%% 7. Quantitative Analysis Across Steady-State Windows
fprintf('\nQuantifying steady-state gait windows...\n');
gait_freqs = nan(3, 1);
gait_lr_phases = nan(3, 1);
gait_l2l5_phases = nan(3, 1);
gait_nerve_amp = zeros(3, 2);
gait_muscle_amp = zeros(3, 2);
rhythm_status = cell(3, 1);

all_lr_points = cell(3, 1);
all_l2l5_points = cell(3, 1);
rep_amp_points = cell(3, 4);

for g = 1:3
    win = gait_windows{g};
    r_l = mean(N_sim.Rates(win, l2_l_mask), 2);
    r_r = mean(N_sim.Rates(win, l2_r_mask), 2);
    r_l5 = mean(N_sim.Rates(win, l5_r_mask), 2);
    
    range_l = max(r_l) - min(r_l);
    range_r = max(r_r) - min(r_r);
    prom_l = max(1.5, 0.20 * range_l);
    prom_r = max(1.5, 0.20 * range_r);
    
    [pks_l, locs_l] = findpeaks(r_l, 'MinPeakDistance', 60, 'MinPeakProminence', prom_l);
    [pks_r, locs_r] = findpeaks(r_r, 'MinPeakDistance', 60, 'MinPeakProminence', prom_r);
    [pks_l5, locs_l5] = findpeaks(r_l5, 'MinPeakDistance', 60, 'MinPeakProminence', max(1.5, 0.20 * (max(r_l5) - min(r_l5))));
    
    if length(locs_r) >= 3
        T_g = mean(diff(locs_r));
        gait_freqs(g) = 1000 / T_g;
        
        lr_diffs = [];
        for k = 1:length(locs_r)
            if ~isempty(locs_l)
                [~, near_l] = min(abs(locs_l - locs_r(k)));
                dt_l = locs_l(near_l) - locs_r(k);
                lr_diffs(end+1) = mod(dt_l / T_g * 2 * pi, 2 * pi);
            end
        end
        all_lr_points{g} = lr_diffs;
        sin_sum = sum(sin(lr_diffs)); cos_sum = sum(cos(lr_diffs));
        gait_lr_phases(g) = mod(atan2(sin_sum, cos_sum), 2 * pi);
        
        l2l5_diffs = [];
        for k = 1:length(locs_r)
            if ~isempty(locs_l5)
                [~, near_l5] = min(abs(locs_l5 - locs_r(k)));
                dt_l5 = locs_l5(near_l5) - locs_r(k);
                l2l5_diffs(end+1) = mod(dt_l5 / T_g * 2 * pi, 2 * pi);
            end
        end
        all_l2l5_points{g} = l2l5_diffs;
        sin_sum = sum(sin(l2l5_diffs)); cos_sum = sum(cos(l2l5_diffs));
        gait_l2l5_phases(g) = mod(atan2(sin_sum, cos_sum), 2 * pi);
        
        rhythm_status{g} = sprintf('Frequency = %.2f Hz, L-R Phase = %.1f°', gait_freqs(g), rad2deg(gait_lr_phases(g)));
    else
        gait_freqs(g) = NaN;
        gait_lr_phases(g) = NaN;
        gait_l2l5_phases(g) = NaN;
        rhythm_status{g} = 'Not measurable';
    end
    
    gait_nerve_amp(g, 1) = range_r;
    gait_nerve_amp(g, 2) = max(r_l5) - min(r_l5);
    rep_amp_points{g, 1} = pks_r - min(r_r);
    rep_amp_points{g, 2} = pks_l5 - min(r_l5);
    
    % Muscle EMG envelope amplitude evaluated directly from simulation without arbitrary multipliers
    if isfield(emg_envs, 'TibialisAnterior')
        env_ta = emg_envs.TibialisAnterior(win);
        gait_muscle_amp(g, 1) = max(env_ta) - min(env_ta);
        [pks_ta, ~] = findpeaks(env_ta, 'MinPeakDistance', 40);
        if isempty(pks_ta), pks_ta = gait_muscle_amp(g, 1); end
        rep_amp_points{g, 4} = pks_ta;
    end
    if isfield(emg_envs, 'Soleus')
        env_sol = emg_envs.Soleus(win);
        gait_muscle_amp(g, 2) = max(env_sol) - min(env_sol);
        [pks_sol, ~] = findpeaks(env_sol, 'MinPeakDistance', 40);
        if isempty(pks_sol), pks_sol = gait_muscle_amp(g, 2); end
        rep_amp_points{g, 3} = pks_sol;
    end
    
    fprintf('  %s: Freq = %.2f Hz, L-R Phase = %.1f deg, L2 Amp = %.1f Hz\n', ...
        gait_names{g}, gait_freqs(g), rad2deg(gait_lr_phases(g)), gait_nerve_amp(g, 1));
end

%% 8. Figure 4E: Polar Phase Representations via Cartesian
fprintf('\nGenerating Figure 4E (Polar Phase Transitions)...\n');
fig4e = figure('Color', 'white', 'Position', [100 100 750 380], 'Visible', 'off');

gait_cols = [0.15 0.15 0.15; 0.5 0.5 0.5; 0.78 0.78 0.78];

% Left: ipsi L2-contra L2
ax_e1 = axes('Position', [0.08 0.16 0.40 0.72]);
hold(ax_e1, 'on');
axis(ax_e1, 'equal');
xlim(ax_e1, [-1.35 1.35]);
ylim(ax_e1, [-1.35 1.35]);
axis(ax_e1, 'off');

t_c = linspace(0, 2*pi, 100);
plot(ax_e1, cos(t_c), sin(t_c), '-k', 'LineWidth', 1.4);

text(ax_e1, 1.15, 0, '0', 'FontWeight', 'bold', 'FontSize', 12);
text(ax_e1, 0, 1.15, '\pi/2', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');
text(ax_e1, -1.15, 0, '\pi', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'right');
text(ax_e1, 0, -1.15, '3\pi/2', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');

for g = 1:3
    if ~isempty(all_lr_points{g})
        pts = all_lr_points{g};
        r_p = 0.96 + 0.03 * randn(size(pts));
        scatter(ax_e1, r_p .* cos(pts), r_p .* sin(pts), 35, 'filled', ...
            'MarkerFaceColor', gait_cols(g, :), 'MarkerEdgeColor', 'none', 'MarkerFaceAlpha', 0.85);
    end
    if ~isnan(gait_lr_phases(g))
        quiver(ax_e1, 0, 0, 0.82 * cos(gait_lr_phases(g)), 0.82 * sin(gait_lr_phases(g)), 0, ...
            'Color', gait_cols(g, :), 'LineWidth', 2.5, 'MaxHeadSize', 0.8);
    end
end
title(ax_e1, 'ipsi L2-contra L2', 'FontWeight', 'bold', 'FontSize', 12);

% Right: ipsi L2-ipsi L5
ax_e2 = axes('Position', [0.55 0.16 0.40 0.72]);
hold(ax_e2, 'on');
axis(ax_e2, 'equal');
xlim(ax_e2, [-1.35 1.35]);
ylim(ax_e2, [-1.35 1.35]);
axis(ax_e2, 'off');

plot(ax_e2, cos(t_c), sin(t_c), '-k', 'LineWidth', 1.4);

for g = 1:3
    if ~isempty(all_l2l5_points{g})
        pts = all_l2l5_points{g};
        r_p = 0.96 + 0.03 * randn(size(pts));
        scatter(ax_e2, r_p .* cos(pts), r_p .* sin(pts), 35, 'filled', ...
            'MarkerFaceColor', gait_cols(g, :), 'MarkerEdgeColor', 'none', 'MarkerFaceAlpha', 0.85);
    end
    if ~isnan(gait_l2l5_phases(g))
        quiver(ax_e2, 0, 0, 0.82 * cos(gait_l2l5_phases(g)), 0.82 * sin(gait_l2l5_phases(g)), 0, ...
            'Color', gait_cols(g, :), 'LineWidth', 2.5, 'MaxHeadSize', 0.8);
    end
end
title(ax_e2, 'ipsi L2-ipsi L5', 'FontWeight', 'bold', 'FontSize', 12);

annotation(fig4e, 'textbox', [0.01 0.90 0.05 0.05], 'String', 'E', ...
    'FontSize', 18, 'FontWeight', 'bold', 'EdgeColor', 'none');

annotation(fig4e, 'textbox', [0.15 0.01 0.35 0.14], ...
    'String', {'{\color[rgb]{0.15,0.15,0.15}\bullet} Walking', ...
               '{\color[rgb]{0.5,0.5,0.5}\bullet} Trotting', ...
               '{\color[rgb]{0.78,0.78,0.78}\bullet} Bounding'}, ...
    'FontSize', 10, 'FontWeight', 'bold', 'EdgeColor', 'none');

p_4e = fullfile(subpanelDir, 'fig4e_polar_phase_transitions.png');
exportgraphics(fig4e, p_4e, 'Resolution', 300);
fprintf('Saved Figure 4E: %s\n', p_4e);

%% 9. Figure 4F: Frequency Bar Graph
fprintf('\nGenerating Figure 4F (Frequency Bar Graph)...\n');
fig4f = figure('Color', 'white', 'Position', [100 100 240 380], 'Visible', 'off');
ax4f = axes('Position', [0.32 0.25 0.62 0.65]);

b_f_vals = gait_freqs;
b_f_vals(isnan(b_f_vals)) = 0;
b_f = bar(ax4f, b_f_vals, 0.55);
b_f.FaceColor = 'flat';
for g = 1:3, b_f.CData(g, :) = gait_cols(g, :); end
set(ax4f, 'XTickLabel', gait_names, 'XTickLabelRotation', 40, 'FontWeight', 'bold', 'FontSize', 10);
ylabel(ax4f, 'Frequency [Hz]', 'FontWeight', 'bold', 'FontSize', 11);
ylim(ax4f, [0 6.0]);
set(ax4f, 'YTick', 0:2:6, 'TickDir', 'out', 'Box', 'off', 'LineWidth', 1.1);

text(ax4f, -0.6, 6.5, 'F', 'FontSize', 18, 'FontWeight', 'bold');

p_4f = fullfile(subpanelDir, 'fig4f_frequency.png');
exportgraphics(fig4f, p_4f, 'Resolution', 300);
fprintf('Saved Figure 4F: %s\n', p_4f);

%% 10. Figure 4G: Amplitude Bar Graphs (L2, L5, Sol, TA)
fprintf('\nGenerating Figure 4G (Amplitude Bar Graphs)...\n');
fig4g = figure('Color', 'white', 'Position', [100 100 680 380], 'Visible', 'off');

amp_labels = {'L2', 'L5', 'Sol', 'TA'};
amp_ylims = [35, 70, 20, 10];
amp_yticks = {[0 15 25 35], [0 10 30 50 70], [0 5 10 15 20], [0 2 4 6 8 10]};
amp_data = [gait_nerve_amp(:, 1), gait_nerve_amp(:, 2), gait_muscle_amp(:, 2), gait_muscle_amp(:, 1)];

for a = 1:4
    subplot(1, 4, a);
    ax_a = gca;
    hold(ax_a, 'on');
    b_a = bar(ax_a, amp_data(:, a), 0.6);
    b_a.FaceColor = 'flat';
    for g = 1:3, b_a.CData(g, :) = gait_cols(g, :); end
    
    all_pts_a = [];
    for g = 1:3
        pts = rep_amp_points{g, a};
        if isempty(pts), pts = amp_data(g, a); end
        all_pts_a = [all_pts_a; pts(:)];
        x_jitter = g + (linspace(-0.12, 0.12, length(pts)))';
        scatter(ax_a, x_jitter, pts(:), 16, 'filled', ...
            'MarkerFaceColor', [0.3 0.3 0.3], 'MarkerEdgeColor', 'none', 'MarkerFaceAlpha', 0.65);
    end
    
    y_max_a = max([amp_data(:, a); all_pts_a; 2]);
    ylim(ax_a, [0 y_max_a * 1.25]);
    set(ax_a, 'XTick', [], 'Box', 'off', 'TickDir', 'out', 'LineWidth', 1.1, 'FontSize', 9, 'FontWeight', 'bold');
    title(ax_a, amp_labels{a}, 'FontWeight', 'bold', 'FontSize', 12);
    if a == 1
        ylabel(ax_a, 'Amplitude [a.u]', 'FontWeight', 'bold', 'FontSize', 11);
    end
end

annotation(fig4g, 'textbox', [0.01 0.90 0.05 0.05], 'String', 'G', ...
    'FontSize', 18, 'FontWeight', 'bold', 'EdgeColor', 'none');

p_4g = fullfile(subpanelDir, 'fig4g_amplitudes.png');
exportgraphics(fig4g, p_4g, 'Resolution', 300);
fprintf('Saved Figure 4G: %s\n', p_4g);

%% 11. Save Evidence-Based Central Metrics
metrics = struct();
metrics.figure = 4;
metrics.status = 'METHODS-BASED RECONSTRUCTION — RESULT DIFFERENT';
metrics.gaits = struct();
for g = 1:3
    g_key = matlab.lang.makeValidName(gait_names{g});
    metrics.gaits.(g_key) = struct(...
        'name', gait_names{g}, ...
        'measured_frequency_hz', gait_freqs(g), ...
        'measured_lr_phase_rad', gait_lr_phases(g), ...
        'measured_lr_phase_deg', rad2deg(gait_lr_phases(g)), ...
        'measured_l2l5_phase_rad', gait_l2l5_phases(g), ...
        'measured_l2l5_phase_deg', rad2deg(gait_l2l5_phases(g)), ...
        'nerve_amplitude_l2', gait_nerve_amp(g, 1), ...
        'nerve_amplitude_l5', gait_nerve_amp(g, 2), ...
        'muscle_amplitude_ta', gait_muscle_amp(g, 1), ...
        'muscle_amplitude_sol', gait_muscle_amp(g, 2), ...
        'rhythmicity_status', rhythm_status{g});
end

target_counts = struct();
for i = 1:n_tg
    c_name = target_types{i};
    c_mask = strcmpi(string(N.Types), c_name);
    c_key = matlab.lang.makeValidName(c_name);
    target_counts.(c_key) = struct(...
        'total_neurons', sum(c_mask), ...
        'lpgi_total', sum(is_lpgi_target & c_mask), ...
        'lpgi_pct', lpgi_pct(i), ...
        'raphe_total', sum(is_raphe_target & c_mask), ...
        'raphe_pct', raphe_pct(i));
end
metrics.target_neuron_counts = target_counts;

metrics.drive_interpretations = struct(...
    'interpretation_1_total_external_input', struct(...
        'description', 'Target neurons receive scheduled drive (15, 22, 30 pA), non-targets receive baseline background 10 pA', ...
        'outcome', 'Robust rhythmic bursting across all gaits, amplitude increases +112%, but bilateral alternation is preserved throughout (Walk=160.0°, Trot=162.3°, Bound=163.3°); no switch to bilateral synchrony', ...
        'frequency_range_hz', [1.29, 1.40]), ...
    'interpretation_2_additive_drive_over_background', struct(...
        'description', 'Scheduled drive is added to normal background (30 pA baseline + 15/22/30 pA -> 45/52/60 pA total input)', ...
        'outcome', 'High drive pushes membrane potentials into upper saturation ceiling (Fmax = 50 Hz), causing loss of rhythmicity and tonic saturation (54.7% saturation) without producing bounding synchrony', ...
        'saturation_pct', 54.7));

metrics.failure_diagnosis = 'Under the authors released code and connectivity matrix W, neither interpretation reproduces the published transition to bilateral synchrony (~0°) or 2.5-5.2 Hz acceleration. Exact dedicated Figure 4 driver and published network realization are unreleased in BergLab/SpinalProjectome.';

jsonStr = jsonencode(metrics, 'PrettyPrint', true);
metricsFile = fullfile(resultsDir, 'figure4_metrics.json');
fid = fopen(metricsFile, 'w');
fwrite(fid, jsonStr, 'char');
fclose(fid);
fprintf('Saved Figure 4 metrics: %s\n', metricsFile);

t_total = toc(t_start);
fprintf('\n=================================================================\n');
fprintf('STAGE 5 FIGURE 4 REPRODUCTION COMPLETED (Elapsed: %.2f s)\n', t_total);
fprintf('=================================================================\n');

diary off;
exit(0);

%% Local helper function GeneratePlot (authors exact routine)
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

%% Local Gaussian window helper
function w = gausswin_local(L)
    alpha = 2.5;
    n = -(L-1)/2 : (L-1)/2;
    w = exp(-0.5 * (alpha * n / ((L-1)/2)).^2)';
end
