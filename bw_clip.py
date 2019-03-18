from pytwig import bw_obj

DEFAULT_NOTE_LENGTH = 0.5

class Clip(bw_obj.BW_Object): #abstract
	def set_duration(self, length):
		length = float(length)
		self.set(38, length)
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
		self.set(648, bw_obj.BW_Object(191))
		self.get(648).set(1180, bw_obj.BW_Object(1740))
		self.set_duration(length)

	def set_duration(self, length):
		length = float(length)
		self.set(38, length)
		end = self.get(648).get(2447).get(2444).get(687) + length
		self.get(648).get(2447).get(2445).set(687, end)
		return self

	def add_note(self, key, pos, dur = None, vel = 100):
		if dur == None:
			dur = DEFAULT_NOTE_LENGTH
		note = Note().set_pos(pos).set_dur(dur).set_vel(vel)
		for each_key in self.get(648).get(1180).get(6347):
			if key == each_key.get(238):
				each_key.get(543).append(note)
				return
		self.get(648).get(1180).get(6347).append(bw_obj.BW_Object(66).set(238, key))
		self.get(648).get(1180).get(6347)[-1].get(543).append(note)

class Note(bw_obj.BW_Object):
	def __init__(self):
		super().__init__(classnum = 102)
		content_timeline = bw_obj.BW_Object(41)
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
