#encoding:utf-8
import os
import cv2

#show image with groundtruth
def show_image(img_path,label_path,class_ind):
    img = cv2.imread(img_path)
    f=open(label_path)
    split_lines = f.readlines()
    print img.shape
    for split_line in split_lines:
        line=split_line.strip().split()
        if line[0] in class_ind:
            xmin=int(float(line[4]))
            ymin=int(float(line[5]))
            xmax=int(float(line[6]))
            ymax=int(float(line[7]))
            cv2.rectangle(img,(xmin,ymin),(xmax,ymax),(255,0,0),1,8)
    cv2.imshow('img',img)              

def merge(line):
    each_line=''
    for i in range(len(line)):
        if i!= (len(line)-1):
            each_line=each_line+line[i]+' '
        else:
            each_line=each_line+line[i] # 最后一条字段后面不加空格
    each_line=each_line+'\n'
    return (each_line)


'''
图像大小不一，将图像大小resize到统一大小，如1224*370
并不采用图像resize方法，仅仅将多出来的部分剪切掉
并将对应的坐标点进行处理，剪切掉一部分
input：
	image path
	label path
	cut image size
'''
def resize_image(img_path,label_path,img_size=(1224,370)):
    global img_num_modif,label_num_modif,remove_num #全局变量

    img = cv2.imread(img_path)
    f=open(label_path, 'r')
    split_lines = f.readlines()
    if len(split_lines) == 0:
        #os.remove(label_path) #TODO 不能先删除 直接返回 不往后操作就行了
        remove_num = remove_num +1
        return
    #shape 0:h 1:w 2:c
    ori_h,ori_w,c = img.shape
    if ori_w == img_size[0]:
        img_num_modif = img_num_modif+1 #测试多少张图片是不做resize
        return
    if ori_w > img_size[0] and ori_h > img_size[1]:
        new_img = img[0:img_size[1], 0:img_size[0]]
        img_out_path = img_path.replace('image_2', 'only_one_size_image')
        cv2.imwrite(img_out_path,new_img)
    new_txt=[]
    for split_line in split_lines:
        line=split_line.strip().split()
        xmin=int(float(line[4]))
        ymin=int(float(line[5]))
        xmax=int(float(line[6]))
        ymax=int(float(line[7]))
        if xmin > img_size[0] or ymin > img_size[1]:
            continue
        if xmax > img_size[0]:
            line[6] = line[6].replace(line[6], str(img_size[0]))
        if ymax > img_size[1]:
            line[7] = line[7].replace(line[7], str(img_size[1]))
        label_num_modif = label_num_modif + 1        
        new_txt.append(merge(line))

    label_out_path = label_path.replace('car_label', 'only_one_size_label')
    if not os.path.isdir(os.path.dirname(label_out_path)):
        os.makedirs(os.path.dirname(label_out_path))
    with open(label_out_path,'w+') as w_tdf: # w+是打开原文件将内容删除，另写新内容进去
        for temp in new_txt:
            w_tdf.write(temp)
    return


if __name__ == '__main__':
    class_ind=('Car')  #经过modify_annotations_txt.py处理过的label，仅剩下car类型
    output_floder = "/media/ly/data/baidunetdiskdownload/KITTI/velodyne_modify/odometry/new_image/"

    #全局变量 测试用
    remove_num = 0
    img_num_modif = 0 
    label_num_modif = 0

    cur_dir=os.getcwd()
    # 'label_2' 用于将图像resize到统一尺寸的标签
    # './image_2' 用于将图像resize到统一尺寸的图像
    # car_label 是将label_2中所有car合并的
    dir=os.path.join(cur_dir,'only_one_size_label')
    #train_txt= open('train.txt','w')
    #test_name_size= open('test_name_size.txt','w')
    for parent, dirnames, filenames in os.walk(dir):
        for file_name in filenames:
            #图片路径
            name= file_name[:-4]
            img_name=name+'.png'
            img_path=os.path.join('./only_one_size_image',img_name)
            #标签路径
            label_path=os.path.join(parent, file_name)
            #all image resize 1224*370
            #resize_image(img_path,label_path)
#    print "remove_num:%d, img_num_modif:%d, label_num_modif:%d "%(remove_num,img_num_modif,label_num_modif)

            print img_name
            show_image(img_path,label_path,class_ind)
            if cv2.waitKey(0) == 27:
                break


            #train_txt.write('image_2/'+img_name+' '+'label/'+name+'.xml'+'\n')
            #test_name_size.write(name+' '+str(img_size[0])+' '+str(img_size[1])+'\n')
