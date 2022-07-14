#!/usr/bin/env python


import argparse
import os
import shutil
import sys

from PIL import Image




g_silent = False



def print(*args, print_=print, **kwargs):
	if g_silent:
		return
	else:
		print_(*args, **kwargs)


def get_image_size(file_name):
	print(f"Trying to get the size of the image ({file_name})")
	if os.path.exists(file_name):
		try:
			img = Image.open(file_name)
			img.close()
			return img.size
		except:
			print("Failed to open image")
			sys.exit(1)


def resize_image(file_name, width, height):
	print(f"Trying to resize an image ({width}, {height})")
	if os.path.exists(file_name):
		try:
			img = Image.open(file_name)
			img_resize = img.resize((width, height))
			img_resize.save(file_name)
			img.close()
		except:
			print("Failed to open image")
			sys.exit(1)


def get_pixels_from_image(file_name):
	print(f"Trying to read pixels data from an image ({file_name})")
	if os.path.exists(file_name):
		try:
			img = Image.open(file_name)
			pixels = img.convert("RGB")
			pixels_data = list(pixels.getdata())

			r = []
			g = []
			b = []

			for p in pixels_data:
				r.append(p[0])
				g.append(p[1])
				b.append(p[2])

			img.close()
			return (r, g, b)
		except:
			print("Failed to open image")
			sys.exit(1)
	else:
		print("No such file exists")
		sys.exit(1)


def calc_position(width, height, is_bottom):
	print("Trying to calculate optimal X, Y position")
	optimal_x = ((320 if is_bottom else 400) - width) // 2
	optimal_y = (240 - height) // 2
	return (optimal_x, optimal_y)


def generate_code(x, y, width, height, is_bottom, pixels_data):
	print("Trying to generate source code")
	cpp_template = '''
#include "draw_image.hpp"

namespace CTRPluginFramework
{
	void draw_image(void) {
		bool draw_bottom_screen = ''' + str(is_bottom).lower() + ''';
		const Screen &scr = draw_bottom_screen ? OSD::GetBottomScreen() : OSD::GetTopScreen();

		int x = ''' + str(x) + ''';
		int y = ''' + str(y) + ''';
		int width = ''' + str(width) + ''';
		int height = ''' + str(height) + ''';

		u8 r[] = {''' + str(pixels_data[0])[1:-1].replace(" ", "") + '''};
		u8 g[] = {''' + str(pixels_data[1])[1:-1].replace(" ", "") + '''};
		u8 b[] = {''' + str(pixels_data[2])[1:-1].replace(" ", "") + '''};

		int nap = 0;

		for (int yy = 0; yy < height; yy++) {
			for (int xx = 0; xx < width; xx++) {
				scr.DrawPixel(xx + x, yy + y, Color(r[nap], g[nap], b[nap], 255));
				nap++;
			}
		}
	}
}
'''
	return cpp_template


def output(raw_cpp, output_dir):
	print("Trying to output source code")
	hpp_template = '''
#ifndef DRAW_H
#define DRAW_H

#include <CTRPluginFramework.hpp>

namespace CTRPluginFramework
{
    void draw_image(void);
}

#endif
'''

	cheats_cpp_template = '''
#include "draw_image.hpp"
// ...
'''

	if os.path.exists(output_dir):
		print("Trying to remove directory")
		shutil.rmtree(output_dir)

	os.mkdir(output_dir)
	os.chdir(output_dir)
	os.mkdir("Includes")
	os.mkdir("Sources")
	root = os.getcwd()
	os.chdir("Includes")
	with open("draw_image.hpp", "w+") as fw1:
		fw1.write(hpp_template)
	os.chdir("./../Sources")
	with open("draw_image.cpp", "w+") as fw2, open("cheats.cpp", "w+") as fw3:
		fw2.write(raw_cpp)
		fw3.write(cheats_cpp_template)


# TODO: refactor this function
def convert(file_name, output_dir, x, y, width, height, is_bottom):
	size = get_image_size(file_name)
	img_width = size[0]
	img_height = size[1]
	width = width if width else img_width
	height = height if height else img_height

	is_larger_img = (400 < img_width and (not is_bottom)) or (320 < img_width and is_bottom) or (240 < img_height)
	is_larger_inp = (400 < width and (not is_bottom)) or (320 < width and is_bottom) or (240 < height)
	
	# Optional resize
	if (not is_larger_inp) and any((width, height)):
		resize_image(file_name, width if width else img_width, height if height else img_height)
		img_width = width if width else img_width
		img_height = height if height else img_height
		width = width if width else img_width
		height = height if height else img_height
	
	# Auto resize
	if is_larger_img or is_larger_inp:
		resize_image(file_name, 320 if is_bottom else 400, 240)
		img_width = 320 if is_bottom else 400
		img_height = 240
		width = 320 if is_bottom else 400
		height = 240

	# Calc X, Y
	optimal_position = calc_position(img_width, img_height, is_bottom)
	x = x if x else optimal_position[0]
	y = y if y else optimal_position[1]
	
	# set width / height
	width = img_width if not width else width
	height = img_height if not height else height

	# get pixel data
	pixels_data = get_pixels_from_image(file_name)
	
	# convert raw data to C++ code
	generated_code = generate_code(x, y, width, height, is_bottom, pixels_data)

	# output generated files
	output(generated_code, output_dir)


def main():
	global g_silent
	parser = argparse.ArgumentParser(description="This program is for drawing images in CTRPF")
	parser.add_argument("file", help="File name of the image to draw")
	parser.add_argument("--start-x", "-x", help="X position at which to start drawing (Default is adjusted to be drawn in the center)", type=int)
	parser.add_argument("--start-y", "-y", help="Y position at which to start drawing (Default is adjusted to be drawn in the center)", type=int)
	parser.add_argument("--width", "-W", help="Image Width (1-400 or 1-320 if bottom screen) (Default, images are automatically resized if they are too large)", type=int)
	parser.add_argument("--height", "-H", help="Image Height (1-240) (Default, images are automatically resized if they are too large)", type=int)
	parser.add_argument("--bottom", "-b", help="If this option is selected, drawing is done on the bottom screen. The default is to draw on the top screen.", action="store_true")
	parser.add_argument("--silent", "-s", help="Runs the program without displaying anything", action="store_true")
	parser.add_argument("--output", "-O", help="Directory to output the generated code. (Default is './ito_output')", default="ito_output")

	args = parser.parse_args()
	g_silent = args.silent

	print("Processing has been started...")

	convert(args.file, args.output, args.start_x, args.start_y, args.width, args.height, args.bottom)

	print("The process was a success!")





if __name__ == "__main__":
	main()
