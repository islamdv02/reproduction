%% simulate_ta_relocated_all_pools.m
% Complete All-Pool Motoneuron Simulation & Extraction (TA-Relocated Model, Condition D)
%
% Parameter Specifications (Condition D Realization 1):
%   - Network seed: 42
%   - Simulation seed: 5
%   - Tonic drive: I_e = 25.0 pA
%   - Duration: 22,000 ms (dt = 1.0 ms)
%   - TA coordinates: Affine relocated into L4-L5 [5600.0, 7900.0] um
%   - Premotor connectome: Rebuilt with author InstantiateNetwork ('Balance', 1, 'Rescale', 1, 'ProjWidth', 500)
%
% Corrected Neuron Selection:
%   - Explicit hindlimb-neuron mask isolates the 14 hindlimb pools (1,366 neurons: L 656, R 710)
%   - Excludes non-hindlimb/axial/tail pools (429 neurons: Axial 330, Tail 58, ThAb 24, QL 17)
%   - Evaluates physical binned maps exclusively on hindlimb motoneurons
%
% Output:
%   experiments/all_pool_analysis/data/ta_relocated_all_pools.mat

clear; clc;
t_total_start = tic;

scriptDir = fileparts(mfilename('fullpath'));
expDir = fullfile(scriptDir, '..');
dataDir = fullfile(expDir, 'data');
rootDir = fullfile(expDir, '..', '..');
sourceDir = fullfile(rootDir, 'source');
resultsDir = fullfile(rootDir, 'results');

if ~exist(dataDir, 'dir'), mkdir(dataDir); end

cd(sourceDir);
addpath(genpath(sourceDir));

fprintf('=================================================================\n');
fprintf('SIMULATION EXTRACTION: ALL-POOL ANALYSIS (TA-RELOCATED MODEL)\n');
fprintf('Timestamp: %s\n', datetime('now'));
fprintf('=================================================================\n');

%% 1. Anatomical Target and Verification
l3_l4_border = 5500.0;
l4_l5_border = 6800.0;
l5_l6_border = 8000.0;
target_span_min = 5600.0;
target_span_max = 7900.0;

t_steps = 22000;
simSeed = 5;
net_seed = 42;
tonic_drive = 25.0;
SynpaticDistributionSpatialStd = 500;
Balance = 1;

%% 2. Load Frozen Baseline Network Structure
fprintf('Loading baseline network structure...\n');
load(fullfile(resultsDir, 'baseline_network.mat'), 'N');
N_base = N;
N_neurons = size(N_base.ConnMat, 1);
pos_base = N_base.Position;

ta_idx = find(string(N_base.Types) == 'MN' & string(N_base.MnID) == 'Tibialis Anterior');
orig_ta_rc = pos_base(ta_idx, 2);
orig_min = min(orig_ta_rc);
orig_max = max(orig_ta_rc);

fprintf('Baseline TA: %d neurons, RC span = [%.1f, %.1f] um, centroid = %.1f um\n', ...
    length(ta_idx), orig_min, orig_max, mean(orig_ta_rc));

% Build Relocated TA Geometry
reloc_ta_rc = target_span_min + (orig_ta_rc - orig_min) * ...
    ((target_span_max - target_span_min) / (orig_max - orig_min));

assert(all(reloc_ta_rc >= l3_l4_border & reloc_ta_rc <= l5_l6_border), ...
    'Relocated TA neuron lies outside verified L4-L5 region!');

new_segs = repmat(categorical({'L4'}), length(ta_idx), 1);
new_segs(reloc_ta_rc >= l4_l5_border) = categorical({'L5'});

Geom_D = N_base.Geometry;
ta_geom_idx = find(string(Geom_D.Type) == 'MN' & string(Geom_D.MnID) == 'Tibialis Anterior');
Geom_D.Position(ta_geom_idx, 2) = reloc_ta_rc;
Geom_D.Layers(ta_geom_idx, 4) = string(new_segs);

