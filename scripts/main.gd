extends Node3D

# 导入工具类
var commons: GDScript = load("res://scripts/commons.gd")
var utils: Node = commons.new()


func _ready() -> void:
	# 获取节点信息保存为json文件
	#var node = $Props
	#var save_path = "res://scripts/pyscript/assets/"
	#_save_transforms_to_json(node, save_path)
	pass


# 将所有子节点基本信息保存至json
func _save_transforms_to_json(node: Node, output_path: String):
	if not node:
		print("Error: Root node not found.")
		return

	# 遍历所有子节点
	var result = []
	_traverse_nodes(node, result)

	# 写入json文件
	var json_string = JSON.stringify(result)
	var file = FileAccess.open(output_path + "all_node_info.json", FileAccess.WRITE_READ)
	file.store_string(json_string)
	file.close()

	# 导出为CSV
	var file_csv = FileAccess.open(output_path + "all_node_info.csv", FileAccess.WRITE_READ)
	file_csv.store_line("name,uuid,description,reference_path,position,rotation,scale,bounding_box_center,bounding_box_extend")
	for item in result:
		var line = (
			'%s,%d,"%s","%s","%s","%s","%s","%s","%s"'
			% [
				item["name"],
				item["uuid"],
				item["description"],
				item["reference_path"],
				utils.vector3_to_string(item["transform"]["position"]),
				utils.vector3_to_string(item["transform"]["rotation"]),
				utils.vector3_to_string(item["transform"]["scale"]),
				utils.vector3_to_string(item["bounding_box"]["center"]),
				utils.vector3_to_string(item["bounding_box"]["extend"]),
			]
		)
		file_csv.store_line(line)
	file_csv.close()
	print("Transforms saved to ", output_path)


# 递归获取所有节点基本信息
func _traverse_nodes(node: Node, result_array: Array):
	# 根节点不参与处理
	if node != $Props:
		# 获取场景节点的transform基本信息
		var name = utils.trim_trailing_digits(utils.camel_to_snake(node.name))
		var position = (node as Node3D).position
		var rotation = (node as Node3D).rotation
		var scale = (node as Node3D).scale

		# 获取子节点模型信息
		var center
		var extend
		var shape = node.get_child(1).shape as Shape3D
		if shape:
			var mesh = shape.get_debug_mesh()
			var combined_aabb = mesh.get_aabb()
			if combined_aabb.size != Vector3.ZERO:
				# 计算中心点
				center = combined_aabb.position + (combined_aabb.size / 2.0)
				# 扩展距离：边界框的尺寸的一半
				extend = combined_aabb.size / 2.0
			else:
				print("No CollisionShapes found or shapes have no volume.")
				print(mesh.get_aabb())

		# 填充节点信息
		var node_info = {
			"name": node.name,
			"uuid": node.get_instance_id(),
			"description": node.editor_description,
			"reference_path": "res://scenes/props/" + name + ".tscn",
			"transform":
			{
				"position":
				{
					"x": round(position.x * 100000) / 100000,
					"y": round(position.y * 100000) / 100000,
					"z": round(position.z * 100000) / 100000,
				},
				"rotation":
				{
					"x": round(rotation.x * 100000) / 100000,
					"y": round(rotation.y * 100000) / 100000,
					"z": round(rotation.z * 100000) / 100000,
				},
				"scale":
				{
					"x": round(scale.x * 100000) / 100000,
					"y": round(scale.y * 100000) / 100000,
					"z": round(scale.z * 100000) / 100000,
				},
			},
			"bounding_box":
			{
				"center":
				{
					"x": round(center.x * 100000) / 100000,
					"y": round(center.y * 100000) / 100000,
					"z": round(center.z * 100000) / 100000,
				},
				"extend":
				{
					"x": round(extend.x * 100000) / 100000,
					"y": round(extend.y * 100000) / 100000,
					"z": round(extend.z * 100000) / 100000,
				},
			}
		}
		result_array.append(node_info)
	else:
		# 处理Props子场景节点
		for child in node.get_children():
			_traverse_nodes(child, result_array)
