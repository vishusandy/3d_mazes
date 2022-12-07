import bpy

from .maze2d import RectGrid
from .maze3d import RectCell3d, VertState
from .cube import Cube, center_maze
from .utils.transform import *
from .utils.blender import new_mesh_obj, join_meshes

from PIL import ImageFont


class CubeCell(RectCell3d):
    def __init__(self, grid, id, row, col, level, weight=1, clear=False):
        self.id = id
        self.row = row
        self.col = col
        self.level = level
        self.weight = weight
        self.calc_neighbors(grid)
        self.links = [] if not clear else list[filter(
            lambda d: d != None, [self.north, self.east, self.south, self.west])]
        pass

    def calc_neighbors(self, grid):
        n = self.id - grid.cols
        e = self.id + 1
        s = self.id + grid.cols
        w = self.id - 1
        self.north = n if self.row > 0 else None
        self.east = e if not self.col >= grid.cols - 1 else None
        self.south = s if not self.row >= grid.rows - 1 else None
        self.west = w if self.col > 0 else None

        last_row = grid.rows - 1
        last_col = grid.cols - 1
        levels = grid.levels
        rows = grid.rows
        cols = grid.cols
        cap = grid.levels * grid.rows * grid.cols
        last_id = cap - 1

        c = grid.calc_id
        row = self.row
        col = self.col
        level = self.level
        match level:
            case 0:
                if col == 0:
                    self.west = c(3, row, last_col)
                if col == last_col:
                    self.east = c(1, row, 0)
                if row == 0:
                    self.north = c(4, col, 0)
                if row == last_row:
                    self.south = c(5, cols-col-1, 0)
            case 1:
                if col == 0:
                    self.west = c(0, row, last_col)
                if col == last_col:
                    self.east = c(2, row, 0)
                if row == 0:
                    self.north = c(4, last_row, col)
                if row == last_row:
                    self.south = c(5, 0, col)
            case 2:
                if col == 0:
                    self.west = c(1, row, last_col)
                if col == last_col:
                    self.east = c(3, row, 0)
                if row == 0:
                    self.north = c(4, cols - col - 1, last_col)
                if row == last_row:
                    self.south = c(5, col, last_col)
            case 3:
                if col == 0:
                    self.west = c(2, row, last_col)
                if col == last_col:
                    self.east = c(0, row, 0)
                if row == 0:
                    self.north = c(4, 0, cols - 1 - col)
                if row == last_row:
                    self.south = c(5, last_row, cols - col - 1)
            case 4:
                if col == 0:
                    self.west = c(0, 0, row)
                if col == last_col:
                    self.east = c(2, 0, rows - row - 1)
                if row == 0:
                    self.north = c(3, 0, cols - col - 1)
                if row == last_row:
                    self.south = c(1, 0, col)
            case 5:
                if col == 0:
                    self.west = c(0, last_row, rows - row - 1)
                if col == last_col:
                    self.east = c(2, last_row, row)
                if row == 0:
                    self.north = c(1, last_row, col)
                if row == last_row:
                    self.south = c(3, last_row, cols - col - 1)

    def neighbors(self):
        return list(filter(lambda d: not d is None, [
            self.north, self.east, self.south, self.west]))

    def neighbors_3d(self):
        self.neighbors()


