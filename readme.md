# ArcOS Backend Server

## About

this is the backend server which powers user and session management,
filesystem and messaging (and prob more later) for [ArcOS' frontend](https://github.com/IzK-ArcOS/ArcOS-Frontend)

## Setup

it is quite easy to setup the thing:
1. clone repo: `git clone https://github.com/IzK-ArcOS/ArcOS-API-Rewritten`
2. install requirements: `pip install -r requirements.txt`

(i would recommend using virtual enviroment when installing requirements)

## Launch

to launch you can just do:
- linux: `./main.py` (assuming file permissions are transferred, otherwise
first do `chmod +x main.py`)
- windows: `py main.py`

## Configuration

default config wil be created right after the first launch and placed in
`config.yaml` file
