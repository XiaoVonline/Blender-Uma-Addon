import bpy
import os
from bpy.props import PointerProperty

from .config import __addon_name__
from .i18n.dictionary import dictionary
from ...common.class_loader import auto_load
from ...common.class_loader.auto_load import add_properties, remove_properties
from ...common.i18n.dictionary import common_dictionary
from ...common.i18n.i18n import load_dictionary

from .panels.Menus import View3dObject_menu, View3dEdit_menu, View3dPose_menu, Outliner_menu, MMR_XFFGL_menu, TanukiTexture_menu, TanukiSwitch_menu
from .operators.TanukiNodes import scene_frame_change_handler
from .operators.Physics import DampedTrackProperties
from .operators.Properties import UmaScene, UmaObject, UmaArmature
from .image.ImageManager import load_image, clear_image

bl_info = {
    "name": "UMA Addon",
    "blender": (4, 2, 0),
    "tracker_url": "https://www.bilibili.com/opus/1101994702993883141",
}

_addon_properties = {
    bpy.types.Scene: {
        "damped_track": PointerProperty(type=DampedTrackProperties),
        "uma_scene": PointerProperty(type=UmaScene),
    },
    bpy.types.Object: {
        "uma_object": PointerProperty(type=UmaObject),
    },
    bpy.types.Armature: {
        "uma_armature": PointerProperty(type=UmaArmature, override={'LIBRARY_OVERRIDABLE'}),
    },
}

