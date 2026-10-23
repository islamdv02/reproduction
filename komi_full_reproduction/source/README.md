# SpinalProjectome

**SpinalProjectome** is a MATLAB-based framework designed to simulate the spinal cord circuitry of a mouse. It enables detailed modeling of neuronal populations with diverse cell types, spatial projection biases, and network connectivity, providing a powerful tool for studying spinal cord dynamics.

---

## Overview

This framework allows you to:
- Define multiple neuronal cell types, each with specific properties and spatial biases.
- Build a spatially organized network reflecting the anatomy and projection patterns of the spinal cord.
- Run dynamic simulations with customizable inputs.
- Visualize neuronal activity through firing rates, spike rasters, and muscle-like signals (EMG).

---

## Requirements

- MATLAB (recommended version: 2024b or higher)
- MATLAB toolboxes (possibly, I just listed here all the toolboxes installed on my MATLAB distribution :D):

Computer Vision Toolbox                               Version 24.2        (R2024b)
Curve Fitting Toolbox                                 Version 24.2        (R2024b)
DSP System Toolbox                                    Version 24.2        (R2024b)
Deep Learning Toolbox                                 Version 24.2        (R2024b)
Image Processing Toolbox                              Version 24.2        (R2024b)
Parallel Computing Toolbox                            Version 24.2        (R2024b)
Partial Differential Equation Toolbox                 Version 24.2        (R2024b)
Phased Array System Toolbox                           Version 24.2        (R2024b)
Predictive Maintenance Toolbox                        Version 24.2        (R2024b)
Reinforcement Learning Toolbox                        Version 24.2        (R2024b)
Signal Processing Toolbox                             Version 24.2        (R2024b)
Statistics and Machine Learning Toolbox               Version 24.2        (R2024b)
System Identification Toolbox                         Version 24.2        (R2024b)
Wavelet Toolbox                                       Version 24.2        (R2024b)

- Clone or download this repository and set your MATLAB path accordingly.
- Set the root of your working directory at the level of the repository.
---

## Step-by-Step Usage

An example usage of the framework can be found in the **InstantiateModel** file

### 1. Instantiate Network Parameters

First, you will create the container for all network parameters and cell types:

```matlab
MyNetwork = NetworkParameters();
```
---

### 2. Add Neuronal Cell Types
Use the method AddCelltype() to add neuron populations. When doing so, specify their spatial and projection biases, cell numbers, and connection properties:

```matlab
% Example: Adding a V2a-2 interneuron with spatial biases
MyNetwork.AddCelltype( Celltype.V2a_2, ...
    'bi', ...                % BiasRC: 'bi' (bilateral)
    'ven', ...               % BiasDV: 'ven' (ventral)
    'lat', ...               % BiasML: 'lat' (lateral)
    '', ...                  % BiasMN: none specified
    'ipsi', ...              % BiasContraIpsi: ipsilateral
    '', ...                  % BiasSegment: none specified
    '', ...                  % BiasLayer: none specified
    600, ...                 % LengthScale: spatial spread in micrometers
    'Gain', 0.7, ...         % Gain: Slope of the activation function of this celltype (sensitivity to input)
    'SynStrength', 1 );   % SynStrength: The mean of the Gaussian distribution from which the synaptic strength are sampled.
```

#### Required Bias Properties (in the right order)

These parameters are specified as required arguments of the AddCelltype method as seen in the example.


| Property          | Description                                               | Possible Values / Explanation                         |
|-------------------|-----------------------------------------------------------|--------------------------------------------------------|
| `BiasRC`         | Rostrocaudal bias (orientation along the caudal-rostral axis) | `'cau'`, `'ro'`, `'bi'`, `'loc'` or `''` (none)       |
| `BiasDV`         | Dorsoventral bias (dorsal vs ventral position)               | `'dor'`, `'ven'`, `'loc'` or `''`                     |
| `BiasML`         | Mediolateral bias (medial vs lateral position)             | `'med'`, `'lat'`, `'loc'`, or `''`                       |
| `BiasMN`         | Motoneurons bias (medial vs lateral position)             | `'Flex'`, `'Ext'`, `'FlexOnly'`, `'ExtOnly'`, or `''`     |
| `BiasContraIpsi` | Contralateral vs Ipsilateral connection bias               | `'contra'`, `'ipsi'`, `'bi'` or `''`                     |
| `BiasLayer`      | Laminar bias (connection in specific laminar layers)        | only `''` for the moment |
| `BiasSeg`    | Segment bias (e.g., `'T13'`, `'L1'`, `'S4'`)                 | e.g., `'T13'`, `'L1'`, `'S4'`, or a string array of the segments of interest |
| `LengthScale` | Spatial mean projection length (μm)	            | e.g., `500`, `600`    |

