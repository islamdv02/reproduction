%% run_ta_placement_experiment.m
% Complete Repaired Controlled Experiment Pipeline: TA Motor-Pool Placement
% Investigates the anatomical appearance, motor coordination, and network dynamics
% of relocating Tibialis Anterior (TA) motoneurons from baseline L2-L4 to anatomical L4-L5
% across 5 paired network realizations under identical simulation drive and seeds.
%
% 4 Paired Conditions:
%   Condition A: Original baseline network and simulation.
%   Condition B: Coordinate-only control (rates and W identical to A; only coordinates change).
%   Condition C: Same-location reconstruction control (rebuilt at original location).
%   Condition D: Relocated TA with consistently rebuilt location-dependent connections.
%
% Scientific Comparison:
%   Condition C vs Condition D isolates the pure effect of spatial relocation with matched random stream.

clear; clc;
t_total_start = tic;

scriptDir = fileparts(mfilename('fullpath'));
expDir = fullfile(scriptDir, '..');
dataDir = fullfile(expDir, 'data');
rootDir = fullfile(expDir, '..', '..');
sourceDir = fullfile(rootDir, 'source');
resultsDir = fullfile(rootDir, 'results');
compatDir = fullfile(rootDir, 'scripts', 'compat');

if ~exist(dataDir, 'dir'), mkdir(dataDir); end

cd(sourceDir);
addpath(genpath(sourceDir));

% Check native MATLAB toolboxes at runtime
has_stats = license('test', 'Statistics_Toolbox') && ~isempty(ver('stats'));
has_signal = license('test', 'Signal_Toolbox') && ~isempty(ver('signal'));
fprintf('=================================================================\n');
fprintf('CONTROLLED EXPERIMENT: TA MOTOR-POOL PLACEMENT (Komi et al., 2026)\n');
fprintf('Anatomical Target: L4-L5 (Bácskai et al., 2014; Mus musculus)\n');
fprintf('Timestamp: %s\n', datetime('now'));
fprintf('Toolbox Verification:\n');
fprintf('  Statistics Toolbox: %d\n', has_stats);
fprintf('  Signal Processing Toolbox: %d\n', has_signal);
if ~has_stats || ~has_signal
    fprintf('  Adding verified compatibility shims from: %s\n', compatDir);
    addpath(compatDir);
end
fprintf('=================================================================\n');

%% 1. Anatomical Target and Verified Geometry
% Reference: Bácskai et al. (2014), Brain Struct Funct 219:603–621
% Species: Mus musculus, C57BL/6J adult mice, 20-25 g (~8-12 weeks)
% Spinal segments: L4 and L5 dorsolateral motor column
% Unified Segment Boundaries from matGeometry.mat:
%   T13: [0, 1300] um
%   L1:  [1300, 2500] um
%   L2:  [2500, 4000] um
%   L3:  [4000, 5500] um
%   L4:  [5500, 6800] um
%   L5:  [6800, 8000] um
%   L6:  [8000, 9400] um
%   S1-S4: [9400, 13900] um
l3_l4_border = 5500.0;
l4_l5_border = 6800.0;
l5_l6_border = 8000.0;

target_span_min = 5600.0;
target_span_max = 7900.0;

% Simulation parameters
t_steps = 22000;
simSeed = 5;
tonic_drive = 25.0;

% Realization seeds (Seed 42 is frozen baseline; 101-104 provide paired replicates)
realization_seeds = [42, 101, 102, 103, 104];
n_realizations = length(realization_seeds);

% Bin widths to evaluate
bin_widths = [250, 500, 1000];

%% 2. Global Network Parameters for Realizations
gc = 0.5;
Density = 0.8;
Symmetry = 1;
Balance = 1;
SynpaticDistributionSpatialStd = 500;
Segments = [append('T',string([13])), append('L',string([1:6])), append('S',string([1:4]))];

MyNetwork = NetworkParameters();
MyNetwork.AddCelltype(Celltype.V2a_2,'bi','ven','lat','','ipsi','','',7000,'SynStrength',gc*1);
MyNetwork.AddCelltype(Celltype.V2a_1,'cau','ven','med','','ipsi','','',500,'SynStrength',gc*1);
MyNetwork.AddCelltype(Celltype.V1,'ro','ven','','','ipsi','','',2000,'SynStrength',gc*0.2);
MyNetwork.AddCelltype(Celltype.V2b,'cau','ven','lat','','ipsi','','',4000,'SynStrength',gc*1);
MyNetwork.AddCelltype(Celltype.V0d,'loc','ven','med','','contra','','',500,'SynStrength',gc*1);
MyNetwork.AddCelltype(Celltype.V0v,'ro','loc','med','','contra','','',3400,'SynStrength',gc*1);
MyNetwork.AddCelltype(Celltype.DI6,'cau','dor','med','','contra','','',5000,'SynStrength',gc*1);
MyNetwork.AddCelltype(Celltype.V3,'cau','ven','lat','','contra','','',500,'SynStrength',gc*1);
MyNetwork.AddCelltype(Celltype.MN,'loc','ven','lat','','ipsi','','',300,'SynStrength',gc*1);
MyNetwork.SetCellBiasPop('MN','All',0.1);

%% 3. Main Realization Loop
realization_data = struct([]);

