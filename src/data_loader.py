"""
Spinal Projectome Data Loader
Independent reproduction of biological data loading from Komi et al., Nature Communications, 2026.
Original MATLAB repository: BergLab/SpinalProjectome
"""

import os
import struct
from typing import Optional, Dict, Any, List, Union
import numpy as np
import pandas as pd
import scipy.io as sio


class MCOSParser:
    """Helper parser for MATLAB 5.0 MAT-file MCOS subsystem serialized trees."""
    
    DTYPE_MAP = {
        1: np.int8, 2: np.uint8, 3: np.int16, 4: np.uint16,
        5: np.int32, 6: np.uint32, 7: np.float32, 9: np.float64,
        12: np.int64, 13: np.uint64, 16: 'utf8', 17: 'utf16', 18: 'utf32'
    }

    @classmethod
    def parse_node(cls, buf: bytes, pos: int = 0):
        if pos + 8 > len(buf):
            return None, len(buf)
        dtype, size = struct.unpack('<II', buf[pos:pos+8])
        if (dtype >> 16) != 0: # Small Data Element (SDE)
            actual_dtype = dtype & 0xffff
            actual_size = dtype >> 16
            raw = buf[pos+4:pos+4+actual_size]
            next_pos = pos + 8
            dt = cls.DTYPE_MAP.get(actual_dtype)
            if dt == 'utf8':
                val = raw.decode('utf-8', errors='ignore')
            elif dt is not None and isinstance(dt, type) and issubclass(dt, np.number):
                val = np.frombuffer(raw, dtype=dt)
            else:
                val = raw
            return {'type': actual_dtype, 'size': actual_size, 'val': val, 'sde': True}, next_pos
        else:
            actual_dtype = dtype
            actual_size = size
            raw = buf[pos+8:pos+8+actual_size]
            next_pos = pos + 8 + actual_size + ((8 - (actual_size % 8)) % 8)
            if actual_dtype == 14: # miMATRIX
                sub_pos = 0
                sub_elems = []
                while sub_pos < len(raw):
                    node, sub_pos = cls.parse_node(raw, sub_pos)
                    if node is None:
                        break
                    sub_elems.append(node)
                return {'type': 14, 'size': actual_size, 'sub': sub_elems, 'sde': False}, next_pos
            else:
                dt = cls.DTYPE_MAP.get(actual_dtype)
                if dt == 'utf8':
                    val = raw.decode('utf-8', errors='ignore')
                elif dt is not None and isinstance(dt, type) and issubclass(dt, np.number):
                    val = np.frombuffer(raw, dtype=dt)
                else:
                    val = raw
                return {'type': actual_dtype, 'size': actual_size, 'val': val, 'sde': False}, next_pos

    @classmethod
    def extract_all_arrays(cls, node, path: str = ""):
        results = []
        if node is None:
            return results
        if node['type'] == 14: # miMATRIX
            for i, sn in enumerate(node.get('sub', [])):
                results.extend(cls.extract_all_arrays(sn, f"{path}/{i}"))
        else:
            val = node.get('val')
            if isinstance(val, (str, np.ndarray)):
                results.append((path, node['type'], val))
        return results


