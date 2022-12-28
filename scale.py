#!/usr/bin/env python
# ----------------------------------------------------------------------------
# 28-Dec-2022 Matt L
#
# Scale a gcode file
# ----------------------------------------------------------------------------
from optparse import OptionParser
from os.path import splitext
from sys import argv

from util import loadGCode, saveGCode, Scale

# --- Usage information
USAGE = """
Usage:
       %s [--scale factor] [--output filename] [--image] filename

Where:

  --scale   factor      multiplying factor to scale (1.0 is no scale)
  --image               generate an image of the result
  --output  filename    the name of the file to write the results to
"""

if __name__ == "__main__":
    # Set up program options
    parser = OptionParser()
    parser.add_option("-s", "--scale", action="store", type="float", dest="factor")
    parser.add_option("-o", "--output", action="store", type="string", dest="output")
    parser.add_option("-i", "--image", action="store_true", dest="image", default=False)
    options, args = parser.parse_args()
    # Check positional arguments
    if len(args) != 1:
        print(USAGE.strip() % argv[0])
        exit(1)
    # Make sure required arguments are present
    for req in ("output", "factor"):
        if getattr(options, req) is None:
            print("ERROR: Missing required argument '%s'" % req)
            print(USAGE.strip() % argv[0])
            exit(1)
    source = args[0]
    # Process the file
    gcode = loadGCode(source)
    print("Loaded - %s" % str(gcode))
    gcode = gcode.clone(Scale(options.factor))
    print("Generated - %s" % str(gcode))
    # Generate an image if required
    name, ext = splitext(options.output)
    if options.image:
        filename = name + ".png"
        gcode.render(filename)
    # Generate the output file
    if ext == "":
        ext = ".ngc"
    saveGCode(name + ext, gcode)
