# Vision
## Turning on debug mode
Add the following to any test scripts you want to run in debug mode.
```Python
from vision import config

config.debug = True
```

## images.py
### get_image
Used for getting an image from the `images` folder of this repository. Each argument specifies the path to the image you want to use. For example, if you wanted the image located at `images/objects/1/star/1.jpg`, then you would use
```Python
from vision.images import get_image
...
...
image = get_image("objects", "1", "star", "1.jpg")
```

### show_debug
Used for only showing an image when running in debug mode. In general, you should use this method instead of `cv2.imshow` so that it is easier for us to use the code in competition. This method has two optional parameters.

The `name` parameter specifies the name of the window. It will default to `"Image"`. OpenCV will only display one window per name, so if the same name gets used, the old window with the same name will close.

The `wait` parameter specifies whether or not code should stop executing until the user enters a key. This defaults to `True`.

If you want to call this with the default parameters, use `show_debug(image)`. If you want to specify the parameters, use `show_debug(image, name="Window name", wait=False)`. You can also only set one of the optional parameters.