# Class declarations of atoms and references and special data types that only atoms use (modified from original)
# author: stylemistake https://github.com/stylemistake

from collections import OrderedDict
from src.lib import util
from src.lib.luts import typeLists
import uuid
import struct

id_count = 0
## Serializes all device atoms

def serialize(obj, state = None): # should this go somewhere else?
	if state == None:
		state = []
	if isinstance(obj, Atom):
		'''if obj in state:
			return {
				'object_ref': state.index(obj) + 1,
			}'''
		state.append(obj)
		try:
			obj.classname
		except AttributeError:
			return serialize(obj.data, state) #maybe not the best way to do this, feels a little hacky
		else:
			return OrderedDict([
				('class', obj.classname),
				('object_id', obj.id),
				('data', serialize(obj.data, state))
			])
	if isinstance(obj, list):
		return [serialize(x, state) for x in obj]
	if isinstance(obj, dict):
		result = OrderedDict()
		for i, value in obj.items():
			result[i] = serialize(value, state)
		return result
	if isinstance(obj, Reference):
		return obj.serialize()
	if isinstance(obj, Color):
		return serialize(obj.data, state)
	return obj

def resetId(): # geez this feels so hacky -jaxter184
	global id_count
	id_count = 0

class Atom:
	# classname
	# data
	# classnum?

	def __init__(self, classname = '', fields = None,):
		global id_count
		if classname != None:
			self.classname = classname
		if fields != None:
			self.data = fields
		else:
			self.data = OrderedDict([])
		self.id = id_count #might need to make a manual override for id number
		id_count+=1

	def __str__(self):
		return "Atom: " +  str(self.classname) + '>'

	def setID(self, id):
		self.id = id

	# removed: def stringify(self, tabs = 0):

	def listFields(self):
		output = ''
		output += "class : " +  str(self.classname) + '\n'
		for each_field in self.data:
			output += each_field + '\n'
		return output

	def extractNum(self, text = None):
		if text == None:
			text = self.classname
		if text[-1:] == ')':
			start = len(text)-1
			end = start
			while text[start] != '(':
				start-=1
			return int(str(text[start+1:end]))
		else:
			return text

	def encodeField(self, output, field):
		value = self.data[field]
		fieldNum = self.extractNum(field)
		if value==None:
			output += bytearray.fromhex('0a')
			#print("none")
		else:
			#print(typeLists.fieldList[fieldNum])
			#print(value)
			if fieldNum in typeLists.fieldList:
				if typeLists.fieldList[fieldNum] == 0x01:
					if value <= 127 and value >= -128:
						output += bytearray.fromhex('01')
						if value < 0:
							#print(hex(0xFF + value + 1)[2:])
							output += bytearray.fromhex(hex(0xFF + value + 1)[2:])
						else:
							output += util.hexPad(value, 2)
					elif value <= 32767 and value >= -32768:
						output += bytearray.fromhex('02')
						if value < 0:
							#print(value)
							#print(hex((value + (1 << 4)) % (1 << 4)))
							output += bytearray.fromhex(hex(0xFFFF + value + 1)[2:])
						else:
							output += util.hexPad(value, 4)
					elif value <= 2147483647 and value >= -2147483648:
						output += bytearray.fromhex('03')
						if value < 0:
							output += bytearray.fromhex(hex(0xFFFFFFFF + value + 1)[2:])
						else:
							output += util.hexPad(value, 8)
				elif typeLists.fieldList[fieldNum] == 0x05:
					output += bytearray.fromhex('05')
					output += bytearray.fromhex('01' if value else '00')
				elif typeLists.fieldList[fieldNum] == 0x06:
					flVal = struct.unpack('<I', struct.pack('<f', value))[0]
					output += bytearray.fromhex('06')
					output += util.hexPad(flVal,8)
				elif typeLists.fieldList[fieldNum] == 0x07:
					dbVal = struct.unpack('<Q', struct.pack('<d', value))[0]
					output += bytearray.fromhex('07')
					output += util.hexPad(dbVal,16)
				elif typeLists.fieldList[fieldNum] == 0x08:
					output += bytearray.fromhex('08')
					value = value.replace('\\n', '\n')
					try: value.encode("ascii")
					except UnicodeEncodeError:
						output += bytearray.fromhex(hex(0x80000000 + len(value))[2:])
						output.extend(value.encode('utf-16be'))
					else:
						output += util.hexPad(len(value), 8)
						output.extend(value.encode('utf-8'))
				elif typeLists.fieldList[fieldNum] == 0x09:
					if type(value) == Reference:
						output += bytearray.fromhex('0b')
						output += value.encode()
					elif type(value) == Atom:
						output += bytearray.fromhex('09')
						output += value.encode()
					elif type(value) == NoneType:
						output += bytearray.fromhex('0a')
				elif typeLists.fieldList[fieldNum] == 0x12:
					output += bytearray.fromhex('12')
					for item in value:
						if type(item) == Atom:
							output += item.encode()
						elif type(item) ==  Reference:
							output += bytearray.fromhex('00000001')
							output += item.encode()
						else:
							print("something went wrong in atoms.py. \'not object list\'")
					output += bytearray.fromhex('00000003')
				elif typeLists.fieldList[fieldNum] == 0x14:
					output += bytearray.fromhex('14')
					if '' in value["type"]:
						#print("empty string: this shouldnt happen in devices and presets")
						pass
					else:
						output += bytearray.fromhex('01')
						for key in value["data"]:
							output += util.hexPad(len(key), 8)
							output.extend(key.encode('utf-8'))
							output += value["data"][key].encode()
					output += bytearray.fromhex('00')
				elif typeLists.fieldList[fieldNum] == 0x15:
					output += bytearray.fromhex('15')
					placeholder = uuid.UUID(value)
					output.extend(placeholder.bytes)
				elif typeLists.fieldList[fieldNum] == 0x16:
					output += bytearray.fromhex('16')
					output += value.encode()
				elif typeLists.fieldList[fieldNum] == 0x17:
					output += bytearray.fromhex('17')
					output += util.hexPad(len(value), 8)
					for item in value:
						flVal = hex(struct.unpack('<I', struct.pack('<f', item))[0])[2:]
						output += util.hexPad(flVal,8)
				elif typeLists.fieldList[fieldNum] == 0x19: #string array
					output += bytearray.fromhex('19')
					output += util.hexPad(len(value), 8)
					for i in value:
						i = i.replace('\\n', '\n')
						output += util.hexPad(len(i), 8)
						output.extend(i.encode('utf-8'))
				else:
					if typeLists.fieldList[fieldNum] == None:
						#print("atoms.py: 'None' in atom encoder. obj: " + str(fieldNum)) #temporarily disabling this error warning because i have no clue what any of these fields are
						pass
					else:
						print("jaxter stop being a lazy nerd and " + hex(typeLists.fieldList[fieldNum]) + " to the atom encoder. obj: " + str(fieldNum))
			else:
				print("missing type in typeLists.fieldList: " + str(fieldNum))
		return output

	def encode(self):
		output = bytearray(b'')
		if self.classname == 'meta':
			output += bytearray.fromhex('00000004')
			output += bytearray.fromhex('00000004')
			output.extend('meta'.encode('utf-8'))
			for each_field in self.data:
				output += bytearray.fromhex('00000001')
				output += util.hexPad(len(each_field), 8)
				output.extend(data.encode('utf-8'))
				output = self.encodeField(output, each_field)
			output += bytearray.fromhex('00000000')
		else:
			output += util.hexPad(self.extractNum(),8)
			for each_field in self.data:
				output += util.hexPad(self.extractNum(each_field),8)
				output = self.encodeField(output, each_field)
			output += bytearray.fromhex('00000000')
		return output

	def add_inport(self, atom):
		self.data['settings'].add_connection(InportConnection(atom))
		return self

	def add_field(self, field, value): #need this to be able to add fields, making this a simpler format -jaxter184
		self.data[field] = value

	def set_fields(self, fields): #for replacing the entire set of fields. maybe unnecessary.
		self.data = fields

