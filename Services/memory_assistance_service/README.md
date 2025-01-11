# MemoryAssistance

MemoryAssistance is a service that allows you to store and retrieve observed past instances in environment, which can
be in the form of text (transcribed audio) or images.

- The service always saves memories as both text and an image, sampled at regular intervals defined by
  `IMAGE_SAMPLING_DURATION_SECONDS` in [MemoryAssistanceConfig](memory_assistance_config.py).
- It continuously transcribes audio from the microphone but saves it alongside the corresponding image.
- To retrieve a memory, the user must press and hold a designated button (specified by `MEMORY_RECALL_KEY_CODE` in
  [MemoryAssistanceConfig](memory_assistance_config.py)), speak about the memory, and then release the button.
    - Note: Different OS (e.g., MacOS vs Windows) have different key codes.
- The service will search for the memory that best matches the spoken text and display the associated image.

## Requirements

- Enable [local_clip](../../APIs/local_clip/README.md)
- Enable [local_vector_db](../../APIs/local_vector_db/README.md)
- Uses the `Template` scene in the Unity-Client to send the retrieved text and image.