# Owltracker

This is a containerized REST API that can be used to track weekly metrics for someone tracking their progress using Duolingo. I built this minimal app to store and serve data as a replacement for some of Duolingo's own (defunct) API services. The API is built using FastAPI, with built in documentation for its routes at `/docs`.

## Starting the API

I'm using `podman` to build/run container images.

```bash
# from the app's directory
podman build -t owltracker-latest .
podman volume create owltracker-data
podman run -it --rm \
    -v owltracker-data:/app/data \
    owltracker-latest
```
