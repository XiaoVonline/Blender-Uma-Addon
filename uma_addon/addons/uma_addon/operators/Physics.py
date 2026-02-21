import bpy
from bpy.props import BoolProperty

from ..config import __addon_name__

EAR_BONES = ['Ear_01_L', 'Ear_02_L', 'Ear_01_R', 'Ear_02_R']
BUST_BONES = ['Sp_Ch_Bust0_L_00', 'Sp_Ch_Bust0_R_00']
TAIL_BONES = ['Sp_Hi_Tail0_B_00', 'Sp_Hi_Tail0_B_01', 'Sp_Hi_Tail0_B_02', 'Sp_Hi_Tail0_B_03']

class DampedTrackProperties(bpy.types.PropertyGroup):

    def get_enable(bone_names):
        def get(self):
            arm = bpy.context.active_object
            if arm is None:
                return False
            for bone_name in bone_names:
                if bone_name in arm.pose.bones:
                    pbone = arm.pose.bones[bone_name]
                    for c in pbone.constraints:
                        if c.name.endswith(__addon_name__):
                            return True
                return False
            return False
        return get

    def set_enable(bone_names):
        def set(self, value):
            arm = bpy.context.active_object
            if arm is None:
                return
            if value:
                # 添加约束
                for bone_name in bone_names:
                    if bone_name in arm.pose.bones:
                        pbone = arm.pose.bones[bone_name]
                        if pbone.children:
                            c = pbone.constraints.new(type='DAMPED_TRACK')
                            c.name += __addon_name__
                            c.influence = 0.3
                            if 'Tail' in bone_name:
                                c.influence = 0.7
                            c.target = arm
                            c.subtarget = pbone.children[0].name
            else:
                # 删除所有现有插件约束
                for bone_name in bone_names:
                    if bone_name in arm.pose.bones:
                        pbone = arm.pose.bones[bone_name]
                        for c in pbone.constraints:
                            if c.name.endswith(__addon_name__) and c.type == 'DAMPED_TRACK':
                                pbone.constraints.remove(c)
        return set

    ear_enable: BoolProperty(get=get_enable(EAR_BONES), set=set_enable(EAR_BONES))
    bust_enable: BoolProperty(get=get_enable(BUST_BONES), set=set_enable(BUST_BONES))
    tail_enable: BoolProperty(get=get_enable(TAIL_BONES), set=set_enable(TAIL_BONES))