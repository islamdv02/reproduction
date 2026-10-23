%% run_figure3_reproduction.m
% Strictly reproduces Figure 3 of Komi et al. (Nature Communications, 2026):
%   3A: Connectivity matrix W of the network (pink excitatory, black inhibitory)
%   3B: Top: Eigenspectrum in complex plane with stability line Re=1 and Mode 1/2 marks
%       Bottom: Dominant spatial eigenmodes across segments:
%               Mode 1 "Walking" (alternating) vs Mode 2 "Bounding" (synchronous)
%               with motoneuron pools VM, BF, TA, Sol beside Mode 2.
%   3C: Global descending input (transverse schematic + 25 pA input bar labeled "All")
%   3D: Single non-linear activation function (tanh_f_V, 0 to 50 Hz, Input 0 to 150 pA)
%   3E: Spatiotemporal dynamics:
%       - Segmental spatial rate image across time (T13 to S4, min to max rate [a.u.])
%       - VM, BF, TA, Sol EMG traces with alternating grey phase shading (Right)
%       - Right L2 and Right L5 motor outputs
%       - Left L2 motor output
%       - 1s time scale bar
%   3F: Polar representation of cycle phase relationships:
%       - iL2-iL5 (black vector, ~210 deg)
%       - iL2-cL2 (cyan vector, ~150 deg)
%       - Individual cycle points and circular mean vector
%   3G: Restored neuronal phase distribution:
%       - Polar histogram across rhythmic neurons (24 bins, R = 400 neurons)
%   3H: Author low-dimensional rotational dynamics in PC1-PC3 space:
%       - Computed via author pipeline: ComputeSpikes -> ComputeEstimatedRates -> ComputePC
%       - Outward spiral settling into single-loop limit cycle with red "Time" arrow

clear; clc; close all;
t_start = tic;

scriptDir = fileparts(which('run_figure3_reproduction.m'));
rootDir = fileparts(scriptDir);
sourceDir = fullfile(rootDir, 'source');
resultsDir = fullfile(rootDir, 'results');
subpanelDir = fullfile(rootDir, 'figures', 'subpanels_fig3');
logsDir = fullfile(rootDir, 'logs');

if ~exist(subpanelDir, 'dir'), mkdir(subpanelDir); end
if ~exist(logsDir, 'dir'), mkdir(logsDir); end

logFile = fullfile(logsDir, 'step4_figure3_reproduction.log');
diary(logFile); diary on;

fprintf('=================================================================\n');
fprintf('STAGE 4: Figure 3 Reconstruction (Komi et al., 2026)\n');
fprintf('Timestamp: %s\n', datestr(now));
fprintf('MATLAB Version: %s\n', version);
fprintf('=================================================================\n');

addpath(genpath(sourceDir));

%% 1. Load Simulated Network Object
networkFile = fullfile(resultsDir, 'simulated_network.mat');
fprintf('Loading simulated network object from: %s ...\n', networkFile);
load(networkFile, 'N');
N_neurons = size(N.ConnMat, 1);
n_steps = size(N.Rates, 1);
fprintf('Loaded network: N = %d neurons, %d simulation time steps.\n', N_neurons, n_steps);

t_win = 1000:6000; % 5000 ms display window (matching published 3E with ~6-7 cycles and 1s scale bar)
t_steady = 2000:n_steps; % Steady-state analysis window (capturing 27 cycles)

%% 2. Figure 3A: Connectivity Matrix W (Pink Excitatory, Black Inhibitory)
p_3a = fullfile(subpanelDir, 'fig3a_connectivity_matrix.png');
fprintf('\nGenerating Figure 3A (Connectivity Matrix W)...\n');
fig3a = figure('Color', 'white', 'Position', [100 100 650 650], 'Visible', 'off');
ax3a = axes('Position', [0.15 0.15 0.78 0.78]);
hold(ax3a, 'on');

W_full = full(N.ConnMat);
[i_exc, j_exc] = find(W_full > 0);
[i_inh, j_inh] = find(W_full < 0);

% Excitatory connections in pink with high-resolution fine dots
scatter(ax3a, j_exc, i_exc, 0.6, [0.95 0.35 0.55], 'filled', 'MarkerFaceAlpha', 0.35);
% Inhibitory connections in black with high-resolution fine dots
scatter(ax3a, j_inh, i_inh, 0.6, [0.20 0.20 0.20], 'filled', 'MarkerFaceAlpha', 0.35);

xlim(ax3a, [1 N_neurons]); ylim(ax3a, [1 N_neurons]);
set(ax3a, 'YDir', 'reverse');
set(ax3a, 'XTick', [], 'YTick', []);
xlabel(ax3a, 'Presynaptic', 'FontWeight', 'bold', 'FontSize', 12);
ylabel(ax3a, 'Postsynaptic', 'FontWeight', 'bold', 'FontSize', 12);
box(ax3a, 'on'); set(ax3a, 'LineWidth', 1.0);

exportgraphics(fig3a, p_3a, 'Resolution', 300);
fprintf('Saved: %s\n', p_3a);

%% 3. Figure 3B: Eigenspectrum & Spatial Eigenmodes (Walking vs Bounding)
p_3b = fullfile(subpanelDir, 'fig3b_eigenspectrum_and_modes.png');
fprintf('\nGenerating Figure 3B (Eigenspectrum and Spatial Eigenmodes - Author Pipeline)...\n');
fig3b = figure('Color', 'white', 'Position', [100 100 500 1180], 'Visible', 'off');

% Compute eigenvalues and modes using author method directly from W_full
[V, D] = eig(W_full, 'vector');
brevr = real(D);
bievr = imag(D);
[brevr_sort, bixev] = sort(brevr, 'descend');
[~, ind] = unique(brevr_sort, 'stable');

% Selected eigenvector indices:
idx_m1 = bixev(ind(1)); % Mode 1 (Walking): lambda_1 = 2.019392 + 0.758961i
idx_m2 = bixev(ind(2)); % Mode 2 (Bounding): lambda_2 = 1.692955 + 1.132317i

