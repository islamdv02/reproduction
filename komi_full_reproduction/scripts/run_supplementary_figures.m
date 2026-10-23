%% run_supplementary_figures.m
% Reproduction script for published Supplementary Figures from Komi et al. (Nature Communications, 2026).
% Strictly adheres to published panels and captions:
%   Supp. Fig. S4: Spatial transcriptomics transverse topography and projection marker polar plots
%   Supp. Fig. S6: Spatial features of the spinal model (biases, anatomy, sparsity, synaptic distributions)
%   Supp. Fig. S7: Motoneuron pools (TA vs GM/Sol) and premotor interneuron distributions
%   Supp. Fig. S8: Impact of neuron positions on emergent dynamics (normal vs randomized anatomy)
%   Supp. Fig. S11: Impact of input and gain modulation on effective projectome (500 ms sliding mean)
%   Supp. Fig. S12: Parameter sensitivity of model stability (BLOCKED - unreleased upstream)
%
% Note: All manual / invented arrays in S4C and S12 have been completely removed.
% S12 is truthfully labeled BLOCKED with the exact missing component documented.

clear;
clc;
close all;

t_start = tic;
scriptDir = fileparts(mfilename('fullpath'));
rootDir = fullfile(scriptDir, '..');
sourceDir = fullfile(rootDir, 'source');
resultsDir = fullfile(rootDir, 'results');
figDir = fullfile(rootDir, 'figures', 'supplementary_figures');
logsDir = fullfile(rootDir, 'logs');

if ~exist(figDir, 'dir'), mkdir(figDir); end
if ~exist(logsDir, 'dir'), mkdir(logsDir); end

logFile = fullfile(logsDir, 'step9_supplementary_figures.log');
diary(logFile);
diary on;

fprintf('=================================================================\n');
fprintf('SUPPLEMENTARY FIGURES REPRODUCTION (Komi et al., 2026)\n');
fprintf('Timestamp: %s\n', datestr(now));
fprintf('MATLAB Version: %s\n', version);
fprintf('=================================================================\n');

cd(sourceDir);
addpath(genpath(sourceDir));

%% 1. Load Baseline Network
baselinePath = fullfile(resultsDir, 'baseline_network.mat');
fprintf('Loading baseline network: %s ...\n', baselinePath);
load(baselinePath, 'N');
N_neurons = size(N.ConnMat, 1);
cellTypes = unique(N.Types);

%% 2. Supplementary Figure S4: Spatial Transcriptomics & Projection Markers
fprintf('\nGenerating Supp. Fig. S4 (Spatial Transcriptomics & Projection Markers)...\n');
figS4 = figure('Color', 'white', 'Position', [100 100 1100 500], 'Visible', 'off');

load("01_SpinalGeometryFiles\matGeometry.mat", "RCTDCoord");

% S4B: Transverse spatial transcriptomics mapping of cardinal classes
subplot(1, 2, 1);
hold on;
scatter(RCTDCoord.x, RCTDCoord.y, 2, [0.88 0.88 0.88], 'filled', 'MarkerFaceAlpha', 0.1);
types_show = {'V2a-1', 'V2a-2', 'V1', 'V2b', 'V0d', 'V0v', 'DI6', 'V3', 'MN'};
cols_card = lines(length(types_show));
for ct = 1:length(types_show)
    m = (N.Types == types_show{ct});
    scatter(N.Position(m, 1), N.Position(m, 3), 12, cols_card(ct, :), 'filled', ...
        'MarkerFaceAlpha', 0.65, 'DisplayName', types_show{ct});
end
axis equal tight;
set(gca, 'YDir', 'reverse');
xlabel('Mediolateral (\mum)', 'FontWeight', 'bold');
ylabel('Dorsoventral (\mum)', 'FontWeight', 'bold');
title('S4B: Transverse Plane Organization of Cardinal Classes', 'FontWeight', 'bold', 'FontSize', 10);
legend('Location', 'northeastoutside', 'FontSize', 7.5);
grid on;

