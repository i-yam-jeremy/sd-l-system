import math

import sd
from PySide2 import QtWidgets
from sd.api.sdbasetypes import float2, float4, ColorRGBA
from sd.api.sdproperty import SDPropertyCategory
from sd.api.sdvaluefloat import SDValueFloat
from sd.api.sdvaluefloat2 import SDValueFloat2
from sd.api.sdvaluefloat4 import SDValueFloat4
from sd.api.sdvaluestring import SDValueString
from sd.api.sdvalueint import SDValueInt

MENU_NAME = "doc.lsystem.lsystem_menu"

CONST_FLOAT1 = "sbs::function::const_float1"
CONST_FLOAT2 = "sbs::function::const_float2"
CONST_FLOAT4 = "sbs::function::const_float4"
VECTOR2 = "sbs::function::vector2"
GET_FLOAT2 = "sbs::function::get_float2"
SWIZZLE1 = "sbs::function::swizzle1"
ADD = "sbs::function::add"
MUL = "sbs::function::mul"
DIV = "sbs::function::div"
ABS = "sbs::function::abs"
LESSTHAN = "sbs::function::lr"
AND = "sbs::function::and"
IFELSE = "sbs::function::ifelse"
DOT_PROD = "sbs::function::dot"
PIXEL_PROCESSOR = "sbs::compositing::pixelprocessor"

