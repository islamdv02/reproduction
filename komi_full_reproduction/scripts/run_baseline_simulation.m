%% run_baseline_simulation.m
% Minimal execution wrapper for Stage 2: Baseline Locomotor Rate Simulation.
% Uses ONLY the authors' original Simulate method from @Network/Simulate.m.
% Duration: 10,000 ms (10 s), dt = 1 ms, tonic drive I_e = 30 pA, seed = 5.

clear;
clc;

t_start = tic;
scriptDir = fileparts(mfilename('fullpath'));
rootDir = fullfile(scriptDir, '..');
sourceDir = fullfile(rootDir, 'source');
resultsDir = fullfile(rootDir, 'results');
logsDir = fullfile(rootDir, 'logs');

logFile = fullfile(logsDir, 'step2_baseline_simulation.log');
diary(logFile);
diary on;

fprintf('=================================================================\n');
fprintf('STAGE 2: Baseline Locomotor Rate Simulation (Komi et al., 2026)\n');
fprintf('Timestamp: %s\n', datetime('now'));
fprintf('MATLAB Version: %s\n', version);
fprintf('=================================================================\n');

cd(sourceDir);
addpath(genpath(sourceDir));

%% 1. Load Baseline Network Object
networkFile = fullfile(resultsDir, 'baseline_network.mat');
fprintf('Loading baseline network object from: %s ...\n', networkFile);
load(networkFile, 'N');
N_neurons = size(N.ConnMat, 1);
fprintf('Loaded network: N = %d neurons.\n', N_neurons);

%% 2. Configure Simulation Parameters
t_steps = 22000; % 22 seconds duration (1 ms per step) to capture >= 27 steady-state cycles
simSeed = 5; % simulation RNG seed for Gaussian noise
fprintf('Setting up simulation: %d steps (1 ms/step), tonic I_e = 25 pA, seed = %d...\n', t_steps, simSeed);

I_e = zeros(N_neurons, t_steps);
I_e(:, :) = 25;

%% 3. Run Authors' Original Simulate Method
fprintf('Running N.Simulate using authors original code...\n');
ticSim = tic;
h_dummy = figure('Visible', 'off');
N.Simulate(t_steps, 'I_e', I_e, 'seed', simSeed);
if isvalid(h_dummy), close(h_dummy); end
t_sim = toc(ticSim);
fprintf('Simulation completed in %.2f seconds (%.2f s simulated per real second).\n', ...
    t_sim, (t_steps/1000) / t_sim);

%% 4. Validate Simulated Outputs
assert(size(N.Rates, 1) == t_steps, 'Rates rows != t_steps!');
assert(size(N.Rates, 2) == N_neurons, 'Rates cols != N_neurons!');
assert(size(N.Voltage, 1) == t_steps, 'Voltage rows != t_steps!');
assert(size(N.Voltage, 2) == N_neurons, 'Voltage cols != N_neurons!');

mean_rate = mean(N.Rates(:));
max_rate = max(N.Rates(:));
active_frac = sum(mean(N.Rates, 1) > 0.1) / N_neurons * 100;
fprintf('\nSimulation Statistics:\n');
fprintf('  Mean Firing Rate across all neurons & time: %.2f Hz\n', mean_rate);
fprintf('  Max Firing Rate: %.2f Hz\n', max_rate);
fprintf('  Active Neurons (>0.1 Hz mean): %.1f%%\n', active_frac);

%% 5. Compute PCA Manifold (for Figure 3F & Movies)
fprintf('\nComputing Principal Components using N.ComputePC...\n');
N.ComputePC('Estimated', 0);
assert(~isempty(N.PC), 'PC matrix should not be empty!');
fprintf('Computed %d principal components over %d time steps.\n', size(N.PC, 2), size(N.PC, 1));

%% 6. Save Simulated Network Object
targetFile = fullfile(resultsDir, 'simulated_network.mat');
fprintf('\nSaving simulated network object to: %s ...\n', targetFile);
save(targetFile, 'N', 't_steps', 'simSeed', '-v7.3');
fprintf('Saved simulated_network.mat successfully.\n');

t_total = toc(t_start);
fprintf('\n=================================================================\n');
fprintf('STAGE 2 SIMULATION COMPLETED SUCCESSFULLY (Elapsed: %.2f s)\n', t_total);
fprintf('=================================================================\n');

diary off;
exit(0);
