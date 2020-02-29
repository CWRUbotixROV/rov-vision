# Editing Masks
`masktest.py` is used to set mask values which are stored in `colors.txt`. Put the image you want to calibrate to in the `images` folder. Then run `python3 masktest.py filename.png`. Press `esc` to exit the program.
### Adjusting Mask Values
The sliders adjust the range of colors in the mask using HLS color space. To load a color from the calibration image, double click a specific point of the calibration image. This will set the mask values to the color selected.
### Saving a Mask
To save a mask, type `s`, then type the name of the color in the command line and hit enter.
### Loading a Mask
To load a mask, type `l` , then type the name of the color in the command line and hit enter.

# Using Masks
Use `from mask import colors` in your python file to use masks. To get a mask for an image use `colors.get_mask('color', image)` where `'color'` is a string of the color you are masking for and `image` is the cv2 image in RGB color space.
If your python file is located at `vision/folder/file.py` you must run it from the `vision` folder using `python3 -m folder.file`.
