import bpy
import os
import mathutils
import math
import bmesh
from mathutils import Vector

from ..config import __addon_name__
# from ..preference.AddonPreferences import ExampleAddonPreferences

class BoneLayerOperator(bpy.types.Operator):
    '''Layer the umamusume skeleton'''
    # 唯一的操作标识符，用于找到和调用这个操作
    bl_idname = "object.uma_bonelayer_ops"
    # 操作的显示名称 
    bl_label = "Set Armature Layers"
    # 确保在操作之前备份数据，用户撤销操作时可以恢复
    bl_options = {'REGISTER', 'UNDO'}

    # 操作的前提条件
    @classmethod
    def poll(cls, context: bpy.types.Context):
        # 检查当前上下文是否有选中的对象，并且该对象是骨架类型
        return context.active_object is not None and context.active_object.type == 'ARMATURE' and len(context.selected_objects) == 1

    # 执行操作的具体方法
    def execute(self, context: bpy.types.Context):

        # 获取当前骨架对象和数据
        armature_obj = context.active_object
        armature_data = armature_obj.data

        # 创建名为"Body"的骨骼集合
        collection = armature_data.collections.get("Body")
        if not collection:
            collection = armature_data.collections.new("Body")        
        bones_name = {"Eye_L", "Eye_R", "Head", "Neck", "Chest", "Spine", "Waist", "UpBody_Ctrl", "Hip"}
        bones = [bone for bone in armature_data.bones if bone.name in bones_name]
        body_count = 0
        for bone in bones:
            collection.assign(bone)
            body_count += 1
        if body_count == 0:
            armature_data.collections.remove(collection)

        # 创建名为"Arm"的骨骼集合
        collection = armature_data.collections.get("Arm")
        if not collection:
            collection = armature_data.collections.new("Arm")        
        bones_name = {"Shoulder_L", "Shoulder_R", "Arm_L", "Arm_R", "ShoulderRoll_L", "ShoulderRoll_R", "ArmRoll_L", "ArmRoll_R", "Elbow_L", "Elbow_R", "Wrist_L", "Wrist_R"}
        bones = [bone for bone in armature_data.bones if bone.name in bones_name]
        arm_count = 0
        for bone in bones:
            collection.assign(bone)
            arm_count += 1
        if arm_count == 0:
            armature_data.collections.remove(collection)

        # 创建名为"Leg"的骨骼集合
        collection = armature_data.collections.get("Leg")
        if not collection:
            collection = armature_data.collections.new("Leg")
        bones_name = {"Thigh_L", "Thigh_R", "Knee_L", "Knee_R", "Ankle_L", "Ankle_R", "Ankle_offset_L", "Ankle_offset_R", "Toe_L", "Toe_R", "Toe_offset_L", "Toe_offset_R"}
        bones = [bone for bone in armature_data.bones if bone.name in bones_name]
        leg_count = 0
        for bone in bones:
            collection.assign(bone)
            leg_count += 1
        if leg_count == 0:
            armature_data.collections.remove(collection)

        # 创建名为"Finger"的骨骼集合
        collection = armature_data.collections.get("Finger")
        if not collection:
            collection = armature_data.collections.new("Finger")
        bones_name = {"Thumb_01_L", "Thumb_02_L", "Thumb_03_L", "Index_01_L", "Index_02_L", "Index_03_L", "Middle_01_L", "Middle_02_L", "Middle_03_L", "Ring_01_L", "Ring_02_L", "Ring_03_L", "Pinky_01_L", "Pinky_02_L", "Pinky_03_L", "Thumb_01_R", "Thumb_02_R", "Thumb_03_R", "Index_01_R", "Index_02_R", "Index_03_R", "Middle_01_R", "Middle_02_R", "Middle_03_R", "Ring_01_R", "Ring_02_R", "Ring_03_R", "Pinky_01_R", "Pinky_02_R", "Pinky_03_R"}
        bones = [bone for bone in armature_data.bones if bone.name in bones_name]
        finger_count = 0
        for bone in bones:
            collection.assign(bone)
            finger_count += 1
        if finger_count == 0:
            armature_data.collections.remove(collection)

        # 创建名为"Hair"的骨骼集合
        collection = armature_data.collections.get("Hair")
        if not collection:
            collection = armature_data.collections.new("Hair")
        # 设置集合为不可见
        collection.is_visible = False  
        # 查找所有名称中含"Tali"且不以"Handle"结尾的骨骼
        bones = [bone for bone in armature_data.bones if "Hair" in bone.name and not bone.name.endswith("Handle")]
        hair_count = len(bones)
        for bone in bones:
            collection.assign(bone)
        if hair_count == 0:
            armature_data.collections.remove(collection)

        # 创建名为"Phys"的骨骼集合
        collection = armature_data.collections.get("Phys")
        if not collection:
            collection = armature_data.collections.new("Phys")
        # 设置集合为不可见
        collection.is_visible = False  
        # 查找所有名称中含"Sp_"且不以"Handle"结尾不以"Sp_He_Ear"和"Sp_He_Hair"开头的骨骼
        bones = [bone for bone in armature_data.bones if "Sp_" in bone.name and not bone.name.endswith("Handle") and not bone.name.startswith("Sp_He_Ear") and not bone.name.startswith("Sp_He_Hair")]
        phys_count = len(bones)
        for bone in bones:
            collection.assign(bone)
        if phys_count == 0:
            armature_data.collections.remove(collection)

        # 创建名为"Tail"的骨骼集合
        collection = armature_data.collections.get("Tail")
        if not collection:
            collection = armature_data.collections.new("Tail")
        # 查找所有名称中含"Tali"且不以"Handle"结尾的骨骼
        bones = [bone for bone in armature_data.bones if "Tail" in bone.name and not bone.name.endswith("Handle")]
        tail_count = len(bones)
        for bone in bones:
            collection.assign(bone)
        if tail_count == 0:
            armature_data.collections.remove(collection)

        # 创建名为"Handle"的骨骼集合
        collection = armature_data.collections.get("Handle")
        if not collection:
            collection = armature_data.collections.new("Handle")        
        # 设置集合为不可见
        collection.is_visible = False        
        # 查找所有名称以"Handle"结尾的骨骼
        bones = [bone for bone in armature_data.bones if bone.name.endswith("Handle")]
        handle_count = len(bones)   
        # 所有匹配的骨骼，添加到集合
        for bone in bones:
             collection.assign(bone)
        if handle_count == 0:
            armature_data.collections.remove(collection) 
        
        # 创建名为"Ear"的骨骼集合
        collection = armature_data.collections.get("Ear")
        if not collection:
            collection = armature_data.collections.new("Ear")
        # 设置集合为不可见
        collection.is_visible = False  
        # 查找所有名称中含"Tali"且不以"Handle"结尾和"Sp_"开头的骨骼
        bones = [bone for bone in armature_data.bones if "Ear" in bone.name and not bone.name.endswith("Handle") and not bone.name.startswith("Sp_")]
        ear_count = len(bones)
        for bone in bones:
            collection.assign(bone)
        if ear_count == 0:
            armature_data.collections.remove(collection)

        # 创建名为"Face"的骨骼集合
        collection = armature_data.collections.get("Face")
        if not collection:
            collection = armature_data.collections.new("Face")        
        # 设置集合为不可见
        collection.is_visible = False        
        # 添加所有名称以"Eye"开头的骨骼，但排除Eye_L和Eye_R
        bones = [bone for bone in armature_data.bones if bone.name.startswith("Eye") and bone.name not in {"Eye_L", "Eye_R"}]
        face_count = len(bones)   
        for bone in bones:
             collection.assign(bone)
        # 添加所有名称以"Mouth"开头的骨骼
        bones = [bone for bone in armature_data.bones if bone.name.startswith("Mouth")]
        face_count += len(bones) 
        for bone in bones:
             collection.assign(bone)
        # 添加所有名称以"Cheek"开头的骨骼
        bones = [bone for bone in armature_data.bones if bone.name.startswith("Cheek")]
        face_count += len(bones) 
        for bone in bones:
             collection.assign(bone)
        # 添加所有名称以"Tooth"开头的骨骼
        bones = [bone for bone in armature_data.bones if bone.name.startswith("Tooth")]
        face_count += len(bones)
        for bone in bones:
             collection.assign(bone)
        # 添加所有名称以"Tongue"开头的骨骼
        bones = [bone for bone in armature_data.bones if bone.name.startswith("Tongue")]
        face_count += len(bones)
        for bone in bones:
             collection.assign(bone)
        # 添加名称为Chin, Nose, M_Line00"的骨骼
        bones_name = {"Chin", "Nose", "M_Line00"}
        bones = [bone for bone in armature_data.bones if bone.name in bones_name]
        face_count += len(bones)
        for bone in bones:
             collection.assign(bone)
        # 添加名称为M_Cheek, M_Eye, M_Mayu_L, M_Mayu_R, M_Mouth的骨骼
        bones_name = {"M_Cheek", "M_Eye", "M_Mayu_L", "M_Mayu_R", "M_Mouth"}
        bones = [bone for bone in armature_data.bones if bone.name in bones_name]
        face_count += len(bones)        
        for bone in bones:
            collection.assign(bone)

        if face_count == 0:
            armature_data.collections.remove(collection)

        # 创建名为"Others"的骨骼集合
        collection = armature_data.collections.get("Others")
        if not collection:
            collection = armature_data.collections.new("Others")        
        # 设置集合为不可见
        collection.is_visible = False        
        # 添加名称为Wrist_L_Pole, Wrist_R_Pole, Wrist_L_Target, Wrist_R_Target, Hand_Attach_L, Hand_Attach_R的骨骼
        bones_name = {"Wrist_L_Pole", "Wrist_R_Pole", "Wrist_L_Target", "Wrist_R_Target", "Hand_Attach_L", "Hand_Attach_R"}
        bones = [bone for bone in armature_data.bones if bone.name in bones_name]
        others_count = len(bones)
        for bone in bones:
             collection.assign(bone)
        # 添加所有名称以"Head"开头的骨骼，但排除Head
        bones = [bone for bone in armature_data.bones if bone.name.startswith("Head") and bone.name != "Head" and bone.name != "Head_Handle"]
        others_count += len(bones)
        for bone in bones:
             collection.assign(bone)
        # 添加所有名称以"Sp_He_Ear"开头的骨骼
        bones = [bone for bone in armature_data.bones if bone.name.startswith("Sp_He_Ear")]
        others_count += len(bones)
        for bone in bones:
             collection.assign(bone)
        if others_count == 0:
            armature_data.collections.remove(collection)

        # 找出所有未被任何集合包含的骨骼
        bones = []
        for bone in armature_data.bones:
            assigned = False
            for coll in armature_data.collections:
                if bone.name in coll.bones:
                    assigned = True
                    break
            if not assigned:
                bones.append(bone.name)
        unassigned_count = len(bones)

        if unassigned_count != 0:
            # 创建名为"Unassigned"的骨骼集合
            collection = armature_data.collections.get("Unassigned")
            if not collection:
                collection = armature_data.collections.new("Unassigned")        
            collection.is_visible = False
            # 移动未分层的骨骼
            for bone in bones:
                collection.assign(armature_data.bones[bone])

        match handle_count + face_count + others_count + hair_count + ear_count + phys_count + unassigned_count:
            case 0:
                self.report({'INFO'}, "No bones are hidden; No bones are unassigned")
            case 1:
                match unassigned_count:
                    case 0:
                        self.report({'INFO'}, "1 bone is hidden; No bones are unassigned")
                    case 1:
                        self.report({'INFO'}, "1 bone is hidden and unassigned")
            case _:
                match unassigned_count:
                    case 0:
                        self.report({'INFO'}, f"{handle_count + face_count + others_count + hair_count + ear_count + phys_count + unassigned_count} bone is hidden; No bones are unassigned")
                    case 1:
                        self.report({'INFO'}, f"{handle_count + face_count + others_count + hair_count + ear_count + phys_count + unassigned_count} bone is hidden; 1 bone is unassigned")
                    case _:
                        self.report({'INFO'}, f"{handle_count + face_count + others_count + hair_count + ear_count + phys_count + unassigned_count} bone is hidden; {unassigned_count} bones are unassigned")
        return {'FINISHED'}