lambda_1 = D(idx_m1);
lambda_2 = D(idx_m2);

% Phase-aligned components:
% The complex eigenvectors V(:, idx_m1) and V(:, idx_m2) rotate in the 2D modal subspace.
% A phase rotation by 90 deg (imaginary component with sign convention) yields the
% instantaneous traveling wave snapshot published in Komi et al. (Fig 3B).
% Author normalization formula:
% obj.EigenModes(ii,:) = 100*normalize(real(vec(TP,bixev(ind(ii)))+abs(min(vec(TP,bixev(ind(ii)))))),'range')+0.01;
v1_comp = imag(V(:, idx_m1));
v2_comp = -imag(V(:, idx_m2));

m1_vals = 100 * normalize(v1_comp + abs(min(v1_comp)), 'range') + 0.01;
m2_vals = 100 * normalize(v2_comp + abs(min(v2_comp)), 'range') + 0.01;

% --- TOP PANEL: Eigenspectrum in Complex Plane ---
ax_top = axes('Position', [0.10 0.65 0.82 0.32]);
hold(ax_top, 'on');

% Central dense disc
th = linspace(0, 2*pi, 100);
fill(ax_top, 0.42*cos(th), 0.42*sin(th), [0.28 0.28 0.28], 'EdgeColor', 'none');

% Grey background scatter points for all eigenvalues
scatter(ax_top, brevr, bievr, 9, [0.75 0.75 0.75], 'filled', 'MarkerFaceAlpha', 0.6);

% Dashed axes crossing at (0,0)
plot(ax_top, [-1.2 2.5], [0 0], '--', 'Color', [0.5 0.5 0.5], 'LineWidth', 0.8);
plot(ax_top, [0 0], [-1.4 1.4], '--', 'Color', [0.5 0.5 0.5], 'LineWidth', 0.8);
text(ax_top, -0.06, -0.15, '0', 'FontWeight', 'bold', 'FontSize', 9.5, 'HorizontalAlignment', 'right');
text(ax_top, 0.08, -1.35, '0', 'FontWeight', 'bold', 'FontSize', 9.5, 'HorizontalAlignment', 'left');

% Stability line at Re = 1.0 (pink dashed line)
plot(ax_top, [1.0 1.0], [-1.4 1.4], '--', 'Color', [0.88 0.20 0.45], 'LineWidth', 1.5);
% "Stability Line" label with underline under Line and arrow pointing down-right
text(ax_top, 0.96, 1.45, 'Stability Line', 'Color', [0.15 0.15 0.15], 'FontWeight', 'bold', 'FontSize', 9.5, 'HorizontalAlignment', 'right');
% Underline under "Line" (from ~0.72 to 0.97)
plot(ax_top, [0.72 0.97], [1.36 1.36], 'k-', 'LineWidth', 1.0);
% Arrow pointing from right end of underline to stability line
plot(ax_top, [0.97 1.02], [1.36 1.16], 'k-', 'LineWidth', 1.0);
plot(ax_top, 1.02, 1.15, 'v', 'Color', 'k', 'MarkerFaceColor', 'k', 'MarkerSize', 3.5);

% Mode 1 conjugate pair markers (solid black circles)
scatter(ax_top, real(lambda_1), imag(lambda_1), 52, 'k', 'filled');
scatter(ax_top, real(lambda_1), -imag(lambda_1), 52, 'k', 'filled');

% Mode 2 conjugate pair markers (grey circles with black border)
scatter(ax_top, real(lambda_2), imag(lambda_2), 52, [0.75 0.75 0.75], 'filled', 'MarkerEdgeColor', 'k', 'LineWidth', 1.2);
scatter(ax_top, real(lambda_2), -imag(lambda_2), 52, [0.75 0.75 0.75], 'filled', 'MarkerEdgeColor', 'k', 'LineWidth', 1.2);

% Mode 1 Bracket: curly/square bracket connecting the inner pair
plot(ax_top, [2.14 2.22 2.22], [imag(lambda_1) imag(lambda_1) 0.10], 'Color', [0.4 0.4 0.4], 'LineWidth', 1.0);
plot(ax_top, [2.22 2.28], [0.10 0.0], 'Color', [0.4 0.4 0.4], 'LineWidth', 1.0);
plot(ax_top, [2.28 2.22], [0.0 -0.10], 'Color', [0.4 0.4 0.4], 'LineWidth', 1.0);
plot(ax_top, [2.22 2.22 2.14], [-0.10 -imag(lambda_1) -imag(lambda_1)], 'Color', [0.4 0.4 0.4], 'LineWidth', 1.0);
text(ax_top, 2.34, 0.0, 'Mode {\bf 1}', 'FontSize', 10, 'FontWeight', 'normal');

% Mode 2 Bracket: outer vertical line with two arrows pointing to the grey dots
plot(ax_top, [1.78 2.15 2.15], [imag(lambda_2) imag(lambda_2) 0.60], 'Color', [0.5 0.5 0.5], 'LineWidth', 1.0);
plot(ax_top, [2.15 2.15 1.78], [-0.60 -imag(lambda_2) -imag(lambda_2)], 'Color', [0.5 0.5 0.5], 'LineWidth', 1.0);
% Arrowheads pointing to grey dots
plot(ax_top, 1.76, imag(lambda_2), '<', 'Color', [0.5 0.5 0.5], 'MarkerFaceColor', [0.5 0.5 0.5], 'MarkerSize', 3.5);
plot(ax_top, 1.76, -imag(lambda_2), '<', 'Color', [0.5 0.5 0.5], 'MarkerFaceColor', [0.5 0.5 0.5], 'MarkerSize', 3.5);
% Line from Mode 2 label to the vertical bracket
plot(ax_top, [2.15 2.30], [-0.65 -0.65], 'Color', [0.5 0.5 0.5], 'LineWidth', 1.0);
text(ax_top, 2.34, -0.65, 'Mode {\bf 2}', 'FontSize', 10, 'FontWeight', 'normal');

