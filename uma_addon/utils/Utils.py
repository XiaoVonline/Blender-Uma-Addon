import bpy
import os
import io
import struct

BONE_MAPPING_DICT = {
    "Arm_L":["腕.L", "upper_arm.L", "LeftArm", "mixamorig:LeftArm", "upperarm_l", "Left Upper Arm", "J_Bip_L_UpperArm", "L_UpperArm"],
    "Arm_R":["腕.R", "upper_arm.R", "RightArm", "mixamorig:RightArm", "upperarm_r", "Right Upper Arm", "J_Bip_R_UpperArm", "R_UpperArm"],
    "Elbow_L":["ひじ.L", "forearm.L", "LeftForeArm", "mixamorig:LeftForeArm", "lowerarm_l", "Left Lower Arm", "J_Bip_L_LowerArm", "L_LowerArm"],
    "Elbow_R":["ひじ.R", "forearm.R", "RightForeArm", "mixamorig:RightForeArm", "lowerarm_r", "Right Lower Arm", "J_Bip_R_LowerArm", "R_LowerArm"],
    "Shoulder_L":["肩.L", "shoulder.L", "LeftShoulder", "mixamorig:LeftShoulder", "clavicle_l", "J_Bip_L_Shoulder", "L_Shoulder"],
    "Shoulder_R":["肩.R", "shoulder.R", "RightShoulder", "mixamorig:RightShoulder", "clavicle_r", "J_Bip_R_Shoulder", "R_Shoulder"],
    "Thigh_L":["足.L", "thigh.L", "LeftUpLeg", "mixamorig:LeftUpLeg", "thigh_l", "Left Upper Leg", "J_Bip_L_UpperLeg", "L_UpperLeg"],
    "Thigh_R":["足.R", "thigh.R", "RightUpLeg", "mixamorig:RightUpLeg", "thigh_r", "Right Upper Leg", "J_Bip_R_UpperLeg", "R_UpperLeg"],
    "Knee_L":["ひざ.L", "shin.L", "LeftLeg", "mixamorig:LeftLeg", "calf_l", "Left Lower Leg", "J_Bip_L_LowerLeg", "L_LowerLeg"],
    "Knee_R":["ひざ.R", "shin.R", "RightLeg", "mixamorig:RightLeg", "calf_r", "Right Lower Leg", "J_Bip_R_LowerLeg", "R_LowerLeg"],
    "Ankle_L":["足首.L", "foot.L", "LeftFoot", "mixamorig:LeftFoot", "foot_l", "J_Bip_L_Foot", "L_Foot"],
    "Ankle_R":["足首.R", "foot.R", "RightFoot", "mixamorig:RightFoot", "foot_r", "J_Bip_R_Foot", "R_Foot"],
    "Toe_L":["足先EX.L", "toe.L", "LeftToeBase", "mixamorig:LeftToeBase", "ball_l", "Left Toes", "J_Bip_L_ToeBase", "L_Toe"],
    "Toe_R":["足先EX.R", "toe.R", "RightToeBase", "mixamorig:RightToeBase", "ball_r", "Right Toes", "J_Bip_R_ToeBase", "R_Toe"],
    "Wrist_L":["手首.L", "hand.L", "LeftHand", "mixamorig:LeftHand", "hand_l", "J_Bip_L_Hand", "L_Hand"],
    "Wrist_R":["手首.R", "hand.R", "RightHand", "mixamorig:RightHand", "hand_r", "J_Bip_R_Hand", "R_Hand"],
    "Position":["全ての親", "root", "Root", "master", "Center"],
    "Hip":["下半身", "spine", "Hips", "mixamorig:Hips", "pelvis", "J_Bip_C_Hips"],
    "Waist":["上半身", "spine.001", "Spine", "mixamorig:Spine", "spine_01", "J_Bip_C_Spine"],
    "Spine":["上半身3", "spine.002", "Spine1", "mixamorig:Spine1", "spine_02", "Chest", "J_Bip_C_Chest"],
    "Chest":["上半身2", "spine.003", "Spine2", "mixamorig:Spine2", "spine_03", "UpperChest", "J_Bip_C_UpperChest"],
    "Neck":["首", "spine.004", "Neck", "mixamorig:Neck", "neck_01", "J_Bip_C_Neck"],
    "Head":["頭", "spine.006", "Head", "mixamorig:Head", "head", "J_Bip_C_Head"],
    "Eye_L":["目.L", "eye.L", "LeftEye", "mixamorig:LeftEye", "eye_l", "J_Adj_L_FaceEye"],
    "Eye_R":["目.R", "eye.R", "RightEye", "mixamorig:RightEye", "eye_r", "J_Adj_R_FaceEye"],
    "Thumb_01_R":["親指０.R", "thumb.01.R", "RightHandThumb1", "mixamorig:RightHandThumb1", "thumb_01_r", "J_Bip_R_Thumb1"],
    "Thumb_02_R":["親指１.R", "thumb.02.R", "RightHandThumb2", "mixamorig:RightHandThumb2", "thumb_02_r", "J_Bip_R_Thumb2"],
    "Thumb_03_R":["親指２.R", "thumb.03.R", "RightHandThumb3", "mixamorig:RightHandThumb3", "thumb_03_r", "J_Bip_R_Thumb3"],
    "Index_01_R":["人指１.R", "f_index.01.R", "RightHandIndex1", "mixamorig:RightHandIndex1", "index_01_r", "J_Bip_R_Index1"],
    "Index_02_R":["人指２.R", "f_index.02.R", "RightHandIndex2", "mixamorig:RightHandIndex2", "index_02_r", "J_Bip_R_Index2"],
    "Index_03_R":["人指３.R", "f_index.03.R", "RightHandIndex3", "mixamorig:RightHandIndex3", "index_03_r", "J_Bip_R_Index3"],
    "Middle_01_R":["中指１.R", "f_middle.01.R", "RightHandMiddle1", "mixamorig:RightHandMiddle1", "middle_01_r", "J_Bip_R_Middle1"],
    "Middle_02_R":["中指２.R", "f_middle.02.R", "RightHandMiddle2", "mixamorig:RightHandMiddle2", "middle_02_r", "J_Bip_R_Middle2"],
    "Middle_03_R":["中指３.R", "f_middle.03.R", "RightHandMiddle3", "mixamorig:RightHandMiddle3", "middle_03_r", "J_Bip_R_Middle3"],
    "Ring_01_R":["薬指１.R", "f_ring.01.R", "RightHandRing1", "mixamorig:RightHandRing1", "ring_01_r", "J_Bip_R_Ring1"],
    "Ring_02_R":["薬指２.R", "f_ring.02.R", "RightHandRing2", "mixamorig:RightHandRing2", "ring_02_r", "J_Bip_R_Ring2"],
    "Ring_03_R":["薬指３.R", "f_ring.03.R", "RightHandRing3", "mixamorig:RightHandRing3", "ring_03_r", "J_Bip_R_Ring3"],
    "Pinky_01_R":["小指１.R", "f_pinky.01.R", "RightHandPinky1", "mixamorig:RightHandPinky1", "pinky_01_r", "J_Bip_R_Pinky1"],
    "Pinky_02_R":["小指２.R", "f_pinky.02.R", "RightHandPinky2", "mixamorig:RightHandPinky2", "pinky_02_r", "J_Bip_R_Pinky2"],
    "Pinky_03_R":["小指３.R", "f_pinky.03.R", "RightHandPinky3", "mixamorig:RightHandPinky3", "pinky_03_r", "J_Bip_R_Pinky3"],
    "Thumb_01_L":["親指０.L", "thumb.01.L", "LeftHandThumb1", "mixamorig:LeftHandThumb1", "thumb_01_l", "J_Bip_L_Thumb1"],
    "Thumb_02_L":["親指１.L", "thumb.02.L", "LeftHandThumb2", "mixamorig:LeftHandThumb2", "thumb_02_l", "J_Bip_L_Thumb2"],
    "Thumb_03_L":["親指２.L", "thumb.03.L", "LeftHandThumb3", "mixamorig:LeftHandThumb3", "thumb_03_l", "J_Bip_L_Thumb3"],
    "Index_01_L":["人指１.L", "f_index.01.L", "LeftHandIndex1", "mixamorig:LeftHandIndex1", "index_01_l", "J_Bip_L_Index1"],
    "Index_02_L":["人指２.L", "f_index.02.L", "LeftHandIndex2", "mixamorig:LeftHandIndex2", "index_02_l", "J_Bip_L_Index2"],
    "Index_03_L":["人指３.L", "f_index.03.L", "LeftHandIndex3", "mixamorig:LeftHandIndex3", "index_03_l", "J_Bip_L_Index3"],
    "Middle_01_L":["中指１.L", "f_middle.01.L", "LeftHandMiddle1", "mixamorig:LeftHandMiddle1", "middle_01_l", "J_Bip_L_Middle1"],
    "Middle_02_L":["中指２.L", "f_middle.02.L", "LeftHandMiddle2", "mixamorig:LeftHandMiddle2", "middle_02_l", "J_Bip_L_Middle2"],
    "Middle_03_L":["中指３.L", "f_middle.03.L", "LeftHandMiddle3", "mixamorig:LeftHandMiddle3", "middle_03_l", "J_Bip_L_Middle3"],
    "Ring_01_L":["薬指１.L", "f_ring.01.L", "LeftHandRing1", "mixamorig:LeftHandRing1", "ring_01_l", "J_Bip_L_Ring1"],
    "Ring_02_L":["薬指２.L", "f_ring.02.L", "LeftHandRing2", "mixamorig:LeftHandRing2", "ring_02_l", "J_Bip_L_Ring2"],
    "Ring_03_L":["薬指３.L", "f_ring.03.L", "LeftHandRing3", "mixamorig:LeftHandRing3", "ring_03_l", "J_Bip_L_Ring3"],
    "Pinky_01_L":["小指１.L", "f_pinky.01.L", "LeftHandPinky1", "mixamorig:LeftHandPinky1", "pinky_01_l", "J_Bip_L_Pinky1"],
    "Pinky_02_L":["小指２.L", "f_pinky.02.L", "LeftHandPinky2", "mixamorig:LeftHandPinky2", "pinky_02_l", "J_Bip_L_Pinky2"],
    "Pinky_03_L":["小指３.L", "f_pinky.03.L", "LeftHandPinky3", "mixamorig:LeftHandPinky3", "pinky_03_l", "J_Bip_L_Pinky3"]
}

