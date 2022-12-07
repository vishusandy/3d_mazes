from typing import Callable

# Rotations
#   https://calcworkshop.com/transformations/rotation-rules/
# rotations are around the center, (0, 0, 0)


def rotate_xy_ccw(p: tuple):
    x, y, z = p
    return (-y, x, z)


def rotate_xy_cw(p: tuple):
    x, y, z = p
    return (y, -x, z)


def rotate_xz_ccw(p: tuple):
    x, y, z = p
    return (-z, y, x)


def rotate_xz_cw(p: tuple):
    x, y, z = p
    return (z, y, -x)


def rotate_yz_ccw(p: tuple):
    x, y, z = p
    return (x, -z, y)


def roate_yz_cw(p: tuple):
    x, y, z = p
    return (x, z, -y)


def mirror_x(p: tuple):
    x, y, z = p
    return (-x, y, z)


def mirror_y(p: tuple):
    x, y, z = p
    return (x, -y, z)


def mirror_z(p: tuple):
    x, y, z = p
    return (x, y, -z)


def point_offset(p: tuple, ox, oy, oz):
    x, y, z = p
    return (x+ox, y+oy, z+oz)


# 180° rotation around xy
def flip_xy(p: tuple):
    x, y, z = p
    return (-y, -x, z)


# 180° rotation around xz
def flip_xz(p: tuple):
    x, y, z = p
    return (-z, y, -x)


# 180° rotation around yz
def flip_yz(p: tuple):
    x, y, z = p
    return (x, -z, -y)


def add_x(v: tuple, offset):
    return (v[0] + offset, v[1], v[2])


def add_y(v: tuple, offset):
    return (v[0], v[1] + offset, v[2])


def add_z(v: tuple, offset):
    return (v[0], v[1], v[2] + offset)


def move_x(verts: list, offset):
    return list(map(lambda v: add_x(v, offset), verts))
    # return list(map(lambda p: (p[0] + offset, p[1]. p[2]), verts))


def move_y(verts: list, offset):
    return list(map(lambda v: add_y(v, offset), verts))
    # return list(map(lambda p: (p[0], p[1] + offset. p[2]), verts))


def move_z(verts: list, offset):
    return list(map(lambda v: add_z(v, offset), verts))
    # return list(map(lambda p: (p[0], p[1]. p[2] + offset), verts))


def map_verts(func: Callable[[tuple], tuple], verts: list):
    return list(map(lambda v: func(v), verts))
