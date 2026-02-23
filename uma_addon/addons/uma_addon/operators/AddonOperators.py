import bpy
import os
import mathutils
import math
import bmesh
from mathutils import Vector

from ..config import __addon_name__
# from ..preference.AddonPreferences import AddonPreferences

from ..utils.Utils import assign_bone_to_collection

class SetBoneCollections(bpy.types.Operator):
    '''Layer the umamusume skeleton'''
    bl_idname = "uma.set_bone_collections"
    bl_label = "Set Bone Collections"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        # 检查当前上下文是否有选中的对象，并且该对象是骨架类型
        return context.active_object and context.active_object.type == 'ARMATURE' and len(context.selected_objects) == 1

    def execute(self, context: bpy.types.Context):

        obj = context.active_object
        current_mode = obj.mode
        if current_mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # 创建名为"Root"的骨骼集合
        bones_name = {"Position"}
        root_count = 0
        for n in bones_name:
            if assign_bone_to_collection(obj, n,'Root'):
                root_count += 1
        # 设置集合为不可见
        obj.data.collections.get('Root').is_visible = False

        # 创建名为"Body"的骨骼集合
        bones_name = {"Eye_L", "Eye_R", "Head", "Neck", "Chest", "Spine", "Waist", "UpBody_Ctrl", "Hip"}
        body_count = 0
        for n in bones_name:
            if assign_bone_to_collection(obj, n,'Body'):
                body_count += 1

        # 创建名为"Arm"的骨骼集合
        bones_name = {"Shoulder_L", "Shoulder_R", "Arm_L", "Arm_R", "ShoulderRoll_L", "ShoulderRoll_R", "ArmRoll_L", "ArmRoll_R", "Elbow_L", "Elbow_R", "Wrist_L", "Wrist_R", "Hand_Attach_L", "Hand_Attach_R"}
        arm_count = 0
        for n in bones_name:
            if assign_bone_to_collection(obj, n,'Arm'):
                arm_count += 1

        # 创建名为"Leg"的骨骼集合
        bones_name = {"Thigh_L", "Thigh_R", "Knee_L", "Knee_R", "Ankle_L", "Ankle_R", "Ankle_offset_L", "Ankle_offset_R", "Toe_L", "Toe_R", "Toe_offset_L", "Toe_offset_R"}
        leg_count = 0
        for n in bones_name:
            if assign_bone_to_collection(obj, n,'Leg'):
                leg_count += 1

        # 创建名为"Finger"的骨骼集合
        bones_name = {"Thumb_01_L", "Thumb_02_L", "Thumb_03_L", "Index_01_L", "Index_02_L", "Index_03_L", "Middle_01_L", "Middle_02_L", "Middle_03_L", "Ring_01_L", "Ring_02_L", "Ring_03_L", "Pinky_01_L", "Pinky_02_L", "Pinky_03_L", "Thumb_01_R", "Thumb_02_R", "Thumb_03_R", "Index_01_R", "Index_02_R", "Index_03_R", "Middle_01_R", "Middle_02_R", "Middle_03_R", "Ring_01_R", "Ring_02_R", "Ring_03_R", "Pinky_01_R", "Pinky_02_R", "Pinky_03_R"}
        finger_count = 0
        for n in bones_name:
            if assign_bone_to_collection(obj, n,'Finger'):
             finger_count += 1

        # 创建名为"Hair"的骨骼集合
        data = obj.data
        collection = data.collections.get("Hair")
        if not collection:
            collection = data.collections.new("Hair")
        # 设置集合为不可见
        collection.is_visible = False  
        # 查找所有名称中含"Tali"且不以"Handle"结尾的骨骼
        bones = [bone for bone in data.bones if "Hair" in bone.name and not bone.name.endswith("Handle")]
        hair_count = len(bones)
        for bone in bones:
            collection.assign(bone)

        # 创建名为"Tail"的骨骼集合
        collection = data.collections.get("Tail")
        if not collection:
            collection = data.collections.new("Tail")
        # 设置集合为不可见
        collection.is_visible = False  
        # 查找所有名称中含"Tali"且不以"Handle"结尾的骨骼
        bones = [bone for bone in data.bones if "Tail" in bone.name and not bone.name.endswith("Handle")]
        tail_count = len(bones)
        for bone in bones:
            collection.assign(bone)

        # 创建名为"Ear"的骨骼集合
        collection = data.collections.get("Ear")
        if not collection:
            collection = data.collections.new("Ear")
        # 设置集合为不可见
        collection.is_visible = False  
        # 查找所有名称中含"Ear"且不以"Handle"结尾和"Sp_"开头的骨骼
        bones = [bone for bone in data.bones if "Ear" in bone.name and not bone.name.endswith("Handle") and not bone.name.startswith("Sp_")]
        ear_count = len(bones)
        for bone in bones:
            collection.assign(bone)

        # 创建名为"Phys"的骨骼集合
        collection = data.collections.get("Phys")
        if not collection:
            collection = data.collections.new("Phys")
        # 设置集合为不可见
        collection.is_visible = False  
        # 查找所有名称中含"Sp_"且不以"Handle"结尾不以"Sp_He_Hair"和"Sp_Hi_Tail"和"Sp_He_Ear"开头的骨骼
        bones = [bone for bone in data.bones if "Sp_" in bone.name and not bone.name.endswith("Handle") and not bone.name.startswith("Sp_He_Hair") and not bone.name.startswith("Sp_Hi_Tail") and not bone.name.startswith("Sp_He_Ear")]
        phys_count = len(bones)
        for bone in bones:
            collection.assign(bone)

        # 创建名为"Handle"的骨骼集合
        collection = data.collections.get("Handle")
        if not collection:
            collection = data.collections.new("Handle")        
        # 设置集合为不可见
        collection.is_visible = False        
        # 查找所有名称以"Handle"结尾的骨骼
        bones = [bone for bone in data.bones if bone.name.endswith("Handle")]
        handle_count = len(bones)   
        # 所有匹配的骨骼，添加到集合
        for bone in bones:
             collection.assign(bone)
        
        # 创建名为"Face"的骨骼集合
        collection = data.collections.get("Face")
        if not collection:
            collection = data.collections.new("Face")        
        # 设置集合为不可见
        collection.is_visible = False        
        # 添加所有名称以"Eye"开头的骨骼，但排除Eye_L和Eye_R
        bones = [bone for bone in data.bones if bone.name.startswith("Eye") and bone.name not in {"Eye_L", "Eye_R"}]
        face_count = len(bones)   
        for bone in bones:
             collection.assign(bone)
        # 添加所有名称以"Mouth"开头的骨骼
        bones = [bone for bone in data.bones if bone.name.startswith("Mouth")]
        face_count += len(bones) 
        for bone in bones:
             collection.assign(bone)
        # 添加所有名称以"Cheek"开头的骨骼
        bones = [bone for bone in data.bones if bone.name.startswith("Cheek")]
        face_count += len(bones) 
        for bone in bones:
             collection.assign(bone)
        # 添加所有名称以"Tooth"开头的骨骼
        bones = [bone for bone in data.bones if bone.name.startswith("Tooth")]
        face_count += len(bones)
        for bone in bones:
             collection.assign(bone)
        # 添加所有名称以"Tongue"开头的骨骼
        bones = [bone for bone in data.bones if bone.name.startswith("Tongue")]
        face_count += len(bones)
        for bone in bones:
             collection.assign(bone)
        # 添加名称为Chin, Nose, M_Line00"的骨骼
        bones_name = {"Chin", "Nose", "M_Line00"}
        bones = [bone for bone in data.bones if bone.name in bones_name]
        face_count += len(bones)
        for bone in bones:
             collection.assign(bone)
        # 添加名称为M_Cheek, M_Eye, M_Mayu_L, M_Mayu_R, M_Mouth的骨骼
        bones_name = {"M_Cheek", "M_Eye", "M_Mayu_L", "M_Mayu_R", "M_Mouth"}
        bones = [bone for bone in data.bones if bone.name in bones_name]
        face_count += len(bones)        
        for bone in bones:
            collection.assign(bone)

        # 创建名为"Others"的骨骼集合
        collection = data.collections.get("Others")
        if not collection:
            collection = data.collections.new("Others")        
        # 设置集合为不可见
        collection.is_visible = False        
        # 添加名称为Wrist_L_Pole, Wrist_R_Pole, Wrist_L_Target, Wrist_R_Target的骨骼
        bones_name = {"Wrist_L_Pole", "Wrist_R_Pole", "Wrist_L_Target", "Wrist_R_Target"}
        bones = [bone for bone in data.bones if bone.name in bones_name]
        others_count = len(bones)
        for bone in bones:
             collection.assign(bone)
        # 添加所有名称以"Head"开头的骨骼，但排除Head
        bones = [bone for bone in data.bones if bone.name.startswith("Head") and bone.name != "Head" and bone.name != "Head_Handle"]
        others_count += len(bones)
        for bone in bones:
             collection.assign(bone)
        # 添加所有名称以"Sp_He_Ear"开头的骨骼
        bones = [bone for bone in data.bones if bone.name.startswith("Sp_He_Ear") and not bone.name.endswith("Handle")]
        others_count += len(bones)
        for bone in bones:
             collection.assign(bone)

        # 找出所有未被任何集合包含的骨骼
        bones = []
        for bone in data.bones:
            assigned = False
            for coll in data.collections:
                if bone.name in coll.bones:
                    assigned = True
                    break
            if not assigned:
                bones.append(bone.name)

        unassigned_count = len(bones)

        if unassigned_count != 0:
            # 创建名为"Unassigned"的骨骼集合
            collection = data.collections.get("Unassigned")
            if not collection:
                collection = data.collections.new("Unassigned")        
            # 移动未分层的骨骼
            for bone in bones:
                collection.assign(data.bones[bone])

        bpy.ops.armature.collection_remove_unused()

        if current_mode == 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        match root_count + handle_count + face_count + others_count + hair_count + ear_count + phys_count + unassigned_count:
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
                        self.report({'INFO'}, f"{root_count + handle_count + face_count + others_count + hair_count + ear_count + phys_count + unassigned_count} bones are hidden")
                    case 1:
                        self.report({'INFO'}, f"{root_count + handle_count + face_count + others_count + hair_count + ear_count + phys_count + unassigned_count} bones are hidden; 1 bone is unassigned")
                    case _:
                        self.report({'INFO'}, f"{root_count + handle_count + face_count + others_count + hair_count + ear_count + phys_count + unassigned_count} bones are hidden; {unassigned_count} bones are unassigned")
        return {'FINISHED'}

