---
name: Feature Request
about: Propose a new gesture class, OS automation action, model enhancement, or dashboard capability for GestureOS
title: "[FEAT] <short descriptive summary>"
labels: ["enhancement"]
assignees: ""
---

## Problem Statement

<!-- Describe the user problem, workflow friction, or limitation in GestureOS that this feature addresses. -->

## Proposed Solution

<!-- Provide a clear technical description of the proposed change, including affected modules (e.g., `GestureRegistry`, `WindowsController`, `APIServer`, or `frontend/src/components/`). -->

## API / Configuration Impact (If Applicable)

<!-- Show any proposed additions to `config.json`, REST endpoints (`/api/*`), or WebSocket (`/ws`) payloads: -->
```json
{
  "gestures": {
    "example_gesture": {
      "action": "keyboard_shortcut",
      "params": { "keys": ["ctrl", "c"] },
      "cooldown_ms": 400,
      "enabled": true
    }
  }
}
```

## Alternative Approaches Considered

<!-- Describe any alternative designs or workarounds you considered and why the proposed solution is preferred. -->

## Additional Context

<!-- Add any benchmarks, UI mockups, or references to research papers. -->
