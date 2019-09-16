import cv2,os

img_folder = '/media/ly/data/FacialLandmark_Caffe-master/test_train/'
img_list = "/media/ly/data/FacialLandmark_Caffe-master/test_train/test_img_list.txt"
for line in open(img_list):
    a = line.split()
    pts = []
    for i in range(len(a)-1):
        pts.append(int(a[i+1]))
    im_path = os.path.join(img_folder, a[0])
    im = cv2.imread(im_path)
    if im is None:
        print("Invaild image: ", im_path)
        continue
    print pts
    for index in range(len(pts)-1):
        if index % 2 !=0:
            continue
        print (pts[index],pts[index+1])
        cv2.circle(im, (pts[index],pts[index+1]), 2, (0,255,0), -1)
        cv2.imshow("img",im)
        cv2.waitKey()

#对应txt标签为
#0 name
#1-2 左眼
#3-4 右眼
#5-6 鼻尖
#7-8 左嘴角
#9-10 右嘴角
