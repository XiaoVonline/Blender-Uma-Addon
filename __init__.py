from .uma_addon.addons.uma_addon import register as addon_register, unregister as addon_unregister

bl_info = {
    "name": 'UMA Addon',
    "blender": (4, 2, 0),
    "tracker_url": 'https://www.bilibili.com/opus/1101994702993883141'
}

def register():
    addon_register()

def unregister():
    addon_unregister()

    