class BoneLayerResetOperator(bpy.types.Operator):
    '''Reset the umamusume skeleton collections'''
    bl_idname = "object.uma_bonelayerreset_ops"
    bl_label = "Reset"
    bl_options = {'REGISTER', 'UNDO'}

    # 操作的前提条件
    @classmethod
    def poll(cls, context: bpy.types.Context):
        # 检查当前上下文是否有选中的对象，并且该对象是骨架类型
        return context.active_object is not None and context.active_object.type == 'ARMATURE' and len(context.selected_objects) == 1
    
    def execute(self, context: bpy.types.Context):
        armature_obj = context.active_object
        armature_data = armature_obj.data

        collections_to_remove = ["Body", "Arm", "Leg", "Finger", "Hair", "Phys", "Tail", "Handle", "Ear", "Face", "Others", "Unassigned"]
        for collection_name in collections_to_remove:
            collection = armature_data.collections.get(collection_name)
            if collection:
                armature_data.collections.remove(collection)

        self.report({'INFO'}, "Armature collections have been reset")
        return {'FINISHED'}

class BoneSimplifyOperator(bpy.types.Operator):
    '''Delete selected collections and bones in it'''
    bl_idname = "object.uma_bonesimplify_ops"
    bl_label = "Simplify Armature"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE' and context.scene.delete_handle_collection | context.scene.delete_face_collection | context.scene.delete_others_collection  and len(context.selected_objects) == 1

    def transfer_weights_to_head(self, armature_obj, bone_names_to_remove):
        """Transfer vertex weights from specified bones to the Head bone"""
        head_bone_name = "Head"
        
        # 获取所有使用当前骨架的网格对象
        mesh_objs = []
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                for mod in obj.modifiers:
                    if mod.type == 'ARMATURE' and mod.object == armature_obj:
                        mesh_objs.append(obj)
                        break
        
        for obj in mesh_objs:
            # 确保网格对象有顶点组
            if not obj.vertex_groups:
                continue
            
            # 获取或创建Head顶点组
            head_vg = obj.vertex_groups.get(head_bone_name)
            if not head_vg:
                head_vg = obj.vertex_groups.new(name=head_bone_name)
            
            # 遍历所有顶点
            for vertex in obj.data.vertices:
                total_weight = 0.0
                
                # 计算要删除骨骼的权重总和
                for group in vertex.groups:
                    vg = obj.vertex_groups[group.group]
                    if vg.name in bone_names_to_remove:
                        total_weight += group.weight * obj.vertex_groups[vg.name].weight(vertex.index)
                
                # 如果有权重要转移
                if total_weight > 0:
                    # 获取当前Head权重
                    current_head_weight = 0.0
                    for group in vertex.groups:
                        if obj.vertex_groups[group.group].name == head_bone_name:
                            current_head_weight = group.weight
                            break
                    
                    # 计算新权重（不超过1.0）
                    new_weight = min(current_head_weight + total_weight, 1.0)
                    head_vg.add([vertex.index], new_weight, 'REPLACE')
            
            # 移除要删除骨骼的顶点组
            for bone_name in bone_names_to_remove:
                vg = obj.vertex_groups.get(bone_name)
                if vg:
                    obj.vertex_groups.remove(vg)

    def execute(self, context: bpy.types.Context):
        count = 0
        armature_obj = context.active_object
        armature_data = armature_obj.data
        current_mode = armature_obj.mode

        if context.scene.delete_handle_collection:
            # 删除名为"Handle"的骨骼集合中的所有骨骼
            if current_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            collection_to_remove = armature_data.collections.get("Handle")
            if collection_to_remove:
                bone_names_to_remove = [bone.name for bone in collection_to_remove.bones]
                bpy.ops.object.mode_set(mode='EDIT')
                edit_bones = armature_data.edit_bones
                for bone_name in bone_names_to_remove:
                    bone = edit_bones.get(bone_name)
                    if bone:
                        bone.parent = None
                        for child in bone.children_recursive:
                            child.parent = None
                        edit_bones.remove(bone)
                        count += 1
                armature_data.collections.remove(collection_to_remove)

        if context.scene.delete_face_collection:
            # 删除名为"Face"的骨骼集合中的所有骨骼
            bpy.ops.object.mode_set(mode='OBJECT')
            collection_to_remove = armature_data.collections.get("Face")
            if collection_to_remove:
                bone_names_to_remove = [bone.name for bone in collection_to_remove.bones]
                
                # 在删除骨骼前转移权重到Head
                self.transfer_weights_to_head(armature_obj, bone_names_to_remove)
                
                # 删除骨骼
                bpy.ops.object.mode_set(mode='EDIT')
                edit_bones = armature_data.edit_bones
                for bone_name in bone_names_to_remove:
                    bone = edit_bones.get(bone_name)
                    if bone:
                        bone.parent = None
                        for child in bone.children_recursive:
                            child.parent = None
                        edit_bones.remove(bone)
                        count += 1
                armature_data.collections.remove(collection_to_remove)

        if context.scene.delete_others_collection:
            # 删除名为"Others"的骨骼集合中的所有骨骼
            bpy.ops.object.mode_set(mode='OBJECT')
            collection_to_remove = armature_data.collections.get("Others")
            if collection_to_remove:
                bone_names_to_remove = [bone.name for bone in collection_to_remove.bones]
                bpy.ops.object.mode_set(mode='EDIT')
                edit_bones = armature_data.edit_bones
                # 在删除骨骼前，如果被删除的骨骼有子骨骼，则将子骨骼的父骨骼设为Head
                # 查找Head骨骼（作为新的父骨骼）
                head_bone = edit_bones.get("Head")
                for bone_name in bone_names_to_remove:
                    bone = edit_bones.get(bone_name)
                    if bone:
                        # 如果存在Head骨骼且当前骨骼有子骨骼
                        if head_bone and bone.children:
                            for child in bone.children:
                                # 将子骨骼重新父级到Head骨骼
                                child.parent = head_bone
                        bone.parent = None
                        for child in bone.children_recursive:
                            child.parent = None
                        edit_bones.remove(bone)
                        count += 1
                armature_data.collections.remove(collection_to_remove)

        # 恢复原始模式
        bpy.ops.object.mode_set(mode=current_mode)

        match count:
            case 0:
                self.report({'INFO'}, "No bones are deleted")
            case 1:
                self.report({'INFO'}, "1 bone is deleted")
            case _:
                self.report({'INFO'}, f"{count} bones are deleted")
        return {'FINISHED'}
    
