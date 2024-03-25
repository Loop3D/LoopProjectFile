from LoopProjectFile import ProjectFile
from LoopProjectFile.LoopProjectFile import OpenProjectFile
import LoopProjectFile.Extents as Extents


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

    dummy_data = {'geodesic': [0, 1, -180, -179],
                'utm': [1,
                        1,
                        492670.29729283287,
                        559597.3907658446,
                        7495054.492409904,
                        7522315.252989877],
                'depth': [-22, 1200],
                'spacing': [1000, 1000, 10]}
    data = OpenProjectFile("test.loop3d", readOnly=False)
    root = data["root"]

    geodesic=dummy_data['geodesic']
    utm = dummy_data['utm']
    depth = dummy_data['depth']
    spacing=dummy_data['spacing']
    print("setting")
    Extents.SetExtents(root, geodesic , utm, depth, spacing, preference="utm")
    print('finish setting')


def test_get_extents():

    data = OpenProjectFile("test.loop3d", readOnly=False)
    root = data["root"]

    extents_response = Extents.GetExtents(root)

    assert not extents_response["errorFlag"], "GetExtents Error"

    extents = extents_response["value"]

    assert extents['geodesic'] == [0, 1, -180, -179], "Geodesic extents do not match"
    assert extents['utm'] == [1, 1, 492670.29729283287, 559597.3907658446, 7495054.492409904, 7522315.252989877], "UTM extents do not match"
    assert extents['depth'] == [-3200, 1200], "Depth extents do not match"
    assert extents['spacing'] == [1000, 1000, 10], "Spacing extents do not match"
    assert extents['epsg'] == 32601, "epsg does not match" 
    print("GetExtents tests passed")



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

test_set_extents()
test_get_extents()