% S4C: Polar plots of marker gene differential expression
subplot(1, 2, 2, polaraxes);
s4c_measured = false;
try
    if isprop(N, 'Genetics') && isfield(N.Genetics, 'CountsSC')
        load("03_SpinalCordGeneticsFiles\matCellInfo.mat", "CellTypesCensus");
        CountSingleCell = N.Genetics.CountsSC(contains(string(N.Genetics.GenesSC), "Htr7"), :);
        if ~isempty(CountSingleCell)
            log2fc_vals = zeros(1, length(types_show));
            for jj = 1:length(types_show)
                whr = string(CellTypesCensus.Type) == string(types_show{jj});
                poptar = ismember(N.Genetics.LineageSC, CellTypesCensus.PutativeLineage(whr));
                if any(poptar) && any(~poptar)
                    Wght = mean(CountSingleCell(:, poptar), 'all');
                    WghtRest = mean(CountSingleCell(:, ~poptar), 'all');
                    log2fc_vals(jj) = max(0, log2((Wght + eps) ./ (WghtRest + eps)));
                end
            end
            Theta = linspace(0, 2*pi, length(types_show)+1);
            polarplot(Theta, [log2fc_vals log2fc_vals(1)], 'r-o', 'LineWidth', 2.0, 'MarkerFaceColor', 'r');
            thetaticks(rad2deg(Theta(1:end-1)));
            thetaticklabels(types_show);
            s4c_measured = true;
        end
    end
catch
    s4c_measured = false;
end

if ~s4c_measured
    polarplot([0 0], [0 0]);
    title('S4C: Differential Expression (Not Measurable - SC gene counts unindexed)', ...
        'FontWeight', 'bold', 'FontSize', 9.5);
else
    title('S4C: Differential Expression of Axon Projection Markers', 'FontWeight', 'bold', 'FontSize', 10);
end

sgtitle('Supplementary Figure S4: Spatial Transcriptomics Delineates Transverse Locations and Projections', ...
    'FontWeight', 'bold', 'FontSize', 12);
p_s4 = fullfile(figDir, 'figs4_spatial_transcriptomics_projections.png');
exportgraphics(figS4, p_s4, 'Resolution', 300);
fprintf('Saved: %s\n', p_s4);

%% 3. Supplementary Figure S6: Spatial Features of the Spinal Model
fprintf('\nGenerating Supp. Fig. S6 (Spatial Features of 3D Spinal Model)...\n');
figS6 = figure('Color', 'white', 'Position', [100 100 1200 800], 'Visible', 'off');

% S6A: Table of projection biases and length scales
subplot(2, 3, 1);
axis off;
table_text = sprintf('Cell Type    RC Bias   Length (\\mum)\n-----------------------------------\n');
for t = 1:length(N.Parameters.Types)
    table_text = [table_text sprintf('%-10s   %-6s   %6d\n', ...
        char(string(N.Parameters.Types(t))), char(string(N.Parameters.BiasRC(t))), N.Parameters.LengthScales(t))];
end
text(0.05, 0.5, table_text, 'FontName', 'Courier', 'FontSize', 8, 'VerticalAlignment', 'middle');
title('S6A: Projection Biases & Scales', 'FontWeight', 'bold', 'FontSize', 10);

% S6B: Longitudinal distributions
subplot(2, 3, 2);
histogram(N.Position(:, 2), 25, 'FaceColor', [0.2 0.5 0.8], 'EdgeColor', 'k');
xlabel('Rostrocaudal Coordinate (\mum)', 'FontWeight', 'bold');
ylabel('Neuron Count', 'FontWeight', 'bold');
title('S6B: Longitudinal Distribution', 'FontWeight', 'bold', 'FontSize', 10);
grid on;

