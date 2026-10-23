%% export_clean_json.m
% Exports a clean, compact, valid experiment_results.json from experiment_data.mat
clear; clc;
scriptDir = fileparts(mfilename('fullpath'));
expDir = fullfile(scriptDir, '..');
dataDir = fullfile(expDir, 'data');

mat_file = fullfile(dataDir, 'experiment_data.mat');
fprintf('Loading experiment_data.mat...\n');
load(mat_file, 'realization_data', 'summary_stats', 'synthetic_controls', ...
     'target_span_min', 'target_span_max', 'l3_l4_border', 'l4_l5_border', 'l5_l6_border', ...
     'bin_widths', 'realization_seeds');

n_real = length(realization_seeds);

% Build clean per-realization summary (scalars only, no raw time series)
per_realization = struct([]);
for r = 1:n_real
    rd = realization_data(r);
    entry = struct();
    entry.realization_index = rd.realization_index;
    entry.net_seed = rd.net_seed;
    entry.sim_seed = rd.sim_seed;
    entry.N_neurons = rd.N_neurons;
    entry.N_TA = rd.N_TA;
    entry.N_TA_Left = rd.N_TA_Left;
    entry.N_TA_Right = rd.N_TA_Right;
    entry.ta_rc_baseline = rd.ta_rc_baseline;
    entry.ta_rc_relocated = rd.ta_rc_relocated;
    entry.compression_ratio = rd.compression_ratio;
    entry.connectivity_audit = rd.connectivity_audit;
    
    % Condition A
    entry.condA = extract_scalar_metrics(rd.condA, bin_widths);
    % Condition B
    entry.condB = extract_scalar_metrics(rd.condB, bin_widths);
    % Condition C
    entry.condC = extract_scalar_metrics(rd.condC, bin_widths);
    % Condition D
    entry.condD = extract_scalar_metrics(rd.condD, bin_widths);
    
    % Paired comparisons
    entry.paired_D_minus_C = rd.paired_D_minus_C;
    entry.paired_B_minus_A = rd.paired_B_minus_A;
    entry.paired_C_minus_A = rd.paired_C_minus_A;
    
    per_realization = [per_realization; entry];
end

% Build full clean JSON struct
json_struct = struct();
json_struct.experiment_title = "Controlled Experiment: TA Motor-Pool Placement";
json_struct.anatomical_target = struct(...
    'reference', 'Bácskai et al. (2014) Brain Struct Funct 219:603–621', ...
    'species_strain', 'Mus musculus, adult C57BL/6J and C57BL/6J-ChAT-EGFP (20-25 g, 8-12 weeks)', ...
    'segments', 'L4 and L5 dorsolateral motor column', ...
    'verified_segment_boundaries', struct('L3_L4_um', l3_l4_border, 'L4_L5_um', l4_l5_border, 'L5_L6_um', l5_l6_border), ...
    'baseline_komi_placement', struct('segments', 'L2-L4', 'mean_RC_um', 4548.7, 'span_um', [2771.8, 6733.3]), ...
    'relocated_placement', struct('segments', 'L4-L5', 'mean_RC_um', 6750.0, 'span_um', [target_span_min, target_span_max]), ...
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
json_struct.n_realizations = n_real;
json_struct.realization_seeds = realization_seeds;
json_struct.simulation_parameters = struct('t_steps', 22000, 'simSeed', 5, 'I_e', 25.0);
json_struct.summary_statistics = summary_stats;
json_struct.synthetic_controls = synthetic_controls;
json_struct.per_realization_metrics = per_realization;

json_file = fullfile(expDir, 'experiment_results.json');
fprintf('Writing clean JSON to: %s ...\n', json_file);
fid = fopen(json_file, 'w');
fwrite(fid, jsonencode(json_struct, 'PrettyPrint', true));
fclose(fid);
fprintf('Saved clean experiment_results.json successfully!\n');

function s = extract_scalar_metrics(cond, bin_widths)
    s = struct();
    s.freq_hz = cond.freq_hz;
    s.cycle_period_ms = cond.cycle_period_ms;
    s.freq_status = cond.freq_status;
    s.lr_phase_deg = cond.lr_phase_deg;
    
    s.ta_gm_corr = cond.ta_gm_corr;
    s.ta_sol_corr = cond.ta_sol_corr;
    s.ta_vm_corr = cond.ta_vm_corr;
    s.ta_bf_corr = cond.ta_bf_corr;
    
    s.ta_gm_phase_deg = cond.ta_gm_phase_deg;
    s.ta_sol_phase_deg = cond.ta_sol_phase_deg;
    s.ta_vm_phase_deg = cond.ta_vm_phase_deg;
    s.ta_bf_phase_deg = cond.ta_bf_phase_deg;
    
    s.ta_gm_jaccard_20 = cond.ta_gm_jaccard_20;
    s.ta_sol_jaccard_20 = cond.ta_sol_jaccard_20;
    s.ta_vm_jaccard_20 = cond.ta_vm_jaccard_20;
    s.ta_bf_jaccard_20 = cond.ta_bf_jaccard_20;
    
    s.ta_gm_jaccard_10 = cond.ta_gm_jaccard_10;
    s.ta_gm_jaccard_30 = cond.ta_gm_jaccard_30;
    
    for bw = bin_widths
        bname = sprintf('b%d', bw);
        b = cond.(bname);
        s.(bname) = struct(...
            'caudal_delay_frac', b.caudal_delay_frac, ...
            'mean_delay_ms', b.mean_delay_ms, ...
            'mean_speed_um_ms', b.mean_speed_um_ms, ...
            'mean_delay_consistency', b.mean_delay_consistency, ...
            'dwell_fraction', b.dwell_fraction, ...
            'step_fraction', b.step_fraction, ...
            'jump_fraction', b.jump_fraction, ...
            'mean_step_dist_um', b.mean_step_dist_um ...
        );
    end
end
