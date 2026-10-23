%% test_ta_recomputation.m
% Validates the TA relocation and connectivity recomputation for Condition C.
clear; clc;
scriptDir = fileparts(mfilename('fullpath'));
rootDir = fullfile(scriptDir, '..', '..', '..');
sourceDir = fullfile(rootDir, 'source');
resultsDir = fullfile(rootDir, 'results');
compatDir = fullfile(rootDir, 'scripts', 'compat');

cd(sourceDir);
addpath(genpath(sourceDir));
addpath(compatDir);

fprintf('Loading baseline network...\n');
load(fullfile(resultsDir, 'baseline_network.mat'), 'N');
N_neurons = size(N.ConnMat, 1);
ta_idx = find(string(N.Types) == 'MN' & string(N.MnID) == 'Tibialis Anterior');
non_ta_idx = setdiff(1:N_neurons, ta_idx);

fprintf('Network N=%d | TA count=%d (Left=%d, Right=%d)\n', ...
    N_neurons, length(ta_idx), sum(N.Latera(ta_idx) < 0), sum(N.Latera(ta_idx) > 0));

% Current TA coordinates
ta_rc_orig = N.Position(ta_idx, 2);
fprintf('Baseline TA RC range: [%.1f, %.1f], mean: %.1f\n', ...
    min(ta_rc_orig), max(ta_rc_orig), mean(ta_rc_orig));

% Relocation mapping: L4-L5 target span [5600, 7900] um (Bácskai et al., 2014)
% Affine mapping preserving within-pool relative RC structure
target_min = 5600.0;
target_max = 7900.0;
orig_min = min(ta_rc_orig);
orig_max = max(ta_rc_orig);

ta_rc_new = target_min + (ta_rc_orig - orig_min) * ((target_max - target_min) / (orig_max - orig_min));
fprintf('Relocated TA RC range: [%.1f, %.1f], mean: %.1f\n', ...
    min(ta_rc_new), max(ta_rc_new), mean(ta_rc_new));

% Target segment assignments (L4 boundary: 5507.4 - 6823.2; L5 boundary: 6808.7 - 8031.7)
l4_l5_border = 6808.7;
new_segs = repmat(categorical({'L4'}), length(ta_idx), 1);
new_segs(ta_rc_new >= l4_l5_border) = categorical({'L5'});
fprintf('New segment assignments: L4=%d, L5=%d\n', ...
    sum(new_segs == 'L4'), sum(new_segs == 'L5'));

% Extract parameters needed for connection probability recomputation
P = N.Parameters;
[~, IxT] = ismember(N.Types, P.Types);
PosX = N.Position(:, 2)'; % 1 x N
PosY = N.Position(:, 1)'; % 1 x N
PosZ = N.Position(:, 3)'; % 1 x N
Lat = N.Latera;           % N x 1

E = reshape(N.Transmit > 0, 1, []);
I = reshape(N.Transmit < 0, 1, []);
CellIndex = IxT;
SynStrengths_all = reshape(P.SynStrengths(IxT), 1, []);

projwidth = 500;
bRC = unique(P.BiasRC);
bML = unique(P.BiasML);
bDV = unique(P.BiasDV);
bCI = unique(P.BiasContraIpsi);

% Compute hemisphere rescale factors from baseline network
w_base = N.ConnMat;
r_pos = numel(w_base(w_base > 0)) / numel(w_base(w_base < 0));
sp = nnz(~w_base) / numel(w_base);
rescale_factor = sqrt(sp * (1.0 - sp) * (1.0 + r_pos^2) / 2) * sqrt(length(w_base));
fprintf('Baseline hemisphere rescale factor: %.4f\n', rescale_factor);

% Set RNG seed for connection recomputation (deterministic pairing)
rng(42, 'twister');

% Recompute incoming rows for relocated TA neurons
w_new = w_base;
recomputed_rows = 0;

