import bpy
import os
import shutil
import hashlib
import tempfile
from bpy.types import Operator, ShaderNodeCustomGroup
from bpy.props import (StringProperty, IntProperty, BoolProperty)
from bpy.app.handlers import persistent
from .Dependencies import is_pillow_available

class Refresh_Tanuki_Texture(Operator):
    """重新加载 GIF 并修复内部节点结构"""
    bl_idname = "uma.refreshtanukitexture"
    bl_label = "Refresh"
    
    def execute(self, context):
        # 获取当前正在操作的节点
        node = context.node
        if not node or not node.path:
            return {'CANCELLED'}

        abs_path = bpy.path.abspath(node.path)
        path_hash = hashlib.md5(abs_path.encode('utf-8')).hexdigest()
        cache_dir = os.path.join(tempfile.gettempdir(), "blender_uma_tanuki_cache", path_hash)
        # 清除该路径对应的缓存目录
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
            except Exception as e:
                self.report({'ERROR'}, f"{str(e)}")

        # 修复结构
        if not node.node_tree:
            self.report({'ERROR'}, "找不到节点组")
            return
        
        # 清空所有节点
        nodes = node.node_tree.nodes
        nodes.clear()

        # 重新创建节点
        out_node = nodes.new('NodeGroupOutput')
        out_node.name = "NodeGroupOutput"
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.name = "GIF_Internal"

        # 确保接口存在
        links = node.node_tree.links
        if len(node.node_tree.interface.items_tree) < 2:
            node.node_tree.interface.clear()
            node.node_tree.interface.new_socket(name="Color", in_out='OUTPUT', socket_type='NodeSocketColor')
            node.node_tree.interface.new_socket(name="Alpha", in_out='OUTPUT', socket_type='NodeSocketFloat')

        # 颜色连接
        if not any(l.to_node == out_node and l.to_socket.name == "Color" for l in links):
            links.new(tex_node.outputs['Color'], out_node.inputs['Color'])
        # Alpha连接
        if not any(l.to_node == out_node and l.to_socket.name == "Alpha" for l in links):
            links.new(tex_node.outputs['Alpha'], out_node.inputs['Alpha'])

        # 重新加载 GIF
        node.is_loaded = False
        node.gif_to_seq()
        
        # 界面重绘
        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}

