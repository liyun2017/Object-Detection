#encoding=utf8
'''
Detection with SSD
In this example, we will load a SSD model and use it to detect objects.
'''

import os
import sys
import argparse
import numpy as np
from PIL import Image, ImageDraw
# Make sure that caffe is on the python path:
caffe_root = "/home/ly/caffe-weiliu/caffe"
os.chdir(caffe_root)
sys.path.insert(0, os.path.join(caffe_root, 'python'))
import caffe
import cv2
import types

from google.protobuf import text_format
from caffe.proto import caffe_pb2


def get_labelname(labelmap, labels):
    num_labels = len(labelmap.item)
    labelnames = []
    if type(labels) is not list:
        labels = [labels]
    for label in labels:
        found = False
        for i in xrange(0, num_labels):
            if label == labelmap.item[i].label:
                found = True
                labelnames.append(labelmap.item[i].display_name)
                break
        assert found == True
    return labelnames

class CaffeDetection:
    def __init__(self, gpu_id, model_def, model_weights, image_resize, labelmap_file):
        caffe.set_device(gpu_id)
        caffe.set_mode_gpu()

        self.image_resize = image_resize
        # Load the net in the test phase for inference, and configure input preprocessing.
        self.net = caffe.Net(model_def,      # defines the structure of the model
                             model_weights,  # contains the trained weights
                             caffe.TEST)     # use test mode (e.g., don't perform dropout)
         # input preprocessing: 'data' is the name of the input blob == net.inputs[0]
        self.transformer = caffe.io.Transformer({'data': self.net.blobs['data'].data.shape})
        self.transformer.set_transpose('data', (2, 0, 1))
        self.transformer.set_mean('data', np.array([104, 117, 123])) # mean pixel
        # the reference model operates on images in [0,255] range instead of [0,1]
        self.transformer.set_raw_scale('data', 255)
        # the reference model has channels in BGR order instead of RGB
        self.transformer.set_channel_swap('data', (2, 1, 0))

        # load PASCAL VOC labels
        file = open(labelmap_file, 'r')
        self.labelmap = caffe_pb2.LabelMap()
        text_format.Merge(str(file.read()), self.labelmap)

    def detect(self, image_input, conf_thresh=0.7, topn=10):
        '''
        SSD detection
        '''
        # set net to batch size of 1
        # image_resize = 300
        self.net.blobs['data'].reshape(1, 3, self.image_resize[0],self.image_resize[1]) #nchw
        image = np.zeros(shape=(self.image_resize[0],self.image_resize[1]))
        if type(image_input) is types.StringType:
            image = caffe.io.load_image(image_input)
            print "before input net image width :%s, height:%s" %(image.shape[1], image.shape[0])
        else:
            image = image_input.copy()
            image=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
            image=image/255. 
            print "before input net video width :%s, height:%s"%(image.shape[1], image.shape[0])
        #Run the net and examine the top_k results
        transformed_image = self.transformer.preprocess('data', image)
        print transformed_image.shape #(3,288,352)
        self.net.blobs['data'].data[...] = transformed_image

        # Forward pass.
        detections = self.net.forward()['detection_out']

        # Parse the outputs.
        det_label = detections[0,0,:,1]
        det_conf = detections[0,0,:,2]
        det_xmin = detections[0,0,:,3]
        det_ymin = detections[0,0,:,4]
        det_xmax = detections[0,0,:,5]
        det_ymax = detections[0,0,:,6]

        # Get detections with confidence higher than 0.6.
        top_indices = [i for i, conf in enumerate(det_conf) if conf >= conf_thresh]

        top_conf = det_conf[top_indices]
        top_label_indices = det_label[top_indices].tolist()
        top_labels = get_labelname(self.labelmap, top_label_indices)
        top_xmin = det_xmin[top_indices]
        top_ymin = det_ymin[top_indices]
        top_xmax = det_xmax[top_indices]
        top_ymax = det_ymax[top_indices]

        result = []
        for i in xrange(min(topn, top_conf.shape[0])):
            xmin = top_xmin[i] # xmin = int(round(top_xmin[i] * image.shape[1]))
            ymin = top_ymin[i] # ymin = int(round(top_ymin[i] * image.shape[0]))
            xmax = top_xmax[i] # xmax = int(round(top_xmax[i] * image.shape[1]))
            ymax = top_ymax[i] # ymax = int(round(top_ymax[i] * image.shape[0]))
            score = top_conf[i]
            label = int(top_label_indices[i])
            label_name = top_labels[i]
            result.append([xmin, ymin, xmax, ymax, label, score, label_name])
        return result


