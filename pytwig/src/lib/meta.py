BW_VERSION = '2.4'

class BW_Meta():
	def __init__(self, primary = '', type = '', uuid = '41be8f3a-6d24-4442-9508-8548dbe62d47'):
    	self.classname = 'meta'
        if primary[:4] == 'BtWg' and primary[4:40].isdigit():
            # Interpreted header
            self.read_header(primary)
        else:
            # Default headers
            if (type == 'application/bitwig-device'):
        		self.fields = {
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
        		self.fields = {
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
        		self.fields = {
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
        if not (primary[:4] == 'BtWg' and primary[4:40].isdigit()):
            raise TypeError('Text data ' + primary[:40] + ' is not a valid header')
        # Interpreted header
