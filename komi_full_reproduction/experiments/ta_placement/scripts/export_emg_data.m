%% export_emg_data.m
% Generates synthetic EMG traces using the authors' exact algorithm from PlotEMG.m
% for Conditions C and D with matched random seed carriers.
% Exports raw firing rates, raw synthetic EMG, and rectified envelope
% for TA, VM, BF, GM, Soleus across representative steady-state cycles.

clear; clc;
scriptDir = fileparts(mfilename('fullpath'));
expDir = fullfile(scriptDir, '..');
repoDir = fullfile(expDir, '..', '..');
compatDir = fullfile(repoDir, 'scripts', 'compat');
sourceDir = fullfile(repoDir, 'source');
dataDir = fullfile(expDir, 'data');

addpath(compatDir);
addpath(genpath(sourceDir));

fprintf('Loading experiment_data.mat...\n');
load(fullfile(dataDir, 'experiment_data.mat'), 'realization_data');

r1 = realization_data(1);

% Time window: 10000 to 12500 ms (2500 ms, ~3.3 locomotor cycles at 1.34 Hz)
win = 10000:12500;
t_rel_s = (win - win(1)) / 1000.0;
t_ms = win;

% 5 Muscles to analyze:
% Order: Vastus Medialis (VM, Knee Ext), Biceps Femoris (BF, Knee Flex / Hip Ext),
%        Tibialis Anterior (TA, Ankle Dorsiflex), Gastrocnemius (GM, Ankle Plantarflex),
%        Soleus (Sol, Ankle Plantarflex)
muscles = {
    'Vastus Medialis',     'VM',  'Knee Extensor';
    'Biceps Femoris',      'BF',  'Knee Flexor / Hip Extensor';
    'Tibialis Anterior',   'TA',  'Ankle Dorsiflexor';
    'Gastrocnemius',       'GM',  'Ankle Plantarflexor';
    'Soleus',              'Sol', 'Ankle Plantarflexor'
};

% Neuron counts on Left side for Realization 1:
% VM: 55, BF: 43, TA: 36, GM: 34, Sol: 67
counts_left = [55, 43, 36, 34, 67];

emg_data = struct();
emg_data.time_ms = t_ms;
emg_data.t_rel_s = t_rel_s;

noiselevel = 0.10;

zscore_fn = @(x) (x - mean(x)) ./ (std(x) + eps);

for m = 1:size(muscles, 1)
    m_name = muscles{m, 1};
    m_abbr = muscles{m, 2};
    m_role = muscles{m, 3};
    n_mn = counts_left(m);
    
    switch m_abbr
        case 'VM'
            rate_C = r1.condC.trace_vm_l(win);
            rate_D = r1.condD.trace_vm_l(win);
        case 'BF'
            rate_C = r1.condC.trace_bf_l(win);
            rate_D = r1.condD.trace_bf_l(win);
        case 'TA'
            rate_C = r1.condC.trace_ta_l(win);
            rate_D = r1.condD.trace_ta_l(win);
        case 'GM'
            rate_C = r1.condC.trace_gm_l(win);
            rate_D = r1.condD.trace_gm_l(win);
        case 'Sol'
            rate_C = r1.condC.trace_sol_l(win);
            rate_D = r1.condD.trace_sol_l(win);
    end
    
    % Pool activation sum
    prob_C = rate_C * n_mn;
    prob_D = rate_D * n_mn;
    
    % Condition C synthetic EMG
    rng(1000 + m * 37, 'twister');
    sig_C = randn(size(prob_C)) * noiselevel .* binornd(1, normcdf(zscore_fn(prob_C)));
    sig_C = sig_C .* prob_C + randn(size(prob_C)) * noiselevel;
    env_C = movmean(abs(sig_C), 20);
    
    % Condition D synthetic EMG (RESET TO IDENTICAL RNG STREAM FOR MATCHED RANDOMNESS)
    rng(1000 + m * 37, 'twister');
    sig_D = randn(size(prob_D)) * noiselevel .* binornd(1, normcdf(zscore_fn(prob_D)));
    sig_D = sig_D .* prob_D + randn(size(prob_D)) * noiselevel;
    env_D = movmean(abs(sig_D), 20);
    
    entry = struct();
    entry.muscle_name = m_name;
    entry.abbreviation = m_abbr;
    entry.functional_role = m_role;
    entry.neuron_count_left = n_mn;
    
    entry.rate_condC = rate_C;
    entry.rate_condD = rate_D;
    
    entry.sig_condC = sig_C;
    entry.sig_condD = sig_D;
    
    entry.env_condC = env_C;
    entry.env_condD = env_D;
    
    emg_data.(m_abbr) = entry;
    
    fprintf('Muscle %s (%s): Max Rate C=%.1f Hz, D=%.1f Hz | Max Env C=%.2f, D=%.2f\n', ...
        m_abbr, m_name, max(rate_C), max(rate_D), max(env_C), max(env_D));
end

out_file = fullfile(dataDir, 'emg_export.mat');
save(out_file, 'emg_data', 'muscles', '-v7');
fprintf('Saved EMG export data to: %s\n', out_file);