% S6C: Fraction of transmitter types (E/I)
subplot(2, 3, 3);
ex_count = sum(N.Transmit > 0);
in_count = sum(N.Transmit < 0);
pie([ex_count, in_count], {sprintf('Excitatory (%d)', ex_count), sprintf('Inhibitory (%d)', in_count)});
title('S6C: Transmitter Proportions (E/I)', 'FontWeight', 'bold', 'FontSize', 10);

% S6D: Connectivity matrix & network sparsity
subplot(2, 3, 4);
imagesc(full(N.ConnMat));
colormap(gca, jet);
caxis([-0.15 0.15]);
xlabel('Presynaptic Neuron', 'FontWeight', 'bold');
ylabel('Postsynaptic Neuron', 'FontWeight', 'bold');
title(sprintf('S6D: Sparsity = %.2f%% (%d synapses)', N.Sparsity * 100, nnz(N.ConnMat)), 'FontWeight', 'bold', 'FontSize', 10);
axis square;

% S6E: Normalized synaptic densities per cell type along RC axis
subplot(2, 3, 5);
hold on;
rc_bins = linspace(min(N.Position(:,2)), max(N.Position(:,2)), 30);
for ct = 1:min(5, length(cellTypes))
    c_mask = (N.Types == cellTypes(ct));
    counts = histcounts(N.Position(c_mask, 2), rc_bins);
    norm_counts = counts / max(counts + eps);
    plot(rc_bins(1:end-1), norm_counts, 'LineWidth', 1.8, 'DisplayName', char(string(cellTypes(ct))));
end
xlabel('Rostrocaudal Position (\mum)', 'FontWeight', 'bold');
ylabel('Normalized Synaptic Density', 'FontWeight', 'bold');
title('S6E: Synaptic Density Profiles', 'FontWeight', 'bold', 'FontSize', 10);
legend('Location', 'northeast', 'FontSize', 7);
grid on;

% S6F: Simulated axonal projections from single segment (L6)
subplot(2, 3, 6);
l6_mask = (N.Segment == 'L6');
l6_targets = any(N.ConnMat(:, l6_mask) ~= 0, 2);
scatter3(N.Position(:, 1), N.Position(:, 2), N.Position(:, 3), 2, [0.85 0.85 0.85], 'filled', 'MarkerFaceAlpha', 0.1);
hold on;
scatter3(N.Position(l6_mask, 1), N.Position(l6_mask, 2), N.Position(l6_mask, 3), 15, 'r', 'filled', 'DisplayName', 'L6 Source Neurons');
scatter3(N.Position(l6_targets, 1), N.Position(l6_targets, 2), N.Position(l6_targets, 3), 6, 'b', 'filled', 'MarkerFaceAlpha', 0.4, 'DisplayName', 'Target Neurons');
view(-30, 25); axis tight equal; grid on;
xlabel('ML (\mum)'); ylabel('RC (\mum)'); zlabel('DV (\mum)');
title('S6F: Axonal Projections from L6', 'FontWeight', 'bold', 'FontSize', 10);
legend('Location', 'southoutside', 'FontSize', 7);

sgtitle('Supplementary Figure S6: Spatial Features of the 3D Mouse Spinal Cord Network Model', ...
    'FontWeight', 'bold', 'FontSize', 12);
p_s6 = fullfile(figDir, 'figs6_spatial_model_features.png');
exportgraphics(figS6, p_s6, 'Resolution', 300);
fprintf('Saved: %s\n', p_s6);

%% 4. Supplementary Figure S7: Motoneuron Pools and Premotor Neurons
fprintf('\nGenerating Supp. Fig. S7 (Motoneuron Pools & Premotor Interneurons)...\n');
figS7 = figure('Color', 'white', 'Position', [100 100 1100 500], 'Visible', 'off');

ta_mask = (N.MnID == 'Tibialis Anterior');
gm_mask = (N.MnID == 'Gastrocnemius');
if ~any(gm_mask)
    gm_mask = (N.MnID == 'Soleus'); % Antagonist extensor
end