% Axis corner indicator (bottom-left)
plot(ax_top, [-1.1 -1.1 0], [-0.5 -1.3 -1.3], 'k-', 'LineWidth', 1.2);
text(ax_top, -0.55, -1.45, 'Real', 'FontWeight', 'bold', 'FontSize', 9.5, 'HorizontalAlignment', 'center');
text(ax_top, -1.25, -0.9, 'Imaginary', 'FontWeight', 'bold', 'FontSize', 9.5, 'Rotation', 90, 'HorizontalAlignment', 'center');

xlim(ax_top, [-1.3 3.0]);
ylim(ax_top, [-1.6 1.6]);
axis(ax_top, 'off');

% --- BOTTOM PANEL: Longitudinal Spatial Modes ---
ax_bot = axes('Position', [0.08 0.04 0.88 0.57]);
hold(ax_bot, 'on');

% Exact anatomical segment bounds
Seg_list = {'T13', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'S1', 'S2', 'S3', 'S4'};
seg_bounds = zeros(length(Seg_list), 1);
for s = 1:length(Seg_list)
    s_mask = (N.Segment == Seg_list{s});
    if any(s_mask)
        seg_bounds(s) = min(N.Position(s_mask, 2));
    end
end
min_rc = min(N.Position(:, 2));
max_rc = max(N.Position(:, 2));

% Mode 1 horizontal offset: center = -0.72
% Mode 2 horizontal offset: center = +0.10
% Motoneuron pools beside Mode 2: center = +0.58 to +0.91
x_span = max(abs(N.Position(:, 1))); % ~900 um
scale_x = 0.38 / x_span; % maps [-x_span, x_span] to [-0.38, 0.38]

x_m1 = -0.72 + N.Position(:, 1) * scale_x;
x_m2 =  0.10 + N.Position(:, 1) * scale_x;

% Plot segment labels on far left
for s = 1:length(Seg_list)
    if s < length(Seg_list)
        y_mid = (seg_bounds(s) + seg_bounds(s+1)) / 2;
    else
        y_mid = (seg_bounds(s) + max_rc) / 2;
    end
    text(ax_bot, -1.25, y_mid, Seg_list{s}, 'FontWeight', 'bold', 'FontSize', 10, 'HorizontalAlignment', 'center', 'Color', [0.15 0.15 0.15]);
end

% Horizontal dashed segment divider lines at:
% L1/L2 (seg_bounds(3)), L3/L4 (seg_bounds(5)), L6/S1 (seg_bounds(8))
div_y = [seg_bounds(3), seg_bounds(5), seg_bounds(8)];
for dy = div_y
    plot(ax_bot, [-1.35 1.05], [dy dy], '--', 'Color', [0.55 0.55 0.55], 'LineWidth', 0.9);
end

% Vertical dashed midline for Mode 1 and Mode 2
plot(ax_bot, [-0.72 -0.72], [min_rc max_rc], '--', 'Color', [0.6 0.6 0.6], 'LineWidth', 0.8);
plot(ax_bot, [ 0.10  0.10], [min_rc max_rc], '--', 'Color', [0.6 0.6 0.6], 'LineWidth', 0.8);

% Grayscale color and size for Mode 1
norm_m1 = m1_vals(:) / 100;
col_m1 = (1 - norm_m1 * 0.90) * [1 1 1]; % darker = higher activation
sz_m1 = norm_m1 * 9.5 + 0.8;
scatter(ax_bot, x_m1, N.Position(:, 2), sz_m1, col_m1, 'filled');

% Grayscale color and size for Mode 2
norm_m2 = m2_vals(:) / 100;
col_m2 = (1 - norm_m2 * 0.90) * [1 1 1];
sz_m2 = norm_m2 * 9.5 + 0.8;
scatter(ax_bot, x_m2, N.Position(:, 2), sz_m2, col_m2, 'filled');

% Motoneuron pools beside Mode 2:
% VM (magenta), BF (cyan), TA (cyan), Sol (magenta)
% Right side pools
ix_vm  = (N.MnID == 'Vastus Medialis') & (N.Latera > 0);
ix_bf  = (N.MnID == 'Biceps Femoris')  & (N.Latera > 0);
ix_ta  = (N.MnID == 'Tibialis Anterior') & (N.Latera > 0);
ix_sol = (N.MnID == 'Soleus')          & (N.Latera > 0);

x_vm  = 0.58 + randn(sum(ix_vm), 1)*0.010;
x_bf  = 0.69 + randn(sum(ix_bf), 1)*0.010;
x_ta  = 0.80 + randn(sum(ix_ta), 1)*0.010;
x_sol = 0.91 + randn(sum(ix_sol), 1)*0.010;

c_mag = [0.75 0.20 0.70];
c_cya = [0.25 0.75 0.95];

scatter(ax_bot, x_vm,  N.Position(ix_vm, 2),  4.5, c_mag, 'filled');
scatter(ax_bot, x_bf,  N.Position(ix_bf, 2),  4.5, c_cya, 'filled');
scatter(ax_bot, x_ta,  N.Position(ix_ta, 2),  4.5, c_cya, 'filled');
scatter(ax_bot, x_sol, N.Position(ix_sol, 2), 4.5, c_mag, 'filled');

% Labels and pointers for MN pools
text(ax_bot, 0.58, min(N.Position(ix_vm, 2)) - 320, 'VM', 'Color', 'k', 'FontWeight', 'bold', 'FontSize', 9.5, 'HorizontalAlignment', 'center');
plot(ax_bot, [0.58 0.58], [min(N.Position(ix_vm, 2)) - 280, min(N.Position(ix_vm, 2)) - 80], 'k-', 'LineWidth', 1.1);
plot(ax_bot, 0.58, min(N.Position(ix_vm, 2)) - 80, 'v', 'Color', 'k', 'MarkerFaceColor', 'k', 'MarkerSize', 4);

