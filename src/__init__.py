"""
Spinal Projectome Neural Modeling Package.
Faithful reproduction of Komi et al., Nature Communications, 2026.
"""

from .data_loader import SpinalDataLoader
from .connectivity import (
    compute_pairwise_distances,
    compute_spatial_connection_probability,
    balance_connectivity,
    rescale_connectivity
)
from .network import Celltype, NetworkParameters, Network
from .dynamics import (
    tanh_activation,
    euler_step_voltage,
    euler_step_adaptation,
    compute_spectral_analysis
)
from .simulation import SimulationConfig, SimulationResult, Simulator
from .locomotion import (
    generate_synthetic_emg,
    compute_traveling_wave,
    compute_pca_dynamics,
    compute_population_phases,
    generate_poisson_spikes_and_rates,
    MUSCLE_FLEX_EXT
)
from .gait_control import (
    DescendingDriveConfig,
    classify_gait,
    simulate_gait_regime,
    simulate_descending_ramp,
    run_descending_drive_sweep
)
from .figure4_analysis import (
    plot_panel_4a_tanh_gain_curves,
    plot_panel_4b_descending_tract_maps,
    plot_panel_4c_descending_ramp,
    plot_panel_4d_gait_emg_patterns,
    plot_panel_4e_polar_phase_transitions,
    plot_panel_4fg_frequency_amplitude,
    generate_figure4_complete
)

__all__ = [
    "SpinalDataLoader",
    "compute_pairwise_distances",
    "compute_spatial_connection_probability",
    "balance_connectivity",
    "rescale_connectivity",
    "Celltype",
    "NetworkParameters",
    "Network",
    "tanh_activation",
    "euler_step_voltage",
    "euler_step_adaptation",
    "compute_spectral_analysis",
    "SimulationConfig",
    "SimulationResult",
    "Simulator",
    "generate_synthetic_emg",
    "compute_traveling_wave",
    "compute_pca_dynamics",
    "compute_population_phases",
    "generate_poisson_spikes_and_rates",
    "MUSCLE_FLEX_EXT",
    "DescendingDriveConfig",
    "classify_gait",
    "simulate_gait_regime",
    "simulate_descending_ramp",
    "run_descending_drive_sweep",
    "plot_panel_4a_tanh_gain_curves",
    "plot_panel_4b_descending_tract_maps",
    "plot_panel_4c_descending_ramp",
    "plot_panel_4d_gait_emg_patterns",
    "plot_panel_4e_polar_phase_transitions",
    "plot_panel_4fg_frequency_amplitude",
    "generate_figure4_complete"
]

