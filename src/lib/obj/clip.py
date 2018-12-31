from src.lib.obj import bwobj
from src.lib import bwfile

DEFAULT_NOTE_LENGTH = 0.5

class BW_Clip_File(bwfile.BW_File):
	def __init__(self):
		super().__init__('note-clip')
		document = bwobj.BW_Object(46)
		document.get("track_group(1245)").get("main_tracks(1246)").append(bwobj.BW_Object(144))
		self.contents = bwobj.BW_Object("clip_document(479)").set("document(2409)", document)

	def set_clip(self, clip):
		self.contents.get(2409).get(1245).get(1246)[0].get(350).get(561)[0].set(576, clip)

	def set_meta(self):
		self.meta.data['beat_length'] = 1.0

class Clip(bwobj.BW_Object): #abstract
	def set_duration(self, length):
		length = float(length)
		self.set(38, length)
		try:
			end = self.get(648).get(2447).get(2444).get(687) + length
			self.get(648).get(2447).get(2445).set(687, end)
		except:
			pass
		return self

	def set_loop(self, enable = None, length = None):
		if enable != None:
			self.get(648).get(2447).set(2449, enable)
		if length != None:
			self.get(648).get(2447).get(2450).set(38, float(length))
		return self

class Note_Clip(Clip):
	def __init__(self, length = 4):
		super().__init__(classnum = 71)
		self.set(648, bwobj.BW_Object(191))
		self.get(648).set(1180, bwobj.BW_Object(1740))
		self.set_duration(length)

	def add_note(self, key, pos, dur = None, vel = 100):
		if dur == None:
			dur = DEFAULT_NOTE_LENGTH
		note = Note().set_pos(pos).set_dur(dur).set_vel(vel)
		for each_key in self.get(648).get(1180).get(6347):
			if key == each_key.get(238):
				each_key.get(543).append(note)
				return
		self.get(648).get(1180).get(6347).append(bwobj.BW_Object(66).set(238, key))
		self.get(648).get(1180).get(6347)[-1].get(543).append(note)

class Note(bwobj.BW_Object):
	def __init__(self):
		super().__init__(classnum = 102)
		content_timeline = bwobj.BW_Object(41)
		self.set(6288, content_timeline)
		self.set(648, content_timeline)

	def set_pos(self, pos):
		self.set(687, float(pos))
		return self
	def set_dur(self, dur):
		self.set(38, float(dur))
		return self
	def set_key(self, key):
		#self.set(238, int(key))
		return self
	def set_vel(self, vel, rising_falling = 'rf'):
		if isinstance(vel, int):
			if vel > 127:
				vel = 127
			vel = float(vel)/127.0
		if 'r' in rising_falling:
			self.set(239, vel)
		if 'f' in rising_falling:
			self.set(240, vel)
		return self
