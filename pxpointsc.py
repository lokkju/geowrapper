#!/usr/bin/env python
#
# $Id: pxpointsc.py 10059 2013-01-31 22:39:34Z tschutter $
#

"""PxPointSC API wrapper."""

import ctypes
import sys
import re

import pxcommon
import tableset
import table
import datacatalog

PXPOINTSC = None

# IANA name (in ASCII) of character set used to encode/decode strings
# See http://www.iana.org/assignments/character-sets
CHAR_SET_NAME = "UTF-8"

# Standard indicator of success in PxPoint
PXP_SUCCESS = 0

# For extracting layer aliases for attaching layers
_layer_alias_column_regex = re.compile('\[\w\]')

# For keeping track of metadata for attached layers, by their aliases
_alias_fields_map = {}

# For keeping track of layers and datasets
_datacatalog = None

def get_datacatalog(datacatalog_path, shapefile_root_dir):
    return datacatalog.DataCatalog(datacatalog_path, shapefile_root_dir)

def get_fields_from_table(layer_alias, fields_table):
    fields = []
    if fields_table != None and fields_table.nrows > 0 and (layer_alias not in _alias_fields_map):
        name_index = 0
        for i in range(fields_table.ncols()):
            if fields_table.col_names[i].upper() == 'NAME':
                name_index = i
                break
        for i in range(fields_table.nrows()):
            row = fields_table.rows[i]
            fields.append('[{a}]{f}'.format(a=layer_alias, f=str(row[name_index]).encode('unicode_escape')))
    return fields

def add_fields_to_map(layer_alias, fields_table):
    """Adds a list of fields to a layer alias, for constructing output tables"""
    fields = []
    if fields_table != None and fields_table.nrows > 0 and (layer_alias not in _alias_fields_map):
        name_index = 0
        for i in range(fields_table.ncols()):
            if fields_table.col_names[i].upper() == 'NAME':
                name_index = i
                break
        for i in range(fields_table.nrows()):
            row = fields_table.rows[i]
            fields.append(str(row[name_index]).encode('unicode_escape'))
        _alias_fields_map[layer_alias] = fields

def get_fields(layer_alias):
    if layer_alias in _alias_fields_map:
        return _alias_fields_map[layer_alias]
    return None

def get_layer_aliases(output_columns):
    matches = _layer_alias_column_regex.findall(output_columns)
    cleaned_matches = [m.replace('[', '').replace(']', '') for m in matches] 
    final_list = []
    for match in cleaned_matches:
        if not match in final_list:
            final_list.append(match)
    return final_list

