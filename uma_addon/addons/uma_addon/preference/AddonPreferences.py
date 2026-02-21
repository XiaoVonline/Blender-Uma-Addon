import bpy
from bpy.props import StringProperty, IntProperty, BoolProperty
from bpy.types import AddonPreferences

from ..config import __addon_name__

from ..operators.Dependencies import is_pillow_available

from ..utils.Config_handling import get_config_parameter, set_config_parameter, get_panel_name

from ..panels.AddonPanels import AddonPanel, ModelProcessPanel, ControllerPanel, ChangeHeadPanel

UI_PANELS = [AddonPanel, ModelProcessPanel, ControllerPanel, ChangeHeadPanel]

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
        except:
            pass

        AddonPanel.bl_category = self.panel_name

        set_config_parameter("Addon Settings", "panel_name", self.panel_name)

        for c in UI_PANELS:
            bpy.utils.register_class(c)

    panel_name: StringProperty(name="", default=get_panel_name(), update=update_panel_name)
    debug: BoolProperty(name="debug mode", default=False)

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

        layout.prop(self, "debug")