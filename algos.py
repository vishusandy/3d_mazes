import random
random.seed(7331)


def growing_tree(grid, choose_active=None, find_available_neighbors=None, choose_neighbor=None, start=None):
    if choose_active == None:
        choose_active = choose_active_random_cell
    if start == None:
        start = grid.random_cell()
    if choose_neighbor == None:
        choose_neighbor = choose_random_neighbor
    if find_available_neighbors == None:
        find_available_neighbors = list_all_available_neighbors
    cell = start
    active = []
    active.append(cell.id)
    iteration = 0
    while len(active) > 0:
        chosen = choose_active(grid, active, cell.level)
        cell = grid.lookup(chosen)
        available = find_available_neighbors(grid, cell, cell.level)
        if len(available) > 0:
            neighbor = choose_neighbor(grid, cell, available, cell.level)
            grid.link(cell.id, neighbor)
            active.append(neighbor)
        else:
            active.remove(cell.id)
        iteration += 1


def growing_tree_3d(grid, find_available_neighbors=None):
    if find_available_neighbors == None:
        find_available_neighbors = list_same_level_available_neighbors
    for i in range(grid.levels):
        start = grid.random_cell_on_level(i)
        growing_tree(
            grid, find_available_neighbors=find_available_neighbors, start=start)
        cell = grid.random_cell_on_level(i)
        if cell.above:
            grid.link(cell.id, cell.above)


def choose_same_level_random_neighbor(grid, cell, available, level=None):
    choices = list(filter(lambda a: grid.lookup(a).level == level, available))
    random.choice(choices)


def choose_active_random_cell(grid, active, level=None):
    return random.choice(active)


def choose_active_random_cell_same_level(grid, active, level=None):
    if level:
        return random.choice(list(filter(lambda n: grid.lookup(n).level == level, active)))
    else:
        return choose_active_random_cell(grid, active, level)


def list_all_available_neighbors(grid, cell, level=None):
    return list(filter(lambda n: not grid.lookup(n).has_links(), cell.neighbors()))


def list_same_level_available_neighbors(grid, cell, level=None):
    return list(filter(lambda n: grid.lookup(n).level == level and not grid.lookup(n).has_links(), cell.neighbors()))


def choose_random_neighbor(grid, cell, available, level=None):
    return random.choice(available)