def load_dll():
    """Load PxPointSC dll."""

    if sys.platform.startswith("cygwin"):
        print >> sys.stderr, "ERROR: Not supported on cygwin.\n"\
            "       See %s." % __file__
        sys.exit(1)
    elif sys.platform.startswith("win"):
        pxpointsc = ctypes.windll.LoadLibrary("PxPointSC.dll")
    elif sys.platform.startswith("darwin"):
        pxpointsc = ctypes.cdll.LoadLibrary("libPxPointSC.dylib")
    else:
        pxpointsc = ctypes.cdll.LoadLibrary("libPxPointSC.so")

    pxpointsc.TestStringEncoding.restype = pxcommon.PxpUint32
    pxpointsc.TestStringEncoding.argtypes = [
        pxcommon.PxpUTF8Ptr,  # queryString
        pxcommon.PxpUTF8Ptr,  # returnMessage
        pxcommon.PxpInt32     # messageSize
    ]

    pxpointsc.GeocoderInit.restype = pxcommon.PxpHandle
    pxpointsc.GeocoderInit.argtypes = [
        pxcommon.PxpUTF8Ptr,   # dataPath,
        pxcommon.PxpUTF8Ptr,   # datasetList
        pxcommon.PxpUTF8Ptr,   # licenseFileName
        pxcommon.PxpInt32,     # licenseCode
        pxcommon.PxpInt32Ptr,  # returnCode
        pxcommon.PxpUTF8Ptr,   # returnMessage
        pxcommon.PxpInt32      # messageSize
    ]

    pxpointsc.GeocoderGeocode.restype = pxcommon.PxpHandle
    pxpointsc.GeocoderGeocode.argtypes = [
        pxcommon.PxpHandle,    # geocoder
        pxcommon.PxpBytePtr,   # inputTableStream
        pxcommon.PxpUTF8Ptr,   # outColDefinition
        pxcommon.PxpUTF8Ptr,   # errColDefinition
        pxcommon.PxpUTF8Ptr,   # processingOptions
        pxcommon.PxpInt32Ptr,  # returnCode
        pxcommon.PxpUTF8Ptr,   # returnMessage
        pxcommon.PxpInt32      # messageSize
    ]

    pxpointsc.GeocoderFindChildren.restype = pxcommon.PxpHandle
    pxpointsc.GeocoderFindChildren.argtypes = [
        pxcommon.PxpHandle,        # singleCallGeocoder
        pxcommon.PxpBytePtr,       # inputTableStream
        pxcommon.PxpConstUTF8Ptr,  # outColDefinition
        pxcommon.PxpConstUTF8Ptr,  # errColDefinition
        pxcommon.PxpConstUTF8Ptr,  # processingOptions
        pxcommon.PxpInt32Ptr,      # returnCode
        pxcommon.PxpUTF8Ptr,       # returnMessage
        pxcommon.PxpInt32          # messageSize
    ]

    pxpointsc.GeocoderFindParent.restype = pxcommon.PxpHandle
    pxpointsc.GeocoderFindParent.argtypes = [
        pxcommon.PxpHandle,        # singleCallGeocoder
        pxcommon.PxpBytePtr,       # inputTableStream
        pxcommon.PxpConstUTF8Ptr,  # outColDefinition
        pxcommon.PxpConstUTF8Ptr,  # errColDefinition
        pxcommon.PxpConstUTF8Ptr,  # processingOptions
        pxcommon.PxpInt32Ptr,      # returnCode
        pxcommon.PxpUTF8Ptr,       # returnMessage
        pxcommon.PxpInt32          # messageSize
    ]

    pxpointsc.GeocoderFindPlace.restype = pxcommon.PxpHandle
    pxpointsc.GeocoderFindPlace.argtypes = [
        pxcommon.PxpHandle,       # geocoder
        pxcommon.PxpBytePtr,      # inputTableStream
        pxcommon.PxpConstUTF8Ptr, # outColDefinition
        pxcommon.PxpConstUTF8Ptr, # errColDefinition
        pxcommon.PxpConstUTF8Ptr, # processingOptions
        pxcommon.PxpInt32Ptr,     # returnCode
        pxcommon.PxpUTF8Ptr,      # returnMessage
        pxcommon.PxpInt32         # messageSize
    ]

    pxpointsc.GeocoderReverseGeocode.restype = pxcommon.PxpHandle
    pxpointsc.GeocoderReverseGeocode.argtypes = [
        pxcommon.PxpHandle,       # geocoder
        pxcommon.PxpBytePtr,      # inputTableStream
        pxcommon.PxpConstUTF8Ptr, # outColDefinition
        pxcommon.PxpConstUTF8Ptr, # errColDefinition
        pxcommon.PxpConstUTF8Ptr, # processingOptions
        pxcommon.PxpInt32Ptr,     # returnCode
        pxcommon.PxpUTF8Ptr,      # returnMessage
        pxcommon.PxpInt32         # messageSize
    ]

    pxpointsc.GeocoderClose.restype = pxcommon.PxpInt32
    pxpointsc.GeocoderClose.argtypes = [
        pxcommon.PxpHandle,   # geocoder
        pxcommon.PxpUTF8Ptr,  # returnMessage
        pxcommon.PxpInt32     # messageSize
    ]

    pxpointsc.GeoSpatialInit.restype = pxcommon.PxpHandle
    pxpointsc.GeoSpatialInit.argtypes = [
        pxcommon.PxpUTF8Ptr,   # dataPath
        pxcommon.PxpUTF8Ptr,   # licenseFileName
        pxcommon.PxpInt32,     # licenseCode
        pxcommon.PxpInt32Ptr,  # returnCode
        pxcommon.PxpUTF8Ptr,   # returnMessage
        pxcommon.PxpInt32      # messageSize
    ]

    pxpointsc.GeoSpatialAttachLayer.restype = pxcommon.PxpInt32
    pxpointsc.GeoSpatialAttachLayer.argtypes = [
        pxcommon.PxpHandle,        # geoProcessor
        pxcommon.PxpConstUTF8Ptr,  # layerFileName
        pxcommon.PxpConstUTF8Ptr,  # layerAlias
        pxcommon.PxpUTF8Ptr,       # returnMessage
        pxcommon.PxpInt32          # messageSize
    ]

    pxpointsc.GeoSpatialDetachLayer.restype = pxcommon.PxpInt32
    pxpointsc.GeoSpatialDetachLayer.argtypes = [
        pxcommon.PxpHandle,        # geoProcessor
        pxcommon.PxpConstUTF8Ptr,  # layerAlias
        pxcommon.PxpUTF8Ptr,       # returnMessage
        pxcommon.PxpInt32          # messageSize
    ]

    pxpointsc.GeoSpatialLayerInfo.restype = pxcommon.PxpInt32
    pxpointsc.GeoSpatialLayerInfo.argtypes = [
        pxcommon.PxpHandle,        # geoProcessor
        pxcommon.PxpConstUTF8Ptr,  # layerAlias
        pxcommon.PxpInt32Ptr,      # returnCode
        pxcommon.PxpUTF8Ptr,       # returnMessage
        pxcommon.PxpInt32          # messageSize
    ]

    pxpointsc.GeoSpatialQuery.restype = pxcommon.PxpHandle
    pxpointsc.GeoSpatialQuery.argtypes = [
        pxcommon.PxpHandle,         # geoProcessor
        pxcommon.PxpBytePtr,        # inputTableStream
        pxcommon.PxpUTF8Ptr,        # outColDefinition
        pxcommon.PxpUTF8Ptr,        # errColDefinition
        pxcommon.PxpUTF8Ptr,        # processingOptions
        pxcommon.PxpInt32Ptr,       # returnCode
        pxcommon.PxpUTF8Ptr,        # returnMessage
        pxcommon.PxpInt32           # messageSize
    ]

    pxpointsc.GeoSpatialClose.restype = pxcommon.PxpInt32
    pxpointsc.GeoSpatialClose.argtypes = [
        pxcommon.PxpHandle,    # geoProcessor
        pxcommon.PxpUTF8Ptr,   # returnMessage
        pxcommon.PxpInt32      # messageSize
    ]

    pxpointsc.ByteArrayGetSize.restype = pxcommon.PxpUint64
    pxpointsc.ByteArrayGetSize.argtypes = [
        pxcommon.PxpHandle  # byteArray
    ]

    pxpointsc.ByteArrayGetBytes.restype = pxcommon.PxpUint64
    pxpointsc.ByteArrayGetBytes.argtypes = [
        pxcommon.PxpHandle,   # byteArray
        pxcommon.PxpBytePtr,  # buffer
        pxcommon.PxpUint64    # size
    ]

    pxpointsc.ByteArrayClose.restype = pxcommon.PxpInt32
    pxpointsc.ByteArrayClose.argtypes = [
        pxcommon.PxpHandle  # byteArray
    ]

    return pxpointsc