class SDUtil:

	def __init__(self):
		ctx = sd.getContext()
		app = ctx.getSDApplication()
		self.ui_mgr = app.getQtForPythonUIMgr()
		self.graph = self.ui_mgr.getCurrentGraph()

	def get_selected_lsystem_nodes(self):
		selection = self.ui_mgr.getCurrentGraphSelection()
		return [node for node in selection if node.getDefinition().getLabel() == "L-System"]

	def swizzle1(self, func_graph, node, component_index):
		swizzle = func_graph.newNode(SWIZZLE1)
		input = swizzle.getPropertyFromId('vector', SDPropertyCategory.Input)
		output = node.getProperties(SDPropertyCategory.Output)[0]
		node.newPropertyConnection(output, swizzle, input)

		component_prop = swizzle.getPropertyFromId('__constant__', SDPropertyCategory.Input)
		swizzle.setPropertyValue(component_prop, SDValueInt.sNew(component_index))

		return swizzle
	
	def vector2(self, func_graph, a, b):
		v = func_graph.newNode(VECTOR2)
		
		input1 = v.getPropertyFromId('componentsin', SDPropertyCategory.Input)
		output1 = a.getProperties(SDPropertyCategory.Output)[0]
		a.newPropertyConnection(output1, v, input1)
		
		input2 = v.getPropertyFromId('componentslast', SDPropertyCategory.Input)
		output2 = b.getProperties(SDPropertyCategory.Output)[0]
		b.newPropertyConnection(output2, v, input2)

		return v
			
	def const_float1(self, func_graph, value: float):
		node = func_graph.newNode(CONST_FLOAT1)
		value_prop = node.getPropertyFromId('__constant__', SDPropertyCategory.Input)
		node.setPropertyValue(value_prop, SDValueFloat.sNew(value))
		return node
	
	def const_float2(self, func_graph, value: float2):
		node = func_graph.newNode(CONST_FLOAT2)
		value_prop = node.getPropertyFromId('__constant__', SDPropertyCategory.Input)
		node.setPropertyValue(value_prop, SDValueFloat2.sNew(value))
		return node

	def get_current_pos(self, func_graph, graph_pos: float2):
		node = func_graph.newNode(GET_FLOAT2)
		prop = node.getPropertyFromId('__constant__', SDPropertyCategory.Input)
		node.setPropertyValue(prop, SDValueString.sNew("$pos"))
		return node

	def draw_line(self, func_graph, graph_pos: float2, p1: float2, p2: float2, thickness):
		f = func_graph
		segment_dist = self.const_float1(f, math.sqrt((p2.x-p1.x)**2 + (p2.y-p1.y)**2))
		constant = self.const_float1(f, p2.x*p1.y - p2.y*p1.x)
		pvec = self.const_float2(f, float2(p2.y-p1.y, -(p2.x-p1.x)))
		current_pos = self.get_current_pos(f, graph_pos)
		
		dist_to_line = self.div(f, self.abs(f, self.add(f, self.dot_prod(f, pvec, current_pos), constant)), segment_dist)
		
		current_x = self.swizzle1(f, current_pos, 0)
		
		return self.ifelse(f, 
		self.and_nodes(f,
			self.lessthan(f, dist_to_line, self.const_float1(f, thickness)),
			self.and_nodes(f, self.lessthan(f, self.const_float1(f, min(p1.x, p2.x)), current_x), self.lessthan(f, current_x, self.const_float1(f, max(p1.x, p2.x))))),
		self.const_float1(f, 1), 
		self.const_float1(f, 0))

	def ifelse(self, func_graph, condition_node, node1, node2):
		ifelse = func_graph.newNode(IFELSE)

		input = ifelse.getPropertyFromId('condition', SDPropertyCategory.Input)
		output = condition_node.getProperties(SDPropertyCategory.Output)[0]
		condition_node.newPropertyConnection(output, ifelse, input)

		input1 = ifelse.getPropertyFromId('ifpath', SDPropertyCategory.Input)
		output1 = node1.getProperties(SDPropertyCategory.Output)[0]
		node1.newPropertyConnection(output1, ifelse, input1)

		input2 = ifelse.getPropertyFromId('elsepath', SDPropertyCategory.Input)
		output2 = node2.getProperties(SDPropertyCategory.Output)[0]
		node2.newPropertyConnection(output2, ifelse, input2)

		ifelse.setPosition(float2(max(node1.getPosition().x, node2.getPosition().x) + 150, (node1.getPosition().y + node2.getPosition().y) / 2))

		return ifelse

	def and_nodes(self, func_graph, node1, node2):
		and_node = func_graph.newNode(AND)

		input1 = and_node.getPropertyFromId('a', SDPropertyCategory.Input)
		output1 = node1.getProperties(SDPropertyCategory.Output)[0]
		node1.newPropertyConnection(output1, and_node, input1)

		input2 = and_node.getPropertyFromId('b', SDPropertyCategory.Input)
		output2 = node2.getProperties(SDPropertyCategory.Output)[0]
		node2.newPropertyConnection(output2, and_node, input2)

		and_node.setPosition(float2(max(node1.getPosition().x, node2.getPosition().x) + 150, (node1.getPosition().y + node2.getPosition().y) / 2))

		return and_node

	def lessthan(self, func_graph, node1, node2):
		lt = func_graph.newNode(LESSTHAN)

		input1 = lt.getPropertyFromId('a', SDPropertyCategory.Input)
		output1 = node1.getProperties(SDPropertyCategory.Output)[0]
		node1.newPropertyConnection(output1, lt, input1)

		input2 = lt.getPropertyFromId('b', SDPropertyCategory.Input)
		output2 = node2.getProperties(SDPropertyCategory.Output)[0]
		node2.newPropertyConnection(output2, lt, input2)

		lt.setPosition(float2(max(node1.getPosition().x, node2.getPosition().x) + 150, (node1.getPosition().y + node2.getPosition().y) / 2))

		return lt
	
	def dot_prod(self, func_graph, node1, node2):
		dot_prod = func_graph.newNode(DOT_PROD)

		input1 = dot_prod.getPropertyFromId('a', SDPropertyCategory.Input)
		output1 = node1.getProperties(SDPropertyCategory.Output)[0]
		node1.newPropertyConnection(output1, dot_prod, input1)

		input2 = dot_prod.getPropertyFromId('b', SDPropertyCategory.Input)
		output2 = node2.getProperties(SDPropertyCategory.Output)[0]
		node2.newPropertyConnection(output2, dot_prod, input2)

		dot_prod.setPosition(float2(max(node1.getPosition().x, node2.getPosition().x) + 150, (node1.getPosition().y + node2.getPosition().y) / 2))

		return dot_prod

	def mul(self, func_graph, node1, node2):
		mul = func_graph.newNode(MUL)

		input1 = mul.getPropertyFromId('a', SDPropertyCategory.Input)
		output1 = node1.getProperties(SDPropertyCategory.Output)[0]
		node1.newPropertyConnection(output1, mul, input1)

		input2 = mul.getPropertyFromId('b', SDPropertyCategory.Input)
		output2 = node2.getProperties(SDPropertyCategory.Output)[0]
		node2.newPropertyConnection(output2, mul, input2)

		mul.setPosition(float2(max(node1.getPosition().x, node2.getPosition().x) + 150, (node1.getPosition().y + node2.getPosition().y) / 2))

		return mul
	
	def abs(self, func_graph, node):
		abs = func_graph.newNode(ABS)

		input = abs.getPropertyFromId('a', SDPropertyCategory.Input)
		output = node.getProperties(SDPropertyCategory.Output)[0]
		node.newPropertyConnection(output, abs, input)

		return abs
	
	def div(self, func_graph, node1, node2):
		div = func_graph.newNode(DIV)

		input1 = div.getPropertyFromId('a', SDPropertyCategory.Input)
		output1 = node1.getProperties(SDPropertyCategory.Output)[0]
		node1.newPropertyConnection(output1, div, input1)

		input2 = div.getPropertyFromId('b', SDPropertyCategory.Input)
		output2 = node2.getProperties(SDPropertyCategory.Output)[0]
		node2.newPropertyConnection(output2, div, input2)

		div.setPosition(float2(max(node1.getPosition().x, node2.getPosition().x) + 150, (node1.getPosition().y + node2.getPosition().y) / 2))

		return div

	def add(self, func_graph, node1, node2):
		add = func_graph.newNode(ADD)

		input1 = add.getPropertyFromId('a', SDPropertyCategory.Input)
		output1 = node1.getProperties(SDPropertyCategory.Output)[0]
		node1.newPropertyConnection(output1, add, input1)

		input2 = add.getPropertyFromId('b', SDPropertyCategory.Input)
		output2 = node2.getProperties(SDPropertyCategory.Output)[0]
		node2.newPropertyConnection(output2, add, input2)

		add.setPosition(float2(max(node1.getPosition().x, node2.getPosition().x) + 150, (node1.getPosition().y + node2.getPosition().y) / 2))

		return add

	def union(self, func_graph, node1, node2):
		return self.add(func_graph, node1, node2)
	
	def pixel_processor(self, graph_pos):
		node = self.graph.newNode(PIXEL_PROCESSOR)
		node.setPosition(graph_pos)
		return node

