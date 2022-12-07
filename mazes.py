import os
import algos

from meshes.cube import Cube, create_cube
from meshes.outer_cube import OuterCube, create_outer_cube
from meshes.mobius import Mobius, create_mobius_strip


def new_outer_cube(rows=6, cols=6, inset=0.15, inner_cube=False, save_image=False):
    grid = OuterCube(rows=rows, cols=cols, clear=False)
    algos.growing_tree(grid)

    if save_image is True:
        grid.render2d(os.path.join(dir, 'outer_cube.png'), frame_size=0,
                      border_color=(0, 0, 0, 255),
                      block_color=(255, 255, 255, 0),
                      grid_bg=(255, 255, 255, 0),
                      text_color=(55, 55, 55, 100))

    return create_outer_cube(grid, show_outer_faces=False,
                             joined=True, inner_cube=inner_cube, inset=inset)


def new_cube(rows=6, cols=6, levels=6, clear=False, inset=0.15, show_outer_faces=False, save_image=False):
    grid = Cube(rows=rows, cols=cols,
                levels=levels, clear=clear, inset=inset)
    algos.growing_tree(grid)

    if save_image is True:
        grid.render2d(os.path.join(dir, 'cube.png'), frame_size=0,
                      border_color=(0, 0, 0, 255),
                      block_color=(255, 255, 255, 0),
                      grid_bg=(255, 255, 255, 0),
                      text_color=(55, 55, 55, 100))

    create_cube(grid, show_outer_faces=show_outer_faces)


def new_mobius(rows=108, cols=10, res=54, save_image=False):
    grid = Mobius(rows=rows, cols=cols, clear=False)
    algos.growing_tree(grid)

    if save_image is True:
        grid.render2d("imgs/mobius.png", frame_size=0,
                      border_color=(0, 0, 0, 255),
                      block_color=(255, 255, 255, 0),
                      grid_bg=(255, 255, 255, 0),
                      text_color=(55, 55, 55, 100))

    create_mobius_strip(grid, rows=rows, cols=cols,
                        minor_radius=2, height=0.05, smooth=True)
