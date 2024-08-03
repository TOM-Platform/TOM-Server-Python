# TOM-Server-Python

A Python implementation of the server that handles the client data and application logic
- A backend server to handle data processing and running of various services. 
- It takes input from a variety of sources, including video streams and the WebSocket Server. 
- Designed to be easy for developers to implement new services and to be able to support real-time data processing.


## Requirements

- Make sure `python3` is installed


## Installation

- Install `conda` ([Miniconda](https://docs.conda.io/en/latest/miniconda.html)). Note that some packages may not work with Anaconda.
- Create new conda environment `tom` using `conda env create -f environment-cpu.yml` (If you have a previous environment, then update it, `conda env update --file environment-cpu.yml --prune`. To completely remove previous env use, `conda remove -n tom --all`)
  - For ARM Mac (M1-Mn chip), if the installation fails due to `pyaudio`, please follow [this](https://stackoverflow.com/questions/33513522/when-installing-pyaudio-pip-cannot-find-portaudio-h-in-usr-local-include)
  - In addition, locally, you may need to install googlemaps using ` pip install --use-pep517 googlemaps` to avoid OSError
- Activate `tom` environment, `conda activate tom`
- Download the pretrained weights for YOLOv8 from [ultralytics](https://github.com/ultralytics/ultralytics) (e.g., [yolov8n.pt](https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt)) and copy it to `Processors/Yolov8/weights` and rename it as `model.pt` (i.e., `Processors/Yolov8/weights/model.pt`)
- Create the environment files
  - [For development environment] Copy `.sample_env` to `.env.dev` and update the values accordingly
  - [For testing environment] Copy `.sample_env` to `.env.test` and update the values accordingly
- Create the required credential files inside `credential` folder, **ONLY** for third-party libraries you use. Please refer to [Third-party libraries](##Third-party-libraries) section to obtain credentials. (Note: json format must be correct)
  - Create a file `credential/hololens_credential.json` with Hololens credentials such as `{"ip": "IP","username": "USERNAME","password": "PASSWORD"}`
    - [Configure](https://docs.microsoft.com/en-us/windows/mixed-reality/develop/platform-capabilities-and-apis/using-the-windows-device-portal) the Hololens Device Portal. Save [your credentials](https://docs.microsoft.com/en-us/windows/mixed-reality/develop/platform-capabilities-and-apis/using-the-windows-device-portal#creating-a-username-and-password) to `credential/hololens_credential.json`
  - Create a file `credential/google_cloud_credentials.json` with [Google Cloud API](https://cloud.google.com/apis) credentials (follow [authentication](https://github.com/GoogleCloudPlatform/hackathon-toolkit/blob/master/vision/README.md#authentication) to get json key file and rename it to `google_cloud_credentials.json`)
  - Create a file `credential/openai_credential.json` with [OpenAI](https://platform.openai.com/docs/overview) credentials such as `{"openai_api_key": "KEY"}`
  - Create a file `credential/gemini_credential.json` with [Gemini](https://ai.google.dev/gemini-api/docs/) credentials such as `{"gemini_api_key": "KEY"}`
  - Create a file `credential/anthropic_credential.json` with [Anthropic](https://www.anthropic.com/api) credentials such as `{"anthropic_api_key": "KEY"}`
  - Create a file `credential/google_maps_credential.json` with Google Maps credentials such as `{"map_api_key": "KEY"}`
    - Current Google Maps APIs used:
      - [Places API](https://developers.google.com/maps/documentation/places/web-service/overview)
      - [Directions API](https://developers.google.com/maps/documentation/directions/overview)
      - [Static Maps API](https://developers.google.com/maps/documentation/maps-static/overview)
    - To use Google Maps API, you need to have a Google Cloud Platform (GCP) account to get an API key and enable the APIs shown above.
  - Create a file `credential/ors_credential.json` with [Openrouteservice](https://openrouteservice.org/) credentials such as `{"map_api_key": "KEY"}`
  - Create a file `credential/geoapify_credential.json` with [Geoapify](https://www.geoapify.com/) credentials such as `{"map_api_key": "KEY"}`
  - Create a file `credential/fitbit_credential.json` with Fitbit credentials such as `{"client_id": "ID","client_secret": "SECRET"}`
- [Optional] Download the first person video [here](https://e.pcloud.link/publink/show?code=XZkqaBZ5epwEkqARuyqFgy5xs3EAHLegagk) if you want to simulate running on a treadmill. It should be located in `Tests/RunningFpv/fpv.mp4`


## Setup the clients

- Makesure the clients (e.g., HoloLens, Xreal, WearOS Watch) are connected to the same Wi-Fi network of the Sever. Use a **private** network, as public networks may block certain ports used by websocket communication (e.g., 8090). Note: Campus network may not work.
- Use `ipconfig` / `ifconfig` in your terminal to get the Server IP address. Look for the IPv4 address under the Wi-Fi section.
    ![image](https://github.com/NUS-SSI/TOM-Server-Python/assets/95197450/e26ee547-c132-4a14-af59-f85ec4210a5e)
- Set up [TOM-Client-Unity](https://github.com/TOM-Platform/TOM-Client-Unity) on the HoloLens/Xreal and make sure to update the IP address in `Videos/TOM/tom_config.json`.
- [Optional] Set up [TOM-Client-WearOS](https://github.com/TOM-Platform/TOM-Client-WearOS) on the Android smartwatch and make sure to update the IP address in `app/src/main/java/com/hci/tom/android/network/Credentials.kt`.
- [Troubleshooting] If clients cannot connect to the server via websocket, try the following steps:
  - Ensure that all clients are on the same network as the server. For devices running Windows OS, such as PCs or HoloLens, set the network connection to **private**.
  - Check the firewall settings on the server machine and allow the server application to communicate through the firewall.
  - To test if the server is reachable, use another computer on the same network to run [WebSocketClientTester.html](Tests/WebSocketClientTester.html). This test will attempt to open port 8090 on the server, confirming if it's accessible from another device.


## Application execution

- Export the environment variable `set ENV=dev` (for Windows command prompt) or `$env:ENV = "dev"` (for Windows powershell) or `export ENV=dev` (for Linux/Mac)
- Run `main.py` via `python main.py` (Don't use `py main.py`)
- [Optional] Configure the IDE (e.g., VSCode, PyCharm) to run the server with the environment variable `ENV=dev`
- [Optional] Run the clients after the server has started

### Running tests

- Run `pytest` via `python -m pytest` (or `python -m pytest Tests\...\yy.py` or `python -m pytest Tests\...\yy.py::test_xx` to run specific tests)


### Demos

- [Demo details](https://drive.google.com/drive/folders/1Kfzxs6iYMk0pH0TsPFfOm41jElKVgWop?usp=sharing)

#### Configuring First Person Video (FPV) for Running Service

- Download the first person video [here](https://e.pcloud.link/publink/show?code=kZ1tMTZjijd27TBHO50kxwJQ4zpOV0vs2Gk) (you can download `fpv_short.mp4` or `fpv.mp4`). The videos which one is used (short/full) can be configured in the `.env` file (`FPV_OPTION`).
  <br/>Copy the videos to `Tests/RunningFpv/`.
- Setup the Unity and WearOS clients as mentioned in the [Setup the Clients](#Setup-the-Clients) section.
- Ensure that `DemoRunningCoach.yaml` is set in `/Config`, and `RunningCoach.yaml` is in `/Config/Ignore` on the python server.



## References

- [Structuring Your Project](https://docs.python-guide.org/writing/structure/)
- [Modules](https://docs.python.org/3/tutorial/modules.html#packages)
- [python-testing](https://realpython.com/python-testing/)
- To find/update dependencies, use `conda env export > environment.yml` (or `pip3 freeze > requirements.txt`) [ref](https://stackoverflow.com/questions/31684375/automatically-create-requirements-txt)

### Third-party libraries
- [YOLO-WORLD on WSL](https://docs.google.com/document/d/1VQmvMWa7ZUSpK4lyfhRVaZklh0-3_5UDf_cAtNNclm4/edit?usp=sharing) - Guide for setting up YOLO-WORLD on a WSL machine.
- [cloud-vision-api-python](https://codelabs.developers.google.com/codelabs/cloud-vision-api-python), [google-cloud-vision](https://pypi.org/project/google-cloud-vision/),
- [Detic](https://github.com/facebookresearch/Detic)
- [google-maps](https://developers.google.com/maps/documentation), [google-maps-services-python](https://github.com/googlemaps/google-maps-services-python)
- [OpenAI](https://platform.openai.com/docs/api-reference)
- [Gemini](https://ai.google.dev/gemini-api/docs)
- [Anthropic](https://www.anthropic.com/api)
- [Nominatim OpenStreetMap](https://nominatim.org/release-docs/latest/api/Overview/)
- [Openrouteservice](https://openrouteservice.org/dev/#/api-docs), [OpenStreetMap](https://www.openstreetmap.org/copyright)
- [Geoapify](https://apidocs.geoapify.com/)
- [GeographicLib](https://geographiclib.sourceforge.io/html/python/code.html)
- [Shapely](https://shapely.readthedocs.io/en/stable/geometry.html)
- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- [python-fitbit](https://github.com/orcasgit/python-fitbit)
- [python-vlc](https://pypi.org/project/python-vlc/)
- See other dependencies in [environment-cpu.yml](environment-cpu.yml)
