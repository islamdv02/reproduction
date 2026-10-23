%% export_motoneuron_pools.m
% Extracts all 18 motoneuron pools, their segment ranges, counts, and spatial
% coordinates directly from baseline_network.mat as required by Section C.6.
% Outputs machine-readable results/motoneuron_pools.json and results/motoneuron_pools.csv.

clear; clc;
rootDir = fileparts(fileparts(mfilename('fullpath')));
sourceDir = fullfile(rootDir, 'source');
resultsDir = fullfile(rootDir, 'results');

cd(sourceDir);
addpath(genpath(sourceDir));

load(fullfile(resultsDir, 'baseline_network.mat'), 'N');

mn_mask = (N.Types == 'MN');
mn_pools = unique(N.MnID(mn_mask));
mn_pools = mn_pools(~isundefined(mn_pools));

table_entries = {};

fprintf('%-24s | %5s | %5s | %5s | %-12s | %-14s | %-10s\n', ...
    'Pool Name', 'Total', 'Left', 'Right', 'Segments', 'RC Range (um)', 'RC Mean');
fprintf('%s\n', repmat('-', 1, 95));

pool_data = struct([]);

for p = 1:length(mn_pools)
    p_name = char(string(mn_pools(p)));
    p_mask = mn_mask & (N.MnID == mn_pools(p));
    
    total_cnt = sum(p_mask);
    left_cnt = sum(p_mask & (N.Latera < 0));
    right_cnt = sum(p_mask & (N.Latera > 0));
    
    segs = unique(N.Segment(p_mask));
    segs = segs(~isundefined(segs));
    seg_list = cellstr(segs);
    seg_str = strjoin(seg_list, ', ');
    
    rc_vals = N.Position(p_mask, 2);
    ml_vals = N.Position(p_mask, 1);
    dv_vals = N.Position(p_mask, 3);
    
    rc_min = min(rc_vals);
    rc_max = max(rc_vals);
    rc_mean = mean(rc_vals);
    rc_span = rc_max - rc_min;
    
    entry = struct();
    entry.pool_name = p_name;
    entry.neuron_count_total = total_cnt;
    entry.neuron_count_left = left_cnt;
    entry.neuron_count_right = right_cnt;
    entry.segments = seg_list;
    entry.segment_string = seg_str;
    entry.rc_min_um = round(rc_min, 1);
    entry.rc_max_um = round(rc_max, 1);
    entry.rc_mean_um = round(rc_mean, 1);
    entry.rc_span_um = round(rc_span, 1);
    entry.ml_mean_um = round(mean(ml_vals), 1);
    entry.dv_mean_um = round(mean(dv_vals), 1);
    
    pool_data = [pool_data; entry];
    
    fprintf('%-24s | %5d | %5d | %5d | %-12s | [%6.1f, %6.1f] | %7.1f\n', ...
        p_name, total_cnt, left_cnt, right_cnt, seg_str, rc_min, rc_max, rc_mean);
end

% Sort pools by rostrocaudal mean position (rostral to caudal)
[~, sort_order] = sort([pool_data.rc_mean_um]);
pool_data = pool_data(sort_order);

% Save JSON
json_path = fullfile(resultsDir, 'motoneuron_pools.json');
fid = fopen(json_path, 'w');
fwrite(fid, jsonencode(pool_data, 'PrettyPrint', true));
fclose(fid);
fprintf('\nSaved: %s\n', json_path);

% Save CSV
csv_path = fullfile(resultsDir, 'motoneuron_pools.csv');
fid = fopen(csv_path, 'w');
fprintf(fid, 'pool_name,neuron_count_total,neuron_count_left,neuron_count_right,segments,rc_min_um,rc_max_um,rc_mean_um,rc_span_um,ml_mean_um,dv_mean_um\n');
for p = 1:length(pool_data)
    fprintf(fid, '"%s",%d,%d,%d,"%s",%.1f,%.1f,%.1f,%.1f,%.1f,%.1f\n', ...
        pool_data(p).pool_name, ...
        pool_data(p).neuron_count_total, ...
        pool_data(p).neuron_count_left, ...
        pool_data(p).neuron_count_right, ...
        pool_data(p).segment_string, ...
        pool_data(p).rc_min_um, ...
        pool_data(p).rc_max_um, ...
        pool_data(p).rc_mean_um, ...
        pool_data(p).rc_span_um, ...
        pool_data(p).ml_mean_um, ...
        pool_data(p).dv_mean_um);
end
fclose(fid);
fprintf('Saved: %s\n', csv_path);

exit(0);
