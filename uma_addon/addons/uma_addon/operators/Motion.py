import bpy
import os
import re
from ..config import __addon_name__
from ..operators.Properties import get_action

class UmaActionMode(bpy.types.Operator):
    bl_idname = "uma.uma_action_mode"
    bl_label = "UMA Action"
    def execute(self, context):
        context.scene.uma_scene.is_uma_acton = False
        return {'FINISHED'}

class AnyActionMode(bpy.types.Operator):
    bl_idname = "uma.any_action_mode"
    bl_label = "Action"
    def execute(self, context):
        context.scene.uma_scene.is_uma_acton = True
        return {'FINISHED'}

class ToggleFavorite(bpy.types.Operator):
    bl_idname = "uma.toggle_favorite"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene_props = context.scene.uma_scene
        idx = scene_props.action_index
  
        if 0 <= idx < len(scene_props.filtered_actions):
            item = scene_props.filtered_actions[idx]
            item.is_favorite = not item.is_favorite
            bpy.ops.wm.save_userpref()
            
            if scene_props.action_category == "fav":
                get_action(scene_props, context)
        return {'FINISHED'}

class ApplyAction(bpy.types.Operator):
    bl_idname = "uma.apply_action"
    bl_label = "Apply Action"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        scene_props = context.scene.uma_scene
        idx = scene_props.action_index
        actions = scene_props.filtered_actions
        action_name = actions[idx].name

        # 检查是否选择了动作
        if not action_name or action_name == "NONE":
            self.report({'WARNING'}, "No action selected")
            return {'CANCELLED'}

        # 追加源动作
        blend_file = os.path.join(os.path.dirname(__file__), "Umashaders.blend")
        try:
            with bpy.data.libraries.load(blend_file, link=False) as (_, data_to):
                data_to.actions = [action_name]
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load action: {e}")
            return {'CANCELLED'}
        
        if not data_to.actions:
            self.report({'ERROR'}, f"{action_name} not found in library")
            return {'CANCELLED'}
        src_action = data_to.actions[0]

        # 获取目标动作
        obj = context.active_object
        if not obj.animation_data:
            obj.animation_data_create()
        
        target_action = obj.animation_data.action
        # 如果没有动作，创建动作
        if not target_action:
            target_action = bpy.data.actions.new(name=f"{obj.name}Action")
            obj.animation_data.action = target_action

        # 如果没有动作槽，创建并指定动作槽
        target_slot = None
        if hasattr(obj.animation_data, "action_slot"):
            target_slot = obj.animation_data.action_slot
            if not target_slot:
                target_slot = target_action.slots.new(name=obj.name, id_type='OBJECT')
                obj.animation_data.action_slot = target_slot

        for src_fc in src_action.fcurves:
            # 检查骨骼是否存在
            match = re.match(r'pose\.bones\["([^"]+)"\]', src_fc.data_path)
            if not match:
                continue
            bone_name = match.group(1)
            if not obj.data.bones.get(bone_name):
                print(f"WARNING: '{bone_name}' not found")
                continue

            # 获取目标动作的曲线
            if hasattr(target_action, "fcurve_ensure_for_datablock"):
                target_fc = target_action.fcurve_ensure_for_datablock(
                    datablock=obj, 
                    data_path=src_fc.data_path, 
                    index=src_fc.array_index
                )
            else:
                target_fc = target_action.fcurves.find(src_fc.data_path, index=src_fc.array_index)
                if not target_fc:
                    target_fc = target_action.fcurves.new(data_path=src_fc.data_path, index=src_fc.array_index)
            
            # 在目标动作中查找或创建同名组
            if src_fc.group:
                target_group = target_action.groups.get(src_fc.group.name)
                if not target_group:
                    target_group = target_action.groups.new(name=src_fc.group.name)
                if target_fc.group is None:
                    target_fc.group = target_group

            # 插入关键帧
            for src_key in src_fc.keyframe_points:
                # 计算偏移后的新时间
                new_time = src_key.co.x + context.scene.frame_current
                new_value = src_key.co.y

                # 在目标曲线插入关键帧
                new_key = target_fc.keyframe_points.insert(
                    frame=new_time,
                    value=new_value,
                    options={'FAST'}
                )
                
                # 复制关键帧的插值类型和手柄类型
                new_key.interpolation = src_key.interpolation
                new_key.handle_left_type = src_key.handle_left_type
                new_key.handle_right_type = src_key.handle_right_type
                new_key.easing = src_key.easing

            target_fc.update()

        bpy.data.actions.remove(src_action)
        context.area.tag_redraw()
        self.report({'INFO'}, f"Applied successfully")
        return {'FINISHED'}