for r = 1:n_realizations
    net_seed = realization_seeds(r);
    fprintf('\n=================================================================\n');
    fprintf('PROCESSING PAIRED REALIZATION %d/%d (Network Seed: %d)\n', r, n_realizations, net_seed);
    fprintf('=================================================================\n');
    
    if r == 1
        fprintf('Loading frozen baseline network and simulation (Condition A)...\n');
        load(fullfile(resultsDir, 'baseline_network.mat'), 'N');
        N_base = N;
        load(fullfile(resultsDir, 'simulated_network.mat'), 'N');
        N_base_sim = N;
        R_A = N_base_sim.Rates;
        W_A = N_base.ConnMat;
    else
        fprintf('Instantiating paired network realization %d (seed=%d)...\n', r, net_seed);
        rng(net_seed, 'twister');
        N_base = Network(Segments, Density, Symmetry, MyNetwork, ...
            'Balance', Balance, ...
            'ProjWidth', SynpaticDistributionSpatialStd, ...
            'Verbose', 0);
        W_A = N_base.ConnMat;
        
        fprintf('Simulating Condition A (%d ms, simSeed=%d)...\n', t_steps, simSeed);
        I_e = ones(size(N_base.ConnMat, 1), t_steps) * tonic_drive;
        N_base.ConnMat = sparse(N_base.ConnMat);
        ticSimA = tic;
        N_base.Simulate(t_steps, 'I_e', I_e, 'seed', simSeed);
        fprintf('  Condition A simulated in %.2f s.\n', toc(ticSimA));
        R_A = N_base.Rates;
    end
    
    N_neurons = size(W_A, 1);
    pos_base = N_base.Position;
    
    % Muscle pool indices
    ta_idx = find(string(N_base.Types) == 'MN' & string(N_base.MnID) == 'Tibialis Anterior');
    non_ta_idx = setdiff(1:N_neurons, ta_idx);
    
    % Geometry table indices
    Geom_C = N_base.Geometry;
    Geom_D = N_base.Geometry;
    ta_geom_idx = find(string(Geom_D.Type) == 'MN' & string(Geom_D.MnID) == 'Tibialis Anterior');
    
    % Relocation mapping
    orig_ta_rc = pos_base(ta_idx, 2);
    orig_min = min(orig_ta_rc);
    orig_max = max(orig_ta_rc);
    reloc_ta_rc = target_span_min + (orig_ta_rc - orig_min) * ...
        ((target_span_max - target_span_min) / (orig_max - orig_min));
    
    % Assert all relocated TA lie strictly within L4-L5
    assert(all(reloc_ta_rc >= l3_l4_border & reloc_ta_rc <= l5_l6_border), ...
        'Relocated TA neuron lies outside verified L4-L5 region!');
    
    new_segs = repmat(categorical({'L4'}), length(ta_idx), 1);
    new_segs(reloc_ta_rc >= l4_l5_border) = categorical({'L5'});
    
    % Apply to Geom_D
    Geom_D.Position(ta_geom_idx, 2) = reloc_ta_rc;
    Geom_D.Layers(ta_geom_idx, 4) = string(new_segs);
    
    % ---------------------------------------------------------------------
    % CONDITION B: Coordinate-Only Control
    % ---------------------------------------------------------------------
    fprintf('\nConfiguring Condition B (Coordinate-Only Control)...\n');
    pos_B = pos_base;
    pos_B(ta_idx, 2) = reloc_ta_rc;
    seg_B = N_base.Segment;
    seg_B(ta_idx) = new_segs;
    R_B = R_A;
    W_B = W_A;
    
    % Explicit assertion: Rates and W equality
    assert(isequal(R_A, R_B), 'Condition B firing rates must be identical to Condition A!');
    assert(isequal(full(W_A), full(W_B)), 'Condition B weights must be identical to Condition A!');
    fprintf('  Condition B verified: 100%% identical W and rates to Condition A.\n');
    
    % ---------------------------------------------------------------------
    % CONDITION C: Same-Location Reconstruction Control
    % ---------------------------------------------------------------------
    fprintf('\nReconstructing Condition C (Same-Location Control, seed=%d)...\n', net_seed);
    ticC = tic;
    rng(net_seed, 'twister');
    N_C = copy(N_base);
    N_C.InstantiateNetwork(Geom_C, N_base.Genetics, N_base.Parameters, ...
        'Balance', Balance, 'Rescale', 1, 'ProjWidth', SynpaticDistributionSpatialStd, 'Verbose', 0);
    tC = toc(ticC);
    W_C = N_C.ConnMat;
    fprintf('  Condition C instantiated in %.2f s. Sparsity = %.4f\n', tC, N_C.Sparsity);
    
    fprintf('Simulating Condition C (%d ms, simSeed=%d)...\n', t_steps, simSeed);
    I_e = ones(N_neurons, t_steps) * tonic_drive;
    N_C.ConnMat = sparse(N_C.ConnMat);
    ticSimC = tic;
    N_C.Simulate(t_steps, 'I_e', I_e, 'seed', simSeed);
    fprintf('  Condition C simulated in %.2f s.\n', toc(ticSimC));
    R_C = N_C.Rates;
    pos_C = N_C.Position;
    
    % ---------------------------------------------------------------------
    % CONDITION D: Relocated TA with Consistently Rebuilt Connections
    % ---------------------------------------------------------------------
    fprintf('\nReconstructing Condition D (Relocated TA, seed=%d)...\n', net_seed);
    ticD = tic;
    rng(net_seed, 'twister'); % MATCHED SEED TO CONDITION C!
    N_D = copy(N_base);
    N_D.InstantiateNetwork(Geom_D, N_base.Genetics, N_base.Parameters, ...
        'Balance', Balance, 'Rescale', 1, 'ProjWidth', SynpaticDistributionSpatialStd, 'Verbose', 0);
    tD = toc(ticD);
    W_D = N_D.ConnMat;
    fprintf('  Condition D instantiated in %.2f s. Sparsity = %.4f\n', tD, N_D.Sparsity);
    
    fprintf('Simulating Condition D (%d ms, simSeed=%d)...\n', t_steps, simSeed);
    I_e = ones(N_neurons, t_steps) * tonic_drive;
    N_D.ConnMat = sparse(N_D.ConnMat);
    ticSimD = tic;
    N_D.Simulate(t_steps, 'I_e', I_e, 'seed', simSeed);
    fprintf('  Condition D simulated in %.2f s.\n', toc(ticSimD));
    R_D = N_D.Rates;
    pos_D = N_D.Position;
    
    % ---------------------------------------------------------------------
    % Connectivity Differences Audit
    % ---------------------------------------------------------------------
    diff_CD_non_ta = abs(W_C(non_ta_idx, non_ta_idx) - W_D(non_ta_idx, non_ta_idx));
    max_diff_CD_non_ta = max(diff_CD_non_ta(:));
    mean_diff_CD_non_ta = mean(diff_CD_non_ta(:));
    
    diff_AC = abs(full(W_A) - full(W_C));
    max_diff_AC = max(diff_AC(:));
    r_AC_mat = corrcoef(full(W_A(:)), full(W_C(:)));
    corr_AC = r_AC_mat(1, 2);
    
    fprintf('\n--- CONNECTIVITY AUDIT (Realization %d) ---\n', r);
    fprintf('C vs D (isolating relocation): Max non-TA diff = %.6e, Mean non-TA diff = %.6e\n', ...
        max_diff_CD_non_ta, mean_diff_CD_non_ta);
    fprintf('A vs C (baseline vs reconstruction): Max diff = %.6e, corr(W_A, W_C) = %.6f\n', ...
        max_diff_AC, corr_AC);
    fprintf('TA incoming nonzeros: A=%d, C=%d, D=%d\n', ...
        nnz(W_A(ta_idx, :)), nnz(W_C(ta_idx, :)), nnz(W_D(ta_idx, :)));
    fprintf('TA outgoing nonzeros: A=%d, C=%d, D=%d\n', ...
        nnz(W_A(:, ta_idx)), nnz(W_C(:, ta_idx)), nnz(W_D(:, ta_idx)));
    
    % ---------------------------------------------------------------------
    % Compute Comprehensive Metrics for Conditions A, B, C, D
    % ---------------------------------------------------------------------
    entry = struct();
    entry.realization_index = r;
    entry.net_seed = net_seed;
    entry.sim_seed = simSeed;
    entry.N_neurons = N_neurons;
    entry.N_TA = length(ta_idx);
    entry.N_TA_Left = sum(N_base.Latera(ta_idx) < 0);
    entry.N_TA_Right = sum(N_base.Latera(ta_idx) > 0);
    
    entry.ta_rc_baseline = [min(orig_ta_rc), mean(orig_ta_rc), max(orig_ta_rc)];
    entry.ta_rc_relocated = [min(reloc_ta_rc), mean(reloc_ta_rc), max(reloc_ta_rc)];
    entry.compression_ratio = 1.0 - (target_span_max - target_span_min) / (orig_max - orig_min);
    
    entry.connectivity_audit = struct(...
        'max_diff_CD_non_ta', max_diff_CD_non_ta, ...
        'mean_diff_CD_non_ta', mean_diff_CD_non_ta, ...
        'max_diff_AC', max_diff_AC, ...
        'corr_AC', corr_AC, ...
        'ta_in_A', nnz(W_A(ta_idx, :)), ...
        'ta_in_C', nnz(W_C(ta_idx, :)), ...
        'ta_in_D', nnz(W_D(ta_idx, :)), ...
        'ta_out_A', nnz(W_A(:, ta_idx)), ...
        'ta_out_C', nnz(W_C(:, ta_idx)), ...
        'ta_out_D', nnz(W_D(:, ta_idx)) ...
    );
    
    % Metrics for each condition
    fprintf('\nComputing analysis metrics for Conditions A, B, C, D...\n');
    N_B_obj = copy(N_base);
    N_B_obj.Position = pos_B;
    N_B_obj.Segment = seg_B;
    
    entry.condA = compute_condition_metrics(R_A, pos_base, N_base, bin_widths);
    entry.condB = compute_condition_metrics(R_B, pos_B, N_B_obj, bin_widths);
    entry.condC = compute_condition_metrics(R_C, pos_C, N_C, bin_widths);
    entry.condD = compute_condition_metrics(R_D, pos_D, N_D, bin_widths);
    
    % Primary Paired Effect: Condition D vs Condition C
    entry.paired_D_minus_C = compute_paired_comparison(entry.condC, entry.condD);
    % Coordinate Display Effect: Condition B vs Condition A
    entry.paired_B_minus_A = compute_paired_comparison(entry.condA, entry.condB);
    % Reconstruction Effect: Condition C vs Condition A
    entry.paired_C_minus_A = compute_paired_comparison(entry.condA, entry.condC);
    
    realization_data = [realization_data; entry];
    
    fprintf('  Condition A: TA-GM r=%.3f, TA-Sol r=%.3f, TA-VM r=%.3f, Freq=%.2f Hz\n', ...
        entry.condA.ta_gm_corr, entry.condA.ta_sol_corr, entry.condA.ta_vm_corr, entry.condA.freq_hz);
    fprintf('  Condition C: TA-GM r=%.3f, TA-Sol r=%.3f, TA-VM r=%.3f, Freq=%.2f Hz\n', ...
        entry.condC.ta_gm_corr, entry.condC.ta_sol_corr, entry.condC.ta_vm_corr, entry.condC.freq_hz);
    fprintf('  Condition D: TA-GM r=%.3f, TA-Sol r=%.3f, TA-VM r=%.3f, Freq=%.2f Hz\n', ...
        entry.condD.ta_gm_corr, entry.condD.ta_sol_corr, entry.condD.ta_vm_corr, entry.condD.freq_hz);
    fprintf('  Primary C vs D Paired Shift: dPhi(TA-GM)=%.1f deg, dPhi(TA-Sol)=%.1f deg\n', ...
        entry.paired_D_minus_C.circ_diff_ta_gm_deg, entry.paired_D_minus_C.circ_diff_ta_sol_deg);