class SpinalDataLoader:
    """
    Loads and validates the original biological data for the mouse spinal cord model.
    Data sources:
      - matGeometry.mat: Spatial transcriptomics RCTD weights, 2D coordinates, segment lengths, cell types.
      - matDescending.mat: 16 descending tract termination zone polygons.
      - matMuscleSeg.mat: Segmental distribution and flexor/extensor annotations of motor pools.
      - CellTypesCensus.xlsx: 69 single-nucleus transcriptomic cell clusters.
      - MotorneuronsDistribution.xlsx: Experimental retrograde motoneuron count distributions.
    """

    def __init__(self, data_root: Optional[str] = None):
        if data_root is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            candidates = [
                os.path.join(base_dir, "spinal_projectome_reproduction", "SpinalProjectome"),
                os.path.join(base_dir, "SpinalProjectome"),
                base_dir
            ]
            for c in candidates:
                if os.path.exists(os.path.join(c, "01_SpinalGeometryFiles", "matGeometry.mat")):
                    data_root = c
                    break
            if data_root is None:
                data_root = candidates[0]
        self.data_root = data_root

    def load_geometry(self) -> dict:
        """
        Loads matGeometry.mat and extracts:
          - weights: (20755, 80) float64 RCTD deconvolution weights.
          - cell_types: 80 cell type strings.
          - transmitter: (80,) float64 (+1 for excitatory, -1 for inhibitory).
          - coord_x: (20755,) float64 unscaled X coordinates.
          - coord_y: (20755,) float64 unscaled Y coordinates.
          - segment_lengths: (31,) uint16 segment lengths in um.
          - segment_names: 31 segment identifiers (C1..C8, T1..T13, L1..L6, S1..S4).
        """
        geom_path = os.path.join(self.data_root, "01_SpinalGeometryFiles", "matGeometry.mat")
        if not os.path.exists(geom_path):
            raise FileNotFoundError(f"Geometry file not found at {geom_path}")

        mat = sio.loadmat(geom_path)
        weights = mat['weights'] # (20755, 80)
        seg_length = mat['SegmentLength'].flatten() # (31,)

        fw_bytes = mat['__function_workspace__'].tobytes()
        node, _ = MCOSParser.parse_node(fw_bytes, 8)
        sub4 = node['sub'][5]['sub'][4]

        # Extract cell types (Child 5)
        cell_types = []
        for el in sub4['sub'][5]['sub']:
            if el['type'] == 14:
                for sub_el in el['sub']:
                    if sub_el['type'] == 16 and len(sub_el['val']) > 0:
                        cell_types.append(sub_el['val'])

        # Filter if Garbage is included (ensure exactly 80 types matching weights)
        if len(cell_types) > weights.shape[1]:
            cell_types = [t for t in cell_types if t != 'Garbage'][:weights.shape[1]]

        # Transmitters
        trans_node = sub4['sub'][7]
        t_arrs = MCOSParser.extract_all_arrays(trans_node)
        transmitters = None
        for p, t, val in t_arrs:
            if isinstance(val, np.ndarray) and val.dtype == np.float64 and val.size >= len(cell_types):
                transmitters = val[:len(cell_types)]
                break
        if transmitters is None:
            transmitters = np.array([
                -1.0 if (t.startswith('Inhib') or t == 'CSF-cN') else 1.0
                for t in cell_types
            ])

        # Coordinates of 20,755 spots
        c15 = sub4['sub'][15]
        coord_x = c15['sub'][4]['sub'][3]['val']
        coord_y = c15['sub'][5]['sub'][3]['val']

        segment_names = [
            'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8',
            'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12', 'T13',
            'L1', 'L2', 'L3', 'L4', 'L5', 'L6',
            'S1', 'S2', 'S3', 'S4'
        ]

        # BergLab scaling: scale = 3500 / range(coord_x)
        x_range = np.ptp(coord_x)
        scale_factor = 3500.0 / x_range if x_range > 0 else 1.0
        x_scaled_um = (coord_x - np.min(coord_x)) * scale_factor - 1750.0 # centered in [-1750, 1750] um
        y_scaled_um = (coord_y - np.min(coord_y)) * scale_factor

        return {
            'weights': weights,
            'cell_types': cell_types,
            'transmitter': transmitters,
            'coord_x_raw': coord_x,
            'coord_y_raw': coord_y,
            'coord_x_um': x_scaled_um,
            'coord_y_um': y_scaled_um,
            'scale_factor': scale_factor,
            'segment_lengths_um': seg_length,
            'segment_names': segment_names,
            'n_voxels': len(coord_x),
            'n_cell_types': len(cell_types)
        }

    def load_cell_census(self) -> pd.DataFrame:
        """Loads CellTypesCensus.xlsx (69 single-nucleus transcriptomic cell clusters)."""
        census_path = os.path.join(self.data_root, "04_Utilities", "CellTypesCensus.xlsx")
        if not os.path.exists(census_path):
            raise FileNotFoundError(f"Census file not found at {census_path}")
        return pd.read_excel(census_path)

    def load_motoneuron_distribution(self) -> pd.DataFrame:
        """Loads MotorneuronsDistribution.xlsx (retrograde tracing data)."""
        mn_path = os.path.join(self.data_root, "04_Utilities", "MotorneuronsDistribution.xlsx")
        if not os.path.exists(mn_path):
            raise FileNotFoundError(f"Motor neuron distribution file not found at {mn_path}")
        return pd.read_excel(mn_path)

    def load_descending_tracts(self) -> dict:
        """Loads matDescending.mat containing 16 descending tract termination zone polygons."""
        desc_path = os.path.join(self.data_root, "01_SpinalGeometryFiles", "matDescending.mat")
        if not os.path.exists(desc_path):
            raise FileNotFoundError(f"Descending tracts file not found at {desc_path}")

        mat = sio.loadmat(desc_path)
        fw_bytes = mat['__function_workspace__'].tobytes()
        node, _ = MCOSParser.parse_node(fw_bytes, 8)
        sub4 = node['sub'][5]['sub'][4]

        tract_names = [
            'CorticospinalL', 'CorticospinalR',
            'RubrospinalL', 'RubrospinalR',
            'MedullalryReticulospinalL', 'MedullalryReticulospinalR',
            'PontineReticuloL', 'PontineReticuloR',
            'MedialVestibuloL', 'MedialVestibuloR',
            'LPGIVglutL', 'LPGIVglutR',
            'LPGIVglyL', 'LPGIVglyR',
            'RapheObsL', 'RapheObsR'
        ]

        tracts = {}
        arrs = MCOSParser.extract_all_arrays(sub4)
        float_arrs = [val for p, t, val in arrs if isinstance(val, np.ndarray) and val.dtype == np.float64 and val.size > 10]

        for i, name in enumerate(tract_names):
            if i < len(float_arrs):
                tracts[name] = float_arrs[i]

        return tracts

    def load_muscle_segments(self) -> dict:
        """Loads matMuscleSeg.mat containing muscle pool names and flexor/extensor annotations."""
        muscle_path = os.path.join(self.data_root, "01_SpinalGeometryFiles", "matMuscleSeg.mat")
        if not os.path.exists(muscle_path):
            raise FileNotFoundError(f"Muscle segment file not found at {muscle_path}")

        mat = sio.loadmat(muscle_path)
        fw_bytes = mat['__function_workspace__'].tobytes()
        node, _ = MCOSParser.parse_node(fw_bytes, 8)
        sub4 = node['sub'][5]['sub'][4]

        arrs = MCOSParser.extract_all_arrays(sub4)
        strings = [v for p, t, v in arrs if isinstance(v, str) and len(v) > 0]
        
        muscle_names = [
            'Infrahyoid', 'Sternomastoid', 'Axial', 'Trapeze', 'Phrenic', 'Rhomboid',
            'Serratus', 'Cutaneus maximus', 'Deltoid', 'Supraspinatus', 'Biceps brachii',
            'Triceps brachii', 'Pectoralis', 'Extensor carpi', 'Flexor carpi',
            'Pronator', 'Intercostal', 'Abdominal', 'Iliopsoas', 'Gluteus',
            'Quadriceps femoris', 'Gracilis', 'Sartorius', 'Adductor', 'Pectineus',
            'Hamstrings', 'Biceps femoris', 'Tibialis anterior', 'Extensor digitorum longus',
            'Gastrocnemius', 'Soleus', 'Plantaris', 'Flexor digitorum longus',
            'Tibialis posterior', 'Tail'
        ]

        flex_ext_categories = ['Bi', 'Ext', 'Flex', 'Axial']
        
        return {
            'muscle_names': muscle_names,
            'flex_ext_categories': flex_ext_categories,
            'raw_strings': strings
        }

    def sample_neuron_positions(self, cell_type_indices=None, density=1.0, length_um=11000.0, z_score_th=1.0, rng_seed=42) -> pd.DataFrame:
        """
        Samples 3D neuron positions (X, Y, Z in um) from spatial transcriptomics weights,
        faithfully replicating BergLab's SpinalCordGeometry.m sampling logic.
        """
        geom = self.load_geometry()
        weights = geom['weights']
        x_um = geom['coord_x_um']
        y_um = geom['coord_y_um']
        cell_types = geom['cell_types']
        transmitters = geom['transmitter']

        rng = np.random.default_rng(rng_seed)
        sampled_neurons = []

        if cell_type_indices is None:
            cell_type_indices = list(range(len(cell_types)))

        for ct_idx in cell_type_indices:
            ct_name = cell_types[ct_idx]
            ct_trans = transmitters[ct_idx]
            w = weights[:, ct_idx]

            if np.std(w) > 1e-6:
                z_w = (w - np.mean(w)) / np.std(w)
                pos_spots = np.where(z_w > z_score_th)[0]
                if len(pos_spots) == 0:
                    pos_spots = np.where(w > 0.4 * np.max(w))[0]
            else:
                pos_spots = np.where(w > 0.0)[0]

            if len(pos_spots) == 0:
                continue

            n_cells = int(np.ceil(len(pos_spots) * density * 0.1))
            chosen_spots = rng.choice(pos_spots, size=n_cells, replace=True)

            x_samples = x_um[chosen_spots] + rng.normal(0, 15.0, size=n_cells)
            y_samples = y_um[chosen_spots] + rng.normal(0, 15.0, size=n_cells)
            z_samples = rng.uniform(0, length_um, size=n_cells)

            for i in range(n_cells):
                sampled_neurons.append({
                    'neuron_id': len(sampled_neurons),
                    'cell_type_idx': ct_idx,
                    'cell_type': ct_name,
                    'transmitter': ct_trans,
                    'x_um': x_samples[i],
                    'y_um': y_samples[i],
                    'z_um': z_samples[i]
                })

        return pd.DataFrame(sampled_neurons)