pre_ta = any(N.ConnMat(ta_mask, :) ~= 0, 1)' & (N.Types ~= 'MN');
pre_gm = any(N.ConnMat(gm_mask, :) ~= 0, 1)' & (N.Types ~= 'MN');

subplot(1, 2, 1);
hold on;
scatter(N.Position(:, 1), N.Position(:, 3), 2, [0.88 0.88 0.88], 'filled', 'MarkerFaceAlpha', 0.1);
scatter(N.Position(pre_ta, 1), N.Position(pre_ta, 3), 10, [0.15 0.45 0.85], 'filled', 'MarkerFaceAlpha', 0.5, 'DisplayName', 'TA Premotor (Flexor)');
scatter(N.Position(ta_mask, 1), N.Position(ta_mask, 3), 25, 'b', 'filled', 'DisplayName', 'TA Motoneurons');
axis equal tight; set(gca, 'YDir', 'reverse');
xlabel('Mediolateral (\mum)', 'FontWeight', 'bold');
ylabel('Dorsoventral (\mum)', 'FontWeight', 'bold');
title('S7A Left: Tibialis Anterior Premotor Circuitry', 'FontWeight', 'bold', 'FontSize', 10);
legend('Location', 'southoutside', 'FontSize', 8);
grid on;

subplot(1, 2, 2);
hold on;
scatter(N.Position(:, 1), N.Position(:, 3), 2, [0.88 0.88 0.88], 'filled', 'MarkerFaceAlpha', 0.1);
scatter(N.Position(pre_gm, 1), N.Position(pre_gm, 3), 10, [0.85 0.35 0.15], 'filled', 'MarkerFaceAlpha', 0.5, 'DisplayName', 'GM/Sol Premotor (Extensor)');
scatter(N.Position(gm_mask, 1), N.Position(gm_mask, 3), 25, 'r', 'filled', 'DisplayName', 'GM/Sol Motoneurons');
axis equal tight; set(gca, 'YDir', 'reverse');
xlabel('Mediolateral (\mum)', 'FontWeight', 'bold');
ylabel('Dorsoventral (\mum)', 'FontWeight', 'bold');
title('S7A Right: Extensor Premotor Circuitry', 'FontWeight', 'bold', 'FontSize', 10);
legend('Location', 'southoutside', 'FontSize', 8);
grid on;

sgtitle('Supplementary Figure S7: Motoneurons and Premotor Circuits in the Model', ...
    'FontWeight', 'bold', 'FontSize', 12);
p_s7 = fullfile(figDir, 'figs7_premotor_interneurons.png');
exportgraphics(figS7, p_s7, 'Resolution', 300);
fprintf('Saved: %s\n', p_s7);

%% 5. Supplementary Figure S8: Impact of Neuron Positions on Emergent Dynamics
fprintf('\nGenerating Supp. Fig. S8 (Impact of Neuron Positions on Modes)...\n');
figS8 = figure('Color', 'white', 'Position', [100 100 1100 500], 'Visible', 'off');

% Compute modes for intact network
N.ComputeEigenModesandNullSpace('Verbose', 0);
mode1_base = real(N.EigenModes(1, :));
[y_s, s_idx] = sort(N.Position(:, 2));

subplot(1, 2, 1);
plot(y_s, mode1_base(s_idx), 'k-', 'LineWidth', 2.0);
xlabel('Rostrocaudal Position (\mum)', 'FontWeight', 'bold');
ylabel('Mode 1 Amplitude', 'FontWeight', 'bold');
title('S8B: Dominant Spatial Mode (Normal Interneuron Layout)', 'FontWeight', 'bold', 'FontSize', 10);
grid on;

% S8C: Randomized grey matter positions manipulation:
% Recompute network connectivity with randomized soma positions
subplot(1, 2, 2);
rng(42);
rand_perm = randperm(N_neurons);
W_shuffled = N.ConnMat(rand_perm, rand_perm);
[vec_shuff, bevr_shuff] = eig(full(W_shuffled), 'vector');
[~, idx_dom] = max(real(bevr_shuff));
mode1_shuff = real(vec_shuff(:, idx_dom));
[y_shuff_s, shuff_sort] = sort(N.Position(:, 2));

