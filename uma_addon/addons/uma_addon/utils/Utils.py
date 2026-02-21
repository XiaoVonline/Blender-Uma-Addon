import os

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