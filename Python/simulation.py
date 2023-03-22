from samminhch.simutils import ColorLogger, EnvironmentManager

logger = ColorLogger()
e = EnvironmentManager(debug=True)
try:
    e.start_simulation(headless=False)
except Exception as err:
    logger.log_error(str(err)) 
    e.kill_gazebo_subprocesses()
