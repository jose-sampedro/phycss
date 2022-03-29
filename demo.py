import win32com.client
from pprint import pprint

pathFilePsd = 'C:/Users/sampe/Downloads/phycss/PSD/error1.psd'


def treeLayers(layers, returnTreeLayers = []):
    for layer in layers:
        if layer.LayerType == 1:
            returnTreeLayers.append({'name': layer.Name, 'layer': layer})
        else:
            aAux = []
            treeLayers(layer.Layers, aAux)
            returnTreeLayers.append({'name': layer.Name, 'layer': layer, 'layers': aAux})

    return returnTreeLayers


def layersOfTree(aTreeLayers, aReturn = []):
    for layer in aTreeLayers:
        if 'layers' in layer:
            layersOfTree(layer['layers'], aReturn)
        else:
            aReturn.append(layer['layer'])

    return aReturn


def treeLayersOfTree(aTreeLayers, aReturn = []):
    for layer in aTreeLayers:
        if 'layers' in layer:
            aAux = []
            treeLayersOfTree(layer['layers'], aAux)
            aReturn.append({'name': layer['name'],
                           'visible': layer['layer'].Visible,
                           'layers': aAux})
        else:
            # Obtenemos el padre para poderlo visible para que sus capas hijas den la propiedad "visible" correctamente
            layerParent = layer['layer'].Parent

            # Si el padre es un grupo
            if layerParent.__class__.__name__ == 'LayerSet':
                bVisibleParent = layerParent.Visible
                layerParent.Visible = True

            # Insertamos capa
            aReturn.append({'name': layer['layer'].Name,
                           'visible': layer['layer'].Visible})

            # Si el padre es un grupo volvemos a como lo dejamos
            if layerParent.__class__.__name__ == 'LayerSet':
                layerParent.Visible = bVisibleParent

    return aReturn


photoshopApplication = win32com.client.Dispatch('Photoshop.Application')

document = photoshopApplication.Open(pathFilePsd)

treeLayers = treeLayers(document.Layers)
layersOfTree = layersOfTree(treeLayers)
treeLayersOfTree = treeLayersOfTree(treeLayers)

pprint(treeLayersOfTree)