### What's this
人脸关键点检测https://github.com/BobLiu20/FacialLandmark_Caffe.git
数据集cleba
目录：
	common	增加的python层（caffe训练的输入层）
		编译caffe时需要编译pycaffe
		进入Ubuntu下的python根目录/python2.7/dist-packages，加入face_common.pth文件
		face_common.pth:
			加入一句话 /media/ly/data/FacialLandmark_Caffe-master/common   即需要引用的文件路径
	
	testing	存放着测试代码
	test_train 存放着python层的校验代码，为防止进入caffe中的数据出现错误，特此将common中的pyhton层进行校验
	training	训练代码

