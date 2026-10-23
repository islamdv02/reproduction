%% run_ta_simulation_test.m
% Simulates Condition C and compares firing rates and phase with Condition A (Baseline).
clear; clc;
scriptDir = fileparts(mfilename('fullpath'));
rootDir = fullfile(scriptDir, '..', '..', '..');
sourceDir = fullfile(rootDir, 'source');
resultsDir = fullfile(rootDir, 'results');
compatDir = fullfile(rootDir, 'scripts', 'compat');

cd(sourceDir);
addpath(genpath(sourceDir));
addpath(compatDir);

fprintf('=================================================================\n');
fprintf('CONDITION C SIMULATION TEST: Relocated TA with Updated Connectivity\n');
fprintf('=================================================================\n');

% 1. Load baseline simulated network to have Condition A
fprintf('Loading baseline simulated network (Condition A)...\n');
load(fullfile(resultsDir, 'simulated_network.mat'), 'N');
N_base = N;
R_base = N_base.Rates; % 22000 x 4934
pos_base = N_base.Position;

% Identify key muscle pools
ta_idx = find(string(N_base.Types) == 'MN' & string(N_base.MnID) == 'Tibialis Anterior');
gm_idx = find(string(N_base.Types) == 'MN' & string(N_base.MnID) == 'Gastrocnemius');
sol_idx = find(string(N_base.Types) == 'MN' & string(N_base.MnID) == 'Soleus');
vm_idx = find(string(N_base.Types) == 'MN' & string(N_base.MnID) == 'Vastus Medialis');
bf_idx = find(string(N_base.Types) == 'MN' & string(N_base.MnID) == 'Biceps Femoris');

% Relocation mapping
target_min = 5600.0;
target_max = 7900.0;
orig_min = min(pos_base(ta_idx, 2));
orig_max = max(pos_base(ta_idx, 2));
ta_rc_new = target_min + (pos_base(ta_idx, 2) - orig_min) * ((target_max - target_min) / (orig_max - orig_min));

l4_l5_border = 6808.7;
new_segs = repmat(categorical({'L4'}), length(ta_idx), 1);
new_segs(ta_rc_new >= l4_l5_border) = categorical({'L5'});

% Build Condition C Network Object
N_C = copy(N_base);
N_C.Position(ta_idx, 2) = ta_rc_new;
N_C.Segment(ta_idx) = new_segs;

% Recompute TA connectivity
P = N_base.Parameters;
[~, IxT] = ismember(N_base.Types, P.Types);
PosX = N_base.Position(:, 2)';
PosY = N_base.Position(:, 1)';
PosZ = N_base.Position(:, 3)';
Lat = N_base.Latera;
N_neurons = size(N_base.ConnMat, 1);

E = reshape(N_base.Transmit > 0, 1, []);
I = reshape(N_base.Transmit < 0, 1, []);
SynStrengths_all = reshape(P.SynStrengths(IxT), 1, []);

projwidth = 500;
bRC = unique(P.BiasRC);
bML = unique(P.BiasML);
bDV = unique(P.BiasDV);
bCI = unique(P.BiasContraIpsi);

w_base = N_base.ConnMat;
r_pos = numel(w_base(w_base > 0)) / numel(w_base(w_base < 0));
sp = nnz(~w_base) / numel(w_base);
rescale_factor = sqrt(sp * (1.0 - sp) * (1.0 + r_pos^2) / 2) * sqrt(length(w_base));

rng(42, 'twister');
w_C = w_base;

for k = 1:length(ta_idx)
    i = ta_idx(k);
    pos_i_rc = ta_rc_new(k);
    pos_i_ml = PosY(i);
    pos_i_dv = PosZ(i);
    lat_i = Lat(i);
    
    dRC = pos_i_rc - PosX;
    dML = abs(pos_i_ml) - abs(PosY);
    dDV = pos_i_dv - PosZ;
    dCI = lat_i * Lat';
    
    biasRC = nan(1, N_neurons);
    biasML = nan(1, N_neurons);
    biasDV = nan(1, N_neurons);
    biasCI = ones(1, N_neurons);
    
    for brc = bRC
        ioi = ismember(N_base.Types, P.Types(P.BiasRC == brc))';
        switch brc
            case 'cau'
                divider = reshape(P.LengthScales(IxT), 1, []);
                divider = divider + normrnd(0, mean(divider)/10, size(divider));
                biasRC(dRC > 0 & ioi) = (dRC(dRC > 0 & ioi) - divider(dRC > 0 & ioi)) / projwidth;
                biasRC(dRC < 0 & ioi) = (dRC(dRC < 0 & ioi) - divider(dRC < 0 & ioi)) / projwidth;
            case 'ro'
                divider = reshape(P.LengthScales(IxT), 1, []);
                divider = divider + normrnd(0, mean(divider)/10, size(divider));
                biasRC(dRC > 0 & ioi) = (dRC(dRC > 0 & ioi) + divider(dRC > 0 & ioi)) / projwidth;
                biasRC(dRC < 0 & ioi) = (dRC(dRC < 0 & ioi) + divider(dRC < 0 & ioi)) / projwidth;
            case 'bi'
                divider = reshape(P.LengthScales(IxT(ioi)), 1, []);
                divider = divider + normrnd(0, divider/10, size(divider));
                biasRC(ioi) = (abs(dRC(ioi)) - divider) / projwidth;
            case 'loc'
                divider = reshape(P.LengthScales(IxT), 1, []);
                divider = divider + normrnd(0, mean(divider)/10, size(divider));
                biasRC(dRC > 0 & ioi) = dRC(dRC > 0 & ioi) ./ divider(dRC > 0 & ioi);
                biasRC(dRC < 0 & ioi) = dRC(dRC < 0 & ioi) ./ divider(dRC < 0 & ioi);
        end
        biasRC(dRC == 0 & ioi) = 0;
    end
    
    for bml = bML
        ioi = ismember(N_base.Types, P.Types(P.BiasML == bml))';
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
    
    for bdv = bDV
        ioi = ismember(N_base.Types, P.Types(P.BiasDV == bdv))';
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
    
    for bci = bCI
        ioi = ismember(N_base.Types, P.Types(P.BiasContraIpsi == bci))';
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
    
    biasPop = ones(1, N_neurons);
    biasPop(string(N_base.Types) == 'MN') = 0.1;
    
    prob = geomean([normpdf(biasML, 0, 1) ./ normpdf(0, 0, 1); ...
                    normpdf(biasDV, 0, 1) ./ normpdf(0, 0, 1); ...
                    normpdf(biasRC, 0, 1) ./ normpdf(0, 0, 1)], 1, 'omitnan') .* ...
           biasCI .* biasPop;
    prob(isnan(prob)) = 0;
    
    sparsifier = binornd(1, prob);
    conn_row = normrnd(1, 0.1, [1, N_neurons]);
    conn_row(E) = abs(conn_row(E)) .* SynStrengths_all(E);
    conn_row(I) = -abs(conn_row(I)) .* SynStrengths_all(I);
    conn_row = conn_row .* sparsifier;
    conn_row(i) = 0;
    
    other_mns = setdiff(find(string(N_base.Types) == 'MN'), ta_idx);
    conn_row(other_mns) = 0;
    
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
    
    conn_row = conn_row ./ rescale_factor;
    w_C(i, :) = conn_row;
