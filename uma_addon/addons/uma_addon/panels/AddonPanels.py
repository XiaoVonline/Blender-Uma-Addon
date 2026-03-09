import bpy
from ..config import __addon_name__
from ..operators.AddonOperators import *
from ..operators.Controller import GenerateIK, BakeFKtoIK, ToggleTwistConstraints
from ..operators.Umashader import *
from ..operators.EarConvert import *
from ..operators.Motion import *
from ..operators.AnmiCopy import *

from ....common.i18n.i18n import i18n
from ....common.types.framework import reg_order
from ..utils.Config_handling import get_panel_name
from ..image.ImageManager import get_image_id

class BasePanel(object):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = get_panel_name()

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return True

@reg_order(0)
class ModelProcessPanel(BasePanel, bpy.types.Panel):
    bl_label = "Processing Model"
    bl_idname = "SCENE_PT_umaaddonpanel1"

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        scene_props = context.scene.uma_scene
        prefs = context.preferences.addons[__addon_name__].preferences
        obj_props = getattr(context.active_object, "uma_object", None)

        row = layout.row()
        row.operator("mmd_tools.import_model", text="Import")
        row.operator(SetBoneCollections.bl_idname)
        row.operator(RefineBoneStructure.bl_idname)
        row = layout.row(align=True)
        row.prop(scene_props, "del_handle", toggle=True, translate=False)
        row.prop(scene_props, "del_face", toggle=True, translate=False)
        row.prop(scene_props, "del_others", toggle=True, translate=False)
        row.operator(SimplifyArmature.bl_idname)

        layout.operator(ApplyShader.bl_idname, icon="SHADING_RENDERED")
        layout.operator(FixMini.bl_idname, icon="SHADERFX")

        layout.label(text="Use shape keys to drive ear bones")
        split = layout.split(factor=0.7, align=True)
        split.prop_search(scene_props, "ear_target", prefs, "ear_targets")
        split.operator(EarConvert.bl_idname, icon="DRIVER")

class ChangeHeadPanel(BasePanel, bpy.types.Panel):
    bl_label = "Change Head"
    bl_idname = "SCENE_PT_umaaddonpanel2"
    bl_parent_id = "SCENE_PT_umaaddonpanel1"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        
        row = layout.row()
        row.operator(ChangeHeadPretreat.bl_idname)
        row.operator(ChangeHeadHoldout.bl_idname)
        layout.label(text="Create a new absolute shape key:")
        row = layout.row()
        row.operator(ChangeHeadNewShape.bl_idname)        
        row.operator(ChangeHeadCopyShape.bl_idname)

