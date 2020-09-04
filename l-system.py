import math

import sd
from sd.api.sdbasetypes import float2, float4, ColorRGBA
from sd.api.sdproperty import SDPropertyCategory, SDPropertyInheritanceMethod
from sd.api.sdvaluecolorrgba import SDValueColorRGBA
from sd.api.sdvalueenum import SDValueEnum
from sd.api.sdvaluefloat2 import SDValueFloat2
from sd.api.sdvaluefloat4 import SDValueFloat4

GRAYSCALE_CONVERT = "sbs::compositing::grayscaleconversion"
UNIFORM_COLOR = "sbs::compositing::uniform"
TRANSFORM = "sbs::compositing::transformation"
BLEND = "sbs::compositing::blend"
DOT_NODE = "sbs::compositing::passthrough"

class SDUtil:

	def __init__(self):
		ctx = sd.getContext()
		app = ctx.getSDApplication()
		uiMgr = app.getQtForPythonUIMgr()
		self.graph = uiMgr.getCurrentGraph()

	def create_grayscale(self, value, pos: float2):
		blank = self.graph.newNode(UNIFORM_COLOR)
		blank.setPosition(pos)
		gc = self.graph.newNode(GRAYSCALE_CONVERT)
		gc.setPosition(float2(blank.getPosition().x + 150, blank.getPosition().y + 0))
		blankOutput = blank.getProperties(SDPropertyCategory.Output)[0]
		color = blank.getProperties(SDPropertyCategory.Input)[7]
		blank.setPropertyValue(color, SDValueColorRGBA.sNew(ColorRGBA(value, value, value, 1)))
		gcInput = gc.getProperties(SDPropertyCategory.Input)[9]
		blank.newPropertyConnection(blankOutput, gc, gcInput)
		return gc

	def transform(self, graph_pos: float2, node, matrix: float4, offset: float2):
		transform = self.graph.newNode(TRANSFORM)
		transform.setPosition(graph_pos)

		input = transform.getProperties(SDPropertyCategory.Input)[12]
		output = node.getProperties(SDPropertyCategory.Output)[0]
		node.newPropertyConnection(output, transform, input)

		tiling = transform.getProperties(SDPropertyCategory.Input)[4]
		transform.setPropertyInheritanceMethod(tiling, SDPropertyInheritanceMethod.Absolute)
		transform.setPropertyValue(tiling, SDValueEnum.sFromValue("sbs::compositing::tiling", 0))

		matrix_prop = transform.getProperties(SDPropertyCategory.Input)[6]
		transform.setPropertyValue(matrix_prop, SDValueFloat4.sNew(matrix))

		offset_prop = transform.getProperties(SDPropertyCategory.Input)[7]
		transform.setPropertyValue(offset_prop, SDValueFloat2.sNew(offset))

		return transform

	def draw_line(self, graph_pos: float2, input_node, p1: float2, p2: float2, thickness):
		dist = math.sqrt((p2.x-p1.x)**2 + (p2.y-p1.y)**2)
		matrix = float4((p2.x - p1.x)/(dist*dist), (p2.y - p1.y)/(thickness*dist), -(p2.y - p1.y)/(dist*dist), (p2.x - p1.x)/(thickness*dist))
		line_no_offset = self.transform(graph_pos, input_node, matrix, float2(0, 0))
		line = self.transform(float2(graph_pos.x + 150, graph_pos.y), line_no_offset, float4(1, 0, 0, 1), float2(-((p1.x + p2.x)/2 - 0.5), (p1.y + p2.y)/2 - 0.5))
		return line

	def union(self, node1, node2):
		blend = self.graph.newNode(BLEND)

		input1 = blend.getProperties(SDPropertyCategory.Input)[12]
		output1 = node1.getProperties(SDPropertyCategory.Output)[0]
		node1.newPropertyConnection(output1, blend, input1)

		input2 = blend.getProperties(SDPropertyCategory.Input)[13]
		output2 = node2.getProperties(SDPropertyCategory.Output)[0]
		node2.newPropertyConnection(output2, blend, input2)

		blending_mode = blend.getProperties(SDPropertyCategory.Input)[8]
		blend.setPropertyValue(blending_mode, SDValueEnum.sFromValue("sbs::compositing::blendingmode", 5))

		blend.setPosition(float2(max(node1.getPosition().x, node2.getPosition().x) + 150, (node1.getPosition().y + node2.getPosition().y) / 2))

		return blend

	def dot_node(self, node):
		dot = self.graph.newNode(DOT_NODE)
		dot.setPosition(float2(node.getPosition().x + 150, node.getPosition().y))

		input = dot.getProperties(SDPropertyCategory.Input)[6]
		output = node.getProperties(SDPropertyCategory.Output)[0]

		node.newPropertyConnection(output, dot, input)

		return dot

class Rule:
	def __init__(self, var, expr):
		self.var = var
		self.expr = expr

class LSystem:

	def __init__(self, initiator, angle, *rules):
		self.state = initiator
		self.angle = angle
		self.current_angle = 0.0
		self.forward_dist = 0.1
		self.current_pos = float2(0.5, 0.5)
		self.rules = [self.__parse_rule(rule) for rule in rules]

	def __parse_rule(self, rule):
		# NOTE: rule must be of the form (var + "=" + expr) where var is a single char string
		return Rule(rule[0], rule[2:])

	def __render_command(self, util, command, line_input, current_image, graph_pos):
		if c == "F":
			line = util.draw_line(graph_pos, line_input, float2(0, 0), float2(1, 1), 0.01)
			return util.union(line, current_image)
		elif c == "f":
			pass
		elif c == "+":
			self.current_angle -= self.angle_change
		elif c == "-":
			self.current_angle += self.angle_change
		elif c == "[":
			# TODO push state
			pass
		elif c == "]":
			# TODO pop state
			pass
		else:
			raise ValueError("Invalid character: " + c)
			


	def render(self, graph_pos: float2):
			util = SDUtil()
			line_input = util.dot_node(util.create_grayscale(1, float2(0, 0)))
			bg = util.create_grayscale(0, float2(0, 0))
			current_image = bg
			for i in range(0, len(self.state)):
				c = self.state[i]
				new_image = self.__render_command(util, c, line_input, current_image, float2(450, i*150)
				if new_image is not None:
					current_image = new_image
			return current_image


def main():
	lsystem = LSystem("F-F-F-F", 90.0, "F=F-F+F+FF-F-F+F")
	lsystem.render(float2(0, 0))

main()
