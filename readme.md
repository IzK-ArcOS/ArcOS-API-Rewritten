# ArcOS Backend Server

## About

this is the backend server which powers user and session management,
filesystem and messaging (and prob more later) for [ArcOS' frontend](https://github.com/IzK-ArcOS/ArcOS-Frontend)

## Getting Started
Before you continue, make sure you install the system prerequisites:
- Git
- Python 3.11 or higher

Once the prerequisites are met, you can execute the following commands to **clone the API**, **Install dependencies** and **run it for the first time**:
```bash
$ git clone https://github.com/IzK-ArcOS/ArcOS-API-Rewritten  # Clone repository
$ cd ArcOS-API-Rewritten/

$ python -m venv venv  # Create virtual enviroment for ArcAPI

# Activate virtual enviroment (you will need to do this each time when launching ArcAPI)
# If on *nix:
$ source venv/bin/activate
# If on windows (cmd, on powershell replace `.bat` with `.ps1`):
$ venv/Scripts/activate.bat

$ pip install -r requirements.txt  # Satisfy dependencies

$ python3 ./main.py # Start the API

$ deactivate  # Deactivate virtual enviroment
```

When running the API for the first time, a configuration file will be created called `config.yaml`, in which you can personalize your ArcAPI instance.

## Launch

to launch you can just do:
- linux: `./main.py` (assuming file permissions are transferred, otherwise
first do `chmod +x main.py`)
- windows: `py main.py`

## Configuration

default config wil be created right after the first launch and placed in
`config.yaml` file
