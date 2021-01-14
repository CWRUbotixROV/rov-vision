from os import path

parent_dir = path.split(path.dirname(__file__))[0]
images_path = path.join(parent_dir, "images")

class Config:
    def __init__(self, debug):
        self.debug = debug

config = Config(False)
