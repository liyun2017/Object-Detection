cd /home/ly/caffe-weiliu/caffe
./build/tools/caffe train \
--solver="models/VGGNet/wider_face/SSD_300x300/solver.prototxt" \
--gpu 0 2>&1 | tee jobs/VGGNet/wider_face/SSD_300x300/VGG_wider_face_SSD_300x300.log
