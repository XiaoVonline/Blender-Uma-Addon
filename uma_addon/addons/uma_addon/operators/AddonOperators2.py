import bpy
import bmesh
from math import radians

from ..config import __addon_name__
# from ..preference.AddonPreferences import AddonPreferences

class SelectUnassignedMeshes(bpy.types.Operator):
    """选择所有没有材质分配的网格对象"""
    bl_idname = "uma.select_unassigned_meshes"
    bl_label = "选择所有无材质模型"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # 遍历所有网格对象
        for obj in bpy.data.objects:
            if obj.type == 'MESH':
                # 检查是否有材质槽，或材质槽是否为空
                if len(obj.data.materials) == 0 or not any(obj.data.materials):
                    obj.select_set(True)
        return {'FINISHED'}
    
class MarkCollectionCenter(bpy.types.Operator):
    """以当前物体为中心点将所在集合标记为资产"""
    bl_idname = "uma.mark_collection_center"
    bl_label = "以此为中心标记集合资产"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        # 仅当有活动物体时才可用
        return context.active_object is not None

    def execute(self, context):
        obj = context.active_object
        
        # 1. 确定目标集合
        target_collection = None
        
        # 如果物体在多个集合里，优先尝试获取上下文集合，如果不在其中，则取第一个
        if context.collection and obj.name in context.collection.objects:
            target_collection = context.collection
        else:
            if len(obj.users_collection) > 0:
                target_collection = obj.users_collection[0]
        
        if not target_collection:
            self.report({'ERROR'}, "无法找到该物体所在的集合！")
            return {'CANCELLED'}
        
        # 2. 检查是否是场景主集合
        if target_collection == context.scene.collection:
            self.report({'ERROR'}, "无法标记场景主集合，请先将物体放入一个新的子集合中。")
            return {'CANCELLED'}

        # 3. 设置实例偏移
        current_location = obj.matrix_world.translation
        
        # 设置集合的实例偏移量
        target_collection.instance_offset = current_location
        
        # 4. 标记为资产
        target_collection.asset_mark()
        
        self.report({'INFO'}, f"集合 '{target_collection.name}' 已标记，中心点设为: {obj.name}")
        return {'FINISHED'}
    
class PrintSelectedVertices(bpy.types.Operator):
    '''Print selected vertex indexes to the console'''
    bl_idname = "uma.print_selected_vertices"
    bl_label = "Print Vertex Indexes"
    bl_options = {'REGISTER'}

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

        print("Selected vertex indices:", selected_indices)
        self.report({'INFO'}, f"Printed {len(selected_indices)} vertex indexes to console")
        return {'FINISHED'}
    
class PrintSelectedBones(bpy.types.Operator):
    '''Print selected bones to the console'''
    bl_idname = "uma.print_selected_bones"
    bl_label = "Print Selected Bones"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and obj.mode == 'POSE'

    def execute(self, context):
        selected_bones = [bone.name for bone in context.selected_pose_bones] if context.selected_pose_bones else []

        if not selected_bones:
            self.report({'WARNING'}, "No bones selected")
            return {'CANCELLED'}

        print("Selected bone names:", selected_bones)
        self.report({'INFO'}, f"Printed {len(selected_bones)} bone names to console")
        return {'FINISHED'}
    
class PrintAllBones(bpy.types.Operator):
    '''Print all bones to the console'''
    bl_idname = "uma.print_all_bones"
    bl_label = "Print All bones"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'ARMATURE' and obj.mode == 'POSE'

    def execute(self, context):

        obj = context.active_object
        bones = [bone.name for bone in obj.pose.bones]

        if not bones:
            self.report({'WARNING'}, "No bones existed")
            return {'CANCELLED'}

        print("All bone names:", bones)
        self.report({'INFO'}, f"Printed {len(bones)} bones names to console")
        return {'FINISHED'}

class MeshToPython(bpy.types.Operator):
    bl_idname = "uma.mesh_to_python"
    bl_label = "Mesh To Python"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj and obj.type == 'MESH' and obj.mode == 'OBJECT'

    def execute(self, context):

        obj = bpy.context.active_object
        mesh = obj.data

        vertices = [tuple(obj.matrix_world @ v.co) for v in mesh.vertices]

        edges = [list(edge.vertices) for edge in mesh.edges]

        faces = [list(polygon.vertices) for polygon in mesh.polygons]

        code = f'''
    import bpy

    vertices = {repr(vertices)}

    edges = {repr(edges)}

    faces = {repr(faces)}

    mesh = bpy.data.meshes.new("ExportedMesh")
    mesh.from_pydata(vertices, edges, faces)
    mesh.update()
    obj = bpy.data.objects.new("ExportedObject", mesh)
    bpy.context.collection.objects.link(obj)
    '''
        text_name = f"{obj.name}_export.py"
        if text_name in bpy.data.texts:
            text = bpy.data.texts[text_name]
            text.clear()
        else:
            text = bpy.data.texts.new(text_name)
        text.write(code)
        return {'FINISHED'}