class GenerateControllerOperator(bpy.types.Operator):
    '''Generate controller for umamusume'''
    bl_idname = "object.uma_generatecontroller_ops"
    bl_label = "Generate Controller"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE' and len(context.selected_objects) == 1

    def execute(self, context: bpy.types.Context):
        
        armature_obj = context.active_object  

        if "ShoulderRoll_L" not in armature_obj.data.bones:
            self.report({'ERROR'}, "ShoulderRoll_L bone not found")
            return {'CANCELLED'}
        if "ShoulderRoll_R" not in armature_obj.data.bones:
            self.report({'ERROR'}, "ShoulderRoll_R bone not found")
            return {'CANCELLED'}
        if "ArmRoll_L" not in armature_obj.data.bones:
            self.report({'ERROR'}, "ArmRoll_L bone not found")
            return {'CANCELLED'}
        if "ArmRoll_R" not in armature_obj.data.bones:
            self.report({'ERROR'}, "ArmRoll_R bone not found")
            return {'CANCELLED'}

        try:
            result = bpy.ops.object.uma_fixeyebone_ops()
            if result != {'FINISHED'}:
                self.report({'ERROR'}, "Failed to fix eye bones")
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"{str(e)}")
            return {'CANCELLED'}
    
        rename_map = {
            "ShoulderRoll_L": "腕捩.L",
            "ShoulderRoll_R": "腕捩.R",
            "ArmRoll_L": "手捩.L",
            "ArmRoll_R": "手捩.R"
        }
        reverse_map = {v: k for k, v in rename_map.items()}

        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = armature_obj.data.edit_bones
        for eng_name, jp_name in rename_map.items():
            if bone := edit_bones.get(eng_name):
                bone.name = jp_name
        bpy.ops.object.mode_set(mode='OBJECT')

        context.object.mmr.Import_presets = True
        Original_Hide_mmd_skeleton = context.object.mmr.Hide_mmd_skeleton
        context.object.mmr.Hide_mmd_skeleton = True
        context.object.mmr.json_filepath = os.path.join(os.path.dirname(__file__), "umaviewer.json")
        bpy.ops.object.mmr_rig()
        context.object.mmr.Hide_mmd_skeleton = Original_Hide_mmd_skeleton
        rigify_active = context.active_object
        context.view_layer.objects.active = armature_obj

        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = armature_obj.data.edit_bones
        for jp_name, eng_name in reverse_map.items():
            if bone := edit_bones.get(jp_name):
                bone.name = eng_name
        bpy.ops.object.mode_set(mode='OBJECT')

        bpy.context.active_object.hide_set(True)
        rigify_active.select_set(True)
        bpy.context.view_layer.objects.active = rigify_active

        self.report({'INFO'}, "Controller generated successfully")
        return {'FINISHED'}