def get_image(image_path):
    img_files = []
    for parent, imgdirs,imgnames in os.walk(image_path):
        for imgname in imgnames:
            img_file = os.path.join(parent,imgname)
            img_files.append(img_file)
    return img_files

def image_save_result(image_file,result,save_path):
    img = Image.open(image_file)
    draw = ImageDraw.Draw(img)
    width, height = img.size
    print "ori image width:%s, height:%s" %(width, height)
    for item in result:
        xmin = int(round(item[0] * width))
        ymin = int(round(item[1] * height))
        xmax = int(round(item[2] * width))
        ymax = int(round(item[3] * height))
        print [xmin, ymin, xmax, ymax]
        draw.rectangle([xmin, ymin, xmax, ymax], outline=(255, 0, 0))
        draw.text([xmin, ymin], item[-1] + str(item[-2]), (0, 0, 255))
        #print item
        #print [xmin, ymin, xmax, ymax]
        #print [xmin, ymin], item[-1]
    tmp_list = image_file.split('/')
    img.save(save_path + str(tmp_list[-1]))

def image_process(args):
    save_path = "./result/"
    detection = CaffeDetection(args.gpu_id,
                               args.model_def, args.model_weights,
                               args.image_resize, args.labelmap_file)
    img_files = get_image(args.image_path)
    for img_file in img_files:
        result = detection.detect(img_file)
        print "detection result :"
        print result
        image_save_result(img_file,result,save_path)

def video_save_result(image,result,save_path):
    [height,width,_] = image.shape
    for item in result:
        xmin = int(round(item[0] * width))
        ymin = int(round(item[1] * height))
        xmax = int(round(item[2] * width))
        ymax = int(round(item[3] * height))
        cv2.imwrite(save_path,image[ymin:ymax,xmin:xmax])

def video_draw_result(image,result):
    [height,width,_] = image.shape
    print  "ori video width:%s, height:%s" %(width, height)
    for item in result:
        xmin = int(round(item[0] * width))
        ymin = int(round(item[1] * height))
        xmax = int(round(item[2] * width))
        ymax = int(round(item[3] * height))
        print (xmin,ymin),(xmax,ymax)
        cv2.rectangle(image, (xmin,ymin),(xmax,ymax),(255,0,0),2)
        image = cv2.putText(image, item[-1]+str(item[-2]), (xmin,ymin), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        #print item
        #print [xmin, ymin, xmax, ymax]
        #print [xmin, ymin], item[-1]

def video_process(args):
    save_path = "./retrain/data/"
    detection = CaffeDetection(args.gpu_id,
                               args.model_def, args.model_weights,
                               args.image_resize, args.labelmap_file)
    cap = cv2.VideoCapture(args.video_path)
    name_count = 10000 #与kitti 7841 有所区别
    while(True):
        ret, image = cap.read()
        result = detection.detect(image)
        print "detection result :"
        print result
        #video_save_result(image,result,save_path+str(name_count)+'.png')
        video_draw_result(image,result)
        cv2.imshow("iamge",image)
        if cv2.waitKey(1) == 27:
            break
        name_count = name_count + 1
def main(args):
    '''main '''
    if args.model == 'image':
        print "start image process"
        image_process(args)
    else:
        print "start video process"
        video_process(args)



def parse_args():
    '''parse args'''
    parser = argparse.ArgumentParser()
    parser.add_argument('--gpu_id', type=int, default=0, help='gpu id')
    parser.add_argument('--labelmap_file',
                        default='/media/ly/data/CarData/car352x288_splitKitti_MVT_indoor/models/labelmap_voc.prototxt')
    parser.add_argument('--model_def',
                        default='/media/ly/data/CarData/car352x288_splitKitti_MVT_indoor/models/deploy.prototxt')
    parser.add_argument('--image_resize', default=(288,352), type=int)
    parser.add_argument('--model_weights',
                        default='/media/ly/data/CarData/car352x288_splitKitti_MVT_indoor/models/Kitti_and_MVT/car352x288_splitKitti_MVT_indoorSSD_352x288_iter_50000.caffemodel')
    parser.add_argument('--model', default='image')
    parser.add_argument('--image_path', default='/media/ly/data/CarData/car352x288_split_KITTI/video/video_to_image_car_1')
    parser.add_argument('--video_path', default='0')
    return parser.parse_args()

if __name__ == '__main__':
    main(parse_args())
