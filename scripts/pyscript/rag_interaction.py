import os
import time
import json
import random
import hashlib
import requests
from http import HTTPStatus
from dashscope import Application
from dashscope import Generation
from datetime import datetime, timedelta
from deprecated.sphinx import deprecated
from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_bailian20231229.client import Client as bailian20231229Client
from alibabacloud_bailian20231229 import models as bailian_20231229_models
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_tea_util import models as util_models
from godot_scene_handler import get_target_window, take_screenshot


# 确保已设置DASHSCOPE_API_KEY环境变量
api_key = os.getenv("DASHSCOPE_API_KEY")
# 定义Function Call工具列表
tools = [
    # 在场景中生成或者放置一个物体
    {
        "type": "function",
        "function":
        {
            "name": "spawn_object",
            "description": "在场景中生成或者放置一个物体",
            "parameters":
            {
                "type": "object",
                "properties":  # 描述函数的参数
                {
                    "reference_path":
                    {
                        "type": "string",
                        "description": "要生成物体的ReferencePath"
                    },
                    "description":
                    {
                        "type": "string",
                        "description": "要生成物体的描述"
                    },
                    "pos_x":
                    {
                        "type": "number",
                        "description": "物体在x轴上的位置"
                    },
                    "pos_y":
                    {
                        "type": "number",
                        "description": "物体在y轴上的位置"
                    },
                    "pos_z":
                    {
                        "type": "number",
                        "description": "物体在z轴上的位置"
                    },
                    "rot_x":
                    {
                        "type": "number",
                        "description": "物体绕x轴的旋转角度"
                    },
                    "rot_y":
                    {
                        "type": "number",
                        "description": "物体绕y轴的旋转角度"
                    },
                    "rot_z":
                    {
                        "type": "number",
                        "description": "物体绕z轴的旋转角度"
                    },
                    "scale_x":
                    {
                        "type": "number",
                        "description": "物体在x轴上的缩放系数，默认为1.0"
                    },
                    "scale_y":
                    {
                        "type": "number",
                        "description": "物体在y轴上的缩放系数，默认为1.0"
                    },
                    "scale_z":
                    {
                        "type": "number",
                        "description": "物体在z轴上的缩放系数，默认为1.0"
                    }
                },
                "required": [  # 描述调用该函数需要哪些参数
                    "ReferencePath",
                    "description",
                    "pos_x",
                    "pos_y",
                    "pos_z",
                    "rot_x",
                    "rot_y",
                    "rot_z",
                    "scale_x",
                    "scale_y",
                    "scale_z"
                ]
            },
        }
    },
]


def tongyi_function_call(prompt="你好"):
    """
    通过函数调用实现3D游戏场景交互
    """
    print("Function Calling...")
    response = Generation.call(
        api_key=api_key,
        model="qwen-plus",
        messages=[
            {
                "content": prompt,
                "role": "user"
            },
        ],
        tools=tools,
        seed=random.randint(1, 10000),
        result_format="message"
    )

    if response.status_code != HTTPStatus.OK:
        print(f"request_id={response.request_id}")
        print(f"code={response.status_code}")
        print(f"message={response.message}")
        print(f"https://help.aliyun.com/zh/model-studio/developer-reference/error-code")
        return -1
    else:
        return response


def rag_tongyi_vl(prompt, image_url):
    """
    调用百炼3D游戏场景理解智能体
    :param prompt: 提示词
    :param image_url: 图片公网地址
    """
    print("Understanding the scene.")
    response = Application.call(
        api_key=api_key,
        app_id="f4837aa9b3bf46d988e256eacac95f61",
        prompt=prompt,
        image_list=[image_url],
    )

    if response.status_code != HTTPStatus.OK:
        print(f"request_id={response.request_id}")
        print(f"code={response.status_code}")
        print(f"message={response.message}")
        print("https://help.aliyun.com/zh/model-studio/developer-reference/error-code")
        return -1
    else:
        return response.output.text


