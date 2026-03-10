import bpy
import os
import math
import tarfile
from array import array
from ..utils.Utils import BinaryReader
from ..config import __addon_name__

class EarConvert(bpy.types.Operator):
    bl_idname = "uma.ear_convert"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object and context.active_object.type == 'MESH' and context.scene.uma_scene.ear_target

    def parse_raw_data(self, data_source):
        parsed_results =[]
        br = None
        try:
            br = BinaryReader(data_source)
            
            br.read_int32()    # m_GameObject.m_FileID
            br.read_sint64()   # m_GameObject.m_PathID
            br.read_uint8()    # m_Enabled
            br.align(4)
            br.read_int32()    # m_Script.m_FileID
            br.read_sint64()   # m_Script.m_PathID
            m_name = br.read_string() # m_Name
            
            size_1 = br.read_int32() # _targetFaces
            for i in range(size_1):
                bone_data = {}
                
                # TargetGroupInfomation _faceGroupInfo
                size_2 = br.read_int32()
                for j in range(size_2):
                    
                    # TRS _trsArray 
                    size_3 = br.read_int32()
                    for k in range(size_3):
                        path = br.read_string().split('/')[-1]
                        
                        is_valid_scale = br.read_uint8()
                        br.align(4)
                        
                        # Vector3f _position
                        px = br.read_float()
                        py = br.read_float()
                        pz = br.read_float()
                        
                        # Vector3f _scale
                        sx = br.read_float()
                        sy = br.read_float()
                        sz = br.read_float()
                        
                        # Vector3f _rotation
                        rx = br.read_float()
                        ry = br.read_float()
                        rz = br.read_float()
                        
                        is_override = br.read_uint8()
                        br.align(4)
                        
                        bone_data[path] = (rx, ry, rz)
                        
                parsed_results.append(bone_data)

        except Exception as e:
            msg = data_source if isinstance(data_source, str) else "Memory Stream"
            raise Exception(f"{msg} parse error: {str(e)}")
        finally:
            if br: br.close()
        return parsed_results
    
    def execute(self, context):

        ear_target = context.scene.uma_scene.ear_target.replace("chr","")

        archive_path = os.path.join(os.path.dirname(__file__), "MonoBehaviour.tar.xz")

        ear_target_data = None
        if os.path.exists(archive_path):
            with tarfile.open(archive_path, "r:xz") as tar:
                member = tar.getmember(f"{ear_target}")
                f = tar.extractfile(member)
                if f:
                    ear_target_data = self.parse_raw_data(f.read()) 

        if not ear_target_data:
            self.report({'ERROR'}, "Failed to parse configuration file")
            return {'CANCELLED'}
        
        mesh_obj = context.active_object
        # 获取骨架
        if mesh_obj.parent and mesh_obj.parent.type == 'ARMATURE':
            armature_obj = mesh_obj.parent
        else:
            self.report({'ERROR'}, "No associated armature found")
            return {'CANCELLED'}

        # 检查是否拥有形态键
        if not mesh_obj.data.shape_keys:
            mesh_obj.shape_key_add(name="Basis")
        kb = mesh_obj.data.shape_keys.key_blocks
        basis = kb.get("Basis")

        tags = [
            "",
            "Base_N", "Kanasi", "Dere_N", "Dere", "Yure", 
            "Biku_N", "Biku", "Ikari", "Tanosi", "Up_N", 
            "Up", "Down", "Front", "Side", "Back", "Roll"
        ]

        # 补全形态键
        for i in range(1, 17):
            tag_name = tags[i]
            for side in ['L', 'R']:
                target_sk_name = f"Ear_{i}_{side}({tag_name})[M_Hair]"
                if target_sk_name not in kb:
                    mesh_obj.shape_key_add(name=target_sk_name, from_mix=False)

        # 筛选 Ear_ 开头的键名
        shapekey_names =[k.name for k in kb if k.name.startswith("Ear_")]

        # 提取 Basis 坐标缓存
        count = len(basis.data) * 3
        coords = array('f', [0.0] * count)
        basis.data.foreach_get("co", coords)
        
        # 批量重置形态键的网格形变
        for n in shapekey_names:
            kb[n].data.foreach_set("co", coords)
            
        # 建立驱动器
        for side in ['L', 'R']:
            for bone_idx in range(1, 4):
                bone_name = f"Ear_0{bone_idx}_{side}"
                pose_bone = armature_obj.pose.bones.get(bone_name)
                if not pose_bone: 
                    continue

                # 旋转模式为 XYZ Euler
                pose_bone.rotation_mode = 'XYZ'
                bone_name = bone_name.replace('L', 'R') if bone_name.endswith('L') else bone_name.replace('R', 'L')
                for axis_idx in range(3):
                    # 移除旧的驱动器
                    try:
                        pose_bone.driver_remove("rotation_euler", axis_idx)
                    except TypeError:
                        pass
                    
                    expr_parts = []
                    driver_vars =[]
                    
                    # 遍历 1 到 16 的状态
                    for i in range(1, min(17, len(ear_target_data))):
                        if bone_name not in ear_target_data[i]:
                            continue

                        # 获取角度 (axis_idx: 0=X, 1=Y, 2=Z)
                        angle = ear_target_data[i][bone_name][axis_idx]
                        if abs(angle) < 0.0001: 
                            continue

                        # 查找对应的形态键
                        shapekey_name = next((n for n in shapekey_names if n.startswith(f"Ear_{i}_{side}")), None)
                        if not shapekey_name:
                            continue
                            
                        driver_vars.append((i, shapekey_name, angle))

                    # 添加驱动器
                    if driver_vars:
                        fcurve = pose_bone.driver_add("rotation_euler", axis_idx)
                        driver = fcurve.driver
                        driver.type = 'SCRIPTED'
                        
                        for i, shapekey_name, angle in driver_vars:
                            var_name = f"v{i}"
                            
                            var = driver.variables.new()
                            var.name = var_name
                            var.type = 'SINGLE_PROP'
                            var.targets[0].id_type = 'KEY'
                            var.targets[0].id = mesh_obj.data.shape_keys
                            var.targets[0].data_path = f'key_blocks["{shapekey_name}"].value'
                            
                            rad = math.radians(angle)
                            expr_parts.append(f"{rad:.8f}*{var.name}")
                        
                        driver.expression = "+".join(expr_parts)
        
        self.report({'INFO'}, f"Ear shape keys successfully mapped to bone drivers")
        return {'FINISHED'}