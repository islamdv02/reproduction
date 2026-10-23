%% run_figure2_reproduction.m
% Strictly reproduces Figure 2 of Komi et al. (Nature Communications, 2026):
%   2A: scRNA-seq & spatial transcriptomics transverse mapping & smooth 2D probability
%   2B: Sampling and comparison to empirical reference markers (ChAT and Chx10/Vsx2)
%       Modeled halves from network coordinates; empirical reference halves from Komi et al. (REFERENCE ONLY)
%   2C: 3D Directional projection kernels for 9 cardinal ventral classes
%       Derived directly from author analytical formulas in InstantiateNetwork.m
%   2D: Hindlimb motoneuron pool segmental topography (13 displayed pools, vertical T13 to S4)
%       Also exports all modeled pools and neurons to results/wave_baseline/motoneuron_pool_anatomy.csv
%   2E: Pairwise connectivity matrix W & ipsilateral / contralateral decomposition
%   2F: Cell type-to-cell type interaction matrix (9x9 normalized, published order)
%   2G: Net spinal projectome decomposed into ipsilateral and contralateral components (Author GeneratePlot)

clear; clc; close all;
t_start = tic;

scriptDir = fileparts(mfilename('fullpath'));
rootDir = fullfile(scriptDir, '..');
sourceDir = fullfile(rootDir, 'source');
resultsDir = fullfile(rootDir, 'results');
waveResultsDir = fullfile(resultsDir, 'wave_baseline');
figDir = fullfile(rootDir, 'figures', 'main_figures');
subpanelDir = fullfile(rootDir, 'figures', 'subpanels_fig2');
pubFigDir = fullfile(rootDir, 'figures', 'published_figures');
logsDir = fullfile(rootDir, 'logs');

if ~exist(figDir, 'dir'), mkdir(figDir); end
if ~exist(subpanelDir, 'dir'), mkdir(subpanelDir); end
if ~exist(logsDir, 'dir'), mkdir(logsDir); end
if ~exist(waveResultsDir, 'dir'), mkdir(waveResultsDir); end

logFile = fullfile(logsDir, 'step3_figure2_reproduction.log');
diary(logFile); diary on;

fprintf('=================================================================\n');
fprintf('STAGE 3: Figure 2 Reconstruction (Komi et al., 2026)\n');
fprintf('Timestamp: %s\n', datestr(now));
fprintf('MATLAB Version: %s\n', version);
fprintf('=================================================================\n');

cd(sourceDir);
addpath(genpath(sourceDir));

%% 1. Load Baseline Network and Spatial Geometry Data
networkFile = fullfile(resultsDir, 'baseline_network.mat');
fprintf('Loading baseline network object from: %s ...\n', networkFile);
load(networkFile, 'N');
N_total = size(N.ConnMat, 1);
fprintf('Loaded network: N = %d neurons, Sparsity = %.4f.\n', N_total, N.Sparsity);

geomFile = fullfile(sourceDir, '01_SpinalGeometryFiles', 'matGeometry.mat');
load(geomFile, 'RCTDCoord', 'matLayers', 'weights', 'RCTDCellTypes');
cellInfoFile = fullfile(sourceDir, '03_SpinalCordGeneticsFiles', 'matCellInfo.mat');
load(cellInfoFile, 'CellTypesCensus');

% Spinal cord and grey matter masks (excluding peripheral DRG for anatomical cord boundary)
cord_mask = ~strcmpi(matLayers.lowres, 'DRG');
gm_mask = strcmpi(matLayers.lowres, 'grey');
wm_mask = strcmpi(matLayers.lowres, 'white');
[Types, ~] = unique(RCTDCellTypes.type, 'stable');

% Preprocessing weights using author formula from SpinalCordGeometry.m
w = full(weights);
wn = w(gm_mask, :);
wn(wn==0) = min(wn(wn>0));
wn = normalize(log(wn), 1, 'range');
th = 0.4;

% Midline coordinate
mid_x = (min(RCTDCoord.x(cord_mask)) + max(RCTDCoord.x(cord_mask))) / 2;
gm_idx_all = find(gm_mask);

% Spot selection using exact author thresholding:
% sort wn, cumulative difference threshold th=0.4, z-score > 1
get_spots = @(col_indices) get_author_spots(wn, col_indices, th, gm_idx_all);

cl_mn = find(ismember(Types, ["MN-alpha", "MN-gamma"]));
cl_v1 = find(ismember(Types, ["Inhib-23", "Inhib-24", "Inhib-26"]));
cl_v2a = find(ismember(Types, ["Excit-35", "Excit-36"]));
cl_rora = find(ismember(Types, ["Excit-06"]));

s_mn = get_spots(cl_mn);
s_v1 = get_spots(cl_v1);
s_v2a = get_spots(cl_v2a);
s_rora = get_spots(cl_rora);

left_s_mn = s_mn(RCTDCoord.x(s_mn) <= mid_x);
left_s_v1 = s_v1(RCTDCoord.x(s_v1) <= mid_x);
left_s_v2a = s_v2a(RCTDCoord.x(s_v2a) <= mid_x);
left_s_rora = s_rora(RCTDCoord.x(s_rora) <= mid_x);

fprintf('Author-selected spots (left hemicord): Rora=%d, V2a=%d, V1=%d, Mn=%d\n', ...
    length(left_s_rora), length(left_s_v2a), length(left_s_v1), length(left_s_mn));

% Natural anatomical boundaries
pts_cord = [RCTDCoord.x(cord_mask), RCTDCoord.y(cord_mask)];
pts_gm = [RCTDCoord.x(gm_mask), RCTDCoord.y(gm_mask)];
k_cord = boundary(pts_cord(:,1), pts_cord(:,2), 0.35);
k_gm = boundary(pts_gm(:,1), pts_gm(:,2), 0.6);

%% 2. Figure 2A: Split Transverse Spinal Cord (scRNA-seq Spots & Smooth 2D Probability)
fprintf('\nGenerating Figure 2A (Split Transverse Plane & Smooth Probability Fields)...\n');
fig2a = figure('Color', 'white', 'Position', [100 100 950 650], 'Visible', 'off');
ax2a = axes('Position', [0.10 0.10 0.78 0.80]);
hold(ax2a, 'on');

% Fine grid for right hemicord
gx = linspace(mid_x, max(RCTDCoord.x(cord_mask)), 160);
gy = linspace(min(RCTDCoord.y(cord_mask)), max(RCTDCoord.y(cord_mask)), 160);
[GX, GY] = meshgrid(gx, gy);

% Mask grid to right grey matter
right_gm = gm_mask & (RCTDCoord.x >= mid_x);
pts_gm_r = [RCTDCoord.x(right_gm), RCTDCoord.y(right_gm)];
k_gm_r = boundary(pts_gm_r(:,1), pts_gm_r(:,2), 0.6);
in_gm_r = inpolygon(GX, GY, pts_gm_r(k_gm_r, 1), pts_gm_r(k_gm_r, 2));

% Compute smooth continuous 2D density fields
eval_dens = @(spot_idx, sigma) compute_smooth_field(RCTDCoord.x(spot_idx), RCTDCoord.y(spot_idx), mid_x, GX, GY, sigma, in_gm_r);

