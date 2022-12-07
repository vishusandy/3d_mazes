import bpy
import random

from .maze2d import RectGrid
from .maze3d import VertState, vert_pos, RectCell3d
from .utils.blender import new_mesh_obj
from .utils.transform import *

from PIL import ImageFont


class Cube(RectGrid):
    col_block = RectGrid.col_block
    col_border = RectGrid.col_border
    col_grid = RectGrid.col_grid
    col_text = RectGrid.col_text
    col_above = (255, 192, 0, 255)
    col_below = (255, 98, 0, 255)
    col_above_and_below = (192, 255, 0, 255)

    def __init__(self, rows=10, cols=10, levels=3, weight=1, masked=False, clear=False, inset=0, cells=None):
        assert inset >= 0 and inset <= 0.45
        self.inset = inset
        cap2d = rows * cols
        cap3d = cap2d * levels
        self.cap = cap3d
        self.cap2d = cap2d
        self.cap3d = cap3d
        self.rows = rows
        self.cols = cols
        self.levels = levels
        if cells == None:
            self.cells = []
            for level in range(levels):
                for row in range(rows):
                    for col in range(cols):
                        id = self.calc_id(row, col, level)
                        cell = RectCell3d(
                            rows, cols, levels, cap2d, cap3d, id, row, col, level, weight, masked, clear, inset)
                        self.cells.append(cell)
        else:
            self.cells = cells

    def calc_id(self, row, col, level):
        return level * self.cap2d + row * self.cols + col

    def get(self, row, col, level):
        return self.cells[self.calc_id(row, col, level)]

    def connect_above(self, cell, above):
        a = self.cells[above]
        b = self.cells[cell]
        if a.level - b.level == 1:
            b.above = above
            a.below = cell
        else:
            print(
                f'Could not link above (below={cell} with above={above}): incompatible levels')

    def connect_below(self, cell, below):
        a = self.cells[cell]
        b = self.cells[below]
        if abs(a.level - b.level) == 1:
            a.below = below
            b.above = cell
        else:
            print(
                f'Could not link below (below={below} with above={cell}): incompatible levels')

    def row(self, level, row):
        return filter(lambda cell: cell.level == level, super.row(self, row))

    def col(self, level, col):
        return filter(lambda cell: cell.level == level, super.col(self, col))

    def level(self, level):
        return filter(lambda cell: cell.level == level, self.cells)

    def random_cell(self):
        return random.choice(self.cells)

    def random_cell_on_level(self, level):
        return random.choice(list(filter(lambda cell: cell.level == level, self.cells)))

    def render2d(self, filename, block_size=70, frame_size=10, border_color=col_border, block_color=col_block, grid_bg=col_grid, text_color=col_text, show_labels=True, font=ImageFont.truetype("assets/DejaVuSansMono.ttf", 12)):
        for level in range(self.levels):
            parts = filename.rpartition(".")
            file = f'{parts[0]}_{level}{parts[1]}{parts[2]}'
            cells = list(self.level(level))

            custom_bgs = {}
            custom_text = {}

            for cell in filter(lambda c: c.linked_to(c.below), cells):
                custom_bgs[cell.id] = Cube.col_below
            for cell in filter(lambda c: c.linked_to(c.above), cells):
                custom_bgs[cell.id] = Cube.col_above if custom_bgs.get(
                    cell.id) == None else Cube.col_above_and_below

            RectGrid.render2d(self, file, block_size, frame_size, border_color,
                              block_color, grid_bg, text_color, show_labels, font, cells, custom_bgs, custom_text)

    def vertex_indicies(self):
        verts = []
        vdict = {}
        pos = 0
        for x in range(self.cols+1):
            for y in range(self.rows+1):
                for z in range(self.levels+1):
                    verts.append(vert_pos(x, y, z))
                    vdict[vert_pos(x, y, z)] = pos
                    pos += 1
        return (verts, vdict)

    # def generate_model_inset(self, show_outer_faces=False):
    def generate_model(self, show_outer_faces=False):
        # NOTE: show_outer_faces is ignored if `inset == 0`
        state = VertState()
        faces = []

        if self.inset != 0:
            for cell in self.cells:
                for dir in ['above', 'below', 'north', 'east', 'south', 'west']:
                    f = cell.draw_inset(dir, state)
                    faces.extend(f)
        else:
            for cell in self.cells:
                if cell.show_above_wall() and (cell.level != self.levels - 1 or show_outer_faces == True):
                    faces.append(cell.inset_side_above(state))
                if cell.show_north_wall() and (cell.row != 0 or show_outer_faces == True):
                    faces.append(cell.inset_side_north(state))
                if cell.show_east_wall() and (cell.col != self.cols - 1 or show_outer_faces == True):
                    faces.append(cell.inset_side_east(state))
                if cell.level == 0 and show_outer_faces:
                    faces.append(cell.inset_side_below(state))
                if cell.row == self.rows - 1 and show_outer_faces:
                    faces.append(cell.inset_side_south(state))
                if cell.col == 0 and show_outer_faces:
                    faces.append(cell.inset_side_west(state))

        return (state.verts, faces)

    # Takes a list of vertifices for a maze.  Verticies should be centered around (0,0,0)
    def reorient_cube_face(self, face: int, verts: list):
        offset = 0.5
        x = self.rows / 2 + offset
        y = self.cols / 2 + offset
        z = self.levels / 2 + offset
        match face:
            case 0:
                # rotate_yz_ccw
                # shift x by (1-(rows/2))
                # verts = list(map(lambda p: rotate_yz_ccw(p), verts))
                verts = map_verts(rotate_yz_ccw, verts)
                verts = move_y(verts, -x)
                return verts
            case 1:
                verts = map_verts(rotate_yz_ccw, verts)
                verts = move_y(verts, -x)
                verts = map_verts(rotate_xy_ccw, verts)
                return verts
            case 2:
                verts = map_verts(rotate_yz_ccw, verts)
                verts = move_y(verts, -x)
                verts = map_verts(rotate_xy_ccw, verts)
                verts = map_verts(rotate_xy_ccw, verts)
                return verts
            case 3:
                verts = map_verts(rotate_yz_ccw, verts)
                verts = move_y(verts, -y)
                verts = map_verts(rotate_xy_cw, verts)
                return verts
            case 4:
                verts = move_z(verts, x)
                verts = map_verts(rotate_xy_ccw, verts)
                return verts
            case 5:
                verts = move_z(verts, x)
                verts = map_verts(rotate_xy_ccw, verts)
                verts = map_verts(mirror_x, verts)
                verts = map_verts(mirror_z, verts)
                return verts


# Expects a grid starting at (0,0,0) and ending at (x, -y, z)
#   In other words: x and z are positive, y is inverted
def center_maze(grid: Cube, verts: list):
    ox = - (grid.cols / 2)
    oy = (grid.rows / 2)
    oz = - (grid.levels / 2)
    return list(map(lambda v: point_offset(v, ox, oy, oz), verts))


def create_cube(cube: Cube, name="cubic_maze", show_outer_faces=False):
    verts, faces = cube.generate_model(show_outer_faces)
    mesh = new_mesh_obj(name, verts=verts, faces=faces)
