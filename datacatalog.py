import os.path
import xml.etree.ElementTree as ET

class DataCatalog:
    license_path = None
    license_key = None
    pxpoint_datasets = {}
    spatial_layers = {}
    pxpoint_root = None

    def __init__(self, path_to_data_catalog, pxse_dir):
        dc = ET.parse(path_to_data_catalog)

        # get license path and key
        license = dc.getroot().find('PxPointLicense')

        self.license_path = license.attrib['path']
        self.license_key = license.attrib['key']

        datasets = dc.getroot().find('PxPointDatasets')


        # get dataset paths
        dataset_iterator = iter(datasets)
        for dataset in dataset_iterator:
            dataset_path = dataset.attrib['URI'].replace('file:///$PXSEDIR', pxse_dir)
            self.pxpoint_datasets[dataset.attrib['Name']] = dataset_path

        if len(self.pxpoint_datasets) > 0:
            self.pxpoint_root = os.path.dirname(self.pxpoint_datasets.values()[0])

        # get layer paths
        layers = dc.getroot().find('SpatialLayers')
        layer_iterator = iter(layers)
        for layer in layer_iterator:
            self.spatial_layers[layer.attrib['Name']] = layer.attrib['URI'].replace('file:///$PXSEDIR', pxse_dir)


