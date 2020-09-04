import sd
from sd.api.sdbasetypes import float2, float4, ColorRGBA
from sd.api.sdproperty import SDPropertyCategory, SDPropertyInheritanceMethod
from sd.api.sdvaluecolorrgba import SDValueColorRGBA
from sd.api.sdvalueenum import SDValueEnum
from sd.api.sdvaluefloat4 import SDValueFloat4

GRAYSCALE_CONVERT = "sbs::compositing::grayscaleconversion"
UNIFORM_COLOR = "sbs::compositing::uniform"
TRANSFORM = "sbs::compositing::transformation"

def get_graph():
	ctx = sd.getContext()
	app = ctx.getSDApplication()
	uiMgr = app.getQtForPythonUIMgr()
	graph = uiMgr.getCurrentGraph()
	return graph

def create_white_grayscale(graph):
	blank = graph.newNode(UNIFORM_COLOR)
	gc = graph.newNode(GRAYSCALE_CONVERT)
	gc.setPosition(float2(blank.getPosition().x + 150, blank.getPosition().y + 0))
	blankOutput = blank.getProperties(SDPropertyCategory.Output)[0]
	color = blank.getProperties(SDPropertyCategory.Input)[7]
	blank.setPropertyValue(color, SDValueColorRGBA.sNew(ColorRGBA(1, 1, 1, 1)))
	gcInput = gc.getProperties(SDPropertyCategory.Input)[9]
	blank.newPropertyConnection(blankOutput, gc, gcInput)
	return gc

def transform(graph, node, matrix):
	transform = graph.newNode(TRANSFORM)
	transform.setPosition(float2(node.getPosition().x + 150, node.getPosition().y + 0))
	
	input = transform.getProperties(SDPropertyCategory.Input)[12]
	output = node.getProperties(SDPropertyCategory.Output)[0]
	node.newPropertyConnection(output, transform, input)
	
	tiling = transform.getProperties(SDPropertyCategory.Input)[4]
	transform.setPropertyInheritanceMethod(tiling, SDPropertyInheritanceMethod.Absolute)
	transform.setPropertyValue(tiling, SDValueEnum.sFromValue("sbs::compositing::tiling", 0))
	
	matrix_prop = transform.getProperties(SDPropertyCategory.Input)[6]
	print(matrix_prop.getType())
	transform.setPropertyValue(matrix_prop, matrix)

	return transform

def main():
	graph = get_graph()
	white = create_white_grayscale(graph)
	line = transform(graph, white, SDValueFloat4.sNew(float4(2, 0, 0, 2)))
	
main()
