# ImageToOSD
This program is for drawing images in CTRPF.

# Usage
```
usage: ito.py [-h] [--start-x START_X] [--start-y START_Y] [--width WIDTH] [--height HEIGHT] [--bottom] [--silent] [--output OUTPUT] file

This program is for drawing images in CTRPF

positional arguments:
  file                  File name of the image to draw

options:
  -h, --help            show this help message and exit
  --start-x START_X, -x START_X
                        X position at which to start drawing (Default is adjusted to be drawn in the center)
  --start-y START_Y, -y START_Y
                        Y position at which to start drawing (Default is adjusted to be drawn in the center)
  --width WIDTH, -W WIDTH
                        Image Width (1-400 or 1-320 if bottom screen) (Default, images are automatically resized if they are too large)
  --height HEIGHT, -H HEIGHT
                        Image Height (1-240) (Default, images are automatically resized if they are too large)
  --bottom, -b          If this option is selected, drawing is done on the bottom screen. The default is to draw on the top screen.
  --silent, -s          Runs the program without displaying anything
  --output OUTPUT, -O OUTPUT
                        Directory to output the generated code. (Default is './ito_output')
```
