@tool
extends Node3D

var file_path = "res://scripts/pyscript/assets/function_callback.json"
var last_modified_time = 0.0
@onready var test_object: Node3D = $"."


func _process(delta: float) -> void:
	# 仅在编辑器中运行代码
	if Engine.is_editor_hint():
		# 监听通道的文件是否修改
		if FileAccess.file_exists(file_path):
			var modified_time = FileAccess.get_modified_time(file_path)
			if modified_time != last_modified_time:
				# 首次不等时初始化last_modified_time变量
				if last_modified_time == 0.0:
					last_modified_time = modified_time
					return
				
				var file = FileAccess.open(file_path, FileAccess.READ)
				last_modified_time = modified_time

				# 解析通道文件
				var func_data = _parse_json_file(file)
				# 匹配执行函数
				_handle_tool_call(
					func_data["name"],
					func_data["arguments"],
				)
	else:
		pass


# 处理文件数据
func _parse_json_file(file: FileAccess):
	var json_text = file.get_as_text()
	file.close()

	var data = JSON.parse_string(json_text)
	if data.has("finish_reason") and data.has("message"):
		return data["message"]["tool_calls"][0]["function"]


# 执行对应的函数调用
func _handle_tool_call(func_name, args_str):
	var args = JSON.parse_string(args_str)
	match func_name:
		"spawn_object":
			spawn_object(args)
		_:
			print("Unknown function name: ", func_name)


# 在指定位置生成指定物体
func spawn_object(args: Dictionary):
	var reference_path = args["reference_path"]
	var scene = load(reference_path)
	if scene:
		var instance = scene.instantiate()
		add_child(instance)
		
		test_object.position = Vector3(args["pos_x"], args["pos_y"], args["pos_z"])
		test_object.rotation = Vector3(deg_to_rad(args["rot_x"]), deg_to_rad(args["rot_y"]), deg_to_rad(args["rot_z"]))
		test_object.scale = Vector3(args["scale_x"], args["scale_y"], args["scale_z"])
		print("Generating successfully.")
