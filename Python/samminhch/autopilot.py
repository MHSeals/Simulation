import asyncio
from mavsdk import System

from samminhch.simutils import ColorLogger

class AutoBoat:
    def __init__(self):
        self.vehicle = System()
        self.logger = ColorLogger()
        
    async def connect(self, address=None):
        await self.vehicle.connect(system_address="udp://:14540")
        self.logger.log_warn('Waiting for boat to connect...')
        async for state in self.vehicle.core.connection_state():
            if state.is_connected:
                self.logger.log_ok('Boat connected')
                break