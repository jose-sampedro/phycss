import win32com.client

pathFilePsd = 'C:/Users/sampe/Downloads/phycss/PSD/error1.psd'


def treeLayers(layers, aTreeLayers = []):
    for layer in layers:
        if layer.LayerType == 1:
            aTreeLayers.append({'name': layer.Name, 'layer': layer})
        else:
            aAux = []
            treeLayers(layer.Layers, aAux)
            aTreeLayers.append({'name': layer.Name, 'layer': layer, 'layers': aAux})

    return aTreeLayers


photoshopApplication = win32com.client.Dispatch('Photoshop.Application')

document = photoshopApplication.Open(pathFilePsd)

aTreeLayers = treeLayers(document.Layers)

print(aTreeLayers)