class SimplifyArmature(bpy.types.Operator):
    '''Delete selected collections and bones in it'''
    bl_idname = "uma.simplify_armature"
    bl_label = "Del"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE' and context.scene.del_handle | context.scene.del_face | context.scene.del_others and len(context.selected_objects) == 1

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
        
        arm_obj = context.active_object
        data = arm_obj.data
        current_mode = arm_obj.mode
        count = 0

        if context.scene.del_handle:
            # 删除名为"Handle"的骨骼集合中的所有骨骼
            if current_mode != 'OBJECT':
                bpy.ops.object.mode_set(mode='OBJECT')
            collection_to_remove = data.collections.get("Handle")
            if collection_to_remove:
                bone_names_to_remove = [bone.name for bone in collection_to_remove.bones]
                bpy.ops.object.mode_set(mode='EDIT')
                edit_bones = data.edit_bones
                for bone_name in bone_names_to_remove:
                    bone = edit_bones.get(bone_name)
                    if bone:
                        bone.parent = None
                        for child in bone.children_recursive:
                            child.parent = None
                        edit_bones.remove(bone)
                        count += 1
                data.collections.remove(collection_to_remove)

        if context.scene.del_face:
            # 删除名为"Face"的骨骼集合中的所有骨骼
            bpy.ops.object.mode_set(mode='OBJECT')
            collection_to_remove = data.collections.get("Face")
            if collection_to_remove:
                bone_names_to_remove = [bone.name for bone in collection_to_remove.bones]
                
                # 在删除骨骼前转移权重到Head
                self.transfer_weights_to_head(arm_obj, bone_names_to_remove)
                
                # 删除骨骼
                bpy.ops.object.mode_set(mode='EDIT')
                edit_bones = data.edit_bones
                for bone_name in bone_names_to_remove:
                    bone = edit_bones.get(bone_name)
                    if bone:
                        bone.parent = None
                        for child in bone.children_recursive:
                            child.parent = None
                        edit_bones.remove(bone)
                        count += 1
                data.collections.remove(collection_to_remove)

        if context.scene.del_others:
            # 删除名为"Others"的骨骼集合中的所有骨骼
            bpy.ops.object.mode_set(mode='OBJECT')
            collection_to_remove = data.collections.get("Others")
            if collection_to_remove:
                bone_names_to_remove = [bone.name for bone in collection_to_remove.bones]
                bpy.ops.object.mode_set(mode='EDIT')
                edit_bones = data.edit_bones
                # 在删除骨骼前，如果被删除的骨骼有子骨骼，则将子骨骼的父骨骼设为Head
                # 查找Head骨骼作为新的父骨骼
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
                data.collections.remove(collection_to_remove)

        # 恢复原始模式
        bpy.ops.object.mode_set(mode=current_mode)

        match count:
            case 0:
                self.report({'INFO'}, "No bone deleted")
            case 1:
                self.report({'INFO'}, "1 bone is deleted")
            case _:
                self.report({'INFO'}, f"{count} bones are deleted")
        return {'FINISHED'}