for k = 1:length(ta_idx)
    i = ta_idx(k);
    pos_i_rc = ta_rc_new(k);
    pos_i_ml = PosY(i);
    pos_i_dv = PosZ(i);
    lat_i = Lat(i);
    
    % Distances from all presynaptic neurons j to postsynaptic i
    % DistRC(1, j) = PosX(i) - PosX(j)
    dRC = pos_i_rc - PosX;
    dML = abs(pos_i_ml) - abs(PosY);
    dDV = pos_i_dv - PosZ;
    dCI = lat_i * Lat';
    
    biasRC = nan(1, N_neurons);
    biasML = nan(1, N_neurons);
    biasDV = nan(1, N_neurons);
    biasCI = ones(1, N_neurons);
    
    % Rostrocaudal bias
    for brc = bRC
        ioi = ismember(N.Types, P.Types(P.BiasRC == brc))';
        switch brc
            case 'cau'
                divider = reshape(P.LengthScales(CellIndex), 1, []);
                divider = divider + normrnd(0, mean(divider)/10, size(divider));
                biasRC(dRC > 0 & ioi) = (dRC(dRC > 0 & ioi) - divider(dRC > 0 & ioi)) / projwidth;
                biasRC(dRC < 0 & ioi) = (dRC(dRC < 0 & ioi) - divider(dRC < 0 & ioi)) / projwidth;
            case 'ro'
                divider = reshape(P.LengthScales(CellIndex), 1, []);
                divider = divider + normrnd(0, mean(divider)/10, size(divider));
                biasRC(dRC > 0 & ioi) = (dRC(dRC > 0 & ioi) + divider(dRC > 0 & ioi)) / projwidth;
                biasRC(dRC < 0 & ioi) = (dRC(dRC < 0 & ioi) + divider(dRC < 0 & ioi)) / projwidth;
            case 'bi'
                divider = reshape(P.LengthScales(CellIndex(ioi)), 1, []);
                divider = divider + normrnd(0, divider/10, size(divider));
                biasRC(ioi) = (abs(dRC(ioi)) - divider) / projwidth;
            case 'loc'
                divider = reshape(P.LengthScales(CellIndex), 1, []);
                divider = divider + normrnd(0, mean(divider)/10, size(divider));
                biasRC(dRC > 0 & ioi) = dRC(dRC > 0 & ioi) ./ divider(dRC > 0 & ioi);
                biasRC(dRC < 0 & ioi) = dRC(dRC < 0 & ioi) ./ divider(dRC < 0 & ioi);
        end
        biasRC(dRC == 0 & ioi) = 0;
    end
    
    % Mediolateral bias
    for bml = bML
        ioi = ismember(N.Types, P.Types(P.BiasML == bml))';
        switch bml
            case 'lat'
                biasML(dML > 0 & ioi) = abs(dML(dML > 0 & ioi)) ./ (2 * projwidth);
                biasML(dML < 0 & ioi) = abs(dML(dML < 0 & ioi)) ./ (projwidth / 5);
            case 'med'
                biasML(dML > 0 & ioi) = abs(dML(dML > 0 & ioi)) ./ (projwidth / 5);
                biasML(dML < 0 & ioi) = abs(dML(dML < 0 & ioi)) ./ (2 * projwidth);
            case 'loc'
                biasML(ioi) = abs(dML(ioi)) ./ (projwidth / 5);
        end
        biasML(dML == 0 & ioi) = 0;
    end
    
    % Dorsoventral bias
    for bdv = bDV
        ioi = ismember(N.Types, P.Types(P.BiasDV == bdv))';
        switch bdv
            case 'dor'
                biasDV(dDV > 0 & ioi) = abs(dDV(dDV > 0 & ioi)) ./ (2 * projwidth);
                biasDV(dDV < 0 & ioi) = abs(dDV(dDV < 0 & ioi)) ./ (projwidth / 5);
            case 'ven'
                biasDV(dDV > 0 & ioi) = abs(dDV(dDV > 0 & ioi)) ./ (projwidth / 5);
                biasDV(dDV < 0 & ioi) = abs(dDV(dDV < 0 & ioi)) ./ (2 * projwidth);
            case 'loc'
                biasDV(ioi) = abs(dDV(ioi)) ./ (projwidth / 5);
        end
        biasDV(dDV == 0 & ioi) = 0;
    end
    
    % Contra/Ipsi bias
    for bci = bCI
        ioi = ismember(N.Types, P.Types(P.BiasContraIpsi == bci))';
        switch bci
            case 'contra'
                biasCI(dCI < 0 & ioi) = 1;
                biasCI(dCI > 0 & ioi) = 0;
            case 'ipsi'
                biasCI(dCI > 0 & ioi) = 1;
                biasCI(dCI < 0 & ioi) = 0;
            case 'bi'
                biasCI(dCI > 0 & ioi) = 0.2;
                biasCI(dCI < 0 & ioi) = 1;
        end
    end
    
    % BiasPop: for MN postsynaptic, interneurons have 1.0, MN has 0.1
    biasPop = ones(1, N_neurons);
    biasPop(string(N.Types) == 'MN') = 0.1;
    
    % Synaptic probability
    prob = geomean([normpdf(biasML, 0, 1) ./ normpdf(0, 0, 1); ...
                    normpdf(biasDV, 0, 1) ./ normpdf(0, 0, 1); ...
                    normpdf(biasRC, 0, 1) ./ normpdf(0, 0, 1)], 1, 'omitnan') .* ...
           biasCI .* biasPop;
    prob(isnan(prob)) = 0;
    
    % Sparsifier and synaptic strength
    sparsifier = binornd(1, prob);
    conn_row = normrnd(1, 0.1, [1, N_neurons]);
    conn_row(E) = abs(conn_row(E)) .* SynStrengths_all(E);
    conn_row(I) = -abs(conn_row(I)) .* SynStrengths_all(I);
    conn_row = conn_row .* sparsifier;
    
    % Self-synapse removal
    conn_row(i) = 0;
    
    % UnifyMNConnectivity: MNs only connect to same pool
    other_mns = setdiff(find(string(N.Types) == 'MN'), ta_idx);
    conn_row(other_mns) = 0;
    
    % BalanceConnectivity (row balance)
    bal = sum(conn_row);
    j_pos = find(conn_row > 0);
    j_neg = find(conn_row < 0);
    if ~isempty(j_pos) && ~isempty(j_neg)
        bp = sum(conn_row(j_pos)) - (bal / 2);
        bn = sum(conn_row(j_neg)) - (bal / 2);
        facp = bp / sum(conn_row(j_pos));
        facn = bn / sum(conn_row(j_neg));
        conn_row(j_pos) = conn_row(j_pos) * facp;
        conn_row(j_neg) = conn_row(j_neg) * facn;
    end
    
    % Rescale
    conn_row = conn_row ./ rescale_factor;
    
    w_new(i, :) = conn_row;
    recomputed_rows = recomputed_rows + 1;
