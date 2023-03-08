import time
from typing import Tuple
from mavsdk import System
from mavsdk.offboard import (PositionGlobalYaw, PositionNedYaw)

from samminhch.simutils import ColorLogger


class AutoBoat:
    def __init__(self):
        self.vehicle = System()
        self.logger = ColorLogger()
        self.__armed = False
        self.__home_coordinates = ()

    async def connect(self, address=None):
        await self.vehicle.connect(system_address="udp://:14540")
        self.logger.log_warn('Waiting for boat to connect...')
        async for state in self.vehicle.core.connection_state():
            if state.is_connected:
                self.logger.log_ok('Boat connected')
                break

    async def ready(self) -> bool:
        """Arms the boat and sets it to offboard mode. Returns whether
        operations were successful were not

        Returns:
            bool: True if boat was armed and in offboard mode, False if anything bad happens
        """
        arm = await self.__arm()
        offboard = await self.__enable_offboard()
        return arm and offboard

    async def unready(self):
        pass

    async def __enable_offboard(self) -> bool:
        if not self.__armed:
            self.logger.log_error(
                "Tried to enable offboard when boat isn't armed. Canceling...")
            return False

        position = await self.get_position()
        heading = await self.get_heading()
        self.__home_coordinates = position
        altitude_type = PositionGlobalYaw.AltitudeType.REL_HOME
        self.logger.log_debug(
            f'Position: ({position[0]:.3f}, {position[1]:.3f}) | Heading: {heading}')

        try:
            await self.vehicle.offboard.set_position_global(PositionGlobalYaw(position[0], position[1], 0, heading,), altitude_type)
            await self.vehicle.offboard.start()
            return True 
        except Exception as e:
            self.logger.log_error(e)
            return False

    async def __arm(self) -> bool:
        """Attempts to arm the boat. Cancels arming if it takes longer than
        30 seconds.

        Returns:
            bool: The return state. True if the boat was armed, False if the boat could not be armed.
        """

        start_time = time.time()  # keep track of the time taken to arm
        async for health in self.vehicle.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                self.logger.log_ok('Global position state good')
                break
            if time.time() - start_time >= 30:
                self.logger.log_error(
                    'Took longer than 30 seconds to get a GPS lock. Cancelling arming...')
                return False

        self.logger.log_warn('Arming boat...')
        try:
            await self.vehicle.action.arm()
            self.logger.log_ok('Boat armed!')
            self.__armed = True
            return True
        except Exception as e:
            self.logger.log_error(e)
            return False

    async def get_position(self) -> Tuple[float, float]:
        """Returns the boat's current geometric position

        Returns:
            Tuple[float, float]: The latitude and longitude of the boat, respectively
        """
        async for position in self.vehicle.telemetry.position():
            return (position.latitude_deg, position.longitude_deg)

    async def get_heading(self) -> float:
        """Returns the boat's current heading

        Returns:
            float: The boat's current heading from the ranges [0, 360]
        """
        async for heading in self.vehicle.telemetry.heading():
            return heading.heading_deg