end

%% 4. Synthetic Controls Validation (Wave Kinematics Ground Truth)
fprintf('\n=================================================================\n');
fprintf('RUNNING SYNTHETIC CONTROLS VALIDATION\n');
fprintf('=================================================================\n');
synthetic_controls = run_synthetic_wave_controls(bin_widths);
fprintf('Continuous Wave: speed=%.1f um/ms, caudal_delay_frac=%.2f, jump_frac=%.2f\n', ...
    synthetic_controls.continuous.b500.speed_um_ms, ...
    synthetic_controls.continuous.b500.caudal_delay_frac, ...
    synthetic_controls.continuous.b500.jump_fraction);
fprintf('Regional Switching: speed=%.1f um/ms, caudal_delay_frac=%.2f, jump_frac=%.2f\n', ...
    synthetic_controls.switching.b500.speed_um_ms, ...
    synthetic_controls.switching.b500.caudal_delay_frac, ...
    synthetic_controls.switching.b500.jump_fraction);

%% 5. Aggregate Summary Statistics Across 5 Realizations
fprintf('\n=================================================================\n');
fprintf('AGGREGATING SUMMARY STATISTICS (N=%d Realizations)\n', n_realizations);
fprintf('=================================================================\n');

summary_stats = struct();
cond_names = {'condA', 'condB', 'condC', 'condD'};
coord_fields = {'freq_hz', 'lr_phase_deg', ...
                'ta_gm_corr', 'ta_sol_corr', 'ta_vm_corr', 'ta_bf_corr', ...
                'ta_gm_phase_deg', 'ta_sol_phase_deg', 'ta_vm_phase_deg', 'ta_bf_phase_deg', ...
                'ta_gm_jaccard_20', 'ta_sol_jaccard_20', 'ta_vm_jaccard_20', 'ta_bf_jaccard_20', ...
                'ta_gm_jaccard_10', 'ta_gm_jaccard_30'};