UMA_BONES = ['Position', 'Hip', 'Waist', 'Spine', 'Chest', 'Neck', 'Head', 'Thigh_L', 'Knee_L', 'Ankle_L', 'Toe_L', 'Thigh_R', 'Knee_R', 'Ankle_R', 'Toe_R', 'Shoulder_L', 'Arm_L', 'Elbow_L', 'Wrist_L', 'Shoulder_R', 'Arm_R', 'Elbow_R', 'Wrist_R', 'Thumb_01_L', 'Thumb_02_L', 'Thumb_03_L', 'Index_01_L', 'Index_02_L', 'Index_03_L', 'Middle_01_L', 'Middle_02_L', 'Middle_03_L', 'Ring_01_L', 'Ring_02_L', 'Ring_03_L', 'Pinky_01_L', 'Pinky_02_L', 'Pinky_03_L', 'Thumb_01_R', 'Thumb_02_R', 'Thumb_03_R', 'Index_01_R', 'Index_02_R', 'Index_03_R', 'Middle_01_R', 'Middle_02_R', 'Middle_03_R', 'Ring_01_R', 'Ring_02_R', 'Ring_03_R', 'Pinky_01_R', 'Pinky_02_R', 'Pinky_03_R']

def assign_bone_to_collection(armature_obj, bone_name, collection_name):

    coll = armature_obj.data.collections.get(collection_name)
    if not coll:
        coll = armature_obj.data.collections.new(collection_name)
    bone = armature_obj.data.bones.get(bone_name)
    if bone:
        for c in bone.collections:
            c.unassign(bone)
        coll.assign(bone)
        return True
    else:
        return False
    