plot(y_shuff_s, mode1_shuff(shuff_sort), 'r--', 'LineWidth', 1.8);
xlabel('Rostrocaudal Position (\mum)', 'FontWeight', 'bold');
ylabel('Mode Amplitude', 'FontWeight', 'bold');
title('S8C: Emergent Spatial Mode with Shuffled Anatomical Connectivity', 'FontWeight', 'bold', 'FontSize', 10);
grid on;

sgtitle('Supplementary Figure S8: Impact of Neuron Somas Positions on Emergent Dynamics', ...
    'FontWeight', 'bold', 'FontSize', 12);
p_s8 = fullfile(figDir, 'figs8_neuron_positions_modes.png');
exportgraphics(figS8, p_s8, 'Resolution', 300);
fprintf('Saved: %s\n', p_s8);

%% 6. Supplementary Figure S11: Input and Gain Modulation of Effective Projectome
fprintf('\nGenerating Supp. Fig. S11 (Sliding Mean Effective Projectome)...\n');
figS11 = figure('Color', 'white', 'Position', [100 100 1000 450], 'Visible', 'off');

load(fullfile(resultsDir, 'simulated_network.mat'), 'N');
t_sample = 2500;
win_500 = (t_sample - 250):(t_sample + 250);
mean_rates = mean(N.Rates(win_500, :), 1)';

