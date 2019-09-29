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

    #修改保存路径
    label_out_path = label_path.replace('car_label', 'only_one_size_label')   #替换保存路径
    if not os.path.isdir(os.path.dirname(label_out_path)):
        os.makedirs(os.path.dirname(label_out_path))
    with open(label_out_path,'w+') as w_tdf: # w+是打开原文件将内容删除，另写新内容进去
        for temp in new_txt:
            w_tdf.write(temp)
    return


def split_image(img_path,label_path):
    img = cv2.imread(img_path)
    split_width = img.shape[1] /3 #1224/3=408 0 408 408*2 = 816 1242
    img1 = img[:,0:split_width].copy()
    img2 = img[:,split_width:2*split_width].copy()
    img3 = img[:,2*split_width:3*split_width].copy()
    f=open(label_path, 'r')
    split_lines = f.readlines()
    new_txt_1=[]
    new_txt_2=[]
    new_txt_3=[]
    for split_line in split_lines:
        line=split_line.strip().split()
        xmin=int(float(line[4]))
        ymin=int(float(line[5]))
        xmax=int(float(line[6]))
        ymax=int(float(line[7]))
        #img_ori = cv2.rectangle(img,(xmin,ymin),(xmax,ymax),(255,0,0),1,8)
        #cv2.imshow("img_ori",img_ori)
        #print line
        if xmax < split_width:
            new_txt_1.append(merge(line))
        elif xmax < 2 * split_width:
            if xmin > split_width:   #即方框在第二幅图像x坐标都需要减去分割408的宽度
                line[4] = line[4].replace(line[4], str(int(float(line[4]))-split_width))
                line[6] = line[6].replace(line[6], str(int(float(line[6]))-split_width))
                new_txt_2.append(merge(line))
            else:
                if abs(xmin - split_width) > abs(xmax - split_width):  #第一第二幅图像分割处，且第一幅图像中多一些，故xmax变为408
                    line[6] = line[6].replace(line[6], str(split_width))
                    new_txt_1.append(merge(line))
                else:                           #第一第二幅图像分割处，且第二幅图像中多一些，故xmin变为408，但都需要减去分割408的宽度
                    line[4] = line[4].replace(line[4], str(split_width))
                    line[4] = line[4].replace(line[4], str(int(float(line[4]))-split_width))
                    line[6] = line[6].replace(line[6], str(int(float(line[6]))-split_width))
                    new_txt_2.append(merge(line))
        else:
            if xmin > 2 * split_width:   #即方框在第三幅图像x坐标都需要减去分割2*408的宽度
                line[4] = line[4].replace(line[4], str(int(float(line[4]))-2*split_width))
                line[6] = line[6].replace(line[6], str(int(float(line[6]))-2*split_width))
                new_txt_3.append(merge(line))
            else:
                if abs(xmin - 2 * split_width) > abs(xmax - 2 * split_width):  #第二第三幅图像分割处，且第二幅图像中多一些，故xmax变为408，且都减去408
                    line[6] = line[6].replace(line[6], str(2*split_width))
                    line[4] = line[4].replace(line[4], str(int(float(line[4]))-split_width))
                    line[6] = line[6].replace(line[6], str(int(float(line[6]))-split_width))
                    new_txt_2.append(merge(line))
                else:                           #第二第三幅图像分割处，且第三幅图像中多一些，故xmin变为2*408，但都需要减去分割2*408的宽度
                    line[4] = line[4].replace(line[4], str(2*split_width))
                    line[4] = line[4].replace(line[4], str(int(float(line[4]))-2*split_width))
                    line[6] = line[6].replace(line[6], str(int(float(line[6]))-2*split_width))
                    new_txt_3.append(merge(line))
    
    label_path = label_path.replace("only_one_size_label","split_label")
    img_path = img_path.replace("only_one_size_image","split_image")
    
    #第一幅图像
    if new_txt_1:
        label_out_path_1 = label_path.replace(".txt","_1.txt")
        with open(label_out_path_1,'w+') as w_tdf: # w+是打开原文件将内容删除，另写新内容进去
            img_path_1 = img_path.replace(".png","_1.png")
            cv2.imwrite(img_path_1,img1)
            for temp in new_txt_1:
                w_tdf.write(temp)

    #第二幅图像
    if new_txt_2:
        label_out_path_2 = label_path.replace(".txt","_2.txt")
        with open(label_out_path_2,'w+') as w_tdf: # w+是打开原文件将内容删除，另写新内容进去
            img_path_2 = img_path.replace(".png","_2.png")
            cv2.imwrite(img_path_2,img2)
            for temp in new_txt_2:
                w_tdf.write(temp)       
    
    #第二幅图像
    if new_txt_3:
        label_out_path_3 = label_path.replace(".txt","_3.txt")
        with open(label_out_path_3,'w+') as w_tdf: # w+是打开原文件将内容删除，另写新内容进去
            img_path_3 = img_path.replace(".png","_3.png")
            cv2.imwrite(img_path_3,img3)
            for temp in new_txt_3:
                w_tdf.write(temp)
    print "successful"+label_path

if __name__ == '__main__':
    class_ind=('Car')  #经过modify_annotations_txt.py处理过的label，仅剩下car类型
    #全局变量 测试用
    remove_num = 0
    img_num_modif = 0 
    label_num_modif = 0
    
    cur_dir=os.getcwd()
    # 'label_2' 用于将图像resize到统一尺寸的标签
    # './image_2' 用于将图像resize到统一尺寸的图像
    # car_label 是将label_2中所有car合并的
    #only_one_size_label 是label已经resize之后的结果
    #only_one_size_image 是图像resize到统一尺寸
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
            
            if False:
                #all image resize 1224*370
                resize_image(img_path,label_path)
    #print "remove_num:%d, img_num_modif:%d, label_num_modif:%d "%(remove_num,img_num_modif,label_num_modif)
            if False:
                #打印时，需将上面的 image  label修改路径
                print img_name
                show_image(img_path,label_path,class_ind)
                if cv2.waitKey(0) == 27:
                    break
            
            if True:
                split_image(img_path,label_path)
                
            
            
            
            #train_txt.write('image_2/'+img_name+' '+'label/'+name+'.xml'+'\n')
            #test_name_size.write(name+' '+str(img_size[0])+' '+str(img_size[1])+'\n')
