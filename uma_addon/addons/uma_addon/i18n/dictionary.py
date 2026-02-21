from ....common.i18n.dictionary import preprocess_dictionary

dictionary = {
    "zh_CN": {
        ("*", "Example Addon Side Bar Panel"): "示例插件面板",
        ("*", "Example Functions"): "示例功能",
        ("*", "ExampleAddon"): "示例插件",
        ("*", "Resource Folder"): "资源文件夹",
        ("*", "Int Config"): "整数参数",
        # This is not a standard way to define a translation, but it is still supported with preprocess_dictionary.
        "Boolean Config": "布尔参数",
        "Second Panel": "第二面板",
        ("*", "Add-on Preferences View"): "插件设置面板",
        ("*","UMA Addon"):"赛马娘插件",
        ("*","Processing Model"):"处理模型",
        ("*","Controller"):"控制器",
        ("*","Change Head"):"换头",
        ("Operator", "Set Bone Collections"): "骨架分层",
        ("*", "Layer the umamusume skeleton"):"对赛马娘骨架进行分层",
        ("Operator", "Refine Structure"): "优化形态",
        ("*", "Refine the bone structure of the umamusume skeleton"):"优化赛马娘骨架的形态",
        ("Operator", "Del"):"删除",
        ("*", "Delete selected collections and bones in it"):"删除选中的集合以及其中的骨骼",
        ("Operator", "For Umamusume"):"为赛马娘",
        ("*", "Generate MMR controller for umamusume"):"为赛马娘生成MMR控制器",
        ("Operator", "Generate IK"):"生成 IK",
        ("*", "Generate IK controller for umamusume"):"为赛马娘生成IK控制器",
        ("Operator", "Bake FK to IK"):"烘焙 FK 到 IK",
        ("*", "Bake FK motion to IK controller within scene frame range"):"在场景帧范围内烘焙选定对象的FK运动到IK控制器上",
        ("Operator", "Fix Blush"):"修复腮红",
        ("*", "Fix blush of mini umamusume model"):"修复迷你赛马娘模型的腮红",
        ("Operator", "Fix Normals"):"修复法向",
        ("*", "Fix normals of mini umamusume model"):"修复迷你赛马娘模型的法向",
        ("*", "Fix mini umamusume model:"):"修复迷你赛马娘模型：",
        ("*", "Make the umamusume model more suitable for the production of change-head secondary creation"):"使赛马娘模型更适合换头二创的制作",
        ("Operator", "Pretreat"):"预处理",
        ("*", "Blocking render"):"阻隔渲染",
        ("Operator", "Holdout"):"阻隔",
        ("*", "From basis"):"从基形",
        ("*", "From active shape key"):"从活动形态键",
        ("*", "Create a new absolute shape key:"):"创建一个新的绝对形态键：",
        ("*", "Tanuki Texture"):"纹狸",
        ("Operator", "Tanuki Texture"):"纹狸",
        ("*", "Tanuki Switch"):"改变狸",
        ("Operator", "Tanuki Switch"):"改变狸",
        ("*", "Pillow is installed"):"已安装 Pillow",
        ("*", "Pillow is not installed"):"未安装 Pillow",
        ("*", "The duration of the blockage caused by the installation depends on the network quality. Uninstallation takes effect after a restart."):"安装造成的阻塞时长取决于网络质量。卸载在重启后生效。",
        ("Operator", "Install Pillow"):"安装 Pillow",
        ("Operator", "Uninstall Pillow"):"卸载 Pillow",
        ("Operator", "Auto Twist"):"自动捩骨",
        ("*","Ear"):"耳朵",
        ("*","Bust"):"胸部",
    }
}

dictionary = preprocess_dictionary(dictionary)

dictionary["zh_HANS"] = dictionary["zh_CN"]
