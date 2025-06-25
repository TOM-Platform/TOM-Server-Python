## A service to support in-context documentation while traveling

- This service is implemented based on the [PANDALens](https://github.com/Synteraction-Lab/PANDALens) project
- However, this does not exactly mimic the original implementation

- To test this, need to include credentials for `GoogleMaps` and `OpenAI` in `credential` folder

### Interactions

- **Voice Commands**:
    - To take photos or verbalize your thoughts, say the voice command, `Ok, TOM`, and speak after the beep sound.
    - To see record moments, use the voice command, `Summary`.
    - To cancel any system prompt, use the voice command, `Hide`.

- **Gesture Commands**:
    - Do the pinch gesture on right hand to take a photo.

- **Ring Mouse Commands**:
    - Ring mouse had natural mapping with the circular menu shown on the screen.

- **Blogs**
    - Generated blogs are saved in `logs/PandaLens/Blogs` folder.