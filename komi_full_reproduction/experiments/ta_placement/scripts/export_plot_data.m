%% export_plot_data.m
% Exports plot-specific matrices from experiment_data.mat to a lightweight v7 mat file
% for seamless loading into Python matplotlib.

clear; clc;
scriptDir = fileparts(mfilename('fullpath'));
expDir = fullfile(scriptDir, '..');
dataDir = fullfile(expDir, 'data');

mat_file = fullfile(dataDir, 'experiment_data.mat');
if ~exist(mat_file, 'file')
    error('experiment_data.mat does not exist yet. Run simulation first.');
end

fprintf('Loading experiment_data.mat...\n');
load(mat_file);

fprintf('Exporting plot data to v7 format...\n');
% Extract realization 1 data for representative plots
r1 = realization_data(1);

% Bins (500 um)
plot_time = r1.condA.b500.plot_time_ms;
bin_centers = r1.condA.b500.bin_centers;
bin_counts_A = r1.condA.b500.bin_counts;
bin_counts_B = r1.condB.b500.bin_counts;
bin_counts_C = r1.condC.b500.bin_counts;

% Activity maps (Right MN)
act_A_sum = r1.condA.b500.plot_sum_act;
act_B_sum = r1.condB.b500.plot_sum_act;
act_C_sum = r1.condC.b500.plot_sum_act;

act_A_mean = r1.condA.b500.plot_mean_act;
act_B_mean = r1.condB.b500.plot_mean_act;
act_C_mean = r1.condC.b500.plot_mean_act;

% Left MN for Condition C check
act_C_sum_l = r1.condC.b500.plot_sum_act_l;
act_C_mean_l = r1.condC.b500.plot_mean_act_l;

% Trajectories
peak_A = r1.condA.b500.plot_peak_y;
coa_A = r1.condA.b500.plot_coa_y;

peak_B = r1.condB.b500.plot_peak_y;
coa_B = r1.condB.b500.plot_coa_y;

peak_C = r1.condC.b500.plot_peak_y;
coa_C = r1.condC.b500.plot_coa_y;

peak_C_l = r1.condC.b500.plot_peak_y_l;
coa_C_l = r1.condC.b500.plot_coa_y_l;

% Pool firing rate traces (window 10000:12000)
win = 10000:12000;
trace_ta_A = r1.condA.trace_ta(win);
trace_gm_A = r1.condA.trace_gm(win);
trace_sol_A = r1.condA.trace_sol(win);
trace_vm_A = r1.condA.trace_vm(win);
trace_bf_A = r1.condA.trace_bf(win);

trace_ta_C = r1.condC.trace_ta(win);
trace_gm_C = r1.condC.trace_gm(win);
trace_sol_C = r1.condC.trace_sol(win);
trace_vm_C = r1.condC.trace_vm(win);
trace_bf_C = r1.condC.trace_bf(win);

trace_ta_l_C = r1.condC.trace_ta_l(win);

% Save lightweight v7 MAT file
out_file = fullfile(dataDir, 'plot_export.mat');
save(out_file, ...
    'plot_time', 'bin_centers', ...
    'bin_counts_A', 'bin_counts_B', 'bin_counts_C', ...
    'act_A_sum', 'act_B_sum', 'act_C_sum', ...
    'act_A_mean', 'act_B_mean', 'act_C_mean', ...
    'act_C_sum_l', 'act_C_mean_l', ...
    'peak_A', 'coa_A', 'peak_B', 'coa_B', 'peak_C', 'coa_C', 'peak_C_l', 'coa_C_l', ...
    'trace_ta_A', 'trace_gm_A', 'trace_sol_A', 'trace_vm_A', 'trace_bf_A', ...
    'trace_ta_C', 'trace_gm_C', 'trace_sol_C', 'trace_vm_C', 'trace_bf_C', 'trace_ta_l_C', ...
    '-v7');

fprintf('Successfully exported plot data to: %s\n', out_file);
