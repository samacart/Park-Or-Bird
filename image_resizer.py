'''
On Centos: yum install ImageMagick-devel
On Ubuntu: apt-get install libmagickwand-dev
pip install Wand
'''

import glob
from wand.image import Image
from wand.display import display
import numpy as np

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


if __name__ == "__main__":

	dir_path = './test_images/*.pgm'

	sizeList = [i for i in YieldImageSizes(dir_path)]
	print sizeList

	x = np.array(sizeList)
	img_mean = x.mean(axis=0).round(0).astype(int)

	print img_mean

	ResizeImages(dir_path, img_mean)

	newSizes = [i for i in YieldImageSizes(dir_path)]
	print newSizes


