import cv2
import numpy as np

classPath = "data/coco.names"
configPath = "cfg/yolov4-tiny.cfg"
weightPath = "yolov4-tiny.weights"
scale = 0.00392
conf_threshold = 0.5
nms_threshold = 0.4
CONFIDENCE = 0.5

def settext(img, str, local):
    cv2.putText(img, str, local, cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

def getOutput(net):
    layer_names = net.getLayerNames()
    outputLayer = [layer_names[i-1] for i in net.getUnconnectedOutLayers()]
    return outputLayer

class LYL:
    img = None
    boxes = []
    confidences = []
    classIds = []
    classes = []
    indices = None

    def init(self, im):
        self.img = im
        with open(classPath, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]

        H, W, _ = self.img.shape
        net = cv2.dnn.readNet(weightPath, configPath)
        blob = cv2.dnn.blobFromImage(self.img, scale, (416, 416), (0, 0, 0), True, crop=False)
        net.setInput(blob)
        outs = net.forward(getOutput(net))

        for out in outs:
            for detection in out:
                scores = detection[5:]
                classId = np.argmax(scores)
                confidence = scores[classId]
                if confidence > CONFIDENCE:
                    centerX = int(detection[0] * W)
                    centerY = int(detection[1] * H)
                    w = int(detection[2] * W)
                    h = int(detection[3] * H)
                    x = int(centerX - w / 2)
                    y = int(centerY - h / 2)
                    self.classIds.append(classId)
                    self.confidences.append(float(confidence))
                    self.boxes.append([x, y, w, h])
        self.indices = cv2.dnn.NMSBoxes(self.boxes, self.confidences, conf_threshold, nms_threshold)
        return self

    def countObj(self, obj):
        count = 0
        for i in self.indices:
            label = str(self.classes[self.classIds[i]])
            if label == obj:
                count = count + 1
        return count

    def drawObj(self, obj, withLabel = False):
        img = self.img
        for i in self.indices:
            box = self.boxes[i]
            x1 = box[0]
            y1 = box[1]
            w1 = box[2]
            h1 = box[3]
            label = str(self.classes[self.classIds[i]])

            if label == obj or obj == "":
                cv2.rectangle(img, (round(x1), round(y1)), (round(x1 + w1), round(y1 + h1)), (0, 255, 0), 2)
                if withLabel == True:
                    cv2.putText(img, label, (x1 - 10, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        return img