#### Optional Properties 

These parameters are specified as variable arguments in the AddCelltype method as seen in the example.

| Property          | Description                                               | Possible Values / Explanation                         |
|-------------------|-----------------------------------------------------------|--------------------------------------------------------|
| `Gain`         | Rostrocaudal bias (orientation along the caudal-rostral axis) | `'cau'`, `'ro'`, `'bi'`, `'loc'` or `''` (none)                  |
| `Threshold`         | Dorsoventral bias (dorsal vs ventral position)               | `'dors'`, `'ven'`, `'loc'` or `''`                        |
| `F_max`         | Mediolateral bias (medial vs lateral position)             | `'med'`, `'lat'`, `'loc'`, or `''`                        |
| `SynStrength`         | Mediolateral bias (medial vs lateral position)             | `'med'`, `'lat'`, `'loc'`, or `''`                        |

---

### 4. Modify Cell Types Specific Biases

Use the method SetCellBiasPop() to modify a specific celltype-to-celltype connection probability. When doing so, you effectively modify how probable the first populations connects to the second.

```matlab
MyNetwork.SetCellBiasPop('V2a_2', 'All', 0.1); % the probability of V2a_2 connecting to all other populations is set to 0.1
MyNetwork.SetCellBiasPop('V1', 'V3', 0.5); % the probability of V1 connecting to V3 other populations is set to 0.5
```

### 5. Instantiate the network

Once all parameters are set, you can instantiate a Network object that will use all prior knowledge on celltype spatial distributions, motoneuron segmental locations and numbers and other information to construct a network embedding some known features of the mouse spinal cord.

```matlab
    Density = 0.8; %global density (relative number of neurons)
    Symmetry = 1; %is the network symetric with respect to the middline
    Balance = 1; %is the network balanced (E/I synatic input balance)
    SynpaticDistributionSpatialStd = 500; % it sets the width of the synaptic terminal distributions from which synapses are sampled
    verbose = 1; % is the eigenspectrum and modes shown after instantiation
    Segments = [append('T',string([13])),append('L',string([1:6])),append('S',string([1:4]))]; % cell array of strings of the segments to include in the model.

%% Instantiate the network with all its parameters.
    N = Network(Segments, Density, Symmetry, MyNetwork, 'Balance', Balance, 'ProjWidth', SynpaticDistributionSpatialStd, 'Verbose', verbose);
```

### 6. Run the simulation
You can now run a simulation by simply calling the method N.Simulate() with the appropriate parameters. This will iteratively solve a rate-based model of the network.

```matlab
t_steps = 10000; % Set duration of the simulation in ms
I_e = zeros(size(N.ConnMat,1),t_steps); % initialise an input matrix (NumberOfNeuronsXDuration). You hence can design the input to any cell the way you want.
I_e(:,:) = 30;
N.Simulate(t_steps,'I_e',I_e); 
```

#### Required Simulation Parameters 

Only the simulation duration parameter is a  required argument of the Simulate() method as seen in the example.

| Parameters          | Description                                               | Possible Values / Explanation                         |
|-------------------|-----------------------------------------------------------|--------------------------------------------------------|
| `t_steps`         | Duration of the simulation | e.g `'1000'` in ms  |

#### Optional Parameters 

These parameters are specified as variable arguments in the Simulate() method as seen in the example.

| Property          | Description                                               | Possible Values / Explanation                         |
|-------------------|-----------------------------------------------------------|--------------------------------------------------------|
| `I_e`         | External Voltage input to each neuron over time     | Matrix (NumberOfNeurons X Duration) |
| `tau_V`        | Membrane time constant of each neuron over time  | Matrix (NumberOfNeurons X Duration)  |
| `fmax`         | Maximum Firing frequency of each neuron   | Vector (NumberOfNeurons X 1)  |
| `gain`         | Gain of the activation function of each neuron over time| Matrix (NumberOfNeurons X Duration)    |
| `V_init`         | Initial Membrane Voltage | Vector (NumberOfNeurons X 1)   |
| `threshold`         | Activation threshold of each neuron over time  | Matrix (NumberOfNeurons X Duration)     |
| `noise_ampl`         | Amplification factor of the Gaussian noise on the input | e.g `0.5` |
| `seed`         | Seed of the simulation for reproducibility  | e.g `20` |

