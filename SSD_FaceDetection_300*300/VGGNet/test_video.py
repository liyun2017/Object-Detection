import os
import cv2
import sys
import numpy as np

#caffe_root = "/home/kuan/code/caffe-ssd"

#os.chdir(caffe_root)

#sys.path.insert(0,os.path.join(caffe_root, 'python'))

import caffe

caffe.set_device(0)
caffe.set_mode_gpu()

model_def = "deploy.prototxt"
model_weight = "VGG_wider_face_SSD_300x300_iter_50000.caffemodel"

net = caffe.Net(model_def,model_weight,caffe.TEST)

cap = cv2.VideoCapture(0)
while(True):
    ret, image = cap.read()
    if not ret:
        print "video open error"
        break
    image_data=cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
    image_data=image_data/255.  
    #print image_data.shape
    #print image_data[0,0,:]
    #image_data = caffe.io.load_image(img_path)  #RGB and already normlization(/255.)
    tranformer = caffe.io.Transformer({'data':net.blobs['data'].data.shape})
    tranformer.set_transpose('data', (2,0,1))   # first channel   whc->cwh
    tranformer.set_mean('data',np.array([104,117,123]))
    tranformer.set_raw_scale('data', 255)    #ensure pixel->[0,255]
    #tranformer.set_channel_swap('data', (2,1,0))  #change channel rgb->bgr
    tranformer_image = tranformer.preprocess('data', image_data)
    #print tranformer_image.shape
    #print tranformer_image[:,0,0]

    net.blobs['data'].reshape(1,3,300,300)
    net.blobs['data'].data[...] = tranformer_image
    detect_out = net.forward()['detection_out']

    #print detect_out.shape   (1,1,163,7)
    #print detect_out

    det_label = detect_out[0,0,:,1]
    #print det_label.shape 163
    det_conf  = detect_out[0,0,:,2]
    #print det_conf.shape 163
    det_xmin = detect_out[0,0,:,3]
    det_ymin = detect_out[0,0,:,4]
    det_xmax = detect_out[0,0,:,5]
    det_ymax = detect_out[0,0,:,6]
    
    top_indices = [i for i , conf in enumerate(det_conf) if conf >=0.8]
    #print top_indices
    top_conf = det_conf[top_indices]
    #print top_conf
    top_xmin = det_xmin[top_indices]
    top_ymin = det_ymin[top_indices]
    top_xmax = det_xmax[top_indices]
    top_ymax = det_ymax[top_indices]

    [height,width,_] = image_data.shape
    
    for i in range(min(5, top_conf.shape[0])):
        xmin = int(top_xmin[i] * width)
        ymin = int(top_ymin[i] * height)
        xmax = int(top_xmax[i] * width)
        ymax = int(top_ymax[i] * height)
        cv2.rectangle(image, (xmin,ymin),(xmax,ymax),(255,0,0),5)
#    print image_data.shape
    cv2.imshow("face", image)
    #cv2.imwrite("detection_result.png",image_data)
    if cv2.waitKey(1) == 27:
        break
