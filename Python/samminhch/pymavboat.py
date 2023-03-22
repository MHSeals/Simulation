from samminhch.simutils import ColorLogger
import time
from dronekit import connect, VehicleMode


class ScuffedBoat():
    def __init__(self, connection_string='0.0.0.0:14540', baud_rate=57600) -> None:
        """This constructor tries to connect the boat to the connection string. By
        default, this connects via serial '/dev/ttyACM0' with a baud rate of 57600.
        """
        self.logger = ColorLogger()
        self.vehicle = connect(connection_string)

        # seconds until program times out
        self.timeout = 30

    def arm(self) -> None:
        if self.vehicle.armed:
            self.logger.log_error(
                "Cannot arm boat if it's already armed... Cancelling action")
            return

        self.logger.log_warn("Setting offboard control...")
        self.vehicle.mode = VehicleMode("OFFBOARD")
        self.logger.log_ok("Offboard mode is a go!")

        self.logger.log_warn("Arming the boat...")
        self.vehicle.armed = True
        self.logger.log_ok("Boat armed!")

    def disarm(self) -> None:
        if not self.vehicle.armed:
            self.logger.log_error(
                "Cannot disarmed boat when it's not armed... Cancelling action")
            return

        self.logger.log_warn("Disarming boat...")
        self.vehicle.armed = False
        self.logger.log_ok("Boat disarmed!")

        # close the connection
        self.vehicle.close()

    def thruster(self, which_motor, power):
        # TODO: God I pray for your help :D
        pass
