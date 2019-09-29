#encoding:utf-8
import os
import cv2


def merge(line):
    each_line=''
    for i in range(len(line)):
        if i!= (len(line)-1):
            each_line=each_line+line[i]+' '
        else:
            each_line=each_line+line[i] # 最后一条字段后面不加空格
    each_line=each_line+'\n'
    return (each_line)

image_path = "/media/ly/data/baidunetdiskdownload/KITTI/velodyne_modify/odometry/only_one_size_image/000025.png"
label_path = "/media/ly/data/baidunetdiskdownload/KITTI/velodyne_modify/odometry/only_one_size_label/000025.txt"
img = cv2.imread(image_path)
print img.shape  #1224 370
#cv2.imshow("img",img)

split_width = img.shape[1] /3 #1224/3=408 0 408 408*2 = 816 1242
#print split_width   #408
img1 = img[:,0:split_width].copy()
img2 = img[:,split_width:2*split_width].copy()
img3 = img[:,2*split_width:3*split_width].copy()
cv2.imshow("img1",img1)
cv2.imshow("img2",img2)
cv2.imshow("img3",img3)
cv2.waitKey(0)==27
f=open(label_path, 'r')
split_lines = f.readlines()
new_txt_1=[]
new_txt_2=[]
new_txt_3=[]
"""
    判断属于分割后的图像中那一部分，且需要判断物体在那一部分多一些就属于那一部分
    先分割物体标签信息，使其不跨分割图像size，然后在分割图像，修改标签信息到每一张分割图像中
    思路：
	xmax值小于第一个分割线
		则该方框不用改动，即方框在第一幅图像
	xmax值大于第一个分割线且小于第二个分割线
		xmin值大于第一个分割线，xmax小于第二个分割线，该方框不用改动，即方框在第二幅图像
		xmin值小于第一个分割线，xmax大于第一个分割线，判断xmin与xman值离那边近一些，舍弃小的一边
		并且将修改成分割后图像的方框，即去掉分割408的宽度
	xmax值大于第二个分割线且小于边界
		xmin值大于第二个分割线，xmax小于图像边界，该方框不用改动，即方框在第三幅图像
		xmin值小于第二个分割线，xmax大于第二个分割线，判断xmin与xman值离那边近一些，舍弃小的一边
		并且将修改成分割后图像的方框，即去掉分割408的宽度
"""
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

label_out_path_1 = label_path.replace("only_one_size_label/000025.txt","split_label/000025_1.txt")
with open(label_out_path_1,'w+') as w_tdf: # w+是打开原文件将内容删除，另写新内容进去
    img_1_path = image_path.replace("only_one_size_image/000025.png","split_image/000025_1.png")
    cv2.imwrite(img_1_path,img1)
    for temp in new_txt_1:
        w_tdf.write(temp)

label_out_path_2 = label_path.replace("only_one_size_label/000025.txt","split_label/000025_2.txt")
with open(label_out_path_2,'w+') as w_tdf: # w+是打开原文件将内容删除，另写新内容进去
    img_2_path = image_path.replace("only_one_size_image/000025.png","split_image/000025_2.png")
    cv2.imwrite(img_2_path,img2)
    for temp in new_txt_2:
        w_tdf.write(temp)

label_out_path_3 = label_path.replace("only_one_size_label/000025.txt","split_label/000025_3.txt")
with open(label_out_path_3,'w+') as w_tdf: # w+是打开原文件将内容删除，另写新内容进去
    img_3_path = image_path.replace("only_one_size_image/000025.png","split_image/000025_3.png")
    cv2.imwrite(img_3_path,img3)
    for temp in new_txt_3:
        w_tdf.write(temp)

cv2.waitKey(0)==27

