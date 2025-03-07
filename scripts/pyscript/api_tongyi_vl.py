import os
import base64
import json
from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)


def encode_image(image_path):
    """
    编码图片为base64格式
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def tongyi_vl(image_path, prompt="这是什么"):
    base64_image = encode_image(image_path)
    completion = client.chat.completions.create(
        model="qwen-vl-max",
        messages=[{"role": "user", "content": [
            {
                "type": "text",
                "text": prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }
        ]}]
    )
    return completion.model_dump_json()


def get_content(response_dict):
    if "choices" in response_dict and len(response_dict["choices"]) > 0:
        first_choice = response_dict["choices"][0]
        if "message" in first_choice and "content" in first_choice["message"]:
            content = first_choice["message"]["content"]
            return content
        else:
            print("Message or content not found in the response.")
            return
    else:
        print("No choices found in the response.")
        return


if __name__ == "__main__":
    prompt = "类中世纪题材3D资产，极简描述物体主要特征"
    result_str = tongyi_vl("image\\model\\banner_mounted.jpg", prompt)
    response_dict = json.loads(result_str)
    content = get_content(response_dict)
    print(content)