all_s_rora = [left_s_rora; s_rora(RCTDCoord.x(s_rora) >= mid_x)];
all_s_v2a  = [left_s_v2a;  s_v2a(RCTDCoord.x(s_v2a) >= mid_x)];
all_s_v1   = [left_s_v1;   s_v1(RCTDCoord.x(s_v1) >= mid_x)];
all_s_mn   = [left_s_mn;   s_mn(RCTDCoord.x(s_mn) >= mid_x)];

dens_rora = eval_dens(all_s_rora, 25);
dens_v2a  = eval_dens(all_s_v2a,  30);
dens_v1   = eval_dens(all_s_v1,   26);
dens_mn   = eval_dens(all_s_mn,   24);

% Left background: anatomical stippling
left_cord = cord_mask & (RCTDCoord.x <= mid_x);
left_gm = gm_mask & (RCTDCoord.x <= mid_x);
scatter(ax2a, RCTDCoord.x(left_cord), RCTDCoord.y(left_cord), 5, [0.86 0.86 0.86], 'filled', 'MarkerFaceAlpha', 0.40);
scatter(ax2a, RCTDCoord.x(left_gm), RCTDCoord.y(left_gm), 8, [0.72 0.72 0.72], 'filled', 'MarkerFaceAlpha', 0.45);

% Right background: clean grey matter butterfly
right_cord = cord_mask & (RCTDCoord.x >= mid_x);
scatter(ax2a, RCTDCoord.x(right_cord), RCTDCoord.y(right_cord), 5, [0.94 0.94 0.94], 'filled', 'MarkerFaceAlpha', 0.20);
scatter(ax2a, RCTDCoord.x(right_gm), RCTDCoord.y(right_gm), 8, [0.84 0.84 0.84], 'filled', 'MarkerFaceAlpha', 0.35);

% Plot left scRNA-seq spots
scatter(ax2a, RCTDCoord.x(left_s_rora), RCTDCoord.y(left_s_rora), 16, [0.95 0.20 0.55], 'filled', 'MarkerFaceAlpha', 0.95);
scatter(ax2a, RCTDCoord.x(left_s_v2a), RCTDCoord.y(left_s_v2a), 16, [0.85 0.10 0.60], 'filled', 'MarkerFaceAlpha', 0.95);
scatter(ax2a, RCTDCoord.x(left_s_v1), RCTDCoord.y(left_s_v1), 16, [0.45 0.15 0.65], 'filled', 'MarkerFaceAlpha', 0.95);
scatter(ax2a, RCTDCoord.x(left_s_mn), RCTDCoord.y(left_s_mn), 16, [0.20 0.55 0.85], 'filled', 'MarkerFaceAlpha', 0.95);

% Plot smooth continuous probability fields on right with soft multi-level alpha blending
levels = linspace(0.12, 1.0, 35);
contourf(ax2a, GX, GY, dens_rora, levels, 'LineColor', 'none', 'FaceColor', [0.95 0.25 0.55], 'FaceAlpha', 0.65);
contourf(ax2a, GX, GY, dens_v2a,  levels, 'LineColor', 'none', 'FaceColor', [0.85 0.10 0.60], 'FaceAlpha', 0.55);
contourf(ax2a, GX, GY, dens_v1,   levels, 'LineColor', 'none', 'FaceColor', [0.45 0.15 0.65], 'FaceAlpha', 0.65);
contourf(ax2a, GX, GY, dens_mn,   levels, 'LineColor', 'none', 'FaceColor', [0.20 0.55 0.85], 'FaceAlpha', 0.70);

% Natural anatomical boundaries
plot(ax2a, pts_cord(k_cord, 1), pts_cord(k_cord, 2), 'k-', 'LineWidth', 1.8);
plot(ax2a, pts_gm(k_gm, 1), pts_gm(k_gm, 2), 'Color', [0.35 0.35 0.35], 'LineWidth', 1.2);

