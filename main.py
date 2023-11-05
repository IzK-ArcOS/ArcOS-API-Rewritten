import uvicorn


import arcos_backend


if __name__ == '__main__':
    cfg = arcos_backend.get_cfg()
    uvicorn.run(
        arcos_backend.app,
        host="0.0.0.0" if cfg['info']['listen'] else "localhost",
        port=cfg['info']['port']
    )