class Reference:
	def __init__(self, id = 0):
		self.id = id

	def __str__(self):
		return "<Reference: " + str(self.id) + '>'

	def setID(self, id):
		self.id = id

	def serialize(self):
		return {'object_ref': self.id}

	def encode(self):
		output = bytearray(b'')
		output += util.hexPad(self.id,8)
		return output

class Color:
	def __init__(self, rd, gr, bl, al):
		self.data = {'type': "color", 'data': [rd, gr, bl, al]}
		if (al == 1.0):
			self.data['data'] = self.data['data'][:-1]

	def encode(self):
		output = bytearray(b'')
		count = 0
		for item in self.data["data"]:
			flVal = struct.unpack('<I', struct.pack('<f', item))[0]
			output += util.hexPad(flVal,8)
			count += 1
		if count == 3:
			output += struct.pack('<f', 1.0)
		return output

class AbstractValue(Atom):

   def __init__(self, name, default = None, tooltip = '', label = ''):
      self.data = OrderedDict([
         ('settings', Settings()),
         ('channel_count', 0),
         ('oversampling', 0),
         ('name', name),
         ('label', label),
         ('tooltip_text', tooltip),
         ('preset_identifier', name.upper()),
         ('modulations_to_ignore', 'MATH'),
         ('value_type', None),
         ('value', default)
      ])