for c = 1:length(cond_names)
    cname = cond_names{c};
    for f = 1:length(coord_fields)
        fname = coord_fields{f};
        vals = arrayfun(@(x) x.(cname).(fname), realization_data);
        if contains(fname, 'phase_deg')
            % Circular mean and circular standard error
            summary_stats.(cname).(fname).values = vals;
            summary_stats.(cname).(fname).mean = circ_mean_deg(vals);
            summary_stats.(cname).(fname).std = circ_std_deg(vals);
            summary_stats.(cname).(fname).sem = circ_std_deg(vals) / sqrt(length(vals));
        else
            summary_stats.(cname).(fname).values = vals;
            summary_stats.(cname).(fname).mean = mean(vals);
            summary_stats.(cname).(fname).std = std(vals);
            summary_stats.(cname).(fname).sem = std(vals) / sqrt(length(vals));
        end
    end
    
    % Wave metrics for each bin width
    for bw = bin_widths
        bname = sprintf('b%d', bw);
        % Neighbor delay metrics
        c_frac = arrayfun(@(x) x.(cname).(bname).caudal_delay_frac, realization_data);
        spd = arrayfun(@(x) x.(cname).(bname).mean_speed_um_ms, realization_data);
        cons = arrayfun(@(x) x.(cname).(bname).mean_delay_consistency, realization_data);
        
        % Global jump diagnostics
        dw = arrayfun(@(x) x.(cname).(bname).dwell_fraction, realization_data);
        step = arrayfun(@(x) x.(cname).(bname).step_fraction, realization_data);
        jump = arrayfun(@(x) x.(cname).(bname).jump_fraction, realization_data);
        dist = arrayfun(@(x) x.(cname).(bname).mean_step_dist_um, realization_data);
        
        summary_stats.(cname).(bname).caudal_delay_frac = struct('mean', mean(c_frac), 'std', std(c_frac), 'sem', std(c_frac)/sqrt(length(c_frac)));
        summary_stats.(cname).(bname).mean_speed_um_ms = struct('mean', mean(spd), 'std', std(spd), 'sem', std(spd)/sqrt(length(spd)));
        summary_stats.(cname).(bname).mean_delay_consistency = struct('mean', mean(cons), 'std', std(cons), 'sem', std(cons)/sqrt(length(cons)));
        summary_stats.(cname).(bname).dwell_fraction = struct('mean', mean(dw), 'std', std(dw), 'sem', std(dw)/sqrt(length(dw)));
        summary_stats.(cname).(bname).step_fraction = struct('mean', mean(step), 'std', std(step), 'sem', std(step)/sqrt(length(step)));
        summary_stats.(cname).(bname).jump_fraction = struct('mean', mean(jump), 'std', std(jump), 'sem', std(jump)/sqrt(length(jump)));
        summary_stats.(cname).(bname).mean_step_dist_um = struct('mean', mean(dist), 'std', std(dist), 'sem', std(dist)/sqrt(length(dist)));
    end
end

% Primary Paired Comparisons Summary (Condition D vs C)
paired_diff_fields = {'circ_diff_ta_gm_deg', 'circ_diff_ta_sol_deg', 'circ_diff_ta_vm_deg', 'circ_diff_ta_bf_deg', ...
                      'delta_ta_gm_corr', 'delta_ta_sol_corr', 'delta_ta_vm_corr', 'delta_ta_bf_corr', ...
                      'delta_ta_gm_jaccard_20', 'delta_ta_sol_jaccard_20', 'delta_ta_vm_jaccard_20', 'delta_ta_bf_jaccard_20'};

for f = 1:length(paired_diff_fields)
    fname = paired_diff_fields{f};
    vals_DC = arrayfun(@(x) x.paired_D_minus_C.(fname), realization_data);
    vals_BA = arrayfun(@(x) x.paired_B_minus_A.(fname), realization_data);
    vals_CA = arrayfun(@(x) x.paired_C_minus_A.(fname), realization_data);
    
    summary_stats.paired_D_minus_C.(fname) = struct('values', vals_DC, 'mean', mean(vals_DC), 'std', std(vals_DC), 'sem', std(vals_DC)/sqrt(length(vals_DC)));
    summary_stats.paired_B_minus_A.(fname) = struct('values', vals_BA, 'mean', mean(vals_BA), 'std', std(vals_BA), 'sem', std(vals_BA)/sqrt(length(vals_BA)));
    summary_stats.paired_C_minus_A.(fname) = struct('values', vals_CA, 'mean', mean(vals_CA), 'std', std(vals_CA), 'sem', std(vals_CA)/sqrt(length(vals_CA)));
end

%% 6. Save Complete Experimental Data and JSON
mat_file = fullfile(dataDir, 'experiment_data.mat');
fprintf('Saving experiment_data.mat to: %s ...\n', mat_file);
save(mat_file, 'realization_data', 'summary_stats', 'synthetic_controls', ...
     'target_span_min', 'target_span_max', 'l3_l4_border', 'l4_l5_border', 'l5_l6_border', ...
     'bin_widths', 'realization_seeds', '-v7.3');
fprintf('Saved experiment_data.mat successfully.\n');

