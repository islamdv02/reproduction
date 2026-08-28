"""
Spatial Mapping Module: Embedding Yakovenko et al. (2002) 30-Slice Anatomy into 3D Continuous Geometry.
Generates 3D coordinates (X, Y, Z) and assigns functional neuronal populations (E, I, Commissural, Motoneuron).
"""

from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd

# 27 Cat Hindlimb Muscle Names from Yakovenko et al. (2002)
MUSCLE_NAMES = [
    'Psoas', 'Iliacus', 'SRTa', 'SRTm', 'RF', 'VL', 'VM', 'VI',
    'TA', 'EDL', 'AdFM', 'Gracilis', 'SMa', 'GlutMed', 'CF', 'BFa', 'GlutMax',
    'BFp', 'ST', 'SMp', 'FDL', 'FHL', 'Plantaris', 'Soleus', 'LG', 'MG', 'TP'
]

# Population classifications
POPULATION_CLASSES = [
    'RFlex_E',    # Rostral Flexor Excitatory Interneurons (L4-L6)
    'RFlex_I',    # Rostral Flexor Inhibitory Interneurons (L4-L6)
    'CExt_E',     # Caudal Extensor Excitatory Interneurons (L6-L7)
    'CExt_I',     # Caudal Extensor Inhibitory Interneurons (L6-L7)
    'CRet_E',     # Caudal Retractor Excitatory Interneurons (L7-S1)
    'CRet_I',     # Caudal Retractor Inhibitory Interneurons (L7-S1)
    'Comm_Contra',# Contralaterally Projecting Commissural Interneurons
    'MN_Pool'     # Motoneuron Output Pools
]


class YakovenkoKomiSpatialNetwork:
    """
    3D Spatial Network Model embedding Yakovenko cat lumbosacral anatomy into continuous coordinates.
    Length: 28.8 mm (L4 to S1, 30 slices). Width: +/-3.6 mm. Height: 5.5 mm.
    """

    def __init__(self, n_neurons: int = 1200, rng_seed: int = 42):
        self.n_neurons = int(n_neurons)
        self.rng = np.random.default_rng(rng_seed)
        self.length_mm = 28.8
        self.width_mm = 3.6
        self.height_mm = 5.5
        self.n_slices = 30
        self.slice_thickness = self.length_mm / self.n_slices # 0.96 mm

        self._generate_spatial_embedding()

    def _generate_spatial_embedding(self):
        """Generates continuous 3D coordinates (X, Y, Z), hemicord assignments, and functional cell types."""
        # Split neurons: 50% left hemicord, 50% right hemicord
        n_half = self.n_neurons // 2
        
        # 1. Longitudinal Coordinates (Z in [0, 28.8] mm)
        # Sample Z reflecting the 33% rostral / 67% caudal anatomical distribution of Table 1
        z_rostral = self.rng.uniform(0.0, 14.4, int(self.n_neurons * 0.33))
        z_caudal = self.rng.uniform(14.4, 28.8, self.n_neurons - len(z_rostral))
        self.z = np.concatenate([z_rostral, z_caudal])
        self.rng.shuffle(self.z)

        # 2. Mediolateral Coordinates (X in [-3.6, 3.6] mm)
        # Ventral horn positioned ~1.8 mm from midline
        x_left = self.rng.normal(-1.8, 0.45, n_half)
        x_right = self.rng.normal(1.8, 0.45, self.n_neurons - n_half)
        self.x = np.concatenate([x_left, x_right])
        self.rng.shuffle(self.x)

        # 3. Dorsoventral Coordinates (Y in [1.0, 4.5] mm, ventral horn)
        self.y = self.rng.uniform(1.2, 4.2, self.n_neurons)

        # 4. Hemicord assignment
        self.hemicord = np.where(self.x < 0, 'left', 'right')

        # 5. Functional Population Assignment
        self.population = np.empty(self.n_neurons, dtype=object)
        self.is_excitatory = np.zeros(self.n_neurons, dtype=bool)
        self.is_commissural = np.zeros(self.n_neurons, dtype=bool)
        self.is_motoneuron = np.zeros(self.n_neurons, dtype=bool)

        for i in range(self.n_neurons):
            z_pos = self.z[i]
            # 15% of neurons are commissural cross-cord
            if self.rng.random() < 0.15:
                self.population[i] = 'Comm_Contra'
                self.is_excitatory[i] = (self.rng.random() < 0.60) # 60% exc, 40% inh commissural
                self.is_commissural[i] = True
            elif z_pos < 12.0: # Rostral region (L4-L5): Flexor-dominant
                if self.rng.random() < 0.55:
                    self.population[i] = 'RFlex_E'
                    self.is_excitatory[i] = True
                else:
                    self.population[i] = 'RFlex_I'
                    self.is_excitatory[i] = False
            elif z_pos < 23.0: # Mid-to-caudal region (L6-L7): Extensor-dominant
                if self.rng.random() < 0.60:
                    self.population[i] = 'CExt_E'
                    self.is_excitatory[i] = True
                else:
                    self.population[i] = 'CExt_I'
                    self.is_excitatory[i] = False
            else: # Caudal extremity (L7-S1): Retractor-dominant
                if self.rng.random() < 0.55:
                    self.population[i] = 'CRet_E'
                    self.is_excitatory[i] = True
                else:
                    self.population[i] = 'CRet_I'
                    self.is_excitatory[i] = False

        # DataFrame of spatial properties
        self.df_neurons = pd.DataFrame({
            'neuron_id': np.arange(self.n_neurons),
            'x_mm': np.round(self.x, 3),
            'y_mm': np.round(self.y, 3),
            'z_mm': np.round(self.z, 3),
            'level_norm': np.round((self.z / self.length_mm) * 100.0, 2),
            'hemicord': self.hemicord,
            'population': self.population,
            'is_excitatory': self.is_excitatory,
            'is_commissural': self.is_commissural
        })

    def get_slice_index(self, z_mm: float) -> int:
        """Returns 0-indexed slice (0..29) for given z coordinate."""
        return int(np.clip(np.floor(z_mm / self.slice_thickness), 0, self.n_slices - 1))