class FixEyeBoneOperator(bpy.types.Operator):
    '''Repairs bones used to control binocular movements'''
    bl_idname = "object.uma_fixeyebone_ops"
    bl_label = "Fix Eye Bone"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE' and len(context.selected_objects) == 1

    def execute(self, context: bpy.types.Context):

        armature_obj = context.active_object
        current_mode = armature_obj.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # 检测是否存在眼部骨骼
        if "Eye_L" not in armature_obj.data.bones or "Eye_R" not in armature_obj.data.bones:
            self.report({'ERROR'}, "Eye_L and Eye_R bones not found")
            return {'CANCELLED'}

        mesh_objects = []
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                for mod in obj.modifiers:
                    if mod.type == 'ARMATURE' and mod.object == armature_obj:
                        mesh_objects.append(obj)
                        break
        
        for mesh_obj in mesh_objects:
            if "Head" not in mesh_obj.vertex_groups:
                head_group = mesh_obj.vertex_groups.new(name="Head")
            else:
                head_group = mesh_obj.vertex_groups["Head"]
            
            # 处理每个眼部骨骼
            for eye_bone in ["Eye_L", "Eye_R"]:
                if eye_bone in mesh_obj.vertex_groups:
                    eye_group = mesh_obj.vertex_groups[eye_bone]                    
                    # 遍历网格的所有顶点
                    for vert in mesh_obj.data.vertices:
                        try:
                            # 获取顶点在眼部骨骼组的权重
                            weight = eye_group.weight(vert.index)
                            
                            # 添加到Head组, 替换原有权重
                            head_group.add([vert.index], weight, 'REPLACE')
                        except RuntimeError:
                            # 顶点不在该组中则跳过
                            continue                    
                    # 删除眼部骨骼顶点组
                    mesh_obj.vertex_groups.remove(eye_group)

        bpy.ops.object.mode_set(mode='EDIT')
        edit_bones = armature_obj.data.edit_bones

        for bone_name in ["Eye_L", "Eye_R"]:
            if bone_name in edit_bones:
                bone = edit_bones[bone_name]
                if  bone.length > 0.07:
                    # 旋转眼部骨骼
                    bone.matrix @= mathutils.Matrix.Rotation(math.radians(90), 4, 'X')
                    # 缩小眼部骨骼
                    bone.length *= 0.4
                
        # 为该骨架控制的网格添加形态键驱动器
        for mesh_obj in mesh_objects:
            if mesh_obj.data.shape_keys:
                # 右眼水平形态键
                right_hsk_name = "Eye_20_R(XRange)[M_Face]"
                if right_hsk_name in mesh_obj.data.shape_keys.key_blocks:
                    # 创建驱动器
                    drv = mesh_obj.data.shape_keys.key_blocks[right_hsk_name].driver_add("value").driver
                    drv.type = 'SCRIPTED'                    
                    # 添加变量
                    var = drv.variables.new()
                    var.name = "eye_rot"
                    var.type = 'TRANSFORMS'
                    target = var.targets[0]
                    target.id = armature_obj
                    target.bone_target = "Eye_R"
                    target.transform_type = 'ROT_Z'
                    target.transform_space = 'LOCAL_SPACE'                    
                    # 设置表达式
                    drv.expression = "eye_rot * 2"
                
                # 左眼水平形态键
                left_hsk_name = "Eye_20_L(XRange)[M_Face]"
                if left_hsk_name in mesh_obj.data.shape_keys.key_blocks:
                    # 创建驱动器
                    drv = mesh_obj.data.shape_keys.key_blocks[left_hsk_name].driver_add("value").driver
                    drv.type = 'SCRIPTED'                    
                    # 添加变量
                    var = drv.variables.new()
                    var.name = "eye_rot"
                    var.type = 'TRANSFORMS'
                    target = var.targets[0]
                    target.id = armature_obj
                    target.bone_target = "Eye_L"
                    target.transform_type = 'ROT_Z'
                    target.transform_space = 'LOCAL_SPACE'                    
                    # 设置表达式
                    drv.expression = "eye_rot * 2"

                # 右眼垂直形态键
                right_vsk_name = "Eye_21_R(YRange)[M_Face]"
                if right_vsk_name in mesh_obj.data.shape_keys.key_blocks:
                    # 创建驱动器
                    drv = mesh_obj.data.shape_keys.key_blocks[right_vsk_name].driver_add("value").driver
                    drv.type = 'SCRIPTED'                    
                    # 添加变量
                    var = drv.variables.new()
                    var.name = "eye_rot"
                    var.type = 'TRANSFORMS'
                    target = var.targets[0]
                    target.id = armature_obj
                    target.bone_target = "Eye_R"
                    target.transform_type = 'ROT_X'
                    target.transform_space = 'LOCAL_SPACE'                    
                    # 设置表达式
                    drv.expression = "eye_rot * 2"

                # 左眼垂直形态键
                left_vsk_name = "Eye_21_L(YRange)[M_Face]"
                if left_vsk_name in mesh_obj.data.shape_keys.key_blocks:
                    # 创建驱动器
                    drv = mesh_obj.data.shape_keys.key_blocks[left_vsk_name].driver_add("value").driver
                    drv.type = 'SCRIPTED'                    
                    # 添加变量
                    var = drv.variables.new()
                    var.name = "eye_rot"
                    var.type = 'TRANSFORMS'
                    target = var.targets[0]
                    target.id = armature_obj
                    target.bone_target = "Eye_L"
                    target.transform_type = 'ROT_X'
                    target.transform_space = 'LOCAL_SPACE'                    
                    # 设置表达式
                    drv.expression = "- eye_rot * 2"

        # 将形态键的范围设置为-2到2
        for mesh_obj in mesh_objects:
            if mesh_obj.data.shape_keys:
                for key_block in mesh_obj.data.shape_keys.key_blocks:
                    if "Eye_20" in key_block.name or "Eye_21" in key_block.name:
                        key_block.slider_min = -2.0
                        key_block.slider_max = 2.0

        bpy.ops.object.mode_set(mode=current_mode)
        self.report({'INFO'}, "Eye bones fixed successfully")
        return {'FINISHED'}
    