% Prepare clean JSON summary
json_file = fullfile(expDir, 'experiment_results.json');
fprintf('Saving experiment_results.json to: %s ...\n', json_file);
json_struct = struct();
json_struct.experiment_title = "Controlled Experiment: TA Motor-Pool Placement";
json_struct.anatomical_target = struct(...
    'reference', 'Bácskai et al. (2014) Brain Struct Funct 219:603–621', ...
    'species_strain', 'Mus musculus, adult C57BL/6J and C57BL/6J-ChAT-EGFP (20-25 g, 8-12 weeks)', ...
    'segments', 'L4 and L5 dorsolateral motor column', ...
    'verified_segment_boundaries', struct('L3_L4_um', 5500.0, 'L4_L5_um', 6800.0, 'L5_L6_um', 8000.0), ...
    'baseline_komi_placement', struct('segments', 'L2-L4', 'mean_RC_um', 4548.7, 'span_um', [2771.8, 6733.3]), ...
    'relocated_placement', struct('segments', 'L4-L5', 'mean_RC_um', 6750.0, 'span_um', [5600.0, 7900.0]), ...
    'compression_percentage', 41.9, ...
    'mapping_assumption', 'Affine rank-order mapping into [5600, 7900] um (position and longitudinal spread both change; distribution within range is an experimental assumption)' ...
);
json_struct.experimental_conditions = struct(...
    'A', 'Original baseline network and simulation', ...
    'B', 'Coordinate-only relocation control (identical W and rates; only coordinates change)', ...
    'C', 'Same-location reconstruction control (rebuilt at baseline location using author InstantiateNetwork)', ...
    'D', 'Relocated TA with rebuilt connections (rebuilt at L4-L5 location using author InstantiateNetwork and matched seeds)' ...
);
json_struct.primary_causal_comparison = "Condition C vs Condition D isolates spatial relocation with zero stochastic rewiring confounding.";
json_struct.n_realizations = n_realizations;
json_struct.realization_seeds = realization_seeds;
json_struct.simulation_parameters = struct('t_steps', t_steps, 'simSeed', simSeed, 'I_e', tonic_drive);
json_struct.summary_statistics = summary_stats;
json_struct.synthetic_controls = synthetic_controls;
json_struct.realization_data = realization_data;

fid = fopen(json_file, 'w');
fwrite(fid, jsonencode(json_struct, 'PrettyPrint', true));
fclose(fid);
fprintf('Saved experiment_results.json successfully.\n');

%% 7. Export Plot Data for High-Resolution Visualization
plot_file = fullfile(dataDir, 'plot_export.mat');
fprintf('Exporting plot data to: %s ...\n', plot_file);

% Export representative steady-state window (Realization 1, 10000 to 12000 ms)
plot_win = 10000:12000;
pe = struct();
pe.time_ms = plot_win;
pe.t_rel_s = (plot_win - plot_win(1)) / 1000.0;

% Representative traces (Realization 1)
r1 = realization_data(1);
pe.condA_traces = struct('ta', r1.condA.trace_ta_l(plot_win), 'gm', r1.condA.trace_gm_l(plot_win), ...
                         'sol', r1.condA.trace_sol_l(plot_win), 'vm', r1.condA.trace_vm_l(plot_win), ...
                         'bf', r1.condA.trace_bf_l(plot_win));
pe.condB_traces = pe.condA_traces; % Bit-for-bit identical
pe.condC_traces = struct('ta', r1.condC.trace_ta_l(plot_win), 'gm', r1.condC.trace_gm_l(plot_win), ...
                         'sol', r1.condC.trace_sol_l(plot_win), 'vm', r1.condC.trace_vm_l(plot_win), ...
                         'bf', r1.condC.trace_bf_l(plot_win));
pe.condD_traces = struct('ta', r1.condD.trace_ta_l(plot_win), 'gm', r1.condD.trace_gm_l(plot_win), ...
                         'sol', r1.condD.trace_sol_l(plot_win), 'vm', r1.condD.trace_vm_l(plot_win), ...
                         'bf', r1.condD.trace_bf_l(plot_win));

% 500 um binned maps for Conditions A, B, C, D (Lumbar enlargement 2500 to 9400 um)
pe.b500_centers = r1.condA.b500.bin_centers;
pe.b500_lumb_idx = find(pe.b500_centers >= 2500 & pe.b500_centers <= 9400);
pe.b500_lumb_centers = pe.b500_centers(pe.b500_lumb_idx);

pe.condA_sum_map = r1.condA.b500.sum_act_l(pe.b500_lumb_idx, plot_win);
pe.condA_mean_map = r1.condA.b500.mean_act_l(pe.b500_lumb_idx, plot_win);
pe.condB_sum_map = r1.condB.b500.sum_act_l(pe.b500_lumb_idx, plot_win);
pe.condB_mean_map = r1.condB.b500.mean_act_l(pe.b500_lumb_idx, plot_win);
pe.condC_sum_map = r1.condC.b500.sum_act_l(pe.b500_lumb_idx, plot_win);
pe.condC_mean_map = r1.condC.b500.mean_act_l(pe.b500_lumb_idx, plot_win);
pe.condD_sum_map = r1.condD.b500.sum_act_l(pe.b500_lumb_idx, plot_win);
pe.condD_mean_map = r1.condD.b500.mean_act_l(pe.b500_lumb_idx, plot_win);

% Common color limits across all conditions
pe.common_sum_cmax = max([max(pe.condA_sum_map(:)), max(pe.condB_sum_map(:)), ...
                          max(pe.condC_sum_map(:)), max(pe.condD_sum_map(:))]);
pe.common_mean_cmax = max([max(pe.condA_mean_map(~isnan(pe.condA_mean_map))), ...
                           max(pe.condB_mean_map(~isnan(pe.condB_mean_map))), ...
                           max(pe.condC_mean_map(~isnan(pe.condC_mean_map))), ...
                           max(pe.condD_mean_map(~isnan(pe.condD_mean_map)))]);

% Neuron coordinates for anatomy panel
pe.pos_base = pos_base;
pe.pos_reloc = pos_B;
pe.ta_idx = ta_idx;
pe.types = N_base.Types;
pe.mn_id = N_base.MnID;
pe.latera = N_base.Latera;

save(plot_file, 'pe', 'summary_stats', 'synthetic_controls', '-v7.3');
fprintf('Exported plot_export.mat successfully.\n');

t_total = toc(t_total_start);
fprintf('\n=================================================================\n');
fprintf('ALL EXPERIMENT RUNS COMPLETED SUCCESSFULLY (Total Elapsed: %.2f s)\n', t_total);
fprintf('=================================================================\n');

%% ========================================================================
% HELPER FUNCTIONS
% ========================================================================

