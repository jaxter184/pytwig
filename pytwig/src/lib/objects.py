# Class declarations of filetypes like devices and clips.
# Some content taken from stylemistake's Bitwig modulator stuff https://github.com/stylemistake

from collections import OrderedDict
from src.lib import util, atoms
from src.lib.luts import typeLists
import uuid
import struct

idCount = 0
## Serializes all device atoms

class BW_File:
	def __init__():
		print("this class should not be initialized")

	def read():
		print("TODO: read files")

BW_VERSION = '2.4'

class BW_Meta(atoms.Atom):
	def __init__(self, name = '', type = '', uuid = '41be8f3a-6d24-4442-9508-8548dbe62d47'):
    	self.classname = 'meta'
        # Default headers
        if (type == 'application/bitwig-device'):
    		self.data = {
                'application_version_name': BW_VERSION,
                'branch': 'releases',
                'comment': '',
                'creator': 'Bitwig', # If it works, change this to 'Unknown'
                'device_category': 'Unknown',
                'device_description' : '',
                'device_id' : uuid,
                'device_name' : primary,
                'revision_id' : '4eab62ea750680f05a8515dd06615fa3efab6c0f', # Find out what this can be
                'revision_no' : 53807, # Find out what this can be
                'tags' : '',
                'type' : 'application/bitwig-device'

                'device_type' : 'audio_to_audio', # If it works, change this to ''
                'device_uuid' : uuid,

                # TODO: find out what these do
                'has_audio_input' : False,
                'has_audio_output' : False,
                'has_note_input' : False,
                'has_note_output' : False,
                'suggest_for_audio_input' : True,
                'suggest_for_note_input' : True,
            }
        elif (type == 'application/bitwig-modulator'):
    		self.data = {
                'application_version_name': BW_VERSION,
                'branch': 'releases',
                'comment': '',
                'creator': 'Bitwig', # If it works, change this to 'Unknown'
                'device_category': 'Unknown',
        		'device_id' : 'modulator:' + uuid,
        		'device_name' : primary,
        		'revision_id' : '70ff9163e17adee5a5bec0966115c2d1db31d9d3',
        		'revision_no' : 69110,
        		'tags' : '',
        		'type' : 'application/bitwig-modulator'

        		'device_description' : '',
        		'device_uuid' : uuid,
        		'is_polyphonic' : False,
    		}
        elif (type == 'application/bitwig-preset'):
    		self.data = {
                'application_version_name': BW_VERSION,
                'branch': 'releases',
                'comment': '',
                'creator': 'Bitwig', # If it works, change this to 'Unknown'
                'device_category': 'Unknown',
                'device_id' : uuid,
                'device_name' : primary,
                'revision_id' : '7e2a6b1f43653ded07446c597894d45b0c562940',
                'revision_no' : 43068,
                'tags' : '',
                'type' : 'application/bitwig-preset'

                'device_creator' : '',
                'device_type' : 'audio_to_audio', # If it works, change this to ''
                'preset_category' : 'Unknown',
                'referenced_device_ids' : [],
                'referenced_packaged_file_ids' : [],
    		}
        else:
            raise TypeError('Type "' + type + '" is an invalid header type')

    def read_header(self, text_data):
		if primary[:4] == 'BtWg' and primary[4:40].isdigit():
			# Interpreted header
	        if not (primary[:4] == 'BtWg' and primary[4:40].isdigit()):
	            raise TypeError('Text data ' + primary[:40] + ' is not a valid header')
        # Interpreted header

class Device(BW_File):

	classname = 'Device'

	def __init__(self, name, description = '', type = '', tags = ''):
		self.metadata = Meta(type = 'application/bitwig-device');

	def __str__(self): #just some debugging tools -jaxter184
		#return self.stringify(0)
		#return self.listFields()
		return self.classname + ": " +  self.metadata['device_name']

class Device_Contents(atoms.Atom):
	def __init__(self, name, description = '', type = '', tags = ''):
		self.classname = 'float_core.device_contents(151)'

class Modulator(BW_File):

	classname = 'float_core.modulator_contents'

	def __init__(self, name, description = 'Custom modulator',
			header = 'BtWg000100010088000015e50000000000000000'):
		self.fields = OrderedDict([
			('settings', None),
			('child_components', []),
			('panels', []),
			('proxy_in_ports', []),
			('proxy_out_ports', []),
			('fft_order', 0),
			('context_menu_panel', None),
			('device_UUID', '6146bcd7-f813-44c6-96e5-2e9d77093a81'),
			('device_name', name),
			('description', description),
			('creator', 'Bitwig'),
			('comment', ''),
			('keywords', ''),
			('category', 'Control'),
			('has_been_modified', True),
			('detail_panel', None),
			('can_be_polyphonic', True),
			('should_be_polyphonic_by_default', False),
			('should_enable_perform_mode_by_default', False)
		])
		self.meta = Meta(name, description, 'application/bitwig-modulator')
		self.header = header
		self.set_uuid(util.uuid_from_text(name))

	def add_component(self, atom):
		self.fields['child_components'].append(atom)
		return self

	def add_panel(self, atom):
		self.fields['panels'].append(atom)
		return self

	def add_proxy_in(self, atom): #should be consolidated with "add_component"
		self.fields['proxy_in_ports'].append(atom)
		return self

	def add_proxy_out(self, atom): #should be consolidated with "add_component"
		self.fields['proxy_out_ports'].append(atom)
		return self

	def set_description(self, value):
		self.meta.fields['device_description'] = value
		self.fields['description'] = value
		return self

	def set_uuid(self, value):
		self.meta.fields['device_uuid'] = value
		self.meta.fields['device_id'] = 'modulator:' + value
		self.fields['device_UUID'] = value
		return self

	def serialize(self):
		return util.serialize_bitwig_device(OrderedDict([
			('header', self.header),
			('meta', serialize(self.meta)),
			('contents', serialize(self))
		]))
