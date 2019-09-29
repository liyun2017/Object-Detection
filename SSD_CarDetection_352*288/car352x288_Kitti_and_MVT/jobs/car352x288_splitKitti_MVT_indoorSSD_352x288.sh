cd /home/ly/caffe-weiliu/caffe
./build/tools/caffe train \
--solver="models/VGGNet/car352x288_splitKitti_MVT_indoor/SSD_352x288/solver.prototxt" \
--snapshot="models/VGGNet/car352x288_splitKitti_MVT_indoor/SSD_352x288/car352x288_splitKitti_MVT_indoorSSD_352x288_iter_60703.solverstate" \
--gpu 0 2>&1 | tee jobs/VGGNet/car352x288_splitKitti_MVT_indoor/SSD_352x288/car352x288_splitKitti_MVT_indoorSSD_352x288.log
