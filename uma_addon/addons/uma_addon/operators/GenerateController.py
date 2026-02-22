import bpy
import os
from math import radians, pi ,sin, cos
from mathutils import Vector
import logging
import re
import addon_utils
import numpy as np
from bpy.props import BoolProperty

from ..config import __addon_name__

from ..utils.Utils import assign_bone_to_collection

class MMRRig(bpy.types.Operator):
    '''Generate MMR controller for umamusume'''
    bl_idname = "uma.mmr_rig"
    bl_label = "For Umamusume"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object and context.active_object.type == 'ARMATURE'

    def execute(self, context: bpy.types.Context):
        # preset Towards config Twist_bones
        context.active_object.select_set(True)
        bpy.ops.uma.refine_bone_structure()

        mmr = context.object.mmr
       
        mod = next((m for m in addon_utils.modules() if m.__name__ == "MikuMikuRig"), None)
        if mod is None:
            self.report({'ERROR'},"MMR not found")
            return {'CANCELLED'}

        # 将当前文件夹路径和文件名组合成完整的文件路径
        mmr_path = os.path.dirname(mod.__file__)
        blend_file_path = os.path.join(mmr_path, "addons", "MikuMikuRig", "operators", "MMR_Rig.blend")

        # 设置追加参数
        filepath = os.path.join(blend_file_path, "Object", "MMR_Rig_relative")
        directory = os.path.join(blend_file_path, "Object")
        filename = "MMR_Rig_relative"

        # 执行追加操作
        if bpy.data.objects.get('MMR_Rig_relative') is None:
            bpy.ops.wm.append(
                filepath=filepath,
                directory=directory,
                filename=filename,
            )

        # 检测是否开启rigify
        if 'rigify' not in bpy.context.preferences.addons.keys():
            logging.info("检测到未开启rigify，已自动开启")
            bpy.ops.preferences.addon_enable(module="rigify")

        # 切换物体模式
        bpy.ops.object.mode_set(mode='OBJECT')
        # 当前活动物体名称
        mmd_arm = bpy.context.active_object
        print("当前活动骨骼名称:", mmd_arm.name)

        # 记住变换
        mmd_arm_matrix = mmd_arm.matrix_world.copy()

        # 清除旋转
        mmd_arm.rotation_euler = (0, 0, 0)

        # 激活物体
        bpy.context.view_layer.objects.active = mmd_arm
        mmd_arm.select_set(True)

        # 应用旋转变换
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)

        RIG = bpy.data.objects.get("MMR_Rig_relative")

        def check_keywords(target_string: str, keywords) -> bool:
            """
            检查目标字符串是否包含指定关键词列表中的任意一个
            :param target_string: 待检查的目标字符串
            :return: 若包含任意关键词返回True，否则返回False
            """
            for keyword in keywords:
                if keyword in target_string:
                    return True
            return False

        # 判断字符串的左(L)右(R)
        def determine_side(s):
            parts = s.split('.')
            if len(parts) < 1:
                return None
            suffix = parts[-1].strip().upper()  # 统一转大写并去除首尾空格
            if suffix == 'L':
                return True
            elif suffix == 'R':
                return False
            else:
                return None

        def get_bone_world_rotation(armature_obj, bone_name):
            # 获取骨骼对象
            bone = armature_obj.pose.bones.get(bone_name)
            if bone is None:
                print(f"骨骼 {bone_name} 未找到。")
                return None

            # 获取骨骼的矩阵
            bone_matrix = armature_obj.matrix_world @ bone.matrix

            # 获取旋转部分(四元数)
            rotation = bone_matrix.to_quaternion()

            # 将四元数转换为欧拉角(弧度)
            euler_rotation = rotation.to_euler()

            return euler_rotation

        # 对齐骨骼roll
        def align_bones_roll(A, D, B, C):
            # A骨骼(D骨架),B骨骼(C骨架)
            # 获取 D 骨架和 C 骨架对象
            D_armature_obj = bpy.data.objects.get(D)
            C_armature_obj = bpy.data.objects.get(C)

            if not D_armature_obj or not C_armature_obj:
                print("未找到 D 骨架或 C 骨架对象，请检查名称。")
                return

            if D_armature_obj.type != 'ARMATURE' or C_armature_obj.type != 'ARMATURE':
                print("D 或 C 对象不是骨架类型，请检查。")
                return

            # 进入 D 骨架的编辑模式
            bpy.context.view_layer.objects.active = D_armature_obj
            bpy.ops.object.mode_set(mode='EDIT')
            D_edit_bones = D_armature_obj.data.edit_bones

            # 进入 C 骨架的编辑模式
            bpy.context.view_layer.objects.active = C_armature_obj
            bpy.ops.object.mode_set(mode='EDIT')
            C_edit_bones = C_armature_obj.data.edit_bones

            # 获取 A 骨骼和 B 骨骼
            A_bone = D_edit_bones.get(A)
            B_bone = C_edit_bones.get(B)

            if not A_bone or not B_bone:
                print(f"未找到 {A} 骨骼或 {B} 骨骼，请检查名称。")
                bpy.ops.object.mode_set(mode='OBJECT')
                return

            B_bone.roll = A_bone.roll

        # 对齐骨骼
        def align_bones(A, D_armature_obj, B, C_armature_obj, Compare_Boolean=False, count = False, length = 0.0):
            # A骨骼(D骨架),B骨骼(C骨架)

            if not D_armature_obj or not C_armature_obj:
                print("未找到 D 骨架或 C 骨架对象，请检查名称。")
                return

            if D_armature_obj.type != 'ARMATURE' or C_armature_obj.type != 'ARMATURE':
                print("D 或 C 对象不是骨架类型，请检查。")
                return

            # 进入 D 骨架的编辑模式
            bpy.context.view_layer.objects.active = D_armature_obj
            bpy.ops.object.mode_set(mode='EDIT')
            D_edit_bones = D_armature_obj.data.edit_bones

            # 进入 C 骨架的编辑模式
            bpy.context.view_layer.objects.active = C_armature_obj
            bpy.ops.object.mode_set(mode='EDIT')
            C_edit_bones = C_armature_obj.data.edit_bones

            # 获取 A 骨骼和 B 骨骼
            A_bone = D_edit_bones.get(A)
            B_bone = C_edit_bones.get(B)

            if not A_bone or not B_bone:
                print(f"未找到 {A} 骨骼或 {B} 骨骼，请检查名称。")
                bpy.ops.object.mode_set(mode='OBJECT')
                return False
            else:
                if count:
                    return True

            # 转换 B 骨骼的头和尾坐标到世界空间
            world_matrix_C = C_armature_obj.matrix_world
            world_head_B = world_matrix_C @ B_bone.head
            world_tail_B = world_matrix_C @ B_bone.tail

            # 转换世界空间坐标到 D 骨架的局部空间
            world_matrix_D = D_armature_obj.matrix_world
            local_matrix_D = world_matrix_D.inverted()
            local_head_B = local_matrix_D @ world_head_B
            local_tail_B = local_matrix_D @ world_tail_B

            if Compare_Boolean:
                if local_head_B[2] < local_tail_B[2]:
                    return False
                else:
                    return True

            # 设置 A 骨骼的头和尾
            if A == 'spine':
                if local_head_B[2] < local_tail_B[2]:
                    A_bone.head = local_head_B
                    A_bone.tail = local_tail_B
                else:
                    A_bone.head = local_tail_B
                    A_bone.tail = local_head_B
            else:
                A_bone.head = local_head_B
                A_bone.tail = local_tail_B

            if length != 0.0:
                A_bone.length = A_bone.length * length

            # 退出编辑模式
            bpy.ops.object.mode_set(mode='OBJECT')

        def move_bone_a_to_b(d_armature_name, c_armature_name, bone_a_name, bone_b_name, A_bone_Z_location = False):

            # 获取 D 骨架和 C 骨架对象
            d_armature_obj = bpy.data.objects.get(d_armature_name)
            c_armature_obj = bpy.data.objects.get(c_armature_name)

            if d_armature_obj and c_armature_obj:
                # 确保 D 骨架和 C 骨架处于姿态模式
                for obj in [d_armature_obj, c_armature_obj]:
                    bpy.context.view_layer.objects.active = obj
                    bpy.ops.object.mode_set(mode='POSE')

                # 获取 A 骨骼和 B 骨骼
                bone_A = d_armature_obj.pose.bones.get(bone_a_name)
                bone_B = c_armature_obj.pose.bones.get(bone_b_name)

                if bone_A and bone_B:
                    # 下面的注释是Ai写的,不能全信
                    # 使用矩阵操作（如需同时处理位置和旋转）
                    # 1. 计算骨骼 B 的世界矩阵（包含位置、旋转、缩放）
                    world_matrix_b = c_armature_obj.matrix_world @ bone_B.matrix  # 补充此处定义

                    # 2. 分解骨骼 A 的原有旋转、Z位置和缩放（避免被覆盖）
                    original_rot = bone_A.rotation_quaternion.copy()
                    original_scale = bone_A.scale.copy()
                    A_bone_Z = bone_A.location.z

                    # 3. 设置骨骼 A 的局部矩阵（世界矩阵反转为局部空间）
                    bone_A.matrix = d_armature_obj.matrix_world.inverted() @ world_matrix_b

                    # 4. 恢复骨骼 A 的原有旋转和缩放（仅保留目标位置）
                    bone_A.rotation_quaternion = original_rot
                    bone_A.scale = original_scale

                    if A_bone_Z_location:
                        bone_A.location.z = A_bone_Z

                    # 更新场景以反映更改
                    bpy.context.view_layer.update()
                else:
                    print("未找到指定的骨骼。")
            else:
                print("未找到指定的骨架对象。")

        def Size_settings(A, B):
            obj_a = A
            obj_b = B

            if obj_a and obj_b:
                # 获取目标Z轴尺寸和当前Z轴尺寸
                target_z = obj_b.dimensions.z
                current_z = obj_a.dimensions.z

                # 避免除以零错误
                if current_z == 0:
                    print("Error: 物体A的Z轴尺寸为0，无法缩放")
                    return

                if target_z == current_z:
                    print('尺寸相同，无法缩放')
                    return

                # 直接计算缩放因子
                scale_factor = target_z / current_z

                # 应用缩放因子到所有轴向（保持比例）
                obj_a.scale *= scale_factor

                # 更新视图层以确保尺寸计算准确
                bpy.context.view_layer.update()

                # 应用缩放变换
                bpy.ops.object.select_all(action='DESELECT')
                obj_a.select_set(True)
                bpy.context.view_layer.objects.active = obj_a
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

        def Move_location(A,B):
            object_a = A
            object_b = B

            if object_a and object_b:
                object_a_copy = object_a.copy()  # 复制物体 A

                # 获取物体 B 的世界矩阵
                world_matrix_b = object_b.matrix_world

                # 计算物体 A 的世界矩阵
                world_matrix_a = object_a.matrix_world

                # 计算新的局部变换矩阵
                new_world_matrix = world_matrix_b @ world_matrix_a.inverted()

                # 应用新的局部变换矩阵到物体 A
                object_a.matrix_local = new_world_matrix
                object_a.scale = object_a_copy.scale  # 保留原始缩放
                # 删除object_a_copy
                bpy.data.objects.remove(object_a_copy, do_unlink=True)
                # 更新场景
                bpy.context.view_layer.update()

            else:
                print("未找到指定的物体")

        def rotate_bone_x(armature_object, bone_name, angle_deg=10, armature_apply=True):

            bpy.ops.object.mode_set(mode='POSE')

            # 获取姿态骨骼
            pose_bone = armature_object.pose.bones.get(bone_name)

            # 欧拉旋转
            pose_bone.rotation_mode = 'XYZ'

            # 转换为弧度并应用旋转
            angle_rad = radians(angle_deg)
            pose_bone.rotation_euler.x += angle_rad
            if armature_apply:
                bpy.ops.pose.armature_apply(selected=False)

        def match_bone_transforms(arm, hand_ik, hand_fk):

            # 获取对象
            armature_obj = arm

            # 确保对象是骨骼对象
            if armature_obj.type == 'ARMATURE':
                # 进入姿态模式
                bpy.ops.object.mode_set(mode='POSE')

                # 获取骨骼数据
                pose_bones = armature_obj.pose.bones

                # 获取 hand_ik 和 hand_fk 骨骼
                hand_ik_bone = pose_bones.get(hand_ik)
                hand_fk_bone = pose_bones.get(hand_fk)

                if hand_ik_bone and hand_fk_bone:

                    # 获取 hand_fk 骨骼的世界空间矩阵
                    hand_fk_matrix_world = armature_obj.matrix_world @ hand_fk_bone.matrix

                    # 计算 hand_ik 骨骼的本地空间矩阵
                    hand_ik_matrix_local = armature_obj.matrix_world.inverted() @ hand_fk_matrix_world

                    # 将 hand_ik 骨骼的本地空间矩阵设置为计算得到的矩阵
                    hand_ik_bone.matrix = hand_ik_matrix_local

        def calculate_tail_coordinates(bone_name, bone_name2, arm_obj_name, scale = True, distance = False, lengths = False):

            arm = bpy.data.objects.get(arm_obj_name)

            bpy.context.view_layer.objects.active = arm
            bpy.ops.object.mode_set(mode='EDIT')  # 切到编辑模式

            # 确保骨骼存在
            if bone_name not in arm.data.edit_bones or bone_name2 not in arm.data.edit_bones:
                print(f"骨骼 {bone_name} 或 {bone_name2} 不存在于骨架 {arm_obj_name} 中")
                return

            bone1 = arm.data.edit_bones.get(bone_name)
            bone2 = arm.data.edit_bones.get(bone_name2)

            bone1_head = bone1.head # 头坐标
            bone1_tail = bone1.tail # 尾坐标
            bone2_length = bone2.length # 长度
            bone1_length = bone1.length # 长度

            if distance:
                head1 = np.array([bone1_head.x, bone1_head.y, bone1_head.z])
                tail1 = np.array([bone1_tail.x, bone1_tail.y, bone1_tail.z])

                # 计算方向向量和缩放因子
                direction = tail1 - head1
                length = np.linalg.norm(direction)
                if lengths:
                    k = bone1_length / length  # 缩放因子
                else:
                    k = bone2_length / length  # 缩放因子


                # 生成两种方向的尾坐标
                scaled_dir1 = direction * k  # 原方向
                scaled_dir2 = -direction * k  # 反方向
                tail2_case1 = tail1 + scaled_dir1
                tail2_case2 = tail1 + scaled_dir2

                # 计算到 head1 的距离
                distance_case1 = np.linalg.norm(head1 - tail2_case1)
                distance_case2 = np.linalg.norm(head1 - tail2_case2)

                if distance_case1 > distance_case2:  # 选择距离更长的
                    bone2.tail = tail2_case1
                    print(f"Case 1 尾坐标: {np.round(tail2_case1, 4)}, 距离: {np.round(distance_case1, 4)}")
                else:
                    bone2.tail = tail2_case2
                    print(f"Case 2 尾坐标: {np.round(tail2_case2, 4)}, 距离: {np.round(distance_case2, 4)}")

            if not distance:
                bone2.tail = bone1_head
                if scale:
                    bone2.length = bone2_length

        def Calculate_intersection_angle(Arm, a_bone, b_bone):

            bpy.ops.object.mode_set(mode='EDIT')

            A_bone = Arm.data.edit_bones.get(a_bone)
            B_bone = Arm.data.edit_bones.get(b_bone)

            # 定义点坐标
            A = np.array([A_bone.head.x, A_bone.head.y, A_bone.head.z])  # 起点
            B = np.array([B_bone.head.x, B_bone.head.y, B_bone.head.z])  # 交点
            C = np.array([B_bone.tail.x, B_bone.tail.y, B_bone.tail.z])  # 终点

            # 计算从交点B出发的向量
            BA = A - B  # 向量BA
            BC = C - B  # 向量BC

            # 计算点积
            dot_product = np.dot(BA, BC)

            # 计算向量模长
            norm_BA = np.linalg.norm(BA)
            norm_BC = np.linalg.norm(BC)

            # 计算夹角余弦值
            cos_theta = dot_product / (norm_BA * norm_BC)

            # 计算夹角（弧度）
            theta_rad = np.arccos(np.clip(cos_theta, -1.0, 1.0))

            # 转换为角度
            theta_deg = np.degrees(theta_rad)

            # 输出结果
            print('骨骼: ', a_bone, b_bone)
            print(f"向量 BA: {BA}")
            print(f"向量 BC: {BC}")
            print(f"点积: {dot_product}")
            print(f"向量 BA 模长: {norm_BA:.6f}")
            print(f"向量 BC 模长: {norm_BC:.6f}")
            print(f"余弦值: {cos_theta:.6f}")
            print(f"角度(弧度): {theta_rad:.6f}")
            print(f"角度(度数): {theta_deg:.6f}")
            print('------------------')

            return theta_deg

        # 获取某个骨骼的世界空间z轴坐标
        def get_bone_world_z(bone_name, armature_obj):
            # 切换到姿势模式
            bpy.context.view_layer.objects.active = armature_obj
            bpy.ops.object.mode_set(mode='POSE')

            # 获取骨骼
            pose_bone = armature_obj.pose.bones.get(bone_name)
            if not pose_bone:
                print(f"骨骼 {bone_name} 不存在")
                return

            # 获取骨骼z轴坐标
            z_coordinate = pose_bone.matrix.translation.z
            return z_coordinate

        # 设置骨骼的世界空间z轴坐标(在姿势模式)
        def set_bone_world_z(bone_name, armature_obj, z_value):
            # 切换到姿势模式
            bpy.context.view_layer.objects.active = armature_obj
            bpy.ops.object.mode_set(mode='POSE')

            # 获取骨骼
            pose_bone = armature_obj.pose.bones.get(bone_name)
            if not pose_bone:
                print(f"骨骼 {bone_name} 不存在")
                return

            # 设置骨骼z轴坐标
            pose_bone.matrix.translation.z = z_value

            # 应用变换
            bpy.ops.pose.armature_apply(selected=False)

        # 版本比较
        def compare_version(version1, version2):
            parts1 = []
            parts2 = []
            for part in re.split('[.-]', version1):
                try:
                    num = int(part)
                except ValueError:
                    num = 0
                parts1.append(num)
            for part in re.split('[.-]', version2):
                try:
                    num = int(part)
                except ValueError:
                    num = 0
                parts2.append(num)
            min_length = min(len(parts1), len(parts2))
            for i in range(min_length):
                if parts1[i] < parts2[i]:
                    return True
                elif parts1[i] > parts2[i]:
                    return False
            return len(parts1) < len(parts2)

        finger_bone = []

        arm_number = 0

        if not RIG.mmr.Generate_controllers:

            # 变换
            Move_location(mmd_arm,RIG)
            # 缩放
            Size_settings(RIG,mmd_arm)

            config = {
                "Arm_L": "upper_arm.L",
                "Arm_R": "upper_arm.R",
                "Elbow_L": "forearm.L",
                "Elbow_R": "forearm.R",
                "Shoulder_L": "shoulder.L",
                "Shoulder_R": "shoulder.R",
                "Thigh_L": "thigh.L",
                "Thigh_R": "thigh.R",
                "Knee_L": "shin.L",
                "Knee_R": "shin.R",
                "Ankle_offset_L": "foot.L",
                "Ankle_offset_R": "foot.R",
                "Toe_L": "toe.L",
                "Toe_R": "toe.R",
                "Wrist_L": "hand.L",
                "Wrist_R": "hand.R",
                "Hip": "spine",
                "Waist": "spine.001",
                "Spine": "spine.002",
                "Chest": "spine.003",
                "Neck": "spine.004",
                "Head": "spine.006",
                "Eye_L": "eye.L",
                "Eye_R": "eye.R",
                "Thumb_01_R": "thumb.01.R",
                "Thumb_02_R": "thumb.02.R",
                "Thumb_03_R": "thumb.03.R",
                "Index_01_R": "f_index.01.R",
                "Index_02_R": "f_index.02.R",
                "Index_03_R": "f_index.03.R",
                "Middle_01_R": "f_middle.01.R",
                "Middle_02_R": "f_middle.02.R",
                "Middle_03_R": "f_middle.03.R",
                "Ring_01_R": "f_ring.01.R",
                "Ring_02_R": "f_ring.02.R",
                "Ring_03_R": "f_ring.03.R",
                "Pinky_01_R": "f_pinky.01.R",
                "Pinky_02_R": "f_pinky.02.R",
                "Pinky_03_R": "f_pinky.03.R",
                "Thumb_01_L": "thumb.01.L",
                "Thumb_02_L": "thumb.02.L",
                "Thumb_03_L": "thumb.03.L",
                "Index_01_L": "f_index.01.L",
                "Index_02_L": "f_index.02.L",
                "Index_03_L": "f_index.03.L",
                "Middle_01_L": "f_middle.01.L",
                "Middle_02_L": "f_middle.02.L",
                "Middle_03_L": "f_middle.03.L",
                "Ring_01_L": "f_ring.01.L",
                "Ring_02_L": "f_ring.02.L",
                "Ring_03_L": "f_ring.03.L",
                "Pinky_01_L": "f_pinky.01.L",
                "Pinky_02_L": "f_pinky.02.L",
                "Pinky_03_L": "f_pinky.03.L"
            }

            # 遍历字典的键值对并打印
            for key, value in config.items():
                print(f"键名: {key}, 值: {value}")

                if check_keywords(value, ["thumb", "index", "middle", "ring", "pinky"]):
                    finger_bone.append(value)

                # 调用函数
                align_bones(value, RIG, key, mmd_arm)

                if value == "spine.006":
                    # 移动到正确位置
                    move_bone_a_to_b(RIG.name, mmd_arm.name, "face", key)
                    # 遍历字典的键值
                    for key, value in config.items():
                        # 眼睛
                        if value == "eye.L" or value == "eye.R":
                            move_bone_a_to_b(RIG.name, mmd_arm.name, value, key)

                if align_bones(value, RIG, key, mmd_arm, count=True):
                    arm_number += 1
                    # 激活物体      
                    bpy.context.view_layer.objects.active = RIG
                    # 选择物体
                    RIG.select_set(True)
                    # 应用
                    bpy.ops.object.mode_set(mode='POSE')
                    bpy.ops.pose.armature_apply(selected=False)

            # 手掌修正
            if not mmd_arm.mmr.Disable_hand_fix:
                for key, value in config.items():
                    if 'hand' in value:
                        if determine_side(value):
                            calculate_tail_coordinates('forearm.L', 'hand.L', RIG.name,distance=True)
                        else:
                            calculate_tail_coordinates('forearm.R', 'hand.R', RIG.name,distance=True)

                if value == 'spine.003':
                    calculate_tail_coordinates('spine.004', 'spine.003', RIG.name, scale=False)

                if 'foot' in value:
                    if determine_side(value):
                        move_bone_a_to_b(RIG.name, RIG.name, "heel.02.L", value, A_bone_Z_location=True)
                    else:
                        move_bone_a_to_b(RIG.name, RIG.name, "heel.02.R", value, A_bone_Z_location=True)

            palm_aligs = {
                'palm.01.L': 'f_index.01.L',
                'palm.01.R': 'f_index.01.R',
                'palm.02.L': 'f_middle.01.L',
                'palm.02.R': 'f_middle.01.R',
                'palm.03.L': 'f_ring.01.L',
                'palm.03.R': 'f_ring.01.R',
                'palm.04.L': 'f_pinky.01.L',
                'palm.04.R': 'f_pinky.01.R',
            }

            for key, value in palm_aligs.items():
                align_bones(key, RIG, value, RIG, length=2)
                finger_bone.append(key)

                bpy.ops.object.mode_set(mode='POSE')  # 切到pose模式
                bpy.ops.pose.armature_apply(selected=False)  # 应用

            finger_bone_L = []
            finger_bone_R = []

            for v in finger_bone:
                if determine_side(v):
                    finger_bone_L.append(v)
                else:
                    finger_bone_R.append(v)

            bpy.context.view_layer.objects.active = RIG
            bpy.ops.object.mode_set(mode='EDIT')  # 切到编辑模式

            if mmr.f_pin:
                for key, value in config.items():
                    if '03' in value:
                        f_pin = ['thumb', 'index', 'middle', 'ring', 'pinky']
                        for f in f_pin:
                            if f in value:
                                v_bone = RIG.data.edit_bones.get(value)
                                if format(v_bone.head.x, '.4f') == format(v_bone.tail.x, '.4f'):
                                    if format(v_bone.head.y, '.4f') == format(v_bone.tail.y, '.4f'):
                                        pinky_parent = v_bone.parent.name
                                        calculate_tail_coordinates(pinky_parent, value, RIG.name, distance=True,lengths=True)

            for bone in RIG.data.edit_bones:  # 遍历所有骨骼
                bone.select = bone.name in finger_bone_R  # True=选中，False=不选
            bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')  # 原本想设x的,看到0.56 MMR这样用的,就这样吧
            bpy.ops.armature.select_all(action='DESELECT')  # 取消所有选择

            for bone in RIG.data.edit_bones:
                bone.select = bone.name in finger_bone_L
            bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')
            bpy.ops.armature.select_all(action='DESELECT')

            roll_thumb = 'GLOBAL_NEG_Y'

            if mmr.Thumb_twist_aligns_with_the_world_Z_axis:
                roll_thumb = 'GLOBAL_POS_Z'

            for bone in RIG.data.edit_bones:
                if bone.name in finger_bone_R:
                    if 'thumb' in bone.name:
                        bone.select = True
                        bpy.ops.armature.calculate_roll(type=roll_thumb)
                        bpy.ops.armature.select_all(action='DESELECT')
                else:
                    if bone.name in finger_bone_L:
                        if 'thumb' in bone.name:
                            bone.select = True
                            bpy.ops.armature.calculate_roll(type=roll_thumb)
                            bpy.ops.armature.select_all(action='DESELECT')

            bjiy_1 = ['thigh.L', 'shin.L',
                      'thigh.R', 'shin.R']

            bjiy_2 = ['spine', 'spine.001',
                      'spine.002', 'spine.003',
                      'spine.004', 'spine.006',
                      'upper_arm.L', 'forearm.L',
                      'hand.L', 'upper_arm.R',
                      'forearm.R', 'hand.R']

            bjiy_3 = ['thigh.L', 'shin.L', 'foot.L', 'toe.L', 'thigh.R', 'shin.R', 'foot.R', 'toe.R']

            bjiy_4 = {'foot.L': 'toe.L', 'foot.R': 'toe.R'}

            bjiy_5 = ['shoulder.L', 'shoulder.R']

            for bone in RIG.data.edit_bones:
                bone.select = bone.name in bjiy_2
            bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Y')
            bpy.ops.armature.select_all(action='DESELECT')

            for bone in RIG.data.edit_bones:
                bone.select = bone.name in bjiy_2
            bpy.ops.armature.calculate_roll(type='GLOBAL_NEG_Y')
            bpy.ops.armature.select_all(action='DESELECT')

            for bone in RIG.data.edit_bones:
                bone.select = bone.name in bjiy_3
            bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Y')
            bpy.ops.armature.select_all(action='DESELECT')

            for k, v in bjiy_4.items():
                for bone in RIG.data.edit_bones:
                    if bone.name == k:
                        bone.select = True
                        bpy.ops.armature.calculate_roll(type='GLOBAL_NEG_Z')
                        bpy.ops.armature.select_all(action='DESELECT')
                    if bone.name == v:
                        bone.select = True
                        bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')
                        bpy.ops.armature.select_all(action='DESELECT')

            for bone in RIG.data.edit_bones:
                bone.select = bone.name in bjiy_5
            bpy.ops.armature.calculate_roll(type='GLOBAL_POS_Z')
            bpy.ops.armature.select_all(action='DESELECT')
        else:
            mmd_arm = context.object.mmr.mmd_Armature

        if mmr.Only_meta_bones_are_generated:
            mmr.Only_meta_bones_are_generated = False
            RIG.mmr.presets = mmd_arm.mmr.presets
            RIG.mmr.Import_presets = mmd_arm.mmr.Import_presets
            RIG.mmr.json_filepath = mmd_arm.mmr.json_filepath
            RIG.mmr.Generate_controllers = True
            RIG.mmr.mmd_Armature = mmd_arm
            mmd_arm.matrix_world = mmd_arm_matrix  # 还原位置
            RIG.matrix_world = mmd_arm_matrix  # 吸附位置
            RIG.show_in_front = True # 在前面
            RIG.mmr.MMR_Arm = True
            return {'FINISHED'}

        # 更新场景
        bpy.context.view_layer.update()

        bpy.ops.object.mode_set(mode='POSE')  # 切到姿态模式

        ct_op = {}

        # 备份所有骨骼的Set_constraints
        for bone in RIG.data.bones:
            lists = []
            for item in bone.mmr_bone.Set_constraints:
                lists.append(item)

            ct_op[bone.name] = lists

        bpy.ops.object.mode_set(mode='EDIT')  # 切到编辑模式

        BackupMatrix = {}

        # 备份所有骨骼的矩阵
        for bone in RIG.data.edit_bones:
            bone_matrix = bone.matrix.copy()
            # 世界矩阵
            bone_world_matrix = bone_matrix @ RIG.matrix_world
            # 备份世界矩阵
            BackupMatrix[bone.name] = bone_world_matrix

        # 激活骨架
        bpy.context.view_layer.objects.active = RIG
        RIG.select_set(True)

        foot_L_world_z = get_bone_world_z('foot.L',RIG)
        foot_R_world_z = get_bone_world_z('foot.R',RIG)

        heel_bones = ['heel.02.L', 'heel.02.R']

        heel_L_world_z = get_bone_world_z('heel.02.L',RIG)
        heel_R_world_z = get_bone_world_z('heel.02.R',RIG)

        heel_world_z = (heel_L_world_z + heel_R_world_z) / 2

        # 角度
        v = mmr.Bend_angle_leg
        v1 = mmr.Bend_angle_arm

        # 弯曲骨骼
        if mmr.Bend_the_bones:
            if Calculate_intersection_angle(RIG, 'upper_arm.L', 'forearm.L') > 165:
                rotate_bone_x(RIG,'upper_arm.L',angle_deg=-v1)
                rotate_bone_x(RIG,'forearm.L',angle_deg=v1*2)

            if Calculate_intersection_angle(RIG, 'upper_arm.R', 'forearm.R') > 165:
                rotate_bone_x(RIG,'upper_arm.R',angle_deg=-v1)
                rotate_bone_x(RIG,'forearm.R',angle_deg=v1*2)

        # 弯曲腿部骨骼
        if mmr.Bend_the_leg_bones:

            print('heel_world_z: ', heel_world_z)

            if Calculate_intersection_angle(RIG, 'thigh.L', 'shin.L') > 165:
                rotate_bone_x(RIG, 'thigh.L',angle_deg=-v)
                rotate_bone_x(RIG, 'shin.L',angle_deg=v*2)
                rotate_bone_x(RIG, 'foot.L',angle_deg=-v)

            if Calculate_intersection_angle(RIG, 'thigh.R', 'shin.R') > 165:
                rotate_bone_x(RIG, 'thigh.R',angle_deg=-v)
                rotate_bone_x(RIG, 'shin.R',angle_deg=v*2)
                rotate_bone_x(RIG, 'foot.R',angle_deg=-v)

            foot_L_world_z_1 = get_bone_world_z('foot.L', RIG)
            foot_R_world_z_1 = get_bone_world_z('foot.R', RIG)

            foot_L_world_z_difference = foot_L_world_z_1 - foot_L_world_z
            foot_R_world_z_difference = foot_R_world_z_1 - foot_R_world_z

            foot_world_z_difference = (foot_L_world_z_difference + foot_R_world_z_difference) / 2

            print('foot_world_z 差异: ', foot_world_z_difference)

            spine_world_z = get_bone_world_z('spine',RIG)
            print('spine_world_z: ', spine_world_z)

            spine_world_z_1 = spine_world_z - foot_world_z_difference
            print('spine_world_z 坐标: ', spine_world_z_1)

            set_bone_world_z('spine',RIG,spine_world_z_1)

            for bone in heel_bones:
                set_bone_world_z(bone,RIG,heel_world_z)

        u = "WGTS_" + RIG.name
        if u in bpy.data.collections:
            bpy.context.object.data.rigify_widgets_collection = bpy.data.collections["WGTS_" + RIG.name]

        RIG.name = 'MMR-' + mmd_arm.name

        # 生成
        bpy.ops.pose.rigify_generate()

        rigify = bpy.context.active_object
        rigify.name = 'RIG-' + mmd_arm.name

        # 设置父子级
        for key, value in config.items():

            # 原始矩阵
            org_matrix = BackupMatrix.get(value)

            if org_matrix is None:
                print(f"骨骼 {value} 不存在于org_matrix中")
                continue

            value = 'ORG-' + value

            # 进入RIG的编辑模式
            bpy.context.view_layer.objects.active = rigify
            bpy.ops.object.mode_set(mode='EDIT')
            # 进入mmd_arm的编辑模式
            bpy.context.view_layer.objects.active = mmd_arm
            bpy.ops.object.mode_set(mode='EDIT')

            mmd_edit_bones = mmd_arm.data.edit_bones
            rigify_edit_bones = rigify.data.edit_bones

            if 'eye' in value:
                continue

            # 检查骨骼是否存在
            if key in mmd_edit_bones and value in rigify_edit_bones:
                # 获取骨骼对象
                mmd_bone = mmd_edit_bones[key]
                rigify_bone = rigify_edit_bones[value]
                # 新建骨骼
                new_bone = rigify_edit_bones.new(name=value + '_parent')
                new_bone.head = mmd_bone.head  # 复制头位置
                new_bone.tail = mmd_bone.tail  # 复制尾位置
                new_bone.roll = mmd_bone.roll  # 复制旋转
                new_bone.parent = rigify_bone  # 设置父级

                # 获取骨骼矩阵
                new_bone_matrix = new_bone.matrix
                # 世界空间矩阵
                new_bone_world_matrix = new_bone_matrix @ rigify.matrix_world
                # 获取rigify骨骼矩阵
                rigify_bone_matrix = rigify_bone.matrix
                # 获取rigify骨骼世界空间矩阵
                rigify_bone_world_matrix = rigify_bone_matrix @ rigify.matrix_world

                # 计算相对变换矩阵
                relative_matrix = org_matrix.inverted() @ new_bone_world_matrix
                # 得到新的世界空间矩阵
                new_bone_world_matrix = rigify_bone_world_matrix @ relative_matrix

                # 转换为局部空间
                new_bone_matrix = new_bone_world_matrix @ rigify.matrix_world.inverted()
                new_bone.matrix = new_bone_matrix

                bpy.ops.object.mode_set(mode='POSE')

                # 加入集合
                bone = rigify.pose.bones.get(value + '_parent')
                rigify.data.collections_all['ORG'].assign(bone)
            else:
                print(f"骨骼 {key} 或 {value} 不存在于骨架中")

        # 设置捩骨
        Twist_bones = [
            {
                'forearm.L': 'ArmRoll_L', 
                'forearm.R': 'ArmRoll_R', 
                'upper_arm.L': 'ShoulderRoll_L', 
                'upper_arm.R': 'ShoulderRoll_R'
            },
            {
                'DEF-forearm.L.001': 'ArmRoll_L', 
                'DEF-forearm.R.001': 'ArmRoll_R', 
                'DEF-upper_arm.L.001': 'ShoulderRoll_L', 
                'DEF-upper_arm.R.001': 'ShoulderRoll_R'
            }
        ]

        for key, value in Twist_bones[0].items():

            # 原始矩阵
            org_matrix = BackupMatrix.get(key)

            if org_matrix is None:
                print(f"骨骼 {key} 不存在于org_matrix中")
                continue

            key = 'DEF-' + key

            # 进入RIG的编辑模式
            bpy.context.view_layer.objects.active = rigify
            bpy.ops.object.mode_set(mode='EDIT')
            # 进入mmd_arm的编辑模式
            bpy.context.view_layer.objects.active = mmd_arm
            bpy.ops.object.mode_set(mode='EDIT')

            mmd_edit_bones = mmd_arm.data.edit_bones
            rigify_edit_bones = rigify.data.edit_bones

            # 获取骨骼
            mmd_bone = mmd_edit_bones.get(value)
            rigify_bone = rigify_edit_bones.get(key)

            if not mmd_bone or not rigify_bone:
                print(f"骨骼 {value} 或 {key} 不存在于骨架中")
                continue

            value = 'ORG-' + value

            # 新建骨骼
            new_bone = rigify_edit_bones.new(name=value + '_parent')
            new_bone.head = mmd_bone.head  # 复制头位置
            new_bone.tail = mmd_bone.tail  # 复制尾位置
            new_bone.roll = mmd_bone.roll  # 复制旋转
            new_bone.parent = rigify_bone

            # 获取骨骼矩阵
            new_bone_matrix = new_bone.matrix
            # 世界空间矩阵
            new_bone_world_matrix = new_bone_matrix @ rigify.matrix_world
            # 获取rigify骨骼矩阵
            rigify_bone_matrix = rigify_bone.matrix
            # 获取rigify骨骼世界空间矩阵
            rigify_bone_world_matrix = rigify_bone_matrix @ rigify.matrix_world

            # 计算相对变换矩阵
            relative_matrix = org_matrix.inverted() @ new_bone_world_matrix
            # 得到新的世界空间矩阵
            new_bone_world_matrix = rigify_bone_world_matrix @ relative_matrix

            # 转换为局部空间
            new_bone_matrix = new_bone_world_matrix @ rigify.matrix_world.inverted()
            new_bone.matrix = new_bone_matrix

            bpy.ops.object.mode_set(mode='POSE')

            # 加入集合
            bone = rigify.pose.bones.get(value + '_parent')
            rigify.data.collections_all['ORG'].assign(bone)

        bpy.ops.object.mode_set(mode='EDIT')

        if not mmr.ORG_mode:
            for key, value in config.items():
                if 'eye' in value:
                    continue

                value1 = 'ORG-' + value + '_parent'

                # 进入编辑模式
                bpy.context.view_layer.objects.active = rigify
                bpy.ops.object.mode_set(mode='EDIT')

                bone = rigify.data.edit_bones.get(value1)

                if value1 in rigify.data.edit_bones:
                    # 父级
                    bone.parent = rigify.data.edit_bones['DEF-' + value]

        eye_pt = ['eye.L', 'eye.R']

        for n in eye_pt:
            for k , v in config.items():
                if v == n:
                    n = 'ORG-' + v
                    # 进入编辑模式
                    bpy.context.view_layer.objects.active = rigify
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.context.view_layer.objects.active = mmd_arm
                    bpy.ops.object.mode_set(mode='EDIT')

                    edit_bones = rigify.data.edit_bones
                    mmd_edit_bones = mmd_arm.data.edit_bones

                    s_bone = edit_bones[n]
                    m_bone = mmd_edit_bones[k]

                    # 复制骨骼（新建骨骼并复制属性）
                    new_bone = edit_bones.new(name = n +'_parent')
                    # 位置
                    new_bone.head = m_bone.head
                    new_bone.tail = m_bone.tail
                    # 扭转
                    new_bone.roll = m_bone.roll

        bpy.context.view_layer.objects.active = rigify
        rigify.select_set(True)
        bpy.ops.object.mode_set(mode='POSE')
        # 应用姿态
        bpy.ops.pose.armature_apply(selected=False)

        for k in eye_pt:
            # 进入编辑模式
            bpy.ops.object.mode_set(mode='EDIT')

            edit_bones = rigify.data.edit_bones

            s_bone = edit_bones['ORG-' + k + '_parent']
            e_bone = edit_bones['ORG-' + k]

            # 父级
            s_bone.parent = e_bone

            bpy.ops.object.mode_set(mode='POSE')
            # 加入集合
            data_bones = rigify.data.bones
            t_bone = data_bones.get('ORG-' + k + '_parent')
            rigify.data.collections_all['ORG'].assign(t_bone)

        # 捩骨约束
        for key, value in Twist_bones[1].items():
            value1 = 'ORG-' + value + '_parent'
            # 进入编辑模式
            bpy.ops.object.mode_set(mode='EDIT')
            edit_bones = rigify.data.edit_bones

            bone1 = edit_bones.get(key)
            bone2 = edit_bones.get(value1)

            if key in edit_bones and value1 in edit_bones:
                bone2.parent = bone1

            bpy.context.view_layer.objects.active = mmd_arm
            mmd_arm.select_set(True)
            bpy.ops.object.mode_set(mode='POSE')

            bone = mmd_arm.pose.bones.get(value)  # 获取骨骼

            # 检查骨骼是否存在
            if bone is None:
                print(f"警告: 未找到名为 {value} 的骨骼，跳过约束操作")
                continue  # 跳过后续约束

            # 删除所有约束
            for constraint in list(bone.constraints):
                if constraint.name == 'MMR_复制旋转':
                    bone.constraints.remove(constraint)

            # 添加复制旋转约束
            constraint = bone.constraints.new(type='COPY_ROTATION')  # 复制旋转
            constraint.name = 'MMR_复制旋转'
            constraint.target = rigify
            constraint.subtarget = value1

        constraint_names = ['MMR_复制旋转', 'MMR_复制位置', 'MMR_复制缩放']

        # 添加约束
        for key, value in config.items():

            value1 = 'ORG-' + value + '_parent'

            print(f"键名: {key}, 值: {value1}")

            bpy.context.view_layer.objects.active = mmd_arm
            mmd_arm.select_set(True)
            bpy.ops.object.mode_set(mode='POSE')

            bone = mmd_arm.pose.bones.get(key)  # 获取骨骼

            # 检查骨骼是否存在
            if bone is None:
                print(f"警告: 未找到名为 {key} 的骨骼，跳过约束操作")
                continue  # 跳过后续约束

            # 删除所有约束
            for constraint in list(bone.constraints):
                if constraint.name in constraint_names:
                    bone.constraints.remove(constraint)

            # 添加复制旋转约束
            constraint = bone.constraints.new(type='COPY_ROTATION')  # 复制旋转
            constraint.name = constraint_names[0]
            constraint.target = rigify
            constraint.subtarget = value1
            if not (ct_op.get(value))[0]:
                constraint.influence = 0

            # 添加复制位置约束
            constraint = bone.constraints.new(type='COPY_TRANSFORMS')  # 复制位置
            constraint.name = constraint_names[1]
            constraint.target = rigify
            constraint.subtarget = value1
            if not (ct_op.get(value))[1]:
                constraint.influence = 0

            # 添加复制缩放约束
            constraint = bone.constraints.new(type='COPY_SCALE')  # 复制缩放
            constraint.name = constraint_names[2]
            constraint.target = rigify
            constraint.subtarget = value1
            if not (ct_op.get(value))[2]:
                constraint.influence = 0

        subtarget = ['つま先ＩＫ.L', 'つま先ＩＫ.R', '足ＩＫ.R', '足ＩＫ.L']

        mmd_arms = True # 是否是mmd的armature

        # 遍历骨骼
        for bone in mmd_arm.pose.bones:
            # 遍历骨骼约束
            for constraint in bone.constraints:
                # 类型是否为IK
                if constraint.type == 'IK':
                    for s in subtarget:
                        if constraint.subtarget == s:
                            # 设置影响值为0
                            constraint.influence = 0.0
                            print(f"已将骨骼 '{bone.name}' 的IK约束影响值设置为0")
                            mmd_arms = False
        if mmd_arms:
            # 遍历骨骼
            for bone in mmd_arm.pose.bones:
                # 遍历骨骼约束
                for constraint in bone.constraints:
                    # 类型是否为IK
                    if constraint.type == 'IK':
                        # 设置影响值为0
                        constraint.influence = 0.0
                        print(f"已将骨骼 '{bone.name}' 的IK约束影响值设置为0")

        bpy.context.view_layer.objects.active = rigify
        rigify.select_set(True)
        # 进入编辑模式
        bpy.ops.object.mode_set(mode='EDIT')

        edit_bones = rigify.data.edit_bones

        e_bone = edit_bones['thigh_ik.R']
        c_bone = edit_bones['torso']
        root_bone = edit_bones['root']
        L_bone = edit_bones['hand_ik.L']
        R_bone = edit_bones['hand_ik.R']

        # 复制骨骼（新建骨骼并复制属性）
        new_bone = edit_bones.new(name='torso_root')
        # 位置
        new_bone.head.x = c_bone.head.copy().x
        new_bone.head.y = c_bone.head.copy().y
        new_bone.head.z = e_bone.tail.copy().z
        new_bone.tail.x = c_bone.tail.copy().x
        new_bone.tail.y = c_bone.tail.copy().y
        new_bone.tail.z = e_bone.tail.copy().z
        # 父级
        new_bone.parent = root_bone
        c_bone.parent = new_bone
        R_bone.parent = new_bone
        L_bone.parent = new_bone
        # 形状
        bpy.ops.object.mode_set(mode='POSE')
        pose_bones = rigify.pose.bones
        t_bone = pose_bones.get('torso_root')
        t_bone.color.palette = 'THEME09'
        t_bone.custom_shape = bpy.data.objects["WGT-RIG-" + RIG.name + "_root"]
        # 加入集合
        data_bones = rigify.data.bones
        t_bone = data_bones.get('torso_root')
        rigify.data.collections_all['Torso'].assign(t_bone)

        rigify.show_in_front = True # 在前面

        if mmr.Upper_body_linkage:
            rigify.pose.bones["torso"]["neck_follow"] = 0
            rigify.pose.bones["torso"]["head_follow"] = 0
        else:
            rigify.pose.bones["torso"]["neck_follow"] = 1
            rigify.pose.bones["torso"]["head_follow"] = 1

        is_gto = ['Face (Primary)', 'Face (Secondary)', 'Torso (Tweak)', 'Fingers (Detail)', 'Arm.L (FK)', 'Arm.R (FK)',
                  'Arm.L (Tweak)', 'Arm.R (Tweak)', 'Leg.L (FK)', 'Leg.R (FK)', 'Leg.L (Tweak)', 'Leg.R (Tweak)']

        # 隐藏骨骼集合
        for n in is_gto:
            rigify.data.collections_all[n].is_visible = False

        not_bone = ['ear.L', 'ear.R', 'jaw_master', 'teeth.B', 'tongue_master', 'teeth.T', 'nose_master']

        blender_version = bpy.app.version_string

        if compare_version(blender_version, "4.9.9"):
            # 隐藏骨骼
            for n in not_bone:
                bone = rigify.data.bones.get(n)
                bone.hide = True
        else:
            # 隐藏骨骼
            for n in not_bone:
                bone = rigify.pose.bones.get(n)
                bone.hide = True

        ik_stretch = ["upper_arm_parent.L", "upper_arm_parent.R", "thigh_parent.R","thigh_parent.L" ]

        # 关闭ik拉伸
        for i in ik_stretch:
            rigify.pose.bones[i]["IK_Stretch"] = 0

        # 极向目标
        if mmr.Polar_target:
            for i in ik_stretch:
                bone = rigify.pose.bones.get(i)
                bone["pole_vector"] = True

        if mmr.Use_ITASC_solver:
            rigify.pose.ik_solver = 'ITASC' # 设置IK解算器

        bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS' # 各自的原点

        bpy.ops.object.mode_set(mode='OBJECT')

        del_obj = [RIG.name]

        # 删除临时对象
        for y in del_obj:
            bpy.ops.object.select_all(action='DESELECT')
            del_object = bpy.data.objects.get(y)
            del_object.select_set(True)
            bpy.context.view_layer.objects.active = del_object
            bpy.ops.object.delete(use_global=False)

        if not mmr.Hide_mmd_skeleton:
            mmd_arm.hide_set(True) # 隐藏mmd骨架
        else:
            mmd_arm.select_set(True) # 选中mmd骨架

        mmd_arm.matrix_world = mmd_arm_matrix # 还原位置

        rigify.matrix_world = mmd_arm_matrix # 吸附位置

        # 激活并选择最终生成的Rigify骨架
        rigify.select_set(True)
        bpy.context.view_layer.objects.active = rigify

        self.report({'INFO'}, f"生成成功, 匹配骨骼数: {arm_number}")

        return {'FINISHED'}

