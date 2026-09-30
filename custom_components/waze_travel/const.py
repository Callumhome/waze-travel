"""Constants for Waze Travel."""

from datetime import timedelta

DOMAIN = "waze_travel"
CONF_ORIGIN = "origin"
CONF_DESTINATION = "destination"
CONF_REGION = "region"
CONF_REALTIME = "realtime"
CONF_VEHICLE_TYPE = "vehicle_type"
CONF_AVOID_TOLL_ROADS = "avoid_toll_roads"
CONF_AVOID_SUBSCRIPTION_ROADS = "avoid_subscription_roads"
CONF_AVOID_FERRIES = "avoid_ferries"
CONF_SCAN_INTERVAL = "scan_interval"
CONF_BASE_COORDINATES = "base_coordinates"

DEFAULT_REGION = "EU"
DEFAULT_REALTIME = True
DEFAULT_VEHICLE_TYPE = "car"
DEFAULT_SCAN_INTERVAL = 300
MIN_SCAN_INTERVAL = 60
DEFAULT_AVOID_TOLL_ROADS = False
DEFAULT_AVOID_SUBSCRIPTION_ROADS = False
DEFAULT_AVOID_FERRIES = False

REGIONS = ["US", "NA", "EU", "IL", "AU"]
VEHICLE_TYPES = ["car", "taxi", "motorcycle"]
DEFAULT_TIMEOUT = 60
UPDATE_TIMEOUT = timedelta(seconds=DEFAULT_TIMEOUT)
