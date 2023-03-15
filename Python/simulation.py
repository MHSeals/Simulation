from samminhch.simutils import EnvironmentManager

e = EnvironmentManager(debug=True)
try:
    e.start_simulation(headless=False)
except Exception as err:
    print(err)
    e.kill_gazebo_subprocesses()