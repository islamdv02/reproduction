"""
Generate publication-quality diagnostic plots for Step 2 Network Construction.
1. 3D neuron locations
2. Connectivity matrix
3. Connection probability vs spatial distance
4. Excitatory connectivity
5. Inhibitory connectivity
6. Asymmetric Mexican-hat profile
"""

import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from network import Network, NetworkParameters

def main():
    plots_dir = os.path.join(os.path.dirname(__file__), "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    print("Building standard locomotion network...")
    segments = ['T13', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'S1', 'S2', 'S3', 'S4']
    net = Network(segments=segments, density=0.8, symmetry=True, balance=True, rescale=True, rng_seed=42, compute_eigenspectrum=False)
    print(f"Network instantiated with N = {net.n_neurons} neurons.")

    # 1. 3D Neuron Locations
    fig = plt.figure(figsize=(10, 8), dpi=300)
    ax = fig.add_subplot(111, projection='3d')
    
    unique_types = list(net.parameters.celltypes.keys())
    type_colors = {
        'V2a-1': '#e41a1c', 'V2a-2': '#ff7f00', 'V1': '#377eb8',
        'V2b': '#984ea3', 'V0d': '#4daf4a', 'V0v': '#a65628',
        'dI6': '#f781bf', 'V3': '#999999', 'MN': '#1b9e77'
    }
    
    for t_name in unique_types:
        idx = (net.types == t_name)
        if np.any(idx):
            ax.scatter(net.pos_x[idx], net.pos_z[idx], net.pos_y[idx],
                       c=type_colors.get(t_name, '#333333'), s=6, alpha=0.7, label=f"{t_name} (n={np.sum(idx)})")
            
    ax.set_xlabel('Mediolateral (µm)', fontsize=11, labelpad=8)
    ax.set_ylabel('Rostrocaudal (µm)', fontsize=11, labelpad=8)
    ax.set_zlabel('Dorsoventral (µm)', fontsize=11, labelpad=8)
    ax.set_title(f'Mouse Spinal Network 3D Architecture (N = {net.n_neurons})', fontsize=13, fontweight='bold', pad=15)
    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.0), fontsize=9, frameon=True)
    ax.view_init(elev=22, azim=45)
    plt.tight_layout()
    p1 = os.path.join(plots_dir, "05_network_neuron_locations.png")
    fig.savefig(p1, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {p1}")

    # 2. Connectivity Matrix Heatmap
    fig, ax = plt.subplots(figsize=(9, 8), dpi=300)
    # Sort neurons by type for visual clarity
    sort_idx = np.argsort(net.types)
    W_sorted = net.conn_mat[sort_idx, :][:, sort_idx]
    
    vmax = np.percentile(np.abs(W_sorted[W_sorted != 0]), 99) if np.any(W_sorted != 0) else 1.0
    im = ax.imshow(W_sorted, cmap='coolwarm', vmin=-vmax, vmax=vmax, aspect='auto')
    plt.colorbar(im, ax=ax, label='Synaptic Weight (Rescaled)', fraction=0.046, pad=0.04)
    ax.set_title(f'Full Synaptic Connectivity Matrix ({net.n_neurons} × {net.n_neurons})\nSparsity = {net.sparsity*100:.1f}%', fontsize=12, fontweight='bold')
    ax.set_xlabel('Presynaptic Neuron Index (Sorted by Type)', fontsize=11)
    ax.set_ylabel('Postsynaptic Neuron Index (Sorted by Type)', fontsize=11)
    
    # Add population division lines
    types_sorted = net.types[sort_idx]
    unique_pops, pop_indices = np.unique(types_sorted, return_index=True)
    for p_idx in pop_indices:
        if p_idx > 0:
            ax.axvline(p_idx, color='black', linewidth=0.5, linestyle=':')
            ax.axhline(p_idx, color='black', linewidth=0.5, linestyle=':')
            
    plt.tight_layout()
    p2 = os.path.join(plots_dir, "06_connectivity_matrix.png")
    fig.savefig(p2)
    plt.close(fig)
    print(f"Saved: {p2}")

    # 3. Connection Probability vs. Spatial Distance
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    # Sample 100,000 random pairs to compute empirical connection probability
    rng = np.random.default_rng(42)
    sample_size = min(150000, net.n_neurons * 50)
    i_sample = rng.integers(0, net.n_neurons, size=sample_size)
    j_sample = rng.integers(0, net.n_neurons, size=sample_size)
    valid = (i_sample != j_sample)
    i_sample, j_sample = i_sample[valid], j_sample[valid]
    
    dx = net.pos_x[i_sample] - net.pos_x[j_sample]
    dy = net.pos_y[i_sample] - net.pos_y[j_sample]
    dz = net.pos_z[i_sample] - net.pos_z[j_sample]
    dist_3d = np.sqrt(dx**2 + dy**2 + dz**2)
    connected = (net.conn_mat[i_sample, j_sample] != 0).astype(float)
    
    # Bin distances
    bin_edges = np.linspace(0, 10000, 40)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0
    bin_indices = np.digitize(dist_3d, bin_edges) - 1
    
    emp_prob = []
    for b in range(len(bin_centers)):
        in_bin = (bin_indices == b)
        if np.sum(in_bin) > 20:
            emp_prob.append(np.mean(connected[in_bin]))
        else:
            emp_prob.append(np.nan)
            
    ax.plot(bin_centers, emp_prob, 'o-', color='#1f77b4', linewidth=2, markersize=5, label='Empirical Network Connectivity')
    ax.set_xlabel('3D Euclidean Distance (µm)', fontsize=11)
    ax.set_ylabel('Connection Probability P(d)', fontsize=11)
    ax.set_title('Synaptic Connection Probability vs. 3D Inter-Neuron Distance', fontsize=12, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.legend(loc='upper right', frameon=True)
    plt.tight_layout()
    p3 = os.path.join(plots_dir, "07_connection_prob_vs_distance.png")
    fig.savefig(p3)
    plt.close(fig)
    print(f"Saved: {p3}")

    # 4. Excitatory Connectivity Subnetwork
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    is_excit = (net.transmitters > 0)
    W_excit = net.conn_mat[:, is_excit]
    
    im1 = ax1.imshow(W_excit, cmap='Reds', aspect='auto', vmin=0, vmax=np.percentile(W_excit[W_excit > 0], 98) if np.any(W_excit > 0) else 1.0)
    plt.colorbar(im1, ax=ax1, label='Excitatory Synaptic Weight', fraction=0.046, pad=0.04)
    ax1.set_title(f'Excitatory Synapses (N_source = {np.sum(is_excit)})', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Presynaptic Excitatory Neurons', fontsize=10)
    ax1.set_ylabel('Postsynaptic Target Neurons', fontsize=10)
    
    # Excitatory weight distribution
    exc_weights = W_excit[W_excit > 0]
    ax2.hist(exc_weights, bins=40, color='#d95f02', edgecolor='black', linewidth=0.5, alpha=0.8)
    ax2.set_xlabel('Synaptic Weight', fontsize=10)
    ax2.set_ylabel('Synapse Count', fontsize=10)
    ax2.set_title(f'Excitatory Weight Distribution (Total = {len(exc_weights):,})', fontsize=11, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.4)
    
    plt.tight_layout()
    p4 = os.path.join(plots_dir, "08_excitatory_connectivity.png")
    fig.savefig(p4)
    plt.close(fig)
    print(f"Saved: {p4}")

    # 5. Inhibitory Connectivity Subnetwork
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)
    is_inhib = (net.transmitters < 0)
    W_inhib = net.conn_mat[:, is_inhib]
    
    im1 = ax1.imshow(np.abs(W_inhib), cmap='Blues', aspect='auto', vmin=0, vmax=np.percentile(np.abs(W_inhib[W_inhib < 0]), 98) if np.any(W_inhib < 0) else 1.0)
    plt.colorbar(im1, ax=ax1, label='Inhibitory Synaptic Weight (Magnitude)', fraction=0.046, pad=0.04)
    ax1.set_title(f'Inhibitory Synapses (N_source = {np.sum(is_inhib)})', fontsize=11, fontweight='bold')
    ax1.set_xlabel('Presynaptic Inhibitory Neurons', fontsize=10)
    ax1.set_ylabel('Postsynaptic Target Neurons', fontsize=10)
    
    # Inhibitory weight distribution
    inh_weights = np.abs(W_inhib[W_inhib < 0])
    ax2.hist(inh_weights, bins=40, color='#7570b3', edgecolor='black', linewidth=0.5, alpha=0.8)
    ax2.set_xlabel('Synaptic Weight Magnitude', fontsize=10)
    ax2.set_ylabel('Synapse Count', fontsize=10)
    ax2.set_title(f'Inhibitory Weight Distribution (Total = {len(inh_weights):,})', fontsize=11, fontweight='bold')
    ax2.grid(True, linestyle=':', alpha=0.4)
    
    plt.tight_layout()
    p5 = os.path.join(plots_dir, "09_inhibitory_connectivity.png")
    fig.savefig(p5)
    plt.close(fig)
    print(f"Saved: {p5}")

    # 6. Asymmetric Mexican-Hat Spatial Interaction Profile
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    # Compute net synaptic weight as a function of Rostrocaudal distance (Z_target - Z_source)
    dz_all = net.pos_z[i_sample] - net.pos_z[j_sample] # dz > 0: target is caudal; dz < 0: target is rostral
    weights_sample = net.conn_mat[i_sample, j_sample]
    
    rc_bins = np.linspace(-6000, 6000, 60)
    rc_centers = (rc_bins[:-1] + rc_bins[1:]) / 2.0
    rc_indices = np.digitize(dz_all, rc_bins) - 1
    
    mean_weights = []
    mean_exc = []
    mean_inh = []
    
    for b in range(len(rc_centers)):
        in_bin = (rc_indices == b)
        if np.sum(in_bin) > 50:
            w_bin = weights_sample[in_bin]
            mean_weights.append(np.mean(w_bin))
            mean_exc.append(np.mean(np.maximum(w_bin, 0.0)))
            mean_inh.append(np.mean(np.minimum(w_bin, 0.0)))
        else:
            mean_weights.append(np.nan)
            mean_exc.append(np.nan)
            mean_inh.append(np.nan)
            
    ax.axhline(0, color='black', linestyle='--', linewidth=0.8)
    ax.axvline(0, color='gray', linestyle=':', linewidth=0.8)
    
    ax.plot(rc_centers, mean_exc, color='#d95f02', linestyle='--', label='Excitatory Projection Kernel')
    ax.plot(rc_centers, mean_inh, color='#7570b3', linestyle='--', label='Inhibitory Projection Kernel')
    ax.plot(rc_centers, mean_weights, color='#111111', linewidth=2.5, label='Net Interaction Kernel ΔW(ΔZ) (Mexican-Hat)')
    
    ax.fill_between(rc_centers, 0, mean_weights, where=(np.array(mean_weights) > 0), color='#d95f02', alpha=0.25, label='Net Excitation (Local)')
    ax.fill_between(rc_centers, 0, mean_weights, where=(np.array(mean_weights) < 0), color='#7570b3', alpha=0.25, label='Net Inhibition (Surround)')
    
    ax.set_xlabel('Rostrocaudal Distance ΔZ = Z_target - Z_source (µm)\n(← Rostral Projection | Caudal Projection →)', fontsize=11)
    ax.set_ylabel('Average Effective Synaptic Weight', fontsize=11)
    ax.set_title('Asymmetric Mexican-Hat Spatial Connectivity Profile along Spinal Cord', fontsize=12, fontweight='bold')
    ax.grid(True, linestyle=':', alpha=0.4)
    ax.legend(loc='lower right', frameon=True)
    
    plt.tight_layout()
    p6 = os.path.join(plots_dir, "10_asymmetric_mexican_hat_profile.png")
    fig.savefig(p6)
    plt.close(fig)
    print(f"Saved: {p6}")

if __name__ == "__main__":
    main()
