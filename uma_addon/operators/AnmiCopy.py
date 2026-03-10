import bpy
import difflib
# import os
# from bl_operators.presets import AddPresetBase
from ..utils.Utils import alert_error, BONE_MAPPING_DICT, UMA_BONES

# class BAC_MT_presets(bpy.types.Menu):
#     bl_label = "映射表预设"
#     preset_subdir = "kumopult_bac"
#     preset_operator = "script.execute_preset"
#     draw = bpy.types.Menu.draw_preset

# class AddPresetBACMapping(AddPresetBase, bpy.types.Operator):
#     bl_idname = "kumopult_bac.mappings_preset_add"
#     bl_label = ""
#     bl_description = "将当前骨骼映射表保存为预设，以供后续直接套用"
#     preset_menu = "BAC_MT_presets"

#     # variable used for all preset values
#     preset_defines = [
#         "s = bpy.context.scene.kumopult_bac_owner.data.kumopult_bac"
#     ]

#     # properties to store in the preset
#     preset_values = [
#         "s.mappings",
#         "s.selected_count"
#     ]

#     # where to store the preset
#     preset_subdir = "kumopult_bac"

# class BAC_OT_OpenPresetFolder(bpy.types.Operator):
#     bl_idname = 'kumopult_bac.open_preset_folder'
#     bl_label = '打开预设文件夹'

#     def execute(self, context):
#         os.system('explorer ' + bpy.utils.resource_path('USER') + '\scripts\presets\kumopult_bac')
#         return {'FINISHED'}

class SelectEditType(bpy.types.Operator):
    bl_idname = 'uma.select_edit_type'
    bl_label = ''
    bl_options = {'UNDO'}
    selected_type: bpy.props.IntProperty(override={'LIBRARY_OVERRIDABLE'})

    def execute(self, context):
        context.scene.uma_scene.editing_type = self.selected_type
        return {'FINISHED'}

class BakeAnm(bpy.types.Operator):
    bl_idname = 'uma.bake_anm'
    bl_label = 'Bake'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene_props = context.scene.uma_scene
        anm = scene_props.action_source.animation_data

        if anm:
            bpy.ops.object.mode_set(mode='OBJECT')
            context.view_layer.objects.active = scene_props.action_target
            bpy.ops.object.mode_set(mode='POSE')
            bpy.ops.pose.select_all(action='DESELECT')                

            target_bones = scene_props.action_target.pose.bones
            for b in UMA_BONES:
                if target_bones.get(b):
                    # 选中约束的骨骼
                    target_bones.get(b).select = True
                    # 打开约束
                    for c in target_bones.get(b).constraints:
                        if c.name in {'BAC_ROT_COPY', 'BAC_ROT_ROLL', 'BAC_LOC_COPY'}:
                            c.mute = False
            bpy.ops.nla.bake(
                frame_start=int(anm.action.frame_range[0]),
                frame_end=int(anm.action.frame_range[1]),
                step=1,
                only_selected=True,
                visual_keying=True,
                clear_constraints=True,
                clear_parents=True,
                use_current_action=True,
                clean_curves=True,
                bake_types = {'POSE'},
                channel_types= {'LOCATION', 'ROTATION'}
            )
            bpy.ops.uma.group_fcurves_by_bone()
            return {'FINISHED'}
        else:
            alert_error('Bake Failed', '源骨架上没有动作！')
            return {'CANCELLED'}

