import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
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

    #get size of image
    #im = np.asarray(image)
    #im_h, im_w, _ = im.shape
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
        #draw.text((xmin, ymin), text='{:.3f}'.format(s))
    h = 5
    # fonts: courbi.ttf (bold and italic), courbd.ttf (bold only)
    fnt_name = 'courbd.ttf'
    fnt = ImageFont.truetype(fnt_name, 30, 0, "unic") #unicode encodings
    fnt2 = ImageFont.truetype(fnt_name, 20, 0, "unic")

    #if FPS > 0:
      #  draw.text((20, 30), text='Chỉ số FPS = {:.1f}'.format(FPS), font=fnt,  fill=(255,0,0,255))

    #draw.text((h, show_h-7*h), text='#faces={:.0f}'.format(len(boxes)) + ', ' + MODEL_PATH, font=fnt2,  fill=(255,0,0,128))
    #draw.text((show_w-35*h, h), text='#faces={:.0f}'.format(len(boxes)), font=fnt2,  fill=(0,255,128,128))
    #draw.text((h, show_h/2), text='#faces={:.0f}'.format(len(boxes)), font=fnt2,  fill=(255,0,0,128))    
    return image_copy

def predict_image(img_path):
    image_array = cv2.imread(img_path)    
    frame_copy = image_array.copy() 
    T1 = time.time()
    image_array = cv2.resize(image_array, (im_detect_wi, im_detect_hi), cv2.INTER_LINEAR) 
    image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
    boxes, scores = people_detector(image_array, score_threshold=face_score_threshold)
    T2 = time.time()
    FPS = 1.0/(T2-T1)
    print('+ FPS: ', FPS)

    img = draw_boxes_on_image(frame_copy, boxes, scores, 0)
    s1 = img_path.split('/')
    s11 = s1[1].split('.')    
    s22 = MODEL_PATH.rsplit('/', 1)[1].split('.')      
   
    img.save('video/results/' + s11[0] + '_' + s22[0] + '.png')    

def predict_folder(img_path):
    
    list_image = [s for s in os.listdir(img_path) if s.endswith('.jpg')] #read jpg files only
    out_path = img_path + 'results/'
    create_folder(out_path)
    fps_sum = 0
    counts = 0
    for im in list_image:
        imPath = img_path+'/'+im
        #print('+ file: ' + im)
        image_array = cv2.imread(imPath)            
        frame_copy = image_array.copy() 
        T1 = time.time()
       
        image_array = cv2.resize(image_array, (im_detect_wi, im_detect_hi), cv2.INTER_LINEAR) 
        image_array = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
        boxes, scores = people_detector(image_array, score_threshold=0.3)

        T2 = time.time()
        FPS = 1.0/(T2-T1)
        print('+ file: ' + im + ', FPS: ' + str(FPS) + ', boxes: ', len(boxes))
        counts = counts + 1
        fps_sum += FPS

        img = draw_boxes_on_image(frame_copy, boxes, scores, 0)
         
        show_img = 1 # 1, 0
        if show_img == 1:
            image_data = np.asarray(img)
            cv2.imshow("Image Detection", cv2.cvtColor(image_data, cv2.COLOR_RGB2BGR))        
            key = cv2.waitKey(1)
            if key == ord('q'):
                break
    print('+ mean FPS: ', fps_sum/counts)

if __name__ == '__main__':
    predict_folder('demo/')
    
#python create_pb.py -s export/run00/1628857224/ -o  models/hdu-pd5g-final.pb
#tensorboard --logdir=models/run00