BONE_MAP = {
    'Leg_L': {
        'start': 'Thigh_L', 'mid': 'MCH_Knee_L', 'end': 'Ankle_offset_L', 
        'ik_name': 'IK_Foot_L', 'pole_name': 'Pole_Knee_L', 
        'angle': -90
    },
    'Leg_R': {
        'start': 'Thigh_R', 'mid': 'MCH_Knee_R', 'end': 'Ankle_offset_R', 
        'ik_name': 'IK_Foot_R', 'pole_name': 'Pole_Knee_R', 
        'angle': -90
    },
    'Arm_L': {
        'start': 'Arm_L', 'mid': 'MCH_Elbow_L', 'end': 'Wrist_L', 
        'ik_name': 'IK_Hand_L', 'pole_name': 'Pole_Elbow_L', 
        'angle': 180
    },
    'Arm_R': {
        'start': 'Arm_R', 'mid': 'MCH_Elbow_R', 'end': 'Wrist_R', 
        'ik_name': 'IK_Hand_R', 'pole_name': 'Pole_Elbow_R', 
        'angle': 0
    },
}

class ControllerProperties(bpy.types.PropertyGroup):
    auto_twist_bones: BoolProperty(default=False)
    ik_generated: BoolProperty(default=False)

class GenerateIK(bpy.types.Operator):
    '''Generate IK controller for umamusume'''
    bl_idname = "uma.generate_ik"
    bl_label = "Generate IK"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object and context.active_object.type == 'ARMATURE' and len(context.selected_objects) == 1

    def execute(self, context):

        obj = context.active_object
        bpy.ops.uma.refine_bone_structure()

        # 创建形状
        square_shape = self.create_widget_shape("WGT_IK_Square", 'Square')
        pole_shape = self.create_widget_shape("WGT_IK_Pole", 'Dodecahedron')

        bpy.ops.object.mode_set(mode='EDIT')
        eb = obj.data.edit_bones

        # 创建 MCH 骨骼
        for key, data in BONE_MAP.items():
            if data['start'] not in eb: continue
            start_name = data['start']
            mid_name = data['mid']
            end_name = data['end']

            if eb.get(mid_name): continue

            mch_bone = eb.new(mid_name)
            mch_bone.head = eb.get(start_name).tail
            mch_bone.tail = eb.get(end_name).head
            mch_bone.parent = eb.get(start_name)
            
        created_data = []

        # 创建 IK 骨骼
        for key, data in BONE_MAP.items():
            if data['start'] not in eb: continue
            
            # 创建 IK
            ik_name = data['ik_name']
            if ik_name not in eb:
                ik = eb.new(ik_name)
                target = eb[data['end']]
                ik.head, ik.tail, ik.roll = target.head, target.tail, target.roll
                ik.parent = eb.get('Position')
                created_data.append(data)
            
            # 创建 Pole
            pole_name = data['pole_name']
            if pole_name not in eb:
                pole = eb.new(pole_name)
                mid = eb[data['mid']]
                if 'Leg' in key:
                    pole.head = mid.head + Vector((0, -0.5, 0))
                elif 'Arm' in key:
                    pole.head = mid.head + Vector((0, 0.3, 0))
                pole.tail = pole.head + Vector((0, 0, 0.1))
                if('Knee' in pole_name):
                    pole.parent = eb[ik_name]
                elif('Elbow' in pole_name):
                    pole.parent = eb.get('Position')
                pole.use_inherit_rotation = False

        bpy.ops.object.mode_set(mode='POSE')
        pb = obj.pose.bones

        # 创建 IK 约束
        for data in created_data:
            mid_name = data['mid']
            ik_name = data['ik_name']
            pole_name = data['pole_name']
            
            mid_pb = pb.get(mid_name)
            ik_pb = pb.get(ik_name)
            pole_pb = pb.get(pole_name)
            
            # 分组
            assign_bone_to_collection(obj, ik_name, "IK")
            assign_bone_to_collection(obj, pole_name, "IK")

            # 设置形状
            ik_pb.custom_shape = square_shape
            if('Foot' in ik_name):
                ik_pb.custom_shape_scale_xyz = (0.5, 0.9, 1)
                ik_pb.custom_shape_translation = (0, 0.06, 0)
            elif('Hand' in ik_name):
                ik_pb.custom_shape_scale_xyz = (0.5, 0.5, 1)
                if('_L' in ik_name):
                    ik_pb.custom_shape_rotation_euler = (radians(20), radians(15), radians(-15))
                    ik_pb.custom_shape_translation = (0.01, 0.03, 0)
                elif('_R' in ik_name):
                    ik_pb.custom_shape_rotation_euler = (radians(20), radians(-15), radians(15))
                    ik_pb.custom_shape_translation = (-0.01, 0.03, 0)

            pole_pb.custom_shape = pole_shape
            pole_pb.custom_shape_scale_xyz = (0.15, 0.15, 0.15)
            
            # IK 约束
            const = mid_pb.constraints.get('IK')
            if not const:
                const = mid_pb.constraints.new('IK')
            const.target = obj
            const.subtarget = ik_name
            const.pole_target = obj
            const.pole_subtarget = pole_name
            const.chain_count = 2
            const.pole_angle = radians(data['angle'])

        hidden_bones = ['MCH_Elbow_L', 'MCH_Elbow_R', 'MCH_Knee_L', 'MCH_Knee_R']
        for bone_name in hidden_bones:
            pbone = pb.get(bone_name)
            if pbone:
                pbone.bone.hide = True
                assign_bone_to_collection(obj, bone_name, "IK")

        bone_coll_name = ['Phys', 'Arm', 'Leg']
        for n in bone_coll_name:
            bone_coll = context.active_object.data.collections.get(n)
            if bone_coll:
                bone_coll.is_visible = False

        # 复制旋转
        suffix = ['_L', '_R']
        for i in suffix:
            orig_pb = pb.get('Elbow' + i)
            if not orig_pb: continue
            cr = orig_pb.constraints.get("COPY_ROTATION")
            if not cr: 
                cr = orig_pb.constraints.new('COPY_ROTATION')
            cr.target = obj
            cr.subtarget = 'MCH_Elbow' + i

        for i in suffix:
            orig_pb = pb.get('Knee' + i)
            if not orig_pb: continue
            cr = orig_pb.constraints.get("COPY_ROTATION")
            if not cr: 
                cr = orig_pb.constraints.new('COPY_ROTATION')
            cr.target = obj
            cr.subtarget = 'MCH_Knee' + i

        for i in suffix:
            orig_pb = pb.get('Wrist' + i)
            if not orig_pb: continue
            cr = orig_pb.constraints.get("COPY_ROTATION")
            if not cr: 
                cr = orig_pb.constraints.new('COPY_ROTATION')
            cr.target = obj
            cr.subtarget = 'IK_Hand' + i

        for i in suffix:
            orig_pb = pb.get('Ankle_offset' + i)
            if not orig_pb: continue
            cr = orig_pb.constraints.get("COPY_ROTATION")
            if not cr: 
                cr = orig_pb.constraints.new('COPY_ROTATION')
            cr.target = obj
            cr.subtarget = 'IK_Foot' + i

        eyes_config = {
            'left_eye': 'Eye_L',
            'right_eye': 'Eye_R',      
            'ik_master': 'IK_Eyes',
            'ik_target_L': 'IK_Eye_L',
            'ik_target_R': 'IK_Eye_R',
        }
        self.generate_eye_ik(obj, eyes_config)

        # 锁定骨骼旋转和缩放
        lock_pb_name = ['IK_Foot_L', 'Pole_Knee_L', 'IK_Foot_R', 'Pole_Knee_R', 'IK_Hand_L', 'Pole_Elbow_L', 'IK_Hand_R', 'Pole_Elbow_R', 'IK_Eyes', 'IK_Eye_L', 'IK_Eye_R'] 
        for n in lock_pb_name:
            if pb.get(n):
                pb.get(n).lock_scale = (True, True, True)
                pb.get(n).lock_location = (False, False, False)
                if 'Pole' in n:
                    pb.get(n).lock_rotation_w = (True)
                    pb.get(n).lock_rotation = (True, True, True)

        obj.uma_controller.ik_generated = True
        self.report({'INFO'}, "IK Rig Generated")
        return {'FINISHED'}
    
    def generate_eye_ik(self, obj, eyes_config):

        # 进入编辑模式创建骨骼
        bpy.ops.object.mode_set(mode='EDIT')
        eb = obj.data.edit_bones

        # 检查基础骨骼是否存在
        if eyes_config['left_eye'] not in eb or eyes_config['right_eye'] not in eb:
            print("Eye bones not found, skipping Eye IK generation.")
            return

        # 获取坐标参考
        eye_l = eb[eyes_config['left_eye']]
        eye_r = eb[eyes_config['right_eye']]
        
        # 计算眼睛中心点和前方偏移位置
        eye_center = (eye_l.head + eye_r.head) / 2
        forward_offset = Vector((0, -0.3, 0))
        bone_scale = 0.1747 * (eye_l.head - eye_r.head).length
        master_scale = (0.28878 * (eye_l.head - eye_r.head).length + 0.00166 ) / bone_scale
        lr_scale = 0.488 * master_scale
        
        # 创建总控制器
        ik_master_name = eyes_config['ik_master']
        if ik_master_name not in eb:
            ik_master = eb.new(ik_master_name)
            ik_master.head = eye_center + forward_offset
            ik_master.tail = ik_master.head + Vector((0, 0, bone_scale))
            ik_master.parent = None
        
        # 创建左右眼独立控制器
        for org_name, ik_name in [(eyes_config['left_eye'], eyes_config['ik_target_L']), (eyes_config['right_eye'], eyes_config['ik_target_R'])]:
            if ik_name not in eb:
                ik_target = eb.new(ik_name)
                org_bone = eb[org_name]
                ik_target.head = org_bone.head + forward_offset
                ik_target.tail = ik_target.head + Vector((0, 0, bone_scale))
                # 父级设为总控制器
                ik_target.parent = eb[ik_master_name]

        # 进入姿态模式设置约束和形状
        bpy.ops.object.mode_set(mode='POSE')
        pb = obj.pose.bones

        # 设置总控制器形状和组
        p_master = pb.get(eyes_config['ik_master'])
        if p_master:
            p_master.custom_shape = self.create_widget_shape("WGT_IK_Eyes", 'Eyes')
            p_master.custom_shape_scale_xyz = (master_scale, master_scale, 1)
            assign_bone_to_collection(obj, p_master.name, "IK")

        # 设置子控制器形状和组
        for ik_name in [eyes_config['ik_target_L'], eyes_config['ik_target_R']]:
            p_target = pb.get(ik_name)
            if p_target:
                p_target.custom_shape = self.create_widget_shape("WGT_IK_Circle", 'Circle')
                p_target.custom_shape_scale_xyz = (lr_scale, lr_scale, 1)
                assign_bone_to_collection(obj, p_target.name, "IK")

        # 添加约束
        for org_name, target_name in [(eyes_config['left_eye'], eyes_config['ik_target_L']), (eyes_config['right_eye'], eyes_config['ik_target_R'])]:
            p_org = pb.get(org_name)
            p_target = pb.get(target_name)
            
            if p_org and p_target:
                # 清理约束
                for con in p_org.constraints:
                    p_org.constraints.remove(con)
                
                # 添加阻尼追踪
                con = p_org.constraints.new('DAMPED_TRACK')
                con.target = obj
                con.subtarget = target_name
                con.track_axis = 'TRACK_Y'
                con.head_tail = 0.0
                p_org.bone.hide = True

    def create_widget_shape(self, name, shape_type):

        coll = bpy.data.collections.get("WGTS_UMA")
        if not coll:
            coll = bpy.data.collections.new("WGTS_UMA")
        coll.hide_viewport = True

        # 检查形状是否已存在
        mesh = bpy.data.meshes.get(name + "_Mesh")
        if not mesh:
            mesh = bpy.data.meshes.new(name + "_Mesh")
        
        obj = bpy.data.objects.get(name)
        if not obj:
            obj = bpy.data.objects.new(name, mesh)
            coll.objects.link(obj)
        else:
            # 确保它在集合里
            if obj.name not in coll.objects:
                coll.objects.link(obj)
        
        verts = []
        edges = []
        
        if shape_type == 'Square':
            verts = [(1.0, -1.0, 0.0), (1.0, 1.0, 0.0), (-1.0, 1.0, 0.0), (-1.0, -1.0, 0.0)]
            edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
            
        elif shape_type == 'Octahedron':
            verts = [(1.0, 0.0, 0.0), (-1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, -1.0, 0.0), (0.0, 0.0, 1.0), (0.0, 0.0, -1.0)]
            edges = [(0, 2), (0, 3), (0, 4), (0, 5), (1, 2), (1, 3), (1, 4), (1, 5), (2, 4), (2, 5), (3, 4), (3, 5)]

        elif shape_type == 'Dodecahedron':
            verts = [(-1.0, -1.0, -1.0), (-1.0, -1.0, 1.0), (-1.0, 1.0, -1.0), (-1.0, 1.0, 1.0), (1.0, -1.0, -1.0), (1.0, -1.0, 1.0), (1.0, 1.0, -1.0), (1.0, 1.0, 1.0), (0.0, -0.6180340051651001, -1.6180340051651), (0.0, -0.6180340051651001, 1.6180340051651), (0.0, 0.6180340051651001, -1.6180340051651), (0.0, 0.6180340051651001, 1.6180340051651), (-0.6180340051651001, -1.6180340051651, 0.0), (-0.6180340051651001, 1.6180340051651, 0.0), (0.6180340051651001, -1.6180340051651, 0.0), (0.6180340051651001, 1.6180340051651, 0.0), (-1.6180340051651, 0.0, -0.6180340051651001), (-1.6180340051651, 0.0, 0.6180340051651001), (1.6180340051651, 0.0, -0.6180340051651001), (1.6180340051651, 0.0, 0.6180340051651001)]
            edges = [[0, 8], [0, 12], [0, 16], [1, 9], [1, 12], [1, 17], [2, 10], [2, 13], [2, 16], [3, 11], [3, 13], [3, 17], [4, 8], [4, 14], [4, 18], [5, 9], [5, 14], [5, 19], [6, 10], [6, 15], [6, 18], [7, 11], [7, 15], [7, 19], [8, 10], [9, 11], [12, 14], [13, 15], [16, 17], [18, 19]]

        elif shape_type == 'Eyes': 
            verts = [(0.8928930759429932, -0.7071065902709961, 0.0), (0.8928932547569275, 0.7071067690849304, 0.0), (-1.8588197231292725, -0.9659252762794495, 0.0), (-2.100001096725464, -0.8660248517990112, 0.0), (-2.3071072101593018, -0.7071059942245483, 0.0), (-2.4660258293151855, -0.49999913573265076, 0.0), (-2.5659260749816895, -0.258818119764328, 0.0), (-2.5999999046325684, 8.575012770961621e-07, 0.0), (-2.5659255981445312, 0.2588198482990265, 0.0), (-2.4660253524780273, 0.5000006556510925, 0.0), (-2.3071064949035645, 0.7071075439453125, 0.0), (-2.099999189376831, 0.866025984287262, 0.0), (-1.8588184118270874, 0.9659261703491211, 0.0), (-1.5999996662139893, 1.000000238418579, 0.0), (-1.341180443763733, 0.9659258723258972, 0.0), (-1.0999995470046997, 0.8660253882408142, 0.0), (-0.8928929567337036, 0.7071067094802856, 0.0), (-0.892893373966217, -0.7071066498756409, 0.0), (-1.100000262260437, -0.8660252690315247, 0.0), (-1.3411810398101807, -0.9659255743026733, 0.0), (1.600000023841858, 1.0, 0.0), (1.3411810398101807, 0.9659258127212524, 0.0), (1.100000023841858, 0.8660253882408142, 0.0), (-1.600000262260437, -0.9999997615814209, 0.0), (1.0999997854232788, -0.8660252690315247, 0.0), (1.341180682182312, -0.9659257531166077, 0.0), (1.5999996662139893, -1.0, 0.0), (1.8588186502456665, -0.965925931930542, 0.0), (2.0999996662139893, -0.8660256266593933, 0.0), (2.3071064949035645, -0.7071071863174438, 0.0), (2.4660253524780273, -0.5000002980232239, 0.0), (2.5659255981445312, -0.25881943106651306, 0.0), (2.5999999046325684, -4.649122899991198e-07, 0.0), (2.5659260749816895, 0.25881853699684143, 0.0), (2.4660258293151855, 0.4999994933605194, 0.0), (2.3071072101593018, 0.707106351852417, 0.0), (2.1000006198883057, 0.8660250902175903, 0.0), (1.8588197231292725, 0.9659256339073181, 0.0), (-1.8070557117462158, -0.7727401852607727, 0.0), (-2.0000009536743164, -0.6928198337554932, 0.0), (-2.1656856536865234, -0.5656847357749939, 0.0), (-2.292820692062378, -0.3999992609024048, 0.0), (-2.3727407455444336, -0.20705445110797882, 0.0), (-2.3999998569488525, 7.336847716032935e-07, 0.0), (-2.3727405071258545, 0.207055926322937, 0.0), (-2.2928202152252197, 0.40000057220458984, 0.0), (-2.1656851768493652, 0.5656861066818237, 0.0), (-1.9999992847442627, 0.6928208470344543, 0.0), (-1.8070547580718994, 0.7727410197257996, 0.0), (-1.5999996662139893, 0.8000002503395081, 0.0), (-1.3929443359375, 0.7727407813072205, 0.0), (-1.1999995708465576, 0.6928203701972961, 0.0), (-1.0343143939971924, 0.5656854510307312, 0.0), (-1.0343146324157715, -0.5656852722167969, 0.0), (-1.2000001668930054, -0.6928201913833618, 0.0), (-1.3929448127746582, -0.7727404236793518, 0.0), (-1.6000001430511475, -0.7999997735023499, 0.0), (1.8070557117462158, 0.772739827632904, 0.0), (2.0000009536743164, 0.6928195953369141, 0.0), (2.1656856536865234, 0.5656843781471252, 0.0), (2.292820692062378, 0.39999890327453613, 0.0), (2.3727407455444336, 0.20705409348011017, 0.0), (2.3999998569488525, -1.0960745839838637e-06, 0.0), (2.3727405071258545, -0.20705628395080566, 0.0), (2.2928202152252197, -0.4000009298324585, 0.0), (2.1656851768493652, -0.5656863451004028, 0.0), (1.9999992847442627, -0.692821204662323, 0.0), (1.8070547580718994, -0.7727413773536682, 0.0), (1.5999996662139893, -0.8000004887580872, 0.0), (1.3929443359375, -0.7727410197257996, 0.0), (1.1999995708465576, -0.6928204894065857, 0.0), (1.0343143939971924, -0.5656855702400208, 0.0), (1.0343146324157715, 0.5656850337982178, 0.0), (1.2000004053115845, 0.6928199529647827, 0.0), (1.3929448127746582, 0.7727401852607727, 0.0), (1.6000001430511475, 0.7999995350837708, 0.0)]
            edges = [[24, 0], [1, 22], [16, 1], [17, 0], [23, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 8], [8, 9], [9, 10], [10, 11], [11, 12], [12, 13], [21, 20], [22, 21], [13, 14], [14, 15], [15, 16], [17, 18], [18, 19], [19, 23], [25, 24], [26, 25], [27, 26], [28, 27], [29, 28], [30, 29], [31, 30], [32, 31], [33, 32], [34, 33], [35, 34], [36, 35], [37, 36], [20, 37], [56, 38], [38, 39], [39, 40], [40, 41], [41, 42], [42, 43], [43, 44], [44, 45], [45, 46], [46, 47], [47, 48], [48, 49], [49, 50], [50, 51], [51, 52], [53, 54], [54, 55], [55, 56], [75, 57], [57, 58], [58, 59], [59, 60], [60, 61], [61, 62], [62, 63], [63, 64], [64, 65], [65, 66], [66, 67], [67, 68], [68, 69], [69, 70], [70, 71], [72, 73], [73, 74], [74, 75], [52, 72], [53, 71]]

        elif shape_type == 'Circle':
            res = 32
            for i in range(res):
                angle = 2 * pi * i / res
                verts.append((cos(angle), sin(angle), 0.0))
                if i > 0: edges.append((i-1, i))
            edges.append((res-1, 0))

        # 更新网格数据
        mesh.clear_geometry()
        mesh.from_pydata(verts, edges, [])
        mesh.update()
        return obj

