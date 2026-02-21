from ..config import __addon_name__
from ..operators.AddonOperators2 import SelectUnassignedMeshes, MarkCollectionCenter, PrintSelectedVertices, PrintSelectedBones, PrintAllBones, MeshToPython, CombineShapekeys, SyncShapekeys
from ..operators.GenerateController import MMRRig
from ..operators.TanukiNodes import Tanuki_Texture, Tanuki_Switch
from ....common.i18n.i18n import i18n
from ....common.types.framework import reg_order
from ..preference.AddonPreferences import AddonPreferences

def View3dObject_menu(self, context):
    prefs = context.preferences.addons[__addon_name__].preferences
    self.layout.separator()
    self.layout.operator(SelectUnassignedMeshes.bl_idname)
    if prefs.debug:
        self.layout.operator(MeshToPython.bl_idname)
        self.layout.operator(CombineShapekeys.bl_idname)
        self.layout.operator(SyncShapekeys.bl_idname)

def View3dEdit_menu(self, context):
    prefs = context.preferences.addons[__addon_name__].preferences
    if prefs.debug:
        self.layout.separator()
        self.layout.operator(PrintSelectedVertices.bl_idname)

def View3dPose_menu(self, context):
    prefs = context.preferences.addons[__addon_name__].preferences
    if prefs.debug:
        self.layout.separator()
        self.layout.operator(PrintSelectedBones.bl_idname)
        self.layout.operator(PrintAllBones.bl_idname)

def Outliner_menu(self, context):
    self.layout.separator()
    self.layout.operator(MarkCollectionCenter.bl_idname, icon='ASSET_MANAGER')

def MMR_XFFGL_menu(self, context):
    self.layout.operator(MMRRig.bl_idname, icon='OUTLINER_DATA_ARMATURE')

# 节点菜单
def TanukiTexture_menu(self, context):
    self.layout.separator()
    self.layout.operator("node.add_node", text="Tanuki Texture").type = Tanuki_Texture.bl_idname

def TanukiSwitch_menu(self, context):
    self.layout.separator()
    self.layout.operator("node.add_node", text="Tanuki Switch").type = Tanuki_Switch.bl_idname