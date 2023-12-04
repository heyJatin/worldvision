import math

def calc_angle_ppixel(h_fov: float, v_fov: float, frame_dimensions: tuple) -> tuple:
    """
    Calculates the angle per pixel for both horizontal and vertical axes.

    Parameters:
    - h_fov (float): Horizontal field of view in degrees.
    - v_fov (float): Vertical field of view in degrees.
    - frame_dimensions (tuple): Tuple representing the frame dimensions (width, height).

    Returns:
    Tuple containing the angle per pixel for the horizontal and vertical axes.
    """

    # Get frame width and height
    frame_width, frame_height = frame_dimensions

    # Calculate angle per pixel
    h_angle_per_pixel = h_fov / frame_width
    v_angle_per_pixel = v_fov / frame_height

    return h_angle_per_pixel, v_angle_per_pixel

def calc_distance(point_1: tuple, point_2: tuple) -> float:
    """
    Calculates the distance between two points in the real world.

    Parameters:
    - point_1 (tuple): Tuple representing the first point (x, y, z).
    - point_2 (tuple): Tuple representing the second point (x, y, z).

    Returns:
    Distance between the two points in the real world.
    """
    
    # Get x, y, and z values
    x_1, y_1, z_1 = point_1
    x_2, y_2, z_2 = point_2

    # Calculate distance
    distance = math.sqrt((x_2 - x_1)**2 + (y_2 - y_1)**2 + (z_2 - z_1)**2)

    return distance

def calc_angle(point_1: tuple, point_2: tuple, point_3: tuple) -> float:
    """
    Calculates the angle between three points in the real world.
    The angle is being formed at point_2 between two lines:
    - Line 1: point_1 to point_2
    - Line 2: point_2 to point_3

    Parameters:
    - point_1 (tuple): Tuple representing the first point (x, y, z).
    - point_2 (tuple): Tuple representing the second point (x, y, z).
    - point_3 (tuple): Tuple representing the third point (x, y, z).

    Returns:
    Angle between the three points in the real world.
    """
    
    # Get x, y, and z values
    x_1, y_1, z_1 = point_1
    x_2, y_2, z_2 = point_2
    x_3, y_3, z_3 = point_3

    # Calculate vectors
    vector_1 = [x_1 - x_2, y_1 - y_2, z_1 - z_2]
    vector_2 = [x_3 - x_2, y_3 - y_2, z_3 - z_2]

    # Manually calculate the dot product
    dot_product = sum(v1 * v2 for v1, v2 in zip(vector_1, vector_2))

    # Manually calculate the magnitudes (norms) of both vectors
    magnitude_1 = math.sqrt(sum(coord**2 for coord in vector_1))
    magnitude_2 = math.sqrt(sum(coord**2 for coord in vector_2))

    # Calculate the angle in radians and then convert to degrees
    angle_radians = math.acos(dot_product / (magnitude_1 * magnitude_2))
    angle_degrees = math.degrees(angle_radians)

    return angle_degrees

def get_3d_coords(camera: object, point_2d: tuple, point_height: float = 0.0) -> tuple:
    """
    Calculates the 3D coordinates (x, y, z) of a point in the real world.
    The x-axis is horizontal (left and right),
    the y-axis is vertical (up and down),
    and the z-axis is depth (forwards and backwards).
    For example,
    (0, camera.altitude, 0): This is the exact coordinate of camera.
    (0, 0, 0): Origin, the point on ground where camera is mounted.

    Parameters:
    - point_2d (tuple): Tuple representing the 2D point (x, y) on frame.
    - camera (object): Camera object.
    - point_height (float): Height of point from the ground, 0 if the point is on ground.

    Returns:
    Tuple representing the 3D coordinates of the point (x, y, z).
    """

    # Get 2D point coordinates
    x_2d, y_2d = point_2d

    # Calculate the angle difference from the center of the frame
    delta_x_angle = (camera.x_center_frame - x_2d) * camera.h_angle_ppixel
    delta_y_angle = (camera.y_center_frame - y_2d) * camera.v_angle_ppixel

    # Calculate the angle from the camera's forward direction
    angle_from_forward_x = delta_x_angle
    angle_from_forward_y = camera.pitch - delta_y_angle

    # Calculate the horizontal (x) and depth (z) components

    # calculate distance from x-axis to line of horizon (in meters)
    loh = 3569.72 * math.sqrt(camera.altitude) # Source: https://sites.math.washington.edu/~conroy/m120-general/horizon.pdf
    
    # Calculate the distance on the ground plane from the camera to the point
    try:
        ground_distance = (camera.altitude - point_height) / math.tan(math.radians(angle_from_forward_y))
        # keep ground_distance less than or equal to line of horizon
        if ground_distance > loh:
            ground_distance = loh
    except ZeroDivisionError:
        # Object is on the line of horizon
        ground_distance = loh
    x_3d = ground_distance * math.tan(math.radians(angle_from_forward_x))
    z_3d = ground_distance

    # The y-coordinate is the given point_height
    y_3d = point_height

    return x_3d, y_3d, z_3d

def get_2d_coords(camera: object, point_3d: tuple) -> tuple:
    """
    Calculates the 2D coordinates (x, y) of a point on the frame.
    The x-axis is horizontal (left and right),
    the y-axis is vertical (up and down).
    For example,
    (0, 0): Top-left corner of the frame.
    (640, 480): Bottom-right corner of the frame.

    Parameters:
    - point_3d (tuple): Tuple representing the 3D point (x, y, z) in the real world.

    Returns:
    Tuple representing the 2D coordinates of the point (x, y) on frame.
    """
    
    # Get 3D point coordinates
    x_3d, y_3d, z_3d = point_3d

    # Calculate the angle from the camera's forward direction
    angle_from_forward_x = math.degrees(math.atan(x_3d / z_3d))
    angle_from_forward_y = math.degrees(math.atan((y_3d - camera.altitude) / z_3d)) + camera.pitch

    # Calculate the angle difference from the center of the frame
    delta_x_angle = angle_from_forward_x
    delta_y_angle = angle_from_forward_y  # Here we just use the angle from the forward direction

    # Calculate the pixel difference from the center of the frame
    delta_x_pixel = delta_x_angle / camera.h_angle_ppixel
    delta_y_pixel = delta_y_angle / camera.v_angle_ppixel

    # Calculate the pixel coordinates correcting the sign for y-axis
    x_2d = camera.x_center_frame - delta_x_pixel
    y_2d = camera.y_center_frame - delta_y_pixel  # Corrected to subtract delta_y_pixel

    return x_2d, y_2d