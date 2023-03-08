import os
import subprocess
import psutil
import time
import shutil

SRC_DIR   = '/root/src/px4-autopilot'
BUILD_DIR = SRC_DIR + '/build/px4_sitl_default'
SITL_EXEC = BUILD_DIR + '/bin/px4'

os.environ['GAZEBO_PLUGIN_PATH']  = f':{BUILD_DIR}/build_gazebo-classic'
os.environ['GAZEBO_MODEL_PATH']   = f':{SRC_DIR}/Tools/simulation/gazebo-classic/sitl_gazebo-classic/models'
# os.environ['LD_LIBRARY_PATH']    += f':{BUILD_DIR}/build_gazebo-classic'
os.environ['PX4_SIM_MODEL']       = 'gazebo-classic_boat'

class EnvironmentManager:
    def __init__(self):
        self.define_models()
        self.define_physical_scales()
        self.kill_all_gz_processes()

    def start_simulation(self, scenario=1):
        self.spawn_gzserver()
        self.populate_scenario(scenario_number=scenario)
        self.spawn_gzclient()
        self.spawn_sitl()

    def define_models(self):
        self.base_path        = '/root/src/roboboat-models'
        self.world_file       = self.base_path + '/benderson_park.world'
        self.boat_model       = self.base_path + '/Boat/boat.sdf'
        self.red_buoy_model   = self.base_path + '/Buoy/red_buoy.sdf'
        self.green_buoy_model = self.base_path + '/Buoy/green_buoy.sdf'
        self.root_fs          = '/root/src/px4-autopilot/build/sitl_default/rootfs'
        subprocess.run(f'mkdir -p {self.root_fs}',
                       shell=True,
                       executable='/bin/bash')

    def kill_all_gz_processes(self):
        for proc in psutil.process_iter():
            if proc.name() in ['gazebo',
                               'gz',
                               'gzclient',
                               'gzserver',
                               'px4']:
                proc.kill()

    def purge_temp_dir(self):
        base = os.getcwd()
        # os.remove(base + '/dataman')
        # os.remove(base + '/parameters.bson')
        # os.remove(base + '/parameters_backup.bson')
        # shutil.rmtree(base + '/eeprom')
        # os.unlink(base + '/etc')
        shutil.rmtree(base + '/frames')
        shutil.rmtree(base + '/logs')
        # shutil.rmtree(base + '/log')
        # os.unlink(base + '/test_data')

    def spawn_gzserver(self, default_wait=3):
        command = ['gzserver', self.world_file]
        self.gzserver = subprocess.Popen(command)
        time.sleep(default_wait)

    def populate_scenario(self, scenario_number):
        if scenario_number == 1:
            buoy_locations = [((-self.min_buoy_dist, -self.gateway_gap/2),
                               (-self.min_buoy_dist,  self.gateway_gap/2)),
                              ((-self.min_buoy_dist - self.gateway_distance, -self.gateway_gap/2),
                               (-self.min_buoy_dist - self.gateway_distance,  self.gateway_gap/2))]
        elif scenario_number == 2:
            raise NotImplementedError
        elif scenario_number == 3:
            raise NotImplementedError
        elif scenario_number == 4:
            raise NotImplementedError
        elif scenario_number == 5:
            raise NotImplementedError
        elif scenario_number == 6:
            raise NotImplementedError
        else:
            raise NotImplementedError

        # spawn boat until success
        # could be dangerous...
        while True:
            try:
                subprocess.run((f'gz model '
                                f'--spawn-file={self.boat_model} '
                                f'--model-name=bote '
                                f'-z 1 '
                                f'-Y 3.14'),
                               shell=True,
                               executable='/bin/bash')
                break
            except subprocess.CalledProcessError as e:
                print(e.output)
                time.sleep(1)

        # spawn buoys
        red_count = 0
        green_count = 0
        for ((red_buoy_x, red_buoy_y),
             (green_buoy_x, green_buoy_y)) in buoy_locations:
            cmd = (f'gz model '
                   f'--spawn-file={self.red_buoy_model} '
                   f'--model-name=rbuoy{red_count} '
                   f'-x {red_buoy_x} '
                   f'-y {red_buoy_y} '
                   f'-z 1')
            subprocess.run(cmd, shell=True, executable='/bin/bash')

            cmd = (f'gz model '
                   f'--spawn-file={self.green_buoy_model} '
                   f'--model-name=rbuoy{green_count} '
                   f'-x {green_buoy_x} '
                   f'-y {green_buoy_y} '
                   f'-z 1')
            subprocess.run(cmd, shell=True, executable='/bin/bash')

            green_count += 1
            red_count += 1

    def spawn_gzclient(self):
        command = ['nice',
                   '-n',
                   '20',
                   'gzclient',
                   '--gui-client-plugin',
                   'libgazebo_user_camera_plugin.so']
        self.gzclient = subprocess.Popen(command)

    def spawn_sitl(self):
        self.previous_dir = os.getcwd()
        os.chdir(self.root_fs)
        self.sitl = subprocess.Popen([SITL_EXEC,
                                      '-d',
                                      '/root/src/px4-autopilot/build/px4_sitl_default/etc'])
        try:
            return self.sitl.wait()
        except KeyboardInterrupt as e:
            self.sitl.kill()
            os.chdir(self.previous_dir)
            self.gzclient.kill()
            self.gzserver.kill()
            self.kill_all_gz_processes()
            self.purge_temp_dir()

    def define_physical_scales(self):
        # boat is actually 6m long by 2m wide
        # competition max is 6ft long by 3ft wide
        # competition max is 1.8288m long by 0.9144m wide
        # so to make comparable scaling
        self.width_scale = 2.0 / 0.9144
        self.length_scale = 6.0 / 1.8288

        # each gateway is between 6 to 10 ft wide
        # that's about 1.8288 to 3.048m wide
        self.gateway_gap = self.width_scale * 1.8288  # technically narrowest gate

        # second gateway is between 25 to 100 ft away
        # that's about 7.62 to 30.48m away
        self.gateway_distance = self.length_scale * 15.24 # 50ft away

        # buoys are at least 6 ft away from boat
        # that's about 1.8288m away
        # TODO: spawn using Lat/Long instead of meters from x=0, y=0
        self.min_buoy_dist = self.length_scale * 1.8288


