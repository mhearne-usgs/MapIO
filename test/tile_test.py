#!/usr/bin/env python

import os.path
import time
import sys
import tempfile
import shutil

import numpy as np
import rasterio

from mapio.writer import write
from mapio.geodict import GeoDict
from mapio.grid2d import Grid2D
from mapio.tile import TileCollection


def test_tile():
    # first, make a bunch of image tiles that do not overlap
    tdir = tempfile.mkdtemp()
    try:
        # create 4 grids that together form a cube
        geo1 = GeoDict({'xmin': 20, 'xmax': 40,
                        'ymin': 40, 'ymax': 70,
                        'dx': 10, 'dy': 10,
                        'nx': 3, 'ny': 4})
        img1 = np.array([[1, 2, 3],
                         [7, 8, 9],
                         [13, 14, 15],
                         [19, 20, 21]], dtype=np.float32)
        grid1 = Grid2D(img1, geo1)
        file1 = os.path.join(tdir, 'grid1.cdf')

        geo2 = GeoDict({'xmin': 50, 'xmax': 70,
                        'ymin': 40, 'ymax': 70,
                        'dx': 10, 'dy': 10,
                        'nx': 3, 'ny': 4})
        img2 = np.array([[4, 5, 6],
                         [10, 11, 12],
                         [16, 17, 18],
                         [22, 23, 24]], dtype=np.float32)
        grid2 = Grid2D(img2, geo2)
        file2 = os.path.join(tdir, 'grid2.cdf')

        geo3 = GeoDict({'xmin': 20, 'xmax': 40,
                        'ymin': 0, 'ymax': 30,
                        'dx': 10, 'dy': 10,
                        'nx': 3, 'ny': 4})
        img3 = np.array([[25, 26, 27],
                         [31, 32, 33],
                         [37, 38, 39],
                         [43, 44, 45]], dtype=np.float32)
        grid3 = Grid2D(img3, geo3)
        file3 = os.path.join(tdir, 'grid3.cdf')

        geo4 = GeoDict({'xmin': 50, 'xmax': 70,
                        'ymin': 0, 'ymax': 30,
                        'dx': 10, 'dy': 10,
                        'nx': 3, 'ny': 4})
        img4 = np.array([[28, 29, 30],
                         [34, 35, 36],
                         [40, 41, 42],
                         [46, 47, 48]], dtype=np.float32)
        grid4 = Grid2D(img4, geo4)
        file4 = os.path.join(tdir, 'grid4.cdf')

        write(grid1, file1, 'netcdf')
        write(grid2, file2, 'netcdf')
        write(grid3, file3, 'netcdf')
        write(grid4, file4, 'netcdf')

        # whew.  Ok, let's get a simple subset
        geodict = GeoDict({'xmin': 30, 'xmax': 60,
                           'ymin': 20, 'ymax': 50,
                           'dx': 10, 'dy': 10,
                           'nx': 4, 'ny': 4})
        tile_collection = TileCollection(tdir)
        grid = tile_collection.getGrid(geodict, resample_method='nearest')
        tdata = np.array([[14, 15, 16, 17],
                          [20, 21, 22, 23],
                          [26, 27, 28, 29],
                          [32, 33, 34, 35]])
        np.testing.assert_almost_equal(grid._data, tdata)

    except Exception as e:
        assert 1 == 2
    finally:
        shutil.rmtree(tdir)


if __name__ == '__main__':
    test_tile()
