# encoding: utf-8
import os,cv2,sys,shutil

from xml.dom.minidom import Document

rootdir = "/media/ly/data/CarData/CarData"

def convertimgset(img_set):
    imgdir = rootdir + "/" + img_set

    index = 0

    #三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名字
    for parent, dirnames, filenames in os.walk(imgdir): 
        for dirname in dirnames:    #输出文件夹信息
            print "parent is: " + parent #/media/ly/data/CarData/CarData/val
            print "dirname is: " + dirname #MVI_63562
        for filename in filenames:
            print "parent is: " + parent  #/media/ly/data/CarData/CarData/val/MVI_63563
            print "filename is: " + filename  #img00091.jpg
            print "the full name of the file is: " + os.path.join(parent,filename) #输出文件路径信息
            index = index +1
    print index

if __name__=="__main__":
    img_sets = ["train","val"]
    for img_set in img_sets:
        convertimgset(img_set)
