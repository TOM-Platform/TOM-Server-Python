from ultralytics import YOLO

model = YOLO("model.pt")  # load a pretrained model

# Train the model
model.train(data="training.yaml", epochs=25)
metrics = model.val()
# results = model("https://ultralytics.com/images/bus.jpg")
success = model.export(format="onnx")

# model.predict(
#    source='https://media.roboflow.com/notebooks/examples/dog.jpeg',
#    conf=0.25
# )