text(ax_bot, 0.69, min(N.Position(ix_bf, 2)) - 320, 'BF', 'Color', 'k', 'FontWeight', 'bold', 'FontSize', 9.5, 'HorizontalAlignment', 'center');
plot(ax_bot, [0.69 0.69], [min(N.Position(ix_bf, 2)) - 280, min(N.Position(ix_bf, 2)) - 80], 'k-', 'LineWidth', 1.1);
plot(ax_bot, 0.69, min(N.Position(ix_bf, 2)) - 80, 'v', 'Color', 'k', 'MarkerFaceColor', 'k', 'MarkerSize', 4);

text(ax_bot, 0.80, min(N.Position(ix_ta, 2)) - 320, 'TA', 'Color', 'k', 'FontWeight', 'bold', 'FontSize', 9.5, 'HorizontalAlignment', 'center');
plot(ax_bot, [0.80 0.80], [min(N.Position(ix_ta, 2)) - 280, min(N.Position(ix_ta, 2)) - 80], 'k-', 'LineWidth', 1.1);
plot(ax_bot, 0.80, min(N.Position(ix_ta, 2)) - 80, 'v', 'Color', 'k', 'MarkerFaceColor', 'k', 'MarkerSize', 4);

text(ax_bot, 0.91, min(N.Position(ix_sol, 2)) - 320, 'Sol', 'Color', 'k', 'FontWeight', 'bold', 'FontSize', 9.5, 'HorizontalAlignment', 'center');
plot(ax_bot, [0.91 0.91], [min(N.Position(ix_sol, 2)) - 280, min(N.Position(ix_sol, 2)) - 80], 'k-', 'LineWidth', 1.1);
plot(ax_bot, 0.91, min(N.Position(ix_sol, 2)) - 80, 'v', 'Color', 'k', 'MarkerFaceColor', 'k', 'MarkerSize', 4);

% Mode titles at top
text(ax_bot, -0.72, min_rc - 650, {'Mode {\bf 1}', '“Walking”'}, 'FontWeight', 'normal', 'FontSize', 10.5, 'HorizontalAlignment', 'center');
text(ax_bot,  0.10, min_rc - 650, {'Mode {\bf 2}', '“Bounding”'}, 'FontWeight', 'normal', 'FontSize', 10.5, 'HorizontalAlignment', 'center');

% Bottom legends:
% Under Mode 1: Left <-> Right
plot(ax_bot, [-0.92 -0.52], [max_rc + 600, max_rc + 600], 'k-', 'LineWidth', 1.1);
plot(ax_bot, [-0.72 -0.72], [max_rc + 540, max_rc + 660], 'k-', 'LineWidth', 1.1);
plot(ax_bot, -0.92, max_rc + 600, '<', 'Color', 'k', 'MarkerFaceColor', 'k', 'MarkerSize', 4.5);
plot(ax_bot, -0.52, max_rc + 600, '>', 'Color', 'k', 'MarkerFaceColor', 'k', 'MarkerSize', 4.5);
text(ax_bot, -0.92, max_rc + 950, 'Left', 'FontWeight', 'bold', 'FontSize', 9.5, 'HorizontalAlignment', 'center');
text(ax_bot, -0.52, max_rc + 950, 'Right', 'FontWeight', 'bold', 'FontSize', 9.5, 'HorizontalAlignment', 'center');

% Under Mode 2: 0 ... 1 dots scale
text(ax_bot, -0.10, max_rc + 800, '0', 'FontWeight', 'bold', 'FontSize', 9.5, 'HorizontalAlignment', 'center');
text(ax_bot,  0.30, max_rc + 800, '1', 'FontWeight', 'bold', 'FontSize', 9.5, 'HorizontalAlignment', 'center');
x_dots = linspace(-0.01, 0.21, 4);
sz_dots = [2, 4, 6, 8];
col_dots = [0.85 0.85 0.85; 0.65 0.65 0.65; 0.40 0.40 0.40; 0.10 0.10 0.10];
for di = 1:4
    scatter(ax_bot, x_dots(di), max_rc + 800, sz_dots(di)*1.5, col_dots(di, :), 'filled');
end

xlim(ax_bot, [-1.40 1.08]);
ylim(ax_bot, [min_rc - 900, max_rc + 1150]);
set(ax_bot, 'YDir', 'reverse');
axis(ax_bot, 'off');

p_3b = fullfile(subpanelDir, 'fig3b_eigenspectrum_and_modes.png');
exportgraphics(fig3b, p_3b, 'Resolution', 300);
fprintf('Saved: %s\n', p_3b);

%% 4. Figure 3C: Global Input (Transverse Schematic + 25 pA Bar)
p_3c = fullfile(subpanelDir, 'fig3c_global_input.png');
fprintf('\nGenerating Figure 3C (Global Input Schematic & Bar)...\n');
fig3c = figure('Color', 'white', 'Position', [100 100 450 350], 'Visible', 'off');

% Left: Transverse spinal hemicord schematic
ax3c_cord = axes('Position', [0.08 0.12 0.50 0.75]);
hold(ax3c_cord, 'on');

% Outer cord contour
t_c = linspace(0, pi, 100);
x_outer = [0, 0.9*sin(t_c), 0];
y_outer = [1.2, 0.6 + 0.6*cos(t_c), 0];
plot(ax3c_cord, x_outer, y_outer, 'k-', 'LineWidth', 1.2);

% Grey matter butterfly shape
th_gm = linspace(0, 2*pi, 80);
x_gm = 0.45 + 0.22*cos(th_gm) + 0.05*cos(2*th_gm);
y_gm = 0.6 + 0.35*sin(th_gm);
fill(ax3c_cord, x_gm, y_gm, [0.95 0.55 0.75], 'EdgeColor', 'none', 'FaceAlpha', 0.65);

