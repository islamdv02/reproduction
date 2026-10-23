%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%% REVIEWERS CODE TESTING %%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
clear
%% Model Instantiation Global Model Parameters
gc = 0.5; % Global synaptic strength parameter
Density = 0.8; %global density (relative number of neurons)
Symmetry = 1; %is the network symetric with respect to the middline
Balance = 1; %is the network balanced (E/I synatic input balance)
SynpaticDistributionSpatialStd = 500; %um
verbose = 1; % is the eigenspectrum and modes shown after instantiation
Segments = [append('T',string([13])),append('L',string([1:6])),append('S',string([1:4]))]; % cell array of strings of the segments to include in the model.
%% Begin Model 
MyNetwork = NetworkParameters();
% Set Ventral Interneurons population parameters
MyNetwork.AddCelltype(Celltype.V2a_2,'bi','ven','lat','','ipsi','','',7000,'SynStrength',gc*1);
MyNetwork.AddCelltype(Celltype.V2a_1,'cau','ven','med','','ipsi','','',500,'SynStrength',gc*1);
MyNetwork.AddCelltype(Celltype.V1,'ro','ven','','','ipsi','','',2000,'SynStrength',gc*0.2)
MyNetwork.AddCelltype(Celltype.V2b,'cau','ven','lat','','ipsi','','',4000,'SynStrength',gc*1)
MyNetwork.AddCelltype(Celltype.V0d,'loc','ven','med','','contra','','',500,'SynStrength',gc*1)
MyNetwork.AddCelltype(Celltype.V0v,'ro','loc','med','','contra','','',3400,'SynStrength',gc*1);
MyNetwork.AddCelltype(Celltype.DI6,'cau','dor','med','','contra','','',5000,'SynStrength',gc*1)
MyNetwork.AddCelltype(Celltype.V3,'cau','ven','lat','','contra','','',500,'SynStrength',gc*1);
MyNetwork.AddCelltype(Celltype.MN,'loc','ven','lat','','ipsi','','',300,'SynStrength',gc*1);

% Reduce synaptic strenggth of motoneurons to all interneuron populations
MyNetwork.SetCellBiasPop('MN','All',0.1);
%% Instantiate the model 
N = Network(Segments,Density,Symmetry,MyNetwork,'Balance',Balance,'ProjWidth',SynpaticDistributionSpatialStd,'Verbose',verbose);
%% Simple Simulation with uniform input to all cell in the network
t_steps = 10000; % Set during of
I_e = zeros(size(N.ConnMat,1),t_steps);
I_e(:,:) = 30;
N.Simulate(t_steps,'I_e',I_e); 
%% Visualize dynamics 
N.AnimatedPlotRates
%% Plot EMGs of interest 
N.PlotEMG
%% Plot Firing Rates
N.PlotRates
%% Plot Simulated Spiking 
N.PlotRaster

    