if __name__ == "__main__":
    instruction = input("请输入交互指令。\n")

    # 获得场景截图
    window = get_target_window()
    if window:
        image_name = "SCENE_" + str(int(time.time())) + ".png"
        save_path = "image/scene/" + image_name
        take_screenshot(window, save_path)

    # LLM场景理解
    cpolar_base_url = "http://cf91f80.r16.cpolar.top"
    scene_desc = rag_tongyi_vl(
        f"这是一个奇幻风格三维场景的截图，请用json格式输出所有相关信息。指令：{instruction}",
        cpolar_base_url + "/" + image_name,
    )
    print(scene_desc)

    # LLM函数调用
    callback = tongyi_function_call(
        f"阅读以下场景描述文件：\n\n{scene_desc}\n\n函数调用：{instruction}",
    )
    with open("assets\\function_callback.json", 'w', encoding='utf-8') as f:
        json.dump(callback.output.choices[0], f, ensure_ascii=False, indent=4)
    print(json.dumps(callback.output.choices[0], ensure_ascii=False))


@deprecated(version="0.1.0", reason="PICUI图床无Content-Length字段")
def upload_image(image_path):
    # PICUI API文档参考：https://picui.cn/page/api-docs.html
    api = "https://picui.cn/api/v1/upload"
    token = "726|GXvg6aC3oYa5V8ROm4f0phZbC8Fd6pMHIzwuEIgS"

    # 设置过期时间
    current_time = datetime.now()
    expire_time = current_time + timedelta(minutes=1)
    expire_time_str = expire_time.strftime('%Y-%m-%d %H:%M:%S')

    # 设置请求头和数据
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    files = {
        "file": (os.path.basename(image_path), open(image_path, "rb"), "image/jpeg")
    }
    data = {
        "permission": 0,
        "expired_at": expire_time_str,
    }

    # 上传图像至图床
    response = requests.post(api, headers=headers, files=files, data=data)
    if response.status_code == 200:
        json = response.json()
        print("Upload image successfully")
        return json["data"]["links"]["url"]
    else:
        print(f"Upload failed: {response.status_code}, {response.text}")
        return -1


@deprecated(version="0.1.0", reason="不支持百炼临时文件方案")
def create_client() -> bailian20231229Client:
    """
    使用AK&SK初始化账号Client
    @return: Client
    @throws Exception
    """
    config = open_api_models.Config(
        access_key_id=os.environ["ALIBABA_CLOUD_ACCESS_KEY_ID"],
        access_key_secret=os.environ["ALIBABA_CLOUD_ACCESS_KEY_SECRET"]
    )
    config.endpoint = f'bailian.cn-beijing.aliyuncs.com'
    return bailian20231229Client(config)


@deprecated(version="0.1.0", reason="不支持百炼临时文件方案")
def calculate_md5(file_path):
    """
    计算文档的 MD5 值。
    """
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


@deprecated(version="0.1.0", reason="不支持百炼临时文件方案")
def apply_file_upload_lease(image_path):
    """
    向百炼平台申请文档上传租约
    :param image_path: 文档路径
    :return: lease_map
    """
    client = create_client()

    apply_file_upload_lease_request = bailian_20231229_models.ApplyFileUploadLeaseRequest(
        category_type='SESSION_FILE',
        file_name=os.path.basename(image_path),
        md_5=calculate_md5(image_path),
        size_in_bytes=os.path.getsize(image_path),
    )
    runtime = util_models.RuntimeOptions()
    headers = {}

    try:
        response = client.apply_file_upload_lease_with_options(
            'default',
            'llm-koxcnpq89bdtt6tf',
            apply_file_upload_lease_request,
            headers,
            runtime,
        )
        data_map = response.body.data.to_map()
        return {
            "id": data_map["FileUploadLeaseId"],
            "url": data_map["Param"]["Url"],
            "method": data_map["Param"]["Method"],
            "x_bailian_extra": data_map["Param"]["Headers"]["X-bailian-extra"],
            "content_type": data_map["Param"]["Headers"]["Content-Type"],
        }
    except Exception as error:
        print(error.message)
        print(error.data.get("Recommend"))
        UtilClient.assert_as_string(error.message)


@deprecated(version="0.1.0", reason="不支持百炼临时文件方案")
def upload_image(lease_map, image_path):
    """
    上传临时文件至百炼平台
    """
    try:
        headers = {
            "X-bailian-extra": lease_map["x_bailian_extra"],
            "Content-Type": lease_map["content_type"],
        }

        # 读取文档并上传
        with open(image_path, 'rb') as file:
            response = requests.put(
                lease_map["url"], data=file, headers=headers)

        if response.status_code == 200:
            print(f"File uploaded successfully. {response}")
            return lease_map["url"]  # 返回临时图片Url
        else:
            print(f"Failed to upload the file: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
