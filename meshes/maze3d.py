import bpy
import copy

from .utils.transform import *
from .maze2d import RectCell, RectGrid


class VertState:
    def __init__(self, log=False):
        self.log = log
        self.verts = []
        self.vdict = {}

    def lookup(self, v):
        i = self.vdict.get(v)
        if i == None:
            if self.log:
                print(f'adding {v}')
            self.verts.append(v)
            pos = len(self.verts)-1
            self.vdict[v] = pos
            if self.log:
                print(f'verts={self.verts}')
                print(f'vdict={self.vdict}')
            return pos
        else:
            if self.log:
                print(f'found {v}')
            return i


class RectCell3d(RectCell):
    def __init__(self, rows, cols, levels, cap2d, cap3d, id, row, col, level, weight=1, masked=False, clear=False, inset=0):
        assert inset >= 0 and inset <= 0.45
        self.id = id
        self.row = row
        self.col = col
        self.level = level
        self.links = []
        self.masked = masked
        self.weight = weight
        self.inset = inset
        self.calc_neighbors_3d(rows, cols, levels, cap2d)
        if clear:
            self.links.extend(self.neighbors_3d())

    def flatten_cell(self, inset=0.0):
        new = copy.copy(self)
        new.level = 0
        new.inset = inset
        new.above = None
        new.below = None
        return new

    def string(self):
        return f'''id={self.id} row={self.row} col={self.col} level={self.level} links={self.links} masked={self.masked} weight={self.weight}
        n={self.north} e={self.east} s={self.south} w={self.west} above={self.above} below={self.below}'''

    def calc_neighbors_3d(self, rows, cols, levels, cap2d):
        n = self.id - cols  # was using rows here, why?
        e = self.id + 1
        s = self.id + cols  # was using rows here, why?
        w = self.id - 1
        a = self.id + cap2d
        b = self.id - cap2d
        self.north = n if self.row > 0 else None
        self.east = e if not self.col >= cols-1 else None
        self.south = s if not self.row >= rows-1 else None
        self.west = w if self.col > 0 else None
        self.above = a if self.level < levels - 1 else None
        self.below = b if self.level > 0 else None

    # Neighbor Methods

    def neighbors_3d(self):
        return list(filter(lambda d: d != None, [
            self.north, self.east, self.south, self.west, self.above, self.below]))

    def neighbors_2d(self):
        return list(filter(lambda d: not d is None, [
            self.north, self.east, self.south, self.west]))

    def neighbors(self):
        return self.neighbors_3d()

    # Link methods

    def linked_above(self):
        return self.linked_to(self.above)

    def linked_below(self):
        return self.linked_to(self.below)

    def has_links(self):
        return self.north in self.links or self.east in self.links or self.south in self.links or self.west in self.links

    def has_links_3d(self):
        return len(self.links) != 0

    def show_above_wall(self):
        return self.above == None or not self.linked_to(self.above)

    def show_below_wall(self):
        return self.below == None or not self.linked_to(self.below)

    def has_neighbor_at(self, dir):
        match dir:
            case 'above': return self.above != None
            case 'below': return self.below != None
            case 'north': return self.north != None
            case 'east': return self.east != None
            case 'south': return self.south != None
            case 'west': return self.west != None

    def linked_at(self, dir):
        match dir:
            case 'above': return self.linked_above()
            case 'below': return self.linked_below()
            case 'north': return self.linked_north()
            case 'east': return self.linked_east()
            case 'south': return self.linked_south()
            case 'west': return self.linked_west()

    def is_edge(self, grid, dir):
        match dir:
            case 'above': return self.level == grid.levels - 1
            case 'below': return self.level == 0
            case 'north': return self.row == 0
            case 'east': return self.col == grid.cols - 1
            case 'south': return self.row == grid.rows - 1
            case 'west': return self.col == 0

    def show_wall(self, dir):
        match dir:
            case 'above': return self.show_above_wall()
            case 'below': return self.show_below_wall()
            case 'north': return self.show_north_wall()
            case 'east': return self.show_east_wall()
            case 'south': return self.show_south_wall()
            case 'west': return self.show_west_wall()

    # Verticies

    def vswb(self):
        return vert_pos(self.col, self.row+1, self.level)

    def vseb(self):
        return vert_pos(self.col+1, self.row+1, self.level)

    def vswa(self):
        return vert_pos(self.col, self.row+1, self.level+1)

    def vsea(self):
        return vert_pos(self.col+1, self.row+1, self.level+1)

    def vnwb(self):
        return vert_pos(self.col, self.row, self.level)

    def vneb(self):
        return vert_pos(self.col+1, self.row, self.level)

    def vnwa(self):
        return vert_pos(self.col, self.row, self.level+1)

    def vnea(self):
        return vert_pos(self.col+1, self.row, self.level+1)

    # Inset verticies

    def vix0(self):
        return self.col
        # return self.neg0(self.col, self.inset)

    def vix1(self):
        return self.col + self.inset
        # return self.neg1(self.col, self.inset)

    def vix2(self):
        return self.col + 1 - self.inset
        # return self.neg2(self.col, self.inset)

    def vix3(self):
        return self.col + 1
        # # return self.neg3(self.col, self.inset)

    def viy0(self):
        # return self.row
        return self.neg0(self.row, self.inset)

    def viy1(self):
        # return self.row + self.inset
        return self.neg1(self.row, self.inset)

    def viy2(self):
        # return self.row + 1 - self.inset
        return self.neg2(self.row, self.inset)

    def viy3(self):
        # return self.row + 1
        return self.neg3(self.row, self.inset)

    def viz0(self):
        return self.level

    def viz1(self):
        return self.level + self.inset

    def viz2(self):
        return self.level + 1 - self.inset

    def viz3(self):
        return self.level + 1

    def vx_left_inner(self):
        return self.vix1()

    def vx_right_inner(self):
        return self.vix2()

    def vx_left_outer(self):
        return self.vix0()

    def vx_right_outer(self):
        return self.vix3()

    def vy_top_inner(self):
        return self.viy1()

    def vy_bottom_inner(self):
        return self.viy2()

    def vy_top_outer(self):
        return self.viy0()

    def vy_bottom_outer(self):
        return self.viy3()

    def vz_top_inner(self):
        return self.viz2()

    def vz_bottom_inner(self):
        return self.viz1()

    def vz_top_outer(self):
        return self.viz3()

    def vz_bottom_outer(self):
        return self.viz0()

    def neg0(self, loc, inset=0):
        return 0 - loc

    def neg1(self, loc, inset=0):
        return 0 - loc - self.inset

    def neg2(self, loc, inset=0):
        return 0 - loc - 1 + inset

    def neg3(self, loc, inset=0):
        return 0 - loc - 1

    # Face methods (that reference verticies in a list by their index position, which is found via dicitonary)

    def face_below(self, vdict):
        return [vdict[self.vswb()], vdict[self.vseb()], vdict[self.vneb()], vdict[self.vnwb()]]

    def face_above(self, vdict):
        return [vdict[self.vswa()], vdict[self.vsea()], vdict[self.vnea()], vdict[self.vnwa()]]

    def face_north(self, vdict):
        return [vdict[self.vnwb()], vdict[self.vneb()], vdict[self.vnea()], vdict[self.vnwa()]]

    def face_south(self, vdict):
        return [vdict[self.vswb()], vdict[self.vseb()], vdict[self.vsea()], vdict[self.vswa()]]

    def face_west(self, vdict):
        return [vdict[self.vswb()], vdict[self.vswa()], vdict[self.vnwa()], vdict[self.vnwb()]]

    def face_east(self, vdict):
        return [vdict[self.vseb()], vdict[self.vsea()], vdict[self.vnea()], vdict[self.vneb()]]

    def side_below(self, state):
        return [
            state.lookup(
                (self.vx_left_outer(), self.vy_top_outer(), self.vz_top_outer())),
            state.lookup(
                (self.vx_right_outer(), self.vy_top_outer(), self.vz_top_outer())),
            state.lookup(
                (self.vx_right_outer(), self.vy_bottom_outer(), self.vz_top_outer())),
            state.lookup(
                (self.vx_left_outer(), self.vy_bottom_outer(), self.vz_top_outer())),
        ]

    def side_above(self, state):
        return [
            state.lookup(
                (self.vx_left_outer(), self.vy_top_outer(), self.vz_top_outer())),
            state.lookup(
                (self.vx_right_outer(), self.vy_top_outer(), self.vz_top_outer())),
            state.lookup(
                (self.vx_right_outer(), self.vy_bottom_outer(), self.vz_top_outer())),
            state.lookup(
                (self.vx_left_outer(), self.vy_bottom_outer(), self.vz_top_outer())),
        ]

    def side_west(self, state):
        return [
            state.lookup(
                (self.vx_left_outer(), self.vy_top_outer(), self.vz_top_outer())),
            state.lookup(
                (self.vx_left_outer(), self.vy_bottom_outer(), self.vz_top_outer())),
            state.lookup(
                (self.vx_left_outer(), self.vy_bottom_outer(), self.vz_bottom_outer())),
            state.lookup(
                (self.vx_left_outer(), self.vy_top_outer(), self.vz_bottom_outer())),
        ]

    def side_east(self, state):
        return [
            state.lookup(
                (self.vx_right_outer(), self.vy_top_outer(), self.vz_top_outer())),
            state.lookup(
                (self.vx_right_outer(), self.vy_bottom_outer(), self.vz_top_outer())),
            state.lookup(
                (self.vx_right_outer(), self.vy_bottom_outer(), self.vz_bottom_outer())),
            state.lookup(
                (self.vx_right_outer(), self.vy_top_outer(), self.vz_bottom_outer())),
        ]

    def side_north(self, state):
        return [
            state.lookup(
                (self.vx_left_outer(), self.vy_top_outer(), self.vz_top_outer())),
            state.lookup(
                (self.vx_right_outer(), self.vy_top_outer(), self.vz_top_outer())),
            state.lookup(
                (self.vx_right_outer(), self.vy_top_outer(), self.vz_bottom_outer())),
            state.lookup(
                (self.vx_left_outer(), self.vy_top_outer(), self.vz_bottom_outer())),
        ]

    def side_south(self, state):
        return [
            state.lookup(
                (self.vx_left_outer(), self.vy_bottom_outer(), self.vz_top_outer())),
            state.lookup(
                (self.vx_right_outer(), self.vy_bottom_outer(), self.vz_top_outer())),
            state.lookup(
                (self.vx_right_outer(), self.vy_bottom_outer(), self.vz_bottom_outer())),
            state.lookup(
                (self.vx_left_outer(), self.vy_bottom_outer(), self.vz_bottom_outer())),
        ]

    # Inset face methods

    def inset_faces_above(self, state):
        w = [
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_top_outer())),
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_top_outer())),
        ]

        e = [
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_top_outer())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_top_outer())),
        ]

        n = [
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_top_outer())),
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_top_outer())),
        ]

        s = [
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_top_outer())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_top_outer())),
        ]

        return [w, e, n, s]

    def inset_faces_below(self, state):
        w = [
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_bottom_outer())),
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_bottom_outer())),
        ]

        e = [
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_bottom_outer())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_bottom_outer())),
        ]

        n = [
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_bottom_outer())),
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_bottom_outer())),
        ]

        s = [
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_bottom_outer())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_bottom_outer())),
        ]

        return [w, e, n, s]

    def inset_faces_west(self, state):
        n = [
            state.lookup(
                (self.vx_left_outer(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_left_outer(), self.vy_top_inner(), self.vz_top_inner())),
        ]

        s = [
            state.lookup(
                (self.vx_left_outer(), self.vy_bottom_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_left_outer(), self.vy_bottom_inner(), self.vz_top_inner())),
        ]

        a = [
            state.lookup(
                (self.vx_left_outer(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_left_outer(), self.vy_bottom_inner(), self.vz_top_inner())),
        ]

        b = [
            state.lookup(
                (self.vx_left_outer(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_left_outer(), self.vy_bottom_inner(), self.vz_bottom_inner())),
        ]

        return [n, s, a, b]

    def inset_faces_east(self, state):
        n = [
            state.lookup(
                (self.vx_right_outer(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_outer(), self.vy_top_inner(), self.vz_top_inner())),
        ]

        s = [
            state.lookup(
                (self.vx_right_outer(), self.vy_bottom_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_outer(), self.vy_bottom_inner(), self.vz_top_inner())),
        ]

        a = [
            state.lookup(
                (self.vx_right_outer(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_outer(), self.vy_bottom_inner(), self.vz_top_inner())),
        ]

        b = [
            state.lookup(
                (self.vx_right_outer(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_outer(), self.vy_bottom_inner(), self.vz_bottom_inner())),
        ]

        return [n, s, a, b]

    def inset_faces_north(self, state):
        w = [
            state.lookup(
                (self.vx_left_inner(), self.vy_top_outer(), self.vz_top_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_top_outer(), self.vz_bottom_inner())),
        ]

        e = [
            state.lookup(
                (self.vx_right_inner(), self.vy_top_outer(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_outer(), self.vz_bottom_inner())),
        ]

        a = [
            state.lookup(
                (self.vx_left_inner(), self.vy_top_outer(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_outer(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_top_inner())),
        ]

        b = [
            state.lookup(
                (self.vx_left_inner(), self.vy_top_outer(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_outer(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
        ]

        return [w, e, a, b]

    def inset_faces_south(self, state):
        w = [
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_outer(), self.vz_top_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_outer(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
        ]

        e = [
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_outer(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_outer(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
        ]

        a = [
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_outer(), self.vz_top_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_outer(), self.vz_top_inner())),
        ]

        b = [
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_outer(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_outer(), self.vz_bottom_inner())),
        ]

        return [w, e, a, b]

    def inset_faces_inner(self, state):
        return [self.inset_side_above(state), self.inset_side_below(state), self.inset_side_west(state), self.inset_side_east(state), self.inset_side_north(state), self.inset_side_south(state)]

    # Inner inset sides

    def inset_side_above(self, state):
        return [
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
        ]

    def inset_side_below(self, state):
        return [
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
        ]

    def inset_side_west(self, state):
        return [
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
        ]

    def inset_side_east(self, state):
        return [
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
        ]

    def inset_side_north(self, state):
        return [
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_top_inner(), self.vz_bottom_inner())),
        ]

    def inset_side_south(self, state):
        return [
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_top_inner())),
            state.lookup(
                (self.vx_right_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
            state.lookup(
                (self.vx_left_inner(), self.vy_bottom_inner(), self.vz_bottom_inner())),
        ]

    def draw_inset(self, dir, state):
        if self.show_wall(dir):
            return [self.inset_side(dir, state)]
        else:
            return self.inset_faces(dir, state)

    def inset_side(self, dir, state):
        match dir:
            case 'above': return self.inset_side_above(state)
            case 'below': return self.inset_side_below(state)
            case 'north': return self.inset_side_north(state)
            case 'east': return self.inset_side_east(state)
            case 'south': return self.inset_side_south(state)
            case 'west': return self.inset_side_west(state)

    def inset_faces(self, dir, state):
        match dir:
            case 'above': return self.inset_faces_above(state)
            case 'below': return self.inset_faces_below(state)
            case 'north': return self.inset_faces_north(state)
            case 'east': return self.inset_faces_east(state)
            case 'south': return self.inset_faces_south(state)
            case 'west': return self.inset_faces_west(state)

    def outside_connection_west(self, state, show_outer_faces=False):
        outer = copy.copy(self)
        outer.col -= 1
        faces = []
        # extend outer inset faces
        faces.extend(outer.inset_faces_east(state))
        faces.extend(outer.inset_faces_below(state))
        # append inner faces
        faces.append(outer.inset_side_north(state))
        faces.append(outer.inset_side_south(state))
        faces.append(outer.inset_side_above(state))
        faces.append(outer.inset_side_west(state))
        # else:
        #     # todo: add outside connections for non-inset cells
        #     # if show_outer_faces:
        #     #     faces.append(outer.side_north(state))
        #     #     faces.append(outer.side_south(state))
        #     # faces.append(outer.side_above(state))
        #     # faces.append(outer.side_east(state))
        #     pass
        return faces

    def outside_connection_east(self, state, show_outer_faces=False):
        outer = copy.copy(self)
        outer.col += 1
        faces = []
        # extend outer inset faces
        faces.extend(outer.inset_faces_west(state))
        faces.extend(outer.inset_faces_below(state))
        # append inner faces
        faces.append(outer.inset_side_north(state))
        faces.append(outer.inset_side_south(state))
        faces.append(outer.inset_side_above(state))
        faces.append(outer.inset_side_east(state))
        # else:
        #     # todo: add outside connections for non-inset cells
        #     # if show_outer_faces:
        #     #     faces.append(outer.side_north(state))
        #     #     faces.append(outer.side_south(state))
        #     # faces.append(outer.side_above(state))
        #     # faces.append(outer.side_west(state))
        #     pass
        return faces

    def outside_connection_north(self, state, show_outer_faces=False):
        outer = copy.copy(self)
        outer.row -= 1
        faces = []
        # extend outer inset faces
        faces.extend(outer.inset_faces_south(state))
        faces.extend(outer.inset_faces_below(state))
        # append inner faces
        faces.append(outer.inset_side_north(state))
        faces.append(outer.inset_side_above(state))
        faces.append(outer.inset_side_west(state))
        faces.append(outer.inset_side_east(state))
        # else:
        #     # todo: add outside connections for non-inset cells
        #     # if show_outer_faces:
        #     #     faces.append(outer.side_north(state))
        #     #     faces.append(outer.side_above(state))
        #     # faces.append(outer.side_west(state))
        #     # faces.append(outer.side_east(state))
        #     pass
        return faces

    def outside_connection_south(self, state, show_outer_faces=False):
        outer = copy.copy(self)
        outer.row += 1
        faces = []
        # extend outer inset faces
        faces.extend(outer.inset_faces_north(state))
        faces.extend(outer.inset_faces_below(state))
        # append inner faces
        faces.append(outer.inset_side_south(state))
        faces.append(outer.inset_side_above(state))
        faces.append(outer.inset_side_west(state))
        faces.append(outer.inset_side_east(state))
        # else:
        #     # todo: add outside connections for non-inset cells
        #     # if show_outer_faces:
        #     #     faces.append(outer.side_south(state))
        #     #     faces.append(outer.side_above(state))
        #     # faces.append(outer.side_west(state))
        #     # faces.append(outer.side_east(state))
        #     pass
        return faces

    def outside_connections(self, face, rows, cols, state, show_outer_faces=False):
        faces = []
        match face:
            case 4:
                if self.col == 0 and self.linked_west():
                    faces.extend(self.outside_connection_west(state))
                if self.row == 0 and self.linked_north():
                    faces.extend(self.outside_connection_north(state))
                if self.col == cols - 1 and self.linked_east():
                    faces.extend(self.outside_connection_east(state))
                if self.row == rows - 1 and self.linked_south():
                    faces.extend(self.outside_connection_south(state))
                pass
            case 5:
                pass
            case _:
                if self.col == cols - 1 and self.linked_east():
                    faces.extend(self.outside_connection_east(
                        state, show_outer_faces))
                if self.row == rows - 1 and self.linked_south():
                    faces.extend(self.outside_connection_south(
                        state, show_outer_faces))
        return faces


def vert_pos(row, col, level):
    return (row, -col, level)
