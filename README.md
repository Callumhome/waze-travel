# Waze Travel

A modern Home Assistant integration for live Waze travel times.

> **Unofficial:** Waze Travel is not affiliated with or endorsed by Waze or Google.

## Status

Early development — **v0.1.0**.

Waze Travel uses the maintained [`pywaze`](https://github.com/eifinger/pywaze) client to calculate Waze routes.

## Features

- UI-based setup
- Origin and destination using addresses or coordinates
- Waze region selection
- Live traffic routing
- Car, taxi and motorcycle vehicle types
- Toll-road avoidance
- Subscription-road avoidance
- Ferry avoidance
- Configurable update interval
- Travel-time sensor
- Distance sensor
- Alternative route information

## Installation

### HACS

Once published, add this repository as a custom repository in HACS and install **Waze Travel**.

### Manual

Copy the `custom_components/waze_travel` directory into your Home Assistant `config/custom_components` directory and restart Home Assistant.

## Configuration

Go to:

**Settings → Devices & services → Add Integration → Waze Travel**

Enter your origin and destination and configure the routing options.

## Disclaimer

Waze Travel accesses Waze routing services through the `pywaze` client. Waze may change its services without notice. This is a community-maintained project and may require updates if Waze changes its routing service.

## License

MIT. See [LICENSE](LICENSE).
