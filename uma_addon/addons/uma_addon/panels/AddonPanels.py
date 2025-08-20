import bpy

from ..config import __addon_name__
from ..operators.AddonOperators import BoneLayerOperator, BoneLayerResetOperator, BoneSimplifyOperator, GenerateControllerOperator, FixEyeBoneOperator, CombineShapeKeysOperator, FixBlushOperator, FixNormalsOperator, ChangeHeadPretreatmentOperator, PrintSelectedVerticesOperator, ChangeHeadHoldoutOperator, ChangeHeadNewShapeOperator
from ....common.i18n.i18n import i18n
from ....common.types.framework import reg_order

class BasePanel(object):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True


@reg_order(0)
class MMRAddonPanel(BasePanel, bpy.types.Panel):
    bl_label = "UMA Addon Panel"
    bl_idname = "MMR_SCENE_PT_sample"
    bl_category = "MMR"

    def draw(self, context: bpy.types.Context):
        layout = self.layout

        layout.operator(GenerateControllerOperator.bl_idname)

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True

class MMDtoolsAddonPanel(BasePanel, bpy.types.Panel):
    bl_label = "UMA Addon Panel"
    bl_idname = "MMD_SCENE_PT_sample"
    bl_category = "MMD"

    def draw(self, context: bpy.types.Context):
        layout = self.layout

        split = layout.split(factor=0.7)
        split.operator(BoneLayerOperator.bl_idname)
        split.operator(BoneLayerResetOperator.bl_idname)

        layout.operator(FixEyeBoneOperator.bl_idname)

        layout.operator(CombineShapeKeysOperator.bl_idname)

        box = layout.box()
        box.label(text="Delete Selected Collections:")
        row = box.row()
        row.prop(context.scene, "delete_handle_collection", text="handle")
        row.prop(context.scene, "delete_face_collection", text="face")
        row.prop(context.scene, "delete_others_collection", text="others")

        box.operator(BoneSimplifyOperator.bl_idname)        
        box.label(text="Only works on umamusume skeletons layered by this plugin", icon="ERROR")
        box.label(text="Please remove the bones you want to keep from the selected collection", icon="ERROR")

        layout.operator(PrintSelectedVerticesOperator.bl_idname)

        layout.label(text="Change-head secondary creation:")
        layout.operator(ChangeHeadPretreatmentOperator.bl_idname)
        split = layout.split(factor=0.5)
        split.operator(ChangeHeadHoldoutOperator.bl_idname)
        split.operator(ChangeHeadNewShapeOperator.bl_idname)        

        layout.label(text="Fix mini umamusume model:")
        split = layout.split(factor=0.5)
        split.operator(FixBlushOperator.bl_idname)
        split.operator(FixNormalsOperator.bl_idname)

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True

# This panel will be drawn after ExampleAddonPanel since it has a higher order value
# @reg_order(1)
# class ExampleAddonPanel2(BasePanel, bpy.types.Panel):
#     bl_label = "Example Addon Side Bar Panel"
#     bl_idname = "SCENE_PT_sample2"

#     def draw(self, context: bpy.types.Context):
#         layout = self.layout
#         layout.label(text="Second Panel")
#         layout.operator(BoneLayerOperator.bl_idname)