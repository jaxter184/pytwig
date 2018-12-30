from src.lib import bwfile, objects, atoms
from src.lib import color as col
from src.lib.luts import non_overlap

if __name__ == "__main__":
	test = bwfile.BW_File()
	test.read('input/clip6.bwclip')
	#test.read('input/proj.bwproject', meta_only = False, raw = True)
	#test.read('input/preset.bwpreset', meta_only = False, raw = True)

	preset_body = test.contents.get(2409).get(1245).get(1246)[0].get(356).get(324)[0].get(407) # gets the first item of the device chain
	preset_body.set(4830, "preset3")
	preset_body.set(158, "jaxter184")
	preset_body.set(162, test.meta.data["tags"])
	preset = bwfile.BW_File('preset')
	preset.num_spaces = test.num_spaces
	preset.header = "BtWg00010002008f000017140000000000000000"
	preset.contents = objects.Contents(1377)
	preset.contents.set(5153, preset_body)
	preset.meta.set_multi({
		"application_version_name" : "2.4.3",
		"branch" : "releases",
		"comment" : preset_body.get(159),
		"creator" : preset_body.get(158),
		"device_category" : preset_body.get(156),
		"device_creator" : preset_body.get(155),
		"device_id" : preset_body.get(153),
		"device_name" : preset_body.get(154),
		"device_type" : "note_to_audio",
		"preset_category" : preset_body.get(161),
		"referenced_device_ids" : preset.contents.get_referenced_ids(),
		"referenced_packaged_file_ids" : [],
		"referenced_modulator_ids" : [],
		"referenced_module_ids" : [],
		"referenced_packaged_file_ids" : [],
		"revision_id" : test.meta.data["revision_id"],
		"revision_no" : test.meta.data["revision_no"],
		"tags" :  test.meta.data["tags"],
		"type" : "application/bitwig-preset"
	})

	preset.contents.clean()


	test.export('output/clip json.bwclip')
	test.write('output/clip.bwclip')
	#test.export('output/proj json.bwproject')
	#test.write('output/proj.bwproject')
	#preset.write('output/preset.bwpreset')
	#preset.export('output/preset json.bwpreset')
