import sd
from sd.api.sdbasetypes import float2, float4, ColorRGBA
from sd.api.sdproperty import SDPropertyCategory
from sd.api.sdvaluecolorrgba import SDValueColorRGBA

GRAYSCALE_CONVERT = "sbs::compositing::grayscaleconversion"
UNIFORM_COLOR = "sbs::compositing::uniform"

ctx = sd.getContext()
app = ctx.getSDApplication()
uiMgr = app.getQtForPythonUIMgr()
g = uiMgr.getCurrentGraph()
blank = g.newNode(UNIFORM_COLOR)
gc = g.newNode(GRAYSCALE_CONVERT)
gc.setPosition(float2(150, 0))
blankOutput = blank.getProperties(SDPropertyCategory.Output)[0]
color = blank.getProperties(SDPropertyCategory.Input)[7]
print(color.getType())
blank.setPropertyValue(color, SDValueColorRGBA.sNew(ColorRGBA(1, 1, 1, 1)))
gcInput = gc.getProperties(SDPropertyCategory.Input)[9]
print(blank.newPropertyConnection(blankOutput, gc, gcInput))
