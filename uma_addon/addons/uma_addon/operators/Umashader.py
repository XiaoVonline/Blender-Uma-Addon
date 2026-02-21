import bpy
import os
from ..config import __addon_name__

from ..utils.Utils import find_file_by_keywords

class ApplyShader(bpy.types.Operator):
    '''Apply uma shader to the model'''
    bl_idname = "uma.apply_shader"
    bl_label = "Shading"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context):
        return context.active_object and context.active_object.type == 'MESH' and len(context.selected_objects) == 1

    def execute(self, context: bpy.types.Context):
        obj = context.active_object
        
        # 定位同文件夹下的 Umashaders.blend
        blend_file = os.path.join(os.path.dirname(__file__), "Umashaders.blend")

        if not os.path.exists(blend_file):
            self.report({'ERROR'}, f"{blend_file} not found")
            return {'CANCELLED'}

        # 追加 Icosphere of Materials Collection
        col_name = None
        with bpy.data.libraries.load(blend_file, link=False) as (data_from, data_to):
            for name in data_from.collections:
                if "Icosphere" in name:
                    col_name = name
                    break
            if col_name:
                # 只在当前工程没有该集合时追加
                if col_name not in bpy.data.collections:
                    data_to.collections.append(col_name)
            else:
                self.report({'ERROR'}, "Icosphere of Materials collection not found in Umashaders.blend")
                return {'CANCELLED'}
        
        # 链接到当前场景的视图层
        coll = bpy.data.collections.get(col_name)
        if coll:
            if coll.name not in context.scene.collection.children:
                context.scene.collection.children.link(coll)
        else:
            self.report({'ERROR'}, "Failed to load Icosphere of Materials collection")
            return {'CANCELLED'}

        # 遍历选中模型的材质槽
        for slot in obj.material_slots:
            old_mat = slot.material
            if not old_mat: 
                continue
            # 判断部位类型
            part_type = None
            mat_name_lower = old_mat.name.lower()
            if 'bdy' in mat_name_lower or 'body' in mat_name_lower: part_type = 'bdy'
            elif 'hair' in mat_name_lower: part_type = 'hair'
            elif 'face' in mat_name_lower or 'mayu' in mat_name_lower: part_type = 'face'
            elif 'tail' in mat_name_lower: part_type = 'tail'
            elif 'eye' in mat_name_lower: part_type = 'eye'
            if not part_type:
                continue
            
            # 推导 Texture2D 贴图名
            if old_mat.node_tree:
                # 寻找原有材质里的图像节点来推导
                img_node = next((n for n in old_mat.node_tree.nodes if n.name == 'mmd_base_tex' or n.name == 'Image Texture' and n.image), None)
                if img_node:
                    img_path = bpy.path.abspath(img_node.image.filepath)
                    tex_dir = os.path.dirname(img_path)
                    tex_diff = os.path.basename(img_path)
                else:
                    self.report({'ERROR'}, f"Cannot find a valid image node in material {old_mat.name} to determine texture path")
                    return {'CANCELLED'}

                # 找到 Uma Shader
                target_shader_name = "Uma Eyes" if part_type == 'eye' else "Uma Shader"
                uma_shader = bpy.data.materials.get(target_shader_name)
                if not uma_shader:
                    with bpy.data.libraries.load(blend_file, link=False) as (data_from, data_to):
                        if target_shader_name in data_from.materials:
                            data_to.materials.append(target_shader_name)
                            uma_shader = bpy.data.materials.get(target_shader_name)
                        else:
                            self.report({'ERROR'}, f"{target_shader_name} not found in Umashaders.blend")
                            return {'CANCELLED'}

                # 对材质进行深拷贝并替换
                new_mat = uma_shader.copy()
                old_mat_name = old_mat.name
                if old_mat.users <= 1:
                    bpy.data.materials.remove(old_mat)
                new_mat.name = old_mat_name
                slot.material = new_mat
                nodes = new_mat.node_tree.nodes

                if part_type == 'eye':
                    for i, suffix in enumerate([None, "eyehi00", "eyehi01", "eyehi02"]):
                        node_name = "Image Texture" if i == 0 else f"Image Texture.{i:03d}"
                        node = nodes.get(node_name)
                        if node:
                            if i == 0:
                                node.image = bpy.data.images.load(img_path, check_existing=True)
                                node.image.colorspace_settings.name = 'sRGB'
                            else:
                                p = os.path.join(tex_dir, tex_diff.replace("eye0", suffix))
                                if os.path.exists(p):
                                    node.image = bpy.data.images.load(p, check_existing=True)
                                    node.image.colorspace_settings.name = 'Non-Color'

                else:
                    node = nodes.get("Image Texture")
                    if node:
                        node.image = bpy.data.images.load(img_path, check_existing=True)
                        node.image.colorspace_settings.name = 'sRGB'

                    node = nodes.get("Image Texture.001")
                    if node:
                        img_path = os.path.join(tex_dir, tex_diff.replace("diff", "ctrl"))
                        if not os.path.exists(img_path):
                            img_path = find_file_by_keywords(tex_dir, [part_type, 'ctrl'])  
                        if img_path and os.path.exists(img_path):
                            node.image = bpy.data.images.load(img_path, check_existing=True)
                            node.image.colorspace_settings.name = 'Non-Color'
                        else:
                            img_path = os.path.join(tex_dir, tex_diff.replace("diff", "ctrl"))
                            print(f"{img_path} not found")

                    node = nodes.get("Image Texture.002")
                    if node:
                        img_path = os.path.join(tex_dir, tex_diff.replace("diff", "shad_c"))
                        if os.path.exists(img_path):
                            img = bpy.data.images.load(img_path, check_existing=True)
                            node.image = img
                            node.image.colorspace_settings.name = 'sRGB'
                        else:
                            print(f"{img_path} not found")

                    node = nodes.get("Image Texture.003")
                    if node:
                        img_path = os.path.join(tex_dir, tex_diff.replace("diff", "base"))
                        if not os.path.exists(img_path):
                            img_path = find_file_by_keywords(tex_dir, [part_type, 'base'])  
                        if img_path and os.path.exists(img_path):
                            node.image = bpy.data.images.load(img_path, check_existing=True)
                            node.image.colorspace_settings.name = 'Non-Color'
                        else:
                            img_path = os.path.join(tex_dir, tex_diff.replace("diff", "base"))
                            print(f"{img_path} not found")

                    node = nodes.get("Image Texture.004")
                    if node:
                        img_path = os.path.join(tex_dir, tex_diff.replace("diff", "emi"))
                        if os.path.exists(img_path):
                            img = bpy.data.images.load(img_path, check_existing=True)
                            node.image = img
                            node.image.colorspace_settings.name = 'Non-Color'

                            for n in nodes:
                                if n.type == 'GROUP' and n.node_tree and "Uma Shader" in n.node_tree.name:
                                    n.inputs["Emmission Toggle"].default_value = 1
                        else:
                            print(f"{img_path} not found")

                    if part_type == 'face':
                        for n in nodes:
                            if n.type == 'GROUP' and n.node_tree and "Uma Shader" in n.node_tree.name:
                                n.inputs["Toggle If Face [0=Off,1=On]"].default_value = 1

        # 为选中模型加上 Uma Outlines 几何节点
        if "Uma Outlines" not in obj.modifiers:
            if "Uma Outlines" not in bpy.data.node_groups:
                with bpy.data.libraries.load(blend_file, link=False) as (data_from, data_to):
                    if "Uma Outlines" in data_from.node_groups:
                        data_to.node_groups.append("Uma Outlines")
            node_group = bpy.data.node_groups.get("Uma Outlines")
            if node_group:
                geom_mod = obj.modifiers.new(name="Uma Outlines", type='NODES')
                geom_mod.node_group = node_group

        geom_mod = obj.modifiers.get("Uma Outlines")
        if "Input_15" in geom_mod:
            geom_mod["Input_15"] = 0.1

        self.report({'INFO'}, "Uma shader applied")
        return {'FINISHED'}
