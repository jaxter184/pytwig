# All classes regarding bitwig files
from src.lib import meta

# initialize by importing file info.
class BW_File:
    # in_file: A string of characters representing the
	def __init__(self, in_file = '',):
        self.header = in_file[:40]
        if self.header[:4] != 'BtWg':
            raise TypeError("Not a valid Bitwig file. Header does not start with 'BtWg'.")
        # TODO: verify header
        if header[11] == 2:
            # TODO: convert file
            pass
        elif header[11] == 1:
            raise TypeError("Bitwig File Type is JSON. PyTwig does not yet support it.")
        else:
        self.raw_input = in_file
        self.text_data = in_file

	def __str__(self):
        return filename

class BW_Device_File(BW_File):
    device_name = ''
    meta_object = null

    def __init__(self, in_file = ''):