def deserialize_table(table_handle):
    """Deserialize a table handle to create a Table."""
    size = PXPOINTSC.ByteArrayGetSize(table_handle)
    table_bytes = ctypes.create_string_buffer(size)
    size = PXPOINTSC.ByteArrayGetBytes(
        table_handle,
        table_bytes,
        size
    )
    return_table = table.Table()
    return_table.deserialize(table_bytes, 0)
    PXPOINTSC.ByteArrayClose(table_handle)
    return return_table

def deserialize_tableset(tableset_handle):
    """Deserialize a tableset handle to create a TableSet."""

    # Get the actual handle value.
    tableset_handle = tableset_handle.value

    # Get the number of serialized bytes for the output table.
    size = PXPOINTSC.ByteArrayGetSize(tableset_handle)

    # Get the actual serialized bytes of the output table.
    tableset_bytes = ctypes.create_string_buffer(size)
    size = PXPOINTSC.ByteArrayGetBytes(
        tableset_handle,
        tableset_bytes,
        size
    )

    # Deserialize.
    return_tableset = tableset.TableSet()
    return_tableset.deserialize(tableset_bytes)

    # Close the handle to the output table byte stream.
    PXPOINTSC.ByteArrayClose(tableset_handle)

    return return_tableset


def test_string_encoding():
    """Test API string handling."""
    query_string = u"Q: Quelle est votre couleur pr\u00e9f\u00e9r\u00e9e?"
    message_buffer = ctypes.create_string_buffer(1024)
    return_code = PXPOINTSC.TestStringEncoding(
        query_string.encode(CHAR_SET_NAME),
        message_buffer,
        ctypes.sizeof(message_buffer)
    )
    return_message = message_buffer.value.decode(CHAR_SET_NAME)
    if return_message != u"A: \ud478\ub978":
        return_code = -1
    return (return_code, return_message)

