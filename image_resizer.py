'''
On Centos: yum install ImageMagick-devel
On Ubuntu: apt-get install libmagickwand-dev
pip install Wand
'''

import glob
from wand.image import Image
from wand.display import display
import numpy as np
import os

def YieldImageSizes(dir_path):
	for fn in glob.glob(dir_path):
		with Image(filename=fn) as img:
			yield img.size

def ResizeImages(dir_path, size):
	for fn in glob.glob(dir_path):
		with Image(filename=fn) as img:
			#using sample since it is faster than resize
			#similar function but does not provide filter and blur options
			img.sample(size[0], size[1])
			img.save(filename="./resize/r_" + os.path.basename(fn))

def LiquidResizeImages(dir_path, size):
	# DOES NOT WORK WITH DEFAULT IMAGEMAGICK ON CENTOS
	for fn in glob.glob(dir_path):
		with Image(filename=fn) as img:
			img.liquid_rescale(size[0], size[1])
			img.save(filename="./liquid/l_" + os.path.basename(fn))

def TransformImage(dir_path, size):
	for fn in glob.glob(dir_path):
		with Image(filename=fn) as img:
			resize_str = str(size[0]) + 'x' + str(size[1]) + '>'

			#if larger than the resize_str, fit within box, preserving aspect ratio
			img.transform(resize=resize_str)
			img.save(filename="./transform/t_" + os.path.basename(fn))
		

if __name__ == "__main__":

	dir_path = './test_images/*.pgm'

	sizeList = [i for i in YieldImageSizes(dir_path)]
	print sizeList

	x = np.array(sizeList)
	img_mean = x.mean(axis=0).round(0).astype(int)

	ResizeImages(dir_path, img_mean)
	#LiquidResizeImages(dir_path, img_mean)
	TransformImage(dir_path, img_mean)