def find_file_by_keywords(directory, keywords):
    if not directory or not os.path.exists(directory):
        return None
    for f in os.listdir(directory):
        f_lower = f.lower()
        if all(k.lower() in f_lower for k in keywords):
            return os.path.join(directory, f)
    return None

def alert_error(title, message):
	def draw(self, context):
		self.layout.label(text=message)
	bpy.context.window_manager.popup_menu(draw, title=title, icon='ERROR')

class BinaryReader:
    def __init__(self, input_data):
        if isinstance(input_data, str):
            self.file = open(input_data, 'rb')
        elif isinstance(input_data, bytes):
            self.file = io.BytesIO(input_data)
        else:
            self.file = input_data
    
    def close(self):
        self.file.close()

    def read_int32(self):
        return struct.unpack('<i', self.file.read(4))[0]

    def read_sint64(self):
        return struct.unpack('<q', self.file.read(8))[0]

    def read_uint8(self):
        return struct.unpack('<B', self.file.read(1))[0]

    def read_float(self):
        return struct.unpack('<f', self.file.read(4))[0]

    def read_string(self):
        length = self.read_int32()
        if length < 0 or length > 10000:
            raise ValueError(f"invalid string length: {length}")
        data = self.file.read(length)
        self.align(4)
        return data.decode('utf-8')

    def align(self, alignment):
        pos = self.file.tell()
        mod = pos % alignment
        if mod != 0:
            self.file.read(alignment - mod)