def pxpointsc_init(
        datacatalog_path, 
        shapefile_root_dir, 
        geocoder_init_func=None, 
        geospatial_init_func=None):
    geocoder_handle = None
    geospatial_handle = None
    catalog = datacatalog.DataCatalog(datacatalog_path, shapefile_root_dir) 
    dataset_list = catalog.pxpoint_datasets.keys()
    dataset_list.remove('All')
    if (geocoder_init_func is None) and (geospatial_init_func is None):
        raise RuntimeError('pxpointsc_init requires an init function')
    # initialize geocoder
    if geocoder_init_func is not None:
        (geocoder_handle, return_code, return_message) = geocoder_init_func(
                catalog.pxpoint_root,
                dataset_list,
                catalog.license_path,
                int(catalog.license_key)
            )
        if return_code != PXP_SUCCESS:
            raise RuntimeError(
                'Error in geocoder_init. Code: {c}. Message: {m}'.format(
                    c=str(return_code), m=return_message))
    # initialize spatial processor
    if geospatial_init_func is not None:
        (geospatial_handle, return_code, return_message) = geospatial_init_func(
                shapefile_root_dir,
                catalog.license_path,
                int(catalog.license_key)
            )
        if return_code != PXP_SUCCESS:
            raise RuntimeError(
                'Error in geospatial_init. Code: {c}. Message: {m}'.format(
                    c=str(return_code), m=return_message))

    return (geocoder_handle, geospatial_handle)

def geocoder_init(
    data_dir,
    datasets,
    license_pathname,
    license_code
):
    """Create static Geocoder object for handling table-based geocoding."""
    datasets = ",".join(datasets)
    return_code = pxcommon.PxpInt32()
    message_buffer = ctypes.create_string_buffer(1024)
    geocoder_handle = pxcommon.PxpHandleWrapper(
        PXPOINTSC.GeocoderInit(
            data_dir.encode(CHAR_SET_NAME),
            datasets.encode(CHAR_SET_NAME),
            license_pathname.encode(CHAR_SET_NAME),
            license_code,
            ctypes.byref(return_code),
            message_buffer,
            ctypes.sizeof(message_buffer)
        )
    )
    return_code = return_code.value
    return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()

    return (geocoder_handle, return_code, return_message)


def geocoder_geocode(
    geocoder_handle,
    input_table,
    out_col_definition,
    err_col_definition,
    processing_options
):
    """Perform a geocode operation."""
    return_code = pxcommon.PxpInt32()
    message_buffer = ctypes.create_string_buffer(1024)

    output_tableset_handle = pxcommon.PxpHandle(
        PXPOINTSC.GeocoderGeocode(
            geocoder_handle.handle,
            pxcommon.serialize_table(input_table),
            out_col_definition,
            err_col_definition,
            processing_options,
            ctypes.byref(return_code),
            message_buffer,
            ctypes.sizeof(message_buffer)
        )
    )
    return_code = return_code.value
    return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()
    if return_code == 0:
        output_tableset = deserialize_tableset(output_tableset_handle)
        output_table = output_tableset.tables["Output"]
        error_table = output_tableset.tables["Error"]
    else:
        output_table = None
        error_table = None

    return (output_table, error_table, return_code, return_message)


def geocoder_find_aggregate(
    geocoder_handle,
    input_table,
    out_col_definition,
    err_col_definition,
    processing_options
):
    """Perform a find aggregate operation."""
    return_code = pxcommon.PxpInt32()
    message_buffer = ctypes.create_string_buffer(1024)

    output_tableset_handle = pxcommon.PxpHandle(
        PXPOINTSC.GeocoderFindAggregate(
            geocoder_handle.handle,
            pxcommon.serialize_table(input_table),
            out_col_definition,
            err_col_definition,
            processing_options,
            ctypes.byref(return_code),
            message_buffer,
            ctypes.sizeof(message_buffer)
        )
    )
    return_code = return_code.value
    return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()
    if return_code == 0:
        output_tableset = deserialize_tableset(output_tableset_handle)
        output_table = output_tableset.tables["Output"]
        error_table = output_tableset.tables["Error"]
    else:
        output_table = None
        error_table = None

    return (output_table, error_table, return_code, return_message)


