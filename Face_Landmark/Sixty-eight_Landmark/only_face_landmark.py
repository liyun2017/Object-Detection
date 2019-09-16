import sys
import os

import time
import pprint

import caffe
import cv2
import numpy as np

def file_list_fn(path):

    file_list = []
    files = os.listdir(path)
    for f in files:
        file_list.append(f)
    return file_list

net_work_path = '/media/ly/data/face-landmark/model/landmark_deploy.prototxt'
weight_path = '/media/ly/data/face-landmark/model/VanFace.caffemodel'
images_dir = '/media/ly/data/FacialLandmark_Caffe-master/testing/test_images/'
result_dir = '/media/ly/data/face-landmark/result/test_image_result/'

image_list = file_list_fn(images_dir)
caffe.set_mode_cpu()
net = caffe.Net(net_work_path, weight_path, caffe.TEST)
net.name = 'FaceThink_face_landmark_test'

total_landmark_time = 0.0
for image in image_list:
    print("Processing file: {}".format(image))
    img = cv2.imread(images_dir + image)
    det_start_time = time.time()
    gary_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    w = 60
    h = 60
    print image
    res = cv2.resize(gary_img, (w, h), 0.0, 0.0, interpolation=cv2.INTER_CUBIC)
    resize_mat = np.float32(res)
    m = np.zeros((w, h))
    sd = np.zeros((w, h))
    mean, std_dev = cv2.meanStdDev(resize_mat, m, sd)
    new_m = mean[0][0]
    new_sd = std_dev[0][0]
    new_img = (resize_mat - new_m) / (0.000001 + new_sd)

    if new_img.shape[0] != net.blobs['data'].data[0].shape or new_img.shape[1] != net.blobs['data'].data[1].shape:
        print "Incorrect " + image + ", resize to correct dimensions."

    net.blobs['data'].data[...] = new_img
    landmark_time_start = time.time()
    out = net.forward()
    landmark_time_end = time.time()
    landmark_time = landmark_time_end - landmark_time_start
    total_landmark_time += landmark_time
    print "landmark time is {}".format(landmark_time)
    points = net.blobs['Dense3'].data[0].flatten()
    print points
    point_pair_l = len(points)
    for i in range(point_pair_l / 2):
        #x = points[2*i] * (x2 - x1) + x1
        #y = points[2*i+1] * (y2 - y1) + y1
        x = points[2*i] * w
        y = points[2*i+1] * h
        cv2.circle(res, (int(x), int(y)), 1, (0, 0, 255), 2)
    cv2.imwrite(result_dir + image, res)

print total_landmark_time
per_image_landmark_time = total_landmark_time / len(image_list)

print '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'
print "per image detecting time is {}".format(per_image_landmark_time)