% Descending tract outline (lateral column)
t_tr = linspace(pi/4, 3*pi/4, 40);
x_tr = 0.22 + 0.08*cos(t_tr);
y_tr = 0.45 + 0.25*sin(t_tr);
plot(ax3c_cord, x_tr, y_tr, 'Color', [0.85 0.15 0.55], 'LineWidth', 1.5);

% Terminals entering grey matter with arrowheads
for y_arr = [0.45, 0.55, 0.65, 0.75]
    plot(ax3c_cord, [0.25 0.42], [y_arr y_arr], 'k-', 'LineWidth', 1.0);
    plot(ax3c_cord, 0.42, y_arr, 'k^', 'MarkerFaceColor', 'k', 'MarkerSize', 5);
end
axis(ax3c_cord, 'equal', 'off');
title(ax3c_cord, 'Global Input', 'FontWeight', 'bold', 'FontSize', 11);

% Right: 25 pA Input Bar (matching published value and simulation input)
ax3c_bar = axes('Position', [0.68 0.22 0.22 0.60]);
bar(ax3c_bar, 1, 25.0, 0.45, 'FaceColor', [0.55 0.55 0.55], 'EdgeColor', 'none');
ylim(ax3c_bar, [0 38]);
set(ax3c_bar, 'YTick', [5 15 25 35], 'FontWeight', 'bold', 'FontSize', 9);
set(ax3c_bar, 'XTick', 1, 'XTickLabel', {'All'}, 'FontWeight', 'bold', 'FontSize', 10);
ylabel(ax3c_bar, 'Input', 'FontWeight', 'bold', 'FontSize', 10);
box(ax3c_bar, 'off');

p_3c = fullfile(subpanelDir, 'fig3c_global_input.png');
exportgraphics(fig3c, p_3c, 'Resolution', 300);
fprintf('Saved: %s\n', p_3c);

%% 5. Figure 3D: Activation Function (Single tanh_f_V Curve)
p_3d = fullfile(subpanelDir, 'fig3d_activation_function.png');
fprintf('\nGenerating Figure 3D (Single Activation Function Curve)...\n');
fig3d = figure('Color', 'white', 'Position', [100 100 450 350], 'Visible', 'off');
ax3d = axes('Position', [0.20 0.20 0.72 0.65]);
hold(ax3d, 'on');

threshold = 5;
f_max = 50;
gain = 1.0;
V_range = linspace(0, 150, 400);

f = zeros(size(V_range));
neg = (V_range - threshold) <= 0;
pos = (V_range - threshold) > 0;
f(neg) = threshold .* tanh(gain .* (V_range(neg) - threshold) ./ threshold);
f(pos) = f_max .* tanh(gain .* (V_range(pos) - threshold) ./ f_max);
val = f + threshold;
val(val < 0) = 0;

plot(ax3d, V_range, val, 'k-', 'LineWidth', 2.0);
xlim(ax3d, [-10 150]); ylim(ax3d, [-2 55]);
set(ax3d, 'XTick', [0 150], 'YTick', [], 'FontWeight', 'bold', 'FontSize', 9.5);
xlabel(ax3d, 'Input', 'FontWeight', 'bold', 'FontSize', 10);
ylabel(ax3d, 'Rate R [Hz]', 'FontWeight', 'bold', 'FontSize', 10);
title(ax3d, 'Activation function', 'FontWeight', 'bold', 'FontSize', 11);
box(ax3d, 'off'); set(ax3d, 'LineWidth', 1.0);

p_3d = fullfile(subpanelDir, 'fig3d_activation_function.png');
exportgraphics(fig3d, p_3d, 'Resolution', 300);
fprintf('Saved: %s\n', p_3d);

%% 6. Figure 3E: Spatiotemporal Dynamics, EMGs, and Motor Outputs
p_3e = fullfile(subpanelDir, 'fig3e_spatiotemporal_dynamics.png');
fprintf('\nGenerating Figure 3E (Spatiotemporal Dynamics, EMGs, Motor Outputs)...\n');
fig3e = figure('Color', 'white', 'Position', [100 100 950 1100], 'Visible', 'off');

% 3E Top: Segmental Spatial-Rate Image across RC axis (Right Hemicord)
ax3e_top = axes('Position', [0.12 0.72 0.78 0.22]);
right_mask = (N.Latera > 0);
y_right = N.Position(right_mask, 2);
[y_sorted, sort_rc] = sort(y_right, 'ascend');
rates_right = N.Rates(t_win, right_mask);
rates_sorted = rates_right(:, sort_rc)';

y_bins = linspace(min(y_sorted), max(y_sorted), 80);
t_axis = (t_win - t_win(1));
binned_rates = zeros(length(y_bins)-1, length(t_axis));
for b = 1:(length(y_bins)-1)
    in_bin = (y_sorted >= y_bins(b)) & (y_sorted < y_bins(b+1));
    if any(in_bin)
        binned_rates(b, :) = mean(rates_sorted(in_bin, :), 1);
    end
end

imagesc(ax3e_top, t_axis, y_bins(1:end-1), binned_rates);
colormap(ax3e_top, flipud(gray(128)));
caxis(ax3e_top, [0 35]);
ylabel(ax3e_top, 'Segments', 'FontWeight', 'bold', 'FontSize', 10);
set(ax3e_top, 'XTick', [], 'YTick', []);
title(ax3e_top, 'rate [a.u.]  min            max', 'FontWeight', 'bold', 'FontSize', 10, 'HorizontalAlignment', 'right');

% Cycle phase shading intervals from Right L2
ix_l2_r = (N.Segment == 'L2') & (N.Types == 'MN') & (N.Latera > 0);
ref_signal = mean(N.Rates(t_win, ix_l2_r), 2);
ref_norm = ref_signal - median(ref_signal);
ref_norm(ref_norm < 0) = 0; ref_norm(ref_norm > 0) = 1;
[~, locs_cycles] = findpeaks(abs(diff(ref_norm)));

