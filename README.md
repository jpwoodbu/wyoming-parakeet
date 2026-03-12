# Wyoming Parakeet

A Wyoming protocol server for NVIDIA Parakeet. This project is currently
configured to only run on CPUs, not GPUs. As a reference, on my Ryzen 5500, most
Home Assistant related commands, _e.g. "Turn off the light"_, are transcribed in
about 200ms. I initially planned to have GPU support, but at this time, at least
for me, the latency while running on the CPU is adequate.

## Quick start with Docker

```sh
docker run --name wyoming-parakeet -u 1000:1000 -p 10300:10300 -d ghcr.io/jpwoodbu/wyoming-parakeet:latest
```

Alternatively, using _Docker compose_:
```yaml
services:
  wyoming-parakeet:
    image: ghcr.io/jpwoodbu/wyoming-parakeet:latest
    container_name: wyoming-parakeet
    restart: unless-stopped
    ports:
      - "10300:10300"
    user: "1000:1000"
    volumes:
      - models:/models

volumes:
  models:
```

## Setup without Docker

From the project root:
```sh
python3 -m venv .venv
. .venv/bin/activate
pip install .
```

### Running the server

```sh
. .venv/bin/activate
python -m wyoming_parakeet
```

To see flags, run:
```sh
python -m wyoming_parakeet --help
```
