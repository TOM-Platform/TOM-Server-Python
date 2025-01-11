# Change log (version history)

## main
- Latest stable version

## v0.3
- Enable new capabilities (e.g., CLIP, VectorDB, KeyboardWidget)

## v0.2
- Enable new services and capabilities
- Uniform the protobuf keys
- Enforce linting and formatting

## v0.1
- Initial version


## TODO
- Update documentation
- Update development guide


## Known issues/limitations
- Due to multiprocessing, log rolling is not working properly (FIX: remove the prev log files before starting the server)
- Server can not send data to connected clients directly. Thus, clients need to request data from the server.
- The automatic switching of services are not implemented yet.

