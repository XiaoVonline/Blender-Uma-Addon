import subprocess
import sys
from bpy.types import Operator

from ..config import __addon_name__

def is_pillow_available():
    try:
        from PIL import Image, ImageSequence
        return True
    except ImportError:
        return False
    
class InstallPillow(Operator):
    bl_idname = "uma.install_pillow"
    bl_label = "Install Pillow"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        # 执行安装
        target_cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "Pillow"]
        
        try:
            # 运行安装命令
            subprocess.run(
                target_cmd, 
                check=True, 
                capture_output=True, 
                text=True, 
                timeout=120
            )
            self.report({'INFO'}, "Pillow installed")
        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"Install failed: {e.stderr}")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        
        # 更新偏好设置显示
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'PREFERENCES':
                    area.tag_redraw()
        
        return {'FINISHED'}

class UninstallPillow(Operator):
    bl_idname = "uma.uninstall_pillow"
    bl_label = "Uninstall Pillow"
    bl_options = {'REGISTER', 'INTERNAL'}
    
    def execute(self, context):
        # 执行卸载
        target_cmd = [sys.executable, "-m", "pip", "uninstall", "-y", "Pillow"]
    
        try:
            # 运行卸载命令
            subprocess.run(
                target_cmd, 
                check=True, 
                capture_output=True, 
                text=True, 
                timeout=60
            )
            self.report({'INFO'}, "Pillow uninstalled")
        except subprocess.CalledProcessError as e:
            self.report({'ERROR'}, f"Uninstall failed: {e.stderr}")
        except Exception as e:
            self.report({'ERROR'}, str(e))
        
        # 更新偏好设置显示
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'PREFERENCES':
                    area.tag_redraw()
        
        return {'FINISHED'}
