'''
On Centos: yum install ImageMagick-devel
On Ubuntu: apt-get install libmagickwand-dev
pip install Wand
'''

import glob
from wand.image import Image
from wand.display import display


def YieldImageSizes(dir_path):
	for fn in glob.glob(dir_path):
		with Image(filename=fn) as img:
			yield img.size

if __name__ == "__main__":

	dir_path = './test_images/*.pgm'

	sizeList = [i for i in YieldImageSizes(dir_path)]
	print sizeList
