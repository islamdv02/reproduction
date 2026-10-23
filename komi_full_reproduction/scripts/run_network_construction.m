%% run_network_construction.m
% Minimal, non-intrusive execution wrapper for Komi et al. (2026) Network Construction.
% Uses ONLY the authors' original classes and parameters from source/.
% Sets random seed, instantiates Network, validates dimensions, and saves baseline_network.mat.

clear;
clc;

t_start = tic;
scriptDir = fileparts(mfilename('fullpath'));
rootDir = fullfile(scriptDir, '..');
sourceDir = fullfile(rootDir, 'source');
resultsDir = fullfile(rootDir, 'results');
logsDir = fullfile(rootDir, 'logs');

if ~exist(resultsDir, 'dir'), mkdir(resultsDir); end
if ~exist(logsDir, 'dir'), mkdir(logsDir); end

% Open log file
logFile = fullfile(logsDir, 'step1_network_construction.log');
diary(logFile);
diary on;

fprintf('=================================================================\n');
fprintf('STAGE 1: Network Construction (Komi et al., 2026)\n');
fprintf('Timestamp: %s\n', datetime('now'));
fprintf('MATLAB Version: %s\n', version);
fprintf('Source Directory: %s\n', sourceDir);
fprintf('=================================================================\n');

% Set working directory to source directory so relative files load correctly
cd(sourceDir);
addpath(genpath(sourceDir));

%% 1. Random Number Generator State
initialSeed = 42;
rng(initialSeed, 'twister');
fprintf('Pre-instantiation RNG Seed: %d (twister)\n', initialSeed);

%% 2. Global Parameters (Identical to InstantiateModel.m)
gc = 0.5; % Global synaptic strength parameter
Density = 0.8; % global density (relative number of neurons)
Symmetry = 1; % symmetric with respect to midline
Balance = 1; % E/I synaptic input balance
SynpaticDistributionSpatialStd = 500; % um
verbose = 0; % headless execution
Segments = [append('T',string([13])), append('L',string([1:6])), append('S',string([1:4]))];

fprintf('\nModel Configuration:\n');
fprintf('  gc: %.2f\n', gc);
fprintf('  Density: %.2f\n', Density);
fprintf('  Symmetry: %d\n', Symmetry);
fprintf('  Balance: %d\n', Balance);
fprintf('  ProjWidth: %d um\n', SynpaticDistributionSpatialStd);
fprintf('  Segments: %s\n', strjoin(Segments, ', '));

%% 3. Cell Type Definitions & Spatial Biases (Identical to InstantiateModel.m)
fprintf('\nConfiguring NetworkParameters and 9 ventral cell types...\n');
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

% Reduce motoneuron transmission to interneurons
MyNetwork.SetCellBiasPop('MN','All',0.1);

%% 4. Instantiate Network Object
fprintf('\nInstantiating Network object using authors original code...\n');
ticNet = tic;
N = Network(Segments, Density, Symmetry, MyNetwork, ...
    'Balance', Balance, ...
    'ProjWidth', SynpaticDistributionSpatialStd, ...
    'Verbose', verbose);
t_net = toc(ticNet);
fprintf('Network instantiation completed in %.2f seconds.\n', t_net);

%% 5. Validate Dimensions and Conventions
N_neurons = size(N.ConnMat, 1);
assert(size(N.ConnMat, 2) == N_neurons, 'ConnMat must be square!');
assert(size(N.Position, 1) == N_neurons, 'Position rows must equal N_neurons!');
assert(size(N.Position, 2) == 3, 'Position must have 3 spatial dimensions (ML, RC, DV)!');
assert(length(N.Types) == N_neurons, 'Types length must equal N_neurons!');
assert(length(N.Latera) == N_neurons, 'Latera length must equal N_neurons!');
assert(length(N.Segment) == N_neurons, 'Segment length must equal N_neurons!');

% Verify Row-sum E/I balance (Balance = 1)
row_sums = sum(N.ConnMat, 2);
mean_row_sum = mean(abs(row_sums));
fprintf('Row-sum E/I balance check: mean |sum_j W_ij| = %.6e\n', mean_row_sum);

% Verify Coordinate Ranges
ml_range = [min(N.Position(:,1)), max(N.Position(:,1))];
rc_range = [min(N.Position(:,2)), max(N.Position(:,2))];
dv_range = [min(N.Position(:,3)), max(N.Position(:,3))];
fprintf('Spatial Coordinates Bounds (um):\n');
fprintf('  ML (Col 1): [%.1f, %.1f]\n', ml_range(1), ml_range(2));
fprintf('  RC (Col 2): [%.1f, %.1f]\n', rc_range(1), rc_range(2));
fprintf('  DV (Col 3): [%.1f, %.1f]\n', dv_range(1), dv_range(2));

% Verify Cell Counts
fprintf('\nNeuron Population Counts (Total N = %d):\n', N_neurons);
cell_types = unique(N.Types);
for c = 1:length(cell_types)
    ct = cell_types(c);
    cnt = sum(N.Types == ct);
    fprintf('  %-8s: %4d (%5.1f%%)\n', string(ct), cnt, cnt / N_neurons * 100);
end

%% 6. Save Baseline Network Object
targetFile = fullfile(resultsDir, 'baseline_network.mat');
fprintf('\nSaving baseline network object to: %s ...\n', targetFile);
save(targetFile, 'N', 'initialSeed', 'gc', 'Density', 'Symmetry', 'Balance', ...
     'SynpaticDistributionSpatialStd', 'Segments', '-v7.3');
fprintf('Saved baseline_network.mat successfully.\n');

t_total = toc(t_start);
fprintf('\n=================================================================\n');
fprintf('STAGE 1 NETWORK CONSTRUCTION SUCCESSFUL (Elapsed: %.2f s)\n', t_total);
fprintf('=================================================================\n');

diary off;
exit(0);
