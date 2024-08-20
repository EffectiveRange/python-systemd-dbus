
[![Test and Release](https://github.com/EffectiveRange/python-systemd-dbus/actions/workflows/test_and_release.yml/badge.svg)](https://github.com/EffectiveRange/python-systemd-dbus/actions/workflows/test_and_release.yml)
[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/EffectiveRange/python-systemd-dbus/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/EffectiveRange/python-systemd-dbus/blob/python-coverage-comment-action-data/htmlcov/index.html)

# python-systemd-dbus

Python dbus interface library for systemd

Uses [dbus_python](https://dbus.freedesktop.org/doc/dbus-python/) to interface with
systemd's [dbus API](https://www.freedesktop.org/software/systemd/man/latest/org.freedesktop.systemd1.html).

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
    - [Debian packages](#debian-packages)
    - [Python packages](#python-packages)
- [Installation](#installation)
- [Usage](#usage)
    - [Start/Stop/Restart/Reload services](#startstoprestartreload-services)
    - [Enable/Disable service files](#enabledisable-service-files)
    - [Mask/Unmask service files](#maskunmask-service-files)
    - [Get service state/error code](#get-service-stateerror-code)
    - [Get service/service file properties](#get-serviceservice-file-properties)
    - [Reload systemd daemon](#reload-systemd-daemon)
    - [New in 1.3.0](#new-in-130)

## Features

- [x] Start/Stop/Restart/Reload services
- [x] Enable/Disable service files
- [x] Mask/Unmask service files
- [x] Get service state/error code
- [x] Get service/service file properties
- [x] Reload systemd daemon (to apply service file changes)
- [x] [New in 1.3.0](#new-in-130) Subscribe to service property change events

## Requirements

### Debian packages

- dbus
- libdbus-1-dev
- Python 3

### Python packages

- dbus-python
- context-logger

## Installation

### Install from source root directory

```bash
pip install .
```

### Install from source distribution

1. Create source distribution
    ```bash
    pip setup.py sdist
    ```

2. Install from distribution file
    ```bash
    pip install dist/systemd-dbus-1.0.0.tar.gz
    ```

3. Install from GitHub repository
    ```bash
    pip install git+https://github.com/EffectiveRange/python-systemd-dbus.git@latest
    ```

## Usage

Note: `service_name` is automatically appended with `.service` if not provided.

### Start/Stop/Restart/Reload services

```python
from systemd_dbus import SystemdDbus

systemd = SystemdDbus()

systemd.start_service('service_name')
systemd.stop_service('service_name')
systemd.restart_service('service_name')
systemd.reload_service('service_name')
```

### Enable/Disable service files

```python
from systemd_dbus import SystemdDbus

systemd = SystemdDbus()

systemd.enable_service('service_name')
systemd.disable_service('service_name')
```

### Mask/Unmask service files

```python
from systemd_dbus import SystemdDbus

systemd = SystemdDbus()

systemd.mask_service('service_name')
systemd.unmask_service('service_name')
```

### Get service state/error code

```python
from systemd_dbus import SystemdDbus

systemd = SystemdDbus()

state = systemd.get_active_state('service_name')
print(state)

error_code = systemd.get_error_code('service_name')
print(error_code)
```

### Get service/service file properties

```python
from systemd_dbus import SystemdDbus

systemd = SystemdDbus()

properties = systemd.get_service_properties('service_name')
for key, value in properties.items():
    print(f'{key}: {value}')

properties = systemd.get_service_file_properties('service_name')
for key, value in properties.items():
    print(f'{key}: {value}')
```

### Reload systemd daemon

```python
from systemd_dbus import SystemdDbus

systemd = SystemdDbus()

state = systemd.reload_daemon()
```

### New in 1.3.0

Subscribe to service property change events.
Retrieve the object path of the service from the output of the following command:

```bash
dbus-send --system --print-reply --reply-timeout=2000 --type=method_call \
--dest=org.freedesktop.systemd1 /org/freedesktop/systemd1 org.freedesktop.systemd1.Manager.ListUnits | grep dhcpcd_
```

Output:

```bash
         object path "/org/freedesktop/systemd1/unit/dhcpcd_2eservice"
```

Example to print status changes for `dhcpcd` service:

```python
from typing import Any
from systemd_dbus import SystemdDbus


def on_property_changed(*args: Any) -> None:
    _, props, _ = args
    state = props.get('ActiveState')
    if state:
        print(f'State of dhcpcd service changed to {state}')


systemd = SystemdDbus()
systemd.add_property_change_handler('/org/freedesktop/systemd1/unit/dhcpcd_2eservice', on_property_changed)
```