class CombineShapeKeysOperator(bpy.types.Operator):
    '''Generate left-right symmetirc combination form keys'''
    bl_idname = "object.uma_combineshapekeys_ops"
    bl_label = "Combine Shape Keys"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object and context.active_object.type == 'MESH' and len(context.selected_objects) == 1
    
    def execute(self, context: bpy.types.Context):
        mesh_obj = context.active_object
        if not mesh_obj.data.shape_keys or not mesh_obj.data.shape_keys.key_blocks:
            self.report({'ERROR'}, "The selected mesh has no shape keys")
            return {'CANCELLED'}
        if len(mesh_obj.data.shape_keys.key_blocks) <= 1:
            self.report({'ERROR'}, "The selected mesh has no shape keys to combine")
            return {'CANCELLED'}
        
        shape_keys = mesh_obj.data.shape_keys.key_blocks
        for key in shape_keys:
            key.value = 0.0
        
        eyebrow_pairs = [
            ("WaraiA", 1), ("WaraiB", 2), ("WaraiC", 3), ("WaraiD", 4),
            ("IkariA", 5), ("KanasiA", 6), ("DoyaA", 7), ("DereA", 8),
            ("OdorokiA", 9), ("OdorokiB", 10), ("JitoA", 11), ("KomariA", 12),
            ("KusyoA", 13), ("UreiA", 14), ("RunA", 15), ("RunB", 16),
            ("SeriousA", 17), ("SeriousB", 18), ("ShiwaA", 19), ("ShiwaB", 20),
            ("Offset_U", 21), ("Offset_D", 22)
        ]
        
        for name, num in eyebrow_pairs:
            right_key = f"EyeBrow_{num}_R({name})[M_Face]"
            left_key = f"EyeBrow_{num}_L({name})[M_Face]"
            
            if right_key in shape_keys and left_key in shape_keys:
                shape_keys[right_key].value = 1.0
                shape_keys[left_key].value = 1.0
                bpy.ops.object.shape_key_add(from_mix=True)
                new_key = mesh_obj.data.shape_keys.key_blocks[-1]
                new_key.name = f"EyeBrow_{num}({name})"
                shape_keys[right_key].value = 0
                shape_keys[left_key].value = 0
        
        eye_pairs = [
            ("HalfA", 1), ("CloseA", 2), ("HalfB", 3), ("HalfC", 4),
            ("WaraiA", 5), ("WaraiB", 6), ("WaraiC", 7), ("WaraiD", 8),
            ("IkariA", 9), ("KanasiA", 10), ("DereA", 11), ("OdorokiA", 12),
            ("OdorokiB", 13), ("OdorokiC", 14), ("JitoA", 15), ("KusyoA", 16),
            ("UreiA", 17), ("RunA", 18), ("DrivenA", 19),
            ("EyeHideA", 22), ("SeriousA", 23), ("PupilA", 24),
            ("PupilB", 25), ("PupilC", 26), ("EyelidHideA", 27), ("EyelidHideB", 28)
        ]
        
        for name, num in eye_pairs:
            right_key = f"Eye_{num}_R({name})[M_Face]"
            left_key = f"Eye_{num}_L({name})[M_Face]"
            
            if right_key in shape_keys and left_key in shape_keys:
                shape_keys[right_key].value = 1.0
                shape_keys[left_key].value = 1.0
                bpy.ops.object.shape_key_add(from_mix=True)
                new_key = mesh_obj.data.shape_keys.key_blocks[-1]
                new_key.name = f"Eye_{num}({name})"
                shape_keys[right_key].value = 0
                shape_keys[left_key].value = 0
        
        ear_pairs = [
            ("Base_N", 1), ("Kanasi", 2), ("Dere_N", 3), ("Dere", 4),
            ("Yure", 5), ("Biku_N", 6), ("Biku", 7), ("Ikari", 8),
            ("Tanosi", 9), ("Up_N", 10), ("Up", 11), ("Down", 12),
            ("Front", 13), ("Side", 14), ("Back", 15), ("Roll", 16)
        ]
        
        for name, num in ear_pairs:
            right_key = f"Ear_{num}_R({name})[M_Hair]"
            left_key = f"Ear_{num}_L({name})[M_Hair]"
            
            if right_key in shape_keys and left_key in shape_keys:
                shape_keys[right_key].value = 1.0
                shape_keys[left_key].value = 1.0
                bpy.ops.object.shape_key_add(from_mix=True)
                new_key = mesh_obj.data.shape_keys.key_blocks[-1]
                new_key.name = f"Ear_{num}({name})"
                shape_keys[right_key].value = 0
                shape_keys[left_key].value = 0
        
        return {'FINISHED'}
    
