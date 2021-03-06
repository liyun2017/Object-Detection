#coding=utf-8
import os
import sys
import numpy as np
import cv2
import math
import signal
import random
import time
from multiprocessing import Process, Queue, Event

from landmark_augment import LandmarkAugment
from landmark_helper import LandmarkHelper

exitEvent = Event() # for noitfy all process exit.

#def handler(sig_num, stack_frame):
#    global exitEvent
#    exitEvent.set()
#signal.signal(signal.SIGINT, handler)

class BatchReader():
    def __init__(self, **kwargs):
        # param
        self._kwargs = kwargs
        self._batch_size = kwargs['batch_size']
        self._process_num = kwargs['process_num']
        # total lsit
        self._sample_list = [] # each item: (filepath, landmarks, ...)
        self._total_sample = 0
        # real time buffer
        self._process_list = []
        self._output_queue = []
        for i in range(self._process_num):
            self._output_queue.append(Queue(maxsize=3)) # for each process
        # epoch
        self._idx_in_epoch = 0
        self._curr_epoch = 0
        self._max_epoch = kwargs['max_epoch']
        # start buffering
        self._start_buffering(kwargs['input_paths'], kwargs['landmark_type'])

    def batch_generator(self):
        __curr_queue = 0
        while True:
            self.__update_epoch()
            while True:
                __curr_queue += 1
                if __curr_queue >= self._process_num:
                    __curr_queue = 0
                try:
                    image_list, landmarks_list = self._output_queue[__curr_queue].get(block=True, timeout=0.01)
                    break
                except Exception as ex:
                    pass
            yield image_list, landmarks_list

    def get_epoch(self):
        return self._curr_epoch

    def should_stop(self):
        if exitEvent.is_set() or self._curr_epoch > self._max_epoch:
            exitEvent.set()
            self.__clear_and_exit()
            return True
        else:
            return False

    def __clear_and_exit(self):
        print ("[Exiting] Clear all queue.")
        while True:
            time.sleep(1)
            _alive = False
            for i in range(self._process_num):
                try:
                    self._output_queue[i].get(block=True, timeout=0.01)
                    _alive = True
                except Exception as ex:
                    pass
            if _alive == False: break
        print ("[Exiting] Confirm all process is exited.")
        for i in range(self._process_num):
            if self._process_list[i].is_alive():
                print ("[Exiting] Force to terminate process %d"%(i))
                self._process_list[i].terminate()
        print ("[Exiting] Batch reader clear done!")

    def _start_buffering(self, input_paths, landmark_type):
        if type(input_paths) in [str, unicode]:
            input_paths = [input_paths]
        for input_path in input_paths:
            for line in open(input_path):
                info = LandmarkHelper.parse(line, landmark_type)
                self._sample_list.append(info)
        self._total_sample = len(self._sample_list) 
        #print self._total_sample #样本总数
        #print self._sample_list #样本列表 name array(5对坐标)
        #print "_process_num: %d"%self._process_num
        
        num_per_process = int(math.ceil(self._total_sample / float(self._process_num))) #ceil函数返回数字的上入整数
        
        #print "num_per_process: %d"%num_per_process
        
        for idx, offset in enumerate(range(0, self._total_sample, num_per_process)):
            '''
            print "idx:%d,offset %d"%(idx,offset)
            print len(self._sample_list[offset: offset+num_per_process])
            print self._sample_list[offset: offset+num_per_process]
            '''
            
            p = Process(target=self._process, args=(idx, self._sample_list[offset: offset+num_per_process]))
            p.start()
            self._process_list.append(p)

    def _process(self, idx, sample_list):
        __landmark_augment = LandmarkAugment()
        # read all image to memory to speed up!
        if self._kwargs['buffer2memory']:
            print ("[Process %d] Start to read image to memory! Count=%d"%(idx, len(sample_list)))
            sample_list = __landmark_augment.mini_crop_by_landmarks(sample_list, 4.5, self._kwargs['img_format'])
            print ("[Process %d] Read all image to memory finish!"%(idx))
        sample_cnt = 0 # count for one batch
        image_list, landmarks_list = [], [] # one batch list
        while True:
            for sample in sample_list:
                # preprocess
                if type(sample[0]) in [str, unicode]:
                    image = cv2.imread(sample[0])
                    if self._kwargs['img_format'] == 'RGB':
                        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                else:
                    image = cv2.imdecode(sample[0], cv2.IMREAD_COLOR)
                landmarks = sample[1].copy()# keep deep copy
                '''
                tmp_img = image.copy()
                for i in range(len(landmarks)):
                    tmp_img = cv2.circle(tmp_img, tuple(landmarks[i]), 3, (0,0,255), -1)
                cv2.imwrite(("output_tmp/"+str(idx)+"mini_crop_by_landmarks.jpg"),tmp_img)
                '''
                scale_range = (2.7, 3.3)
                image_new, landmarks_new = __landmark_augment.augment(image, landmarks, self._kwargs['img_size'],
                                            self._kwargs['max_angle'], scale_range)
                '''
                #print landmarks_new
                tmp_image_new = image_new.copy()
                cv2.imwrite(("output_tmp/"+str(idx)+"augment.jpg"),tmp_image_new)
                for i in range(len(landmarks_new)):
                    if i % 2 !=0:
                        continue
                    tmp_image_new = cv2.circle(tmp_image_new, (int(landmarks_new[i]*128),int(landmarks_new[i+1]*128)), 3, (0,0,255), -1)
                cv2.imwrite(("output_tmp/"+str(idx)+"image_new.jpg"),tmp_image_new)
                '''
                # caffe data format
                im_ = np.transpose(image_new, (2, 0, 1))
                im_ = im_.astype(np.float32)
                im_ = im_/127.5-1.0
                # sent a batch
                sample_cnt += 1
                image_list.append(im_)
                landmarks_list.append(landmarks_new)
                if sample_cnt >= self._kwargs['batch_size']:
                    self._output_queue[idx].put((np.array(image_list), np.array(landmarks_list)))
                    sample_cnt = 0
                    image_list, landmarks_list = [], []
                # if exit
                if exitEvent.is_set():
                    break
            if exitEvent.is_set():
                break
            np.random.shuffle(sample_list)

    def __update_epoch(self):
        self._idx_in_epoch += self._batch_size
        if self._idx_in_epoch > self._total_sample:
            self._curr_epoch += 1
            self._idx_in_epoch = 0

