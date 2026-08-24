"""
Unit tests for SpinalDataLoader.
Validates the original biological data for the mouse spinal cord model.
"""

import sys
import os
import pytest
import numpy as np
import pandas as pd

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))
try:
    from data_loader import SpinalDataLoader
except ImportError:
    from src.data_loader import SpinalDataLoader


@pytest.fixture
def loader():
    return SpinalDataLoader()


def test_load_geometry_dimensions(loader):
    geom = loader.load_geometry()
    assert geom['weights'].shape == (20755, 80), "Weights must have shape (20755, 80)"
    assert geom['n_voxels'] == 20755, "Should have 20,755 spatial voxels"
    assert geom['n_cell_types'] == 80, "Should have 80 cell types in spatial geometry"
    assert len(geom['cell_types']) == 80, "Cell types list length must match 80"
    assert geom['weights'].min() >= 0.0, "Weights must be non-negative"
    assert geom['weights'].max() <= 1.0, "Weights must be normalized <= 1.0"


def test_load_geometry_transmitters(loader):
    geom = loader.load_geometry()
    trans = geom['transmitter']
    assert len(trans) == 80, "Transmitter array must have 80 elements"
    assert np.all(np.isin(trans, [-1.0, 1.0])), "Transmitter values must be +1.0 or -1.0"
    
    # Check that inhibitory types are -1 and excitatory are +1
    for i, name in enumerate(geom['cell_types']):
        if name.startswith('Inhib') or name == 'CSF-cN':
            assert trans[i] == -1.0, f"Cell type {name} should be inhibitory (-1)"
        elif name.startswith('Excit') or name.startswith('MN'):
            assert trans[i] == 1.0, f"Cell type {name} should be excitatory (+1)"


def test_load_geometry_coordinates(loader):
    geom = loader.load_geometry()
    x = geom['coord_x_um']
    y = geom['coord_y_um']
    assert len(x) == 20755, "X coordinate length must be 20,755"
    assert len(y) == 20755, "Y coordinate length must be 20,755"
    
    # Mediolateral range should span 3500 um centered around 0
    assert np.isclose(np.ptp(x), 3500.0, atol=1e-3), "X span should be exactly 3500 um"
    assert x.min() >= -1750.1 and x.max() <= 1750.1, "X range must be within [-1750, 1750] um"
    # Dorsoventral range
    assert y.min() >= 0.0 and y.max() <= 2000.0, "Y range must be within [0, 2000] um"


def test_load_geometry_segments(loader):
    geom = loader.load_geometry()
    lengths = geom['segment_lengths_um']
    names = geom['segment_names']
    assert len(lengths) == 31, "Should have 31 spinal segments"
    assert len(names) == 31, "Should have 31 segment names"
    assert np.all(lengths > 0), "All segment lengths must be positive"
    assert names[0] == 'C1' and names[20] == 'T13' and names[21] == 'L1' and names[30] == 'S4'


def test_load_cell_census(loader):
    df = loader.load_cell_census()
    assert isinstance(df, pd.DataFrame), "Census must be a DataFrame"
    assert len(df) == 69, "Census should contain 69 cell types"
    expected_cols = ['Cluster', 'Lamina', '%', 'NT', 'Family', 'Putative Lineage']
    for col in expected_cols:
        assert col in df.columns, f"Column '{col}' must be present in census"


def test_load_motoneuron_distribution(loader):
    df = loader.load_motoneuron_distribution()
    assert isinstance(df, pd.DataFrame), "Motoneuron distribution must be a DataFrame"
    assert len(df) > 0, "Motoneuron distribution DataFrame must not be empty"


def test_load_descending_tracts(loader):
    tracts = loader.load_descending_tracts()
    assert len(tracts) == 16, "Should load 16 descending tract ROIs"
    expected_tracts = [
        'CorticospinalL', 'CorticospinalR',
        'RubrospinalL', 'RubrospinalR',
        'MedullalryReticulospinalL', 'MedullalryReticulospinalR',
        'PontineReticuloL', 'PontineReticuloR',
        'MedialVestibuloL', 'MedialVestibuloR',
        'LPGIVglutL', 'LPGIVglutR',
        'LPGIVglyL', 'LPGIVglyR',
        'RapheObsL', 'RapheObsR'
    ]
    for t in expected_tracts:
        assert t in tracts, f"Tract {t} must be present in descending tracts dictionary"
        assert len(tracts[t]) > 0, f"Tract {t} coordinate array must not be empty"


def test_load_muscle_segments(loader):
    muscles = loader.load_muscle_segments()
    assert len(muscles['muscle_names']) == 35, "Should have 35 muscle pools"
    assert 'Tibialis anterior' in muscles['muscle_names']
    assert 'Gastrocnemius' in muscles['muscle_names']
    assert 'Biceps femoris' in muscles['muscle_names']


def test_sample_neuron_positions(loader):
    df_cells = loader.sample_neuron_positions(density=1.0, length_um=11000.0, rng_seed=42)
    assert len(df_cells) > 0, "Sampled neurons should not be empty"
    assert set(df_cells.columns) >= {'neuron_id', 'cell_type_idx', 'cell_type', 'transmitter', 'x_um', 'y_um', 'z_um'}
    assert df_cells['x_um'].min() >= -2000.0 and df_cells['x_um'].max() <= 2000.0
    assert df_cells['y_um'].min() >= -100.0 and df_cells['y_um'].max() <= 2000.0
    assert df_cells['z_um'].min() >= 0.0 and df_cells['z_um'].max() <= 11000.0
