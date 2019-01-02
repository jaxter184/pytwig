import pytwig.file as bwfile
import pytwig.object as bwobj

class BW_Preset_File(bwfile.BW_File):
	def __init__(self):
		super().__init__('preset')
		self.contents = bwobj.BW_Object(1377)

	def get_preset(self):
		return self.contents.get(5153)
