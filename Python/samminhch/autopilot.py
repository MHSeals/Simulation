import time
import asyncio
from typing import Tuple
from mavsdk import System
from mavsdk.offboard import (PositionGlobalYaw, PositionNedYaw)
from mavsdk.offboard import (OffboardError, VelocityNedYaw)

from samminhch.simutils import ColorLogger


class AutoBoat:
    def __init__(self):
        self.vehicle = System()
        self.logger = ColorLogger()
        self.__armed = False
        self.__home_coordinates = ()
        self.__timeout_seconds = 30

    async def connect(self, address=None):
        self.logger.log_warn('Waiting for boat to connect...')
        await self.vehicle.connect(system_address="udp://:14540")
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
        self.logger.log_warn("Arming the boat")
        arm = await self.__arm()
        self.logger.log_warn("Enabling offboard mode")
        offboard = await self.__enable_offboard()

        if not arm or not offboard:
            await self.unready()
            return False
        return True

    async def unready(self):
        if not self.__armed:
            return False

        try:
            if await self.vehicle.offboard.is_active():
                self.logger.log_warn("Stopping offboard mode")
                await self.vehicle.offboard.stop()
                self.logger.log_ok("Offboard mode disabled!")

            self.logger.log_warn("Disarming boat")
            await self.vehicle.action.land()
            self.logger.log_ok("Boat disarmed!")
        except Exception as e:
            self.logger.log_error(e)
            self.logger.log_error("Error Occurred. Killing boat.!")
            await self.vehicle.action.kill()
            # send a signal to cut power to motors
        finally:
            self.__armed = False

    async def get_position(self) -> Tuple[float, float]:
        """Returns the boat's current geometric position

        Returns:
            Tuple[float, float]: The latitude and longitude of the boat, respectively
        """
        async for position in self.vehicle.telemetry.position():
            return (position.latitude_deg, position.longitude_deg)

    async def get_position_ned(self) -> Tuple[float, float]:
        """Returns the boat's current NED position

        Returns:
            Tuple[float, float]: The boat's north and east position in feet
        """
        async for pos_vel_ned in self.vehicle.telemetry.position_velocity_ned():
            north = pos_vel_ned.position.north_m
            east = pos_vel_ned.position.east_m
            break

        # convert these values to feet and return them
        meters_to_feet = 3.281
        return (north * meters_to_feet, east * meters_to_feet)

    async def get_heading(self) -> float:
        """Returns the boat's current heading

        Returns:
            float: The boat's current heading from the ranges [0, 360]
        """
        async for heading in self.vehicle.telemetry.heading():
            return heading.heading_deg
    

    async def __arm(self) -> bool:
        """Attempts to arm the boat. Cancels arming if it takes longer than
        self.__timeout_seconds.

        Returns:
            bool: The return state. True if the boat was armed, False if the boat could not be armed.
        """
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
            self.__armed = True
            return True
        except Exception as e:
            self.logger.log_error(e)
            return False

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
            self.logger.log_error(f'Starting offboard mode failed with error code: {error._result.result}')
            self.logger.log_error('Disarming')
            await self.vehicle.action.disarm()
            
    async def disable_offboard(self):
        self.logger.log_warn('Stopping offboard')
        try:
            await self.vehicle.offboard.stop()
        except OffboardError as error:
            print(f'Stopping offboard mode failed with error code: {error._result.result}')
    
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