class RefineBoneStructure(bpy.types.Operator):
    '''Refine the bone structure of the umamusume skeleton'''
    bl_idname = "uma.refine_bone_structure"
    bl_label = "Refine Structure"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object and context.active_object.type == 'ARMATURE' and len(context.selected_objects) == 1

    def execute(self, context: bpy.types.Context):

        armature_obj = context.active_object
        original_mode = armature_obj.mode

        # 检测是否存在眼部骨骼
        if 'Eye_L' not in armature_obj.data.bones or 'Eye_R' not in armature_obj.data.bones:
            self.report({'ERROR'}, "Eye bones not found")
            return {'CANCELLED'}

        edit_bones = armature_obj.data.edit_bones
        if self.fix_eye_shapekeys(context, armature_obj):
            # 调整骨骼变换
            bpy.ops.object.mode_set(mode='EDIT')
            for name in ['Eye_L', 'Eye_R']:
                eb = edit_bones.get(name)
                if eb:
                    eb.matrix @= mathutils.Matrix.Rotation(math.radians(90), 4, 'X')
                    eb.length *= 0.4

            for name in ["Toe_offset_L", "Toe_offset_R"]:
                eb = edit_bones.get(name)
                if eb:
                    eb.matrix @= mathutils.Matrix.Rotation(math.radians(90), 4, 'X')

            for name in ['Ear_03_L', 'Ear_03_R', 'Index_03_L', 'Middle_03_L', 'Pinky_03_L', 'Ring_03_L', 'Thumb_03_L', 'Index_03_R', 'Middle_03_R', 'Pinky_03_R', 'Ring_03_R', 'Thumb_03_R', 'Sp_Hi_Tail0_B_04']:
                eb = edit_bones.get(name)
                if eb and eb.parent:
                    eb.tail = eb.head + eb.parent.tail - eb.parent.head

        # 连接骨骼
        connect_bones = ['Head', 'Neck', 'Chest', 'Spine', 'Arm_L', 'Elbow_L', 'Arm_R', 'Elbow_R', 'Knee_L', 'Knee_R', 'Index_02_L', 'Index_03_L', 'Middle_02_L', 'Middle_03_L', 'Pinky_02_L', 'Pinky_03_L', 'Ring_02_L', 'Ring_03_L', 'Thumb_02_L', 'Thumb_03_L', 'Index_02_R', 'Index_03_R', 'Middle_02_R', 'Middle_03_R', 'Pinky_02_R', 'Pinky_03_R', 'Ring_02_R', 'Ring_03_R', 'Thumb_02_R', 'Thumb_03_R']
        for b in connect_bones:
            if b in edit_bones:
                edit_bones[b].use_connect = True

        # 隐藏骨骼
        bpy.ops.object.mode_set(mode='POSE')
        hidden_bones = ['Ankle_L', 'Toe_L', 'Ankle_R', 'Toe_R', 'Hand_Attach_L', 'Hand_Attach_R', 'UpBody_Ctrl']
        for b in hidden_bones:
            pbone = armature_obj.pose.bones.get(b)
            if pbone:
                pbone.bone.hide = True

        if armature_obj.mode != original_mode:
            bpy.ops.object.mode_set(mode=original_mode)

        self.report({'INFO'}, "Refine the bone successfully")
        return {'FINISHED'}

    def fix_eye_shapekeys(self, context, armature_obj):

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')

        mesh_counter = 0
        for obj in context.scene.objects:
            if obj.type == 'MESH' and any(m.type == 'ARMATURE' and m.object == armature_obj for m in obj.modifiers):
                mesh_obj = obj
                mesh_counter += 1
            if mesh_counter == 2:
                print("Fix eye shapekeys failed. Multiple meshes use this armature")
                return False
        if mesh_counter == 0:
            print("Fix eye shapekeys failed. No mesh found using this armature")
            return False
        
        vgroup_names = ['Eye_L', 'Eye_R']
        for v in vgroup_names:
            if v not in mesh_obj.vertex_groups:
                return False

        # 激活网格
        context.view_layer.objects.active = mesh_obj
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        # 选中顶点组
        for name in vgroup_names:
            bpy.ops.object.vertex_group_set_active(group=name)
            bpy.ops.object.vertex_group_select()

        # 分离选中项
        bpy.ops.mesh.separate(type='SELECTED')
        # 将分离出来的网格对象设为活动
        bpy.ops.object.mode_set(mode='OBJECT')
        eye_mesh_obj = context.selected_objects[0]
        context.view_layer.objects.active = eye_mesh_obj
        
        # 吸附到对称结构
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all()
        bpy.ops.mesh.symmetry_snap()
        bpy.ops.mesh.select_all(action='DESELECT')

        # 形态键
        bpy.ops.object.mode_set(mode='OBJECT')
        kb_data = eye_mesh_obj.data.shape_keys.key_blocks

        # 设置所有形态键的值为 0
        for key_block in kb_data:
            key_block.value = 0.0

        key_names = [
            ("Eye_20_R(XRange)[M_Face]", "Eye_R(R)", "Eye_L(L)"),
            ("Eye_20_L(XRange)[M_Face]", "Eye_L(R)", "Eye_R(L)"),
            ("Eye_21_R(YRange)[M_Face]", "Eye_R(D)", "Eye_L(D)"),
            ("Eye_21_L(YRange)[M_Face]", "Eye_L(U)", "Eye_R(U)"),
        ]

        for ori, sor, mir in key_names:
            # 检查形态键是否存在
            if ori not in kb_data:
                continue
            # 设定源形态键为 1
            kb_data[ori].value = 1
            # 选中源形态键
            eye_mesh_obj.active_shape_key_index = kb_data.keys().index(ori)
            # 复制形态键
            bpy.ops.object.shape_key_add(from_mix=True)
            # 获取新生成的形态键
            new_key = kb_data[-1]
            # 镜像形态键
            kb_data[ori].value = 0
            new_key.value = 1
            bpy.ops.object.shape_key_mirror()
            new_key.value = 0
            # 重命名
            kb_data[ori].name = sor
            new_key.name = mir

        mesh_obj.select_set(True)
        context.view_layer.objects.active = mesh_obj
        bpy.ops.object.join()

        # 删除形态键
        kb_data = mesh_obj.data.shape_keys.key_blocks
        for name, _, _ in key_names:
            if kb_data.get(name):
                mesh_obj.shape_key_remove(kb_data.get(name))
        if kb_data.get('Basis.001'):
                mesh_obj.shape_key_remove(kb_data.get('Basis.001'))

        # 驱动器
        drivers = [
            ("Eye_L(L)", "Eye_L", 'ROT_Z', -1), 
            ("Eye_L(R)", "Eye_L", 'ROT_Z',  1), 
            ("Eye_L(U)", "Eye_L", 'ROT_X', -1), 
            ("Eye_L(D)", "Eye_L", 'ROT_X',  1), 
            ("Eye_R(L)", "Eye_R", 'ROT_Z', -1), 
            ("Eye_R(R)", "Eye_R", 'ROT_Z',  1), 
            ("Eye_R(U)", "Eye_R", 'ROT_X', -1), 
            ("Eye_R(D)", "Eye_R", 'ROT_X',  1), 
        ]

        for sk_name, bone_name, axis, direction in drivers:
            # 检查形态键是否存在
            if sk_name not in kb_data:
                print(f"Skipping driver for missing key: {sk_name}")
                continue
            
            shape_key = kb_data[sk_name]
            # 移除驱动器
            shape_key.driver_remove("value")
            # 添加驱动器
            drv = shape_key.driver_add("value").driver
            drv.type = 'SCRIPTED'
            # 创建骨骼旋转的变量 
            var = drv.variables.new()
            var.type = 'TRANSFORMS'
            target = var.targets[0]
            target.id = armature_obj
            target.bone_target = bone_name
            target.transform_type = axis
            target.transform_space = 'LOCAL_SPACE'
            # 驱动器表达式
            drv.expression = f"{var.name} * {direction}  * 1.5"

        # 顶点组
        for eye_bone in vgroup_names:
            if eye_bone in mesh_obj.vertex_groups and "Head" in mesh_obj.vertex_groups:
                # 使用修改器合并权重
                mod = mesh_obj.modifiers.new(name="TMP", type='VERTEX_WEIGHT_MIX')
                mod.vertex_group_a = "Head"
                mod.vertex_group_b = eye_bone
                mod.mix_mode = 'ADD'
                mod.mix_set = 'ALL'
                # 将修改器移动到顶部
                with context.temp_override(object=mesh_obj, active_object=mesh_obj):
                    bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=0)
                # 应用修改器
                with context.temp_override(object=mesh_obj, active_object=mesh_obj):
                    bpy.ops.object.modifier_apply(modifier=mod.name)
                # 删除顶点组
                mesh_obj.vertex_groups.remove(mesh_obj.vertex_groups[eye_bone])

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        context.view_layer.objects.active = armature_obj
        return True
   
