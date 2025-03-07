extends Node


# 将三维坐标格式化为字符串
func vector3_to_string(v) -> String:
	return "[{0}, {1}, {2}]".format([v.x, v.y, v.z])


# 去除末尾的数字
func trim_trailing_digits(s: String) -> String:
	while s.length() > 0:
		var last_char = s[s.length() - 1]
		if last_char >= "0" and last_char <= "9":
			s = s.left(s.length() - 1)
		else:
			break
	return s


# 驼峰转下划线变量命名法
func camel_to_snake(camel_case_str: String) -> String:
	# 首先检查并移除字符串末尾的数字
	var trimmed_str = camel_case_str.trim_suffix("0123456789")

	# 将大驼峰命名转换为小写，并在每个大写字母前添加下划线
	var snake_case_str = ""
	for i in range(trimmed_str.length()):
		var char = trimmed_str.substr(i, 1)
		if char >= "A" and char <= "Z":
			# 如果不是第一个字符，在大写字母前加下划线
			if i > 0:
				snake_case_str += "_"
			# 转换为小写
			snake_case_str += char.to_lower()
		else:
			snake_case_str += char

	return snake_case_str
