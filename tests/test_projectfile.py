from LoopProjectFile import ProjectFile
# import pandas as pd
# import numpy as np


def test_create_basic():
    # file = ProjectFile.new('test.loop3d')
    # file = ProjectFile('test.loop3d')
    pass


def test_set_stratigraphic_log():
    # file = ProjectFile.new('test.loop3d')

    pass


def test_set_extents():
    file = ProjectFile.new("test.loop3d")
    file.extents = {
        "geodesic": [0, 1, -180, -179],
        "utm": [
            1,
            1,
            492670.29729283287,
            559597.3907658446,
            7495054.492409904,
            7522315.252989877,
        ],
        "depth": [-3200, 1200],
        "spacing": [1000, 1000, 10],
    }
    extents = file.extents
    assert extents["geodesic"] == [0, 1, -180, -179]
    assert extents["utm"] == [
        1,
        1,
        492670.29729283287,
        559597.3907658446,
        7495054.492409904,
        7522315.252989877,
    ]
    assert extents["depth"] == [-3200, 1200]
    assert extents["spacing"] == [1000, 1000, 10]
    assert file.is_valid()


def test_set_fault_observations():
    # file = ProjectFile.new('test.loop3d')

    pass


def test_set_fault_locations():
    pass


def test_set_fault_orientations():
    pass


def test_set_fault_log():
    pass


def test_set_foliation_observations():
    pass


def test_set_fold_observations():
    pass


def test_set_stratigraphy_locations():
    pass


def test_set_stratigraphy_orientations():
    pass
