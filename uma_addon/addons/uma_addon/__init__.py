import bpy
from bpy.props import BoolProperty, PointerProperty

from .config import __addon_name__
from .i18n.dictionary import dictionary
from ...common.class_loader import auto_load
from ...common.class_loader.auto_load import add_properties, remove_properties
from ...common.i18n.dictionary import common_dictionary
from ...common.i18n.i18n import load_dictionary

from .panels.Menus import View3dObject_menu, View3dEdit_menu, View3dPose_menu, Outliner_menu, MMR_XFFGL_menu, TanukiTexture_menu, TanukiSwitch_menu
from .operators.TanukiNodes import scene_frame_change_handler
from .operators.Physics import DampedTrackProperties
from .operators.GenerateController import ControllerProperties

bl_info = {
    "name": "UMA Addon",
    "blender": (4, 2, 0),
    "tracker_url": "https://www.bilibili.com/opus/1101994702993883141",
}

_addon_properties = {
    bpy.types.Scene: {
        "del_handle": BoolProperty(name="handle", default=True),
        "del_face": BoolProperty(name="face", default=True),
        "del_others": BoolProperty(name="others", default=True),
        "damped_track": PointerProperty(type=DampedTrackProperties),
    },
    bpy.types.Object: {
        "uma_controller": PointerProperty(type=ControllerProperties),
    },
}

def register():
    # Register classes
    auto_load.init()
    auto_load.register()
    add_properties(_addon_properties)

    # Internationalization
    load_dictionary(dictionary)
    bpy.app.translations.register(__addon_name__, common_dictionary)

    bpy.types.VIEW3D_MT_object_context_menu.append(View3dObject_menu)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(View3dEdit_menu)
    bpy.types.VIEW3D_MT_pose_context_menu.append(View3dPose_menu)
    bpy.types.OUTLINER_MT_object.append(Outliner_menu)

    mmr_panel = getattr(bpy.types, "SCENE_PT_MMR_Rig_0", None)
    if mmr_panel:
        mmr_panel.append(MMR_XFFGL_menu)
    else:
        print("未找到 MMR 插件")

    if hasattr(bpy.types, "NODE_MT_category_shader_texture"):
        bpy.types.NODE_MT_category_shader_texture.append(TanukiTexture_menu)
    if hasattr(bpy.types, "NODE_MT_category_shader_converter"):
        bpy.types.NODE_MT_category_shader_converter.append(TanukiSwitch_menu)
    # 注册帧变化处理
    if scene_frame_change_handler not in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.append(scene_frame_change_handler)
    
    print("{} is installed.".format(__addon_name__))

def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(View3dObject_menu)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(View3dEdit_menu)
    bpy.types.VIEW3D_MT_pose_context_menu.remove(View3dPose_menu)
    bpy.types.OUTLINER_MT_object.remove(Outliner_menu)

    mmr_panel = getattr(bpy.types, "SCENE_PT_MMR_Rig_0", None)
    if mmr_panel:
        mmr_panel.remove(MMR_XFFGL_menu)

    if hasattr(bpy.types, "NODE_MT_category_shader_texture"):
        bpy.types.NODE_MT_category_shader_texture.remove(TanukiTexture_menu)
    if hasattr(bpy.types, "NODE_MT_category_shader_converter"):
        bpy.types.NODE_MT_category_shader_converter.remove(TanukiSwitch_menu)
    # 注销帧变化处理
    if scene_frame_change_handler in bpy.app.handlers.frame_change_pre:
        bpy.app.handlers.frame_change_pre.remove(scene_frame_change_handler)

    # Internationalization
    bpy.app.translations.unregister(__addon_name__)
    # unRegister classes
    auto_load.unregister()
    remove_properties(_addon_properties)

    print("{} is uninstalled.".format(__addon_name__))