def geocoder_find_place(
    geocoder_handle,
    input_table,
    out_col_definition,
    err_col_definition,
    processing_options
):
    """Perform a find place operation."""
    return_code = pxcommon.PxpInt32()
    message_buffer = ctypes.create_string_buffer(1024)

    output_tableset_handle = pxcommon.PxpHandle(
        PXPOINTSC.GeocoderFindPlace(
            geocoder_handle.handle,
            pxcommon.serialize_table(input_table),
            out_col_definition,
            err_col_definition,
            processing_options,
            ctypes.byref(return_code),
            message_buffer,
            ctypes.sizeof(message_buffer)
        )
    )
    return_code = return_code.value
    return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()
    if return_code == 0:
        output_tableset = deserialize_tableset(output_tableset_handle)
        output_table = output_tableset.tables["Output"]
        error_table = output_tableset.tables["Error"]
    else:
        output_table = None
        error_table = None

    return (output_table, error_table, return_code, return_message)


def geocoder_reverse_geocode(
    geocoder_handle,
    input_table,
    out_col_definition,
    err_col_definition,
    processing_options
):
    """Perform a reverse geocode operation."""
    return_code = pxcommon.PxpInt32()
    message_buffer = ctypes.create_string_buffer(1024)

    output_tableset_handle = pxcommon.PxpHandle(
        PXPOINTSC.GeocoderReverseGeocode(
            geocoder_handle.handle,
            pxcommon.serialize_table(input_table),
            out_col_definition,
            err_col_definition,
            processing_options,
            ctypes.byref(return_code),
            message_buffer,
            ctypes.sizeof(message_buffer)
        )
    )
    return_code = return_code.value
    return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()
    if return_code == 0:
        output_tableset = deserialize_tableset(output_tableset_handle)
        output_table = output_tableset.tables["Output"]
        error_table = output_tableset.tables["Error"]
    else:
        output_table = None
        error_table = None

    return (output_table, error_table, return_code, return_message)


def geocoder_close(geocoder_handle):
    """Remove static Geocoder object after all geocoding tasks."""
    message_buffer = ctypes.create_string_buffer(1024)
    return_code = PXPOINTSC.GeocoderClose(
        geocoder_handle.handle,
        message_buffer,
        ctypes.sizeof(message_buffer)
    )
    return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()
    return (return_code, return_message)


def geospatial_init(
    data_dir,
    license_pathname,
    license_code
):
    """Create static GeoSpatial object for handling table-based
    spatial operations."""
    return_code = pxcommon.PxpInt32()
    message_buffer = ctypes.create_string_buffer(1024)
    geocoder_handle = pxcommon.PxpHandleWrapper(
        PXPOINTSC.GeoSpatialInit(
            data_dir.encode(CHAR_SET_NAME),
            license_pathname.encode(CHAR_SET_NAME),
            license_code,
            ctypes.byref(return_code),
            message_buffer,
            ctypes.sizeof(message_buffer)
        )
    )
    return_code = return_code.value
    return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()

    return (geocoder_handle, return_code, return_message)


def geospatial_prepare(geospatial_handle, datacatalog_path, shapefile_root_dir, layer_alias_list):
    """Attach a list of layers to a geospatial processor, and get back
       a map of layer_aliases to a list of output columns."""
    layer_alias_field_map = {}
    catalog = datacatalog.DataCatalog(datacatalog_path, shapefile_root_dir)
    for layer_alias in layer_alias_list:
        if layer_alias in _alias_fields_map:
            if layer_alias not in layer_alias_field_map:
                layer_alias_field_map[layer_alias] = _alias_fields_map[layer_alias]
        else:
            # attach the layer, then get the fields
            return_code = pxcommon.PxpInt32()
            message_buffer = ctypes.create_string_buffer(1024)
            layer_pathname = catalog.spatial_layers[layer_alias]
            return_code = PXPOINTSC.GeoSpatialAttachLayer(
                geospatial_handle.handle,
                layer_pathname.encode(CHAR_SET_NAME),
                layer_alias.encode(CHAR_SET_NAME),
                message_buffer,
                ctypes.sizeof(message_buffer)
            )
            if return_code != pxcommon.error_str_to_code('SUCCESS'):
                raise RuntimeError('Error. Code: {c}. Message: {m}'.format(c = return_code, m=return_message))
            else:
                # get the fields
                return_code = pxcommon.PxpInt32()
                message_buffer = ctypes.create_string_buffer(1024)
                output_table_handle = PXPOINTSC.GeoSpatialLayerInfo(
                    geospatial_handle.handle,
                    layer_alias,
                    ctypes.byref(return_code),
                    message_buffer,
                    ctypes.sizeof(message_buffer)
                )
                return_code = return_code.value
                return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()
                if return_code == 0:
                    output_table = deserialize_table(output_table_handle)
                    layer_alias_field_map[layer_alias] = get_fields_from_table(layer_alias, output_table)
                else:
                    raise RuntimeError('Error. Code: {c}. Message: {m}'.format(c = return_code, m=return_message))
    return layer_alias_field_map 