class OuterCube(Cube):
    col_block = RectGrid.col_block
    col_border = RectGrid.col_border
    col_grid = RectGrid.col_grid
    col_text = RectGrid.col_text
    col_above = (255, 192, 0, 255)
    col_below = (255, 98, 0, 255)
    col_above_and_below = (192, 255, 0, 255)

    def __init__(self, rows=10, cols=10, weight=1, masked=False, clear=False):
        assert rows == cols
        self.levels = 6
        super().__init__(rows, cols, self.levels, weight, masked, clear, inset=0)
        self.cells = []
        for level in range(6):
            for row in range(rows):
                for col in range(cols):
                    id = self.calc_id(level, row, col)
                    self.cells.append(
                        CubeCell(self, id, row, col, level, weight, clear))

    def calc_id(self, level, row, col):
        return self.rows * self.cols * level + row * self.cols + col

    def wrap_neighbors(self):
        pass

    def lookup(self, id):
        return self.cells[id]

    def get(self, level, row, col):
        return self.cells[level*self.rows*self.cols + row * self.cols + col]

    def render2d(self, filename, block_size=70, frame_size=10, border_color=col_border, block_color=col_block, grid_bg=col_grid, text_color=col_text, show_labels=True, font=ImageFont.truetype("assets/DejaVuSansMono.ttf", 12)):
        cap = self.rows * self.cols
        for level in range(self.levels):
            parts = filename.rpartition(".")
            file = f'{parts[0]}_{level}{parts[1]}{parts[2]}'
            cells = self.cells[level*cap:level*cap+cap]

            custom_bgs = {}
            custom_text = {}

            RectGrid.render2d(self, file, block_size, frame_size, border_color,
                              block_color, grid_bg, text_color, show_labels, font, cells, custom_bgs, custom_text)

    def split_cube(self, inset=0.25):
        if inset < 0.05:
            inset = 0.05
        grids = []
        cap = self.rows * self.cols
        for face in range(6):
            cells = self.cells[face*cap:face*cap+cap]
            cells = list(
                map(lambda cell: cell.flatten_cell(inset), cells))
            grid = OuterCubePlane(face=face, rows=self.rows,
                                  cols=self.cols, inset=inset, cells=cells)
            grids.append(grid)
        return tuple(grids)


class OuterCubePlane(Cube):
    def __init__(self, face: int, rows=10, cols=10, weight=1, masked=False, clear=False, inset=0, cells=None):
        super().__init__(rows, cols, 1, weight, masked, clear, inset, cells)
        self.face = face

    def generate_cube_face(self, show_outer_faces=False):
        # NOTE: show_outer_faces is ignored if `inset == 0`
        state = VertState()
        faces = []

        if self.inset != 0:
            for cell in self.cells:
                for dir in ['above', 'below', 'north', 'east', 'south', 'west']:
                    f = cell.draw_inset(dir, state)
                    faces.extend(f)
                faces.extend(cell.outside_connections(
                    self.face, self.rows, self.cols, state))
        else:
            for cell in self.cells:
                if cell.show_above_wall() and (cell.level != self.levels - 1 or show_outer_faces == True):
                    faces.append(cell.inset_side_above(state))
                if cell.show_north_wall() and (cell.row != 0 or show_outer_faces == True):
                    faces.append(cell.inset_side_north(state))
                if cell.show_east_wall() and (cell.col != self.cols - 1 or show_outer_faces == True):
                    faces.append(cell.inset_side_east(state))
                if cell.row == self.rows - 1 and show_outer_faces:
                    faces.append(cell.inset_side_south(state))
                if cell.col == 0 and show_outer_faces:
                    faces.append(cell.inset_side_west(state))
                faces.extend(cell.outside_connections(
                    self.face, self.rows, self.cols, state))
        return (state.verts, faces)


def create_outer_cube(cube: OuterCube, name="outer_cubic_maze", show_outer_faces=False, joined=True, inner_cube=True, inset=0.0):
    grids = cube.split_cube(inset)
    assert len(grids) == 6
    assert grids[0].rows == grids[1].cols
    for i in range(5):
        assert grids[i].rows == grids[i+1].rows
        assert grids[i].cols == grids[i+1].cols

    rows = grids[0].rows
    cols = grids[0].cols
    midx = cols / 2
    midy = rows / 2

    objs = []

    for i, grid in enumerate(grids):
        verts, faces = grid.generate_cube_face(show_outer_faces)
        verts = center_maze(grid, verts)
        verts = grid.reorient_cube_face(i, verts)
        mesh = new_mesh_obj(name+'__face_'+str(i), verts=verts, faces=faces)
        objs.append(mesh)
    if inner_cube:
        bpy.ops.mesh.primitive_cube_add(size=grids[0].rows)
        cube = bpy.context.selected_objects[0]
        cube.name = name + '__inner_cube'
        objs.append(cube)
    if not joined:
        return objs
    else:
        join_meshes(objs)
        return
