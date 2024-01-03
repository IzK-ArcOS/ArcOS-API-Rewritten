# Docker Instructions

To build the docker image, run the following command:

`docker build -t "arc:latest" .`

To run the docker image, run the following command:

`docker run -p 3333:3333 -e ARCOS_LISTEN_CONFIG_OVERRIDE="true" arc:latest`