class CombineShapekeys(bpy.types.Operator):
    bl_idname = "uma.combine_shapekeys"
    bl_label = "Combine Shapekeys"
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

class SyncShapekeys(bpy.types.Operator):
    bl_idname = "uma.sync_shapekeys"
    bl_label = "Sync Shapekeys"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object and context.active_object.type == 'MESH' and len(context.selected_objects) >= 2 
    
    def execute(self, context: bpy.types.Context):

        source_obj = context.active_object
        target_objs = [obj for obj in context.selected_objects if obj != source_obj and obj.type == 'MESH' and obj.data.shape_keys]

        for target_obj in target_objs:
            source_keys = [kb.name for kb in source_obj.data.shape_keys.key_blocks if kb.name != "Basis"]
            target_keys = [kb.name for kb in target_obj.data.shape_keys.key_blocks if kb.name != "Basis"]
            # 找出同名的形态键
            common_keys = set(source_keys).intersection(target_keys)
            # 为每个同名的形态键添加驱动器
            for key_name in common_keys:
                target_kb = target_obj.data.shape_keys.key_blocks[key_name]
                target_kb.driver_remove("value")
                driver = target_kb.driver_add("value").driver
                # 设置驱动变量
                var = driver.variables.new()
                var.name = "var"
                var.type = 'SINGLE_PROP'
                target = var.targets[0]
                target.id_type = 'KEY'
                target.id = source_obj.data.shape_keys
                target.data_path = f'key_blocks["{key_name}"].value'
                driver.expression = var.name
        return {'FINISHED'}

TWIST_CONFIG = {
    'ShoulderRoll': {'up':'Shoulder', 'up_influ':0, 'down':'Arm', 'down_influ':-0.3},
    'ArmRoll': {'up':'Elbow', 'up_influ':0, 'down':'Wrist', 'down_influ':0.5},
}

class BuildTwistConstraints(bpy.types.Operator):
    bl_idname = "uma.build_twist_constraints"
    bl_label = "Build Twist Constraints"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object and context.active_object.type == 'ARMATURE' and len(context.selected_objects) == 1

    def execute(self, context):
        arm = context.active_object
        for suffix in ['_L', '_R']:
            for bone_name, target_name in TWIST_CONFIG.items():
                if bone_name + suffix in arm.pose.bones:
                    pbone = arm.pose.bones[bone_name + suffix]
                    
                    c = pbone.constraints.new(type='TRANSFORM')
                    c.name += __addon_name__
                    c.target = arm
                    c.subtarget = target_name['up'] + suffix
                    c.map_from = 'ROTATION'
                    c.map_to = 'ROTATION'
                    c.target_space = 'LOCAL'
                    c.owner_space = 'LOCAL'
                    c.from_rotation_mode = 'QUATERNION'
                    c.from_min_y_rot = radians(-180)
                    c.from_max_y_rot = radians(180)
                    c.map_to_x_from = 'Y'
                    c.to_min_x_rot = radians(-180) * target_name['up_influ']
                    c.to_max_x_rot = radians(180) * target_name['up_influ']

                    c = pbone.constraints.new(type='TRANSFORM')
                    c.name += __addon_name__
                    c.target = arm
                    c.subtarget = target_name['down'] + suffix
                    c.map_from = 'ROTATION'
                    c.map_to = 'ROTATION'
                    c.target_space = 'LOCAL'
                    c.owner_space = 'LOCAL'
                    c.from_rotation_mode = 'QUATERNION'
                    c.from_min_y_rot = radians(-180)
                    c.from_max_y_rot = radians(180)
                    c.map_to_x_from = 'Y'
                    c.to_min_x_rot = radians(-180) * target_name['down_influ']
                    c.to_max_x_rot = radians(180) * target_name['down_influ']

                    c = pbone.constraints.new(type='LIMIT_ROTATION')
                    c.name += __addon_name__
                    c.owner_space = 'LOCAL'
                    c.use_limit_x, c.use_limit_y, c.use_limit_z = False, True, True

        arm.uma_controller.auto_twist_bones = True
        self.report({'INFO'}, "Twist bone constraints built")
        return {'FINISHED'}

class ClearTwistConstraints(bpy.types.Operator):
    bl_idname = "uma.clear_twist_constraints"
    bl_label = "Clear Twist Constraints"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object and context.active_object.type == 'ARMATURE' and len(context.selected_objects) == 1

    def execute(self, context):
        arm = context.active_object
        for suffix in ['_L', '_R']:
            for bone_name in TWIST_CONFIG.keys():
                if bone_name + suffix in arm.pose.bones:
                    pbone = arm.pose.bones[bone_name + suffix ]
                    for c in reversed(pbone.constraints):
                        if __addon_name__ in c.name:
                            pbone.constraints.remove(c)
                            
        arm.uma_controller.auto_twist_bones = False
        self.report({'INFO'}, "Twist bone constraints cleared")
        return {'FINISHED'}