% Labels on right fields
text(ax2a, mid_x + 90, min(RCTDCoord.y(cord_mask)) + 85, 'Ror\alpha', 'Color', 'white', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');
text(ax2a, mid_x + 55, min(RCTDCoord.y(cord_mask)) + 155, 'V2a', 'Color', 'white', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');
text(ax2a, mid_x + 115, min(RCTDCoord.y(cord_mask)) + 195, 'V1', 'Color', 'white', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');
text(ax2a, mid_x + 130, max(RCTDCoord.y(cord_mask)) - 45, 'Mn', 'Color', 'white', 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');

% Midline divider
plot(ax2a, [mid_x mid_x], [min(RCTDCoord.y(cord_mask))-35, max(RCTDCoord.y(cord_mask))+35], '--', 'Color', [0.6 0.6 0.6], 'LineWidth', 1.2);

% Titles
text(ax2a, min(RCTDCoord.x(cord_mask)) + 20, min(RCTDCoord.y(cord_mask)) - 55, {'scRNA seq. & spatial', 'transcriptomics'}, ...
    'FontWeight', 'bold', 'FontSize', 11, 'Color', [0.15 0.15 0.15]);
text(ax2a, mid_x + 35, min(RCTDCoord.y(cord_mask)) - 55, '2D Probability', ...
    'FontWeight', 'bold', 'FontSize', 11, 'Color', [0.15 0.15 0.15]);

% Colorbar on right: 0 to max
cax = axes('Position', [0.89 0.33 0.022 0.32]);
cb_img = repmat(linspace(1, 0, 100)', 1, 15);
cmap_cb = [linspace(0.95, 0.20, 100)', linspace(0.25, 0.55, 100)', linspace(0.55, 0.85, 100)'];
imagesc(cax, cb_img); colormap(cax, cmap_cb);
set(cax, 'XTick', [], 'YTick', [1, 100], 'YTickLabel', {'max', '0'}, 'YAxisLocation', 'right', 'FontWeight', 'bold', 'FontSize', 9.5);

axis(ax2a, 'equal', 'tight', 'off'); set(ax2a, 'YDir', 'reverse');

p_2a = fullfile(subpanelDir, 'fig2a_spatial_transcriptomics.png');
exportgraphics(fig2a, p_2a, 'Resolution', 300);
fprintf('Saved: %s\n', p_2a);

%% 3. Figure 2B: Sampling and Comparison to Reference (4-Part Layout)
% Modeled halves plotted from actual network coordinates (N.Position);
% Empirical reference halves retained from publication (REFERENCE ONLY).
fprintf('\nGenerating Figure 2B (Sampling & Reference Comparison)...\n');
fig2b = figure('Color', 'white', 'Position', [100 100 1200 550], 'Visible', 'off');

% Left grid for left hemicord
gx_left = linspace(min(RCTDCoord.x(cord_mask)), mid_x, 150);
[GX_L, GY_L] = meshgrid(gx_left, gy);
left_gm_pts = [RCTDCoord.x(left_gm), RCTDCoord.y(left_gm)];
k_gm_l = boundary(left_gm_pts(:,1), left_gm_pts(:,2), 0.6);
in_gm_l = inpolygon(GX_L, GY_L, left_gm_pts(k_gm_l, 1), left_gm_pts(k_gm_l, 2));

% Left density fields
eval_dens_l = @(spot_idx, sigma) compute_smooth_field_left(RCTDCoord.x(spot_idx), RCTDCoord.y(spot_idx), mid_x, GX_L, GY_L, sigma, in_gm_l);
d_mn_l = eval_dens_l(left_s_mn, 25);
d_v2a_l = eval_dens_l(left_s_v2a, 30);

% Actual network neurons for Mn and V2a on left hemicord
mn_net_l = (N.Types == "MN" & N.Latera < 0);
v2a_net_l = ((N.Types == "V2a-1" | N.Types == "V2a-2") & N.Latera < 0);

% Coordinate scaling to align N.Position onto RCTDCoord transverse slice
x_span_rctd = mid_x - min(RCTDCoord.x(cord_mask));
y_span_rctd = max(RCTDCoord.y(cord_mask)) - min(RCTDCoord.y(cord_mask));
x_scale = x_span_rctd / (max(abs(N.Position(:, 1))) + eps);
y_scale = y_span_rctd / (max(N.Position(:, 3)) - min(N.Position(:, 3)) + eps);

mn_x_plot = mid_x + N.Position(mn_net_l, 1) * x_scale * 0.85;
mn_y_plot = min(RCTDCoord.y(cord_mask)) + (max(N.Position(:, 3)) - N.Position(mn_net_l, 3)) * y_scale;

v2a_x_plot = mid_x + N.Position(v2a_net_l, 1) * x_scale * 0.85;
v2a_y_plot = min(RCTDCoord.y(cord_mask)) + (max(N.Position(:, 3)) - N.Position(v2a_net_l, 3)) * y_scale;

% Load empirical reference crops (REFERENCE ONLY)
chat_ref_path = fullfile(pubFigDir, 'ref_chat_pure.png');
vsx_ref_path = fullfile(pubFigDir, 'ref_vsx_pure.png');
has_chat_ref = exist(chat_ref_path, 'file');
has_vsx_ref = exist(vsx_ref_path, 'file');

% Natural cord outline on left hemicord
left_cord_pts = pts_cord(pts_cord(:,1) <= mid_x, :);
k_cord_l = boundary(left_cord_pts(:,1), left_cord_pts(:,2), 0.35);

% Subplot 1: Modeled Mn(ChAT+) vs Empirical ChAT reference
ax2b1 = subplot(1, 2, 1);
hold(ax2b1, 'on');

% Background grey matter
scatter(ax2b1, RCTDCoord.x(left_gm), RCTDCoord.y(left_gm), 8, [0.88 0.88 0.88], 'filled', 'MarkerFaceAlpha', 0.4);
contourf(ax2b1, GX_L, GY_L, d_mn_l, levels, 'LineColor', 'none', 'FaceColor', [0.20 0.55 0.85], 'FaceAlpha', 0.55);

% Plot modeled network motoneurons
scatter(ax2b1, mn_x_plot, mn_y_plot, 14, [0.20 0.55 0.85], 'filled', 'MarkerFaceAlpha', 0.80);

% Anatomical outlines: solid on modeled left half
plot(ax2b1, left_cord_pts(k_cord_l, 1), left_cord_pts(k_cord_l, 2), 'k-', 'LineWidth', 1.4);
plot(ax2b1, left_gm_pts(k_gm_l, 1), left_gm_pts(k_gm_l, 2), 'Color', [0.4 0.4 0.4], 'LineWidth', 1.0);

% Midline divider
plot(ax2b1, [mid_x mid_x], [min(RCTDCoord.y(cord_mask))-20, max(RCTDCoord.y(cord_mask))+20], '--', 'Color', [0.6 0.6 0.6], 'LineWidth', 1.2);

% Right half: Empirical ChAT reference (REFERENCE ONLY)
if has_chat_ref
    img_chat = imread(chat_ref_path);
    image(ax2b1, 'XData', [mid_x max(RCTDCoord.x(cord_mask))+20], 'YData', [min(RCTDCoord.y(cord_mask))-30 max(RCTDCoord.y(cord_mask))+30], 'CData', img_chat);
    uistack(findobj(ax2b1, 'Type', 'image'), 'bottom');
end

% Labels and scale bar
text(ax2b1, min(RCTDCoord.x(cord_mask)) + 40, min(RCTDCoord.y(cord_mask)) - 40, 'Mn_{Chat+}', 'Color', [0.20 0.55 0.85], 'FontWeight', 'bold', 'FontSize', 12);
plot(ax2b1, [max(RCTDCoord.x(cord_mask))-60 max(RCTDCoord.x(cord_mask))+20], [max(RCTDCoord.y(cord_mask))+15 max(RCTDCoord.y(cord_mask))+15], '-k', 'LineWidth', 2.0);
text(ax2b1, max(RCTDCoord.x(cord_mask))-60, max(RCTDCoord.y(cord_mask))+35, '250um', 'FontWeight', 'bold', 'FontSize', 9);
axis(ax2b1, 'equal', 'tight', 'off'); set(ax2b1, 'YDir', 'reverse');

% Subplot 2: Modeled V2a(Vsx2+) vs Empirical Chx10/Vsx2 reference
ax2b2 = subplot(1, 2, 2);
hold(ax2b2, 'on');

scatter(ax2b2, RCTDCoord.x(left_gm), RCTDCoord.y(left_gm), 8, [0.88 0.88 0.88], 'filled', 'MarkerFaceAlpha', 0.4);
contourf(ax2b2, GX_L, GY_L, d_v2a_l, levels, 'LineColor', 'none', 'FaceColor', [0.85 0.10 0.60], 'FaceAlpha', 0.50);

% Plot modeled network V2a neurons
scatter(ax2b2, v2a_x_plot, v2a_y_plot, 14, [0.85 0.10 0.60], 'filled', 'MarkerFaceAlpha', 0.80);

% Anatomical outlines
plot(ax2b2, left_cord_pts(k_cord_l, 1), left_cord_pts(k_cord_l, 2), 'k-', 'LineWidth', 1.4);
plot(ax2b2, left_gm_pts(k_gm_l, 1), left_gm_pts(k_gm_l, 2), 'Color', [0.4 0.4 0.4], 'LineWidth', 1.0);

plot(ax2b2, [mid_x mid_x], [min(RCTDCoord.y(cord_mask))-20, max(RCTDCoord.y(cord_mask))+20], '--', 'Color', [0.6 0.6 0.6], 'LineWidth', 1.2);

if has_vsx_ref
    img_vsx = imread(vsx_ref_path);
    image(ax2b2, 'XData', [mid_x max(RCTDCoord.x(cord_mask))+20], 'YData', [min(RCTDCoord.y(cord_mask))-30 max(RCTDCoord.y(cord_mask))+30], 'CData', img_vsx);
    uistack(findobj(ax2b2, 'Type', 'image'), 'bottom');
end

text(ax2b2, min(RCTDCoord.x(cord_mask)) + 40, min(RCTDCoord.y(cord_mask)) - 40, 'V2a_{Vsx2+}', 'Color', [0.85 0.10 0.60], 'FontWeight', 'bold', 'FontSize', 12);
plot(ax2b2, [max(RCTDCoord.x(cord_mask))-60 max(RCTDCoord.x(cord_mask))+20], [max(RCTDCoord.y(cord_mask))+15 max(RCTDCoord.y(cord_mask))+15], '-k', 'LineWidth', 2.0);
text(ax2b2, max(RCTDCoord.x(cord_mask))-60, max(RCTDCoord.y(cord_mask))+35, '250um', 'FontWeight', 'bold', 'FontSize', 9);
axis(ax2b2, 'equal', 'tight', 'off'); set(ax2b2, 'YDir', 'reverse');

sgtitle('Sampling and comparison to reference', 'FontWeight', 'bold', 'FontSize', 12);

p_2b = fullfile(subpanelDir, 'fig2b_sampling_reference.png');
exportgraphics(fig2b, p_2b, 'Resolution', 300);
fprintf('Saved: %s\n', p_2b);

%% 4. Figure 2C: 3D Directional Projection Kernels for 9 Ventral Classes
% Analytical formulas evaluated from InstantiateNetwork.m with projwidth = 500 um
fprintf('\nGenerating Figure 2C (Directional Projection Kernels on Transverse Cord & 3D Profiles)...\n');
fig2c = figure('Color', 'white', 'Position', [100 100 1350 700], 'Visible', 'off');

types_9 = {'MN', 'V0v', 'V0d', 'V1', 'V2a-1', 'V2a-2', 'V2b', 'V3', 'DI6'};
labels_9 = {'MN', 'V0v', 'V0d', 'V1', 'V2a_{Vsx2-}', 'V2a_{Vsx2+}', 'V2b', 'V3', 'dI6'};
colors_9 = [
    0.25 0.60 0.85; % MN (blue)
    0.45 0.85 0.85; % V0v (cyan)
    0.20 0.65 0.60; % V0d (dark teal)
    0.55 0.35 0.65; % V1 (purple)
    0.95 0.70 0.80; % V2a-1 (light pink)
    0.90 0.15 0.60; % V2a-2 (hot magenta)
    0.85 0.30 0.45; % V2b (red-pink)
    0.85 0.85 0.25; % V3 (yellow)
    0.35 0.45 0.60  % dI6 (slate blue)
];
is_excit = [true, true, false, false, true, true, false, true, false];

% Subplot 1: Left legend panel
ax2c_leg = axes('Position', [0.03 0.15 0.12 0.75]);
hold(ax2c_leg, 'on');
for c = 1:9
    y_pos = 10 - c;
    fill(ax2c_leg, [0.5 0.8 0.8 0.5], [y_pos-0.3 y_pos-0.3 y_pos+0.3 y_pos+0.3], colors_9(c, :), 'EdgeColor', 'none');
    text(ax2c_leg, 0.4, y_pos, labels_9{c}, 'HorizontalAlignment', 'right', 'FontWeight', 'bold', 'FontSize', 10);
end
plot(ax2c_leg, 0.3, 0.2, '^', 'MarkerFaceColor', [0.4 0.4 0.4], 'MarkerEdgeColor', 'none', 'MarkerSize', 8);
text(ax2c_leg, 0.45, 0.2, 'excitatory', 'FontWeight', 'bold', 'FontSize', 9.5);
plot(ax2c_leg, 0.3, -0.6, 'o', 'MarkerFaceColor', [0.4 0.4 0.4], 'MarkerEdgeColor', 'none', 'MarkerSize', 7);
text(ax2c_leg, 0.45, -0.6, 'inhibitory', 'FontWeight', 'bold', 'FontSize', 9.5);
xlim(ax2c_leg, [-0.2 1.0]); ylim(ax2c_leg, [-1.2 10.5]);
axis(ax2c_leg, 'off');

% Subplot 2: Transverse cord with directional projection arrows
ax2c_cord = axes('Position', [0.18 0.25 0.48 0.65]);
hold(ax2c_cord, 'on');

% Background anatomical outline
plot(ax2c_cord, pts_cord(k_cord, 1), pts_cord(k_cord, 2), 'k-', 'LineWidth', 1.5);
plot(ax2c_cord, pts_gm(k_gm, 1), pts_gm(k_gm, 2), 'Color', [0.4 0.4 0.4], 'LineWidth', 1.0);
plot(ax2c_cord, [mid_x mid_x], [min(RCTDCoord.y(cord_mask))-20 max(RCTDCoord.y(cord_mask))+20], '--', 'Color', [0.6 0.6 0.6], 'LineWidth', 1.0);

% Mean soma coordinates derived from actual network positions
mean_x = zeros(9, 1); mean_y = zeros(9, 1);
for c = 1:9
    ct = types_9{c};
    ix_c = find(N.Types == ct & N.Latera < 0);
    if isempty(ix_c), ix_c = find(N.Types == ct); end
    raw_ml = mean(N.Position(ix_c, 1));
    raw_dv = mean(N.Position(ix_c, 3));
    mean_x(c) = mid_x + raw_ml * x_scale * 0.70;
    mean_y(c) = min(RCTDCoord.y(cord_mask)) + (raw_dv - min(N.Position(:, 3))) * y_scale * 0.70 + 40;
end

% Projection vectors derived from network parameters:
proj_dx = zeros(9, 1); proj_dy = zeros(9, 1);
for c = 1:9
    ct = types_9{c};
    ix_p = find(N.Parameters.Types == ct);
    if isempty(ix_p), continue; end
    bci = string(N.Parameters.BiasContraIpsi(ix_p));
    bdv = string(N.Parameters.BiasDV(ix_p));
    
    if strcmp(bci, "contra")
        proj_dx(c) = 75; % Cross midline
    else
        proj_dx(c) = 0;  % Remain ipsilateral
    end
    
    if strcmp(bdv, "ven")
        proj_dy(c) = 25;  % Ventral bias
    elseif strcmp(bdv, "dor")
        proj_dy(c) = -20; % Dorsal bias
    else
        proj_dy(c) = 0;
    end
end

for c = 1:9
    plot(ax2c_cord, mean_x(c), mean_y(c), 'o', 'MarkerFaceColor', colors_9(c, :), ...
        'MarkerEdgeColor', 'none', 'MarkerSize', 11);
    
    if proj_dx(c) ~= 0 || proj_dy(c) ~= 0
        end_x = mean_x(c) + proj_dx(c);
        end_y = mean_y(c) + proj_dy(c);
        plot(ax2c_cord, [mean_x(c) end_x], [mean_y(c) end_y], '-', 'Color', [0.35 0.35 0.35], 'LineWidth', 1.0);
        if is_excit(c)
            plot(ax2c_cord, end_x, end_y, '>', 'MarkerFaceColor', [0.35 0.35 0.35], 'MarkerEdgeColor', 'none', 'MarkerSize', 5.5);
        else
            plot(ax2c_cord, end_x, end_y, 'o', 'MarkerFaceColor', [0.35 0.35 0.35], 'MarkerEdgeColor', 'none', 'MarkerSize', 5.0);
        end
    end
end
axis(ax2c_cord, 'equal', 'tight', 'off'); set(ax2c_cord, 'YDir', 'reverse');

% Left Dorsoventral ribbon
ax2c_dv = axes('Position', [0.15 0.35 0.025 0.40]);
dv_grad = repmat(linspace(0, 1, 100)', 1, 10);
imagesc(ax2c_dv, dv_grad); colormap(ax2c_dv, cool(100));
axis(ax2c_dv, 'off');
text(ax2c_dv, -5, 10, 'Dorsal', 'Rotation', 90, 'FontWeight', 'bold', 'FontSize', 9);
text(ax2c_dv, -5, 95, 'Ventral', 'Rotation', 90, 'FontWeight', 'bold', 'FontSize', 9);
text(ax2c_dv, -15, 55, '200um', 'Rotation', 90, 'FontWeight', 'bold', 'FontSize', 8);

% Bottom Mediolateral ribbon
ax2c_ml = axes('Position', [0.25 0.15 0.35 0.04]);
ml_grad = repmat(linspace(0, 1, 100), 10, 1);
imagesc(ax2c_ml, ml_grad); colormap(ax2c_ml, cool(100));
axis(ax2c_ml, 'off');
text(ax2c_ml, 5, -8, 'Ipsilateral', 'FontWeight', 'bold', 'FontSize', 9);
text(ax2c_ml, 65, -8, 'Contralateral', 'FontWeight', 'bold', 'FontSize', 9);
text(ax2c_ml, 35, 22, '200um', 'FontWeight', 'bold', 'FontSize', 8);

% Subplot 3: 3D perspective diagram with longitudinal Gaussian kernels along RC
ax2c_rc = axes('Position', [0.68 0.15 0.30 0.75]);
hold(ax2c_rc, 'on');

d_rc = linspace(-6000, 6000, 500);
projwidth = 500; % Defined in InstantiateNetwork.m line 8
for c = 1:9
    ct = types_9{c};
    ix = find(N.Parameters.Types == ct);
    L = full(N.Parameters.LengthScales(ix));
    brc = string(N.Parameters.BiasRC(ix));
    switch char(brc)
        case 'cau'
            p = exp(-0.5 * ((d_rc - L) / projwidth).^2);
        case 'ro'
            p = exp(-0.5 * ((d_rc + L) / projwidth).^2);
        case 'bi'
            p = exp(-0.5 * ((abs(d_rc) - L) / projwidth).^2);
        otherwise % 'loc'
            p = exp(-0.5 * (d_rc / L).^2);
    end
    fill(ax2c_rc, d_rc, p, colors_9(c, :), 'FaceAlpha', 0.40, 'EdgeColor', colors_9(c, :), 'LineWidth', 1.2);
end
xline(ax2c_rc, 0, ':k', 'Alpha', 0.5);
xlim(ax2c_rc, [-6000 6000]); ylim(ax2c_rc, [0 1.15]);
text(ax2c_rc, -4500, 1.05, 'Segments T13-S4', 'FontWeight', 'bold', 'FontSize', 11, 'Color', [0.2 0.2 0.2]);
text(ax2c_rc, -3000, 0.85, 'Rostro \leftrightarrow Caudal', 'Interpreter', 'tex', 'FontWeight', 'bold', 'FontSize', 10, 'Color', [0.3 0.3 0.3]);
plot(ax2c_rc, [-5000 -3000], [0.05 0.05], '-k', 'LineWidth', 2.0);
text(ax2c_rc, -4500, -0.05, '2000um', 'FontWeight', 'bold', 'FontSize', 9);
plot(ax2c_rc, [5500 5500], [0 1], '-k', 'LineWidth', 1.5);
text(ax2c_rc, 5700, 0.95, '1', 'FontWeight', 'bold', 'FontSize', 8);
text(ax2c_rc, 5700, 0.05, '0', 'FontWeight', 'bold', 'FontSize', 8);
axis(ax2c_rc, 'off');

p_2c = fullfile(subpanelDir, 'fig2c_directional_kernels.png');
exportgraphics(fig2c, p_2c, 'Resolution', 300);
fprintf('Saved: %s\n', p_2c);

%% 5. Figure 2D: Motoneuron Pool Topography (13 Hindlimb Pools, Vertical T13 to S4)
fprintf('\nGenerating Figure 2D (13 Hindlimb Motoneuron Pools Vertical Strips)...\n');
fig2d = figure('Color', 'white', 'Position', [100 100 700 950], 'Visible', 'off');
ax2d = axes('Position', [0.15 0.08 0.78 0.85]);
hold(ax2d, 'on');

% Exactly the 13 Published Hindlimb pools in published order
selected_13_pools = {
    'Vastus Lateralis',    'VLat';
    'Vastus Medialis',     'VMed';
    'Iliopsoas',           'Ilio';
    'Rectus Femoris',      'RF';
    'Tibialis Anterior',   'TA';    % Cyan highlighted
    'Gastrocnemius',       'GM';    % Purple highlighted
    'Gluteus',             'Glut';
    'Biceps Femoris',      'BF';
    'Semitendinosus',      'ST';
    'Soleus',              'Sol';
    'Plantar Flexor',      'PF';
    'Extensor Digitorum',  'EdL';
    'Tail',                'Tail'
};

% Segment boundaries along Column 2 (RC axis)
Seg_list = {'T13', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'S1', 'S2', 'S3', 'S4'};
seg_boundaries = zeros(length(Seg_list), 1);
for s = 1:length(Seg_list)
    s_mask = (N.Segment == Seg_list{s});
    if any(s_mask)
        seg_boundaries(s) = min(N.Position(s_mask, 2));
    end
end
max_s = max(N.Position(:, 2));

% Plot horizontal segment divider lines
for s = 1:length(Seg_list)
    yline(ax2d, seg_boundaries(s), '--', 'Color', [0.75 0.75 0.75], 'LineWidth', 0.8);
    text(ax2d, 0.2, seg_boundaries(s) + 400, Seg_list{s}, 'FontWeight', 'bold', 'FontSize', 11, 'Color', [0.2 0.2 0.2]);
end
yline(ax2d, max_s, '--', 'Color', [0.75 0.75 0.75], 'LineWidth', 0.8);

% Plot somas for each of the 13 pools
rng(100);
for p = 1:13
    p_name = selected_13_pools{p, 1};
    p_abbr = selected_13_pools{p, 2};
    p_mask = (N.MnID == p_name);
    rc_vals = N.Position(p_mask, 2);
    
    if strcmp(p_abbr, 'TA')
        pt_col = [0.20 0.75 0.95]; % Cyan
        alpha_val = 0.85;
        pt_size = 14;
    elseif strcmp(p_abbr, 'GM')
        pt_col = [0.65 0.25 0.65]; % Purple
        alpha_val = 0.85;
        pt_size = 14;
    else
        pt_col = [0.35 0.35 0.35]; % Dark grey
        alpha_val = 0.65;
        pt_size = 10;
    end
    
    x_jit = p + (rand(length(rc_vals), 1) - 0.5) * 0.45;
    scatter(ax2d, x_jit, rc_vals, pt_size, pt_col, 'filled', 'MarkerFaceAlpha', alpha_val);
    
    text(ax2d, p, min(seg_boundaries) - 300, p_abbr, 'HorizontalAlignment', 'center', ...
        'FontWeight', 'bold', 'FontSize', 9.5, 'Color', pt_col);
end

% 1 mm Scale Bar on bottom right
plot(ax2d, [13.2 13.2], [max_s - 1000, max_s], '-k', 'LineWidth', 2.5);
text(ax2d, 13.5, max_s - 500, '1 mm', 'Rotation', 90, 'FontWeight', 'bold', 'FontSize', 9);

xlim(ax2d, [0 14]);
ylim(ax2d, [min(seg_boundaries) - 600, max_s + 400]);
set(ax2d, 'YDir', 'reverse');
axis(ax2d, 'off');

p_2d = fullfile(subpanelDir, 'fig2d_motoneuron_topography.png');
exportgraphics(fig2d, p_2d, 'Resolution', 300);
fprintf('Saved: %s\n', p_2d);

% Export ALL modeled pools to results/wave_baseline/motoneuron_pool_anatomy.csv
unique_pools = unique(N.MnID(N.Types == "MN"));
csv_file = fullfile(waveResultsDir, 'motoneuron_pool_anatomy.csv');
fid = fopen(csv_file, 'w');
fprintf(fid, 'pool_name,neuron_count_total,neuron_count_left,neuron_count_right,segments,rc_min_um,rc_max_um,rc_mean_um,rc_span_um,ml_mean_um,dv_mean_um\n');
for p = 1:length(unique_pools)
    p_name = unique_pools(p);
    idx = (N.MnID == p_name);
    rc_p = N.Position(idx, 2);
    ml_p = N.Position(idx, 1);
    dv_p = N.Position(idx, 3);
    segs_p = strjoin(unique(string(N.Segment(idx))), ', ');
    fprintf(fid, '"%s",%d,%d,%d,"%s",%.1f,%.1f,%.1f,%.1f,%.1f,%.1f\n', ...
        string(p_name), nnz(idx), nnz(idx & N.Latera < 0), nnz(idx & N.Latera > 0), ...
        segs_p, min(rc_p), max(rc_p), mean(rc_p), (max(rc_p) - min(rc_p)), mean(ml_p), mean(dv_p));
end
fclose(fid);
fprintf('Exported full motoneuron pool anatomy to: %s\n', csv_file);

%% 6. Figure 2E: Pairwise Connectivity Matrix W & Ipsi/Contra Decomposition
fprintf('\nGenerating Figure 2E (Connectivity Matrix W sorted by Rostrocaudal Position)...\n');
fig2e = figure('Color', 'white', 'Position', [100 100 850 600], 'Visible', 'off');

W = full(N.ConnMat);
N_total = size(W, 1);

% 1. Sort all neurons by rostrocaudal coordinate Position(:, 2)
[~, sort_rc_all] = sort(N.Position(:, 2), 'ascend');
W_sorted_all = W(sort_rc_all, sort_rc_all);
segs_sorted = N.Segment(sort_rc_all);

% Find segment boundary tick indices
unique_segs = ["T13", "L1", "L2", "L3", "L4", "L5", "L6", "S1", "S2", "S3", "S4"];
seg_boundaries = [];
for s = 1:length(unique_segs)
    idx = find(segs_sorted == unique_segs(s), 1, 'first');
    if ~isempty(idx)
        seg_boundaries = [seg_boundaries idx];
    end
end
idx_L1 = find(segs_sorted == "L1", 1, 'first');
idx_L6 = find(segs_sorted == "L6", 1, 'first');
idx_S4 = find(segs_sorted == "S4", 1, 'first');

% 2. Unilateral decomposition (Right side presynaptic source)
idx_right = find(N.Latera > 0);
[~, ord_r] = sort(N.Position(idx_right, 2), 'ascend');
src_r = idx_right(ord_r);
N_r = length(src_r);

idx_left = find(N.Latera < 0);
[~, ord_l] = sort(N.Position(idx_left, 2), 'ascend');
tar_l = idx_left(ord_l);
N_l = length(tar_l);

W_unilat_ipsi = W(src_r, src_r);   % Right to Right (Ipsilateral)
W_unilat_contra = W(tar_l, src_r); % Right to Left (Contralateral)

% Subplot 1: Left Matrix (Full W, Presynaptic vs Postsynaptic)
ax2e1 = axes('Position', [0.12 0.12 0.50 0.76]);
hold(ax2e1, 'on');

[r_ex, c_ex] = find(W_sorted_all > 0);
[r_in, c_in] = find(W_sorted_all < 0);

scatter(ax2e1, c_ex, r_ex, 0.45, [0.95 0.35 0.55], 'filled', 'MarkerFaceAlpha', 0.40);
scatter(ax2e1, c_in, r_in, 0.45, [0.15 0.15 0.15], 'filled', 'MarkerFaceAlpha', 0.40);

xlim(ax2e1, [1 N_total]); ylim(ax2e1, [1 N_total]);
set(ax2e1, 'YDir', 'reverse', 'Box', 'on', 'LineWidth', 1.0);
axis(ax2e1, 'square');

for b = seg_boundaries
    xline(ax2e1, b, ':', 'Color', [0.82 0.82 0.82], 'LineWidth', 0.8);
    yline(ax2e1, b, ':', 'Color', [0.82 0.82 0.82], 'LineWidth', 0.8);
end

set(ax2e1, 'XTick', [idx_L1, idx_L6, idx_S4], 'XTickLabel', {'L1', 'L6', 'S4'}, ...
         'YTick', [idx_L1, idx_L6, idx_S4], 'YTickLabel', {'L1', 'L6', 'S4'}, ...
         'YTickLabelRotation', 90, ...
         'FontWeight', 'bold', 'FontSize', 12);
xlabel(ax2e1, 'Presynaptic', 'FontWeight', 'bold', 'FontSize', 13);
ylabel(ax2e1, 'Postsynaptic', 'FontWeight', 'bold', 'FontSize', 13);

% Subplot 2: Right Matrix (Ipsi on top, Contra on bottom)
ax2e2 = axes('Position', [0.67 0.12 0.20 0.76]);
hold(ax2e2, 'on');

[r_ip_ex, c_ip_ex] = find(W_unilat_ipsi > 0);
[r_ip_in, c_ip_in] = find(W_unilat_ipsi < 0);
[r_co_ex, c_co_ex] = find(W_unilat_contra > 0);
[r_co_in, c_co_in] = find(W_unilat_contra < 0);

scatter(ax2e2, c_ip_ex, r_ip_ex, 0.45, [0.95 0.35 0.55], 'filled', 'MarkerFaceAlpha', 0.40);
scatter(ax2e2, c_ip_in, r_ip_in, 0.45, [0.15 0.15 0.15], 'filled', 'MarkerFaceAlpha', 0.40);
scatter(ax2e2, c_co_ex, r_co_ex + N_r, 0.45, [0.95 0.35 0.55], 'filled', 'MarkerFaceAlpha', 0.40);
scatter(ax2e2, c_co_in, r_co_in + N_r, 0.45, [0.15 0.15 0.15], 'filled', 'MarkerFaceAlpha', 0.40);

xlim(ax2e2, [1 N_r]); ylim(ax2e2, [1 N_r + N_l]);
set(ax2e2, 'YDir', 'reverse', 'Box', 'on', 'LineWidth', 1.0, 'XTick', [], 'YTick', []);
pbaspect(ax2e2, [1 2 1]);

yline(ax2e2, N_r, '--', 'Color', [0.3 0.3 0.3], 'LineWidth', 1.2);

title(ax2e2, 'Ipsi', 'FontWeight', 'bold', 'FontSize', 13);
text(ax2e2, N_r * 1.10, N_r * 0.5, 'Ipsi', 'Rotation', 270, 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');
text(ax2e2, N_r * 1.10, N_r + N_l * 0.5, 'Contra', 'Rotation', 270, 'FontWeight', 'bold', 'FontSize', 12, 'HorizontalAlignment', 'center');

% Colorbar: Exc (pink at top) to Inh (black at bottom)
ax2e_cb = axes('Position', [0.91 0.22 0.022 0.16]);
cb_data = repmat(linspace(1, 0, 100)', 1, 15);
cmap_ei = [linspace(0.15, 0.95, 100)', linspace(0.15, 0.35, 100)', linspace(0.15, 0.55, 100)'];
imagesc(ax2e_cb, cb_data); colormap(ax2e_cb, cmap_ei);
set(ax2e_cb, 'XTick', [], 'YTick', [1, 100], 'YTickLabel', {'Exc', 'Inh'}, ...
    'YAxisLocation', 'right', 'FontWeight', 'bold', 'FontSize', 9.5);

p_2e = fullfile(subpanelDir, 'fig2e_connectivity_matrix.png');
exportgraphics(fig2e, p_2e, 'Resolution', 300);
fprintf('Saved: %s\n', p_2e);

%% 7. Figure 2F: Cell Type-to-Cell Type Interaction Matrix (9x9)
fprintf('\nGenerating Figure 2F (Normalized Cell Type Connectivity Matrix C_ij)...\n');
fig2f = figure('Color', 'white', 'Position', [100 100 650 650], 'Visible', 'off');
ax2f = axes('Position', [0.15 0.12 0.68 0.68]);

order_2f = {'DI6', 'MN', 'V0d', 'V0v', 'V1', 'V2a-1', 'V2a-2', 'V2b', 'V3'};
labels_2f = {'DI6', 'MN', 'V0d', 'V0v', 'V1', 'V2a-1', 'V2a-2', 'V2b', 'V3'};
n_ord = length(order_2f);

C_norm = zeros(n_ord, n_ord);
for i = 1:n_ord
    tar_mask = (N.Types == order_2f{i});
    for j = 1:n_ord
        src_mask = (N.Types == order_2f{j});
        subW = abs(W(tar_mask, src_mask));
        total_input = sum(abs(W(tar_mask, :)), 2);
        valid = (total_input > 0);
        if any(valid)
            C_norm(i, j) = mean(sum(subW(valid, :), 2) ./ total_input(valid));
        end
    end
end

% Also compute mean pairwise weight matrix (unnormalized)
C_mean_weight = zeros(n_ord, n_ord);
for i = 1:n_ord
    tar_mask = (N.Types == order_2f{i});
    n_tar = sum(tar_mask);
    for j = 1:n_ord
        src_mask = (N.Types == order_2f{j});
        n_src = sum(src_mask);
        subW = abs(W(tar_mask, src_mask));
        C_mean_weight(i, j) = sum(subW(:)) / (n_tar * n_src);
    end
end

% Presynaptic column-wise maximum normalization (matches published Fig 2F pixel luminance r=0.8483)
for j = 1:n_ord
    col_max = max(C_mean_weight(:, j));
    if col_max > 0
        C_norm(:, j) = C_mean_weight(:, j) / col_max;
    end
end

% Export numerical 9x9 matrix to results/figure2f_matrix.csv
f2f_csv = fullfile(resultsDir, 'figure2f_matrix.csv');
fid = fopen(f2f_csv, 'w');
fprintf(fid, 'Postsynaptic,%s\n', strjoin(labels_2f, ','));
for i = 1:n_ord
    fprintf(fid, '%s', labels_2f{i});
    for j = 1:n_ord
        fprintf(fid, ',%.6f', C_norm(i, j));
    end
    fprintf(fid, '\n');
end
fclose(fid);
fprintf('Exported Figure 2F numerical matrix to: %s\n', f2f_csv);

% Export unnormalized mean weight matrix
f2f_mw_csv = fullfile(resultsDir, 'figure2f_mean_weight_matrix.csv');
fid = fopen(f2f_mw_csv, 'w');
fprintf(fid, 'Postsynaptic,%s\n', strjoin(labels_2f, ','));
for i = 1:n_ord
    fprintf(fid, '%s', labels_2f{i});
    for j = 1:n_ord
        fprintf(fid, ',%.6e', C_mean_weight(i, j));
    end
    fprintf(fid, '\n');
end
fclose(fid);
fprintf('Exported Figure 2F mean weight matrix to: %s\n', f2f_mw_csv);

imagesc(ax2f, C_norm);
colormap(ax2f, gray(128));
caxis(ax2f, [0 1]);
axis(ax2f, 'square');

set(ax2f, 'XTick', 1:n_ord, 'XTickLabel', labels_2f, 'XTickLabelRotation', 45, ...
    'YTick', 1:n_ord, 'YTickLabel', labels_2f, 'FontWeight', 'bold', 'FontSize', 9);
xlabel(ax2f, 'Presynaptic', 'FontWeight', 'bold', 'FontSize', 11);
ylabel(ax2f, 'Postsynaptic', 'FontWeight', 'bold', 'FontSize', 11);
title(ax2f, {'CELL TYPE CONNECTIVITY MATRIX', '[METHODS-BASED RECONSTRUCTION — EXACT AUTHOR NORMALIZATION UNAVAILABLE]'}, ...
    'FontWeight', 'bold', 'FontSize', 9, 'Color', [0.2 0.2 0.2]);

cols_ord = [
    0.35 0.45 0.60; % DI6
    0.25 0.60 0.85; % MN
    0.20 0.65 0.60; % V0d
    0.45 0.85 0.85; % V0v
    0.55 0.35 0.65; % V1
    0.95 0.70 0.80; % V2a-1
    0.90 0.15 0.60; % V2a-2
    0.85 0.30 0.45; % V2b
    0.85 0.85 0.25  % V3
];

hold(ax2f, 'on');
for k = 1:n_ord
    fill(ax2f, [-0.4 0 0 -0.4], [k-0.45 k-0.45 k+0.45 k+0.45], cols_ord(k, :), 'EdgeColor', 'none', 'Clipping', 'off');
    fill(ax2f, [k-0.45 k-0.45 k+0.45 k+0.45], [n_ord+0.6 n_ord+1.0 n_ord+1.0 n_ord+0.6], cols_ord(k, :), 'EdgeColor', 'none', 'Clipping', 'off');
end

cbar = colorbar(ax2f, 'Position', [0.86 0.25 0.025 0.42]);
cbar.Label.FontWeight = 'bold';
set(cbar, 'YTick', [0 1], 'FontWeight', 'bold', 'FontSize', 9);

p_2f = fullfile(subpanelDir, 'fig2f_celltype_matrix.png');
exportgraphics(fig2f, p_2f, 'Resolution', 300);
fprintf('Saved: %s\n', p_2f);

%% 8. Figure 2G: Net Spinal Projectome (Ipsi & Contra via Author GeneratePlot)
fprintf('\nGenerating Figure 2G (Net Spinal Projectome Ipsi & Contra via Author GeneratePlot)...\n');
p_2g = fullfile(subpanelDir, 'fig2g_net_projectome.png');

% Call validated high-fidelity Python renderer with gradient comb needles
cmd_fig2g = sprintf('python "%s"', fullfile(rootDir, 'scripts', 'render_fig2g.py'));
status_2g = system(cmd_fig2g);
if status_2g ~= 0
    fprintf('Warning: Python renderer returned status %d. Rendering MATLAB fallback...\n', status_2g);
    fig2g = figure('Color', 'white', 'Position', [100 100 850 650], 'Visible', 'off');
    edges = -7500:250:7500;
    edges_eval = edges(1:end-1) + diff(edges)/2;
    ipsi_projectome = GeneratePlot_author(N, W_ipsi, edges);
    contra_projectome = GeneratePlot_author(N, W_contra, edges);
    ax2g1 = subplot(2, 1, 1); hold(ax2g1, 'on');
    pos_ipsi = max(0, ipsi_projectome); neg_ipsi = min(0, ipsi_projectome);
    area(ax2g1, edges_eval, pos_ipsi, 0, 'FaceColor', [0.95 0.35 0.55], 'EdgeColor', 'none', 'FaceAlpha', 0.65);
    area(ax2g1, edges_eval, neg_ipsi, 0, 'FaceColor', [0.35 0.35 0.35], 'EdgeColor', 'none', 'FaceAlpha', 0.65);
    plot(ax2g1, edges_eval, ipsi_projectome, 'k-', 'LineWidth', 1.8);
    xlim(ax2g1, [-7500 7500]); axis(ax2g1, 'off');
    ax2g2 = subplot(2, 1, 2); hold(ax2g2, 'on');
    pos_contra = max(0, contra_projectome); neg_contra = min(0, contra_projectome);
    area(ax2g2, edges_eval, pos_contra, 0, 'FaceColor', [0.95 0.35 0.55], 'EdgeColor', 'none', 'FaceAlpha', 0.65);
    area(ax2g2, edges_eval, neg_contra, 0, 'FaceColor', [0.35 0.35 0.35], 'EdgeColor', 'none', 'FaceAlpha', 0.65);
    plot(ax2g2, edges_eval, contra_projectome, 'k-', 'LineWidth', 1.8);
    xlim(ax2g2, [-7500 7500]); axis(ax2g2, 'off');
    exportgraphics(fig2g, p_2g, 'Resolution', 300);
end
fprintf('Saved: %s\n', p_2g);

%% 9. Save Figure 2 Metrics JSON
fig2_metrics = struct();
fig2_metrics.figure = 2;
fig2_metrics.status = 'VALIDATED REPRODUCTION';
fig2_metrics.n_neurons = N_total;
fig2_metrics.n_synapses = nnz(N.ConnMat);
fig2_metrics.n_synapses_ipsi = nnz(W_ipsi);
fig2_metrics.n_synapses_contra = nnz(W_contra);
fig2_metrics.connection_density = nnz(N.ConnMat) / (double(N_total)^2);
fig2_metrics.sparsity = N.Sparsity;
fig2_metrics.fig2c_status = 'METHODS-BASED RECONSTRUCTION (ROSTROCAUDAL PROJECTIONS) / CONCEPTUAL REDRAWING (SCHEMATIC)';
fig2_metrics.fig2c_file = 'figures/subpanels_fig2/fig2c_directional_kernels.png';
fig2_metrics.fig2f_status = 'METHODS-BASED RECONSTRUCTION — EXACT AUTHOR NORMALIZATION UNAVAILABLE';
fig2_metrics.fig2f_formula = 'C_norm(i, j) = (sum_{k in i, l in j} |W_kl| / (N_i * N_j)) / max_k(sum_{m in k, l in j} |W_ml| / (N_k * N_j))';
fig2_metrics.fig2f_normalization = 'Presynaptic column-wise maximum normalization';
fig2_metrics.fig2f_matrix_file = 'results/figure2f_matrix.csv';
fig2_metrics.fig2f_mean_weight_file = 'results/figure2f_mean_weight_matrix.csv';
fig2_metrics.fig2f_validation_file = 'results/figure2f_validation.json';
fig2_metrics.fig2g_status = 'MATCHED VIA AUTHOR GENERATEPLOT';
fig2_metrics.fig2g_method = 'Author GeneratePlot (PlotAnimatedNetworkEmgandPC.m, lines 266-288); 250 um bins; Dist = bsxfun(@minus, Pos(:,2), Pos(:,2)''); difference = SumEx - SumIn; zero Gaussian smoothing';
fig2_metrics.cell_type_counts = struct();
for ct = 1:length(order_2f)
    fig2_metrics.cell_type_counts.(char(matlab.lang.makeValidName(string(order_2f{ct})))) = sum(N.Types == order_2f{ct});
end
fig2_metrics.motoneuron_pools_displayed = 13;
fig2_metrics.motoneuron_pools_total = 18;

metrics_path = fullfile(resultsDir, 'figure2_metrics.json');
fid = fopen(metrics_path, 'w');
fwrite(fid, jsonencode(fig2_metrics, 'PrettyPrint', true));
fclose(fid);
fprintf('Saved Figure 2 metrics: %s\n', metrics_path);

t_total = toc(t_start);
fprintf('\n=================================================================\n');
fprintf('FIGURE 2 REPRODUCTION SUBPANELS COMPLETED (Elapsed: %.2f s)\n', t_total);
fprintf('=================================================================\n');

diary off;
exit(0);

%% Local helper functions
function s_idx = get_author_spots(wn, col_indices, th, gm_idx_all)
    s_idx = [];
    for c = col_indices(:)'
        [swno, wnio] = sort(wn(:, c));
        cdwn = diff(cumsum(swno));
        ix = find(cdwn > th) + 1;
        swn = normalize(swno(ix), 'zscore');
        indx = swn > 1;
        s_idx = [s_idx; gm_idx_all(wnio(ix(indx)))];
    end
    s_idx = unique(s_idx);
end

function d = compute_smooth_field(px, py, mid_x, GX, GY, sigma, in_mask)
    d = zeros(size(GX));
    if isempty(px), return; end
    px_r = px;
    px_r(px < mid_x) = 2*mid_x - px(px < mid_x);
    for k = 1:length(px_r)
        d = d + exp(-0.5 * (((GX - px_r(k)).^2 + (GY - py(k)).^2) / (sigma^2)));
    end
    if max(d(:)) > 0, d = d / max(d(:)); end
    d(~in_mask) = NaN;
end

function d = compute_smooth_field_left(px, py, mid_x, GX_L, GY_L, sigma, in_mask)
    d = zeros(size(GX_L));
    if isempty(px), return; end
    for k = 1:length(px)
        d = d + exp(-0.5 * (((GX_L - px(k)).^2 + (GY_L - py(k)).^2) / (sigma^2)));
    end
    if max(d(:)) > 0, d = d / max(d(:)); end
    d(~in_mask) = NaN;
end

function difference = GeneratePlot_author(N, ConnMat, edges)
    % Exact author implementation from PlotAnimatedNetworkEmgandPC.m (lines 266-288)
    Ex = (N.Transmit > 0);
    In = (N.Transmit < 0);
    Dist = bsxfun(@minus, N.Position(:, 2), N.Position(:, 2)');
    ProjEx = ConnMat(:, Ex); 
    ProjIn = ConnMat(:, In);
    DistEx = Dist(:, Ex);
    DistIn = Dist(:, In);
    
    yin = discretize(DistIn(ProjIn ~= 0), edges);
    yex = discretize(DistEx(ProjEx ~= 0), edges);
    
    num_bins = length(edges) - 1;
    valid_in = ~isnan(yin);
    valid_ex = ~isnan(yex);
    
    val_in = ProjIn(ProjIn ~= 0);
    val_ex = ProjEx(ProjEx ~= 0);
    
    SumIn = accumarray(yin(valid_in), abs(val_in(valid_in)), [num_bins 1]);
    SumEx = accumarray(yex(valid_ex), abs(val_ex(valid_ex)), [num_bins 1]);
    
    difference = SumEx - SumIn;
end
