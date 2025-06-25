# TOM-Server-Python

A Python implementation of the server that handles the client data and application logic
- A backend server to handle data processing and running of various services. 
- It takes input from a variety of sources, including video streams and the WebSocket Server. 
- Designed to be easy for developers to implement new services and to be able to support real-time data processing.


## Requirements (Setup Guide)
Follow these steps to set up your development environment:

### 1. Install Python and Conda
- Ensure that `python3` is installed on your system.
- Install **Miniconda** from [here](https://docs.conda.io/en/latest/miniconda.html). 
  - **Note:** Some packages may not work with **Anaconda**, so Miniconda is recommended.

### 2. Install Essential Packages
- Upgrade pip, using `pip install --upgrade pip setuptools wheel`
- Download and install [VLC Player](https://www.videolan.org/vlc/).
- Download and install [FFmpeg](https://ffmpeg.org/) and add it to your environment path.
  - **macOS**: Use Homebrew install: [`brew install ffmpeg`](https://formulae.brew.sh/formula/ffmpeg)
  - **Windows**, Follow [this guide](https://phoenixnap.com/kb/ffmpeg-windows) to manually install FFmpeg and add it to your environment variables.

### 3. Create a Conda Environment
- Create new conda environment `tom` using `conda env create -f environment-cpu.yml`
  - If you already have an existing environment and need to update it, `conda env update --file environment-cpu.yml --prune`. 
  - To completely remove the existing `tom` environment before recreating it,  `conda remove -n tom --all`.
  - For ARM Mac (M1-Mn chip), 
    - If the installation fails due to `pyaudio`, please follow [this](https://stackoverflow.com/questions/33513522/when-installing-pyaudio-pip-cannot-find-portaudio-h-in-usr-local-include)
    - If the installation fails due to `egg_info`, change the dependency `psycopg2` to `psycopg2-binary` in `environment-cpu.yml`
    - If the installation fails due to `googlemaps`, either remove it from `environment-cpu.yml` or install it separately using `pip install --use-pep517 googlemaps` after activating the `tom` environment.
  - For torchaudio IO functions on MacOS, if you get an error with `torchaudio.load` function
    - The ffmpeg<7 libraries can be installed with : `conda install -c conda-forge 'ffmpeg<7'`
    - Refer to https://docs.pytorch.org/audio/main/installation.html for more details

### 4. Activate the Conda Environment
- Once the environment is set up, activate it using, `conda activate tom`


## Installation
Follow these steps to set up the project on your computer.

### 1. Clone the Project
- Clone the repository to your computer and navigate inside the project folder
  -  ```sh
      git clone <your-repository-url>
      cd TOM-Server-Python
     ```
  - **Note**: If you plan to contribute, [fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo) the repository first and then clone your forked version. This is necessary because the main repository is read-only.

### 2. Download the Pretrained Weights
- Download the pretrained weights for YOLOv8 from [Ultralytics](https://github.com/ultralytics/ultralytics) (e.g., [yolov8n.pt](https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt)).
  - Move the downloaded file to the `Processors/Yolov8/weights` directory. If the directory does not exist, create it. 
  - Rename the file to `model.pt` (i.e., `Processors/Yolov8/weights/model.pt`).
  - [Optional] Use a custom YOLOv8 model (or train one) for other detection (e.g., emotion, face) purposes.
  - [Optional] To enable pose landmark, face detection, audio classification  with MediaPipe, manually download the following model weights:
    - **Pose Landmark model** from [Pose Landmarker](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker#models):
      - Rename the file to `pose_landmarker.task`.  
      - Place it in the `Processors/PoseLandmarkDetection/weights/` directory.
    - **Face Detection model** from [Face Detector](https://ai.google.dev/edge/mediapipe/solutions/vision/face_detector#models):
      - Rename the file to `face_detector.tflite`.  
      - Place it in the `Processors/FaceDetection/weights/` directory.
    - **Audio Classification (YamNet) model** from [Audio Classifier](https://ai.google.dev/edge/mediapipe/solutions/audio/audio_classifier#yamnet_model_recommended):
      - Rename the file to `yamnet.tflite`.  
      - Place it in the `Processors/BackgroundAudioClassifier/weights/` directory.

### 3. Set Up Environment Files
Environment files store project-specific settings. Follow these steps:
- **For Development Environment**:
  - Copy `.sample_env` and paste it as `.env.dev` in the (root) project folder. (e.g., `cp .sample_env .env.dev`)
  - [Optional] Update the file as needed. 
    - Example: `CAMERA_VIDEO_SOURCE = 0` uses the default camera. You can change it to any video stream/URL/file source.
    - [Optional] If using a HoloLens camera, enable it by uncommenting the following lines in [main.py](main.py) and update the IP address in `credential/hololens_credential.json`:
      ```python
      # from APIs.hololens import hololens_portal
      # hololens_portal.set_api_credentials()
      # hololens_portal.set_hololens_as_camera()
      ```
- **For Testing Environment**:
  - Copy `.sample_env` and paste it as `.env.test` in the (root) project folder. (e.g., `cp .sample_env .env.test`)

### 4. [Optional] Create Credential Files
Some [Third-party services](#Third-party-libraries) require credentials. If you are using them, create credential files inside a new `credential` folder. *(Note: JSON format must be correct.)*
- **Hololens Credentials**: 
  - Create a file `credential/hololens_credential.json` with Hololens credentials such as `{"ip": "IP","username": "USERNAME","password": "PASSWORD"}`
    - [Configure](https://learn.microsoft.com/en-us/windows/mixed-reality/develop/advanced-concepts/using-the-windows-device-portal#connecting-over-wi-fi) the Hololens Device Portal. Save [your credentials](https://docs.microsoft.com/en-us/windows/mixed-reality/develop/platform-capabilities-and-apis/using-the-windows-device-portal#creating-a-username-and-password) to `credential/hololens_credential.json`
- **Google Cloud API Credentials**:
  - Create a file `credential/google_cloud_credentials.json` with [Google Cloud API](https://cloud.google.com/apis) credentials.
    - Follow [authentication](https://github.com/GoogleCloudPlatform/hackathon-toolkit/blob/master/vision/README.md#authentication) to get json key file and rename it to `google_cloud_credentials.json`
- **OpenAI Credentials**:
  - Create a file `credential/openai_credential.json` with [OpenAI](https://platform.openai.com/docs/overview) credentials such as `{"openai_api_key": "KEY"}`
- **Gemini API Credentials**:
  - Create a file `credential/gemini_credential.json` with [Gemini](https://ai.google.dev/gemini-api/docs/) credentials such as `{"gemini_api_key": "KEY"}`
- **Anthropic API Credentials**:
  - Create a file `credential/anthropic_credential.json` with [Anthropic](https://www.anthropic.com/api) credentials such as `{"anthropic_api_key": "KEY"}`
- **Google Maps API Credentials**:
  - Create a file `credential/google_maps_credential.json` with Google Maps credentials such as `{"map_api_key": "KEY"}`
    - Current Google Maps APIs used:
      - [Places API](https://developers.google.com/maps/documentation/places/web-service/overview)
      - [Directions API](https://developers.google.com/maps/documentation/directions/overview)
      - [Static Maps API](https://developers.google.com/maps/documentation/maps-static/overview)
      - [Geocoding API](https://developers.google.com/maps/documentation/geocoding/)
      - [Geolocation API](https://developers.google.com/maps/documentation/geolocation/overview)
    - To use Google Maps API, you need to have a Google Cloud Platform (GCP) account to get an API key and enable the APIs shown above.
- **OpenRouteService API Credentials**:
  - Create a file `credential/ors_credential.json` with [Openrouteservice](https://openrouteservice.org/) credentials such as `{"map_api_key": "KEY"}`
- **Geoapify API Credentials**:
  - Create a file `credential/geoapify_credential.json` with [Geoapify](https://www.geoapify.com/) credentials such as `{"map_api_key": "KEY"}`
- **Fitbit API Credentials**:
  - Create a file `credential/fitbit_credential.json` with Fitbit credentials such as `{"client_id": "ID","client_secret": "SECRET"}`

### 5. [Optional] Running Assistance on a Treadmill
- If you want to simulate running assistance on a treadmill, follow the steps in [Running Demo Service](#configuring-first-person-video-for-running-service)

### 6. [Optional] Using Local APIs
- If you plan to use local APIs (e.g., [local_vector_db](APIs/local_vector_db/README.md)), check their individual `README.md` files for configuration steps.
- Note: Certain services (e.g., [memory_assistance_service](Services/memory_assistance_service)) depends on those local APIs.


## Setup the clients
Follow these steps to ensure your clients (e.g., **HoloLens, Xreal, WearOS Watch**) can connect to the server properly.

### 1. Connect Clients to the Same Wi-Fi Network
- Ensure all client devices are connected to the **same Wi-Fi network** as the server.
- Use a **private** network, as public networks may block ports used for WebSocket communication (e.g., **8090**).
  - **Note:** Campus networks or public hotspots may not work due to firewall restrictions.

### 2. Find the Server IP Address
- Use the following command in your terminal to get the **Server IP address**:
  - **Windows:** Open Command Prompt and run:
    ```sh
    ipconfig
    ```
  - **Mac/Linux:** Open Terminal and run:
    ```sh
    ifconfig
    ```
- Look for the **IPv4 address** under the **Wi-Fi** section.
  ![image](https://github.com/NUS-SSI/TOM-Server-Python/assets/95197450/e26ee547-c132-4a14-af59-f85ec4210a5e)

### 3. Set Up Clients

#### **(a) HoloLens / Xreal / Quest3 Setup**
- Install [TOM-Client-Unity](../TOM-Client-Unity) on your **HoloLens/Xreal/Quest3** device.
- Update the IP address in `Videos/TOM/tom_config.json`.


#### **(b) [Optional] Brilliant Labs Frame**
- Pair the [Brilliant Labs Frame](https://docs.brilliant.xyz/frame/frame/) to the server (laptop) via Bluetooth.
- Makesure the device is connected via Bluetooth.


#### **(c) [Optional] Android Smartwatch Setup (WearOS)**
- Install [TOM-Client-WearOS](../TOM-Client-WearOS) on your **WearOS smartwatch**.
- Update the IP address in `app/src/main/java/com/hci/tom/android/network/Credentials.kt`.


### 4. Troubleshooting Connection Issues

If clients cannot connect to the server via WebSocket, try these steps:

- Ensure all devices are on the same Wi-Fi network
  - Windows devices (e.g., **PCs or HoloLens**) must set their network connection to **private**.
- Check firewall settings on the server machine
  - Allow the **server application** to communicate through the firewall.
- Test if the server is reachable
  - Use another computer on the same network to open [`Tests/WebSocketClientTester.html`](Tests/WebSocketClientTester.html)
  - This test will attempt to open **port 8090** on the server. If it fails, check the network and firewall settings.


## Application Execution

### 1. Use the `tom` environment:
   - Activate it via the command line: `conda activate tom` (for Conda users) or through your IDE.
### 2. Export the environment variable `ENV`:
   - For Windows Command Prompt:
     ```cmd
     set ENV=dev
     ```
   - For Windows PowerShell:
     ```powershell
     $env:ENV = "dev"
     ```
   - For Linux/Mac:
     ```bash
     export ENV=dev
     ```
### 3. Run the application:
   - Execute `main.py` using:
     ```bash
     python main.py
     ```
     *(Avoid using `py main.py`.)*
### 4. [Optional] Configure your IDE 
  - Configure the IDE (e.g., [VSCode](https://code.visualstudio.com/docs/python/environments), [VSCode-Debug](https://code.visualstudio.com/docs/python/debugging), [PyCharm](https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html)) to run the server with the environment variable `ENV=dev`.
### 5. [Optional] Run the clients
  - Run the clients after the server has started.


## Running Tests

- Run `pytest` via `python -m pytest` (or `python -m pytest Tests\...\yy.py` or `python -m pytest Tests\...\yy.py::test_xx` to run specific tests)


## Demos

- See the implemented [services](Services)
- Examples
    - [Running Service](https://docs.google.com/document/d/1BQ3E__t1UrvDw2LkB2W7rEe1mjQY0k54Jqc03cd2o94/edit?usp=sharing)
    - [Martial Arts Service](https://docs.google.com/presentation/d/1aqiftWgnduz5ie8XZ-aKVJ_jFcnK_77X_ZSRo22rBWw/edit?usp=sharing)
    - [PandaLens Service](https://docs.google.com/presentation/d/1FVehX40EAYrX6l39N0dlkxh9tcJR3IWYLJEXiHfLFmg/edit?usp=sharing)

### Configuring First-Person Video for Running Service

- Download the first person video [here](https://e.pcloud.link/publink/show?code=kZ1tMTZjijd27TBHO50kxwJQ4zpOV0vs2Gk) (you can download `fpv_short.mp4` or `fpv.mp4`).
  - Copy the video/s to `Tests/RunningFpv/`.
  - Configure which video to be used (short/full) in the `.env` file (`FPV_OPTION`). 
- Set up the Unity and WearOS clients as mentioned in the [Setup the Clients](#Setup-the-Clients) section.
- Ensure that `DemoRunningCoach.yaml` is set in `/Config`, and `RunningCoach.yaml` is in `/Config/Ignore` on the python server.


## Development

- See [DeveloperGuide.md](DeveloperGuide.md) for more details on development guidelines and adding new services/components.


## References
- [Structuring Your Project](https://docs.python-guide.org/writing/structure/)
- [Modules](https://docs.python.org/3/tutorial/modules.html#packages)
- [python-testing](https://realpython.com/python-testing/)
- To find/update dependencies, use `conda env export > environment.yml` (or `pip3 freeze > requirements.txt`) [ref](https://stackoverflow.com/questions/31684375/automatically-create-requirements-txt)

### Third-party Libraries
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