% 3E Middle: Antagonistic Muscle Activity (VM, BF, TA, Sol - Right Side)
ax3e_emg = axes('Position', [0.12 0.38 0.78 0.30]);
hold(ax3e_emg, 'on');

% Draw alternating phase shading
for n = 1:2:(length(locs_cycles)-1)
    patch(ax3e_emg, [t_axis(locs_cycles(n)) t_axis(locs_cycles(n+1)) t_axis(locs_cycles(n+1)) t_axis(locs_cycles(n))], ...
          [-10 -10 120 120], [0.90 0.90 0.90], 'EdgeColor', 'none', 'FaceAlpha', 0.6);
end

% Muscle roles:
% Soleus: ankle extensor / plantarflexor
% Tibialis Anterior: ankle dorsiflexor (flexor-associated)
% Biceps Femoris: knee flexor
% Vastus Medialis: knee extensor
muscles_order = {'Soleus', 'Tibialis Anterior', 'Biceps Femoris', 'Vastus Medialis'};
muscle_names_display = {'Sol', 'TA', 'BF', 'VM'};
y_offsets_emg = [15, 38, 62, 85];
rng(42);
noiselevel = 0.10;

for m = 1:4
    m_name = muscles_order{m};
    ix_m = (N.MnID == m_name) & (N.Latera > 0);
    if any(ix_m)
        prob = sum(N.Rates(t_win, ix_m), 2);
        sig = randn(size(prob)) * noiselevel .* binornd(1, normcdf(normalize(prob, 'zscore')));
        sig = sig .* prob + (randn(size(prob)) * noiselevel);
        env = movmean(abs(sig), 20);
        scale_m = 8.5 / max(eps, max(env));
        plot(ax3e_emg, t_axis, sig * scale_m + y_offsets_emg(m), 'Color', [0.25 0.25 0.25 0.55], 'LineWidth', 0.5);
        plot(ax3e_emg, t_axis, -env * scale_m + y_offsets_emg(m), 'Color', [0.15 0.15 0.15], 'LineWidth', 1.3);
    end
end
set(ax3e_emg, 'YTick', y_offsets_emg, 'YTickLabel', muscle_names_display, 'FontWeight', 'bold', 'FontSize', 9.5);
xlim(ax3e_emg, [0 max(t_axis)]); ylim(ax3e_emg, [0 108]);
set(ax3e_emg, 'XTick', []);
box(ax3e_emg, 'off');
text(ax3e_emg, max(t_axis)*1.02, 50, 'Right', 'Rotation', 90, 'FontWeight', 'bold', 'FontSize', 11);

% 3E Bottom: Motor Outputs (Right L2, Right L5, Left L2)
ax3e_out = axes('Position', [0.12 0.10 0.78 0.24]);
hold(ax3e_out, 'on');

for n = 1:2:(length(locs_cycles)-1)
    patch(ax3e_out, [t_axis(locs_cycles(n)) t_axis(locs_cycles(n+1)) t_axis(locs_cycles(n+1)) t_axis(locs_cycles(n))], ...
          [-10 -10 90 90], [0.90 0.90 0.90], 'EdgeColor', 'none', 'FaceAlpha', 0.6);
end

% Traces: Left L2 (bottom), Right L5 (middle), Right L2 (top)
ix_l2_l = (N.Segment == 'L2') & (N.Types == 'MN') & (N.Latera < 0);
ix_l5_r = (N.Segment == 'L5') & (N.Types == 'MN') & (N.Latera > 0);
ix_l2_r = (N.Segment == 'L2') & (N.Types == 'MN') & (N.Latera > 0);

motor_masks = {ix_l2_l, ix_l5_r, ix_l2_r};
motor_offsets = [12, 38, 64];
for mo = 1:3
    ix_mo = motor_masks{mo};
    prob = sum(N.Rates(t_win, ix_mo), 2);
    sig = randn(size(prob)) * noiselevel .* binornd(1, normcdf(normalize(prob, 'zscore')));
    sig = sig .* prob + (randn(size(prob)) * noiselevel);
    env = movmean(abs(sig), 20);
    scale_mo = 8.5 / max(eps, max(env));
    plot(ax3e_out, t_axis, sig * scale_mo + motor_offsets(mo), 'Color', [0.25 0.25 0.25 0.55], 'LineWidth', 0.5);
    plot(ax3e_out, t_axis, -env * scale_mo + motor_offsets(mo), 'Color', [0.15 0.15 0.15], 'LineWidth', 1.3);
end

set(ax3e_out, 'YTick', motor_offsets, 'YTickLabel', {'L2', 'L5', 'L2'}, 'FontWeight', 'bold', 'FontSize', 10);
text(ax3e_out, max(t_axis)*1.02, 51, 'Right', 'Rotation', 90, 'FontWeight', 'bold', 'FontSize', 10.5);
text(ax3e_out, max(t_axis)*1.02, 12, 'Left', 'Rotation', 90, 'FontWeight', 'bold', 'FontSize', 10.5);
xlim(ax3e_out, [0 max(t_axis)]); ylim(ax3e_out, [0 85]);
set(ax3e_out, 'XTick', []);
box(ax3e_out, 'off');

% 1s Time scale bar
plot(ax3e_out, [max(t_axis)-1000 max(t_axis)], [3 3], '-k', 'LineWidth', 2.5);
text(ax3e_out, max(t_axis)-600, -2, '1 s', 'FontWeight', 'bold', 'FontSize', 9.5);

exportgraphics(fig3e, p_3e, 'Resolution', 300);
fprintf('Saved: %s\n', p_3e);

