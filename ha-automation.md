# AC Infinity Fan Sync - Home Assistant Automation

Syncs the intake fan (Garage Comms Rack Cloudline T8) to follow the exhaust fan (Garage Main Rack Cloudline Pro T8) at 85% speed, with a minimum floor of 2.

## Entity IDs

| Role | Device | Entity ID |
|------|--------|-----------|
| Exhaust (leader) | Garage Main Rack Cloudline Pro T8 | `number.garage_main_rack_cloudline_pro_t8_current_power` |
| Intake (follower) | Garage Comms Rack Cloudline T8 | `number.garage_comms_rack_cloudline_t8_on_power` |

> **Note:** Verify these entity IDs in Developer Tools → States before using.

## Automation YAML

```yaml
automation:
  - alias: "Sync intake fan to exhaust"
    description: "Keep intake at 85% of exhaust speed, minimum 2"
    trigger:
      - platform: state
        entity_id: number.garage_main_rack_cloudline_pro_t8_current_power
    condition:
      - condition: template
        value_template: "{{ trigger.from_state.state != trigger.to_state.state }}"
    action:
      - service: number.set_value
        target:
          entity_id: number.garage_comms_rack_cloudline_t8_on_power
        data:
          value: >-
            {% set calculated = (trigger.to_state.state | float) * 0.85 %}
            {% set floored = [calculated, 2] | max %}
            {{ floored | round(0) }}
```

## How It Works

1. Triggers whenever the exhaust fan's current power changes
2. Calculates 85% of the exhaust speed
3. Applies a minimum floor of 2 (intake will never go below 2)
4. Sets the intake fan's "On Power" to the result

## Speed Mapping

| Exhaust | Calculated (85%) | Actual Intake (min 2) |
|---------|------------------|----------------------|
| 10 | 8.5 | 9 |
| 9 | 7.65 | 8 |
| 8 | 6.8 | 7 |
| 7 | 5.95 | 6 |
| 6 | 5.1 | 5 |
| 5 | 4.25 | 4 |
| 4 | 3.4 | 3 |
| 3 | 2.55 | 3 |
| 2 | 1.7 | 2 |
| 1 | 0.85 | 2 |
| 0 | 0 | 2 |

> **Note:** If exhaust is 0 (off), intake will still run at 2. If you want intake to turn off when exhaust is off, modify the condition accordingly.

## Installation

### Option A: UI

1. Go to **Settings → Automations & Scenes**
2. Click **Create Automation**
3. Click the three dots (top right) → **Edit in YAML**
4. Paste the content inside the `automation:` block (starting from `alias:`)
5. Save

### Option B: automations.yaml

Add the YAML above to your `automations.yaml` file, then reload automations.
