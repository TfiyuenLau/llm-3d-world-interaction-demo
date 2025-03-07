import os
import csv
import json
from pygltflib import GLTF2
from api_tongyi_vl import tongyi_vl, get_content


def flatten_dict(d, parent_key='', sep='_'):
    """
    将嵌套字典展平为一层。
    :param d: 要展平的字典
    :param parent_key: 父级键名前缀
    :param sep: 键名连接符
    :return: 展平后的字典
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def extract_material_info(material):
    """
    提取材质的基本颜色信息。
    """
    pbr = material.pbrMetallicRoughness
    base_color_factor = getattr(pbr, "baseColorFactor", [1.0, 1.0, 1.0, 1.0])
    return {
        "BaseColor": [round(c, 5) for c in base_color_factor[:3]],  # RGB
        "BaseFalloff": None
    }


def calculate_bounding_box(accessors):
    """
    计算边界框中心和范围。
    """
    accessor = accessors[0]
    min_coords = accessor.min if accessor.min is not None else [0, 0, 0]
    max_coords = accessor.max if accessor.max is not None else [0, 0, 0]

    center = [round((min_val + max_val) / 2, 5)
              for min_val, max_val in zip(min_coords, max_coords)]
    extend = [round(max_val - min_val, 5)
              for min_val, max_val in zip(min_coords, max_coords)]
    return {"center": center, "extend": extend}


def parse_glb_to_obj(glb_path, custom_name="", custom_description="", custom_path="", custom_pivot="物体中心"):
    gltf = GLTF2().load(glb_path)

    # 初始化结果字典
    result = {
        "name": custom_name,
        "description": custom_description,
        "reference_path": custom_path,
        "pivot": custom_pivot,
        "geometry_info": {},
        "bounding_box": calculate_bounding_box(gltf.accessors),
        "materials": []
    }

    # 几何信息：顶点数和三角形数量
    if gltf.meshes and gltf.meshes[0].primitives:
        first_primitive = gltf.meshes[0].primitives[0]

        # 使用点符号访问POSITION属性
        position_accessor_index = getattr(
            first_primitive.attributes, "POSITION")
        position_accessor = gltf.accessors[position_accessor_index]

        indices_accessor_index = first_primitive.indices
        indices_accessor = gltf.accessors[indices_accessor_index]

        result["geometry_info"]["vertices"] = position_accessor.count
        result["geometry_info"]["triangles"] = indices_accessor.count // 3

    # 材质信息
    for material in gltf.materials:
        material_dict = {
            material.name if material.name else "UnnamedMaterial": extract_material_info(material)}
        result["materials"].append(material_dict)

    return result


def gen_glb_desc_file(models_dir, images_dir, output_dir):
    """
    遍历models目录下的所有GLB文件，获取基本信息，并调用tongyi_vl接口获取描述，生成JSON和CSV文件
    :param models_dir: 包含GLB文件的目录
    :param images_dir: 包含GLB模型截图的目录
    :param output_dir: 输出JSON文件的目录
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 遍历models目录下的所有GLB文件
    all_results = []
    for filename in os.listdir(models_dir):
        if filename.endswith(".glb"):
            glb_path = os.path.join(models_dir, filename)
            glb_image_path = os.path.join(
                images_dir,
                os.path.splitext(filename)[0] + '.jpg',
            )

            # 调用tongyi_vl获取模型图像描述
            prompt = "类中世纪题材3D资产，极简描述物体主要特征"
            response_dict = json.loads(tongyi_vl(glb_image_path, prompt))
            content = get_content(response_dict)

            # 生成glb模型描述文件
            result = parse_glb_to_obj(
                glb_path,
                os.path.basename(glb_path).split(".")[0],
                custom_description=content,
                custom_path="res:\\scenes\\props\\" +
                os.path.splitext(filename)[0] + '.tscn',
            )
            all_results.append(result)
            print(filename + " process completely.")

    # 保存为JSON文件
    final_output_path = os.path.join(output_dir, "all_model_info.json")
    with open(final_output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)

    print(f"All results have been saved to {final_output_path}")

    # 准备写入CSV
    fieldnames = set()
    flat_results = []
    for result in all_results:
        flat_result = flatten_dict(result)
        flat_results.append(flat_result)
        fieldnames.update(flat_result.keys())

    final_output_csv_path = os.path.join(output_dir, "all_model_info.csv")
    with open(final_output_csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=sorted(fieldnames))
        writer.writeheader()
        writer.writerows(flat_results)

    print(f"All results have been saved to {final_output_csv_path}")


if __name__ == "__main__":
    glb_path = "../../models/props/banner_mounted.glb"
    result = parse_glb_to_obj(
        glb_path,
        os.path.basename(glb_path).split(".")[0],
        custom_description="这是一段物体描述。",
        custom_path=glb_path,
    )
    custom_json = json.dumps(result, ensure_ascii=False, indent=4)
    print(custom_json.encode('utf-8').decode('utf-8'))

    # 生成glb模型描述文件
    # MODELS_DIR = "..\\..\\models\\props"
    # IMAGES_DIR = ".\\image\\model"
    # OUTPUT_DIR = ".\\assets"
    # gen_glb_desc_file(MODELS_DIR, IMAGES_DIR, OUTPUT_DIR)
