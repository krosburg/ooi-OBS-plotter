import sys
import datetime
from configparser import ConfigParser
from obspy import UTCDateTime
from obspy.clients.fdsn import Client


# == READ_CONFIG_HELPER FUNCTION ==============================================
def read_config_helper(config, param_name, s):
    """Given configuration parameter name & cfg section, parses config info."""
    key_str = config.get(s, param_name)
    if key_str is None:
        print('Warning: ' + param_name + ' is missing from config file')
        exit(0)
    else:
        if param_name == 'pdNumsString':
            return key_str
        elif len(key_str.split(',')) > 1:
            return key_str.split(',')
        else:
            return key_str


# == GET_ARGS HELPER FUNCTION =================================================
def get_args():
    """Retrieves important arguments from the command line."""
    if len(sys.argv) < 3:
        raise Exception('Not enough arguments')
    else:
        config_file = sys.argv[1]
        time_window = sys.argv[2]
        if len(sys.argv) >= 4:
            dest_dir = sys.argv[3]
        else:
            dest_dir = './'
        return config_file, time_window, dest_dir


# == GET_OFFSET HELPER FUNCTION ===============================================
def get_offset(time_window):
    """Given a time_window string (day, week, month, year), returns the correct
    time offset (sec) for creating the t_start variable from t_end; and a plot
    interval (minutes) used to define the width of the seis dayplot."""
    if time_window == 'day':
        return 86400, 60           # 1 day, 1 hour
    elif time_window == 'week':
        return 7*86400, 4*60       # 7 days, 4 hours
    elif time_window == 'month':
        return 30*86400, 1440      # 30 days, 1 day
    elif time_window == 'year':
        return 365*86400, 1440*10  # 1 year, 10 days
    else:
        raise Exception('Interval time not specified')


# == READ_CONFIG FUNCTION =====================================================
def read_config(params_list, cfg_file):
    """Reads and parses .cfg config files."""
    config = ConfigParser()
    config.read(cfg_file)

    # Define config dictionary and read in parameters
    cfg = {}
    for s in config.sections():
        # Retrieve Title
        param = {}
        param['title'] = s

        # Parse non-optional parameters
        for param_name in params_list:
            param[param_name] = read_config_helper(config, param_name, s)

        if config.has_option(s, 'opOff'):
            param['opOff'] = int(config.get(s, 'opOff'))
        else:
            param['opOff'] = 0

        # Add to configutation list
        cfg[s] = param
    return cfg


# == BEGIN ZE MAIN PROGRAMEN ==================================================
# Define Ze Important Wariables
params_list = ['name', 'station', 'network', 'location', 'channel']
min_magnitude = 6.5
label_size = 20
filt_type = "lowpass"
filt_freq = 0.05
filt_corn = 2

# Read Wariables from Ze Commanden Line & Zen Read Ze Config File
config_file, time_window, dest_dir = get_args()
cfg = read_config(params_list, config_file)

# Add Trailing Slash to Image Dest Dir If Not Already Zhere
if dest_dir[-1] != '/':
    dest_dir = dest_dir + '/'

# Setup Some Plotting Wariables
line_colors = ['k', 'r', 'b', 'g']
offset, interval = get_offset(time_window)

# Zetup Ztart und End Times Using ze Correct Offset for Given Time Vindow
t_end = UTCDateTime(datetime.datetime.utcnow().isoformat())
t_start = t_end - offset

# Loop On Config Block
for cBlock in cfg:
    # Get Ze Para-meters
    params = cfg.get(cBlock)

    # Setup Plot Title String & Events
    title_str = params['title'] + '\n' + str(t_start) + ' to ' + str(t_end)
    if "year" not in time_window:
        event_str = {'min_magnitude': 6.5}
    else:
        event_str = {}

    # Create ze IRIS Client & Send ze Data Request
    client = Client("IRIS")
    st = client.get_waveforms(network=params['network'],
                              station=params['station'],
                              location=params['location'],
                              channel=params['channel'],
                              starttime=t_start,
                              endtime=t_end)

    # Apply Lowpass Filter (Note 0.05 is just a guess)
    st.filter(filt_type, freq=filt_freq, corners=filt_corn)

    # Plot Ze Datas
    st.plot(type="dayplot", interval=interval, right_vertical_labels=False,
            vertical_scaling_range=5e3, one_tick_per_line=True,
            color=line_colors, show_y_UTC_labe=True, title=title_str + '\n',
            events=event_str)