class FixBlushOperator(bpy.types.Operator):
    '''Fix blush of mini umamusume model'''
    bl_idname = "object.miniuma_fixblush_ops"
    bl_label = "Fix Blush"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.selected_objects and context.active_object.type == 'MESH' and context.active_object.mode == 'OBJECT' and len(context.selected_objects) == 1

    def execute(self, context: bpy.types.Context):
        
        # 将其中名为cheek材质所对应的顶点删除
        obj = context.active_object
        mesh = obj.data

        # 查找名为cheek的材质索引
        cheek_mat_index = None
        for idx, mat in enumerate(mesh.materials):
            if mat and "cheek" in mat.name:
                cheek_mat_index = idx
                break

        if cheek_mat_index is None:
            self.report({'WARNING'}, "Blush already fixed or you chose an illegal model")
            return {'CANCELLED'}

        # 找到所有属于cheek材质的顶点
        verts_to_delete = set()
        for poly in mesh.polygons:
            if poly.material_index == cheek_mat_index:
                verts_to_delete.update(poly.vertices)

        # 进入编辑模式，选中并删除这些顶点
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(mesh)
        bm.verts.ensure_lookup_table()
        for v in bm.verts:
            v.select = False
        for idx in verts_to_delete:
            if idx < len(bm.verts):
                bm.verts[idx].select = True
        bmesh.update_edit_mesh(mesh)
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')

        # 删除名为cheek的材质
        mesh.materials.pop(index=cheek_mat_index)

        # 查找名为face0的材质索引
        cheek_mat_index = None
        for idx, mat in enumerate(mesh.materials):
            if mat and "face0" in mat.name:
                cheek_mat_index = idx
                break

        if cheek_mat_index is None:
            self.report({'ERROR'}, "Face material not found")
            return {'CANCELLED'}
        
        # 在face0材质中增添一个图像纹理节点
        mat = mesh.materials[cheek_mat_index]

        nodes = mat.node_tree.nodes

        # for node in nodes:
        #     print("Node name:", node.name)

        for node in nodes:
            if node.type == 'TEX_IMAGE':
                image_tex_node = node
                break
        image_tex_node = nodes.new(type='ShaderNodeTexImage')
        image_tex_node.label = "Blushed Face Texture"
        image_tex_node.name = "Blushed Face Texture"
        image_tex_node.location = (-830, 950)

        # 在face0材质中增添一个混合颜色节点
        mix_node = nodes.new(type='ShaderNodeMixRGB')
        mix_node.label = "Blush level"
        mix_node.name = "Blush level"
        mix_node.location = (-500, 1100)
        mix_node.inputs['Fac'].default_value = 1.0

        # 查找节点
        for node in nodes:
            if 'mmd_base' in node.name:
                mmd_base_tex_node = node
                break
        for node in nodes:
            if 'mmd_sh' in node.name:
                mmd_sh_node = node
                break
        
        # 连接节点
        mat.node_tree.links.new(mmd_base_tex_node.outputs['Color'], mix_node.inputs['Color1'])
        mat.node_tree.links.new(image_tex_node.outputs['Color'], mix_node.inputs['Color2'])
        mat.node_tree.links.new(mix_node.outputs['Color'], mmd_sh_node.inputs['Base Tex'])

        # 加载纹理图片
        script_file = os.path.realpath(__file__)
        script_dir = os.path.dirname(script_file)
        blush_texture_path = os.path.join(script_dir, "tex_mchr0001_00_faceblush0_1_diff.png")
        
        try:
            if os.path.exists(blush_texture_path):
                # 检查是否已存在同名图片
                existing_image = bpy.data.images.get("tex_mchr0001_00_faceblush0_1_diff.png")
                if existing_image:
                    image_tex_node.image = existing_image
                else:
                    # 加载新图片
                    image = bpy.data.images.load(blush_texture_path)
                    image_tex_node.image = image
                self.report({'INFO'}, "Blush texture loaded successfully")
            else:
                self.report({'WARNING'}, f"Blush texture not found at: {blush_texture_path}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to load blush texture: {str(e)}")
            return {'CANCELLED'}

        bpy.ops.file.pack_all()

        self.report({'INFO'}, "Blush fixed successfully")
        return {'FINISHED'}

class FixNormalsOperator(bpy.types.Operator):
    '''Fix normals of mini umamusume model'''
    bl_idname = "object.miniuma_fixnormals_ops"
    bl_label = "Fix Normals"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.selected_objects and context.active_object.type == 'MESH' and context.active_object.mode == 'OBJECT' and len(context.selected_objects) == 1

    def execute(self, context: bpy.types.Context):

        bpy.ops.mmd_tools.separate_by_materials()

        # 只保留名字以mouth结尾的mesh对象为选中状态
        for obj in context.selected_objects:
            if "mouth" in obj.name:
                obj.select_set(True)
            else:
                obj.select_set(False)
        
        # 检查是否只有一个mesh对象为选中状态
        if len(context.selected_objects) != 1:
            bpy.ops.mmd_tools.join_meshes()
            self.report({'ERROR'}, "There must be exactly one mouth mesh or you chose an illegal model")
            return {'CANCELLED'}

        # 将现在的选中项设置为活动项
        if context.selected_objects:
            context.view_layer.objects.active = context.selected_objects[0]
        
        bpy.ops.object.mode_set(mode='EDIT')

        # 全选顶点，按松散块分离
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.separate(type='LOOSE')
        bpy.ops.object.mode_set(mode='OBJECT')

        if len(context.selected_objects) == 2:
            if "Goo Engine" in bpy.app.version_string:
                bpy.data.objects.remove(context.selected_objects[-1], do_unlink=True)

                vertices_to_select = [67, 68, 77, 78, 79, 80, 81, 82, 84, 94, 102, 103, 105, 107, 121, 122, 123, 124, 125, 127, 128, 131, 133, 134, 159, 164, 166, 167, 209, 212, 213, 216, 217, 222, 224, 231, 256, 257, 261, 262, 263, 267, 269, 374, 375, 377, 378, 379, 380, 382]

            else:
                # 删除活动项，并将选中项命名为活动项的名称
                old_name = context.active_object.name
                bpy.data.objects.remove(context.selected_objects[0], do_unlink=True)
                context.selected_objects[0].name = old_name

                vertices_to_select = [149, 151, 152, 153, 154, 156, 157, 262, 264, 268, 269, 270, 274, 275, 300, 307, 309, 314, 315, 318, 319, 322, 364, 365, 367, 372, 397, 398, 400, 403, 404, 406, 407, 408, 409, 410, 424, 426, 428, 429, 437, 447, 449, 450, 451, 452, 453, 454, 463, 464]

        else:
            if context.selected_objects[0].parent:
                for obj in context.selected_objects[0].parent.children:
                    obj.select_set(True)
                bpy.ops.object.join()
            self.report({'WARNING'}, "Normals already fixed or you chose an illegal model")
            return {'CANCELLED'}

        # 选中选中项同一父级下的eye和face对象
        if context.selected_objects[0].parent:
            for obj in context.selected_objects[0].parent.children:
                if "face0" in obj.name or "eye" in obj.name:
                    obj.select_set(True)
                else:
                    obj.select_set(False)

        # 将face对象设定为活动项
        if "Goo Engine" in bpy.app.version_string:
            context.view_layer.objects.active = context.selected_objects[-1]
        else:
            context.view_layer.objects.active = context.selected_objects[0]

        bpy.ops.object.join()
        obj = bpy.context.active_object
        bpy.ops.object.mode_set(mode="EDIT")
        
        # 选中顶点
        mesh = bmesh.from_edit_mesh(obj.data)
        mesh.verts.ensure_lookup_table()

        for v in mesh.verts:
            v.select = False
        for index in vertices_to_select:
                mesh.verts[index].select = True
        bmesh.update_edit_mesh(obj.data)

        # 删除选中的顶点
        bpy.ops.mesh.delete(type='VERT')

        bpy.ops.object.mode_set(mode='OBJECT')

        # 选中选中项同一父级下的mouth和face对象
        if context.selected_objects[0].parent:
            for obj in context.selected_objects[0].parent.children:
                if "face0" in obj.name or "mouth" in obj.name:
                    obj.select_set(True)
                else:
                    obj.select_set(False)
        if context.selected_objects:
            context.view_layer.objects.active = context.selected_objects[0]
        bpy.ops.object.join()

        # 按距离合并顶点
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.mesh.remove_doubles(threshold=0.0001)

        # 重新计算法向（外侧）
        bpy.ops.mesh.normals_make_consistent(inside=False)

        # 平滑矢量
        bpy.ops.mesh.smooth_normals()

        bpy.ops.object.mode_set(mode='OBJECT')

        # 选中选中项同一父级下的对象并合并
        if context.selected_objects[0].parent:
            for obj in context.selected_objects[0].parent.children:
                obj.select_set(True)
            bpy.ops.object.join()

        obj = context.active_object        

        # 查找mouth材质的索引
        mouth_mat_index = None
        for idx, mat in enumerate(obj.data.materials):
            if mat and "mouth" in mat.name:
                mouth_mat_index = idx
                break
        
        if mouth_mat_index is None:
            self.report({'ERROR'}, "Mouth material not found")
            return {'CANCELLED'}
        
        # 选择指定材质的面
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')
        for poly in obj.data.polygons:
            poly.select = (poly.material_index == mouth_mat_index)        
        
        # 选择UV
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.select_all(action='SELECT')

        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.active
        
        if not uv_layer:
            self.report({'ERROR'}, "No active UV layer found")
            return {'CANCELLED'}
        
        # 变换UV
        for face in bm.faces:
            if face.select:
                for loop in face.loops:
                    loop[uv_layer].uv.y += 1.77 / 2
                    loop[uv_layer].uv.x -= 0.804
                    loop[uv_layer].uv.x *= 1.8

        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.object.mode_set(mode='OBJECT')

        self.report({'INFO'}, "Normals fixed successfully")
        return {'FINISHED'}