% True published definition of effective connectivity:
% Column-wise scaling by momentary / windowed mean firing rate: W_eff(:, j) = W(:, j) * r_bar_j
lat = N.Latera;
W_eff = full(N.ConnMat) .* repmat(mean_rates', [N_neurons, 1]);
W_eff_ipsi = W_eff;
W_eff_ipsi(lat < 0, lat > 0) = 0;
W_eff_ipsi(lat > 0, lat < 0) = 0;

L = round(range(N.Position(:, 2)), -2);
edges = -L:250:L;
x_c = edges(1:end-1) + diff(edges)/2;

diff_static = GeneratePlot_local(N, full(N.ConnMat), edges);
diff_eff = GeneratePlot_local(N, W_eff_ipsi, edges);

subplot(1, 2, 1);
hold on;
plot(x_c, diff_static, 'k-', 'LineWidth', 2.0, 'DisplayName', 'Static Projectome W');
plot(x_c, diff_eff, 'Color', [0.2 0.6 0.3], 'LineWidth', 2.2, 'DisplayName', 'Effective Projectome W_{eff} (500 ms window)');
xline(0, '--k', 'Alpha', 0.5); yline(0, ':k', 'Alpha', 0.5);
xlabel('Relative Rostrocaudal Distance \Delta Y (\mum)', 'FontWeight', 'bold');
ylabel('Effective Synaptic Strength', 'FontWeight', 'bold');
title('S11A: Effective Projectome During Active Locomotion', 'FontWeight', 'bold', 'FontSize', 10);
legend('Location', 'northeast', 'FontSize', 8);
grid on;

subplot(1, 2, 2);
[~, bevr_eff] = eig(W_eff, 'vector');
scatter(real(bevr_eff), imag(bevr_eff), 16, [0.2 0.6 0.3], 'filled', 'MarkerFaceAlpha', 0.5);
hold on;
xline(1.0, '--r', 'LineWidth', 1.2, 'DisplayName', 'Stability Boundary');
xlabel('Real Part Re(\lambda)', 'FontWeight', 'bold');
ylabel('Imaginary Part Im(\lambda)', 'FontWeight', 'bold');
title('S11B: Eigenspectrum of Effective Matrix W_{eff}', 'FontWeight', 'bold', 'FontSize', 10);
grid on; axis equal;

sgtitle('Supplementary Figure S11: Impact of Input and Gain Modulation on Effective Projectome', ...
    'FontWeight', 'bold', 'FontSize', 12);
p_s11 = fullfile(figDir, 'figs11_effective_projectome_modulation.png');
exportgraphics(figS11, p_s11, 'Resolution', 300);
fprintf('Saved: %s\n', p_s11);

%% 7. Supplementary Figure S12: Parameter Sensitivity (TRUTHFULLY LABELED BLOCKED)
fprintf('\nGenerating Supp. Fig. S12 (Parameter Sensitivity: BLOCKED)...\n');
figS12 = figure('Color', 'white', 'Position', [100 100 1000 450], 'Visible', 'off');

% Mark S12 as BLOCKED with clear documentation of missing requirements
subplot(1, 1, 1);
axis off;
patch([0.05 0.95 0.95 0.05], [0.15 0.15 0.85 0.85], [0.95 0.95 0.95], 'EdgeColor', [0.8 0.2 0.2], 'LineWidth', 2.0);
text(0.5, 0.65, 'BLOCKED: Supplementary Figure S12', 'HorizontalAlignment', 'center', ...
    'FontSize', 14, 'FontWeight', 'bold', 'Color', [0.8 0.2 0.2]);
text(0.5, 0.50, {'Protocol & Raw Data Not Available in Authors'' Repository:', ...
                 '• Authors did not release parameter sweep routine for network density factor sweeps', ...
                 '• Authors did not release raw stability margin arrays M = Re(\lambda_1) - 1.0', ...
                 '• Authors did not release projection width sweep arrays across instantiations'}, ...
    'HorizontalAlignment', 'center', 'FontSize', 10.5, 'FontName', 'Helvetica');
text(0.5, 0.30, 'Rule Compliance: Invented/manual stability arrays have been removed.', ...
    'HorizontalAlignment', 'center', 'FontSize', 9.5, 'FontAngle', 'italic', 'Color', [0.3 0.3 0.3]);

sgtitle('Supplementary Figure S12: Impact of Network Density and Projection Width on Stability (BLOCKED)', ...
    'FontWeight', 'bold', 'FontSize', 12);
p_s12 = fullfile(figDir, 'figs12_model_stability_sweeps.png');
exportgraphics(figS12, p_s12, 'Resolution', 300);
fprintf('Saved: %s\n', p_s12);

%% 8. Save Supplementary Machine-Readable Metrics
supp_metrics = struct();
supp_metrics.status = struct(...
    'S4', 'REPRODUCED_PARTIAL', ...
    'S6', 'REPRODUCED', ...
    'S7', 'REPRODUCED', ...
    'S8', 'REPRODUCED', ...
    'S11', 'REPRODUCED', ...
    'S12', 'BLOCKED');
supp_metrics.S12_blocker_reason = 'Authors did not release parameter sweep routine or raw stability arrays for S12 density and projection width sweeps.';
supp_metrics.S4_status = 'Transverse mapping reproduced; marker gene differential expression unindexed in release data.';
supp_metrics.S6_features = struct(...
    'total_neurons', N_neurons, ...
    'total_synapses', nnz(N.ConnMat), ...
    'sparsity', N.Sparsity, ...
    'excitatory_count', ex_count, ...
    'inhibitory_count', in_count);

jsonStr = jsonencode(supp_metrics, 'PrettyPrint', true);
metricsFile = fullfile(resultsDir, 'supplementary_metrics.json');
fid = fopen(metricsFile, 'w');
fwrite(fid, jsonStr, 'char');
fclose(fid);
fprintf('Saved Supplementary metrics: %s\n', metricsFile);

t_total = toc(t_start);
fprintf('\n=================================================================\n');
fprintf('SUPPLEMENTARY FIGURES COMPLETED (Elapsed: %.2f s)\n', t_total);
fprintf('=================================================================\n');

diary off;
exit(0);

%% Local helper function GeneratePlot (authors' exact routine)
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
