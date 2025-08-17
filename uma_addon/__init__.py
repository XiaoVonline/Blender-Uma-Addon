import bpy

from .config import __addon_name__
from .i18n.dictionary import dictionary
from ...common.class_loader import auto_load
from ...common.class_loader.auto_load import add_properties, remove_properties
from ...common.i18n.dictionary import common_dictionary
from ...common.i18n.i18n import load_dictionary

# Add-on info
bl_info = {
    "name": "UMA Addon",
    "author": "小微在线上",
    "blender": (4, 5, 1),
    "version": (0, 0, 1),
    "description": "",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "support": "COMMUNITY",
    "category": "Object"
}

_addon_properties = {}


# You may declare properties like following, framework will automatically add and remove them.
# Do not define your own property group class in the __init__.py file. Define it in a separate file and import it here.
# 注意不要在__init__.py文件中自定义PropertyGroup类。请在单独的文件中定义它们并在此处导入。
# _addon_properties = {
#     bpy.types.Scene: {
#         "property_name": bpy.props.StringProperty(name="property_name"),
#     },
# }

def register():
    # Register classes
    auto_load.init()
    auto_load.register()
    add_properties(_addon_properties)

    # Internationalization
    load_dictionary(dictionary)
    bpy.app.translations.register(__addon_name__, common_dictionary)

    # 注册场景属性
    bpy.types.Scene.delete_handle_collection = bpy.props.BoolProperty(name="delete_handle_collection", default=False)
    bpy.types.Scene.delete_face_collection = bpy.props.BoolProperty(name="delete_face_collection", default=False)
    bpy.types.Scene.delete_others_collection = bpy.props.BoolProperty(name="delete_others_collection", default=False)

    print("{} addon is installed.".format(__addon_name__))


def unregister():
    # Internationalization
    bpy.app.translations.unregister(__addon_name__)
    # unRegister classes
    auto_load.unregister()
    remove_properties(_addon_properties)

    # 注销场景属性    
    del bpy.types.Scene.delete_handle_collection
    del bpy.types.Scene.delete_face_collection
    del bpy.types.Scene.delete_others_collection

    print("{} addon is uninstalled.".format(__addon_name__))
