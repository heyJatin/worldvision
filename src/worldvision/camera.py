from worldvision.calculations import calc_angle_ppixel

class Camera:
    def __init__(self,
                 altitude: float = 0.0,
                 pitch: float = 0.0, roll: float = 0.0, yaw: float = 0.0,
                 h_fov: float = 90.0, v_fov: float = 60.0,
                 frame_dimensions: tuple = (1920, 1080),
                 ):
        # Parameters set by the user
        self.altitude = altitude
        self.pitch, self.roll, self.yaw = pitch, roll, yaw
        self.h_fov, self.v_fov = h_fov, v_fov
        self.frame_dimensions = frame_dimensions

        # Check for unsupported values
        self.check_not_supported()

        # Calculate parameters
        self._calculate_parameters()

    def update_orientation(self,
                           altitude: float = 0.0,
                           pitch: float = 0.0, roll: float = 0.0, yaw: float = 0.0
                           ) -> None:
        """
        Updates the orientation of the camera.

        Parameters:
        - altitude (float): Altitude of the camera.
        - pitch (float): Pitch of the camera.
        - roll (float): Roll of the camera.
        - yaw (float): Yaw of the camera.

        Returns:
        None
        """
        self.altitude = altitude
        self.pitch, self.roll, self.yaw = pitch, roll, yaw

        if yaw or roll:
            self.check_not_supported()

        self._calculate_parameters()

    def update_frame_dimensions(self, width: int = 1920, height: int = 1080) -> None:
        """
        Updates the frame_dimensions of the camera.

        Parameters:
        - width (int): Width of the frame.
        - height (int): Height of the frame.

        Returns:
        None
        """
        self.frame_dimensions = (width, height)
        self._calculate_parameters()

    @property
    def coords(self) -> tuple:
        """
        Returns the coordinates of the camera in the real world.
        """
        return (0, self.altitude, 0)

    def check_not_supported(self):
        """
        Checks if the camera has any unsupported values.
        """
        
        if int(self.yaw) != 0 or int(self.roll) != 0:
            raise NotImplementedError("Non-zero values for Yaw and Roll are not supported yet.")

    def _calculate_parameters(self):
        """
        Calculates all the required parameters for further calculations.
        """

        # Calculate angle per pixel
        self.h_angle_ppixel, self.v_angle_ppixel = calc_angle_ppixel(self.h_fov, self.v_fov, self.frame_dimensions)

        # Calculate the center of the frame
        self.x_center_frame, self.y_center_frame = self.frame_dimensions[0] / 2, self.frame_dimensions[1] / 2
