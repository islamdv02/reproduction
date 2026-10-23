%% =========================================================================
%% STAGE 8: Supplementary Simulation Movies Reproduction (Komi et al., 2026)
%%
%% Movies:
%%   Movie 1: 3D Spatiotemporal Network Activity Dynamics (AnimatedPlotRates)
%%   Movie 2: Multimodal Locomotion Animation (3D + EMG + PC Manifold)
%%   Movie 3: Transition from Random Network to 3D Structured Spinal Cord
%% =========================================================================

clear; clc; close all;
t_start = tic;

scriptDir = fileparts(mfilename('fullpath'));
rootDir = fullfile(scriptDir, '..');
srcDir = fullfile(rootDir, 'source');
resDir = fullfile(rootDir, 'results');
movieDir = fullfile(rootDir, 'movies');
logDir = fullfile(rootDir, 'logs');

if ~exist(movieDir, 'dir'), mkdir(movieDir); end
if ~exist(logDir, 'dir'), mkdir(logDir); end

logFile = fullfile(logDir, 'step8_simulation_movies.log');
diary(logFile);

fprintf('=================================================================\n');
fprintf('STAGE 8: Supplementary Movies Reproduction (Komi et al., 2026)\n');
fprintf('Timestamp: %s\n', datestr(now));
fprintf('MATLAB Version: %s\n', version);
fprintf('=================================================================\n');

% Add source directories
addpath(genpath(srcDir));
cd(srcDir);

%% 1. Load Simulated Network
simPath = fullfile(resDir, 'simulated_network.mat');
fprintf('Loading simulated network from: %s ...\n', simPath);
load(simPath, 'N');
fprintf('Loaded network: N = %d neurons, %d simulation steps.\n', size(N.ConnMat, 1), size(N.Rates, 1));

%% 2. Supplementary Movie 1: 3D Spatiotemporal Dynamics
m1_target = fullfile(movieDir, 'Supplementary_Movie_1_3D_Dynamics.mp4');
if ~exist(m1_target, 'file')
    fprintf('\n--- Generating Supplementary Movie 1 (3D Spatiotemporal Dynamics) ---\n');
    m1_name = 'Supplementary_Movie_1_3D_Dynamics';
    try
        % Run author's AnimatedPlotRates
        N.AnimatedPlotRates('SavePath', movieDir, 'SaveName', m1_name, 'ReplaySpeed', 1);
        
        % Clean up any leading space in filename created by upstream code
        raw_files = dir(fullfile(movieDir, ['*' m1_name '*.mp4']));
        if ~isempty(raw_files)
            actual_path = fullfile(raw_files(1).folder, raw_files(1).name);
            if ~strcmp(actual_path, m1_target)
                movefile(actual_path, m1_target);
            end
            fprintf('Saved Movie 1: %s\n', m1_target);
        end
    catch ME
        fprintf('Error in Movie 1 generation: %s\n', ME.message);
    end
else
    fprintf('Supplementary Movie 1 already exists on disk: %s\n', m1_target);
end

%% 3. Supplementary Movie 2: Multimodal Locomotion Animation
m2_target = fullfile(movieDir, 'Supplementary_Movie_2_Multimodal_Locomotion.mp4');
if ~exist(m2_target, 'file')
    fprintf('\n--- Generating Supplementary Movie 2 (Multimodal Locomotion Animation) ---\n');
    m2_name = 'Supplementary_Movie_2_Multimodal_Locomotion';
    try
        % Run author's PlotAnimatedNetworkEmgandPC
        PlotAnimatedNetworkEmgandPC(N, 'SavePath', movieDir, 'SaveName', m2_name);
        
        raw_files = dir(fullfile(movieDir, ['*' m2_name '*.mp4']));
        if ~isempty(raw_files)
            actual_path = fullfile(raw_files(1).folder, raw_files(1).name);
            if ~strcmp(actual_path, m2_target)
                movefile(actual_path, m2_target);
            end
            fprintf('Saved Movie 2: %s\n', m2_target);
        end
    catch ME
        fprintf('Error in Movie 2 generation: %s\n', ME.message);
    end
else
    fprintf('Supplementary Movie 2 already exists on disk: %s\n', m2_target);
end

%% 4. Supplementary Movie 3: Transition from Random to Structured Network
m3_target = fullfile(movieDir, 'Supplementary_Movie_3_Random_To_Structured.mp4');
if ~exist(m3_target, 'file')
    fprintf('\n--- Generating Supplementary Movie 3 (Random to Structured Transition) ---\n');
    m3_name = 'Supplementary_Movie_3_Random_To_Structured';
    try
        % Run author's PlotTransitionRandomStructured
        PlotTransitionRandomStructured(N, 'SavePath', movieDir, 'SaveName', m3_name);
        
        raw_files = dir(fullfile(movieDir, ['*' m3_name '*.mp4']));
        if ~isempty(raw_files)
            actual_path = fullfile(raw_files(1).folder, raw_files(1).name);
            if ~strcmp(actual_path, m3_target)
                movefile(actual_path, m3_target);
            end
            fprintf('Saved Movie 3: %s\n', m3_target);
        end
    catch ME
        fprintf('Error in Movie 3 generation: %s\n', ME.message);
    end
else
    fprintf('Supplementary Movie 3 already exists on disk: %s\n', m3_target);
end

t_total = toc(t_start);
fprintf('\n=================================================================\n');
fprintf('STAGE 8 SUPPLEMENTARY MOVIES COMPLETED (Elapsed: %.2f s)\n', t_total);
fprintf('=================================================================\n');

diary off;
exit(0);
