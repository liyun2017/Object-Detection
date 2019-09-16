#!/usr/bin/env sh

TOOLS=/home/ly/caffe-weiliu/caffe/build/tools
PROTO_SOLVER=/media/ly/data/FacialLandmark_Caffe-master/training/net1
${TOOLS}/caffe train --solver  ${PROTO_SOLVER}/solver.prototxt --gpu 0 2>&1| tee ${PROTO_SOLVER}/train.log 
