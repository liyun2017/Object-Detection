#coding=utf-8
import sys, os
import caffe
import numpy as np
import cv2

root = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/../")

# set your model in here
#if len(sys.argv) != 3:
#    print（"Run like python test.py xxx.caffemodel deploy.prototxt"）
#    sys.exit()
deploy = '/media/ly/data/FacialLandmark_Caffe-master/training/net1/deploy.prototxt'
caffe_model = '/media/ly/data/FacialLandmark_Caffe-master/training/net1/model/_iter_100000.caffemodel'
#deploy = sys.argv[2]
#caffe_model = sys.argv[1]
img_folder = '/media/ly/data/FacialLandmark_Caffe-master/testing/test_images/'

net = caffe.Net(deploy, caffe_model, caffe.TEST)

cap = cv2.VideoCapture(0)
while(True):
    ret, im = cap.read()
    if not ret:
        print "video open error"
        break
    # preprocess
    im = cv2.resize(im, net.blobs['data'].data.shape[2:])
    im_ = np.transpose(im, (2, 0, 1))
    im_ = im_.astype(np.float32)
    im_ = im_/127.5-1.0
    # feet forward
    net.blobs['data'].data[0,...] = im_
    out = net.forward()
    key = list(net.blobs.keys())
    output = net.blobs[key[-1]].data
    output = output.reshape((5, 2))
    # change to original image
    output = output * np.array([im.shape[1], im.shape[0]])# net.blobs['data'].data.shape[2:]
    output = output.astype(np.int)
    # save result
    for o in output:
        cv2.circle(im, tuple(o), 2, (0,255,0), -1)
    cv2.imshow("im",im)
    cv2.waitKey(1)
    #print output