class ApplyKeyAction(bpy.types.Operator):
    bl_idname = "uma.apply_key_action"
    bl_label = "Apply Action"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH' and context.active_object.data.shape_keys

    def execute(self, context):
        scene_props = context.scene.uma_scene
        idx = scene_props.action_index
        actions = scene_props.filtered_actions             
        action_name = actions[idx].name

        # 检查是否选择了动作
        if not action_name or action_name == "NONE":
            self.report({'WARNING'}, "No action selected")
            return {'CANCELLED'}

        # 从库文件中追加源动作
        blend_file = os.path.join(os.path.dirname(__file__), "Umashaders.blend")
        try:
            with bpy.data.libraries.load(blend_file, link=False) as (_, data_to):
                data_to.actions = [action_name]
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load action: {e}")
            return {'CANCELLED'}
        
        if not data_to.actions:
            self.report({'ERROR'}, f"{action_name} not found in library")
            return {'CANCELLED'}
        src_action = data_to.actions[0]

        # 获取目标对象和形态键数据块
        obj = context.active_object
        kb = obj.data.shape_keys

        # 确保形态键数据块有动画数据
        if not kb.animation_data:
            kb.animation_data_create()
        
        target_action = kb.animation_data.action

        # 如果没有动作，创建形态键动作
        if not target_action:
            target_action = bpy.data.actions.new(name=f"{obj.name}Action")
            target_action.id_root = 'KEY'
            kb.animation_data.action = target_action

        # 如果没有动作槽，创建并指定动作槽
        target_slot = None
        if hasattr(kb.animation_data, "action_slot"):
            target_slot = kb.animation_data.action_slot
            if not target_slot:
                target_slot = target_action.slots.new(name=obj.name, id_type='KEY')
                kb.animation_data.action_slot = target_slot

        for src_fc in src_action.fcurves:

            # 获取目标动作的曲线
            if hasattr(target_action, "layers"):
                if not target_action.layers:
                    strip = target_action.layers.new("Base_Layer")
                layer = target_action.layers[0]
                if not layer.strips:
                    strip = layer.strips.new(type='KEYFRAME')
                strip = layer.strips[0]
                channelbag = strip.channelbag(target_slot, ensure=True)
                target_fc = channelbag.fcurves.find(src_fc.data_path)
                if not target_fc:
                    target_fc = channelbag.fcurves.new(src_fc.data_path)
            else:
                target_fc = target_action.fcurves.find(src_fc.data_path, index=src_fc.array_index)
                if not target_fc:
                    target_fc = target_action.fcurves.new(data_path=src_fc.data_path, index=src_fc.array_index)

            # 复制并插入关键帧
            for src_key in src_fc.keyframe_points:
                # 计算偏移后的新时间
                new_time = src_key.co.x + context.scene.frame_current
                new_value = src_key.co.y

                # 在目标曲线插入关键帧
                new_key = target_fc.keyframe_points.insert(
                    frame=new_time,
                    value=new_value,
                    options={'FAST'}
                )
                
                # 复制关键帧属性
                new_key.interpolation = src_key.interpolation
                new_key.easing = src_key.easing
                new_key.handle_left_type = src_key.handle_left_type
                new_key.handle_right_type = src_key.handle_right_type

            target_fc.update()

        bpy.data.actions.remove(src_action)
        context.area.tag_redraw()
        self.report({'INFO'}, f"Applied successfully")
        return {'FINISHED'}
