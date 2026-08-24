"""
Spinal Projectome Network Module
Defines Celltype, NetworkParameters, and Network classes for mouse spinal cord circuits.
Faithfully reproduces Komi et al., Nature Communications, 2026.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Union
from scipy.sparse.linalg import eigs
from data_loader import SpinalDataLoader
from connectivity import (
    compute_pairwise_distances,
    compute_directional_biases,
    compute_connection_probabilities,
    sample_connectivity_matrix,
    balance_connectivity,
    rescale_connectivity
)


class Celltype:
    """
    Defines the anatomical projection profile, length scale, and synaptic strength of a cell type.
    """
    def __init__(
        self,
        type_name: str,
        bias_rc: str = 'loc',
        bias_dv: str = 'loc',
        bias_ml: str = 'loc',
        bias_mn: str = '',
        bias_ci: str = 'ipsi',
        bias_layer: str = '',
        bias_seg: str = '',
        length_scale: float = 500.0,
        gain: float = 1.0,
        threshold: float = 5.0,
        f_max: float = 50.0,
        syn_strength: float = 1.0,
        pre_syn: str = ''
    ):
        self.type_name = type_name
        self.bias_rc = bias_rc
        self.bias_dv = bias_dv
        self.bias_ml = bias_ml
        self.bias_mn = bias_mn
        self.bias_ci = bias_ci
        self.bias_layer = bias_layer
        self.bias_seg = bias_seg
        self.length_scale = float(length_scale)
        self.gain = float(gain)
        self.threshold = float(threshold)
        self.f_max = float(f_max)
        self.syn_strength = float(syn_strength)
        self.pre_syn = pre_syn
        self.bias_pop: Dict[str, float] = {'All': 1.0}
        self.delays_pop: Dict[str, float] = {'All': 0.0}

    def set_bias_pop(self, target: str, value: float):
        self.bias_pop[target] = float(value)

    def set_delays_pop(self, target: str, value: float):
        self.delays_pop[target] = float(value)


class NetworkParameters:
    """
    Container for network cell types, population biases, and global synaptic gain.
    """
    def __init__(self, gc: float = 0.5):
        self.gc = gc
        self.celltypes: Dict[str, Celltype] = {}

    def add_celltype(
        self,
        celltype_or_name: Union[Celltype, str],
        bias_rc: str = 'loc',
        bias_dv: str = 'loc',
        bias_ml: str = 'loc',
        bias_mn: str = '',
        bias_ci: str = 'ipsi',
        bias_layer: str = '',
        bias_seg: str = '',
        length_scale: float = 500.0,
        gain: float = 1.0,
        threshold: float = 5.0,
        f_max: float = 50.0,
        syn_strength: float = 1.0,
        pre_syn: str = ''
    ):
        if isinstance(celltype_or_name, Celltype):
            ct = celltype_or_name
        else:
            ct = Celltype(
                type_name=celltype_or_name,
                bias_rc=bias_rc,
                bias_dv=bias_dv,
                bias_ml=bias_ml,
                bias_mn=bias_mn,
                bias_ci=bias_ci,
                bias_layer=bias_layer,
                bias_seg=bias_seg,
                length_scale=length_scale,
                gain=gain,
                threshold=threshold,
                f_max=f_max,
                syn_strength=syn_strength,
                pre_syn=pre_syn
            )
        self.celltypes[ct.type_name] = ct

    def set_cell_bias_pop(self, source: str, target: str, value: float):
        if source == 'All':
            for ct in self.celltypes.values():
                ct.set_bias_pop(target, value)
        elif source in self.celltypes:
            self.celltypes[source].set_bias_pop(target, value)

    @classmethod
    def create_ventral_circuit(cls, gc: float = 0.5) -> 'NetworkParameters':
        """Creates the canonical 9-population ventral locomotion network from InstantiateModel.m."""
        params = cls(gc=gc)
        params.add_celltype('V2a-2', bias_rc='bi', bias_dv='ven', bias_ml='lat', bias_ci='ipsi', length_scale=7000.0, syn_strength=gc * 1.0)
        params.add_celltype('V2a-1', bias_rc='cau', bias_dv='ven', bias_ml='med', bias_ci='ipsi', length_scale=500.0, syn_strength=gc * 1.0)
        params.add_celltype('V1', bias_rc='ro', bias_dv='ven', bias_ml='', bias_ci='ipsi', length_scale=2000.0, syn_strength=gc * 0.2)
        params.add_celltype('V2b', bias_rc='cau', bias_dv='ven', bias_ml='lat', bias_ci='ipsi', length_scale=4000.0, syn_strength=gc * 1.0)
        params.add_celltype('V0d', bias_rc='loc', bias_dv='ven', bias_ml='med', bias_ci='contra', length_scale=500.0, syn_strength=gc * 1.0)
        params.add_celltype('V0v', bias_rc='ro', bias_dv='loc', bias_ml='med', bias_ci='contra', length_scale=3400.0, syn_strength=gc * 1.0)
        params.add_celltype('dI6', bias_rc='cau', bias_dv='dor', bias_ml='med', bias_ci='contra', length_scale=5000.0, syn_strength=gc * 1.0)
        params.add_celltype('V3', bias_rc='cau', bias_dv='ven', bias_ml='lat', bias_ci='contra', length_scale=500.0, syn_strength=gc * 1.0)
        params.add_celltype('MN', bias_rc='loc', bias_dv='ven', bias_ml='lat', bias_ci='ipsi', length_scale=300.0, syn_strength=gc * 1.0)

        params.set_cell_bias_pop('MN', 'All', 0.1)
        return params


class Network:
    """
    Spinal neural network model instance.
    """
    def __init__(
        self,
        segments: List[str],
        density: float = 0.8,
        symmetry: bool = True,
        parameters: Optional[NetworkParameters] = None,
        balance: bool = True,
        projwidth: float = 500.0,
        rescale: bool = True,
        rng_seed: int = 42,
        data_loader: Optional[SpinalDataLoader] = None,
        compute_eigenspectrum: bool = True
    ):
        if parameters is None:
            parameters = NetworkParameters.create_ventral_circuit()
        if data_loader is None:
            data_loader = SpinalDataLoader()

        self.segments = segments
        self.density = density
        self.symmetry = symmetry
        self.parameters = parameters
        self.balance = balance
        self.projwidth = projwidth
        self.rescale = rescale
        self.rng_seed = rng_seed
        self.data_loader = data_loader

        self.rng = np.random.default_rng(rng_seed)

        self._instantiate_geometry_and_cells()
        self._instantiate_connectivity()
        
        self.eigenvalues = np.array([])
        self.eigenmodes = np.array([[]])
        if compute_eigenspectrum:
            self.compute_eigenmodes(k=20)

    def _instantiate_geometry_and_cells(self):
        geom_data = self.data_loader.load_geometry()
        seg_lengths = geom_data['segment_lengths_um']
        seg_names = geom_data['segment_names']

        included_mask = [s in self.segments for s in seg_names]
        tot_length_um = np.sum(seg_lengths[included_mask]) if any(included_mask) else 11000.0

        raw_cells = self.data_loader.sample_neuron_positions(
            density=self.density,
            length_um=tot_length_um,
            rng_seed=self.rng_seed
        )

        type_keys = list(self.parameters.celltypes.keys())

        mapped_neurons = []
        for _, row in raw_cells.iterrows():
            orig_type = row['cell_type']
            target_pop = None

            if orig_type in type_keys:
                target_pop = orig_type
            elif orig_type.startswith('Excit'):
                num = int(orig_type.split('-')[1])
                if num <= 10:
                    target_pop = 'V2a-1'
                elif num <= 20:
                    target_pop = 'V2a-2'
                elif num <= 30:
                    target_pop = 'V0v'
                else:
                    target_pop = 'V3'
            elif orig_type.startswith('Inhib'):
                num = int(orig_type.split('-')[1])
                if num <= 7:
                    target_pop = 'V1'
                elif num <= 14:
                    target_pop = 'V2b'
                elif num <= 20:
                    target_pop = 'V0d'
                else:
                    target_pop = 'dI6'
            elif orig_type.startswith('MN'):
                target_pop = 'MN'
            else:
                target_pop = 'V1'

            if target_pop in type_keys:
                ct = self.parameters.celltypes[target_pop]
                lat = 1.0 if row['x_um'] >= 0 else -1.0
                mapped_neurons.append({
                    'neuron_id': len(mapped_neurons),
                    'type': target_pop,
                    'transmitter': row['transmitter'],
                    'x_um': row['x_um'],
                    'y_um': row['y_um'],
                    'z_um': row['z_um'],
                    'latera': lat,
                    'syn_strength': ct.syn_strength,
                    'gain': ct.gain,
                    'threshold': ct.threshold,
                    'f_max': ct.f_max
                })

        self.neurons_df = pd.DataFrame(mapped_neurons)
        self.n_neurons = len(self.neurons_df)

        self.pos_x = np.asarray(self.neurons_df['x_um'].values, dtype=np.float64)
        self.pos_y = np.asarray(self.neurons_df['y_um'].values, dtype=np.float64)
        self.pos_z = np.asarray(self.neurons_df['z_um'].values, dtype=np.float64)
        self.latera = np.asarray(self.neurons_df['latera'].values, dtype=np.float64)
        self.types = np.asarray(self.neurons_df['type'].values, dtype=object)
        self.transmitters = np.asarray(self.neurons_df['transmitter'].values, dtype=object)
        self.syn_strengths = np.asarray(self.neurons_df['syn_strength'].values, dtype=np.float64)

    def _instantiate_connectivity(self):
        type_names = list(self.parameters.celltypes.keys())
        bias_rc = {k: v.bias_rc for k, v in self.parameters.celltypes.items()}
        bias_ml = {k: v.bias_ml for k, v in self.parameters.celltypes.items()}
        bias_dv = {k: v.bias_dv for k, v in self.parameters.celltypes.items()}
        bias_ci = {k: v.bias_ci for k, v in self.parameters.celltypes.items()}
        length_scales = {k: v.length_scale for k, v in self.parameters.celltypes.items()}

        d_rc, d_ml, d_dv, d_ci = compute_pairwise_distances(self.pos_x, self.pos_y, self.pos_z, self.latera)

        b_rc, b_ml, b_dv, b_ci = compute_directional_biases(
            d_rc, d_ml, d_dv, d_ci,
            self.types, type_names,
            bias_rc, bias_ml, bias_dv, bias_ci,
            length_scales, projwidth=self.projwidth, rng=self.rng
        )

        b_pop = np.ones((self.n_neurons, self.n_neurons), dtype=np.float64)
        for s_idx, s_type in enumerate(self.types):
            ct = self.parameters.celltypes.get(s_type)
            if ct is not None:
                for t_name, val in ct.bias_pop.items():
                    if t_name == 'All':
                        is_target = (self.types != s_type)
                        b_pop[is_target, s_idx] = val
                    else:
                        is_target = (self.types == t_name)
                        b_pop[is_target, s_idx] = val

        self.prob_mat = compute_connection_probabilities(
            b_rc, b_ml, b_dv, b_ci, b_pop=b_pop
        )

        self.conn_mat = sample_connectivity_matrix(
            self.prob_mat, self.transmitters, self.syn_strengths, var=0.1, rng=self.rng
        )

        if self.balance:
            self.conn_mat = balance_connectivity(self.conn_mat, latera=self.latera)

        if self.rescale:
            self.conn_mat, self.sparsity = rescale_connectivity(self.conn_mat, latera=self.latera)
        else:
            self.sparsity = np.count_nonzero(self.conn_mat == 0) / self.conn_mat.size

    def compute_eigenmodes(self, k: int = 20, full: bool = False):
        """Computes eigenvalues and leading eigenmodes using Arnoldi iteration or full decomposition."""
        if full or self.n_neurons <= 100:
            evals, evecs = np.linalg.eig(self.conn_mat)
        else:
            k = min(k, self.n_neurons - 2)
            try:
                evals, evecs = eigs(self.conn_mat, k=k, which='LR')
            except Exception:
                evals, evecs = np.linalg.eig(self.conn_mat)

        idx = np.argsort(np.real(evals))[::-1]
        self.eigenvalues = evals[idx]
        self.eigenmodes = evecs[:, idx]
        return self.eigenvalues, self.eigenmodes
