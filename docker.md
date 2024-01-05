# Docker Instructions

To build the docker image, run the following command:

`docker build -t "arc:latest" .`

To run the docker image for testing, run the following command:

`docker run -p 3333:3333 -e ARCOS_LISTEN_CONFIG_OVERRIDE="true" arc:latest`

In production, use Docker Compose. Here is an example `docker-compose.yml` file:

```yaml
version: '3.7'
services:
  arc:
    image: arc:latest
    ports:
      - 3333:3333
    environment:
      - ARCOS_LISTEN_CONFIG_OVERRIDE=true
    volumes:
      - ./data:/ArcOS/data
```

Then run `docker compose up -d` to start the container.