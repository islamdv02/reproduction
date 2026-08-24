"""
Baseline Simulation Runner and Diagnostic Visualizer for Step 3.
Runs standard baseline locomotion simulation (t_steps=10000, I_e=30, tau_V=50 ms, seed=5)
and generates 5 publication-quality diagnostic plots:
1. Network activity vs time
2. Population activity vs time
3. Population activity comparison heatmap
4. Spatiotemporal activity raster (rostrocaudal space vs time)
5. Power spectrum and frequency analysis
"""

import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from network import Network, NetworkParameters
from dynamics import compute_spectral_analysis
from simulation import SimulationConfig, Simulator, SimulationResult

def main():
    plots_dir = os.path.join(os.path.dirname(__file__), "plots")
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(plots_dir, exist_ok=True)
    os.makedirs(results_dir, exist_ok=True)

    print("=" * 60)
    print("1. Instantiating spinal projectome network (T13-S4)...")
    segments = ['T13', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'S1', 'S2', 'S3', 'S4']
    net = Network(segments=segments, density=0.8, symmetry=True, balance=True, rescale=True, rng_seed=42, compute_eigenspectrum=False)
    print(f"Network created with N = {net.n_neurons} neurons.")

    print("\n2. Executing baseline neural dynamics simulation...")
    # Baseline simulation parameters matching InstantiateModel.m lines 31-34
    cfg = SimulationConfig(
        t_steps=10000,
        dt_ms=1.0,
        tau_V_ms=50.0,
        I_e=30.0,
        noise_ampl=0.5,
        V_init_mean=-70.0,
        V_init_std=3.0,
        seed=5,
        adaptation=False
    )
    sim = Simulator(cfg)
    result = sim.run(net, verbose=True)
    
    # Save checkpoint
    result.save_checkpoint(results_dir, prefix="baseline_simulation")
    print(f"Simulation saved to {results_dir}/baseline_simulation_results.npz")
    
    # Spectral metrics
    spec = result.spectral_analysis
    dom_freq = spec.get('dominant_frequency_hz', 0.0)
    peak_pow = spec.get('peak_power', 0.0)
    amp = spec.get('amplitude_hz', 0.0)
    mean_r = spec.get('mean_rate_hz', 0.0)
    std_r = spec.get('std_rate_hz', 0.0)
    
    print(f"\n--- Simulation Dynamics Results ---")
    print(f"Dominant Oscillation Frequency : {dom_freq:.2f} Hz")
    print(f"Peak Power Spectral Density   : {peak_pow:.4e}")
    print(f"Oscillation Amplitude (PTP)   : {amp:.2f} Hz")
    print(f"Mean Population Rate          : {mean_r:.2f} ± {std_r:.2f} Hz")
    print("=" * 60)

    # 1. Network Activity vs Time (First 2000 ms zoom + overview)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), dpi=300, sharex=False)
    
    # Population mean rate
    mean_net_rate = np.mean(result.rates, axis=1)
    
    ax1.plot(result.time_ms / 1000.0, mean_net_rate, color='#111111', linewidth=1.2, label='Mean Network Firing Rate')
    ax1.set_ylabel('Firing Rate (Hz)', fontsize=10)
    ax1.set_title(f'Global Network Firing Rate across Full Duration (T = 10 s, N = {net.n_neurons})', fontsize=11, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.5)
    ax1.set_xlabel('Time (s)', fontsize=10)
    ax1.legend(loc='upper right', frameon=True)
    
    # Zoom-in on 1000 - 3000 ms to inspect rhythmicity
    t_zoom = (result.time_ms >= 1000) & (result.time_ms <= 3000)
    ax2.plot(result.time_ms[t_zoom], mean_net_rate[t_zoom], color='#e41a1c', linewidth=1.5, label='Mean Rate')
    
    # Sample 5 individual neurons
    rng_sample = np.random.default_rng(100)
    sample_neurons = rng_sample.choice(net.n_neurons, size=5, replace=False)
    for n_id in sample_neurons:
        t_type = net.types[n_id]
        ax2.plot(result.time_ms[t_zoom], result.rates[t_zoom, n_id], alpha=0.4, linewidth=0.8, label=f'Neuron {n_id} ({t_type})')
        
    ax2.set_ylabel('Firing Rate (Hz)', fontsize=10)
    ax2.set_xlabel('Time (ms)', fontsize=10)
    ax2.set_title('Rhythmic Activity Microstructure (Zoom: 1000 – 3000 ms)', fontsize=11, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.5)
    ax2.legend(loc='upper right', fontsize=8, ncol=2, frameon=True)
    
    plt.tight_layout()
    p1 = os.path.join(plots_dir, "11_network_activity_vs_time.png")
    fig.savefig(p1)
    plt.close(fig)
    print(f"Saved: {p1}")

    # 2. Population Activity vs Time (Multi-trace overlay)
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    
    type_colors = {
        'V2a-1': '#e41a1c', 'V2a-2': '#ff7f00', 'V1': '#377eb8',
        'V2b': '#984ea3', 'V0d': '#4daf4a', 'V0v': '#a65628',
        'dI6': '#f781bf', 'V3': '#666666', 'MN': '#1b9e77'
    }
    
    t_plot_mask = (result.time_ms >= 1000) & (result.time_ms <= 3000)
    t_plot = result.time_ms[t_plot_mask]
    
    for pop_name, pop_rate in result.population_rates.items():
        color = type_colors.get(pop_name, '#333333')
        ax.plot(t_plot, pop_rate[t_plot_mask], label=pop_name, color=color, linewidth=1.5)
        
    ax.set_xlabel('Time (ms)', fontsize=11)
    ax.set_ylabel('Population Firing Rate (Hz)', fontsize=11)
    ax.set_title('Population-Specific Firing Rates During Locomotion (1000 – 3000 ms)', fontsize=12, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.legend(loc='upper right', ncol=3, frameon=True, fontsize=9)
    
    plt.tight_layout()
    p2 = os.path.join(plots_dir, "12_population_activity_vs_time.png")
    fig.savefig(p2)
    plt.close(fig)
    print(f"Saved: {p2}")

    # 3. Population Activity Comparison Heatmap
    fig, ax = plt.subplots(figsize=(11, 6), dpi=300)
    pop_keys = list(result.population_rates.keys())
    pop_matrix = np.array([result.population_rates[k][t_plot_mask] for k in pop_keys])
    
    im = ax.imshow(pop_matrix, aspect='auto', cmap='magma', extent=[t_plot[0], t_plot[-1], len(pop_keys)-0.5, -0.5])
    plt.colorbar(im, ax=ax, label='Firing Rate (Hz)', fraction=0.046, pad=0.04)
    ax.set_yticks(range(len(pop_keys)))
    ax.set_yticklabels(pop_keys, fontsize=10, fontweight='bold')
    ax.set_xlabel('Time (ms)', fontsize=11)
    ax.set_title('Spatiotemporal Population Dynamics (Phase Relationships)', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    p3 = os.path.join(plots_dir, "13_population_activity_heatmap.png")
    fig.savefig(p3)
    plt.close(fig)
    print(f"Saved: {p3}")

    # 4. Spatiotemporal Activity Raster (Rostrocaudal Space vs. Time)
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    
    # Sort all neurons by Rostrocaudal position Z
    z_sort = np.argsort(net.pos_z)
    rates_sorted_z = result.rates[t_plot_mask, :][:, z_sort].T # Shape: (N, T_plot)
    
    im = ax.imshow(rates_sorted_z, aspect='auto', cmap='viridis', origin='lower',
                   extent=[t_plot[0], t_plot[-1], net.pos_z[z_sort][0], net.pos_z[z_sort][-1]])
    plt.colorbar(im, ax=ax, label='Neuron Firing Rate (Hz)', fraction=0.046, pad=0.04)
    ax.set_xlabel('Time (ms)', fontsize=11)
    ax.set_ylabel('Rostrocaudal Position Z (µm)\n(← Rostral T13 | Caudal S4 →)', fontsize=11)
    ax.set_title('Spatiotemporal Activity Map along Rostrocaudal Spinal Cord Axis', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    p4 = os.path.join(plots_dir, "14_spatiotemporal_activity_raster.png")
    fig.savefig(p4)
    plt.close(fig)
    print(f"Saved: {p4}")

    # 5. Power Spectrum and Frequency Analysis
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
    
    freqs = spec.get('frequencies', np.array([]))
    psd = spec.get('psd', np.array([]))
    
    # Power spectral density in biological range (0 - 20 Hz)
    band_mask = (freqs >= 0.5) & (freqs <= 20.0)
    ax1.plot(freqs[band_mask], psd[band_mask], color='#1f77b4', linewidth=2.0, label='Global Population PSD')
    if dom_freq > 0:
        ax1.axvline(dom_freq, color='#e41a1c', linestyle='--', linewidth=1.5, label=f'Peak Frequency = {dom_freq:.2f} Hz')
    ax1.set_xlabel('Frequency (Hz)', fontsize=11)
    ax1.set_ylabel('Power Spectral Density (Hz²/Hz)', fontsize=11)
    ax1.set_title('Power Spectrum (Welch PSD, 0.5–20 Hz)', fontsize=11, fontweight='bold')
    ax1.grid(True, linestyle=':', alpha=0.5)
    ax1.legend(loc='upper right', frameon=True)
    
    # Population-specific dominant frequencies
    pop_freqs = {}
    for pop_name, p_rate in result.population_rates.items():
        p_spec = compute_spectral_analysis(p_rate, dt=0.001, t_start_ms=1000)
        pop_freqs[pop_name] = p_spec.get('dominant_frequency_hz', 0.0)
        
    pop_names_list = list(pop_freqs.keys())
    pop_freq_vals = [pop_freqs[k] for k in pop_names_list]
    colors_bar = [type_colors.get(k, '#333333') for k in pop_names_list]
    
    bars = ax2.bar(pop_names_list, pop_freq_vals, color=colors_bar, edgecolor='black', linewidth=0.8, alpha=0.85)
    ax2.set_ylabel('Dominant Oscillation Frequency (Hz)', fontsize=11)
    ax2.set_title('Dominant Oscillation Frequency by Cell Type', fontsize=11, fontweight='bold')
    ax2.grid(True, linestyle=':', axis='y', alpha=0.5)
    ax2.set_ylim(0, max(pop_freq_vals + [8.0]) * 1.2)
    
    for bar, val in zip(bars, pop_freq_vals):
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 0.15, f'{val:.2f}', ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    plt.tight_layout()
    p5 = os.path.join(plots_dir, "15_power_spectrum_frequency_analysis.png")
    fig.savefig(p5)
    plt.close(fig)
    print(f"Saved: {p5}")

if __name__ == "__main__":
    main()