class ChangeHeadPretreatmentOperator(bpy.types.Operator):
    '''Make the umamusume model more suitable for the production of change-head secondary creation'''
    bl_idname = "object.uma_changeheadpretreat_ops"
    bl_label = "Pretreat"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None and context.active_object.type == 'EMPTY' and len(context.selected_objects) == 1

    def execute(self, context: bpy.types.Context):
        obj = context.active_object
       
        # 获取活动项的名称，去掉活动项的名称的前五位，记录为一个新的名称
        original_name = obj.name
        new_name = original_name[5:] if len(original_name) > 5 else original_name

        # 选中活动项子级中的骨架
        child_armature = None
        for child in obj.children:
            if child.type == 'ARMATURE':
                child_armature = child
                break
        
        if not child_armature:
            self.report({'ERROR'}, "No child armature found!")
            return {'CANCELLED'}
        
        # 将选中的骨架设置为活动项，取消选中选中的空物体
        obj = child_armature
        obj.select_set(True)
        context.view_layer.objects.active = context.selected_objects[1]
        context.selected_objects[0].select_set(False)

        if "Neck" not in obj.data.bones:
            self.report({'INFO'}, "Already processed or you chose an illegal model")
            return {'FINISHED'}
        
        # 选中Head骨并切断
        bpy.ops.object.mode_set(mode='POSE')
        head_bone = obj.pose.bones.get("Head")
        if head_bone:
            head_bone.bone.select = True
            bpy.ops.mmd_tools.model_separate_by_bones(separate_armature=True, include_descendant_bones=True, boundary_joint_owner='DESTINATION')
        else:
            self.report({'ERROR'}, "Head bone not found!")
            return {'CANCELLED'}

        # 将活动项名称改为之前记录的新名称
        active_obj = context.active_object
        context.active_object.name = new_name
        active_collection = None

        # 查找活动对象所在的集合
        for coll in bpy.data.collections:
            if active_obj.name in coll.objects:
                active_collection = coll
                break
        
        if not active_collection:
            self.report({'ERROR'}, "Active object not found in any collection!")
            return {'CANCELLED'}

        # 递归获取所有子对象
        def get_all_children(obj):
            children = []
            for child in obj.children:
                children.append(child)
                children.extend(get_all_children(child))
            return children

        # 收集所有需要删除的对象
        objects_to_delete = set()
        for obj in active_collection.objects:
            if obj.name.endswith(active_obj.name) and obj != active_obj:
                objects_to_delete.add(obj)
                objects_to_delete.update(get_all_children(obj))

        # 直接删除这些对象而不依赖选择
        if objects_to_delete:
            # 创建要删除的对象名称列表
            object_names_to_delete = [obj.name for obj in objects_to_delete]
            
            # 遍历对象名称而不是对象引用
            for obj_name in object_names_to_delete:
                # 检查对象是否仍然存在
                if obj_name not in bpy.data.objects:
                    continue
                    
                obj = bpy.data.objects[obj_name]
                
                # 确保对象没有被保护
                obj.hide_select = False
                obj.hide_viewport = False
                obj.hide_render = False
                
                # 从所有集合中移除
                for coll in list(obj.users_collection):
                    coll.objects.unlink(obj)
                
                # 删除对象数据（如果不再被其他对象使用）
                if obj.data and obj.data.users == 1:
                    if obj.type == 'MESH':
                        bpy.data.meshes.remove(obj.data, do_unlink=True)
                    elif obj.type == 'ARMATURE':
                        bpy.data.armatures.remove(obj.data, do_unlink=True)
                
                # 删除对象本身
                if obj_name in bpy.data.objects:
                    bpy.data.objects.remove(bpy.data.objects[obj_name], do_unlink=True)

        # 选中活动项子级中的骨架
        obj = context.active_object
        child_armature = None
        for child in obj.children:
            if child.type == 'ARMATURE':
                child_armature = child
                break
        # 将选中的骨架设置为活动项，取消选中选中的空物体
        obj = child_armature
        obj.select_set(True)
        context.view_layer.objects.active = context.selected_objects[1]
        context.selected_objects[0].select_set(False)

        try:
            result = bpy.ops.object.uma_bonelayer_ops()
            if result != {'FINISHED'}:
                self.report({'ERROR'}, "Failed to layer bones")
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"{str(e)}")
            return {'CANCELLED'}    

        ori_delete_handle_collection = context.scene.delete_handle_collection
        ori_delete_face_collection = context.scene.delete_face_collection       
        ori_delete_others_collection = context.scene.delete_others_collection
        context.scene.delete_handle_collection = True
        context.scene.delete_face_collection = True     
        context.scene.delete_others_collection = True
        try:
            result = bpy.ops.object.uma_bonesimplify_ops()
            if result != {'FINISHED'}:
                self.report({'ERROR'}, "Failed to fix simplify bones")
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"{str(e)}")
            return {'CANCELLED'}        
        context.scene.delete_handle_collection = ori_delete_handle_collection
        context.scene.delete_face_collection = ori_delete_face_collection  
        context.scene.delete_others_collection = ori_delete_others_collection
        
        try:
            result = bpy.ops.object.uma_fixeyebone_ops()
            if result != {'FINISHED'}:
                self.report({'ERROR'}, "Failed to fix eye bones")
                return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"{str(e)}")
            return {'CANCELLED'}

        return {'FINISHED'}
    
