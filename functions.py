import win32com.client
import re

# Modos de fusion
aBlend = dict()
aBlend[22] = 'colorBlend'
aBlend[6] = 'colorBurn'
aBlend[10] = 'colorDodge'
aBlend[4] = 'darken'
aBlend[28] = 'darkerColor'
aBlend[18] = 'difference'
aBlend[3] = 'dissolve'
aBlend[30] = 'divide'
aBlend[19] = 'exclusion'
aBlend[14] = 'hardLight'
aBlend[26] = 'hardMix'
aBlend[20] = 'hue'
aBlend[8] = 'lighten'
aBlend[27] = 'lighterColor'
aBlend[7] = 'linearBurn'
aBlend[11] = 'linearDodge'
aBlend[16] = 'linearLight'
aBlend[23] = 'luminosity'
aBlend[5] = 'multiply'
aBlend[2] = 'normalBlend'
aBlend[12] = 'overlay'
aBlend[1] = 'passThrough'
aBlend[17] = 'pinLight'
aBlend[21] = 'saturationBlend'
aBlend[9] = 'screen'
aBlend[13] = 'softLight'
aBlend[29] = 'subtract'
aBlend[15] = 'vividLight'


def treeLayers(layers, returnTreeLayers = []):
    for layer in layers:
        if layer.LayerType == 1:
            returnTreeLayers.append({'name': layer.Name, 'layer': layer})
        else:
            aux = []
            treeLayers(layer.Layers, aux)
            returnTreeLayers.append({'name': layer.Name, 'layer': layer, 'layers': aux})

    return returnTreeLayers


def allLayersOfTree(aTreeLayers, returnLayers = []):
    for layer in aTreeLayers:
        if 'layers' in layer:
            allLayersOfTree(layer['layers'], returnLayers)
        else:
            returnLayers.append(layer['layer'])

    return returnLayers


def treeLayersOfTree(aTreeLayers, returnLayers = []):
    for layer in aTreeLayers:
        if 'layers' in layer:
            aux = []
            treeLayersOfTree(layer['layers'], aux)
            returnLayers.append({'name': layer['name'], 'visible': layer['layer'].Visible, 'layers': aux})
        else:
            # Obtenemos el padre para ponerlo visible para que sus capas hijas den la propiedad "visible" correctamente
            layerParent = layer['layer'].Parent

            # Si el padre es un grupo
            if layerParent.__class__.__name__ == 'LayerSet':
                bVisibleParent = layerParent.Visible
                layerParent.Visible = True

            # Insertamos capa
            returnLayers.append({'name': layer['layer'].Name, 'visible': layer['layer'].Visible})

            # Si el padre es un grupo volvemos a como lo dejamos
            if layerParent.__class__.__name__ == 'LayerSet':
                layerParent.Visible = bVisibleParent

    return returnLayers

def getInfoLayerCss(appPhotoshop, layer):
    # Variables
    aInfo = {'style': dict(), 'info': {'top': 0, 'left': 0, 'width': 0, 'height': 0, 'blend': aBlend[layer.BlendMode], 'display': layer.Visible, 'text': ''}}

    # Padre
    layerParent = layer

    # Si la capa esta visible, obtenemos padres para ver si mostrarla o no
    if layer.Visible == True:
        while True:
            layerParent = layerParent.Parent

            if layerParent.__class__.__name__ == 'LayerSet' and layerParent.Visible == False: 
                aInfo['info']['display'] = False
                break
            elif layerParent.__class__.__name__ == 'Document':
                break

    # Seleccionamos capa
    appPhotoshop.ActiveDocument.ActiveLayer = layer

    # Si es una capa vacia no podemos obtener nada
    if layer.Bounds[0] == 0 and layer.Bounds[1] == 0 and layer.Bounds[2] == 0 and layer.Bounds[3] == 0:
        aInfo['info']['display'] = False
        return aInfo

    # Ejecutamos script para obtener informacion
    sCss = appPhotoshop.DoJavaScriptFile('C:/Users/sampe/Downloads/phycss/getCSS.jsx')

    # Eliminamos
    sCss = re.sub('^.+{|}$|[\r\n\t]+', '', sCss)

    # Convertimos a array
    aCss = sCss.split(';')

    # Recorremos array
    for sCss in aCss:
        if sCss != '':
            aAux = sCss.strip().split(':')

            if aAux[0] not in ['position', 'left', 'top', 'z-index', 'width', 'height']:
                aInfo['style'][aAux[0]] = aAux[1]

    # Si contenemos font-size es una capa texto
    if 'font-size' in aInfo['style']:
        # Modificamos line-height
        aInfo['style']['line-height'] = aInfo['style']['font-size']

        # Insertamos el texto
        aInfo['info']['text'] = layer.TextItem.Contents

    # Retornamos
    return aInfo

def dupLayers(appPhotoshop):
    desc143 = win32com.client.Dispatch('Photoshop.ActionDescriptor')
    ref73 = win32com.client.Dispatch('Photoshop.ActionReference')
    ref74 = win32com.client.Dispatch('Photoshop.ActionReference')

    ref73.PutClass(appPhotoshop.CharIDToTypeID('Dcmn'))
    desc143.PutReference(appPhotoshop.CharIDToTypeID('null'), ref73)
    desc143.PutString(appPhotoshop.CharIDToTypeID('Nm  '),
                      appPhotoshop.ActiveDocument.ActiveLayer.Name)
    ref74.PutEnumerated(appPhotoshop.CharIDToTypeID('Lyr '),
                        appPhotoshop.CharIDToTypeID('Ordn'),
                        appPhotoshop.CharIDToTypeID('Trgt'))
    desc143.PutReference(appPhotoshop.CharIDToTypeID('Usng'), ref74)

    appPhotoshop.ExecuteAction(appPhotoshop.CharIDToTypeID('Mk  '),
                               desc143, 3)