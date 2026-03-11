import bpy
import os
import bpy.utils.previews

_all_images = {
    "ctrl": "1",
    "umapping": "2"
}

_loaded_images = {}

def load_image():
    for key in _all_images:
        path = os.path.join(os.path.dirname(__file__), _all_images[key])
        pcoll = bpy.utils.previews.new()
        pcoll.load(key, path, "IMAGE")
        _loaded_images[key] = pcoll

def clear_image():
    for key in _loaded_images:
        bpy.utils.previews.remove(_loaded_images[key])

def get_image_id(image_name):
    if image_name in _loaded_images:
        return _loaded_images[image_name][image_name].icon_id