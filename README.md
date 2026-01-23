# AC Infinity Fan Sync

Automatically sync intake fan speed to a percentage of exhaust fan speed for AC Infinity UIS controllers.

Creates a slight positive pressure bias by running intake at a lower speed than exhaust (default 85%).

## How It Works

1. Polls the AC Infinity cloud API to read exhaust fan speed
2. Calculates target intake speed (default: 85% of exhaust)
3. Sets intake fan to ON mode with calculated speed
4. Only updates if speed actually changed (avoids unnecessary API calls)
5. Repeats at configurable interval (default: 60 seconds)

## Requirements

- AC Infinity Controller 69 WiFi, Pro, Pro+, or AI+ (must have cloud connectivity)
- Two controllers: one for exhaust, one for intake
- Both controllers registered to the same AC Infinity account

## Configuration

| Environment Variable | Required | Default | Description |
|---------------------|----------|---------|-------------|
| `ACINFINITY_EMAIL` | Yes | - | AC Infinity account email |
| `ACINFINITY_PASSWORD` | Yes | - | AC Infinity account password |
| `EXHAUST_CONTROLLER` | Yes | - | Name of exhaust controller (as shown in app) |
| `EXHAUST_PORT` | No | 1 | Port number of exhaust fan (1-4) |
| `INTAKE_CONTROLLER` | Yes | - | Name of intake controller (as shown in app) |
| `INTAKE_PORT` | No | 1 | Port number of intake fan (1-4) |
| `INTAKE_RATIO` | No | 0.85 | Intake speed ratio (0.85 = 85% of exhaust) |
| `SYNC_INTERVAL` | No | 60 | Seconds between sync checks |
| `LOG_LEVEL` | No | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |

## Usage

### Docker

```bash
docker run -d \
  --name ac-infinity-fansync \
  -e ACINFINITY_EMAIL=your@email.com \
  -e ACINFINITY_PASSWORD=yourpassword \
  -e EXHAUST_CONTROLLER="Garage Main Rack" \
  -e INTAKE_CONTROLLER="Garage Comms Rack" \
  -e INTAKE_RATIO=0.85 \
  ghcr.io/lukeevanstech/ac-infinity-fansync:latest
```

### Docker Compose

```yaml
services:
  ac-infinity-fansync:
    image: ghcr.io/lukeevanstech/ac-infinity-fansync:latest
    container_name: ac-infinity-fansync
    restart: unless-stopped
    environment:
      ACINFINITY_EMAIL: your@email.com
      ACINFINITY_PASSWORD: yourpassword
      EXHAUST_CONTROLLER: "Garage Main Rack"
      INTAKE_CONTROLLER: "Garage Comms Rack"
      INTAKE_RATIO: "0.85"
      SYNC_INTERVAL: "60"
      LOG_LEVEL: INFO
```

### Kubernetes

See `deploy/kubernetes/` for Flux CD / Helm manifests.

## Caveats

- Works via cloud polling, so there's a small delay (sync interval + API latency)
- If internet drops, sync stops - but fans will continue running at their last set speed
- Sets intake fan to ON mode (manual speed control), overriding any temperature-based automation on that port

## Building

```bash
docker build -t ac-infinity-fansync .
```

## License

MIT
