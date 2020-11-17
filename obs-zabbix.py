import json
import socket # Just so we can properly handle hostname exceptions
import obspython as obs
import os
import sys
import subprocess



# Meta
__version__ = '0.1'
__version_info__ = (0, 1)
__license__ = "AGPLv3" # ...or proprietary if you want to negotiate
__license_info__ = {
    "AGPLv3": {
        "product": "obs-zabbix",
        "users": 0, # 0 being unlimited
        "customer": "Unsupported",
        "version": __version__,
        "license_format": "1.0",
    }
}
__author__ = 'Boris Taran'

__doc__ = """\
Publishes real-time OBS status to Zabbix \
at the configured interval.
"""

# Default values for the configurable options:
INTERVAL = 5 # Update interval (in seconds)
ZABBIX_SENDER_BIN = 'c:\\distrib\\zabbix_sender.exe'
ZABBIX_SERVER = ""
ZABBIX_HOST = socket.gethostname()
ZABBIX_KEY = "obs.status"


# sys.exit()

# This is how we keep track of the current status:
STATUS = {
    "recording": False,
    "streaming": False,
    "paused": False,
    "replay_buffer": False, # If it's active or not
    "fps": 0,
    "frame_time_ns": 0,
    "frames": 0,
    "lagged_frames": 0,
}


def on_mqtt_connect(client, userdata, flags, rc):
    """
    Called when the MQTT client is connected from the server.  Just prints a
    message indicating we connected successfully.
    """
    print("MQTT connection successful")

#CLIENT.on_connect = on_mqtt_connect

def on_mqtt_disconnect(client, userdata, rc):
    """
    Called when the MQTT client gets disconnected.  Just logs a message about it
    (we'll auto-reconnect inside of update_status()).
    """
    print("MQTT disconnected.  Reason: {}".format(str(rc)))

#CLIENT.on_disconnect = on_mqtt_disconnect

def update_status():
    """
    Updates the STATUS global with the current status (recording/streaming) and
    publishes it (JSON-encoded) to the configured Zabbix server/host.  
    Meant to be called at the configured
    INTERVAL.
    """

    global STATUS
    STATUS["recording"] = obs.obs_frontend_recording_active()
    STATUS["streaming"] = obs.obs_frontend_streaming_active()
    STATUS["paused"] = obs.obs_frontend_recording_paused()
    STATUS["replay_buffer"] = obs.obs_frontend_replay_buffer_active()
    STATUS["fps"] = obs.obs_get_active_fps()
    STATUS["frame_time_ns"] = obs.obs_get_average_frame_time_ns()
    STATUS["frames"] = obs.obs_get_total_frames()
    STATUS["lagged_frames"] = obs.obs_get_lagged_frames()

    cmd = ZABBIX_SENDER_BIN + " -z " + ZABBIX_SERVER + " -s " + ZABBIX_HOST + " -k " + ZABBIX_KEY + " -o \"" + json.dumps(STATUS).replace('"', '""') + "\""
    
    cmd_str = str(cmd)
    print(cmd_str)
    
    subprocess.call(cmd_str, shell=True)    # to hide console

def script_description():
    return __doc__ # We wrote a nice docstring...  Might as well use it!

def script_load(settings):
    """
    Just prints a message indicating that the script was loaded successfully.
    """
    print("obs-zabbix script loaded.")

def script_unload():
    return true


def script_defaults(settings):
    """
    Sets up our default settings in the OBS Scripts interface.
    """
    obs.obs_data_set_default_string(settings, "ZABBIX_SENDER_BIN", ZABBIX_SENDER_BIN)
    obs.obs_data_set_default_string(settings, "ZABBIX_SERVER", ZABBIX_SERVER)
    obs.obs_data_set_default_string(settings, "ZABBIX_HOST", ZABBIX_HOST)
    obs.obs_data_set_default_string(settings, "ZABBIX_KEY", ZABBIX_KEY)
    obs.obs_data_set_default_int(settings, "interval", INTERVAL)

def script_properties():
    """
    Makes this script's settings configurable via OBS's Scripts GUI.
    """
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "ZABBIX_SENDER_BIN", "Path to zabbix_sender", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "ZABBIX_SERVER", "Zabbix server hostname", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "ZABBIX_HOST", "Zabbix host", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "ZABBIX_KEY", "Zabbix key", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "interval", "Update Interval (seconds)", 1, 3600, 1)
    return props

def script_update(settings):
    """
    Applies any changes made to the MQTT settings in the OBS Scripts GUI then
    reconnects the MQTT client.
    """
    # Apply the new settings
    global ZABBIX_SENDER_BIN
    global ZABBIX_SERVER
    global ZABBIX_HOST
    global ZABBIX_KEY
    global INTERVAL
    
    ZABBIX_SENDER_BIN = obs.obs_data_get_string(settings, "ZABBIX_SENDER_BIN")
    ZABBIX_SERVER = obs.obs_data_get_string(settings, "ZABBIX_SERVER")
    ZABBIX_HOST = obs.obs_data_get_string(settings, "ZABBIX_HOST")
    ZABBIX_KEY = obs.obs_data_get_string(settings, "ZABBIX_KEY")
    INTERVAL = obs.obs_data_get_int(settings, "interval")

    # Remove and replace the timer that publishes our status information
    obs.timer_remove(update_status)
    obs.timer_add(update_status, INTERVAL * 1000)
    
