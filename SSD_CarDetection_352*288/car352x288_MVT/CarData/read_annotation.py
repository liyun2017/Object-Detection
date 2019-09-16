# encoding: utf-8
import cv2,os
import numpy as np
import  xml.dom.minidom
img_dir = "/media/ly/data/CarData/car352x288_MVT/CarData/test/MVI_63562" #ok MVI_20011  #problem MVI_39811 after 200
anno_dir = "/media/ly/data/CarData/car352x288_MVT/CarData/AnnotationsXml/MVI_63562"
img = cv2.imread("/media/ly/data/CarData/car352x288_MVT/CarData/test/MVI_63562/img00001.jpg")
#cv2.imshow("img",img)
#cv2.waitKey(0)
image = np.zeros(img.shape, np.uint8)
def on_EVENT_LBUTTONDOWN(event, x, y, flags, param):
    global image
    if event == cv2.EVENT_LBUTTONDOWN:
        xy = "%d,%d" % (x, y)
        print xy
        cv2.circle(image, (x, y), 1, (255, 0, 0), thickness = -1)
        image = cv2.putText(image, xy, (x, y), cv2.FONT_HERSHEY_PLAIN,
                    1.0, (0,0,0), thickness = 1)
        cv2.imshow("image", image)

cv2.namedWindow("image")
for parent, dirnames, filenames in os.walk(img_dir):
    for filename in filenames:
        image_path = os.path.join(parent,filename)
        anno_path =  os.path.join(anno_dir,filename.split(".")[0]+".xml")
        if not os.path.isfile(anno_path):
            continue
        image = cv2.imread(image_path)
        print anno_path
        image = cv2.putText(image, filename, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 1)

        #read annotion anr plot bbox
        dom = xml.dom.minidom.parse(anno_path)
        root = dom.documentElement
        xmin=dom.getElementsByTagName("xmin")
        ymin=dom.getElementsByTagName("ymin")
        xmax=dom.getElementsByTagName("xmax")
        ymax=dom.getElementsByTagName("ymax")
        if xmin.length != xmax.length:
            break
        print xmin.length
        print xmin[0].firstChild.data
        for i in range(xmin.length):
            gtbbox_start = (int(xmin[i].firstChild.data),
                      int(ymin[i].firstChild.data)) 
            gtbbox_stop = (int(xmax[i].firstChild.data),        
                      int(ymax[i].firstChild.data))       
            print gtbbox_start + gtbbox_stop
            image = cv2.rectangle(image, gtbbox_start, gtbbox_stop, (255,0,0),3)
#            cv2.imshow("image",image)
#            cv2.waitKey(0)

        cv2.setMouseCallback("image", on_EVENT_LBUTTONDOWN)
        cv2.imshow("image",image)
        if cv2.waitKey(0) == 27:
            break
