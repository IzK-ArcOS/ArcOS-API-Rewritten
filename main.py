#!/bin/python
import uvicorn
import os


import arcos_backend


if __name__ == '__main__':
    cfg = arcos_backend.get_cfg()
    uvicorn.run(
        arcos_backend.app,
        host="0.0.0.0" if cfg['info']['listen'] or os.getenv('ARCOS_LISTEN_CONFIG_OVERRIDE') == "true" else "localhost",
        port=cfg['info']['port']
    )
