## Linting (code formatting)

**VSCode**

1. Install the pylint plugin
2. In the settings, change the following configurations:
   1. Pylint > Args: `--rcfile='.github/linters/.pylintrc`
   2. Python > Linting > Pylint Enabled: True

**Pycharm**

1. Install the pylint plugin from the Marketplace, apply the changes and restart the IDEA if prompted.
2. Open Settings and search for 'pylint'. There are 2 configurations:
   1. Path to Pylint Executable
   2. Path to .pylintrc: `.github/linters/.pylintrc`

**Command-Line**

1. `pylint --rcfile='.github/linters/.pylintrc' *`




## Development


### Guides
- Please read the [repository guide](https://docs.google.com/document/d/13nuP668jawXzb_bnPgzxtRhcEUJzmzB0YHYm-yMr15I/edit#heading=h.h8j0qs3w2ubi) to understand how the server works
- Follow development guidelines in creating new service and components.


### Adding third-party libraries

- Add the links of libraries/reference/API docs to [Third-party libraries](#Third-party-libraries) section
- If credentials are required, add the instructions to [Installation](#Installation) section
- Update the [environment-cpu.yml](environment-cpu.yml) file with the new library and version details
- Update [VERSION](VERSION.md) file with added capabilities/changes


### DataTypes.json

- The values should match that of the Client
- Each entry in the `DataTypes.json` must have the following keys:
  - `key`
  - `proto_file`
  - `components`
- Example Template Entry:

```yaml
NAME: {
  key: 0000,
  proto_file: proto_file_pb2.py,
  components: [
    type:name
  ]
}
```

### Component Creation

- All Components **must** inherit from the `BaseComponent` class located in `base_component.py`.
- This Parent Class encapsulates many methods and functions required to accurately pass data between services, as well as to interface with other Utilities. This includes:
  - Shared Memory
  - Database

### Service Creation

- To support the creation of Service Components, the Shared Memory located in `Memory/Memory.py` can be used to save data which is required across multiple threads.
- Generally, as long as your Service requires data from multiple widgets, the Shared Memory is **required**.

- Additionally, there are a few required steps when creating a Service Component, as compared to other Components.
  1. Ensure that you call `set_component_status` with the appropriate new component status in your entry and exit functions. (Refer to `base_keys.py`)

### Websocket

- By default, the socket server will send to all websocket connections that are connected. See [socket_server.py -> `async def send_data_to_websockets(data, websocket_client_type=None)`](Websocket/socket_server.py)
  - To send to a specific connection, we need to set a websocket header to the connection.
  - Here are some examples:
    - [TOM-Client-WearOS](https://github.com/NUS-SSI/TOM-Client-WearOS/blob/demo/running_coach_v2.4/app/src/main/java/com/hci/tom/android/network/SendExerciseDataWorker.kt#L25-L28)
    ```kotlin
    private val request = Request.Builder()
        .url(SERVER_URL)
        .addHeader("websocket_client_type", "wearOS")
        .build()
    ```

    - [TOM-Client-Unity](https://github.com/NUS-SSI/TOM-Client-Unity/blob/demo/running_coach_v2.7/Assets/Scripts/Communication/SocketCommunication.cs#L44-L51)

    ```csharp
    var url = GetWebSocketUrl();
    
    // add custom header to differentiate client type
    Dictionary<string, string> customHeader = new Dictionary<string, string>();
    customHeader["websocket_client_type"] = "unity";
    
    websocket = new WebSocket(url, customHeader);
    ```

- Make sure to also declare the websocket header key in `base_keys.py`.

```python
# NOTE: Websocket
WEBSOCKET_DATATYPE = "websocket_datatype"
WEBSOCKET_MESSAGE = "websocket_message"
WEBSOCKET_CLIENT_TYPE = "websocket_client_type"
UNITY_CLIENT = "unity"
WEAROS_CLIENT = "wearOS"
# declare websocket header key here
```

- This is an example of how we can send messages to unity clients only.

```python
self.running_service.send_to_component(
    websocket_message=result, websocket_client_type=UNITY_CLIENT
)
```

### Protobuf

- Ensure you have `protoc` installed by typing `protoc --version` in your terminal. If it is not installed, you may follow the instructions [here](https://github.com/protocolbuffers/protobuf#protocol-compiler-installation).
- Create your proto file in `DataFormat/ProtoFiles`. For more information on how to structure proto data, please refer [here](https://protobuf.dev/getting-started/pythontutorial/).
- `cd` to `DataFormat` and run this command in your terminal `protoc -I=ProtoFiles --python_out=ProtoFiles ProtoFiles/proto_name.proto` to generate the builder class. Note that you have to run the command again if you edit the proto file.

### Data Saving

- To set up tables in the Database, add a `.json` file in `Database/Models` with the following format:
  - NOTE: Ensure that the Class and Table Names are unique, as they are used to identify the appropriate tables for each operation.

```yaml
{
  "table_name": "UserTable",
  "columns": [
    {
      "name": "id",
      "type": "integer",
      "nullable": false,
      "unique": true
    },
    {
      "name": "age",
      "type": "integer",
      "nullable": false,
      "unique": false
    },
    {
      "name": "name",
      "type": "string",
      "nullable": false,
      "unique": false
    }
  ],
  "primary_key": "id"
}
```

- To save data to the Database, use the `Database/tables.py` file.
  - See `Database/tables.py` for what functions to call for the `READ` and `INSERT` operations, as well as what format is expected. Samples at `Tests/Integration/test_database.py`
  - Do note that if the 1st character of the `key` key **cannot** be a 0 as `json.loads()` will not be able to parse it.


