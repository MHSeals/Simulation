from samminhch.simutils import EnvironmentManager

e = EnvironmentManager()
try:
    e.start_simulation(headless=True)
except Exception as err:
    print(err)
    e.kill_all_gz_processes()

# e.debug_simulation()
