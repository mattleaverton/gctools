#!/usr/bin/env python
# ----------------------------------------------------------------------------
# 04-Dec-2014 ShaneG
#
# A simple program to determine the dimensions and units of a g-code file.
# ----------------------------------------------------------------------------
from optparse import OptionParser
from sys import argv

import matplotlib.pyplot as plt
import numpy as np

from util import defaultExtension

# --- Usage information
USAGE = """
Usage:
       %s [--image] filename

Where:

  --image           generate an image of the file
"""


class ProbeFile:
    """ Represents a probe file
    """

    def __init__(self, filename):
        """ Initialise from a file
        """
        points = list()
        for line in open(defaultExtension(filename, ".probe"), "r"):
            line = line.strip()
            if len(line) > 0:
                parts = line.split(" ")
                if len(parts) != 3:
                    raise Exception("Unrecognised probe file format")
                parts = list([float(val) for val in parts])
                points.append(parts)
        # Do some verification
        if len(points) < 3:
            raise Exception("File appears to be truncated")
        self.xstart, self.xend, self.xsteps = points[0]
        self.ystart, self.yend, self.ysteps = points[1]
        self.zmin, self.zmax, self.feed = points[2]
        points = points[3:]
        if len(points) != (self.xsteps * self.ysteps):
            raise Exception("File appears to be truncated")
        # Sort points into an X/Y array
        self.points = points
        self.pdict = dict()
        total = 0.0
        for x, y, z in points:
            if not self.pdict.has_key(x):
                self.pdict[x] = dict()
            if not self.pdict[x].has_key(y):
                self.pdict[x][y] = z
            else:
                raise Exception("Duplicate point found - %0.4f, %0.4f, %0.4f" % (x, y, z))
        self.xvals = sorted(self.pdict.keys())
        self.yvals = sorted(self.pdict[self.xvals[0]].keys())
        # Calculate average and median
        self.zlevels = sorted([p[2] for p in points])
        self.zcount = len(self.zlevels)
        self.average = sum(self.zlevels) / len(points)
        index = self.zcount // 2
        if len(self.zlevels) % 2:
            self.median = self.zlevels[index]
        else:
            self.median = (self.zlevels[index - 1] + self.zlevels[index]) / 2.0

    def generateImage(self, filename):
        """ Generate a heatmap of the probe
        """
        data = list()
        for y in sorted(self.yvals, reverse=True):
            line = list()
            for x in self.xvals:
                line.append(self.pdict[x][y] - self.median)
            data.append(line)
        my_data = np.array(data)
        fig = plt.figure(figsize=plt.figaspect(0.5))
        plt.subplot(1, 1, 1, xticks=[], yticks=[])
        plt.imshow(my_data, cmap='copper')
        plt.colorbar()
        fig.set_size_inches((16, 8))
        plt.savefig(filename, dpi=100)


# --- Main program
if __name__ == "__main__":
    # Set up program options
    parser = OptionParser()
    parser.add_option("-i", "--image", action="store_true", dest="image", default=False)
    options, args = parser.parse_args()
    # Check positional arguments
    if len(args) != 1:
        print(USAGE.strip() % argv[0])
        exit(1)
    # Load the probe file
    #  try:
    probe = ProbeFile(args[0])
    #  except Exception , ex:
    #    LOG.FATAL("Could not load file '%s' - %s" % (args[0], ex))
    # Display basic information
    print("Probe from X %0.4f -> %0.4f, Y %0.4f -> %0.4f" % (probe.xstart, probe.xend, probe.ystart, probe.yend))
    print("Z levels range from %0.4f to %0.4f" % (min(probe.zlevels), max(probe.zlevels)))
    print(
        "  Diff: %0.4f, Avg: %0.4f, Med: %0.4f" % (
        max(probe.zlevels) - min(probe.zlevels), probe.average, probe.median))
    # Generate a plot if requested
    if options.image:
        probe.generateImage(defaultExtension(args[0], ".png", True))