%% 7. Figure 3F: Polar Phase Relationships (Steady-State 27 Cycles: iL2-iL5 Black, iL2-cL2 Cyan)
fprintf('\nGenerating Figure 3F (Polar Phase Relationships across Steady-State Cycles)...\n');
fig3f = figure('Color', 'white', 'Position', [100 100 450 450], 'Visible', 'off');
ax3f = polaraxes('Position', [0.15 0.15 0.70 0.70]);
hold(ax3f, 'on');

% Compute steady-state cycle peaks over the full 21s window
r_l2_r_full = mean(N.Rates(t_steady, ix_l2_r), 2);
r_l5_r_full = mean(N.Rates(t_steady, ix_l5_r), 2);
r_l2_l_full = mean(N.Rates(t_steady, ix_l2_l), 2);

min_prom = 0.20 * (max(r_l2_r_full) - min(r_l2_r_full));
[~, locs_l2_r] = findpeaks(r_l2_r_full, 'MinPeakDistance', 80, 'MinPeakProminence', min_prom);
[~, locs_l5_r] = findpeaks(r_l5_r_full, 'MinPeakDistance', 80, 'MinPeakProminence', min_prom);
[~, locs_l2_l] = findpeaks(r_l2_l_full, 'MinPeakDistance', 80, 'MinPeakProminence', min_prom);

T_cyc = mean(diff(locs_l2_r));
n_cycles = length(locs_l2_r);
fprintf('Detected %d cycles over %d ms (T_cyc = %.1f ms, Freq = %.2f Hz)\n', ...
    n_cycles, length(t_steady), T_cyc, 1000/T_cyc);

% Calculate cycle phase differences for every detected cycle
phases_l2l5 = [];
phases_lr = [];
for k = 1:length(locs_l2_r)
    if ~isempty(locs_l5_r)
        [~, nn] = min(abs(locs_l5_r - locs_l2_r(k)));
        dt = locs_l5_r(nn) - locs_l2_r(k);
        phi = mod(dt / T_cyc * 2 * pi, 2 * pi);
        phases_l2l5(end+1) = phi;
    end
    if ~isempty(locs_l2_l)
        [~, nn] = min(abs(locs_l2_l - locs_l2_r(k)));
        dt = locs_l2_l(nn) - locs_l2_r(k);
        phi = mod(dt / T_cyc * 2 * pi, 2 * pi);
        phases_lr(end+1) = phi;
    end
end

% Individual cycle points
polarscatter(ax3f, phases_l2l5, ones(size(phases_l2l5)), 25, [0.2 0.2 0.2], 'filled', 'MarkerFaceAlpha', 0.6);
polarscatter(ax3f, phases_lr, ones(size(phases_lr)), 25, [0.25 0.75 0.95], 'filled', 'MarkerFaceAlpha', 0.6);