class FixBlush(bpy.types.Operator):
    '''Fix blush of mini umamusume model'''
    bl_idname = "miniuma.fixblush"
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

class FixNormal(bpy.types.Operator):
    '''Fix normals of mini umamusume model'''
    bl_idname = "miniuma.fixnormal"
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

        print(bpy.app.version_string)

        if len(context.selected_objects) == 2:
            bpy.data.objects.remove(context.selected_objects[-1], do_unlink=True)
            vertices_to_select = [67, 68, 77, 78, 79, 80, 81, 82, 84, 94, 102, 103, 105, 107, 121, 122, 123, 124, 125, 127, 128, 131, 133, 134, 159, 164, 166, 167, 209, 212, 213, 216, 217, 222, 224, 231, 256, 257, 261, 262, 263, 267, 269, 374, 375, 377, 378, 379, 380, 382]
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
        context.view_layer.objects.active = context.selected_objects[-1]

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

class ChangeHeadPretreat(bpy.types.Operator):
    '''Make the umamusume model more suitable for the production of change-head secondary creation'''
    bl_idname = "uma.changehead_pretreat"
    bl_label = "Pretreat"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object and context.active_object.type == 'ARMATURE' and len(context.selected_objects) == 1

    def execute(self, context: bpy.types.Context):

        orig_arm = context.active_object
        current_mode = orig_arm.mode
        arm_name = orig_arm.name
        orig_empty = orig_arm.parent
        empty_name = orig_empty.name
        mesh_name = orig_arm.children[0].name

        if not orig_arm.data.bones.get("Neck"):
            self.report({'ERROR'}, "Neck bone not found")
            return {'CANCELLED'}
        
        # 选中Head骨并切断
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.armature.collection_show_all()
        head_bone = orig_arm.pose.bones.get("Head")
        if head_bone:
            head_bone.bone.select = True
            bpy.ops.mmd_tools.model_separate_by_bones(separate_armature=True, include_descendant_bones=True, boundary_joint_owner='DESTINATION')
        else:
            self.report({'ERROR'}, "Head bone not found")
            return {'CANCELLED'}

        # 删除原物体并重命名
        new_empty = context.active_object
        bpy.data.objects.remove(orig_arm.children[0], do_unlink=True)
        bpy.data.objects.remove(orig_arm, do_unlink=True)
        bpy.data.objects.remove(orig_empty, do_unlink=True)
        new_empty.name = empty_name
        new_empty.children[0].name = arm_name
        new_empty.children[0].data.name = arm_name
        new_empty.children[0].children[0].name = mesh_name
        new_empty.children[0].children[0].data.name = mesh_name

        context.view_layer.objects.active = new_empty.children[0]
        bpy.ops.uma.set_bone_collections()
        attrs = ['del_handle', 'del_face', 'del_others']
        orig = [getattr(context.scene, attr) for attr in attrs]
        try:
            for attr in attrs:
                setattr(context.scene, attr, True)
            bpy.ops.uma.simplify_armature()
        finally:
            for attr, val in zip(attrs, orig):
                setattr(context.scene, attr, val)
        bpy.ops.uma.generate_ik()
        bpy.ops.object.mode_set(mode=current_mode)
        return {'FINISHED'}

class ChangeHeadHoldout(bpy.types.Operator):
    '''Blocking render'''
    bl_idname = "uma.changehead_holdout"
    bl_label = "Holdout"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object and context.active_object.type == 'ARMATURE' and len(context.selected_objects) == 1

    def execute(self, context: bpy.types.Context):

        armature = context.active_object
        head_bone = armature.pose.bones.get('Head')

        if not head_bone: 
            self.report({'ERROR'}, "Head bone not found")
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
        return context.active_object and context.active_object.type == 'MESH' and len(context.selected_objects) == 1 and context.active_object.mode == 'OBJECT' and context.active_object.data.shape_keys

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