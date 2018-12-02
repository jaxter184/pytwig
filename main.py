from src.lib import bwfile
from src.lib.luts import typeLists

chain_meta =  {
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
}

# This script generates a Chain device

if __name__ == "__main__":
	#test = objects.BW_File('application/bitwig-device')
	test = bwfile.BW_File()
	test.read('hidden/Chain.bwdevice')
	'''
	test = objects.BW_File('application/bitwig-device')
	for each_field in chain_meta:
		test.meta.set(each_field, chain_meta[each_field])
	test.header = "BtWg0001000200960000168b0000000000000000"

	# Components
	test.contents = atoms.Atom(151).set(6194, None)
	test.contents.get(173).append(atoms.Atom(301))
	mix_atom = test.contents.get(173)[-1]
	mix_atom.get(6194).get(612).set(18, 316)
	comp_atom = mix_atom.create_inport(1371, True)
	comp_atom.get(6194).get(612).set(17, 2).set(18, 194)
	pxy_audio_in = comp_atom.create_inport(154, True).set(301, objects.BW_Object(242).set(499, " Audio out (PARENT)").set(372, 3))
	mult_atom = mix_atom.create_inport(367, True).set(3154, True)
	mult_atom.get(6194).get(612).set(17, 12).set(18, 136)
	nest_slot = mult_atom.create_inport(587, True)
	nest_slot.set(836, "DEVICE_CHAIN").set(2434, True).set(2435, True).set(5769, True).set(835, "CHAIN").set(2270, True).set(5361, True)
	nest_slot.get(6194).get(612).set(17, 12).set(18, 66)
	nest_slot.create_inport(objects.Reference(pxy_audio_in), True)
	pxy_note_in = nest_slot.create_inport(154, True).set(301, objects.BW_Object(61).set(499, " Note out"))
	pxy_note_in.get(6194).get(612).set(17, 150)
	gain_val = mult_atom.create_inport(289, True).set(701, "GAIN").set(374, "Gain").set(7489, True).set(7490, True)
	gain_val.set(702,atoms.Atom(123).set(292, -24.0).set(293, 24.0).set(294, 1).set(3014, 2).set(1988, -1.0).set(296, 2).set(4433, True).set(4434, True))
	gain_val.get(6194).get(612).set(17, 66).set(18, 50)
	mix_val = mix_atom.create_inport(289, True)
	mix_val.set(701, "MIX").set(374, "Mix").set(7489, True).set(7490, True).set(712, 1.0)
	mix_val.set(702,atoms.Atom(123).set(292, 0.0).set(293, 1.0).set(891, 1.0).set(1988, -1.0).set(296, 1).set(4433, True).set(4434, True))
	mix_val.get(6194).get(612).set(17, 24).set(18, 226)

	test.contents.get(173).append(objects.Reference(nest_slot))
	test.contents.get(173).append(objects.Reference(comp_atom))
	test.contents.get(173).append(objects.Reference(mult_atom))
	test.contents.get(173).append(objects.Reference(gain_val))
	test.contents.get(173).append(objects.Reference(mix_val))

	# Panels
	test.contents.get(6213).append(panel_items.Panel_Item(1680).set(6226, None).set(6211, "Main").set(6232, 11).set(6233, 53))
	panel = test.contents.get(6213)[-1]
	root_panel_item = panel.create_item(1681).set(6226, None).set(6522, 6).set(6245, 1)
	display_panel = root_panel_item.create_item(1704).set(6220, objects.Reference(nest_slot))
	display_panel.get(6226).set(6217, 11).set(6218, 6)
	grid_panel = root_panel_item.create_item(1681).set(6309, True).set(6310, True).set(6228, 1).set(6522, 6).set(6245, 1)
	grid_panel.get(6226).set(6217, 11).set(6218, 46).set(6216, 7)
	gain_knob = grid_panel.create_item(1687).set(6220, objects.Reference(gain_val)).set(6241, "Gain").set(7056, 999).set(7057, 999)
	gain_knob.get(6226).set(6217, 11).set(6218, 9).set(6216, 15)
	mix_knob = grid_panel.create_item(1687).set(6220, objects.Reference(mix_val)).set(6241, "Mix").set(7056, 999).set(7057, 999)
	mix_knob.get(6226).set(6217, 11).set(6218, 9).set(6216, 33)

	# Proxy ports
	test.contents.get(177).append(objects.Reference(pxy_audio_in))
	test.contents.get(177).append(objects.Reference(pxy_note_in))

	pxy_audio_out = atoms.Atom(50)
	pxy_audio_out.get(6194).get(612).set(18, 380)
	pxy_audio_out.create_inport(objects.Reference(mix_atom), True)
	pxy_audio_out.set(301, objects.BW_Object(242).set(499, " Audio in (PARENT)").set(500, True).set(372, 3))
	pxy_note_out = atoms.Atom(50)
	pxy_note_out.get(6194).get(612).set(17, 100).set(18, 500)
	pxy_note_out.create_inport(objects.Reference(nest_slot), True)
	pxy_note_out.get(6194).get(614)[-1].set(249, 1)
	pxy_note_out.get(6194).set(615, True)
	pxy_note_out.set(301, objects.BW_Object(61).set(499, " Note in").set(500, True).set(372, 3))
	pxy_note_out.get(301).data.pop("channel_count(372)") # not sure why this is necessary

	test.contents.get(178).append(pxy_audio_out)
	test.contents.get(178).append(pxy_note_out)

	# Contents data
	test.contents.set(179, 1).set(1977, -96.0).set(1978, 0.05)
	test.contents.set(4846, True).set(4847, True).set(392, True)
	test.contents.set(386, "Chain").set(2057, "Serial device chain group").set(387, "Bitwig").set(390, "Container")
	test.contents.set(385, "c86d21fb-d544-4daf-a1bf-57de22aa320c")
	'''
	test.export("jsond")
	test.write("dsfah")