class Tanuki_Texture(ShaderNodeCustomGroup):
    bl_idname = 'uma.tanuki_texture'
    bl_label = 'Tanuki Texture'
    
    def update_path(self, context):
        if self.path:
            self.gif_to_seq()

    def update_params(self, context):
        if self.is_loaded and self.node_tree:
            self.update_seq_idx(context.scene)

    path: StringProperty(name="Path", default="", subtype='FILE_PATH', update=update_path)
    step: IntProperty(name="Step", default=3, min=1, update=update_params)
    offset: IntProperty(name="Offset", default=0, update=update_params)

    total_frame: IntProperty(default=0)
    current_frame: IntProperty(default=0)
    width: IntProperty(default=0)
    height: IntProperty(default=0)
    is_loaded: BoolProperty(default=False)
    error_message: StringProperty(default="")
    sequence_start_path: StringProperty(default="")

    def init(self, context):
        bpy.app.timers.register(self.deferred_handler, first_interval=0.01)

    def copy(self, node):
        self.is_loaded = False
        bpy.app.timers.register(self.deferred_handler, first_interval=0.01)

    def free(self):
        if self.node_tree:
            if self.node_tree.users <= 1:
                bpy.data.node_groups.remove(self.node_tree, do_unlink=True)

    def deferred_handler(self):
        """延迟初始化，确保节点树结构完整"""
        try:
            if not self.id_data: return None
            
            # 初始化节点树
            if self.node_tree is None:
                self.create_node_tree()
            elif self.node_tree.users > 1:
                self.node_tree = self.node_tree.copy()

            # 尝试加载
            if self.path and not self.is_loaded:
                self.gif_to_seq()

        except Exception as e:
            self.error_message = f"{str(e)}"
            self.is_loaded = False
        return None # 停止计时器

    def create_node_tree(self):
        """创建纹理节点组"""
        new_tree = bpy.data.node_groups.new(self.bl_idname, 'ShaderNodeTree')
        new_tree.interface.new_socket(name="Color", in_out='OUTPUT', socket_type='NodeSocketColor')
        new_tree.interface.new_socket(name="Alpha", in_out='OUTPUT', socket_type='NodeSocketFloat')
        
        nodes = new_tree.nodes
        tex_node = nodes.new('ShaderNodeTexImage')
        tex_node.name = "GIF_Internal"
        out_node = nodes.new('NodeGroupOutput')
        
        links = new_tree.links
        links.new(tex_node.outputs['Color'], out_node.inputs['Color'])
        links.new(tex_node.outputs['Alpha'], out_node.inputs['Alpha'])
        
        self.node_tree = new_tree

    def gif_to_seq(self):
        
        try:
            abs_path = bpy.path.abspath(self.path)
            if not os.path.exists(abs_path):
                self.error_message = "File not exist"
                return
            
            # 生成缓存目录路径
            path_hash = hashlib.md5(abs_path.encode('utf-8')).hexdigest()
            cache_dir = os.path.join(tempfile.gettempdir(), "tanuki_cache", path_hash)

            # 检查缓存是否已存在
            exist_cache = False
            if os.path.exists(cache_dir):
                files = sorted([f for f in os.listdir(cache_dir) if f.endswith(".png")])
                if files and files[0] == "00.png":
                    frame_count = len(files)
                    exist_cache = True

            from PIL import Image, ImageSequence

            # 解压 GIF 到临时目录
            if not exist_cache:
                # 如果目录存在但损坏，重新解压
                if os.path.exists(cache_dir):
                    shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
                
                with Image.open(abs_path) as img:
                    self.width, self.height = img.size
                    frame_count = 0
                    for i, frame in enumerate(ImageSequence.Iterator(img)):
                        if i > 99: 
                            print("超过99帧，已截断。")
                            break

                        frame_rgba = frame.convert('RGBA')
                        out_name = f"{i:02d}.png"
                        out_path = os.path.join(cache_dir, out_name)
                        frame_rgba.save(out_path, format="PNG")
                        frame_count += 1
                        if frame_count == 0:
                            self.error_message = "GIF 解析失败"
                            return
            else:
                # 命中缓存，读取宽高
                first_frame_path = os.path.join(cache_dir, "00.png")
                with Image.open(first_frame_path) as img:
                    self.width, self.height = img.size

            self.total_frame = frame_count
            self.sequence_start_path = os.path.join(cache_dir, "00.png")

            self.setup_node()
            
            self.is_loaded = True
            self.error_message = ""
            
            self.update_seq_idx(bpy.context.scene)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error_message = f"{str(e)}"
            self.is_loaded = False

    def setup_node(self):
        tex_node = self.node_tree.nodes.get("GIF_Internal")
        if not tex_node: return

        try:
            path_hash = hashlib.md5(self.path.encode()).hexdigest()[:8]
            img_name = f"Tanuki_{path_hash}"
            
            # 如果旧图片对象有问题，可以尝试重新加载
            img = bpy.data.images.get(img_name)
            if img:
                # 检查图片是否有效，无效则移除重装
                if not os.path.exists(bpy.path.abspath(img.filepath)):
                    bpy.data.images.remove(img)
                    img = None

            if not img:
                img = bpy.data.images.load(self.sequence_start_path)
                img.name = img_name
            
            img.source = 'SEQUENCE'
            tex_node.image = img
            tex_node.image_user.frame_duration = self.total_frame
            tex_node.image_user.frame_start = 1 - self.total_frame
            tex_node.image_user.use_auto_refresh = True 
            
        except Exception as e:
            self.error_message = f"Setup Error: {str(e)}"
            self.is_loaded = False

    def update_seq_idx(self, scene):
        """计算目标图片索引"""
        if not self.is_loaded or self.total_frame == 0: 
            return
        if not self.node_tree: 
            return
        tex_node = self.node_tree.nodes.get("GIF_Internal")
        if not tex_node or not tex_node.image_user: 
            return
        if scene.frame_current < 0: 
            return
        
        current_step_idx = (scene.frame_current // self.step) + self.offset
        self.current_frame = current_step_idx % self.total_frame
        required_offset = self.current_frame - self.total_frame
        
        if tex_node.image_user.frame_offset != required_offset:
            tex_node.image_user.frame_offset = int(required_offset)

    def draw_buttons(self, context, layout):

        if not is_pillow_available():
            layout.alert = True
            layout.label(text="Please install Pillow first")
            return
            
        layout.prop(self, "path")
        
        if self.error_message:
            layout.alert = True
            layout.label(text=self.error_message, icon='ERROR')
            return
            
        if self.is_loaded:
            split = layout.split(factor=0.5, align=True)
            left = split.row(align=True)
            left.operator("uma.refreshtanukitexture", text="", icon='FILE_REFRESH')
            left.label(text=f"{self.current_frame+1}/{self.total_frame}")
            right = split.row(align=True)
            right.alignment = 'RIGHT'
            right.label(text=f"{self.width}x{self.height}")
            layout.prop(self, "step")
            layout.prop(self, "offset")

class Tanuki_Switch(ShaderNodeCustomGroup):
    bl_idname = 'uma.tanuki_switch'
    bl_label = 'Tanuki Switch'
   
    _is_updating = False

    def update_sockets(self, context):
        if(self.active_index > self.input_count - 1):
            self.active_index = self.input_count - 1
        bpy.app.timers.register(self.deferred_handler, first_interval=0.01)

    input_count: IntProperty(default=2, min=1, max=256, update=update_sockets)
    active_index: IntProperty(default=0, min=0, update=update_sockets)

    def init(self, context):
        bpy.app.timers.register(self.deferred_handler, first_interval=0.01)

    def copy(self, node):
        bpy.app.timers.register(self.deferred_handler, first_interval=0.01)

    def free(self):
        """删除节点时清理"""
        if self.node_tree:
            if self.node_tree.users <= 1:
                bpy.data.node_groups.remove(self.node_tree, do_unlink=True)

    def deferred_handler(self):
        try:
            # 节点如果被删除了，直接退出
            if not self.id_data:
                return None

            # 如果没有树，创建一个新的
            if self.node_tree is None:
                new_tree = bpy.data.node_groups.new(self.bl_idname, 'ShaderNodeTree')
                # 初始化基础节点
                new_tree.nodes.new('NodeGroupInput').name = "GROUP_IN"
                new_tree.nodes.new('NodeGroupOutput').name = "GROUP_OUT"
                self.node_tree = new_tree

            elif self.node_tree.users > 1:
                # 复制现有的树
                old_tree = self.node_tree
                new_tree = old_tree.copy()
                # 赋值给当前节点
                self.node_tree = new_tree

            # 只有在确保树是独立且存在后，才去更新
            if self.node_tree:
                self.refresh_node_tree()

        except Exception as e:
            self.error_message = f"{str(e)}"
            self.is_loaded = False
        
        return None # 停止计时器

    def refresh_node_tree(self):
        """接口更新"""
        if Tanuki_Switch._is_updating: return
        
        # 获取树的引用
        nt = self.node_tree
        if not nt: return

        Tanuki_Switch._is_updating = True
        
        try:
            interface = nt.interface
            
            # 确保内部节点存在
            in_node = nt.nodes.get("GROUP_IN")
            if not in_node:
                in_node = nt.nodes.new('NodeGroupInput')
                in_node.name = "GROUP_IN"
            
            out_node = nt.nodes.get("GROUP_OUT")
            if not out_node:
                out_node = nt.nodes.new('NodeGroupOutput')
                out_node.name = "GROUP_OUT"

            # 接口同步            
            expected_inputs = []
            for i in range(self.input_count):
                expected_inputs.append((f"Color {i}", 'NodeSocketColor'))
                expected_inputs.append((f"Alpha {i}", 'NodeSocketFloat'))

            # 获取当前接口状态
            current_sockets = [s for s in interface.items_tree if s.item_type == 'SOCKET' and s.in_out == 'INPUT']
            current_map = {s.name: s for s in current_sockets}
            expected_names = [n for n, _ in expected_inputs]
            expected_set = set(expected_names)
            
            # 倒序检查删除
            for s in reversed(current_sockets):
                if s.name not in expected_set:
                    interface.remove(s)

            # 只有当确实缺失时，才执行添加
            for name, stype in expected_inputs:
                if name not in current_map:
                    interface.new_socket(name=name, in_out='INPUT', socket_type=stype)

            # 检查输出接口
            out_names = {s.name for s in interface.items_tree if s.in_out == 'OUTPUT'}
            if "Color" not in out_names: 
                interface.new_socket(name="Color", in_out='OUTPUT', socket_type='NodeSocketColor')
            if "Alpha" not in out_names: 
                interface.new_socket(name="Alpha", in_out='OUTPUT', socket_type='NodeSocketFloat')

            # 只有在接口稳定后才连线
            self.update_internal_links(nt, in_node, out_node)

        except Exception as e:
            self.error_message = f"{str(e)}"
            self.is_loaded = False
        finally:
            Tanuki_Switch._is_updating = False

    def update_internal_links(self, nt, in_node, out_node):
        idx = min(self.active_index, self.input_count - 1)
        target_col = f"Color {idx}"
        target_alpha = f"Alpha {idx}"

        if target_col not in in_node.outputs or "Color" not in out_node.inputs:
            return

        def smart_link(from_socket, to_socket):
            if not from_socket or not to_socket: return
            if to_socket.is_linked:
                if to_socket.links[0].from_socket == from_socket:
                    return
                nt.links.remove(to_socket.links[0])
            nt.links.new(from_socket, to_socket)

        try:
            smart_link(in_node.outputs.get(target_col), out_node.inputs.get("Color"))
            smart_link(in_node.outputs.get(target_alpha), out_node.inputs.get("Alpha"))
        except:
            pass

    def update_frame_index(self):
        """检查当前连线是否与 index 匹配"""
        if not self.node_tree: return
        
        nt = self.node_tree
        out_node = nt.nodes.get("GROUP_OUT")
        in_node = nt.nodes.get("GROUP_IN")
        
        if not out_node or not in_node: return

        # 获取当前应有的 index
        idx = min(self.active_index, self.input_count - 1)
        
        # 获取当前连线
        current_linked_socket_name = ""
        if out_node.inputs['Color'].is_linked:
            current_linked_socket_name = out_node.inputs['Color'].links[0].from_socket.name
        
        # 如果当前连线不是目标连线就刷新，如果连对了就直接跳过
        if current_linked_socket_name != f"Color {idx}":
            self.update_internal_links(nt, in_node, out_node)

    def draw_buttons(self, context, layout):
        if not self.node_tree:
            layout.label(text="Init...")
        else:
            layout.prop(self, "input_count", text="Total")
            layout.prop(self, "active_index", text="Index")

@persistent
def scene_frame_change_handler(scene, depsgraph=None):
    # 查找所有 Tanuki 节点
    for mat in bpy.data.materials:
        if not mat or not mat.node_tree: continue
        if mat.users == 0: continue
        
        for node in mat.node_tree.nodes:
            if node.bl_idname == 'uma.tanukitexture':
                node.update_seq_idx(scene)
            elif node.bl_idname == 'uma.tanukiswitch':
                node.update_frame_index()