class UMA_UL_Action(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        row = layout.row(align=True)
        fav_icon = 'FUND' if item.is_favorite else 'NONE'
        row.prop(item, "display_name", text="", icon=fav_icon, emboss=False)

class UMA_UL_Mappings(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
        # 无效时警告
        layout.alert = not item.is_valid()
        row  = layout.row(align=True)

        def mapping():
            source_arm = context.scene.uma_scene.action_source
            if source_arm:
                row.prop_search(item, 'target', source_arm.data, 'bones', text='', translate=False, icon='BONE_DATA')
                row.label(icon='FORWARD')
                row.label(text=item.owner, translate=False, icon='BONE_DATA' if context.scene.uma_scene.action_target.data.bones.get(item.owner) else 'CANCEL')
            else:
                row.label(text=' ', icon='CANCEL')
                row.label(icon='FORWARD')
                row.label(text=item.owner, translate=False, icon='BONE_DATA' if context.scene.uma_scene.action_target.data.bones.get(item.owner) else 'CANCEL')
        def rotation():
            row.prop(item, 'has_rotoffs', icon='CON_ROTLIKE', icon_only=True)
            layout.label(text=item.owner, translate=False)
            if item.has_rotoffs:
                layout.prop(item, 'offset', text='')
        def location():
            row.prop(item, 'has_loccopy', icon='CON_LOCLIKE', icon_only=True)
            layout.label(text=item.owner, translate=False)
            if item.has_loccopy:
                layout.row().prop(item, 'loc_axis', text='', toggle=True)

        draw = {0: mapping, 1: rotation, 2: location}
        draw[context.scene.uma_scene.editing_type]()

@reg_order(1)
class PhysicsandActionsPanel(BasePanel, bpy.types.Panel):
    bl_label = "Physics & Action"
    bl_idname = "SCENE_PT_umaaddonpanel3"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        scene_props = context.scene.uma_scene
        obj_props = getattr(context.active_object, "uma_object", None)
        
        layout.label(text="Physics", icon="PHYSICS")
        row = layout.row(align=True)
        # if obj_props and :
        row.prop(context.scene.damped_track, "ear_enable", toggle=True, text="Ear")
        row.prop(context.scene.damped_track, "bust_enable", toggle=True, text="Bust")
        row.prop(context.scene.damped_track, "tail_enable", toggle=True, text="Tail", text_ctxt="UMA")

        row = layout.row()
        row.alignment = 'LEFT' 
        if scene_props.is_uma_acton:
            row.operator(UmaActionMode.bl_idname, icon="ANIM", emboss=False)
            cat = scene_props.action_category
            if cat == "tail":
                row = layout.row(align=True)
                row.prop(scene_props, "action_category", text_ctxt="UMA")
            elif cat == "ear":
                row = layout.row(align=True)
                row.prop(scene_props, "action_category")
                row.prop(scene_props, "level1")
                if scene_props.level2 != "None":
                    row.prop(scene_props, "level2")
                    if scene_props.level3 != "None":
                        row.prop(scene_props, "level3")

            if scene_props.filtered_actions:
                curr_item = scene_props.filtered_actions[scene_props.action_index]
                fav_icon = 'FUND' if curr_item.is_favorite else 'HEART'
            else:
                fav_icon = 'HEART'
            row = layout.row()
            col = row.column(align=True)
            box = col.box()
            box_row = box.row()
            if cat == 'ear':
                box_row.operator(ApplyKeyAction.bl_idname)
            elif cat == 'tail':
                box_row.operator(ApplyAction.bl_idname)
            col.template_list(
                "UMA_UL_Action", "", 
                scene_props, "filtered_actions", 
                scene_props, "action_index", 
                type='GRID', 
                columns=4, rows=14
            )
            box_row.operator(ToggleFavorite.bl_idname, text="", icon=fav_icon)
        else:
            row.operator(AnyActionMode.bl_idname, icon="ANIM", emboss=False)
            row = layout.row(align=True)
            row.prop(scene_props, 'action_source', text='', icon='ARMATURE_DATA', translate=False)
            row.label(icon='FORWARD')
            row.prop(scene_props, 'action_target', text='', icon='ARMATURE_DATA', translate=False)

            row = layout.row()
            left = row.column(align=True)
            box = left.box()
            box_row = box.row()

            # 编辑模式切换
            box_row.operator(SelectEditType.bl_idname, text='Map', icon='PRESET', emboss=True, depress=scene_props.editing_type==0).selected_type = 0
            box_row.operator(SelectEditType.bl_idname, text='Rot', icon='CON_ROTLIKE', emboss=True, depress=scene_props.editing_type==1).selected_type = 1
            box_row.operator(SelectEditType.bl_idname, text='Pos', icon='CON_LOCLIKE', emboss=True, depress=scene_props.editing_type==2).selected_type = 2
            box_row.separator()
            if scene_props.editing_type==2:
                box_row.operator(BonePositionToZero.bl_idname)
            box_row.operator(Umapping.bl_idname, icon_value=get_image_id("umapping"), text='')

            # 映射列表
            if scene_props.action_target:
                arm = scene_props.action_target.data.uma_armature
                left.template_list(
                    'UMA_UL_Mappings', '', 
                    arm, 'mappings', 
                    arm, 'active_mapping',
                    rows=14
                )
            else:
                left.template_list(
                    'UMA_UL_Mappings', '', 
                    scene_props, 'dummy_coll', 
                    scene_props, 'dummy_idx',
                    rows=14
                )

            # 预设菜单
            # box = left.box().row(align=True)
            # box.menu(BAC_MT_presets.__name__, text=BAC_MT_presets.bl_label, translate=False)
            # box.operator(AddPresetBACMapping.bl_idname, icon='ADD')
            # box.separator()
            # box.operator('kumopult_bac.open_preset_folder', text="", icon='FILE_FOLDER')

            row = layout.row()
            pre_icon = 'HIDE_OFF' if scene_props.preview else 'HIDE_ON'
            row.operator(TogglePreview.bl_idname, icon=pre_icon, depress=scene_props.preview)
            row.operator(BakeAnm.bl_idname, icon='NLA')

@reg_order(2)
class ControllerPanel(BasePanel, bpy.types.Panel):
    bl_label = "Controller"
    bl_idname = "SCENE_PT_umaaddonpanel4"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context: bpy.types.Context):
        layout = self.layout
        obj_props = getattr(context.active_object, "uma_object", False)
        if obj_props:
            layout.operator(ToggleTwistConstraints.bl_idname, text="Auto Twist", depress=obj_props.auto_twist_bones)
        else:
            layout.operator(ToggleTwistConstraints.bl_idname, text="Auto Twist")
        layout.operator(GenerateIK.bl_idname, icon='BONE_DATA')
        layout.operator(BakeFKtoIK.bl_idname, icon='SNAP_ON')
    