# 基于Godot实现LLM交互3D世界——Python脚本部分

>项目使用 [**uv**](https://hellowac.github.io/uv-zh-cn/) 进行包管理。请安装 python 的项目管理工具 uv，并使用`uv sync`命令同步项目依赖。

## 一、项目结构

### Ⅰ、生成 GLB 模型描述文件
1. **glb_json_handler.py**: 处理 GLB 模型的基本信息，将 GLB 描述信息转换为 Python 对象。
2. **api_tongyi_vl.py**: 调用通义千问 VL 图像理解模型，生成 GLB 模型的文本描述。

其中`glb_json_handler.py`生成的 JSON 和 CSV 文件将被保存在`assets`文件夹中。

### Ⅱ、截取并理解 Godot 场景图像
1. **godot_sence_handler.py**: 用于实现对当前的 Godot 窗口场景截图。
2. **image_server.py**: 图床服务器，用于在调用 RAG 智能体时提供场景图像公网链接。
3. **rag_interaction.py**: 通过调用 RAG 智能体，对场景图像进行理解；同时生成用于指令的函数调用描述文件。

其中`rag_interaction.py`生成的指令函数调用 JSON 文件将被保存在`assets`文件夹中，等待 Godot 脚本读取。


## 二、运行方式

>注意：请配置 `**DASHSCOPE_API_KEY**` 环境变量(阿里云百炼平台)，以便调用通义系列模型 API。

Ⅰ、运行 `godot_sence_handler.py` 生成对应的 GLB 模型描述文件。

Ⅱ、运行 `image_server.py` 启动图床服务器；

请注意配置内网穿透，以使得百炼平台的 API 调用可以访问到本地的3D场景截图。

Ⅲ、调整并运行 `rag_interaction` 脚本，并等待 RAG 智能体返回的指令函数调用描述文件。

## 延伸阅读
- [How to make 3D Games in Godot](https://www.youtube.com/watch?v=ke5KpqcoiIU)
- [基于LLM打造沉浸式3D世界](https://mp.weixin.qq.com/s/ozQHvZ5eRNLZwqhcu3QPvQ)