class PrintSelectedVerticesOperator(bpy.types.Operator):
    '''Print selected vertex indexes to the console'''
    bl_idname = "object.print_selected_vertices"
    bl_label = "Print Vertex Indexes"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode == 'EDIT'

    def execute(self, context):

        obj = context.active_object
        bm = bmesh.from_edit_mesh(obj.data)
        selected_indices = [v.index for v in bm.verts if v.select]

        if not selected_indices:
            self.report({'WARNING'}, "No vertices selected")
            return {'CANCELLED'}

        # 输出到控制台
        print("Selected vertex indices:", selected_indices)
        self.report({'INFO'}, f"Print {len(selected_indices)} vertex indexes to the console")
        return {'FINISHED'}
    
class ChangeHeadHoldoutOperator(bpy.types.Operator):
    '''Reduce the workload of post-production keying by blocking render'''
    bl_idname = "object.uma_changeheadholdout_ops"
    bl_label = "Holdout"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context: bpy.types.Context):

        armature = context.active_object
        head_bone = armature.pose.bones.get('Head')

        if not head_bone: 
            self.report({'ERROR'}, "Head bone not found!")
            return {'CANCELLED'}
        
        # 获取骨骼的矩阵
        bone_matrix = armature.matrix_world @ head_bone.matrix            
        # 分解矩阵得到位置、旋转
        bone_loc, bone_rot, bone_scale = bone_matrix.decompose()            
        # 获取骨骼的Y轴方向
        bone_y_axis = bone_rot @ Vector((0, 1, 0))
        
        # 创建栅格对象
        bpy.ops.mesh.primitive_grid_add(
            x_subdivisions=5,
            y_subdivisions=10,
            size=1,
            enter_editmode=False,
            align='WORLD'
        )
        grid = context.active_object
        
        # x方向上缩小2倍
        grid.scale.x *= 0.5
        bpy.ops.object.transform_apply(scale=True)
        # 计算旋转，使栅格的Y轴对齐骨骼的Y轴
        grid.rotation_mode = 'QUATERNION'
        grid.rotation_quaternion = bone_rot            
        # 移动栅格到Head骨位置
        grid.location = bone_loc - (bone_y_axis * 0.53)
        
        # 确保Head骨可见以便设置父级
        head_bone_data = armature.data.bones.get('Head')
        was_head_visible = head_bone_data.hide
        head_bone_data.hide = False
        
        # 检查Head骨所在的骨骼集合的可见性
        head_bone_collections = []
        for coll in armature.data.collections:
            if head_bone_data.name in coll.bones:
                head_bone_collections.append(coll)
                was_collection_solo = coll.is_solo
                coll.is_solo = True


        # 刷新视图层
        context.view_layer.update()
        
        # 设置为Head骨子级
        context.view_layer.objects.active = armature
        grid.select_set(True)
        bpy.context.object.data.bones.active = bpy.context.object.data.bones["Head"]
        bpy.ops.object.parent_set(type='BONE')
        
        # 恢复原始可见性
        head_bone_data.hide = was_head_visible
        for coll in head_bone_collections:
            coll.is_solo = was_collection_solo

        # 启用绝对形态键
        grid.shape_key_add(name="Basis")
        grid.data.shape_keys.use_relative = False

        # 创建Holdout集合
        holdout_collection = bpy.data.collections.get("Holdout")
        if not holdout_collection:
            holdout_collection = bpy.data.collections.new("Holdout")
            bpy.context.scene.collection.children.link(holdout_collection)

        # 设置阻隔渲染
        if not "Holdout" in bpy.context.view_layer.layer_collection.children:
            self.report({'ERROR'}, "Holdout collection not found!")
            return {'CANCELLED'}
        layer_coll = bpy.context.view_layer.layer_collection.children["Holdout"]
        layer_coll.holdout = True
        for coll in grid.users_collection: coll.objects.unlink(grid)
        holdout_collection.objects.link(grid)

        bpy.ops.object.mode_set(mode='OBJECT')
        context.view_layer.objects.active = context.selected_objects[0]
        self.report({'INFO'}, "Grig generated successfully")
        return {'FINISHED'}
    
class ChangeHeadNewShapeOperator(bpy.types.Operator):
    '''From basis'''
    bl_idname = "object.uma_changeheadnewshape_ops"
    bl_label = "New"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None and context.active_object.type == 'MESH' and len(context.selected_objects) == 1 and context.active_object.mode == 'OBJECT' and context.active_object.data.shape_keys is not None

    def execute(self, context: bpy.types.Context):

        # 获取当前活动对象和基础形态键
        obj = context.active_object
        shape_keys = obj.data.shape_keys
        active_index = 0

        active_key = shape_keys.key_blocks[active_index]
        
        # 创建新的形态键
        new_key = obj.shape_key_add()
        
        # 选中新的形态键
        for idx, key in enumerate(obj.data.shape_keys.key_blocks):
            if key == new_key:
                obj.active_shape_key_index = idx
                break        
        
        # 直接复制顶点数据
        mesh = obj.data
        vertices = mesh.vertices
        
        # 复制顶点数据
        for i, vert in enumerate(vertices):
            # 绝对形态键的变形数据
            new_key.data[i].co = active_key.data[i].co.copy()

        # 将估算时刻设为新形态键的frame值
        shape_keys.eval_time = new_key.frame

        # 将估算时刻注册一个关键帧
        shape_keys.keyframe_insert(data_path="eval_time")

        # 切换到编辑模式
        bpy.ops.object.mode_set(mode='EDIT')        
        self.report({'INFO'}, f"New shapekey generated successfully with eval_time set to {new_key.frame}")
        return {'FINISHED'}
    
class ChangeHeadCopyShapeOperator(bpy.types.Operator):
    '''From active shape key'''
    bl_idname = "object.uma_changeheadcopyshape_ops"
    bl_label = "Copy"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None and context.active_object.type == 'MESH' and len(context.selected_objects) == 1 and context.active_object.mode == 'OBJECT' and context.active_object.data.shape_keys is not None

    def execute(self, context: bpy.types.Context):

        # 获取当前活动对象和活动形态键
        obj = context.active_object
        shape_keys = obj.data.shape_keys
        active_index = obj.active_shape_key_index

        active_key = shape_keys.key_blocks[active_index]
        
        # 创建新的形态键
        new_key = obj.shape_key_add()

        # 选中新的形态键
        for idx, key in enumerate(obj.data.shape_keys.key_blocks):
            if key == new_key:
                obj.active_shape_key_index = idx
                break
        
        # 直接复制顶点数据
        mesh = obj.data
        vertices = mesh.vertices

        # 复制顶点数据
        for i, vert in enumerate(vertices):
            new_key.data[i].co = active_key.data[i].co.copy()

        # 将估算时刻设为新形态键的frame值
        shape_keys.eval_time = new_key.frame

        # 将估算时刻注册一个关键帧
        shape_keys.keyframe_insert(data_path="eval_time")

        # 切换到编辑模式
        bpy.ops.object.mode_set(mode='EDIT')        
        self.report({'INFO'}, f"New shapekey generated successfully with eval_time set to {new_key.frame}")
        return {'FINISHED'}