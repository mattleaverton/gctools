#!/usr/bin/env python
# ----------------------------------------------------------------------------
# 22-Jul-2015 ShaneG
#
# A simple set of filters.
# ----------------------------------------------------------------------------
from math import sin, cos, radians

from util.gcode import Filter


class SwapXY(Filter):
    """ Swap X/Y (and I/J) co-ordinates
    """

    def apply(self, command):
        result = command.clone()
        result.X, result.Y = command.Y, command.X
        result.I, result.J = command.J, command.I
        return result


class Translate(Filter):
    """ Translate on one or more axis
    """

    def __init__(self, dx=0.0, dy=0.0, dz=0.0):
        self.dx = dx
        self.dy = dy
        self.dz = dz

    def apply(self, command):
        result = command.clone()
        if command.X is not None:
            result.X = command.X + self.dx
        if command.Y is not None:
            result.Y = command.Y + self.dy
        if command.Z is not None:
            result.Z = command.Z + self.dz
        return result


class Rotate(Filter):
    """ Rotate around the origin
    """

    def __init__(self, angle):
        """ Set the rotation angle
        """
        self.angle = radians(angle)
        self.ox, self.oy = 0.0, 0.0
        self.nx, self.ny = 0.0, 0.0

    def apply(self, command):
        result = command.clone()
        # I, J are relative to current position so translate before rotating
        if (command.I is not None) and (command.J is not None):
            i = command.I + self.ox
            j = command.J + self.oy
            result.I = ((i * cos(self.angle)) - (j * sin(self.angle))) - self.nx
            result.J = ((i * sin(self.angle)) + (j * cos(self.angle))) - self.ny
        # Do the X, Y co-ordinates
        if (command.X is not None) and (command.Y is not None):
            result.X = (command.X * cos(self.angle)) - (command.Y * sin(self.angle))
            result.Y = (command.X * sin(self.angle)) + (command.Y * cos(self.angle))
        # Save position
        self.ox = command.X or self.ox
        self.oy = command.Y or self.oy
        self.nx = (self.ox * cos(self.angle)) - (self.oy * sin(self.angle))
        self.ny = (self.ox * sin(self.angle)) + (self.oy * cos(self.angle))
        # Done
        return result


class Flip(Filter):
    """ Flip X and or Y points around a given center point
    """

    def __init__(self, xflip=None, yflip=None):
        """ Set the rotation angle
        """
        self.xflip = xflip
        self.yflip = yflip
        self.ox, self.oy = 0.0, 0.0
        self.nx, self.ny = 0.0, 0.0

    def apply(self, command):
        result = command.clone()
        if self.xflip is not None:
            if command.X is not None:
                result.X = self.xflip - (command.X - self.xflip)
            if command.I is not None:
                # I is relative so translate first
                i = command.I + self.ox
                result.I = (self.xflip - (i - self.xflip)) - self.nx
                # Arcs change direction in a flip
                if command.command == "G02":
                    result.command = "G03"
                elif command.command == "G03":
                    result.command = "G02"
        if self.yflip is not None:
            if command.Y is not None:
                result.Y = self.yflip - (command.Y - self.yflip)
            if command.J is not None:
                # J is relative so translate first
                j = command.J + self.oy
                result.J = (self.yflip - (j - self.yflip)) - self.ny
                # Arcs change direction in a flip
                if command.command == "G02":
                    result.command = "G03"
                elif command.command == "G03":
                    result.command = "G02"
        # Save position
        self.ox = command.X or self.ox
        self.oy = command.Y or self.oy
        self.nx = result.X or self.nx
        self.ny = result.Y or self.ny
        # All done
        return result


class ZLevel(Filter):
    """ Adjust Z levels for safe and cut depths
    """

    def __init__(self, cut=None, safe=None):
        """ Set the depths to use
        """
        self.cut = cut
        self.safe = safe

    def apply(self, command):
        if command.Z is None:
            return command
        command = command.clone()
        if (command.Z < 0.0) and (self.cut is not None):
            command.Z = self.cut
        elif (command.Z > 0.0) and (self.safe is not None):
            command.Z = self.safe
        # All done
        return command


class FeedRate(Filter):
    """ Adjust the cutting feed rate
    """

    def __init__(self, cutting=None, drilling=None):
        self.cutting = cutting
        self.drilling = drilling

    def apply(self, command):
        # Is it a cutting operation ?
        if not command.command in ("G01", "G02", "G03"):
            return command
        # Are we drilling?
        if command.Z is not None:
            # Is a feed rate set ?
            if (command.F is not None) and (self.drilling is not None):
                command.F = self.drilling
        elif (command.X is not None) or (command.Y is not None):
            # Is a feed rate set ?
            if (command.F is not None) and (self.cutting is not None):
                command.F = self.cutting
        return command
