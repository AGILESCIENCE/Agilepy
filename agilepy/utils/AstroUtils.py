# DESCRIPTION
#       Agilepy software
#
# NOTICE
#      Any information contained in this software
#      is property of the AGILE TEAM and is strictly
#      private and confidential.
#      Copyright (C) 2005-2020 AGILE Team.
#          Baroncelli Leonardo <leonardo.baroncelli@inaf.it>
#          Addis Antonio <antonio.addis@inaf.it>
#          Bulgarelli Andrea <andrea.bulgarelli@inaf.it>
#          Parmiggiani Nicolò <nicolo.parmiggiani@inaf.it>
#      All rights reserved.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import math

#mpl.use("Agg")
import matplotlib.pyplot as plt
from astropy.wcs import WCS
from astropy.io import fits
from regions import read_ds9
import scipy.ndimage as ndimage
import ntpath
from os.path import join



class AstroUtils:

    def __init__(self):
        pass

    @staticmethod
    def distance(ll, bl, lf, bf):

        if ll < 0 or ll > 360 or lf < 0 or lf > 360:
            return -2
        elif bl < -90 or bl > 90 or bf < -90 or bf > 90:
            return -2
        else:
            d1 = bl - bf
            d2 = ll - lf;

            bl1 = math.pi / 2.0 - (bl * math.pi / 180.0)
            bf1 = math.pi / 2.0 - (bf * math.pi / 180.0)
            m4 = math.cos(bl1) * math.cos(bf1) + math.sin(bl1) * math.sin(bf1) * math.cos(d2 * math.pi / 180.0);
            if m4 > 1:
                m4 = 1

            try:
                return math.acos(m4) * 180.0 / math.pi;

            except Exception as e:

                print("\nException in AstroUtils.distance (error in acos() ): ", e)

                return math.sqrt(d1 * d1 + d2 * d2);

    @staticmethod
    def time_mjd_to_tt(timemjd):
        return (timemjd - 53005.0) * 86400.0

    @staticmethod
    def time_tt_to_mjd(timett):
        return (timett / 86400.0) + 53005.0


    def displaySkyMap(fitsFilepath,  smooth, sigma, saveImage, outDir, format, title, cmap, regFilePath):
        hdu = fits.open(fitsFilepath)[0]

        wcs = WCS(hdu.header)
        plt.figure(figsize=(10, 10))
        ax = plt.subplot(projection=wcs)
        if title:
            ax.set_title(title, fontsize='large')
        if smooth:
            data = ndimage.gaussian_filter(hdu.data, sigma=float(sigma), order=0, output=float)
        else:
            data = hdu.data

        #cmap = plt.cm.CMRmap
        #cmap.set_bad(color='black')

        plt.imshow(data, origin='lower', norm=None, cmap=cmap)
        # interpolation = "gaussian",
        if regFilePath is not None:
            regions = read_ds9(regFilePath)
            for region in regions:
                pixelRegion = region.to_pixel(wcs=wcs)
                pixelRegion.plot(ax=ax, color="green")

        plt.grid(color='white', ls='solid')
        plt.colorbar()
        if wcs.wcs.ctype[0].find('LAT') == 0:
            plt.xlabel('Galactic Longitude')
            plt.ylabel('Galactic Latitude')
        if wcs.wcs.ctype[0].find('RA') == 0:
            plt.xlabel('Right ascension')
            plt.ylabel('Declination')

        if saveImage:
            _, filename = ntpath.split(fitsFilepath)
            filename = join(outDir, filename+"."+format)
            plt.savefig(filename)
            return filename
        else:
            plt.show()

#if __name__ == "__main__":
#    path = AstroUtils.displaySkyMap("examples/testcase_EMIN00100_EMAX00300_01.cts.gz", outDir="./", smooth=True, sigma=4, saveImage=False, title="ciao", format=None, cmap="Greys", regFilePath="examples/2AGL_2.reg")