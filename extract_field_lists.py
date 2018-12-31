from src.lib.util import *
from src.lib.obj import bwobj

field_lists = {}
passed = []
def extract(obj):
	#print(obj.classnum)
	if obj in passed:
		return
	passed.append(obj)

	obj_field_list = []
	for i in obj.data:
		obj_field_list.append(extract_num(i))
		if isinstance(obj.data[i], bwobj.BW_Object):
			extract(obj.data[i])
		elif isinstance(obj.data[i], list) and len(obj.data[i]) > 0 and isinstance(obj.data[i][0], bwobj.BW_Object):
			for j in obj.data[i]:
				extract(j)
	if obj.classnum in typeLists.class_type_list:
		if typeLists.class_type_list[obj.classnum] == obj_field_list:
			return
	field_lists[obj.classnum] = obj_field_list

def print_extracted():
	for i in e.field_lists:
		print("{}: {},".format(i, e.field_lists[i]))
