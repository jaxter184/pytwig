from src.lib import bwfile, objects, atoms

# This script generates a Chain device

FROM_SCRATCH = False

if __name__ == "__main__":
	if not FROM_SCRATCH:
		test = bwfile.BW_File()
		test.read('input/Chain.bwdevice')
	else:
		test = bwfile.BW_File('application/bitwig-device')
		test.meta.set_multi({
			"additional_device_types" : 14,
			"branch" : "releases",
			"creator" : "Bitwig",
			"device_category" : "Container",
			"device_description" : "Serial device chain group",
			"device_id" : "c86d21fb-d544-4daf-a1bf-57de22aa320c",
			"device_name" : "Chain",
			"device_type" : "audio_to_audio",
			"device_uuid" : "c86d21fb-d544-4daf-a1bf-57de22aa320c",
			"revision_id" : "3d1c8d38993610c6bdcab8740056e00d95c95ced",
			"revision_no" : 71311,
			"suggest_for_audio_input" : True,
			"suggest_for_note_input" : True,
			"type" : "application/bitwig-device"
		})
		test.header = "BtWg0001000200960000168b0000000000000000"

		# Components
		test.contents = objects.Contents(151)

		mix_atom = test.contents.add_child(301).set_XY(0, 316)
		comp_atom = mix_atom.create_inport(1371, True).set_XY(2, 194)
		pxy_audio_in = comp_atom.create_inport(154, True).set_port("audio")
		mult_atom = mix_atom.create_inport(367, True).set(3154, True).set_XY(12, 136)
		nest_slot = mult_atom.create_inport(587, True)
		nest_slot.set(836, "DEVICE_CHAIN").set(2434, True).set(2435, True).set(5769, True).set(835, "CHAIN").set(2270, True).set(5361, True)
		nest_slot.get(6194).get(612).set(17, 12).set(18, 66)
		nest_slot.create_inport(pxy_audio_in, True)
		pxy_note_in = nest_slot.create_inport(154, True).set_port("note").set_XY(150, 0)

		gain_val = mult_atom.create_inport(289, True).set_XY(66, 50).set_multi({
		"name(374)": "Gain",
		"preset_identifier(701)": "GAIN",
		"allow_automation(7489)": True,
		"allow_modulation(7490)": True,
		})
		gain_val.set(702, atoms.Atom(123).set_multi({
		"min(292)": -24.0,
		"max(293)": 24.0,
		"domain(294)": 1,
		"value_origin(3014)": 2,
		"pixel_step_size(1988)": -1.0,
		"unit(296)": 2,
		"parameter_smoothing(4433)": True,
		"allow_automation_curves(4434)": True,
		}))

		mix_val = mix_atom.create_inport(289, True).set_XY(24, 226).set_multi({
		"name(374)": "Mix",
		"preset_identifier(701)": "MIX",
		"value(712)": 1.0,
		"allow_automation(7489)": True,
		"allow_modulation(7490)": True,
		})
		mix_val.set(702, atoms.Atom(123).set_multi({
		"min(292)": 0.0,
		"max(293)": 1.0,
		"default_value(891)": 1.0,
		"pixel_step_size(1988)": -1.0,
		"unit(296)": 1,
		"parameter_smoothing(4433)": True,
		"allow_automation_curves(4434)": True,
		}))

		test.contents.get(173).append(nest_slot)
		test.contents.get(173).append(comp_atom)
		test.contents.get(173).append(mult_atom)
		test.contents.get(173).append(gain_val)
		test.contents.get(173).append(mix_val)

		# Panels
		panel = test.contents.add_panel(1680).set(6211, "Main").set_WH(11, 53)
		root_panel_item = panel.set_root_item(1681).set(6226, None).set_multi({
		"title_color(6522)": 6,
		"brightness(6245)": 1,
		})
		display_panel = root_panel_item.create_item(1704).set_WH(11, 6).set("data_model(6220)", nest_slot)
		grid_panel = root_panel_item.create_item(1681).set_WH(11, 46).set_XY(0, 7).set_multi({
		"is_visible(6309)": True,
		"is_enabled(6310)": True,
		"border_style(6228)": 1,
		"title_color(6522)": 6,
		"brightness(6245)": 1,
		})

		gain_knob = grid_panel.create_item(1687).set_WH(11, 9).set_XY(0, 15).set_multi({
		"data_model(6220)": gain_val,
		"title(6241)": "Gain",
		"label_color(7056)": 999,
		"pie_color(7057)": 999,
		})
		mix_knob = grid_panel.create_item(1687).set_WH(11, 9).set_XY(0, 33).set_multi({
		"data_model(6220)": mix_val,
		"title(6241)": "Mix",
		"label_color(7056)": 999,
		"pie_color(7057)": 999,
		})

		# Proxy ports
		test.contents.get(177).append(pxy_audio_in)
		test.contents.get(177).append(pxy_note_in)
		pxy_audio_out = test.contents.add_proxy(50).set_XY(0,380)
		pxy_audio_out.create_inport(mix_atom, True)
		pxy_audio_out.set_port('audio')
		pxy_note_out = test.contents.add_proxy(50).set_XY(100,500)
		pxy_note_out.create_inport(nest_slot, True)
		pxy_note_out.get(6194).get(614)[-1].set(249, 1)
		pxy_note_out.get(6194).set("is_polyphonic(615)", True)
		pxy_note_out.set_port('note')

		# Contents data
		test.contents.set_multi({
		"polyphony(179)": 1,
		"sleep_level_threshold(1977)": -96.0,
		"sleep_level_timeout(1978)": 0.05,
		"suggest_for_note_input(4846)": True,
		"suggest_for_audio_input(4847)": True,
		"description(2057)": "Serial device chain group",
		"has_been_modified(392)": True,
		"device_UUID(385)": "c86d21fb-d544-4daf-a1bf-57de22aa320c",
		"device_name(386)": "Chain",
		"creator(387)": "Bitwig",
		"category(390)": "Container",
		})

	if FROM_SCRATCH:
		test.export("output/Chain Clone Json.bwdevice")
		test.write("output/Chain Clone.bwdevice")
	else:
		test.export("output/Chain Dup Json.bwdevice")
		test.write("output/Chain Dup.bwdevice")
