# stdlib imports
import os.path

# third party imports
import numpy as np

# local imports
from .grid2d import Grid2D
from .geodict import GeoDict
from .reader import read, get_file_geodict

BIG = 99999999999
SMALL = -99999999999


class TileCollection(object):
    """Create a collection of images from which data can be subset.

    """

    def __init__(self, tiledir):
        """
        Instantiate a TileCollection with a directory of input data. 

        Non-image data files will be ignored.
        """
        self._tiledir = tiledir
        has_raster_files = False
        xmin, xmax, ymin, ymax = BIG, SMALL, BIG, SMALL
        self._files = []
        for tfile in os.listdir(tiledir):
            fullfile = os.path.join(tiledir, tfile)
            try:
                gdict = get_file_geodict(fullfile)
                # TODO - maybe error out if any of the files
                # cross the 180 meridian?
                has_raster_files = True
                self._files.append(fullfile)
                ######################################
                # TODO: Figure out 180 meridian stuff
                if gdict.xmin < xmin:
                    xmin = gdict.xmin
                if gdict.xmax > xmax:
                    xmax = gdict.xmax
                ######################################

                if gdict.ymin < ymin:
                    ymin = gdict.ymin
                if gdict.ymax > ymax:
                    ymax = gdict.ymax
            except Exception as e:
                continue

        if not has_raster_files:
            msg = 'No valid raster files found in %s' % tiledir
            raise FileNotFoundError(msg)

        self._xmin = xmin
        self._xmax = xmax
        self._ymin = ymin
        self._ymax = ymax

    def getGrid(self, geodict, resample_method='linear', pad_value=np.nan):
        """Extract a Grid2D object from the TileCollection given input sampling geodict.

        Args:
            geodict (GeoDict): Defines bounds/resolution of sampling area.
            resample_method (str): One of ('nearest','linear').
            pad_value (float): Value to insert where real data is not found.
        Returns:
            Grid2D: A resampled grid of data extracted from collection of grid files.
        Raises:
            IndexError: When geodict does not intersect with TileCollection.
        """
        # let's create a geodict from our global boundaries
        global_dict = GeoDict.createDictFromBox(self._xmin, self._xmax,
                                                self._ymin, self._ymax,
                                                5.0, 5.0)
        if not global_dict.intersects(geodict):
            raise IndexError('Input grid not contained by TileCollection.')

        # loop over files, getting all of the pieces that intersect with our grid.
        # TODO: what do we do if there are overlaps?
        # for now, just stomp on top.
        outgrid = np.ones((geodict.ny, geodict.nx))*pad_value
        for tfile in self._files:
            gdict = get_file_geodict(tfile)
            if not gdict.intersects(geodict):
                continue
            intersection = geodict.getIntersection(gdict)
            uly, ulx = geodict.getRowCol(intersection.ymax, intersection.xmin)
            lry, lrx = geodict.getRowCol(intersection.ymin, intersection.xmax)
            data = read(tfile, samplegeodict=intersection, resample=True,
                        doPadding=True)
            outgrid[uly:lry+1, ulx:lrx+1] = data._data

        grid = Grid2D(outgrid, geodict)
        return grid

    def getExtent(self):
        """Get the bounding box (xmin, xmax, ymin, ymax) of TileCollection.

        Returns:
            tuple: Bounding box (xmin, xmax, ymin, ymax) of TileCollection
        """
        return (self._xmin, self._xmax, self._ymin, self._ymax)

    def getFiles(self):
        """Get the contributing grid files found in input directory.

        Returns:
            list: List of contributing grid files found in input directory.
        """
        return self._files