class Rule:
	def __init__(self, var, expr):
		self.var = var
		self.expr = expr

class TurtleState:
	def __init__(self, angle, pos, dist, thickness):
		self.angle = angle
		self.pos = pos
		self.dist = dist
		self.thickness = thickness
	def copy(self):
		return TurtleState(self.angle, self.pos, self.dist, self.thickness)

class LSystem:

	def __init__(self, initiator, angle_change, forward_dist, thickness, rules):
		self.state = initiator
		self.angle_change = angle_change
		self.turtle_state = TurtleState(0.0, float2(0.5, 0.5), forward_dist, thickness)
		self.turtle_states = []
		self.rules = [self.__parse_rule(rule) for rule in rules]

	def __parse_rule(self, rule):
		# NOTE: rule must be of the form (var + "=" + expr) where var is a single char string
		return Rule(rule[0], rule[2:])

	def iterate_generations(self, gen_count):
		for i in range(0, gen_count):
			self.state = self.__iterate_generation(self.state)

	def __iterate_generation(self, state):
		new_state = ""
		for c in state:
			matched_rule = False
			for rule in self.rules:
				if rule.var == c:
					new_state += rule.expr
					matched_rule = True
					break
			if not matched_rule:
				new_state += c
		return new_state


	def __render_command(self, util, func_graph, c, current_image, graph_pos):
		if c == "F":
			new_pos = float2(self.turtle_state.pos.x + self.turtle_state.dist*math.cos(math.pi/180 * self.turtle_state.angle), self.turtle_state.pos.y + self.turtle_state.dist*math.sin(math.pi/180 * self.turtle_state.angle))
			line = util.draw_line(func_graph, graph_pos, self.turtle_state.pos, new_pos, self.turtle_state.thickness)
			self.turtle_state.pos = new_pos
			return util.union(func_graph, line, current_image)
		elif c == "f":
			self.turtle_state.pos = float2(self.turtle_state.pos.x + self.turtle_state.dist*math.cos(math.pi/180 * self.turtle_state.angle), self.turtle_state.pos.y + self.turtle_state.dist*math.sin(math.pi/180 * self.turtle_state.angle))
		elif c == "+":
			self.turtle_state.angle -= self.angle_change
		elif c == "-":
			self.turtle_state.angle += self.angle_change
		elif c == "[":
			self.turtle_states.append(self.turtle_state.copy())
			pass
		elif c == "]":
			if len(self.turtle_states) >= 1:
				self.turtle_state = self.turtle_states.pop()
			else:
				raise ValueError("No states left to POP")
		else:
			raise ValueError("Invalid character: " + c)



	def render(self, util, graph_pos: float2):
			pixel_processor = util.pixel_processor(graph_pos)
			perpixel_prop = pixel_processor.getPropertyFromId('perpixel', SDPropertyCategory.Input)
			func_graph = pixel_processor.newPropertyGraph(perpixel_prop, 'SDSBSFunctionGraph')

			bg = util.const_float1(func_graph, 0)
			current_image = bg
			for i in range(0, len(self.state)):
				c = self.state[i]
				new_image = self.__render_command(util, func_graph, c, current_image, float2(450, i*100))
				if new_image is not None:
					current_image = new_image
			func_graph.setOutputNode(current_image, True)
			return pixel_processor