class Umapping(bpy.types.Operator):
    """Mapping for umamusume"""
    bl_idname = 'uma.umapping'
    bl_label = ''
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        scene_props = context.scene.uma_scene
        return scene_props.action_source and scene_props.action_target

    def execute(self, context):
        bones = context.scene.uma_scene.action_target.pose.bones
        for n in UMA_BONES:
            bone = bones.get(n)
            if bone:
                for con in reversed(bone.constraints):
                    if con.name in {'BAC_ROT_COPY', 'BAC_ROT_ROLL', 'BAC_LOC_COPY'}:
                        bone.constraints.remove(con)

        arm = context.scene.uma_scene.action_target.data.uma_armature
        arm.mappings.clear()
        sor_bones = context.scene.uma_scene.action_source.data.bones
        sor_bones = {b.name.lower(): b.name for b in sor_bones}

        for b in UMA_BONES:
            mapping = arm.mappings.add()
            mapping.owner = b

        # 精确匹配
        unmatched_uma_bones = []
        for i, b in enumerate(UMA_BONES):
            mapping = arm.mappings[i]
            search_names = [b] + BONE_MAPPING_DICT.get(b,[])
            not_match = True

            for n in search_names:
                n_lower = n.lower()
                
                if n_lower in sor_bones:
                    mapping.target = sor_bones[n_lower]
                    del sor_bones[n_lower]
                    not_match = False
                    break 

            if not_match:
                unmatched_uma_bones.append((i, search_names))

        # 模糊匹配
        for i, search_names in unmatched_uma_bones:
            for n in search_names:
                n_lower = n.lower()
                unmatched_sor_bones = list(sor_bones.keys())
                close_matches = difflib.get_close_matches(
                    n_lower, 
                    unmatched_sor_bones, 
                    n=1, 
                    cutoff=0.8
                )
                
                if close_matches:
                    mapping = arm.mappings[i]
                    best_match_key = close_matches[0]
                    mapping.target = sor_bones[best_match_key]
                    del sor_bones[best_match_key]
                    break 
        return {'FINISHED'}           

class TogglePreview(bpy.types.Operator):
    bl_idname = 'uma.toggle_preview'
    bl_label = 'Preview'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.scene.uma_scene.action_target
    
    def execute(self, context):
        scene_props = context.scene.uma_scene
        target_bones = scene_props.action_target.pose.bones

        for b in UMA_BONES:
            if target_bones.get(b):
                for c in target_bones.get(b).constraints:
                    if c.name in {'BAC_ROT_COPY', 'BAC_ROT_ROLL', 'BAC_LOC_COPY'}:
                        c.mute = scene_props.preview
        scene_props.preview = not scene_props.preview
        return {'FINISHED'}

class BonePositionToZero(bpy.types.Operator):
    """If Hip copied location, apply it to the Hip after baking"""
    bl_idname = 'uma.bone_position_to_zero'
    bl_label = 'To Zero'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        # bones.active = bones.get(self.mappings[self.active_mapping].target)
        return context.scene.uma_scene.action_target and context.scene.uma_scene.action_target.data.bones.active
    
    def execute(self, context):
        arm_obj = context.scene.uma_scene.action_target
        active_bone = arm_obj.data.bones.active
        if not active_bone:
            self.report({'ERROR'}, "未选中任何骨骼")
            return {'CANCELLED'}

        # 获取动作数据
        anim_data = arm_obj.animation_data
        if not anim_data or not anim_data.action:
            self.report({'ERROR'}, "骨架没有绑定动作")
            return {'CANCELLED'}
        action = anim_data.action

        current_frame = context.scene.frame_current
        bone_name = active_bone.name

        # 收集该骨骼的所有位移曲线
        loc_fcurves = []
        for fcurve in action.fcurves:
            if fcurve.data_path.startswith(f'pose.bones["{bone_name}"].location'):
                loc_fcurves.append(fcurve)

        if not loc_fcurves:
            self.report({'WARNING'}, f"骨骼 '{bone_name}' 没有位移动画曲线")
            return {'CANCELLED'}

        # 对每条位移曲线分别处理
        for fcurve in loc_fcurves:
            # 计算当前帧的值作为偏移量
            offset = fcurve.evaluate(current_frame)

            # 修改所有关键帧的值及手柄
            for kfp in fcurve.keyframe_points:
                # 关键帧值
                kfp.co[1] -= offset
                # 左手柄 Y 值
                kfp.handle_left[1] -= offset
                # 右手柄 Y 值
                kfp.handle_right[1] -= offset

        self.report({'INFO'}, f"已对骨骼 '{bone_name}' 应用位移归零偏移")
        return {'FINISHED'}
    