end

fprintf('Successfully recomputed %d TA rows.\n', recomputed_rows);

% Verification checks:
w_unaffected_base = w_base(non_ta_idx, non_ta_idx);
w_unaffected_new  = w_new(non_ta_idx, non_ta_idx);
diff_unaffected = max(abs(w_unaffected_base(:) - w_unaffected_new(:)));
fprintf('Max difference in unaffected connections: %.4e (MUST BE ZERO)\n', diff_unaffected);
assert(diff_unaffected == 0, 'Unaffected connections changed!');

w_ta_new = w_new(ta_idx, :);
fprintf('New TA in-degree: min=%d, mean=%.1f, max=%d\n', ...
    min(sum(w_ta_new ~= 0, 2)), mean(sum(w_ta_new ~= 0, 2)), max(sum(w_ta_new ~= 0, 2)));
fprintf('New TA row sum abs: min=%.4e, mean=%.4e, max=%.4e\n', ...
    min(abs(sum(w_ta_new, 2))), mean(abs(sum(w_ta_new, 2))), max(abs(sum(w_ta_new, 2))));
fprintf('New TA pos weight sum: mean=%.3f, neg weight sum: mean=%.3f\n', ...
    mean(sum(w_ta_new .* (w_ta_new > 0), 2)), mean(sum(w_ta_new .* (w_ta_new < 0), 2)));

% Check distribution of presynaptic interneuron RC positions before vs after
w_ta_old = w_base(ta_idx, :);
in_syn_old_rc = [];
in_syn_new_rc = [];
for k = 1:length(ta_idx)
    i = ta_idx(k);
    j_old = find(w_ta_old(k, :) ~= 0 & string(N.Types)' ~= 'MN');
    j_new = find(w_ta_new(k, :) ~= 0 & string(N.Types)' ~= 'MN');
    in_syn_old_rc = [in_syn_old_rc, N.Position(j_old, 2)'];
    in_syn_new_rc = [in_syn_new_rc, N.Position(j_new, 2)'];
end
fprintf('\nPresynaptic interneuron RC position:\n');
fprintf('  Baseline TA inputs: mean=%.1f um, range=[%.1f, %.1f]\n', ...
    mean(in_syn_old_rc), min(in_syn_old_rc), max(in_syn_old_rc));
fprintf('  Relocated TA inputs: mean=%.1f um, range=[%.1f, %.1f]\n', ...
    mean(in_syn_new_rc), min(in_syn_new_rc), max(in_syn_new_rc));
fprintf('Mean shift in presynaptic interneuron territory: +%.1f um\n', ...
    mean(in_syn_new_rc) - mean(in_syn_old_rc));

fprintf('VERIFICATION SUCCESSFUL!\n');
exit(0);
