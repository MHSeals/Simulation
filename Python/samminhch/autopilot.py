import time
import asyncio
from typing import Optional, Tuple
from mavsdk import System
from mavsdk.offboard import PositionGlobalYaw, PositionNedYaw
from mavsdk.offboard import OffboardError, VelocityNedYaw, VelocityBodyYawspeed

from samminhch.simutils import ColorLogger
import samminhch.coordinate_helper as coords


class AutoBoat:
    """This is the main class to connect and send commands to the RoboBoat.
    There's a specific way to use this class.

    1. Create a variable for the class: `boat = AutoBoat()`
    2. Connect using the `connect()` function: `boat.connect()`
    3. Ready up the boat using the `ready()` function: `boat.ready()`
    4. Send commands to the boat. The reccomended use is within a try-catch block
    5. Unready the boat using the `unready()` function after the try-catch block: `boat.unready()`
    """

    def __init__(self, timeout_seconds=30):
        self.vehicle = System()
        self.logger = ColorLogger()
        self.__home_coordinates = ()
        self.__timeout_seconds = timeout_seconds

    async def connect(self, address='udp://:14540'):
        self.logger.log_warn('Waiting for boat to connect...')
        await self.vehicle.connect(system_address=address)
        async for state in self.vehicle.core.connection_state():
            if state.is_connected:
                self.logger.log_ok('Boat connected')
                break

        # set the boat's home coordinates after connecting
        self.__home_coordinates = await self.get_position()

    async def ready(self) -> bool:
        """Arms the boat and sets it to offboard mode. Returns whether
        operations were successful were not

        Returns:
            bool: True if boat was armed and in offboard mode, False if anything bad happens
        """
        arm = await self.arm()
        offboard = await self.enable_offboard()

        if not arm or not offboard:
            await self.unready()
            return False
        return True

    async def unready(self, rtl: bool = True):
        """This stops offboard mode on the boat, and disarms the boat. If
        there are any errors trying to disarm the boat, it will kill the boat.
        """
        armed = await self.is_armed()
        if not armed:
            return False

        try:
            if await self.vehicle.offboard.is_active():
                self.logger.log_warn("Stopping offboard mode")
                await self.vehicle.offboard.stop()
                self.logger.log_ok("Offboard mode disabled!")

            if rtl:
                # Make the boat navigate home
                self.logger.log_warn("Boat returning home")
                await self.return_home()
                self.logger.log_ok("Boat arrived home!")

            self.logger.log_warn("Disarming boat")
            await self.vehicle.action.land()
            self.logger.log_ok("Boat disarmed!")
        except Exception as e:
            self.logger.log_error(e)
            self.logger.log_error("Error occurred, killing boat!")
            await self.vehicle.action.kill()
            # send a signal to cut power to motors

    async def get_position(self) -> Tuple[float, float]:
        """Returns the boat's current geographic position

        Returns:
            Tuple[float, float]: The latitude and longitude of the boat, respectively
        """
        async for position in self.vehicle.telemetry.position():
            return (position.latitude_deg, position.longitude_deg)

    async def get_position_ned(self) -> Tuple[float, float, float]:
        """Returns the boat's current NED position

        Returns:
            Tuple[float, float]: The boat's north and east position in feet
        """
        north = -1
        east = -1
        speed = -1
        async for pos_vel_ned in self.vehicle.telemetry.position_velocity_ned():
            north = pos_vel_ned.position.north_m
            east = pos_vel_ned.position.east_m

            north_v = pos_vel_ned.velocity.north_m
            east_v = pos_vel_ned.velocity.east_m
            speed = (north_v ** 2 + east_v ** 2) ** 0.5
            break

        # convert these values to feet and return them
        meters_to_feet = 3.281
        return (north * meters_to_feet, east * meters_to_feet, speed)

    async def get_heading(self) -> float:
        """Returns the boat's current heading

        Returns:
            float: The boat's current heading from the ranges [0, 360]
        """
        async for heading in self.vehicle.telemetry.heading():
            return heading.heading_deg

    async def arm(self) -> bool:
        """Attempts to arm the boat. Cancels arming if it takes longer than
        self.__timeout_seconds.

        Returns:
            bool: The return state. True if the boat was armed, False if the boat could not be armed.
        """
        self.logger.log_warn("Arming the boat...")
        start_time = time.time()  # keep track of the time taken to arm
        async for health in self.vehicle.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                self.logger.log_ok('Global position state good')
                break
            if time.time() - start_time >= self.__timeout_seconds:
                self.logger.log_error(
                    f'Took longer than {self.__timeout_seconds} seconds to get a GPS lock. Cancelling arming...')
                return False

        try:
            await self.vehicle.action.arm()
            self.logger.log_ok('Boat armed!')
            return True
        except Exception as e:
            self.logger.log_error(str(e))
            return False

    async def is_armed(self):
        async for armed_status in self.vehicle.telemetry.armed():
            return armed_status

    async def forward(self, distance: float, heading: float = 0, error_bound: float = 1):
        """Make the boat move a certain distance in feet in a certain heading.
        If heading is not specified, then boat moves straight.

        Args:
            distance (float): The distance to move forward in feet 
            heading (float): The heading in degrees to turn
            error_bound (float): The distance to stop boat from moving
        """
        armed = await self.is_armed()
        if not armed:
            self.logger.log_error("Can't make boat move, it isn't armed...")
            return

        # calculate the new heading
        current = await self.get_heading()
        self.logger.log_debug(f"Current heading is {current:.2f} degrees")
        target = current + heading
        target = ((target % 360) + 360) % 360
        self.logger.log_debug(f"New heading is {target:.2f} degrees")

        # calculate the new coordinates
        alt_type = PositionGlobalYaw.AltitudeType.REL_HOME
        starting_position = await self.get_position()
        new_coords = coords.get_new_coordinate(
            starting_position, distance, target)

        # create the new PositionGlobalYaw
        new_pos_global = PositionGlobalYaw(
            new_coords[0], new_coords[1], 0, target, alt_type)

        # Tell the boat to go to the new PositionGlobalYaw
        current_position = await self.get_position()
        dist_to_goal = coords.coord_dist(new_coords, current_position)
        degree_delta = abs(current - target)
        direction = 'left' if target > 0 else 'right'
        self.logger.log_warn(
            f"Boat going to head to ({new_coords[0]:.4f}, {new_coords[1]:.4f})"
            f", {dist_to_goal:.2f} feet away @ {heading:.2f}° {direction}"
        )

        await self.vehicle.offboard.set_position_global(new_pos_global)

        while dist_to_goal > error_bound or degree_delta > 5:

            self.logger.log_debug(
                f'{dist_to_goal:05.2f} feet, {degree_delta:.2f}° from goal',
                beg='\r', end='')
            current_position = await self.get_position()
            degree_delta = abs(current - target)
            current = await self.get_heading()
            dist_to_goal = coords.coord_dist(new_coords, current_position)
            direction = 'left' if target > 0 else 'right'
            await asyncio.sleep(0.5)

        self.logger.log_ok("Operation complete!", beg='\n')

    async def get_flight_mode(self):
        async for flight_mode in self.vehicle.telemetry.flight_mode():
            return flight_mode

    async def enable_offboard(self) -> bool:
        """Enables offboard mode for the boat. Returns a boolean indicating
        whether the operation was successful

        Returns:
            bool: True if offboard was enabled, False otherwise
        """
        armed = await self.is_armed()
        if not armed:
            self.logger.log_error(
                "Tried to enable offboard when boat isn't armed. Canceling...")
            return False

        self.logger.log_warn("Enabling offboard mode...")
        try:
            await self.vehicle.offboard.set_position_ned(PositionNedYaw(0, 0, 0, 0))
            await self.vehicle.offboard.start()
            self.logger.log_ok("Offboard mode enabled!")
            return True
        except Exception as e:
            self.logger.log_error(str(e))
            return False

    async def return_home(self, error_bound: float = 5):
        await self.vehicle.action.return_to_launch()

        current_position = await self.get_position()
        dist_from_home = coords.coord_dist(
            current_position, self.__home_coordinates)
        while dist_from_home > error_bound:
            self.logger.log_debug(
                f'Distance from Home: {dist_from_home:05.2f} feet   ',
                beg='\r', end='')
            await asyncio.sleep(0.1)
            current_position = await self.get_position()
            dist_from_home = coords.coord_dist(
                current_position, self.__home_coordinates)

        self.logger.log_ok('Arrived home!', beg='\n')

    async def goto(self, latitude: float, longitude: float, heading: float = 0, error_bound: float = 5):
        # calculate the new heading
        current_heading = await self.get_heading()
        self.logger.log_debug(
            f"Current heading is {current_heading:.2f} degrees")
        target = current_heading + heading
        target = ((target % 360) + 360) % 360
        self.logger.log_debug(f"New heading is {target:.2f} degrees")

        # create the new PositionGlobalYaw
        alt_type = PositionGlobalYaw.AltitudeType.REL_HOME
        new_pos_global = PositionGlobalYaw(
            latitude, longitude, 0, target, alt_type)

        current_position = await self.get_position()
        dist_to_goal = coords.coord_dist(
            current_position, (latitude, longitude))
        direction = 'right' if heading > 0 else 'left'
        degree_delta = abs(target - current_heading)

        self.logger.log_warn(
            f"Boat going to head to ({latitude:.4f}, {longitude:.4f})"
            f", {dist_to_goal:.2f} feet away @ {heading:.2f}° {direction}"
        )

        await self.vehicle.offboard.set_position_global(new_pos_global)

        while dist_to_goal > error_bound:
            self.logger.log_debug(
                f'{dist_to_goal:05.2f} feet, {degree_delta:.2f}° from goal',
                beg='\r', end='')
            current_position = await self.get_position()
            degree_delta = abs(current_heading - target)
            current_heading = await self.get_heading()
            dist_to_goal = coords.coord_dist((latitude, longitude), current_position)
            direction = 'left' if target > 0 else 'right'
            await asyncio.sleep(0.5)

        self.logger.log_ok("Operation complete!", beg='\n')
        pass