class BakeFKtoIK(bpy.types.Operator):
    '''Bake FK motion to IK controller within scene frame range'''
    bl_idname = "uma.bake_fk_to_ik"
    bl_label = "Bake FK to IK"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE' and len(context.selected_objects) == 1 and context.active_object.uma_controller.ik_generated

    def execute(self, context):

        orig_obj = context.active_object
        current_mode = orig_obj.mode

        for _, data in BONE_MAP.items():
            if not data['ik_name'] in orig_obj.pose.bones :
                self.report({'ERROR'}, "IK not found")
                return {'CANCELLED'}
            if not data['pole_name'] in orig_obj.pose.bones :
                self.report({'ERROR'}, "Pole not found")
                return {'CANCELLED'}
            if not data['mid'] in orig_obj.pose.bones :
                self.report({'ERROR'}, "MCH not found")
                return {'CANCELLED'}

        # 复制当前骨架
        if current_mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.duplicate()
        tmp_obj = context.active_object

        # 清理约束
        for pb in tmp_obj.pose.bones:
            for con in pb.constraints:
                pb.constraints.remove(con)

        context.view_layer.objects.active = orig_obj
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')
        
        for _, data in BONE_MAP.items():
            ik_name = data['ik_name']
            pole_name = data['pole_name']
            fk_end_name = data['end']
            fk_mid_name = data['mid']
            
            # IK 控制器吸附到临时骨架的 FK 末端
            pb = orig_obj.pose.bones[ik_name]
            c = pb.constraints.new('COPY_TRANSFORMS')
            c.target = tmp_obj
            c.subtarget = fk_end_name
            # 选中 IK 控制器
            pb.bone.select = True

            pb = orig_obj.pose.bones[pole_name]
            c = pb.constraints.new('COPY_LOCATION')
            c.target = tmp_obj
            c.subtarget = fk_mid_name
            pb.bone.select = True

        bpy.ops.nla.bake(
            frame_start=context.scene.frame_start,
            frame_end=context.scene.frame_end,
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

        # 删除临时骨架
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        tmp_obj.select_set(True)
        bpy.ops.object.delete()

        if orig_obj.mode != current_mode:
            bpy.ops.object.mode_set(mode=current_mode)

        self.report({'INFO'}, "Bake FK to IK successfully")
        return {'FINISHED'}

