import subprocess

# models
red_models = '/root/src/roboboat-models/Buoy/red_buoy.sdf'
green_models = '/root/src/roboboat-models/Buoy/green_buoy.sdf'

# boat is actually 6m long by 2m wide
# competition max is 6ft long by 3ft wide
# competition max is 1.8288m long by 0.9144m wide
# so to make comparable scaling
width_scale = 2.0 / 0.9144
length_scale = 6.0 / 1.8288

# each gateway is between 6 to 10 ft wide
# that's about 1.8288 to 3.048m wide
gateway_gap = width_scale * 1.8288  # technically narrowest gate

# second gateway is between 25 to 100 ft away
# that's about 7.62 to 30.48m away
gateway_distance = length_scale * 15.24 # 50ft away

# buoys are at least 6 ft away from boat
# that's about 1.8288m away
# TODO: spawn using Lat/Long instead of meters from x=0, y=0
min_buoy_dist = length_scale * 1.8288
buoy_locations = [((-min_buoy_dist, -gateway_gap/2), (-min_buoy_dist, gateway_gap/2)),
                  ((-min_buoy_dist - gateway_distance, -gateway_gap/2), (-min_buoy_dist - gateway_distance, gateway_gap/2))]

red_count = 0
green_count = 0
for ((red_buoy_x, red_buoy_y), (green_buoy_x, green_buoy_y)) in buoy_locations:
    cmd = f'gz model --verbose --spawn-file="{red_models}" --model-name=rbuoy{red_count} -x {red_buoy_x} -y {red_buoy_y} -z 1'
    cmd = 'GAZEBO_MASTER_URI=http://127.0.0.1:11345 ' + cmd
    subprocess.run(cmd, shell=True)
    
    cmd = f'gz model --verbose --spawn-file="{green_models}" --model-name=gbuoy{green_count} -x {green_buoy_x} -y {green_buoy_y} -z 1'
    cmd = 'GAZEBO_MASTER_URI=http://127.0.0.1:11345 ' + cmd
    subprocess.run(cmd, shell=True)
    
    green_count += 1
    red_count += 1