end

N_C.ConnMat = w_C;

% 2. Run Paired Simulation
t_steps = 22000;
simSeed = 5;
I_e = zeros(N_neurons, t_steps);
I_e(:, :) = 25;

fprintf('Running Condition C simulation (%d steps, seed=%d)...\n', t_steps, simSeed);
ticSim = tic;
N_C.Simulate(t_steps, 'I_e', I_e, 'seed', simSeed);
t_sim = toc(ticSim);
fprintf('Simulation completed in %.2f s (%.2f s/s).\n', t_sim, (t_steps/1000)/t_sim);

R_C = N_C.Rates;

% 3. Compare Non-TA Firing Rates
non_ta_diff = max(abs(R_base(:, other_mns) - R_C(:, other_mns)), [], 'all');
fprintf('Max difference in other MN firing rates: %.4e (MUST BE ZERO)\n', non_ta_diff);

% 4. Analyze TA Firing Rates and Phase
ta_rate_base = mean(R_base(:, ta_idx), 2);
ta_rate_C    = mean(R_C(:, ta_idx), 2);
gm_rate      = mean(R_base(:, gm_idx), 2);
sol_rate     = mean(R_base(:, sol_idx), 2);
vm_rate      = mean(R_base(:, vm_idx), 2);
bf_rate      = mean(R_base(:, bf_idx), 2);

fprintf('\nMean Firing Rates (Hz):\n');
fprintf('  TA Baseline (L2-L4): %.2f Hz\n', mean(ta_rate_base));
fprintf('  TA Condition C (L4-L5): %.2f Hz\n', mean(ta_rate_C));
fprintf('  GM: %.2f Hz | Sol: %.2f Hz | VM: %.2f Hz | BF: %.2f Hz\n', ...
    mean(gm_rate), mean(sol_rate), mean(vm_rate), mean(bf_rate));

% Quick cross-correlation analysis on steady-state window (5000 to 20000 ms)
t_win = 5000:20000;
[c_base_gm, lags] = xcorr(ta_rate_base(t_win) - mean(ta_rate_base(t_win)), ...
                          gm_rate(t_win) - mean(gm_rate(t_win)), 500, 'coeff');
[c_C_gm, ~]       = xcorr(ta_rate_C(t_win) - mean(ta_rate_C(t_win)), ...
                          gm_rate(t_win) - mean(gm_rate(t_win)), 500, 'coeff');

fprintf('\nZero-lag cross-correlation with Gastrocnemius (GM):\n');
fprintf('  Condition A (Baseline): r = %.3f\n', c_base_gm(lags == 0));
fprintf('  Condition C (Relocated): r = %.3f\n', c_C_gm(lags == 0));

[c_base_sol, ~] = xcorr(ta_rate_base(t_win) - mean(ta_rate_base(t_win)), ...
                        sol_rate(t_win) - mean(sol_rate(t_win)), 500, 'coeff');
[c_C_sol, ~]    = xcorr(ta_rate_C(t_win) - mean(ta_rate_C(t_win)), ...
                        sol_rate(t_win) - mean(sol_rate(t_win)), 500, 'coeff');
fprintf('Zero-lag cross-correlation with Soleus (Sol):\n');
fprintf('  Condition A (Baseline): r = %.3f\n', c_base_sol(lags == 0));
fprintf('  Condition C (Relocated): r = %.3f\n', c_C_sol(lags == 0));

fprintf('\nCondition C Simulation Test COMPLETED SUCCESSFULLY!\n');
exit(0);