class DecimalValue(AbstractValue):

   classname = 'float_core.decimal_value_atom'

   def __init__(self, name, default = 0, tooltip = '', label = '',
         min = -1, max = 1, unit = 0, step = -1, precision = -1):
      default = float(default)
      min = float(min)
      max = float(max)
      super().__init__(name, default, tooltip, label)
      self.data['value_type'] = Atom('float_core.decimal_value_type', OrderedDict([
         ('min', min),
         ('max', max),
         ('default_value', default),
         ('domain', 0),
         ('engine_domain', 0),
         ('value_origin', 0),
         ('pixel_step_size', step),
         ('unit', unit),
         ('decimal_digit_count', precision),
         ('edit_style', 0),
         ('parameter_smoothing', True),
         ('allow_automation_curves', True)
      ]))

   def set_range(self, min, max):
      self.data['value_type'].data['min'] = float(min)
      self.data['value_type'].data['max'] = float(max)
      return self

   def use_smoothing(self, smoothing = True):
      self.data['value_type'].data['parameter_smoothing'] = smoothing
      return self

   def set_decimal_digit_count(self, decimal_digit_count):
      self.data['value_type'].data['decimal_digit_count'] = decimal_digit_count
      return self

   def set_step(self, step):
      self.data['value_type'].data['pixel_step_size'] = step
      return self


class IndexedValue(AbstractValue):

   classname = 'float_core.indexed_value_atom'

   def __init__(self, name, default = 0, tooltip = '', label = '',
         items = []):
      super().__init__(name, default, tooltip, label)
      self.data['value_type'] = Atom('float_core.indexed_value_type', OrderedDict([
         ('items', []),
         ('edit_style', 0),
         ('columns', 0),
         ('default_value', default)
      ]))
      for x in items:
         self.add_item(x)

   def add_item(self, name):
      items = self.data['value_type'].data['items']
      seq_id = len(items)
      items.append(Atom('float_core.indexed_value_item', OrderedDict([
         ('id', seq_id),
         ('name', name)
      ])))
      return self


class Settings(Atom):

   classname = 'float_core.component_settings'

   def __init__(self):
      self.data = OrderedDict([
         ('desktop_settings', Atom('float_core.desktop_settings', OrderedDict([
            ('x', 0),
            ('y', 0),
            ('color', OrderedDict([
               ('type', 'color'),
               ('data', [ 0.5, 0.5, 0.5 ])
            ]))
         ]))),
         ('inport_connections', []),
         ('is_polyphonic', True)
      ])

   def add_connection(self, atom):
      self.data['inport_connections'].append(atom)
      return self


class InportConnection(Atom):

   classname = 'float_core.inport_connection'

   def __init__(self, atom = None):
      self.data = OrderedDict([
         ('source_component', atom),
         ('outport_index', 0),
         ('high_quality', True),
         ('unconnected_value', 0.0),
      ])

   def set_source(self, atom):
      self.source_component = atom
      return self


class Nitro(Atom):

   classname = 'float_common_atoms.nitro_atom'

   def __init__(self):
      self.data = OrderedDict([
         ('settings', Settings()),
         ('channel_count', 1),
         ('oversampling', 0),
         ('code', None),
         ('fft_order', 0)
      ])

   def set_source_file(self, file):
      # TODO
      return self

   def set_source(self, code):
      self.data['code'] = code
      return self


class ModulationSource(Atom):

   classname = 'float_core.modulation_source_atom'

   def __init__(self, name = ''):
      self.data = OrderedDict([
         ('settings', Settings()),
         ('channel_count', 1),
         ('oversampling', 0),
         ('name', name),
         ('preset_identifier', name.upper()),
         ('display_settings', OrderedDict([
            ('type', 'map<string,object>'),
            ('data', OrderedDict([
               ('abique', Atom('float_core.modulation_source_atom_display_settings', {
                  'is_source_expanded_in_inspector': False,
               })),
            ]))
         ]))
      ])


class PolyphonicObserver(Atom):

   classname = 'float_core.polyphonic_observer_atom'

   def __init__(self):
      self.data = OrderedDict([
         ('settings', Settings()),
         ('channel_count', 1),
         ('oversampling', 0),
         ('dimensions', 1)
      ])


