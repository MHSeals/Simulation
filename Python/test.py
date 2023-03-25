import asyncio
from pymavlink import mavutil
import mavsdk

async def main():
    mavutil.mavlink_connection('/dev/ttyACM0') 
    pass


if __name__ == "__main__":
    asyncio.run(main())
