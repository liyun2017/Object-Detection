# Object-Detection
该项目是完成车辆的检测，主要是使用在海思开发板上
目录：
	car352x288_MVT	在数据集Insight-MVT上进行训练
	
	car352x288_KITTI在数据集KITTI上进行训练

TODO：
	MVT数据集是视频数据集，其单帧图片具有非常大的运动模糊，且场景单一，数据不care，导致训练结果出现了误检率
	
	KITTI原图基本以1224×370为主，数据集的size，经过resize，车辆的信息已经包含很少，需要做大量数据处理操作