def geospatial_attach_layer(geospatial_handle, layer_pathname, layer_alias):
    """Attach a layer to a geospatial processor."""
    return_code = pxcommon.PxpInt32()
    message_buffer = ctypes.create_string_buffer(1024)
    return_code = PXPOINTSC.GeoSpatialAttachLayer(
        geospatial_handle.handle,
        layer_pathname.encode(CHAR_SET_NAME),
        layer_alias.encode(CHAR_SET_NAME),
        message_buffer,
        ctypes.sizeof(message_buffer)
    )
    if return_code == pxcommon.error_str_to_code('SUCCESS'):
        _attached_layer_map[layer_alias] = layer_pathname
    return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()
    return (return_code, return_message)

def geospatial_detach_layer(geospatial_handle, layer_alias):
    """Detach a layer from a geospatial processor"""
    return_code = pxcommon.PxpInt32()
    message_buffer = ctypes.create_string_buffer(1024)
    if layer_alias in _attached_layer_map:
        return_code = PXPOINTSC.GeoSpatialDetachLayer(
            geospatial_handle.handle,
            layer_alias.encode(CHAR_SET_NAME),
            message_buffer,
            ctypes.sizeof(message_buffer)
        )
        if return_code == pxcommon.error_str_to_code('SUCCESS'):
            del _attached_layer_map[layer_alias]
            del _alias_fields_map[layer_alias]
        return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()
    return (return_code, return_message)

def geospatial_layer_info(geospatial_handle, layer_alias):
    """Get a description of layer metadata"""
    fields = None
    return_code = pxcommon.PxpInt32()
    message_buffer = ctypes.create_string_buffer(1024)
    output_table = None
    if layer_alias in _alias_fields_map:
        fields = _alias_fields_map[layer_alias]
    else:
        output_table_handle = PXPOINTSC.GeoSpatialLayerInfo(
            geospatial_handle.handle,
            layer_alias,
            ctypes.byref(return_code),
            message_buffer,
            ctypes.sizeof(message_buffer)
        )
        return_code = return_code.value
        return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()
        if return_code == 0:
            output_table = deserialize_table(output_table_handle)
            add_fields_to_map(layer_alias, output_table)
            fields = _alias_fields_map[layer_alias]
        else:
            raise RuntimeError('Error. Code: {c}. Message: {m}'.format(c = return_code, m=return_message))
    return fields

def geospatial_layers_attached():
    """Get a mapping of layer aliases to layer pathnames (for debugging)"""
    return _attached_layer_map.copy()

def geospatial_query(
    geospatial_handle,
    input_table,
    out_col_definition,
    err_col_definition,
    processing_options
):
    """Perform a geospatial query operation."""
    return_code = pxcommon.PxpInt32()
    message_buffer = ctypes.create_string_buffer(1024)

    output_tableset_handle = pxcommon.PxpHandle(
        PXPOINTSC.GeoSpatialQuery(
            geospatial_handle.handle,
            pxcommon.serialize_table(input_table),
            out_col_definition,
            err_col_definition,
            processing_options,
            ctypes.byref(return_code),
            message_buffer,
            ctypes.sizeof(message_buffer)
        )
    )
    return_code = return_code.value
    return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()
    if return_code == pxcommon.error_str_to_code('SUCCESS'):
        output_tableset = deserialize_tableset(output_tableset_handle)
        output_table = output_tableset.tables["Output"]
        error_table = output_tableset.tables["Error"]
    else:
        output_table = None
        error_table = None

    return (output_table, error_table, return_code, return_message)

def geospatial_close(geospatial_handle):
    """Close a geospatial processor."""
    return_code = pxcommon.PxpInt32()
    message_buffer = ctypes.create_string_buffer(1024)

    return_code = PXPOINTSC.GeoSpatialClose(
        geospatial_handle.handle,
        message_buffer,
        ctypes.sizeof(message_buffer)
    )
    return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()
    return (return_code, return_message)


PXPOINTSC = load_dll()
