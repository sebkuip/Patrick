# Patrick

ORE's Discord bot. Built as a replacement for [Chad](https://github.com/openRedstoneEngineers/chad).

## Running

### Basic

Patrick can be run by installing dependencies then executing `patrick.py`:

```bash
pip install -r requirements.txt
python patrick.py
```

### Running via Podman and Buildah

Build with buildah:
```bash
buildah bud -t patrick .
```

Run the container:
```bash
podman run -d --name patrick \
  --env-file .env \
  -v $(pwd):/app:Z \
  localhost/patrick
```

### Deploying

For deployment, create a systemd unit file:
```bash
podman generate systemd --name patrick \
  --restart-policy=always \
  --restart-sec=5 > patrick.service
```

Finally, save this unit file in the appropriate location and enable the service.
Pushing changes to a deployed instance requires removing the `patrick` container, rebuilding Patrick, then rerunning it.