# use for unit test
if __name__ == '__main__':
    kwargs = {
        'input_paths': "/media/ly/data/FacialLandmark_Caffe-master/test_train/test_img_list.txt",
        'landmark_type': 5,
        'batch_size': 2,
        'process_num': 20,
        'img_format': 'RGB',
        'img_size': 128,
        'max_angle': 10,
        'buffer2memory': True,
        'max_epoch': 1,
    }
    output_folder = "output_tmp/"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    b = BatchReader(**kwargs)
    g = b.batch_generator()
    import time
    start_time = time.time()
    #cv2.destroyAllWindows()
    for i in range(1):
        end_time = time.time()
        print ("get new batch...step: %d. epoch: %d. cost: %.3f"%(
                i, b.get_epoch(), end_time-start_time))
        start_time = end_time
        batch_image, batch_landmarks = g.next()
        #for idx, (image, landmarks) in enumerate(zip(batch_image, batch_landmarks)):
        #    if idx > 20: # only see first 10
        #        break
        #    landmarks = landmarks.reshape([-1, 2])
        #    for l in landmarks:
        #        ii = tuple(l * (kwargs['img_size'], kwargs['img_size']))
        #        cv2.circle(image, (int(ii[0]), int(ii[1])), 2, (0,255,0), -1)
        #    cv2.imwrite("%s/%d.jpg"%(output_folder, idx), image)
    print ("Done...Press ctrl+c to exit me")

