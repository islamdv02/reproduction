%% export_topography_data.m
% Exports exact motoneuron pool coordinates for the 13 hindlimb pools
% for Condition C (baseline L2-L4 TA) and Condition D (relocated L4-L5 TA)
% for Figure 2D-style topography before/after comparison.

clear; clc;
scriptDir = fileparts(mfilename('fullpath'));
expDir = fullfile(scriptDir, '..');
repoDir = fullfile(expDir, '..', '..');
sourceDir = fullfile(repoDir, 'source');
resultsDir = fullfile(repoDir, 'results');
dataDir = fullfile(expDir, 'data');

fprintf('Loading baseline network object...\n');
addpath(genpath(sourceDir));
load(fullfile(resultsDir, 'baseline_network.mat'), 'N');

% Exactly the 13 pools in published order
selected_13_pools = {
    'Vastus Lateralis',    'VLat';
    'Vastus Medialis',     'VMed';
    'Iliopsoas',           'Ilio';
    'Rectus Femoris',      'RF';
    'Tibialis Anterior',   'TA';    % Cyan highlighted
    'Gastrocnemius',       'GM';    % Magenta highlighted
    'Gluteus',             'Glut';
    'Biceps Femoris',      'BF';
    'Semitendinosus',      'ST';
    'Soleus',              'Sol';
    'Plantar Flexor',      'PF';
    'Extensor Digitorum',  'EdL';
    'Tail',                'Tail'
};

N_neurons = size(N.Position, 1);
pos_C = N.Position;
pos_D = pos_C;

% Identify TA neurons
ta_idx = find(string(N.Types) == 'MN' & string(N.MnID) == 'Tibialis Anterior');
orig_ta_rc = pos_C(ta_idx, 2);
orig_min = min(orig_ta_rc);
orig_max = max(orig_ta_rc);
target_span_min = 5600.0;
target_span_max = 7900.0;

reloc_ta_rc = target_span_min + (orig_ta_rc - orig_min) * ...
    ((target_span_max - target_span_min) / (orig_max - orig_min));

pos_D(ta_idx, 2) = reloc_ta_rc;

% Verify non-TA neurons are 100% bit-for-bit identical
non_ta_idx = setdiff(1:N_neurons, ta_idx);
max_diff_non_ta = max(max(abs(pos_C(non_ta_idx, :) - pos_D(non_ta_idx, :))));
assert(max_diff_non_ta == 0, 'Non-TA positions are not identical between Condition C and D!');
fprintf('Verified: non-TA coordinates are 100%% identical (max diff = %.1e)\n', max_diff_non_ta);

% Verify TA relocation boundaries
assert(min(reloc_ta_rc) >= 5500.0 && max(reloc_ta_rc) <= 8000.0, 'TA outside L4-L5!');
fprintf('Condition C TA: count=%d, centroid=%.1f um, range=[%.1f, %.1f] um, span=%.1f um\n', ...
    length(ta_idx), mean(orig_ta_rc), orig_min, orig_max, orig_max - orig_min);
fprintf('Condition D TA: count=%d, centroid=%.1f um, range=[%.1f, %.1f] um, span=%.1f um\n', ...
    length(ta_idx), mean(reloc_ta_rc), min(reloc_ta_rc), max(reloc_ta_rc), max(reloc_ta_rc) - min(reloc_ta_rc));

% Build export structure for the 13 pools
pools_export = struct([]);
for p = 1:size(selected_13_pools, 1)
    p_name = selected_13_pools{p, 1};
    p_abbr = selected_13_pools{p, 2};
    p_mask = (string(N.MnID) == p_name);
    
    idx_p = find(p_mask);
    rc_c = pos_C(idx_p, 2);
    rc_d = pos_D(idx_p, 2);
    ml_c = pos_C(idx_p, 1);
    ml_d = pos_D(idx_p, 1);
    dv_c = pos_C(idx_p, 3);
    dv_d = pos_D(idx_p, 3);
    lat = N.Latera(idx_p);
    
    entry = struct();
    entry.pool_index = p;
    entry.pool_name = p_name;
    entry.abbreviation = p_abbr;
    entry.neuron_count_total = length(idx_p);
    entry.neuron_count_left = sum(lat < 0);
    entry.neuron_count_right = sum(lat > 0);
    entry.rc_condC = rc_c;
    entry.rc_condD = rc_d;
    entry.ml = ml_c;
    entry.dv = dv_c;
    entry.latera = lat;
    entry.centroid_condC = mean(rc_c);
    entry.centroid_condD = mean(rc_d);
    entry.min_condC = min(rc_c);
    entry.max_condC = max(rc_c);
    entry.min_condD = min(rc_d);
    entry.max_condD = max(rc_d);
    entry.span_condC = max(rc_c) - min(rc_c);
    entry.span_condD = max(rc_d) - min(rc_d);
    entry.is_ta = strcmp(p_abbr, 'TA');
    entry.is_gm = strcmp(p_abbr, 'GM');
    
    pools_export = [pools_export; entry];
end

% Verified segment boundaries from matGeometry.mat
seg_names = {'T13', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'S1', 'S2', 'S3', 'S4'};
seg_boundaries = [0.0, 1300.0, 2500.0, 4000.0, 5500.0, 6800.0, 8000.0, 9400.0, 10800.0, 12000.0, 12900.0, 13900.0];

out_file = fullfile(dataDir, 'topography_export.mat');
save(out_file, 'pools_export', 'seg_names', 'seg_boundaries', 'max_diff_non_ta', '-v7');
fprintf('Successfully saved topography export to: %s\n', out_file);