fprintf('Relocated TA: %d neurons, RC span = [%.1f, %.1f] um, centroid = %.1f um (L4-L5)\n', ...
    length(ta_idx), min(reloc_ta_rc), max(reloc_ta_rc), mean(reloc_ta_rc));

%% 3. Instantiate Condition D Network
fprintf('\nInstantiating Condition D Network (seed=%d)...\n', net_seed);
rng(net_seed, 'twister');
N_D = copy(N_base);
N_D.InstantiateNetwork(Geom_D, N_base.Genetics, N_base.Parameters, ...
    'Balance', Balance, 'Rescale', 1, 'ProjWidth', SynpaticDistributionSpatialStd, 'Verbose', 0);
fprintf('  Condition D instantiated. Sparsity = %.4f\n', N_D.Sparsity);

%% 4. Simulate Network
fprintf('\nSimulating Condition D (%d ms, drive=%.1f pA, simSeed=%d)...\n', t_steps, tonic_drive, simSeed);
I_e = ones(N_neurons, t_steps) * tonic_drive;
N_D.ConnMat = sparse(N_D.ConnMat);
ticSim = tic;
N_D.Simulate(t_steps, 'I_e', I_e, 'seed', simSeed);
fprintf('  Simulation finished in %.2f s.\n', toc(ticSim));

R = N_D.Rates; % 22000 x N_neurons
pos = N_D.Position;
types = string(N_D.Types);
mn_ids = string(N_D.MnID);
latera = N_D.Latera;
segments = string(N_D.Segment);

%% 5. Cross-Check with All Available Saved Traces in experiment_data.mat
exp_mat = fullfile(rootDir, 'experiments', 'ta_placement', 'data', 'experiment_data.mat');
trace_comparisons = struct();
if exist(exp_mat, 'file')
    fprintf('\nComparing against all 7 previously saved traces in experiment_data.mat...\n');
    load(exp_mat, 'realization_data');
    saved_condD = realization_data(1).condD;
    
    check_pools = {'Tibialis Anterior', 'trace_ta_l', 'trace_left';
                   'Gastrocnemius',     'trace_gm_l', 'trace_left';
                   'Soleus',            'trace_sol_l','trace_left';
                   'Vastus Medialis',   'trace_vm_l', 'trace_left';
                   'Biceps Femoris',    'trace_bf_l', 'trace_left';
                   'Tibialis Anterior', 'trace_ta_r', 'trace_right';
                   'Gastrocnemius',     'trace_gm_r', 'trace_right'};
               
    for c = 1:size(check_pools, 1)
        pname = check_pools{c, 1};
        saved_fld = check_pools{c, 2};
        side_fld = check_pools{c, 3};
        
        if strcmp(side_fld, 'trace_left')
            p_idx = find(types == 'MN' & mn_ids == pname & latera < 0);
        else
            p_idx = find(types == 'MN' & mn_ids == pname & latera > 0);
        end
        
        sim_tr = mean(R(:, p_idx), 2);
        saved_tr = saved_condD.(saved_fld);
        
        diff_val = abs(sim_tr - saved_tr);
        max_d = max(diff_val);
        mean_d = mean(diff_val);
        r_mat = corrcoef(sim_tr, saved_tr);
        r_val = r_mat(1, 2);
        
        trace_comparisons.(saved_fld) = struct('pool', pname, 'max_abs_diff', max_d, ...
                                               'mean_abs_diff', mean_d, 'pearson_r', r_val);
        fprintf('  %-12s (%-17s): max_diff = %.4e Hz, mean_diff = %.4e Hz, r = %.8f\n', ...
            saved_fld, pname, max_d, mean_d, r_val);
    end
end

%% 6. Inventory All Hindlimb Motoneuron Pools
fprintf('\nInventorying all hindlimb motoneuron pools...\n');

% Explicit non-hindlimb/axial/tail pools
exclude_pools = ["Tail", "Thoracic Abdominal", "Quadratus Lumburum", "Axial"];

