"""
Generate publication-quality diagnostic plots for biological data validation.
1. 3D neuron locations
2. Neuron locations separated by cell type
3. Cell-type counts
4. Spatial distribution along the spinal cord
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
from data_loader import SpinalDataLoader

def main():
    plots_dir = os.path.join(os.path.dirname(__file__), "plots")
    os.makedirs(plots_dir, exist_ok=True)
    
    loader = SpinalDataLoader()
    geom = loader.load_geometry()
    df_cells = loader.sample_neuron_positions(density=1.0, length_um=11000.0, rng_seed=42)
    
    # 1. Plot 3D Neuron Locations
    fig = plt.figure(figsize=(10, 8), dpi=300)
    ax = fig.add_subplot(111, projection='3d')
    
    # Excitatory (red/orange) and Inhibitory (blue/cyan)
    is_excit = df_cells['transmitter'] > 0
    ax.scatter(df_cells.loc[is_excit, 'x_um'],
               df_cells.loc[is_excit, 'z_um'],
               df_cells.loc[is_excit, 'y_um'],
               c='#d95f02', s=4, alpha=0.6, label='Excitatory / MN')
    ax.scatter(df_cells.loc[~is_excit, 'x_um'],
               df_cells.loc[~is_excit, 'z_um'],
               df_cells.loc[~is_excit, 'y_um'],
               c='#7570b3', s=4, alpha=0.6, label='Inhibitory / CSF-cN')
    
    ax.set_xlabel('Mediolateral (µm)', fontsize=11, labelpad=8)
    ax.set_ylabel('Rostrocaudal (µm)', fontsize=11, labelpad=8)
    ax.set_zlabel('Dorsoventral (µm)', fontsize=11, labelpad=8)
    ax.set_title('Mouse Spinal Cord Model: 3D Neuron Locations (N = 6,528)', fontsize=13, fontweight='bold', pad=15)
    ax.legend(loc='upper right', frameon=True)
    ax.view_init(elev=20, azim=45)
    plt.tight_layout()
    p1 = os.path.join(plots_dir, "01_3d_neuron_locations.png")
    fig.savefig(p1)
    plt.close(fig)
    print(f"Saved: {p1}")

    # 2. Neuron Locations Separated by Cell Type (Representative ventral & motor populations)
    fig, axes = plt.subplots(2, 3, figsize=(14, 9), dpi=300)
    axes = axes.flatten()
    
    selected_types = ['MN-alpha', 'MN-gamma', 'Excit-01', 'Excit-20', 'Inhib-01', 'Inhib-15']
    colors = ['#e41a1c', '#ff7f00', '#4daf4a', '#377eb8', '#984ea3', '#a65628']
    
    for i, (ctype, color) in enumerate(zip(selected_types, colors)):
        sub = df_cells[df_cells['cell_type'] == ctype]
        ax = axes[i]
        # Background outline (all spots)
        ax.scatter(geom['coord_x_um'], geom['coord_y_um'], c='#e0e0e0', s=1, alpha=0.3, label='Spinal Cord')
        if len(sub) > 0:
            ax.scatter(sub['x_um'], sub['y_um'], c=color, s=15, alpha=0.8, edgecolors='none', label=f'{ctype} (n={len(sub)})')
        ax.set_xlim([-1850, 1850])
        ax.set_ylim([-50, 1750])
        ax.set_title(f'Cell Type: {ctype}', fontsize=12, fontweight='bold')
        ax.set_xlabel('Mediolateral (µm)', fontsize=10)
        ax.set_ylabel('Dorsoventral (µm)', fontsize=10)
        ax.legend(loc='upper right', frameon=True, fontsize=9)
        ax.grid(True, linestyle=':', alpha=0.4)
    
    plt.suptitle('Transverse Spinal Cord Cross-Sections by Cell Type', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout()
    p2 = os.path.join(plots_dir, "02_neuron_locations_by_celltype.png")
    fig.savefig(p2)
    plt.close(fig)
    print(f"Saved: {p2}")

    # 3. Cell-Type Counts Bar Chart
    fig, ax = plt.subplots(figsize=(16, 6), dpi=300)
    counts = df_cells['cell_type'].value_counts()
    types_order = [t for t in geom['cell_types'] if t in counts.index]
    sorted_counts = [counts[t] for t in types_order]
    bar_colors = ['#d95f02' if geom['transmitter'][geom['cell_types'].index(t)] > 0 else '#7570b3' for t in types_order]
    
    bars = ax.bar(types_order, sorted_counts, color=bar_colors, edgecolor='black', linewidth=0.5)
    ax.set_xticklabels(types_order, rotation=90, fontsize=8)
    ax.set_ylabel('Sampled Neuron Count', fontsize=11)
    ax.set_title('Sampled Neuron Counts across 80 Biological Cell Types (Total N = 6,528)', fontsize=13, fontweight='bold')
    
    # Custom legend for Excitatory vs Inhibitory
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#d95f02', edgecolor='black', label='Excitatory / Cholinergic (NT = +1)'),
        Patch(facecolor='#7570b3', edgecolor='black', label='Inhibitory / GABA-Glycine (NT = -1)')
    ]
    ax.legend(handles=legend_elements, loc='upper right', frameon=True)
    ax.grid(axis='y', linestyle=':', alpha=0.5)
    plt.tight_layout()
    p3 = os.path.join(plots_dir, "03_cell_type_counts.png")
    fig.savefig(p3)
    plt.close(fig)
    print(f"Saved: {p3}")

    # 4. Spatial Distribution along Spinal Cord (Rostrocaudal axis)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), dpi=300, sharex=True)
    
    # Density histogram along Rostrocaudal (Z) axis
    z_excit = df_cells.loc[is_excit, 'z_um']
    z_inhib = df_cells.loc[~is_excit, 'z_um']
    
    bins = np.linspace(0, 11000, 50)
    ax1.hist([z_excit, z_inhib], bins=bins, stacked=True, color=['#d95f02', '#7570b3'],
             label=['Excitatory Neurons', 'Inhibitory Neurons'], edgecolor='black', linewidth=0.5)
    ax1.set_ylabel('Neuron Count per Bin', fontsize=11)
    ax1.set_title('Rostrocaudal Distribution of Sampled Neurons (0 to 11,000 µm)', fontsize=12, fontweight='bold')
    ax1.legend(loc='upper right', frameon=True)
    ax1.grid(True, linestyle=':', alpha=0.4)
    
    # Add Segment markers
    seg_names = ['T13', 'L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'S1']
    seg_lens = [1300, 1200, 1500, 1500, 1300, 1200, 1400, 1400]
    cum_lens = np.cumsum([0] + seg_lens)
    
    for s_name, s_start, s_end in zip(seg_names, cum_lens[:-1], cum_lens[1:]):
        ax1.axvline(s_end, color='gray', linestyle='--', alpha=0.6)
        mid = (s_start + min(s_end, 11000)) / 2.0
        if mid < 11000:
            ax1.text(mid, ax1.get_ylim()[1]*0.85, s_name, ha='center', fontsize=9, fontweight='bold', color='#333333')

    # Motoneuron specific distribution along Rostrocaudal axis
    mn_alpha = df_cells[df_cells['cell_type'] == 'MN-alpha']['z_um']
    mn_gamma = df_cells[df_cells['cell_type'] == 'MN-gamma']['z_um']
    ax2.hist([mn_alpha, mn_gamma], bins=bins, stacked=True, color=['#e41a1c', '#ff7f00'],
             label=['MN-alpha', 'MN-gamma'], edgecolor='black', linewidth=0.5)
    ax2.set_xlabel('Rostrocaudal Position (µm)', fontsize=11)
    ax2.set_ylabel('Motoneuron Count', fontsize=11)
    ax2.set_title('Motoneuron Pool Distribution along Lumbar Spinal Cord', fontsize=12, fontweight='bold')
    ax2.legend(loc='upper right', frameon=True)
    ax2.grid(True, linestyle=':', alpha=0.4)
    
    for s_end in cum_lens[1:]:
        if s_end <= 11000:
            ax2.axvline(s_end, color='gray', linestyle='--', alpha=0.6)

    plt.tight_layout()
    p4 = os.path.join(plots_dir, "04_spatial_distribution_rostrocaudal.png")
    fig.savefig(p4)
    plt.close(fig)
    print(f"Saved: {p4}")

if __name__ == "__main__":
    main()