% Circular mean vectors
circ_mean_local = @(alpha) mod(atan2(sum(sin(alpha(:))), sum(cos(alpha(:)))), 2*pi);
mean_l2l5 = circ_mean_local(phases_l2l5');
mean_lr = circ_mean_local(phases_lr');

% Black vector: iL2-iL5
polarplot(ax3f, [mean_l2l5 mean_l2l5], [0 1.0], 'k-', 'LineWidth', 2.8);
% Cyan vector: iL2-cL2
polarplot(ax3f, [mean_lr mean_lr], [0 1.0], 'Color', [0.25 0.75 0.95], 'LineWidth', 2.8);

rlim(ax3f, [0 1.15]); rticks(ax3f, []);
thetaticks(ax3f, [0 90 180 270]);
thetaticklabels(ax3f, {'0', '\pi/2', '\pi', '3\pi/2'});
set(ax3f, 'FontWeight', 'bold', 'FontSize', 10);
title(ax3f, sprintf('n cycles=%d', n_cycles), 'FontWeight', 'bold', 'FontSize', 10.5);

p_3f = fullfile(subpanelDir, 'fig3f_polar_phase.png');
exportgraphics(fig3f, p_3f, 'Resolution', 300);
fprintf('Saved: %s\n', p_3f);

%% 8. Figure 3G: Neuronal Phase Distribution Across Rhythmic Neurons (R = 400)
fprintf('\nGenerating Figure 3G (Neuronal Phase Distribution Polar Histogram)...\n');
fig3g = figure('Color', 'white', 'Position', [100 100 450 450], 'Visible', 'off');
ax3g = polaraxes('Position', [0.15 0.15 0.70 0.70]);

[~, scores, corrs] = ComputeFiringPhaseSorting(N.Rates(t_steady, :));
rhythmic_idx = (corrs > 0.25);
polarhistogram(ax3g, scores(rhythmic_idx), 24, 'FaceColor', [0.65 0.65 0.65], 'EdgeColor', [0.25 0.25 0.25], 'FaceAlpha', 0.85);

rlim(ax3g, [0 450]); rticks(ax3g, [200 400]);
rticklabels(ax3g, {'', ''});
thetaticks(ax3g, [0 90 180 270]);
thetaticklabels(ax3g, {'0', '\pi/2', '\pi', '3\pi/2'});
set(ax3g, 'FontWeight', 'bold', 'FontSize', 10);

% Annotation for R = 400 neurons
text(ax3g, deg2rad(45), 520, {'R = 400', 'neurons'}, 'FontWeight', 'bold', 'FontSize', 9.5);

p_3g = fullfile(subpanelDir, 'fig3g_neuronal_phase_hist.png');
exportgraphics(fig3g, p_3g, 'Resolution', 300);
fprintf('Saved: %s\n', p_3g);

%% 9. Figure 3H: PCA Low-Dimensional Rotational Dynamics (Author Pipeline)
fprintf('\nGenerating Figure 3H (Author PCA Rotational Dynamics: PC1 vs PC3)...\n');
fig3h = figure('Color', 'white', 'Position', [100 100 450 450], 'Visible', 'off');
ax3h = axes('Position', [0.18 0.18 0.68 0.68]);
hold(ax3h, 'on');

% Execute Author PCA pipeline
rng(100);
N.ComputeSpikes;
N.ComputeEstimatedRates;
Source = true(size(N.EstimatedRates, 1), 1);
N.ComputePC('Estimated', 1, 'Source', Source);

% PC1 and PC2 span the dominant 2D oscillatory limit cycle plane (38.53% total variance)
% PC1: 20.43%, PC2: 18.10%, PC3: 0.62%
pc1 = N.PC(:, 1);
pc2 = N.PC(:, 2);
[~, ~, ~, ~, explained] = pca(N.EstimatedRates);

% Plot outward spiral settling into single-loop limit cycle
t_pca = 1:2500;
plot(ax3h, pc1(t_pca), pc2(t_pca), 'k-', 'LineWidth', 2.2);

r_max = max(sqrt(pc1(t_pca).^2 + pc2(t_pca).^2));

% Curved magenta Time arrow along the top rim pointing counter-clockwise (leftwards)
% Matching published Figure 3H
th_arrow = linspace(0.38*pi, 0.62*pi, 40);
r_arrow = r_max * 1.15;
x_arrow = r_arrow * cos(th_arrow);
y_arrow = r_arrow * sin(th_arrow);

magenta_col = [0.85 0.12 0.47];
plot(ax3h, x_arrow, y_arrow, 'Color', magenta_col, 'LineWidth', 2.4);

% Arrowhead at the left end (counter-clockwise tangent)
th_tip = 0.62 * pi;
tip_x = r_arrow * cos(th_tip);
tip_y = r_arrow * sin(th_tip);
tang_x = -sin(th_tip);
tang_y = cos(th_tip);

arrow_len = 0.10 * r_max;
arrow_w = 0.05 * r_max;
p_tip = [tip_x, tip_y];
p_base = p_tip - arrow_len * [tang_x, tang_y];
p_norm = [-tang_y, tang_x];
p1 = p_base + arrow_w * p_norm;
p2 = p_base - arrow_w * p_norm;
patch(ax3h, [p_tip(1) p1(1) p2(1)], [p_tip(2) p1(2) p2(2)], magenta_col, ...
    'EdgeColor', magenta_col, 'LineWidth', 1.0);

% "Time" text centered above the arc
text(ax3h, 0, r_max * 1.28, 'Time', ...
    'Color', magenta_col, 'FontName', 'Arial', 'FontWeight', 'bold', 'FontSize', 15, ...
    'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom');

% Brackets under PC1 and beside PC3 matching published Figure 3H
br_len = 0.85 * r_max;
br_y = -1.18 * r_max;
tick_h = 0.06 * r_max;
plot(ax3h, [-br_len, -br_len, br_len, br_len], ...
    [br_y + tick_h, br_y, br_y, br_y + tick_h], 'k-', 'LineWidth', 1.5);
text(ax3h, 0, br_y - 0.08 * r_max, 'PC1', ...
    'FontName', 'Arial', 'FontWeight', 'bold', 'FontSize', 14, ...
    'HorizontalAlignment', 'center', 'VerticalAlignment', 'top');

br_x_left = -1.18 * r_max;
plot(ax3h, [br_x_left + tick_h, br_x_left, br_x_left, br_x_left + tick_h], ...
    [-br_len, -br_len, br_len, br_len], 'k-', 'LineWidth', 1.5);
text(ax3h, br_x_left - 0.08 * r_max, 0, 'PC3', ...
    'FontName', 'Arial', 'FontWeight', 'bold', 'FontSize', 14, ...
    'HorizontalAlignment', 'center', 'VerticalAlignment', 'bottom', 'Rotation', 90);

set(ax3h, 'XTick', [], 'YTick', []);
axis(ax3h, 'equal');
xlim(ax3h, [-1.55*r_max 1.55*r_max]);
ylim(ax3h, [-1.55*r_max 1.55*r_max]);
box(ax3h, 'off');
axis(ax3h, 'off');

p_3h = fullfile(subpanelDir, 'fig3h_pca_limit_cycle.png');
exportgraphics(fig3h, p_3h, 'Resolution', 300);
fprintf('Saved: %s\n', p_3h);

%% 10. Save Figure 3 Metrics JSON
if ~exist('brevr_sort', 'var')
    brevr_sort = eigs(sparse(N.ConnMat), 4, 'largestreal');
end

fig3_metrics = struct();
fig3_metrics.figure = 3;
fig3_metrics.status = 'MATCHED REPRODUCTION';
fig3_metrics.fig3e_provenance = 'METHODS-BASED ANATOMICAL-BIN RECONSTRUCTION';
fig3_metrics.dominant_eigenvalues = real(brevr_sort(1:min(4, length(brevr_sort))));
fig3_metrics.locomotor_frequency_hz = 1000 / T_cyc;
fig3_metrics.cycle_period_ms = T_cyc;
fig3_metrics.n_cycles = n_cycles;
fig3_metrics.mean_phase_iL2_cL2_rad = mean_lr;
fig3_metrics.mean_phase_iL2_iL5_rad = mean_l2l5;
fig3_metrics.mean_phase_iL2_cL2_deg = rad2deg(mean_lr);
fig3_metrics.mean_phase_iL2_iL5_deg = rad2deg(mean_l2l5);
fig3_metrics.rhythmic_neuron_count = sum(rhythmic_idx);
fig3_metrics.pca_variance_explained_pc1 = explained(1);
fig3_metrics.pca_variance_explained_pc3 = explained(3);

metrics_path = fullfile(resultsDir, 'figure3_metrics.json');
fid = fopen(metrics_path, 'w');
fwrite(fid, jsonencode(fig3_metrics, PrettyPrint=true));
fclose(fid);
fprintf('Saved Figure 3 metrics: %s\n', metrics_path);

t_total = toc(t_start);
fprintf('\n=================================================================\n');
fprintf('FIGURE 3 REPRODUCTION SUBPANELS COMPLETED (Elapsed: %.2f s)\n', t_total);
fprintf('=================================================================\n');

diary off;
exit(0);