all_mn_mask = (types == 'MN');
all_mn_pools = unique(mn_ids(all_mn_mask));
hindlimb_pools = setdiff(all_mn_pools, exclude_pools);

% Explicit hindlimb neuron mask
is_hindlimb_neuron = (types == 'MN' & ismember(mn_ids, hindlimb_pools));
fprintf('Hindlimb motoneurons: %d (Left: %d, Right: %d)\n', ...
    sum(is_hindlimb_neuron), sum(is_hindlimb_neuron & latera < 0), sum(is_hindlimb_neuron & latera > 0));

% Excluded motoneurons derived from data
is_excluded_neuron = (types == 'MN' & ismember(mn_ids, exclude_pools));
fprintf('Excluded motoneurons: %d (Left: %d, Right: %d)\n', ...
    sum(is_excluded_neuron), sum(is_excluded_neuron & latera < 0), sum(is_excluded_neuron & latera > 0));

pool_info = struct([]);

for i = 1:length(hindlimb_pools)
    pname = hindlimb_pools(i);
    p_mask = (types == 'MN' & mn_ids == pname);
    p_indices = find(p_mask);
    
    idx_l = find(p_mask & latera < 0);
    idx_r = find(p_mask & latera > 0);
    
    rc_all = pos(p_indices, 2);
    rc_l = pos(idx_l, 2);
    rc_r = pos(idx_r, 2);
    
    switch pname
        case {'Iliopsoas', 'Gluteus', 'Adductors'}
            joint_group = "Hip";
        case {'Vastus Lateralis', 'Vastus Medialis', 'Rectus Femoris', 'Gracilis', 'Biceps Femoris', 'Semitendinosus'}
            joint_group = "Knee";
        case {'Tibialis Anterior', 'Gastrocnemius', 'Soleus', 'Plantar Flexor', 'Extensor Digitorum'}
            joint_group = "Ankle/Toes";
        otherwise
            joint_group = "Uncertain";
    end
    
    switch pname
        case 'Iliopsoas'
            muscle_func = "Primary Hip Flexor";
            abbrev = "Ilio";
            uncertain_notes = "Pure hip flexor (L2-L4).";
        case 'Gluteus'
            muscle_func = "Hip Extensor / Abductor";
            abbrev = "Glut";
            uncertain_notes = "Major hip extensor and abductor (L3-L6).";
        case 'Adductors'
            muscle_func = "Hip Adductor";
            abbrev = "Add";
            uncertain_notes = "Adductor group (adductor magnus/longus/brevis); multi-articular hip synergist.";
        case 'Vastus Lateralis'
            muscle_func = "Knee Extensor";
            abbrev = "VLat";
            uncertain_notes = "Quadriceps group, primary mono-articular knee extensor (T13-L2).";
        case 'Vastus Medialis'
            muscle_func = "Knee Extensor";
            abbrev = "VMed";
            uncertain_notes = "Quadriceps group, primary mono-articular knee extensor (L1-L3).";
        case 'Rectus Femoris'
            muscle_func = "Knee Extensor / Hip Flexor";
            abbrev = "RF";
            uncertain_notes = "Bi-articular: knee extensor + secondary hip flexor (L2-L4).";
        case 'Gracilis'
            muscle_func = "Knee Flexor / Hip Adductor";
            abbrev = "Grac";
            uncertain_notes = "Multi-articular medial thigh: knee flexor + hip adductor (L1-L5).";
        case 'Biceps Femoris'
            muscle_func = "Knee Flexor / Hip Extensor";
            abbrev = "BF";
            uncertain_notes = "Hamstrings, bi-articular: knee flexor + hip extensor (L3-L6).";
        case 'Semitendinosus'
            muscle_func = "Knee Flexor / Hip Extensor";
            abbrev = "ST";
            uncertain_notes = "Hamstrings, bi-articular: knee flexor + hip extensor (L4-S1).";
        case 'Tibialis Anterior'
            muscle_func = "Ankle Dorsiflexor";
            abbrev = "TA";
            uncertain_notes = "Relocated from baseline L2-L4 to verified anatomical L4-L5 position.";
        case 'Gastrocnemius'
            muscle_func = "Ankle Plantarflexor / Knee Flexor";
            abbrev = "GM";
            uncertain_notes = "Triceps surae, bi-articular: ankle plantarflexor + secondary knee flexor (L3-L5).";
        case 'Soleus'
            muscle_func = "Ankle Plantarflexor";
            abbrev = "Sol";
            uncertain_notes = "Triceps surae, mono-articular slow-twitch ankle plantarflexor (L4-L6).";
        case 'Plantar Flexor'
            muscle_func = "Ankle / Digit Plantarflexor";
            abbrev = "PF";
            uncertain_notes = "Deep flexor group (flexor digitorum longus / tibialis posterior, L4-L6).";
        case 'Extensor Digitorum'
            muscle_func = "Toe Extensor / Ankle Dorsiflexor";
            abbrev = "EDL";
            uncertain_notes = "Extensor digitorum longus: digit extensor + secondary ankle dorsiflexor (L5-L6).";
    end
    
    seg_list = unique(segments(p_indices));
    seg_str = strjoin(seg_list, ', ');
    
    entry = struct();
    entry.name = char(pname);
    entry.abbrev = char(abbrev);
    entry.joint_group = char(joint_group);
    entry.muscle_function = char(muscle_func);
    entry.uncertain_notes = char(uncertain_notes);
    entry.segments = char(seg_str);
    
    entry.count_total = length(p_indices);
    entry.count_left = length(idx_l);
    entry.count_right = length(idx_r);
    
    entry.indices_all = p_indices;
    entry.indices_left = idx_l;
    entry.indices_right = idx_r;
    
    entry.rc_centroid_all = mean(rc_all);
    entry.rc_centroid_left = mean(rc_l);
    entry.rc_centroid_right = mean(rc_r);
    
    entry.rc_min_all = min(rc_all);
    entry.rc_max_all = max(rc_all);
    entry.rc_span_all = max(rc_all) - min(rc_all);
    
    entry.rc_min_left = min(rc_l);
    entry.rc_max_left = max(rc_l);
    entry.rc_span_left = max(rc_l) - min(rc_l);
    
    entry.rc_min_right = min(rc_r);
    entry.rc_max_right = max(rc_r);
    entry.rc_span_right = max(rc_r) - min(rc_r);
    
    if ~isempty(idx_l)
        entry.trace_left = mean(R(:, idx_l), 2);
    else
        entry.trace_left = zeros(t_steps, 1);
    end
    
    if ~isempty(idx_r)
        entry.trace_right = mean(R(:, idx_r), 2);
    else
        entry.trace_right = zeros(t_steps, 1);
    end
    
    entry.trace_all = mean(R(:, p_indices), 2);
    
    pool_info = [pool_info; entry];