def convert_node_to_lsystem(node):
	props = node.getProperties(SDPropertyCategory.Input)
	initiator = node.getPropertyValue(props[6]).get()
	rules = node.getPropertyValue(props[7]).get()
	angle_change = node.getPropertyValue(props[8]).get()
	dist = node.getPropertyValue(props[9]).get()
	thickness = node.getPropertyValue(props[10]).get()
	generations = node.getPropertyValue(props[11]).get()
	lsystem = LSystem(initiator, angle_change, dist, thickness, rules.split("\n"))
	lsystem.iterate_generations(generations)
	return lsystem

def convert_selected_lsystem_nodes():
	util = SDUtil()
	nodes = util.get_selected_lsystem_nodes()
	for node in nodes:
		lsystem = convert_node_to_lsystem(node)
		lsystem.render(util, node.getPosition())

# Plugin entry point. Called by Designer when loading a plugin.
def initializeSDPlugin():
	app = sd.getContext().getSDApplication()
	uiMgr = app.getQtForPythonUIMgr()

	menu = uiMgr.newMenu(menuTitle="Lsystem", objectName=MENU_NAME)
	act = QtWidgets.QAction("Convert Selected", menu)
	act.triggered.connect(convert_selected_lsystem_nodes)

	menu.addAction(act)

# If this function is present in your plugin,
# it will be called by Designer when unloading the plugin.
def uninitializeSDPlugin():
	uiMgr.deleteMenu(MENU_NAME)

initializeSDPlugin()