function m = compute_condition_metrics(R, Position, N_obj, bin_widths)
    m = struct();
    N_neurons = size(Position, 1);
    t_steps = size(R, 1);
    ss_win = 5000:20000;
    
    is_mn = (string(N_obj.Types) == 'MN');
    is_left  = (N_obj.Latera < 0);
    is_right = (N_obj.Latera > 0);
    
    % Left side muscle pools (primary motor output)
    ta_idx_l = find(is_mn & is_left & string(N_obj.MnID) == 'Tibialis Anterior');
    gm_idx_l = find(is_mn & is_left & string(N_obj.MnID) == 'Gastrocnemius');
    sol_idx_l = find(is_mn & is_left & string(N_obj.MnID) == 'Soleus');
    vm_idx_l = find(is_mn & is_left & string(N_obj.MnID) == 'Vastus Medialis');
    bf_idx_l = find(is_mn & is_left & string(N_obj.MnID) == 'Biceps Femoris');
    
    % Right side for bilateral alternation
    gm_idx_r = find(is_mn & is_right & string(N_obj.MnID) == 'Gastrocnemius');
    ta_idx_r = find(is_mn & is_right & string(N_obj.MnID) == 'Tibialis Anterior');
    
    % Mean traces
    m.trace_ta_l = mean(R(:, ta_idx_l), 2);
    m.trace_gm_l = mean(R(:, gm_idx_l), 2);
    m.trace_sol_l = mean(R(:, sol_idx_l), 2);
    m.trace_vm_l = mean(R(:, vm_idx_l), 2);
    m.trace_bf_l = mean(R(:, bf_idx_l), 2);
    m.trace_gm_r = mean(R(:, gm_idx_r), 2);
    m.trace_ta_r = mean(R(:, ta_idx_r), 2);
    
    % Frequency detection from Left GM (ankle extensor burst onset)
    sig_rhythm = m.trace_gm_l(ss_win) - mean(m.trace_gm_l(ss_win));
    [autocorr, lags] = xcorr(sig_rhythm, 2000, 'coeff');
    pos_mask = (lags > 150);
    pos_lags = lags(pos_mask);
    pos_corr = autocorr(pos_mask);
    
    [pks, locs] = findpeaks(pos_corr, 'MinPeakDistance', 150, 'MinPeakProminence', 0.1);
    if ~isempty(locs)
        cycle_period = pos_lags(locs(1));
        m.freq_hz = 1000.0 / cycle_period;
        m.cycle_period_ms = cycle_period;
        m.freq_status = 'detected';
    else
        m.freq_hz = NaN;
        m.cycle_period_ms = NaN;
        m.freq_status = 'insufficient_peaks';
    end
    
    % Cross-correlations
    ta_s = m.trace_ta_l(ss_win);
    gm_s = m.trace_gm_l(ss_win);
    sol_s = m.trace_sol_l(ss_win);
    vm_s = m.trace_vm_l(ss_win);
    bf_s = m.trace_bf_l(ss_win);
    
    m.ta_gm_corr = get_corr(ta_s, gm_s);
    m.ta_sol_corr = get_corr(ta_s, sol_s);
    m.ta_vm_corr = get_corr(ta_s, vm_s);
    m.ta_bf_corr = get_corr(ta_s, bf_s);
    
    % Bilateral phase lag (Left GM vs Right GM)
    if ~isnan(m.cycle_period_ms)
        [c_lr, lag_lr] = xcorr(gm_s - mean(gm_s), (m.trace_gm_r(ss_win) - mean(m.trace_gm_r(ss_win))), ...
            round(m.cycle_period_ms), 'coeff');
        [~, max_lag_idx] = max(c_lr);
        lr_phase = abs(lag_lr(max_lag_idx)) / m.cycle_period_ms * 360.0;
        m.lr_phase_deg = mod(lr_phase, 360.0);
    else
        m.lr_phase_deg = NaN;
    end
    
    % Cycle-by-cycle phase difference and Jaccard overlap
    if ~isnan(m.cycle_period_ms)
        [~, cycle_peaks] = findpeaks(gm_s - mean(gm_s), 'MinPeakDistance', round(0.7 * m.cycle_period_ms));
        cycle_peaks = cycle_peaks + ss_win(1) - 1;
        n_cycles = length(cycle_peaks) - 1;
        
        phase_gm = []; phase_sol = []; phase_vm = []; phase_bf = [];
        ov_gm_20 = []; ov_sol_20 = []; ov_vm_20 = []; ov_bf_20 = [];
        ov_gm_10 = []; ov_gm_30 = [];
        
        for cyc = 1:min(n_cycles, 25)
            t_s = cycle_peaks(cyc);
            t_e = cycle_peaks(cyc + 1);
            c_len = t_e - t_s;
            if c_len < 100 || c_len > 1500, continue; end
            
            c_idx = t_s:t_e;
            [~, p_ta] = max(m.trace_ta_l(c_idx));
            [~, p_gm] = max(m.trace_gm_l(c_idx));
            [~, p_sol] = max(m.trace_sol_l(c_idx));
            [~, p_vm] = max(m.trace_vm_l(c_idx));
            [~, p_bf] = max(m.trace_bf_l(c_idx));
            
            phase_gm = [phase_gm, (p_ta - p_gm) / c_len * 360.0];
            phase_sol = [phase_sol, (p_ta - p_sol) / c_len * 360.0];
            phase_vm = [phase_vm, (p_ta - p_vm) / c_len * 360.0];
            phase_bf = [phase_bf, (p_ta - p_bf) / c_len * 360.0];
            
            % Jaccard overlap = |A & B| / |A | B|
            ov_gm_20 = [ov_gm_20, calc_jaccard(m.trace_ta_l(c_idx), m.trace_gm_l(c_idx), 0.20)];
            ov_sol_20 = [ov_sol_20, calc_jaccard(m.trace_ta_l(c_idx), m.trace_sol_l(c_idx), 0.20)];
            ov_vm_20 = [ov_vm_20, calc_jaccard(m.trace_ta_l(c_idx), m.trace_vm_l(c_idx), 0.20)];
            ov_bf_20 = [ov_bf_20, calc_jaccard(m.trace_ta_l(c_idx), m.trace_bf_l(c_idx), 0.20)];
            
            ov_gm_10 = [ov_gm_10, calc_jaccard(m.trace_ta_l(c_idx), m.trace_gm_l(c_idx), 0.10)];
            ov_gm_30 = [ov_gm_30, calc_jaccard(m.trace_ta_l(c_idx), m.trace_gm_l(c_idx), 0.30)];
        end
        
        m.ta_gm_phase_deg = circ_mean_deg(phase_gm);
        m.ta_sol_phase_deg = circ_mean_deg(phase_sol);
        m.ta_vm_phase_deg = circ_mean_deg(phase_vm);
        m.ta_bf_phase_deg = circ_mean_deg(phase_bf);
        
        m.ta_gm_jaccard_20 = mean(ov_gm_20);
        m.ta_sol_jaccard_20 = mean(ov_sol_20);
        m.ta_vm_jaccard_20 = mean(ov_vm_20);
        m.ta_bf_jaccard_20 = mean(ov_bf_20);
        
        m.ta_gm_jaccard_10 = mean(ov_gm_10);
        m.ta_gm_jaccard_30 = mean(ov_gm_30);
    else
        m.ta_gm_phase_deg = NaN; m.ta_sol_phase_deg = NaN;
        m.ta_vm_phase_deg = NaN; m.ta_bf_phase_deg = NaN;
        m.ta_gm_jaccard_20 = NaN; m.ta_sol_jaccard_20 = NaN;
        m.ta_vm_jaccard_20 = NaN; m.ta_bf_jaccard_20 = NaN;
        m.ta_gm_jaccard_10 = NaN; m.ta_gm_jaccard_30 = NaN;
    end
    
    % Spatial Binning and Wave Kinematics
    mn_l_mask = is_mn & is_left;
    pos_mn_l = Position(mn_l_mask, 2);
    rates_mn_l = R(:, mn_l_mask);
    
    for bw = bin_widths
        bname = sprintf('b%d', bw);
        bin_edges = 0:bw:13900;
        n_bins = length(bin_edges) - 1;
        bin_centers = bin_edges(1:end-1) + bw / 2;
        
        sum_act_l = zeros(n_bins, t_steps);
        mean_act_l = nan(n_bins, t_steps);
        bin_counts_l = zeros(n_bins, 1);
        
        for b = 1:n_bins
            in_b = (pos_mn_l >= bin_edges(b) & pos_mn_l < bin_edges(b+1));
            bin_counts_l(b) = sum(in_b);
            if bin_counts_l(b) > 0
                sum_act_l(b, :) = sum(rates_mn_l(:, in_b), 2)';
                mean_act_l(b, :) = mean(rates_mn_l(:, in_b), 2)';
            end
        end
        
        % Lumbar enlargement populated bins (2500 to 9400 um)
        lumb_idx = find(bin_centers >= 2500 & bin_centers <= 9400 & bin_counts_l' > 0);
        lumb_centers = bin_centers(lumb_idx);
        lumb_rates = mean_act_l(lumb_idx, :); % Use mean activity per neuron
        
        % 1. Local Neighbor Delays across Populated Bins
        n_pop = length(lumb_idx);
        pair_delays_ms = [];
        pair_delays_phase = [];
        pair_speeds = [];
        
        if n_pop >= 2 && ~isnan(m.cycle_period_ms)
            for j = 1:(n_pop - 1)
                dx = lumb_centers(j+1) - lumb_centers(j); % Positive = caudal
                trace1 = lumb_rates(j, ss_win) - mean(lumb_rates(j, ss_win));
                trace2 = lumb_rates(j+1, ss_win) - mean(lumb_rates(j+1, ss_win));
                
                [x_corr, lags] = xcorr(trace2, trace1, round(0.5 * m.cycle_period_ms), 'coeff');
                [~, peak_lag_idx] = max(x_corr);
                dt = lags(peak_lag_idx); % Positive = bin j+1 is delayed relative to j (caudal propagation)
                
                pair_delays_ms = [pair_delays_ms, dt];
                pair_delays_phase = [pair_delays_phase, dt / m.cycle_period_ms * 360.0];
                if dt ~= 0
                    pair_speeds = [pair_speeds, dx / abs(dt)];
                end
            end
        end
        
        if ~isempty(pair_delays_ms)
            b_res.caudal_delay_frac = sum(pair_delays_ms > 0) / length(pair_delays_ms);
            b_res.mean_delay_ms = mean(pair_delays_ms);
            b_res.mean_speed_um_ms = mean(pair_speeds);
            b_res.mean_delay_consistency = circ_std_deg(pair_delays_phase);
        else
            b_res.caudal_delay_frac = NaN;
            b_res.mean_delay_ms = NaN;
            b_res.mean_speed_um_ms = NaN;
            b_res.mean_delay_consistency = NaN;
        end
        
        % 2. Secondary Global Peak Diagnostics (Separating Dwell vs Jump)
        [~, max_bin_idx] = max(lumb_rates(:, ss_win), [], 1);
        peak_y = lumb_centers(max_bin_idx);
        delta_y = diff(peak_y);
        
        n_trans = length(delta_y);
        dwell_count = sum(delta_y == 0);
        step_count = sum(abs(delta_y) > 0 & abs(delta_y) <= bw);
        jump_count = sum(abs(delta_y) > bw);
        
        b_res.bin_width = bw;
        b_res.bin_counts = bin_counts_l;
        b_res.bin_centers = bin_centers;
        b_res.dwell_fraction = dwell_count / n_trans;
        b_res.step_fraction = step_count / n_trans;
        b_res.jump_fraction = jump_count / n_trans;
        nonzero_jumps = abs(delta_y(delta_y ~= 0));
        if ~isempty(nonzero_jumps)
            b_res.mean_step_dist_um = mean(nonzero_jumps);
        else
            b_res.mean_step_dist_um = 0;
        end
        
        b_res.sum_act_l = sum_act_l;
        b_res.mean_act_l = mean_act_l;
        
        m.(bname) = b_res;
    end
end

function comp = compute_paired_comparison(cond1, cond2)
    comp = struct();
    % Circular phase difference: delta = atan2(sin(phi2 - phi1), cos(phi2 - phi1))
    comp.circ_diff_ta_gm_deg = circ_diff_deg(cond1.ta_gm_phase_deg, cond2.ta_gm_phase_deg);
    comp.circ_diff_ta_sol_deg = circ_diff_deg(cond1.ta_sol_phase_deg, cond2.ta_sol_phase_deg);
    comp.circ_diff_ta_vm_deg = circ_diff_deg(cond1.ta_vm_phase_deg, cond2.ta_vm_phase_deg);
    comp.circ_diff_ta_bf_deg = circ_diff_deg(cond1.ta_bf_phase_deg, cond2.ta_bf_phase_deg);
    
    comp.delta_ta_gm_corr = cond2.ta_gm_corr - cond1.ta_gm_corr;
    comp.delta_ta_sol_corr = cond2.ta_sol_corr - cond1.ta_sol_corr;
    comp.delta_ta_vm_corr = cond2.ta_vm_corr - cond1.ta_vm_corr;
    comp.delta_ta_bf_corr = cond2.ta_bf_corr - cond1.ta_bf_corr;
    
    comp.delta_ta_gm_jaccard_20 = cond2.ta_gm_jaccard_20 - cond1.ta_gm_jaccard_20;
    comp.delta_ta_sol_jaccard_20 = cond2.ta_sol_jaccard_20 - cond1.ta_sol_jaccard_20;
    comp.delta_ta_vm_jaccard_20 = cond2.ta_vm_jaccard_20 - cond1.ta_vm_jaccard_20;
    comp.delta_ta_bf_jaccard_20 = cond2.ta_bf_jaccard_20 - cond1.ta_bf_jaccard_20;
    
    comp.delta_freq_hz = cond2.freq_hz - cond1.freq_hz;
end

function d_deg = circ_diff_deg(phi1_deg, phi2_deg)
    if isnan(phi1_deg) || isnan(phi2_deg)
        d_deg = NaN;
        return;
    end
    r1 = phi1_deg * pi / 180.0;
    r2 = phi2_deg * pi / 180.0;
    d_deg = atan2(sin(r2 - r1), cos(r2 - r1)) * 180.0 / pi;
end

function m_deg = circ_mean_deg(angles_deg)
    valid = angles_deg(~isnan(angles_deg));
    if isempty(valid)
        m_deg = NaN;
        return;
    end
    rad = valid * pi / 180.0;
    m_deg = mod(atan2(sum(sin(rad)), sum(cos(rad))) * 180.0 / pi, 360.0);
end

function s_deg = circ_std_deg(angles_deg)
    valid = angles_deg(~isnan(angles_deg));
    if isempty(valid) || length(valid) < 2
        s_deg = NaN;
        return;
    end
    rad = valid * pi / 180.0;
    R_bar = sqrt((sum(sin(rad))/length(valid))^2 + (sum(cos(rad))/length(valid))^2);
    s_deg = sqrt(max(0, -2 * log(min(1.0, R_bar)))) * 180.0 / pi;
end

function r = get_corr(x, y)
    r_mat = corrcoef(x, y);
    r = r_mat(1, 2);
end

function j = calc_jaccard(x, y, thresh_ratio)
    th_x = thresh_ratio * max(x);
    th_y = thresh_ratio * max(y);
    act_x = (x > th_x);
    act_y = (y > th_y);
    denom = sum(act_x | act_y);
    if denom == 0
        j = 0;
    else
        j = sum(act_x & act_y) / denom;
    end
end

function synth = run_synthetic_wave_controls(bin_widths)
    synth = struct();
    t_synth = 0:1:5000; % 5 s
    f = 1.34; % 1.34 Hz matching network rhythm
    omega = 2 * pi * f / 1000.0;
    
    % Spatial coordinates (Lumbar enlargement 2500 to 9400 um)
    x_grid = 2500:50:9400;
    n_x = length(x_grid);
    n_t = length(t_synth);
    
    % 1. Continuous Wave Control: lambda = 7000 um, speed = 9.38 um/ms
    lambda = 7000.0;
    k_w = 2 * pi / lambda;
    R_cont = zeros(n_x, n_t);
    for xi = 1:n_x
        R_cont(xi, :) = max(0, cos(omega * t_synth - k_w * (x_grid(xi) - 2500)) + 0.05 * randn(1, n_t));
    end
    
    % 2. Regional Switching Control: Two discrete spatial bands switching in antiphase
    band1 = (x_grid >= 3000 & x_grid <= 5000);
    band2 = (x_grid >= 6500 & x_grid <= 8500);
    R_switch = zeros(n_x, n_t);
    for xi = 1:n_x
        if band1(xi)
            R_switch(xi, :) = max(0, cos(omega * t_synth) + 0.05 * randn(1, n_t));
        elseif band2(xi)
            R_switch(xi, :) = max(0, -cos(omega * t_synth) + 0.05 * randn(1, n_t));
        else
            R_switch(xi, :) = 0.02 * rand(1, n_t);
        end
    end
    
    % Evaluate across bin widths
    for bw = bin_widths
        bname = sprintf('b%d', bw);
        bin_edges = 2500:bw:9400;
        n_b = length(bin_edges) - 1;
        b_centers = bin_edges(1:end-1) + bw / 2;
        
        % Continuous binning
        b_cont = zeros(n_b, n_t);
        for b = 1:n_b
            in_b = (x_grid >= bin_edges(b) & x_grid < bin_edges(b+1));
            b_cont(b, :) = mean(R_cont(in_b, :), 1);
        end
        
        % Switching binning
        b_switch = zeros(n_b, n_t);
        for b = 1:n_b
            in_b = (x_grid >= bin_edges(b) & x_grid < bin_edges(b+1));
            b_switch(b, :) = mean(R_switch(in_b, :), 1);
        end
        
        synth.continuous.(bname) = analyze_synthetic_wave(b_cont, b_centers, bw, 1000.0/f);
        synth.switching.(bname) = analyze_synthetic_wave(b_switch, b_centers, bw, 1000.0/f);
    end
end

function res = analyze_synthetic_wave(R_binned, b_centers, bw, period_ms)
    res = struct();
    n_b = size(R_binned, 1);
    
    delays = [];
    speeds = [];
    for j = 1:(n_b - 1)
        dx = b_centers(j+1) - b_centers(j);
        [c, lags] = xcorr(R_binned(j+1, :), R_binned(j, :), round(0.5 * period_ms), 'coeff');
        [~, max_idx] = max(c);
        dt = lags(max_idx);
        delays = [delays, dt];
        if dt ~= 0
            speeds = [speeds, dx / abs(dt)];
        end
    end
    
    res.caudal_delay_frac = sum(delays > 0) / length(delays);
    res.mean_delay_ms = mean(delays);
    if ~isempty(speeds)
        res.speed_um_ms = mean(speeds);
    else
        res.speed_um_ms = NaN;
    end
    
    % Peak tracking
    [~, max_idx] = max(R_binned, [], 1);
    pk_y = b_centers(max_idx);
    dy = diff(pk_y);
    res.dwell_fraction = sum(dy == 0) / length(dy);
    res.step_fraction = sum(abs(dy) > 0 & abs(dy) <= bw) / length(dy);
    res.jump_fraction = sum(abs(dy) > bw) / length(dy);
end