end

% Sort pools by anatomical centroid along the rostrocaudal axis (Left side)
[~, sort_idx] = sort([pool_info.rc_centroid_left]);
pool_info = pool_info(sort_idx);

fprintf('Identified %d hindlimb motor pools (ordered rostral to caudal):\n', length(pool_info));
for i = 1:length(pool_info)
    p = pool_info(i);
    fprintf('  %2d. %-20s (%-4s) | %-10s | Total=%3d (L=%2d, R=%2d) | RC=[%.1f, %.1f] Mean=%.1f um\n', ...
        i, p.name, p.abbrev, p.joint_group, p.count_total, p.count_left, p.count_right, ...
        p.rc_min_left, p.rc_max_left, p.rc_centroid_left);
end

%% 7. Compute Physical Rostrocaudal Binned Maps (Using Strictly Hindlimb Neurons)
fprintf('\nComputing physical rostrocaudal binned activity maps (Hindlimb MNs only)...\n');
bin_widths = [250, 500, 1000];
binned_maps = struct();

% Selected hindlimb extent (0 to 11,000 um, covering up to the most caudal hindlimb neuron at 10,672 um)
rc_min_cord = 0;
rc_max_cord = 11000;
lumb_min = 2500;
lumb_max = 9400;

for bw = bin_widths
    edges = rc_min_cord:bw:rc_max_cord;
    n_bins = length(edges) - 1;
    centers = (edges(1:end-1) + edges(2:end)) / 2;
    
    b_struct = struct();
    b_struct.bin_width = bw;
    b_struct.bin_edges = edges;
    b_struct.bin_centers = centers;
    b_struct.n_bins = n_bins;
    
    % Initialize maps
    b_struct.mean_act_left = nan(t_steps, n_bins);
    b_struct.sum_act_left = zeros(t_steps, n_bins);
    b_struct.count_left = zeros(1, n_bins);
    
    b_struct.mean_act_right = nan(t_steps, n_bins);
    b_struct.sum_act_right = zeros(t_steps, n_bins);
    b_struct.count_right = zeros(1, n_bins);
    
    for b = 1:n_bins
        b_low = edges(b);
        b_high = edges(b + 1);
        
        % Left side: HINDLIMB ONLY
        idx_b_l = find(is_hindlimb_neuron & latera < 0 & pos(:, 2) >= b_low & pos(:, 2) < b_high);
        b_struct.count_left(b) = length(idx_b_l);
        if ~isempty(idx_b_l)
            b_struct.sum_act_left(:, b) = sum(R(:, idx_b_l), 2);
            b_struct.mean_act_left(:, b) = mean(R(:, idx_b_l), 2);
        else
            b_struct.mean_act_left(:, b) = NaN; % Empty bin explicitly NaN
            b_struct.sum_act_left(:, b) = 0.0;
        end
        
        % Right side: HINDLIMB ONLY
        idx_b_r = find(is_hindlimb_neuron & latera > 0 & pos(:, 2) >= b_low & pos(:, 2) < b_high);
        b_struct.count_right(b) = length(idx_b_r);
        if ~isempty(idx_b_r)
            b_struct.sum_act_right(:, b) = sum(R(:, idx_b_r), 2);
            b_struct.mean_act_right(:, b) = mean(R(:, idx_b_r), 2);
        else
            b_struct.mean_act_right(:, b) = NaN;
            b_struct.sum_act_right(:, b) = 0.0;
        end
    end
    
    b_struct.empty_bins_left = sum(b_struct.count_left == 0);
    b_struct.empty_bins_right = sum(b_struct.count_right == 0);
    
    binned_maps.(sprintf('b%d', bw)) = b_struct;
    fprintf('  Bin width %4d um: %2d total bins, Empty bins: Left=%d, Right=%d\n', ...
        bw, n_bins, b_struct.empty_bins_left, b_struct.empty_bins_right);
end

%% 8. Save Complete Dataset
output_mat = fullfile(dataDir, 'ta_relocated_all_pools.mat');
fprintf('\nSaving complete all-pool dataset to: %s ...\n', output_mat);

mn_indices_all = find(types == 'MN');
R_MN = single(R(:, mn_indices_all));
pos_MN = pos(mn_indices_all, :);
lat_MN = latera(mn_indices_all);
mn_ids_MN = mn_ids(mn_indices_all);

save(output_mat, 'pool_info', 'binned_maps', 'bin_widths', ...
    'trace_comparisons', 'is_hindlimb_neuron', 'is_excluded_neuron', ...
    'R_MN', 'pos_MN', 'lat_MN', 'mn_ids_MN', 'mn_indices_all', ...
    'types', 'mn_ids', 'pos', 'latera', 'segments', ...
    't_steps', 'simSeed', 'net_seed', 'tonic_drive', ...
    'l3_l4_border', 'l4_l5_border', 'l5_l6_border', ...
    'target_span_min', 'target_span_max', '-v7.3');

fprintf('Successfully saved ta_relocated_all_pools.mat (Elapsed time: %.2f s)\n', toc(t_total_start));
