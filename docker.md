# Docker Instructions

To build the docker image, run the following command:

`docker build -t "arc:latest" .`

To run the docker image, run the following command:

`docker run -p 3333:3333 -e ARCOS_LISTEN_CONFIG_OVERRIDE="true" arc:latest`

To use Docker Compose, use this `docker-compose.yml` file:

```yaml
version: '3.7'
services:
  arc:
    image: arc:latest
    ports:
      - 3333:3333
    environment:
      - ARCOS_LISTEN_CONFIG_OVERRIDE=true
```

Then run `docker-compose up` to start the container.