class AbstractPanel(Atom):

   def __init__(self, tooltip = ''):
      self.data = OrderedDict([
         ('layout_settings', None),
         ('is_visible', True),
         ('is_enabled', True),
         ('tooltip_text', tooltip)
      ])

   def set_tooltip(self, text):
      self.data['tooltip_text'] = text
      return self


class AbstractPanelItem(AbstractPanel):

   def __init__(self, tooltip = '', x = 0, y = 0, width = 17, height = 4):
      super().__init__(tooltip)
      self.data['layout_settings'] = Atom('float_core.grid_panel_item_layout_settings', OrderedDict([
         ('width', width),
         ('height', height),
         ('x', x),
         ('y', y)
      ]))

   def set_size(self, width, height):
      self.data['layout_settings'].data['width'] = width
      self.data['layout_settings'].data['height'] = height
      return self

   def set_position(self, x, y):
      self.data['layout_settings'].data['x'] = x
      self.data['layout_settings'].data['y'] = y
      return self

   def set_model(self, atom):
      self.data['data_model'] = model
      return self


class Panel(AbstractPanel):

   classname = 'float_core.panel'

   def __init__(self, root_item, width = 17, height = 17, name = 'Main',
         tooltip = ''):
      super().__init__(tooltip)
      self.data['root_item'] = root_item
      self.data['name'] = name
      self.data['width'] = width
      self.data['height'] = height
      self.data['expressions'] = []


class GridPanel(AbstractPanel):

   classname = 'float_core.grid_panel_item'

   def __init__(self, tooltip = '', title = ''):
      super().__init__(tooltip)
      self.data['items'] = []
      self.data['border_style'] = 1
      self.data['title'] = title
      self.data['show_title'] = title != ''
      self.data['title_color'] = 6
      self.data['brightness'] = 0

   def add_item(self, atom):
      self.data['items'].append(atom)
      return self


class MappingSourcePanelItem(AbstractPanelItem):

   classname = 'float_core.mapping_source_panel_item'

   def __init__(self, tooltip = '', x = 0, y = 0, width = 17, height = 4,
         model = None):
      super().__init__(tooltip, x, y, width, height)
      self.data['data_model'] = model
      self.data['title'] = ''
      self.data['filename'] = ''


class PopupChooserPanelItem(AbstractPanelItem):

   classname = 'float_core.popup_chooser_panel_item'

   def __init__(self, tooltip = '', x = 0, y = 0, width = 7, height = 4,
         model = None):
      super().__init__(tooltip, x, y, width, height)
      self.data['data_model'] = model
      self.data['label_style'] = 0
      self.data['style'] = 1


class KnobPanelItem(AbstractPanelItem):

   classname = 'float_core.knob_panel_item'

   def __init__(self, tooltip = '', x = 0, y = 0, width = 9, height = 7,
         model = None, size = 1, style = 0):
      super().__init__(tooltip, x, y, width, height)
      self.data['data_model'] = model
      self.data['title'] = ''
      self.data['knob_size'] = size
      self.data['knob_style'] = style
      self.data['label_color'] = 999
      self.data['pie_color'] = 999


class NumberFieldPanelItem(AbstractPanelItem):

   classname = 'float_core.number_field_panel_item'

   def __init__(self, tooltip = '', x = 0, y = 0, width = 13, height = 4,
         model = None, style = 0, show_value_bar = False):
      super().__init__(tooltip, x, y, width, height)
      self.data['data_model'] = model
      self.data['title'] = ''
      self.data['style'] = style
      self.data['show_value_bar'] = show_value_bar

   def with_value_bar(self):
      self.data['show_value_bar'] = True
      return self


class ProxyInPort(Atom):

   classname = 'float_core.proxy_in_port_component'

   def __init__(self, atom):
      self.data = OrderedDict([
         ('settings', Settings()),
         ('port', atom)
      ])


class AudioPort(Atom):

   classname = 'float_core.audio_port'

   def __init__(self):
      self.data = OrderedDict([
         ('name', ''),
         ('description', ''),
         ('decorated_name', ' Audio out (PARENT)'),
         ('is_inport', False),
         ('is_optional', False),
         ('exclude_from_graph', False),
         ('channel_count', 3)
      ])


class NotePort(Atom):

   classname = 'float_core.note_port'

   def __init__(self):
      self.data = OrderedDict([
         ('name', ''),
         ('description', ''),
         ('decorated_name', ' Note out'),
         ('is_inport', False),
         ('is_optional', False),
         ('exclude_from_graph', False)
      ])
