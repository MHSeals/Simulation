import os
import subprocess
import psutil
import time
import shutil
import numpy as np

from typing import Union, Tuple

SRC_DIR   = '/root/src/px4-autopilot'
BUILD_DIR = SRC_DIR + '/build/px4_sitl_default'
SITL_EXEC = BUILD_DIR + '/bin/px4'
SITL_SUPP = BUILD_DIR + '/etc'
ROOT_FS   = SRC_DIR + '/build/sitl_default/rootfs'

os.environ['GAZEBO_PLUGIN_PATH']  = f':{BUILD_DIR}/build_gazebo-classic'
os.environ['GAZEBO_MODEL_PATH']   = f':{SRC_DIR}/Tools/simulation/gazebo-classic/sitl_gazebo-classic/models'
os.environ['LD_LIBRARY_PATH']    += f':{BUILD_DIR}/build_gazebo-classic'
os.environ['PX4_SIM_MODEL']       = 'gazebo-classic_boat'

class EnvironmentManager:
    def __init__(self, world_file: str = 'benderson_park', debug: bool = False) -> None:
        """
        Generalized Gazebo manager instead of the previously used spawn_env.bash

        Args:
            world_file (str, optional): Name of world file to spawn gzserver. Defaults to 'benderson_park'.
            debug (bool, optional): Debug output. Defaults to False.
        """

        # mildly easier to read logger
        self.logger = ColorLogger()

        # verbose output
        self.verbose = debug

        # all necessary models
        self.models = {'red_buoy'    : '/root/src/roboboat-models/Buoy/red_buoy.sdf',
                       'green_buoy'  : '/root/src/roboboat-models/Buoy/green_buoy.sdf',
                       'yellow_buoy' : '/root/src/roboboat-models/Buoy/yellow_buoy.sdf',
                       'black_buoy'  : '/root/src/roboboat-models/Buoy/black_buoy.sdf',
                       'boat'        : '/root/src/roboboat-models/Boat/boat.sdf'}

        # keep track for naming
        self.model_counts = {'red_buoy'    : 0,
                             'green_buoy'  : 0,
                             'yellow_buoy' : 0,
                             'black_buoy'  : 0,
                             'boat'        : 0}

        # for checking valid color
        self.supported_color = ['red', 'green', 'yellow', 'black']

        # world file we're using
        self.world_name = world_file
        self.world_file = f'/root/src/roboboat-models/{world_file}.world'

        # this is basically enlarging everything by a factor
        # meaning the world is now in ft
        self.width_scale   = 2.187226596675416 # 2 / 0.9144
        self.length_scale  = 3.280839895013123 # 6 / 1.8288
        self.gate_distance = 6

        # in case we need to kill halfway
        self.gz_server = None
        self.gz_client = None

        # for cleaning up
        self.gz_kill_list = ['gazebo', 'gz', 'gzclient', 'gzserver', 'px4']

        # debug outputs
        if self.verbose:
            self.logger.log_debug(f'GAZEBO_PLUGIN_PATH = {os.environ["GAZEBO_PLUGIN_PATH"]}')
            self.logger.log_debug(f'GAZEBO_MODEL_PATH  = {os.environ["GAZEBO_MODEL_PATH"]}')
            self.logger.log_debug(f'LD_LIBRARY_PATH    = {os.environ["LD_LIBRARY_PATH"]}')
            self.logger.log_debug(f'PX4_SIM_MODEL      = {os.environ["PX4_SIM_MODEL"]}')
            for key, value in self.models.items():
                self.logger.log_debug(f'{key.upper() + "_MODEL":<18} = {value}')
            self.logger.log_debug(f'WORLD_FILE         = {self.world_file}')

    def start_simulation(self, task=1, headless=False):
        self.spawn_gzserver()
        self.spawn_vehicle()
        self.populate_scenario(task=task)
        if not headless:
            self.spawn_gzclient()
        self.spawn_sitl()

    def purge_temp_dirs(self) -> None:
        """Delete misc files generated by px4 process."""
        self.logger.log_warn('Deleting misc directories...')
        base = os.getcwd()
        path1 = base + '/frames'
        path2 = base + '/logs'
        if self.verbose:
            self.logger.log_debug(f'Deleting {path1}')
            try:
                shutil.rmtree(path1)
            except FileNotFoundError as e:
                self.logger.log_debug(e)
            self.logger.log_debug(f'Deleting {path2}')
            try:
                shutil.rmtree(path2)
            except FileNotFoundError as e:
                self.logger.log_debug(e)
        else:
            try:
                shutil.rmtree(path1)
            except FileNotFoundError as _:
                pass
            try:
                shutil.rmtree(path2)
            except FileNotFoundError as _:
                pass
        self.logger.log_ok('Done!')

    def kill_gazebo_subprocesses(self) -> None:
        """Kill all remaining background processes related to Gazebo or PX4 SITL."""
        self.logger.log_warn('Killing all gazebo subprocesses...')
        for proc in psutil.process_iter():
            if (pname:=proc.name()) in self.gz_kill_list:
                if self.verbose:
                    self.logger.log_debug(f'Killing {pname}...')
                proc.kill()
        self.logger.log_ok('All gazebo subprocesses killed!')

    def spawn_gzserver(self, wait:int = 3) -> None:
        """Start gzserver in the background.

        Args:
            wait (int, optional): Delay in seconds for gzserver to come up. Defaults to 3.
        """
        self.logger.log_warn(f'Starting gzserver with world file')
        if self.verbose:
            command = ['gzserver', '--verbose', self.world_file]
            self.logger.log_debug(f'COMMAND = {str(command)}')
        else:
            command = ['gzserver', self.world_file]
        self.gz_server = subprocess.Popen(command)
        self.logger.log_warn(f'Waiting for {wait} seconds for gzserver to come up...')
        time.sleep(wait)
        self.logger.log_ok('gzserver started!')

    def spawn_vehicle(self, wait: Union[int, float] = 0.5, retries:int = 20) -> None:
        """Attempting to spawn the boat into gzserver.

        Args:
            wait (Union[int, float], optional): Delay in seconds between each spawn attempt. Defaults to 0.5.
            retries (int, optional): Number of retries attempt. Defaults to 20.
        """
        self.logger.log_warn('Spawning boat model into gzserver')
        for i in range(retries):
            try:
                if self.verbose:
                    self.logger.log_debug(f'Attemp {i+1:>2} to spawn boat...')
                subprocess.run((f'gz model '
                                f'--spawn-file={self.models["boat"]} '
                                f'--model-name=bote '
                                f'-z 1 '
                                f'-Y 3.14'),
                               shell=True,
                               executable='/bin/bash')
                # if self.verbose:
                #     self.model_counts["boat"] = self.model_counts["boat"] + 1
                #     self.logger.log_debug(f'self.model_counts["boat"] is now {self.model_counts["boat"]}')
                break
            except subprocess.CalledProcessError as e:
                self.logger.log_error('Unable to communicate with gzserver')
            time.sleep(wait)
        self.logger.log_ok('Vehicle (bote) is spawned!')

    def spawn_buoy(self, location: Tuple[float, float], color: str) -> None:
        """Spawn a buoy of certain color at specified location.

        Args:
            location (Tuple[float, float]): x, y coordinate of the buoy relative to (0, 0).
            color (str): Color of the buoy. Currently suppored [red, green, yellow, black].
        """

        if color not in self.supported_color:
            self.logger.log_error(f'{color} is not a supported color!')
        else:
            bx, by = location
            model  = self.models[f'{color}_buoy']
            gzname = f'{color}_buoy' + str(self.model_counts[f'{color}_buoy'])
            self.logger.log_warn(f'Spawning {color} buoy at x = {bx}, y = {by}...')
            cmd = (f'gz model '
                   f'--spawn-file={model} '
                   f'--model-name={gzname} '
                   f'-x {bx} '
                   f'-y {by} '
                   f'-z 1')
            subprocess.run(cmd, shell=True, executable='/bin/bash')
            self.model_counts[f'{color}_buoy'] = self.model_counts[f'{color}_buoy'] + 1
            self.logger.log_ok('Buoy spawned!')

    def populate_scenario(self, task: int = 1) -> None:
        """Spawn obstacles as defined by competition tasks.

        Args:
            scenario (int, optional): Specific task to spawn. Defaults to 1 (qualification gates).
        """
        if task == 1:
            start_gate_gap = np.random.uniform(1.8288, 3.048) * self.width_scale
            course_length = np.random.uniform(7.62, 30.48) * self.length_scale
            red_buoys = [(-self.gate_distance, -start_gate_gap/2),
                         (-self.gate_distance - course_length, -start_gate_gap/2)]
            green_buoys = [(-self.gate_distance, start_gate_gap/2),
                           (-self.gate_distance - course_length, start_gate_gap/2)]
            for location in red_buoys:
                self.spawn_buoy(location, 'red')
            for location in green_buoys:
                self.spawn_buoy(location, 'green')
        elif task == 2:
            raise NotImplementedError
        elif task == 3:
            raise NotImplementedError
        elif task == 4:
            raise NotImplementedError
        elif task == 5:
            raise NotImplementedError
        elif task == 6:
            raise NotImplementedError
        else:
            raise NotImplementedError

    def spawn_gzclient(self) -> None:
        """Start Gazebo UI Client to visualize environment."""
        if self.verbose:
            command = f'nice -n 20 gzclient --verbose --gui-client-plugin libgazebo_user_camera_plugin.so'.split(' ')
            self.logger.log_debug(f'COMMAND = {command}')
        else:
            command = f'nice -n 20 gzclient --gui-client-plugin libgazebo_user_camera_plugin.so'.split(' ')
        self.gzclient = subprocess.Popen(command)

    def spawn_sitl(self) -> Union[int, None]:
        """Start PX4 SITL.

        Returns:
            Union[int, None]: Exit code of SITL, maybe None if interrupted.
        """
        previous_dir = os.getcwd()
        os.chdir(ROOT_FS)
        command = [SITL_EXEC, '-d', SITL_SUPP]
        if self.verbose:
            self.logger.log_debug(f'COMMAND = {command}')
        sitl = subprocess.Popen(command, shell=True, executable='/bin/bash')
        try:
            return sitl.wait()
        except KeyboardInterrupt as e:
            sitl.kill()
            os.chdir(previous_dir)
            self.kill_gazebo_subprocesses()
            self.purge_temp_dirs()
            return None


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

    def log(self, msg: str, beg: str = '', end:str = "\n"):
        output = beg
        output += f'[LOG]   {msg}'
        output += ColorLogger.END
        print(output, end=end)

    def log_error(self, msg: str, beg:str = '', end:str = "\n"):
        output = beg
        output += ColorLogger.RED
        output += f'[ERROR] {msg}'
        output += ColorLogger.END
        print(output, end=end)

    def log_warn(self, msg: str, beg:str = '', end:str = "\n"):
        output = beg
        output += ColorLogger.YELLOW
        output += f'[WARN]  {msg}'
        output += ColorLogger.END
        print(output, end=end)

    def log_debug(self, msg: str, beg:str = '', end:str = "\n"):
        output = beg
        output += ColorLogger.BLUE
        output += f'[DEBUG] {msg}'
        output += ColorLogger.END
        print(output, end=end)

    def log_ok(self, msg: str, beg:str = '', end:str = "\n"):
        output = beg
        output += ColorLogger.GREEN
        output += f'[OK]    {msg}'
        output += ColorLogger.END
        print(output, end=end)

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
