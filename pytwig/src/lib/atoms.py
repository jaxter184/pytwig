# Class declarations of atoms and references and special data types that only atoms use (modified from original)
# author: stylemistake https://github.com/stylemistake

from collections import OrderedDict
from src.lib import util, objects
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

class Reference(objects.Abstract_BW_Object):
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

class Color(objects.Abstract_BW_Object):
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

class Atom(objects.BW_Object):
	# removed: def add_field(self, field, value): # wow I was dumb a year ago. This is totally unnecessary.

	# component, panel, proxy_in, proxy_out
	def add_atom_to_list(self, list_name, atom):
		if not isinstance(atom, atoms.Atom):
			raise TypeError("Object " + atom + " is not an atom")
		if not list_name in self.data:
			raise TypeError("List " + list_name + " does not exist in " + self.__str__())
		if not isinstance(self.data[list_name], List): # TODO: check to make sure the list is an atom list using typeLists.field_type_list
			raise TypeError(list_name + " is not a list of atoms")
		self.data[list_name].append(atom)
		return self

	def serialize(self):
		return json.dumps(self.data, indent = 2)

class Device_Contents(Atom):

	classname = 'float_core.device_contents(151)'

	def __init__(self, name = '', description = '', type = '', tags = ''):
		self.data = OrderedDict([
			('settings(6194)', None),
			('child_components(173)', []),
			('panels(6213)', []),
			('proxy_in_ports(177)', []),
			('proxy_out_ports(178)', []),
			('fft_order(6566)', 0),
			('context_menu_panel(6834)', None),
			("polyphony(179)", 1), # double quotes are things that arent in Modulator_Contents
			("sleep_level_threshold(1977)", -96.0),
			("sleep_level_timeout(1978)", 0.05),
			('device_UUID(385)', '6146bcd7-f813-44c6-96e5-2e9d77093a81'),
			('device_name(386)', name),
			('description(2057)', description),
			('creator(387)', 'Bitwig'),
			('comment(388)', ''),
			('keywords(389)', ''),
			('category(390)', 'Control'),
			("device_type(391)", 0),
			("suggest_for_note_input(4846)", false),
			("suggest_for_audio_input(4847)", true),
			('has_been_modified', True),
			("color_tint(6384)", 0),
			("header_area_panel(6417)", null)
		])

	# component, panel, proxy_in, proxy_out
	def add_atom_to_list(self, list_name, atom):
		if not isinstance(atom, atoms.Atom):
			raise TypeError("Object " + atom + " is not an atom")
		if not list_name in self.data:
			raise TypeError("List " + list_name + " does not exist in " + self.__str__())
		if not isinstance(self.data[list_name], List): # TODO: check to make sure the list is an atom list using typeLists.field_type_list
			raise TypeError(list_name + " is not a list of atoms")
		self.data[list_name].append(atom)
		return self

class Modulator_Contents(Atom):

	classname = 'float_core.modulator_contents'

	def __init__(self, name, description = ''):
		self.data = OrderedDict([
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
			('should_enable_perform_mode_by_default', False),
		])

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

	def add_inport_connection(self, atom):
		self.add_atom_to_list('inport_connection', InportConnection(atom))
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
