import bpy

from ..config import __addon_name__
from ..operators.AddonOperators import SetBoneCollections, SimplifyArmature, RefineBoneStructure, FixBlush, FixNormal, ChangeHeadPretreat, ChangeHeadHoldout, ChangeHeadCopyShapeOperator, ChangeHeadNewShapeOperator
from ..operators.AddonOperators2 import BuildTwistConstraints, ClearTwistConstraints
from ..operators.GenerateController import GenerateIK, BakeFKtoIK
from ..operators.Umashader import ApplyShader
# from ..operators.Physics import DampedTrackProperties

from ....common.i18n.i18n import i18n
from ....common.types.framework import reg_order
from ..utils.Config_handling import get_panel_name

class BasePanel(object):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = get_panel_name()

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True

@reg_order(0)
class AddonPanel(BasePanel, bpy.types.Panel):
    bl_label = "UMA Addon"
    bl_idname = "SCENE_PT_umaaddonpanel"

    def draw(self, context: bpy.types.Context):
        layout = self.layout

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True

@reg_order(1)
class ModelProcessPanel(BasePanel, bpy.types.Panel):
    bl_label = "Processing Model"
    bl_idname = "SCENE_PT_umaaddonpanel1"
    bl_parent_id = "SCENE_PT_umaaddonpanel"

    def draw(self, context: bpy.types.Context):
        layout = self.layout

        split = layout.split(factor=0.5)
        split.operator(SetBoneCollections.bl_idname)
        split.operator(RefineBoneStructure.bl_idname)
        row = layout.row(align=True)
        row.prop(context.scene, "del_handle", toggle=True)
        row.prop(context.scene, "del_face", toggle=True)
        row.prop(context.scene, "del_others", toggle=True)
        row.operator(SimplifyArmature.bl_idname)

        layout.operator(ApplyShader.bl_idname)
        
        layout.label(text="Fix mini umamusume model:")
        split = layout.split(factor=0.5)
        split.operator(FixBlush.bl_idname)
        split.operator(FixNormal.bl_idname)

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True

@reg_order(2)
class ControllerPanel(BasePanel, bpy.types.Panel):
    bl_label = "Controller"
    bl_idname = "SCENE_PT_umaaddonpanel2"
    bl_parent_id = "SCENE_PT_umaaddonpanel"

    def draw(self, context: bpy.types.Context):
        layout = self.layout

        if getattr(getattr(context.active_object, "uma_controller", None), "auto_twist_bones", False):
            layout.operator(ClearTwistConstraints.bl_idname, text="Auto Twist", depress=True)
        else:
            layout.operator(BuildTwistConstraints.bl_idname, text="Auto Twist",  depress=False)

        layout.operator(GenerateIK.bl_idname, icon='BONE_DATA')
        layout.operator(BakeFKtoIK.bl_idname, icon='SNAP_ON')

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True

@reg_order(3)
class ChangeHeadPanel(BasePanel, bpy.types.Panel):
    bl_label = "Change Head"
    bl_idname = "SCENE_PT_umaaddonpanel3"
    bl_parent_id = "SCENE_PT_umaaddonpanel"

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        
        row = layout.row()
        row.operator(ChangeHeadPretreat.bl_idname)
        row.operator(ChangeHeadHoldout.bl_idname)
        layout.label(text="Create a new absolute shape key:")
        row = layout.row()
        row.operator(ChangeHeadNewShapeOperator.bl_idname)        
        row.operator(ChangeHeadCopyShapeOperator.bl_idname)

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True

@reg_order(4)
class PhysicsPanel(BasePanel, bpy.types.Panel):
    bl_label = "Physics"
    bl_idname = "SCENE_PT_umaaddonpanel4"
    bl_parent_id = "SCENE_PT_umaaddonpanel"

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        
        props = context.scene.damped_track
        row = layout.row(align=True)
        row.prop(props, "ear_enable", toggle=True, text="Ear")
        row.prop(props, "bust_enable", toggle=True, text="Bust")
        row.prop(props, "tail_enable", toggle=True, text="Tail")

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object and context.active_object.type == 'ARMATURE'
    