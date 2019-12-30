import torch
import numpy as np
from .yolo.models import Darknet
from .yolo.utils.utils import non_max_suppression, load_classes

MODEL_DEF = "models/yolo/config/yolov3.cfg"
WEIGHTS_PATH = "models/yolo/weights/yolov3.weights"
CLASS_PATH = "models/yolo/data/coco.names"
CONF_THRES = 0.8
NMS_THRES = 0.4
IMG_SIZE = 416

class YoloModel(torch.nn.Module):

    def __init__(self, device):
        super(YoloModel, self).__init__()
        self.device = device
        self.model = Darknet(MODEL_DEF, img_size=IMG_SIZE).to(self.device)
        self.model.load_darknet_weights(WEIGHTS_PATH)
        self.model.eval()
        self.classes = load_classes(CLASS_PATH)
        #print("classes: {}".format(self.classes))
        #print("classes shape: {}".format(np.shape(self.classes)))

    def forward(self, batch):
        detections = self.model(batch)
        detections = non_max_suppression(detections, CONF_THRES, NMS_THRES)
        detections = detections[0][:, 5:]
        detections = detections[detections[:,0].argsort()]
        detections = torch.flip(detections, [0])
        self.probs = detections[:, :1].squeeze()
        #self.ids = detections[:, 1:].squeeze()
        #ids = self.ids.unsqueeze(0) * 0
        self.ids = detections[:, 1:].squeeze().unsqueeze(0)
        self.forward_ids = torch.from_numpy(np.fromiter((i for i in range(self.ids.shape[1])), int)).unsqueeze(0)

        # return ids
        return self.ids

    def get_probs(self):
        return self.probs

    def get_ids(self):
        return self.forward_ids