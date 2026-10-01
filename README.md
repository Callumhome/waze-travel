Waze Travel for Home Assistant

A custom Home Assistant integration that uses Waze to calculate travel times, distances, and route information between two locations, with live traffic support.

Features

- Calculate travel time using Waze.
- Display route distance in miles or kilometres.
- Miles selected by default.
- Use live traffic information.
- Display route name and street names.
- Retrieve alternative routes.
- Choose vehicle type.
- Avoid toll roads, subscription roads, and ferries.
- Configure the route update interval.
- Use addresses, GPS coordinates, or Home Assistant location entities as the origin and destination.
- Monitor travel information through Home Assistant sensors.

Installation

HACS

1. Open HACS in Home Assistant.

2. Open the integrations section.

3. Open the menu and select Custom repositories.

4. Add this repository URL:
   
   "https://github.com/Callumhome/waze-travel"

5. Select Integration as the category.

6. Find Waze Travel and download it.

7. Restart Home Assistant.

If the repository is already added to HACS, find Waze Travel and download or update it there.

Manual installation

1. Download this repository.
2. Copy the "custom_components/waze_travel" directory into your Home Assistant configuration directory.
3. Restart Home Assistant.

The resulting folder structure should be:

config/
└── custom_components/
    └── waze_travel/
        ├── __init__.py
        ├── config_flow.py
        ├── const.py
        ├── coordinator.py
        ├── manifest.json
        ├── sensor.py
        ├── strings.json
        └── translations/
            └── en.json

The "pywaze" dependency is installed automatically by Home Assistant.

Configuration

1. Open Settings → Devices & services.
2. Select Add integration.
3. Search for Waze Travel.
4. Enter the route details.

Configuration options

Option| Description
Name| Name for this Waze route
Origin| Starting address, coordinates, or supported Home Assistant location entity
Destination| Destination address, coordinates, or supported Home Assistant location entity
Waze region| Waze region used to calculate the route
Use live traffic| Include live traffic conditions
Vehicle type| Car, taxi, or motorcycle
Distance unit| Miles or kilometres
Avoid toll roads| Avoid toll roads where supported
Avoid subscription roads| Avoid subscription roads where supported
Avoid ferries| Avoid ferry routes where supported
Update interval| How often route information is refreshed, in seconds

The minimum update interval is 60 seconds.

Supported location inputs

You can enter:

- A street address.
- GPS coordinates in "latitude,longitude" format.
- A supported Home Assistant entity ID, such as "person.callum", "zone.home", or a "device_tracker" entity with latitude and longitude attributes.

For entity-based locations, Home Assistant must have valid location attributes available.

Sensors

Waze Travel creates two sensors for each configured route.

Travel time

Reports the estimated journey duration in minutes.

Distance

Reports the route distance in the selected unit:

- Miles ("mi") — default.
- Kilometres ("km") — optional.

The distance sensor converts the route distance to the selected unit for display.

Both sensors are associated with the Waze Travel device in Home Assistant.

Changing the distance unit

After setting up a route:

1. Open Settings → Devices & services.
2. Select the Waze Travel integration entry.
3. Open its Configure or options menu.
4. Select Miles or Kilometres.
5. Save the change.

You do not need to delete and recreate the route to change the distance unit.

Dashboard examples

Add the generated sensors to a dashboard using an Entities card, Tile card, or your preferred Lovelace card.

For example, an Entities card can display the travel time and distance together:

type: entities
title: Waze Travel
entities:
  - entity: sensor.travel_time
  - entity: sensor.distance

Replace the example entity IDs with the actual IDs created by Home Assistant.

Troubleshooting

Unable to calculate the route

- Check that the origin and destination are valid.
- Check that the selected Waze region is correct.
- If using a Home Assistant entity, confirm it has latitude and longitude attributes.
- Check the Home Assistant logs for Waze Travel errors.
- Check that Home Assistant has internet access.

Route sensors are unavailable

- Check that the integration loaded successfully.
- Check the Home Assistant logs for update errors.
- Confirm that the route can be calculated by Waze.

Distance appears in the wrong unit

Open the integration's options and confirm the selected distance unit. The sensor uses miles by default when no unit has been saved.

Requirements

- Home Assistant.
- Internet access.
- The "pywaze==1.2.3" Python package, installed automatically by Home Assistant.

Development

The integration source code and issue tracker are available on GitHub:

- Repository: https://github.com/Callumhome/waze-travel
- Issues: https://github.com/Callumhome/waze-travel/issues

Disclaimer

This is a community-developed Home Assistant integration and is not affiliated with, endorsed by, or supported by Waze.

Route availability, travel times, and traffic information depend on Waze and the "pywaze" library. Results may vary and should not be relied upon as a guarantee of journey conditions.
