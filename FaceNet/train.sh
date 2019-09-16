#!/usr/bin/env sh

TOOLS=/home/ly/caffe-weiliu/caffe/build/tools

${TOOLS}/caffe train --solver /media/ly/data/caffe-face/face_example/face_solver.prototxt -weights /media/ly/data/caffe-face/face_example/face_model.caffemodel --gpu 0 2>&1| tee /media/ly/data/caffe-face/face_example/face_snapshot/caffe_softmax.log 
