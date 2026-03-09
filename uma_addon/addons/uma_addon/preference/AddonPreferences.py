import bpy
import os
import tempfile
import shutil
from bpy.props import StringProperty, IntProperty, BoolProperty, CollectionProperty
from bpy.types import AddonPreferences
from ..config import __addon_name__
from ..operators.Properties import EarTargets, AllActions
from ..operators.Dependencies import is_pillow_available
from ..utils.Config_handling import get_config_parameter, set_config_parameter, get_panel_name
from ..panels.AddonPanels import ModelProcessPanel, ControllerPanel, ChangeHeadPanel, PhysicsandActionsPanel

UI_PANELS = [ModelProcessPanel, ControllerPanel, ChangeHeadPanel, PhysicsandActionsPanel]

class AddonPreferences(AddonPreferences):
    # this must match the add-on name (the folder name of the unzipped file)
    bl_idname = __addon_name__

    # https://docs.blender.org/api/current/bpy.props.html
    # The name can't be dynamically translated during blender programming running as they are defined
    # when the class is registered, i.e. we need to restart blender for the property name to be correctly translated.

    def update_panel_name(self, context):
        try:
            for c in UI_PANELS:
                bpy.utils.unregister_class(c)
                c.bl_category = self.panel_name
        except:
            pass

        set_config_parameter("Addon Settings", "panel_name", self.panel_name)

        for c in UI_PANELS:
            bpy.utils.register_class(c)

    panel_name: StringProperty(name="", default=get_panel_name(), update=update_panel_name)
    debug: BoolProperty(default=False)
    ear_targets: CollectionProperty(type=EarTargets)
    all_actions: CollectionProperty(type=AllActions)

    def draw(self, context: bpy.types.Context):
        """绘制偏好设置界面"""
        layout = self.layout

        layout.prop(self, "panel_name")

        box = layout.box()
        row = box.row()
        if is_pillow_available():
            try:
                import PIL
                row.label(text=f"Pillow {PIL.__version__}")
            except:
                row.label(text="Pillow is installed")
            row.operator("uma.uninstall_pillow", icon='REMOVE')
        else:
            row.label(text="Pillow is not installed")
            row.operator("uma.install_pillow", icon='IMPORT')

        box.label(text="The duration of the blockage caused by the installation depends on the network quality. Uninstallation takes effect after a restart.")
        row = layout.row()
        row.operator(RefreshData.bl_idname, icon="FILE_REFRESH")
        row.operator(ClearData.bl_idname, icon="TRASH")

class RefreshData(bpy.types.Operator):
    """Refresh addon data"""
    bl_idname = "uma.refresh_data"
    bl_label = "Refresh Data"
    bl_options = {'REGISTER'}

    def execute(self, context):

        prefs = context.preferences.addons[__addon_name__].preferences
        prefs.debug = False   

        # 刷新时保存收藏和昵称
        # 记录当前已经收藏的名字
        # favorites = {item.name for item in prop if item.is_favorite}
        # prop.clear()
        # for n in action_names:
        #     item = prop.add()
        #     item.name = n
        #     if n in favorites:
        #         item.is_favorite = True

        self.report({'INFO'}, "Refresh addon data successfully")
        return {'FINISHED'}

class ClearData(bpy.types.Operator):
    """Clear addon data"""
    bl_idname = "uma.clear_data"
    bl_label = "Clear Data"
    bl_options = {'REGISTER'}

    def execute(self, context):

        prefs = context.preferences.addons[__addon_name__].preferences
        prefs.panel_name = "UMA"
        prefs.debug = False   
        if prefs.ear_targets:
            prefs.ear_targets.clear()
        if prefs.all_actions:
            prefs.all_actions.clear()     
        try:
            bpy.ops.wm.save_userpref()
        except Exception as e:
            self.report({'WARNING'}, str(e))
        scene_props = context.scene.uma_scene
        scene_props.filtered_actions.clear()
        scene_props.action_index = 0

        cache = os.path.join(tempfile.gettempdir(), "tanuki_cache")
        shutil.rmtree(cache, ignore_errors=True)

        self.report({'INFO'}, "Clear addon data successfully")
        return {'FINISHED'}
