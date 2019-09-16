#coding=utf-8
import cv2,os

img_folder = '/media/ly/data/FacialLandmark_Caffe-master/test_train/test_img/'
img_list = "/media/ly/data/FacialLandmark_Caffe-master/test_train/test_img_bbx.txt"
for line in open(img_list):
    a = line.split()
    im_path = os.path.join(img_folder, a[0])
    im = cv2.imread(im_path)
    if im is None:
        print("Invaild image: ", im_path)
        continue
    cv2.rectangle(im,(int(a[1]),int(a[2])),(int(a[1])+int(a[3]),int(a[2])+int(a[4])),(255,0,0))
    cv2.imshow("img",im)
    cv2.waitKey()

#对应txt标签为
#0 name
#1-2 左眼
#3-4 右眼
#5-6 鼻尖
#7-8 左嘴角
#9-10 右嘴角

