#encoding:utf-8
import os,cv2,sys,shutil

rootdir = "/media/ly/data/CarData/car352x288_split_KITTI"
def split(img_path,label_path,trainval_txt,test_txt):
    files =  os.listdir(img_path)
    trainval_num = len(files) * 0.8
    test_num = len(files) - trainval_num
    print trainval_num,test_num
    f_trainval = open(trainval_txt,'w+')
    f_test = open(test_txt,'w+')
    count = 0
    for file in files:
        if os.path.isdir(file):
            continue
        tmp = file[:-4]
        print tmp
        if os.path.exists(label_path+"/"+tmp+".txt"):
            tmp = tmp + "\n"
            if count <= trainval_num:            
                f_trainval.write(tmp)
            else:
                f_test.write(tmp)
        count = count + 1

#img_path 是KITTI的split数据
#label_path 是KITTI的split数据的标签
#按照voc的格式保存数据

if __name__=="__main__":
    #读取文件，保存文件名，分割为trainval test数据，0.8:0.2
    img_path = rootdir + "/JPEGImages"
    label_path = rootdir + "/Annotations"
    trainval_txt = rootdir + "/ImageSets/Main/" + "trainval.txt"
    test_txt = rootdir + "/ImageSets/Main/" + "test.txt"
    split(img_path,label_path,trainval_txt,test_txt)

