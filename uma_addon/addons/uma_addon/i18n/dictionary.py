from uma_addon.common.i18n.dictionary import preprocess_dictionary

#出现在UI中用*
#出现在操作中用Operator
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
        ("Operator", "ExampleOperator"): "示例操作",
        ("*","UMA Addon Panel"):"赛马娘插件面板",
        ("Operator", "Set Armature Layers"): "骨架分层",
        ("*", "Layer the umamusume skeleton"):"对赛马娘骨架进行分层",
        ("Operator", "Simplify Armature"): "简化骨架",
        ("*", "Delete selected collections and bones in it"):"删除选中的集合以及其中的骨骼",
        ("*", "Please remove the bones you want to keep from the selected collection"):"请从选中的集合中移除要保留的骨骼",
        ("*", "Delete Handle Collection"):"删除Handle集合",
        ("*", "Delete Face Collection"):"删除Face集合",
        ("*", "Delete Others Collection"):"删除Others集合",
        ("Operator", "Generate Controller"):"生成控制器",
        ("*", "Generate controller for umamusume"):"为赛马娘生成控制器",
        ("*", "Only works on umamusume skeletons layered by this plugin"):"仅适用于被本插件分层的赛马娘骨架",
        ("*", "Armature collections have been reset"):"骨骼集合已重置",
        ("*", "Repairs bones used to control binocular movements"):"修复用于控制双眼运动的骨骼",
        ("Operator", "Fix Eye Bone"):"修复眼骨",
        ("*", "Reset the umamusume skeleton collections"):"重置赛马娘骨骼集合",
        ("Operator", "Combine Shape Keys"):"合并形态键",
        ("*", "Generate left-right symmetirc combination form keys"):"生成左右对称的组合形态键",
        ("Operator", "Fix Blush"):"修复腮红",
        ("*", "Fix blush of mini umamusume model"):"修复迷你赛马娘模型的腮红",
        ("Operator", "Fix Normals"):"修复法向",
        ("*", "Fix normals of mini umamusume model"):"修复迷你赛马娘模型的法向",
        ("*", "Fix mini umamusume model:"):"修复迷你赛马娘模型：",
        ("*", "Delete Selected Collections:"):"删除选择的骨骼集合：",
        ("*", "Make the umamusume model more suitable for the production of change-head secondary creation"):"使赛马娘模型更适合换头二创的制作",
        ("*", "Change-head secondary creation:"):"换头二创：",
        ("Operator", "Pretreat"):"预处理",
        ("*", "Print selected vertex indexes to the console"):"将选中顶点的索引打印到控制台",
        ("Operator", "Print Vertex Indexes"):"打印顶点索引",
        ("*", "Reduce the workload of post-production keying by blocking render"):"通过阻隔渲染降低后期抠图的工作量",
        ("Operator", "Holdout"):"阻隔",
        ("*", "Create a new shapekey for the grid"):"为栅格新建一个形态键",
        ("Operator", "New Shape"):"新形态",
    }
}

dictionary = preprocess_dictionary(dictionary)

dictionary["zh_HANS"] = dictionary["zh_CN"]
