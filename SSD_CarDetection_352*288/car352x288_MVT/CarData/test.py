# encoding: utf-8
import os,cv2,sys,shutil

from xml.dom.minidom import Document

rootdir = "/media/ly/data/CarData/CarData"

def convertimgset(img_set):
    imgdir = rootdir + "/" + img_set
    img_savedir = rootdir + "/" + "JPEGImages"
    fwrite = open(rootdir + "/ImageSets/Main/" + img_set + ".txt", 'w')
    annotation_dir = "/media/ly/data/CarData/CarData/AnnotationsXml"
    annotation_savedir = "/media/ly/data/CarData/CarData/Annotations"
    index = 0

    #三个参数：分别返回1.父目录 2.所有文件夹名字（不含路径） 3.所有文件名
    for imgdirparent, imgdirdirnames, imgdirfilenames in os.walk(imgdir): 
        for imgdirdirname in imgdirdirnames:    #输出文件夹信息
            dirname = os.path.join(imgdirparent,imgdirdirname)
            print "the full name of the file is: " + dirname #输出文件夹路径信息
            for parent, dirnames, filenames in os.walk(dirname):
                #index = 0
                for filename in filenames:
                    #print "test:" + filename
                    #print "test:" + os.path.join(parent,filename)
                    old_annotation_dir = annotation_dir + "/" + imgdirdirname + "/" + filename.split(".")[0] + ".xml"
                    if not os.path.isfile(old_annotation_dir):
                        continue
                    new_filename = imgdirdirname + "_" +filename
                    fwrite.write(new_filename.split(".")[0] + "\n")
                    shutil.copyfile(os.path.join(parent,filename),img_savedir+"/"+new_filename)
                    shutil.copyfile(old_annotation_dir, annotation_savedir+"/"+new_filename.split(".")[0]+ ".xml" )
                    index = index +1

    print index

if __name__=="__main__":
    img_sets = ["train","val"]
    for img_set in img_sets:
        convertimgset(img_set)
    shutil.move(rootdir + "/ImageSets/Main/" + "train.txt", rootdir + "/ImageSets/Main/" + "trainval.txt")
    shutil.move(rootdir + "/ImageSets/Main/" + "val.txt", rootdir + "/ImageSets/Main/" + "test.txt")
