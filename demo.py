import win32com.client
from functions import *
from pprint import pprint
import json

# Variables
aLayers = []
nCont = 1

pathFilePsd = 'C:/Users/sampe/Downloads/phycss/PSD/error1.psd'

photoshopApplication = win32com.client.Dispatch('Photoshop.Application')

document = photoshopApplication.Open(pathFilePsd)

# Opciones png
pngSaveOptions = win32com.client.Dispatch( 'Photoshop.PNGSaveOptions' )
pngSaveOptions.Interlaced = False

# Guardamos una imagen del archivo
document.SaveAs( "C:/Users/sampe/Downloads/phycss/out/0.png", pngSaveOptions, True, 3 )

treeLayers = treeLayers(document.Layers)
allLayers = allLayersOfTree(treeLayers)
treeLayersOfTree = treeLayersOfTree(treeLayers)

# Recorremos capas para ocultarlas y obtener informacion necesaria antes
for layer in allLayers:
    # Obtenemos informacion de la capa
    aLayers.append( getInfoLayerCss( photoshopApplication, layer ) )

    # Ocultamos
    layer.Visible = False


# Recorremos capas
for layer in allLayers:
    # Reseteamos
    aBoundMask = False

    # Hacemos que sea visible
    layer.Visible = True

    # Obtenemos padres para ver si estan en un grupo ponerlos visibles
    layerParent = layer
    while True:
        layerParent = layerParent.Parent

        if( layerParent.__class__.__name__ == "LayerSet" ):
            layerParent.Visible = True
        else:
            break;

    # Seleccionamos capa
    document.ActiveLayer = layer

    # Si tiene posicion bloqueado desbloqueamos para poder realizar el trim sin fallos
    if( document.ActiveLayer.PositionLocked ):
        document.ActiveLayer.IsBackgroundLayer = False
        document.ActiveLayer.PositionLocked = False

    # Si es una capa con mascara de recorte
    if layer.Grouped:
        nLayerMaskCheck = nCont

        while True:
            if allLayers[nLayerMaskCheck].Grouped:
                nLayerMaskCheck += 1
            else:
                break;

        # Obtenemos los limites de la capa mask
        aBoundMask = allLayers[nLayerMaskCheck].Bounds

    # Realizamos merge a las capas visibles por si tiene efectos etc
    # Creamos un grupo vacio para poder hacer el merge y la capa sera la nueva creada
    theGroup = document.LayerSets.Add()
    layer.Move( theGroup, 1 )
    document.MergeVisibleLayers()
    layer = document.ActiveLayer

    # Duplicamo la capa visible
    dupLayers( photoshopApplication )

    # Documento duplicado
    docDupPhotoshop = photoshopApplication.Documents.Item( 2 )

    # Cortamos si tiene mascara
    if aBoundMask != False:
        docDupPhotoshop.Crop( aBoundMask )
        aBoundDup = docDupPhotoshop.ActiveLayer.Bounds

    # Recortamos el documento a la capa visible
    docDupPhotoshop.Trim( 0, True, True, True, True )

    # Ancho y alto de la capa
    aLayers[nCont - 1]["info"]["height"] = docDupPhotoshop.Height
    aLayers[nCont - 1]["info"]["width"] = docDupPhotoshop.Width

    # Guardamos
    docDupPhotoshop.SaveAs( "C:/Users/sampe/Downloads/phycss/out/" + str( nCont ) + ".jpg", pngSaveOptions, True, 3 )
    photoshopApplication.ActiveDocument.Close( 2 );

    # Limites de la capa
    aBound = list( layer.Bounds )

    # Modificamos top left si la imagen al hacer trim es menor
    if aBoundMask != False:
        if aBound[2] > aBoundMask[2]:
            aBound[0] = aBoundMask[0] + aBoundDup[0]

        if aBound[0] < aBoundMask[0]:
            aBound[0] = aBoundMask[0]

        if( aBound[1] < aBoundMask[1] ):
            aBound[1] = aBoundMask[1] + aBoundDup[1]
        # photoshopApplication.ActiveDocument.Close( 2 );
        # exit()

    # Top left
    aLayers[nCont - 1]["info"]["top"] = aBound[1];
    aLayers[nCont - 1]["info"]["left"] = aBound[0];

    # Si no es una fuente anadimos alto y ancho al css
    if "font-size" not in aLayers[nCont - 1]['style']:
        aLayers[nCont - 1]["style"]["width"] = str( aLayers[nCont - 1]["info"]["width"] ) + "px"
        aLayers[nCont - 1]["style"]["height"] = str( aLayers[nCont - 1]["info"]["height"] ) + "px"

    # Hacemos que se oculte de nuevo
    layer.Visible = False

    # Aumentamos indice
    nCont += 1

# Cerramos
photoshopApplication.ActiveDocument.Close( 2 )
photoshopApplication.Quit()

# Guardamos en el archivo el json
fFile = open( "C:/Users/sampe/Downloads/phycss/out/parsed.json", "w" )
fFile.write( json.dumps( {"layers": aLayers, "tree": treeLayersOfTree} ) )
fFile.close()