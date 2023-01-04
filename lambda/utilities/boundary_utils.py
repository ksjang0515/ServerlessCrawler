from constants import MINIMUM_DISTANCE


def boundary_to_bounds(boundary):
    return f"{boundary[0][0]:.7f};{boundary[0][1]:.7f};{boundary[1][0]:.7f};{boundary[1][1]:.7f}"


def bounds_to_boundary(bounds):
    boundary = bounds.split(";")
    return [
        [float(boundary[0]), float(boundary[1])],
        [float(boundary[2]), float(boundary[3])],
    ]


def create_child_boundary(bounds):
    boundary = bounds_to_boundary(bounds)

    length_x = round((boundary[1][0] - boundary[0][0]) / 2, 7)
    length_y = round((boundary[1][1] - boundary[0][1]) / 2, 7)

    # if distance is less than minimum distance
    if length_x < MINIMUM_DISTANCE or length_y < MINIMUM_DISTANCE:
        # print error and continue
        raise Exception("Minimum length has been reached")

    # create boundary
    boundary_NW = [
        [boundary[0][0], boundary[0][1] + length_y],
        [boundary[1][0] - length_x, boundary[1][1]],
    ]
    boundary_NE = [
        [boundary[0][0] + length_x, boundary[0][1] + length_y],
        [boundary[1][0], boundary[1][1]],
    ]
    boundary_SW = [
        [boundary[0][0], boundary[0][1]],
        [boundary[1][0] - length_x, boundary[1][1] - length_y],
    ]
    boundary_SE = [
        [boundary[0][0] + length_x, boundary[0][1]],
        [boundary[1][0], boundary[1][1] - length_y],
    ]

    childs = [
        boundary_to_bounds(boundary_NW),
        boundary_to_bounds(boundary_NE),
        boundary_to_bounds(boundary_SW),
        boundary_to_bounds(boundary_SE),
    ]

    return childs
