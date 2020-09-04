import sd
from sd.api.sdbasetypes import float2, float4, ColorRGBA
from sd.api.sdproperty import SDPropertyCategory
from sd.api.sdvaluecolorrgba import SDValueColorRGBA
from sd.api.sdvalueenum import SDValueEnum

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

def transform(graph, node):
	transform = graph.newNode(TRANSFORM)
	transform.setPosition(float2(node.getPosition().x + 150, node.getPosition().y + 0))
	
	input = transform.getProperties(SDPropertyCategory.Input)[12]
	output = node.getProperties(SDPropertyCategory.Output)[0]
	node.newPropertyConnection(output, transform, input)
	
	matrix = transform.getProperties(SDPropertyCategory.Input)[6]
	tiling = transform.getProperties(SDPropertyCategory.Input)[4]
	transform.setPropertyValue(tiling, SDValueEnum.sFromValue("sbs::compositing::tiling", 0))
	
	for i in range(0, len(transform.getProperties(SDPropertyCategory.Input))):
		print(i, transform.getProperties(SDPropertyCategory.Input)[i].getLabel())
	return transform

def main():
	graph = get_graph()
	white = create_white_grayscale(g)
	line = transform(graph, white)
	
main()