class ColorLogger:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"
    
    def log(self, msg: str):
        output = ''
        output += f'[LOG]   {msg}'
        output += ColorLogger.END
        print(output)

    def log_error(self, msg: str):
        output = ''
        output += ColorLogger.RED
        output += f'[ERROR] {msg}'
        output += ColorLogger.END
        print(output)

    def log_warn(self, msg: str):
        output = ''
        output += ColorLogger.YELLOW
        output += f'[WARN]  {msg}'
        output += ColorLogger.END
        print(output)

    def log_debug(self, msg: str):
        output = ''
        output += ColorLogger.BLUE
        output += f'[DEBUG] {msg}'
        output += ColorLogger.END
        print(output)
        
    def log_ok(self, msg: str):
        output = ''
        output += ColorLogger.GREEN
        output += f'[OK]    {msg}'
        output += ColorLogger.END
        print(output)

# ---------------------------------------------------------------------------- #
#                                   CODE DUMP                                  #
# ---------------------------------------------------------------------------- #

# if verbose:
#     self.logger.log_debug('Environment Variables ' + '=' * 30)
#     self.logger.log_debug(f'SRC_DIR={self.src}')
#     self.logger.log_debug(f'BUILD_DIR={self.build}')
#     self.logger.log_debug(f'GAZEBO_PLUGIN_PATH={self.env["GAZEBO_PLUGIN_PATH"]}')
#     self.logger.log_debug(f'GAZEBO_MODEL_PATH={self.env["GAZEBO_MODEL_PATH"]}')
#     self.logger.log_debug(f'LD_LIBRARY_PATH={self.env["LD_LIBRARY_PATH"]}')
#     self.logger.log_debug(f'WORLD={self.world_file}')
#     self.logger.log_debug(f'BOAT_MODEL={self.boat_model}')
#     self.logger.log_debug(f'RED_BUOY_MODEL={self.red_buoy_model}')
#     self.logger.log_debug(f'GREEN_BUOY_MODEL={self.green_buoy_model}')
#     self.logger.log_debug(f'ROOT_FS={self.root_fs}')
#     self.logger.log_debug('=' * (len('Environment Variables ') + 30))
