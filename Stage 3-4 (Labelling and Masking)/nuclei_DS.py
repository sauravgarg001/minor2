import os
import numpy as np 
import cv2
from time import time
from datetime import timedelta
from util import *
from run_restored_model import*

def process(data_folder, format):
	model_folder = 'models'
	model_name = 'nucles_model_v3.meta'
	dir_path = os.path.join(os.getcwd(), data_folder)
	model_path = os.path.join(os.getcwd(), model_folder)

	patch_size = 128
	stride = 16


	model = restored_model(os.path.join(model_path, model_name), model_path)

	file_dir_path_list = os.listdir(dir_path)
	print(str(len(file_dir_path_list)), ' files detected')


	start_time = start_timer() # Timer Start

	for index, file_name in enumerate(file_dir_path_list):

		print(str(index+1), ' File: ', file_name, 'processing...')
		file_dir_path = os.path.join(dir_path, file_name)
		
		
		file_path=cv2.imread(os.path.join(file_dir_path, file_name+format))

		if file_path is None:
			print(file_name+format, ' not found')
			continue

		batch_group, shape=preprocess(file_path, patch_size, stride, file_dir_path)
		mask_list=sess_interference(model, batch_group)
		c_mask=patch2image(mask_list, patch_size, stride, shape)
		c_mask=cv2.medianBlur((255*c_mask).astype(np.uint8), 3)
		c_mask=c_mask.astype(np.float)/255
		thr=0.5
		c_mask[c_mask<thr]=0
		c_mask[c_mask>=thr]=1
		center_edge_mask, gray_map=center_edge(c_mask, file_path)

		cv2.imwrite(os.path.join(file_dir_path, 'mask.png'), gray_map) # writing mask.png
		cv2.imwrite(os.path.join(file_dir_path, 'label.png'), center_edge_mask) # writing label.png

	model.close_sess()

	end_timer(start_time) # Timer Ends
	print("Finished...")


# Timer
def start_timer():
	return time()


def end_timer(start_time):
	end_time = time()
	print("Time usage: " + str(timedelta(seconds=int(round(end_time - start_time)))))


if __name__ == '__main__':
	data_folder = 'data'
	format = '.png'
	process(data_folder, format)