class AutoBoat_Jerry:
    def __init__(self):
        self.vehicle = System()
        self.logger = ColorLogger()

    async def connect(self, address=None):
        self.logger.log_warn('Waiting for boat to connect...')
        await self.vehicle.connect(system_address='udp://:14540')
        async for state in self.vehicle.core.connection_state():
            if state.is_connected:
                self.logger.log_ok('Boat connected')
                break

    async def arm(self):
        async for health in self.vehicle.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                self.logger.log_ok('Global position estimate OK')
                break
        self.logger.log_warn('Arming the boat')
        await self.vehicle.action.arm()
        self.logger.log_ok('Boat armed')
        await asyncio.sleep(5)
        self.logger.log_ok('Ready for the zoomies!')

    async def disarm(self):
        self.logger.log_warn('Disarming the boat')
        # await self.vehicle.action.land()
        await self.vehicle.action.disarm()
        self.logger.log_ok('Boat disarmed')

    async def enable_offboard(self):
        self.logger.log_warn('Setting initial setpoint')
        await self.vehicle.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))
        self.logger.log_warn('Starting offboard')
        try:
            await self.vehicle.offboard.start()
        except OffboardError as error:
            self.logger.log_error(
                f'Starting offboard mode failed with error code: {error._result.result}')
            self.logger.log_error('Disarming')
            await self.vehicle.action.disarm()

    async def disable_offboard(self):
        self.logger.log_warn('Stopping offboard')
        try:
            await self.vehicle.offboard.stop()
        except OffboardError as error:
            print(
                f'Stopping offboard mode failed with error code: {error._result.result}')

    async def turn(self, heading):
        self.logger.log(f'Turning to heading {heading}')
        await self.vehicle.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, heading))
        await asyncio.sleep(5)

    async def set_velocity_ned_yaw(self, north, east, down, heading):
        ned = VelocityNedYaw(north, east, down, heading)
        await self.vehicle.offboard.set_velocity_ned(ned)
        await asyncio.sleep(5)

    async def set_position_ned_yaw(self, north, east, down, heading):
        ned = PositionNedYaw(north, east, down, heading)
        await self.vehicle.offboard.set_position_ned(ned)
        await asyncio.sleep(5)
