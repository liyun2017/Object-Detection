cd /home/ly/caffe-weiliu/caffe
./build/tools/caffe train \
--solver="models/VGGNet/wider_face/SSD_352x288/solver.prototxt" \
--weights="models/VGGNet/VGG_ILSVRC_16_layers_fc_reduced.caffemodel" \
--gpu 0 2>&1 | tee jobs/VGGNet/wider_face/SSD_352x288/VGG_wider_face_SSD_352x288.log
