# Object-Detection
该项目是基于https://github.com/weiliu89/caffe.git来完成的
与SSD_FaceDetection_300*300类似的操作，但是需求的输入需要的大小是352*288的，故将网络重新训练
数据集仍采用的是wider_face
转成VOC0712的格式，在转成imdb格式进入网络训练的
目录结构如下：
	jobs	存放着prototxt 和 训练文件
	VGGNet	存放着测试文件 模型太大没有上传
	widerface352 存放着转化imdb格式的过程
	wider_face存放着wider_face数据集
	
