from .addons.uma_addon import register as addon_register, unregister as addon_unregister

bl_info = {
    "name": 'UMA Addon',
    "author": '小微在线上',
    "blender": (4, 5, 1),
    "version": (0, 0, 1),
    "description": '',
    "warning": '',
    "doc_url": '',
    "tracker_url": '',
    "support": 'COMMUNITY',
    "category": 'Object'
}

def register():
    addon_register()

def unregister():
    addon_unregister()

    