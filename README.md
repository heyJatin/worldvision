# WorldVision

A simple python package to calculate real world distance, angles, and coordinates between objects. This package uses camera's intrinsic and extrinsic parameters like field of view, camera's altitude, pitch, etc.

Checkout `examples/` folder for sample use case.

## Installation

`pipx install worldvision`

#### KNOWN ISSUES:
- get_2d_coords() does not work for special angles (90, -90, etc.)
- Some negative and positive values are not handled correctly.
- ZeroDivisionError is not handled in some cases.

#### TODO:
- Fix known issues.
- Add support for roll and yaw.
- Add support for other units.
- Add support for speed, velocity, acceleration, angular velocity, direction.
- Add other calibration methods.