def fill_data_on_start():
    prefs = bpy.context.preferences.addons[__addon_name__].preferences
    prop = prefs.ear_targets
    if len(prop) < 1:
        for i in ['0001_00_hair000', '0001_00_hair001', '0001_00_hair002', '0001_00_hair003', '0001_00_hair004', '0001_00_hair005', '0001_00_hair006', '0001_00_hair007', '0001_00_hair008', '0001_00_hair009', '0001_00_hair010', '0001_00_hair011', '0001_00_hair012', '0001_00_hair013', '0001_00_hair014', '0001_00_hair015', '0001_00_hair016', '0001_00_hair017', '0001_00_hair018', '0001_00_hair019', '0001_00_hair020', '0001_00_hair021', '0001_00_hair022', '0001_00_hair023', '0001_00_hair024', '0001_00_hair025', '0001_00_hair026', '0900_00_hair000', '0900_00_hair001', '0900_00_hair002', '0900_00_hair003', '0900_00_hair004', '0900_00_hair005', '1001_00', '1001_02', '1001_30', '1001_80', '1001_90', '1002_00', '1002_30', '1002_80', '1003_00', '1003_02', '1003_43', '1003_80', '1004_00', '1004_10', '1004_30', '1004_80', '1004_90', '1005_00', '1005_01', '1005_20', '1005_80', '1006_00', '1006_02', '1006_46', '1006_80', '1007_00', '1007_02', '1007_04', '1007_30', '1007_80', '1008_00', '1008_46', '1008_80', '1009_00', '1009_46', '1009_80', '1010_00', '1010_13', '1010_23', '1010_80', '1011_00', '1011_02', '1011_16', '1011_80', '1012_00', '1012_01', '1012_26', '1012_80', '1013_00', '1013_02', '1013_30', '1013_60', '1013_80', '1014_00', '1014_16', '1014_80', '1014_99', '1015_00', '1015_10', '1015_80', '1015_90', '1016_00', '1016_02', '1016_80', '1016_90', '1017_00', '1017_43', '1017_80', '1017_90', '1018_00', '1018_26', '1018_80', '1019_00', '1019_01', '1019_40', '1019_80', '1020_00', '1020_20', '1020_80', '1021_00', '1021_43', '1021_80', '1022_00', '1022_26', '1022_80', '1023_00', '1023_02', '1023_46', '1023_60', '1023_80', '1024_00', '1024_26', '1024_40', '1024_80', '1025_00', '1025_13', '1025_80', '1026_00', '1026_13', '1026_80', '1027_00', '1027_13', '1027_80', '1028_00', '1028_01', '1028_40', '1028_80', '1029_00', '1029_01', '1029_13', '1029_80', '1030_00', '1030_02', '1030_40', '1030_80', '1030_90', '1031_00', '1031_02', '1031_13', '1031_80', '1031_90', '1032_00', '1032_02', '1032_30', '1032_80', '1033_00', '1033_46', '1033_80', '1034_00', '1034_43', '1034_80', '1035_00', '1035_02', '1035_16', '1035_80', '1035_90', '1036_00', '1036_40', '1036_80', '1036_90', '1037_00', '1037_13', '1037_30', '1037_80', '1038_00', '1038_26', '1038_80', '1039_00', '1039_43', '1039_80', '1040_00', '1040_02', '1040_43', '1040_80', '1041_00', '1041_50', '1041_80', '1042_00', '1042_40', '1042_80', '1043_00', '1043_80', '1044_00', '1044_26', '1044_80', '1044_90', '1045_00', '1045_40', '1045_50', '1045_80', '1046_00', '1046_01', '1046_02', '1046_50', '1046_80', '1047_00', '1047_01', '1047_23', '1047_80', '1048_00', '1048_23', '1048_40', '1048_80', '1049_00', '1049_46', '1049_80', '1050_00', '1050_02', '1050_16', '1050_80', '1050_90', '1051_00', '1051_26', '1051_80', '1052_00', '1052_10', '1052_80', '1053_00', '1053_01', '1053_23', '1053_80', '1054_00', '1054_01', '1054_80', '1055_00', '1055_40', '1055_80', '1056_00', '1056_23', '1056_60', '1056_80', '1057_00', '1057_10', '1057_80', '1057_90', '1058_00', '1058_40', '1058_60', '1058_80', '1059_00', '1059_23', '1059_80', '1060_00', '1060_10', '1060_50', '1060_80', '1061_00', '1061_26', '1061_50', '1061_80', '1062_00', '1062_50', '1062_80', '1062_90', '1063_00', '1063_10', '1063_80', '1064_00', '1064_46', '1064_80', '1065_00', '1065_20', '1065_80', '1066_00', '1066_80', '1067_00', '1067_02', '1067_10', '1067_80', '1068_00', '1068_02', '1068_10', '1068_80', '1069_00', '1069_20', '1069_80', '1070_00', '1070_02', '1070_80', '1071_00', '1071_20', '1071_80', '1072_00', '1072_50', '1072_80', '1073_00', '1073_80', '1074_00', '1074_46', '1074_80', '1075_00', '1075_80', '1076_00', '1076_10', '1076_80', '1077_00', '1077_46', '1077_80', '1077_90', '1078_00', '1078_13', '1078_80', '1079_00', '1079_80', '1080_00', '1080_01', '1080_02', '1080_80', '1081_00', '1081_80', '1082_00', '1082_80', '1082_90', '1083_00', '1083_40', '1083_80', '1084_00', '1084_20', '1084_80', '1085_00', '1085_20', '1085_80', '1086_00', '1086_26', '1086_80', '1086_90', '1087_00', '1087_13', '1087_80', '1087_90', '1088_00', '1088_30', '1088_80', '1089_00', '1089_30', '1089_80', '1089_90', '1090_00', '1090_60', '1090_80', '1090_90', '1091_00', '1091_30', '1091_80', '1092_00', '1092_80', '1093_00', '1093_23', '1093_80', '1094_00', '1094_80', '1095_00', '1095_80', '1096_00', '1096_80', '1096_90', '1097_00', '1097_80', '1097_90', '1098_00', '1098_50', '1098_80', '1098_90', '1099_00', '1099_30', '1099_80', '1099_90', '1100_00', '1100_02', '1100_80', '1102_00', '1102_13', '1102_80', '1103_00', '1103_80', '1104_00', '1104_10', '1104_80', '1104_90', '1105_00', '1105_01', '1105_23', '1105_80', '1106_00', '1106_23', '1106_80', '1107_00', '1107_20', '1107_60', '1107_80', '1108_00', '1108_80', '1109_00', '1109_02', '1109_80', '1110_00', '1110_26', '1110_80', '1111_00', '1111_80', '1112_00', '1112_80', '1113_00', '1113_80', '1113_90', '1114_00', '1114_80', '1115_00', '1115_01', '1115_80', '1115_90', '1116_00', '1116_80', '1117_00', '1117_80', '1118_00', '1118_80', '1119_00', '1119_46', '1119_80', '1120_00', '1120_80', '1121_00', '1121_80', '1124_00', '1124_10', '1124_80', '1126_00', '1126_80', '1127_00', '1127_80', '1127_90', '1128_00', '1128_80', '1129_00', '1129_01', '1129_80', '1130_00', '1130_80', '1131_00', '1131_80', '1131_90', '1132_00', '1132_01', '1132_02', '1132_80', '1133_00', '1133_80', '1133_90', '1134_00', '1134_80', '1135_00', '1135_80', '1136_00', '1136_80', '1137_00', '1137_80', '1138_00', '1138_80', '1139_00', '1140_00', '1140_01', '1141_00', '1141_80', '1142_00', '1142_80', '1143_00', '1143_01', '1143_80', '1144_00', '1144_80', '1145_00', '1145_80', '2001_00', '2002_00', '2003_00', '2004_00', '2005_00', '2006_00', '2007_00', '2008_00', '2008_01', '9001_00', '9002_00', '9003_00', '9004_00', '9005_00', '9006_00', '9007_00', '9008_00', '9040_00', '9041_00', '9042_00', '9043_00', '9044_00', '9045_00', '9046_00', '9047_00', '9048_00', '9049_00', '9050_00', '9051_00', 'mchr0900_00']:
            item = prop.add()
            item.name = i

    prop = prefs.all_actions
    if len(prop) < 1:
        blend_file = os.path.join(os.path.dirname(__file__), "operators", "Umashaders.blend")
        if not os.path.exists(blend_file):
            print(f"ERROR: {blend_file} not found")
            return
        try:
            with bpy.data.libraries.load(blend_file) as (data_from, _):
                action_names = data_from.actions
        except Exception as e:
            print(str(e))
        for i in action_names:
            item = prop.add()
            item.name = i

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
    
    bpy.app.timers.register(fill_data_on_start, first_interval=0.1)
    load_image()
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
    clear_image()

    # Internationalization
    bpy.app.translations.unregister(__addon_name__)
    # unRegister classes
    auto_load.unregister()
    remove_properties(_addon_properties)

    print("{} is uninstalled.".format(__addon_name__))