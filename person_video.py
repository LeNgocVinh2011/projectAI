from importlib.resources import path
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import mimetypes
import os
import cv2
import time
from our_detector import PeopleDetector
import tensorflow as tf
print("Tensorflow version: ", tf.__version__)
import json
from imutils import paths

use_gpu_main = 1
device_list = '0'
if use_gpu_main == 1:
    os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
    device_list = '0'
else:
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    device_list = ''

show_w = 768
show_h = 480

CONFIG = 'config.json'
params = json.load(open(CONFIG))
input_params = params['input_pipeline_params']
im_detect_wi, im_detect_hi = input_params['image_size']
MODEL_PATH = input_params['model_name']

print("Model path: ", MODEL_PATH)

face_score_threshold = 0.5 #[0, 1]
people_detector = PeopleDetector(MODEL_PATH, gpu_memory_fraction = 0.25, visible_device_list = device_list)

def create_folder(path_file):
    if not os.path.exists(path_file):
            os.mkdir(path_file)

def draw_rect(drawcontext, xy, outline=None, width=0):
    (x1, y1), (x2, y2) = xy
    points = (x1, y1), (x2, y1), (x2, y2), (x1, y2), (x1, y1)
    drawcontext.line(points, fill=outline, width=width)

def draw_boxes_on_image(image, boxes, scores, FPS):

    image_copy = cv2.resize(image, (show_w, show_h), cv2.INTER_LINEAR)
    image_copy = cv2.cvtColor(image_copy, cv2.COLOR_BGR2RGB)

    k1 = 1.0*show_w/im_detect_wi
    k2 = 1.0*show_h/im_detect_hi

    image_copy = Image.fromarray(image_copy)
    draw = ImageDraw.Draw(image_copy, 'RGBA')
    for b, s in zip(boxes, scores):
        ymin, xmin, ymax, xmax = b
        xmin = int(xmin*k1)
        ymin = int(ymin*k2)
        xmax = int(xmax*k1)
        ymax = int(ymax*k2)
        fill = (255, 255, 255, 0)
        draw_rect(draw, [(xmin, ymin), (xmax, ymax)], 'red', 3)
    h = 5
    fnt_name = 'courbd.ttf'
    fnt = ImageFont.truetype(fnt_name, 30, 0, "unic")
    fnt2 = ImageFont.truetype(fnt_name, 20, 0, "unic")
    return image_copy

def predict_folder(video_path):
    # Read video file
    cap = cv2.VideoCapture(video_path)
    # Properties
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fps = cap.get(cv2.CAP_PROP_FPS)
    base=os.path.basename(video_path)
    file_name = os.path.splitext(base)
    video_writer = cv2.VideoWriter(os.path.join('video', 'results', file_name[0] + '_output.avi'), cv2.VideoWriter_fourcc('P','I','M','1'), fps, (width, height), isColor=True)

    fps_sum = 0
    counts = 0
    # Loop through each frame
    for frame_idx in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))):
        ret, frame = cap.read()
        image_array = frame
        frame_copy = image_array.copy()
        T1 = time.time()
        image_array = cv2.resize(image_array, (im_detect_wi, im_detect_hi), cv2.INTER_LINEAR)
        image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        boxes, scores = people_detector(image_array, score_threshold=0.3)
        T2 = time.time()
        FPS = 1.0/(T2-T1)
        print('+ Frame: ' + str(frame_idx) + ', FPS: ' + str(FPS) + ', boxes: ', len(boxes))
        counts = counts + 1
        fps_sum += FPS

        img = draw_boxes_on_image(frame_copy, boxes, scores, 0)
        # Create folder frame video
        pathFile = os.path.join('video', 'results', file_name[0] + '_frame')
        create_folder(pathFile)
        if len(boxes) != 0:
            video_writer.write(frame_copy)
            cv2.imwrite(pathFile + '/' + file_name[0] + f"{frame_idx}.jpg", frame_copy)
        show_img = 1 # 1, 0
        if show_img == 1:
            image_data = np.asarray(img)
            cv2.imshow("Video Detection", cv2.cvtColor(image_data, cv2.COLOR_RGB2BGR))
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
    print('+ mean FPS: ', fps_sum/counts)

if __name__ == '__main__':
    pathFile = input("Please enter your video path: ")
    if not mimetypes.guess_type(pathFile)[0].startswith('video'):
        print('Video file is invalid!')
        pathFile = input("Please enter your video path again: ")
    predict_folder(pathFile)
