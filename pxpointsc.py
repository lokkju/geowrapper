#!/usr/bin/env python
#
# $Id: pxpointsc.py 10059 2013-01-31 22:39:34Z tschutter $
#


"""PxPointSC API wrapper."""

import ctypes
import sys

import pxcommon
import tableset
import table

# IANA name (in ASCII) of character set used to encode/decode strings
# See http://www.iana.org/assignments/character-sets
CHAR_SET_NAME = "UTF-8"

# Standard indicator of success in PxPoint
PXP_SUCCESS = pxcommon.error_str_to_code("SUCCESS")


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
        pxcommon.PxpHandle,        # geocoder
        pxcommon.PxpBytePtr,       # inputTableStream
        pxcommon.PxpConstUTF8Ptr,  # outColDefinition
        pxcommon.PxpConstUTF8Ptr,  # errColDefinition
        pxcommon.PxpConstUTF8Ptr,  # processingOptions
        pxcommon.PxpInt32Ptr,      # returnCode
        pxcommon.PxpUTF8Ptr,       # returnMessage
        pxcommon.PxpInt32          # messageSize
    ]

    pxpointsc.GeocoderReverseGeocode.restype = pxcommon.PxpHandle
    pxpointsc.GeocoderReverseGeocode.argtypes = [
        pxcommon.PxpHandle,        # geocoder
        pxcommon.PxpBytePtr,       # inputTableStream
        pxcommon.PxpConstUTF8Ptr,  # outColDefinition
        pxcommon.PxpConstUTF8Ptr,  # errColDefinition
        pxcommon.PxpConstUTF8Ptr,  # processingOptions
        pxcommon.PxpInt32Ptr,      # returnCode
        pxcommon.PxpUTF8Ptr,       # returnMessage
        pxcommon.PxpInt32          # messageSize
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

    # This table_handle doesn't itself wrap a handle.
    size = PXPOINTSC.ByteArrayGetSize(table_handle)

    # Get the number of serialized bytes for the output table.
    table_bytes = ctypes.create_string_buffer(size)

    # Get the actual serialized bytes of the output table.
    PXPOINTSC.ByteArrayGetBytes(
        table_handle,
        table_bytes,
        size
    )
    # Deserialize.
    return_table = table.Table()
    return_table.deserialize(table_bytes, 0)

    # Close the handle to the output table byte stream.
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
    PXPOINTSC.ByteArrayGetBytes(
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


def geocoder_init(data_catalog):
    """Initialize a Geocoder."""
    dataset_list = data_catalog.pxpoint_datasets.keys()
    # remove the all_us dataset
    dataset_list.remove("All")
    datasets = ",".join(dataset_list)

    return_code = pxcommon.PxpInt32()
    message_buffer = ctypes.create_string_buffer(1024)
    geocoder_handle = pxcommon.PxpHandleWrapper(
        PXPOINTSC.GeocoderInit(
            data_catalog.pxpoint_root.encode(CHAR_SET_NAME),
            datasets.encode(CHAR_SET_NAME),
            data_catalog.license_path.encode(CHAR_SET_NAME),
            data_catalog.license_key,
            ctypes.byref(return_code),
            message_buffer,
            ctypes.sizeof(message_buffer)
        )
    )
    return_code = return_code.value
    return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()

    return geocoder_handle, return_code, return_message


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

    return output_table, error_table, return_code, return_message


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

    return output_table, error_table, return_code, return_message


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

    return output_table, error_table, return_code, return_message


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

    return output_table, error_table, return_code, return_message


def geocoder_close(geocoder_handle):
    """Remove static Geocoder object after all geocoding tasks."""
    message_buffer = ctypes.create_string_buffer(1024)
    return_code = PXPOINTSC.GeocoderClose(
        geocoder_handle.handle,
        message_buffer,
        ctypes.sizeof(message_buffer)
    )
    return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()
    return return_code, return_message


def geospatial_init(data_catalog):
    """Initialize a geospatial processor."""
    return_code = pxcommon.PxpInt32()
    message_buffer = ctypes.create_string_buffer(1024)
    geospatial_handle = pxcommon.PxpHandleWrapper(
        PXPOINTSC.GeoSpatialInit(
            data_catalog.spatial_root.encode(CHAR_SET_NAME),
            data_catalog.license_path.encode(CHAR_SET_NAME),
            data_catalog.license_key,
            ctypes.byref(return_code),
            message_buffer,
            ctypes.sizeof(message_buffer)
        )
    )
    return_code = return_code.value
    return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()
    return geospatial_handle, return_code, return_message


def geospatial_prepare(geospatial_handle, data_catalog, layer_alias_list):
    """Attach a list of layers to a geospatial processor, and get back
       a map from layer aliases to lists of output columns."""
    layer_alias_field_map = {}
    for layer_alias in layer_alias_list:
            # attach the layer
            message_buffer = ctypes.create_string_buffer(1024)
            layer_pathname = data_catalog.spatial_layers[layer_alias]
            return_code = PXPOINTSC.GeoSpatialAttachLayer(
                geospatial_handle.handle,
                layer_pathname.encode(CHAR_SET_NAME),
                layer_alias.encode(CHAR_SET_NAME),
                message_buffer,
                ctypes.sizeof(message_buffer)
            )
            return_code = return_code.value
            return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()
            if return_code != PXP_SUCCESS:
                raise RuntimeError("Error. Code: {c}. Message: {m}".format(
                    c=return_code, m=return_message))
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
                return_message = message_buffer.value.decode(
                    CHAR_SET_NAME).strip()
                if return_code == 0:
                    output_table = deserialize_table(output_table_handle)
                    fields = []
                    if output_table is not None and output_table.nrows > 0:
                        name_idx = 0
                        for i in range(output_table.ncols()):
                            if output_table.col_names[i].upper() == "NAME":
                                name_idx = i
                                break
                        for i in range(output_table.nrows()):
                            row = output_table.rows[i]
                            fields.append("[{a}]{f}".format(
                                a=layer_alias, f=str(row[name_idx]).encode(
                                    "unicode_escape")))
                    layer_alias_field_map[layer_alias] = fields
                else:
                    raise RuntimeError(
                        "Error. Code: {c}. Message: {m}".format(
                            c=return_code, m=return_message))
    return layer_alias_field_map 


def geospatial_detach_layer(geospatial_handle, layer_alias):
    """Detach a layer from a geospatial processor."""
    message_buffer = ctypes.create_string_buffer(1024)
    return_code = PXPOINTSC.GeoSpatialDetachLayer(
        geospatial_handle.handle,
        layer_alias.encode(CHAR_SET_NAME),
        message_buffer,
        ctypes.sizeof(message_buffer)
    )
    return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()
    return return_code, return_message


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
    if return_code == PXP_SUCCESS:
        output_tableset = deserialize_tableset(output_tableset_handle)
        output_table = output_tableset.tables["Output"]
        error_table = output_tableset.tables["Error"]
    else:
        output_table = None
        error_table = None

    return output_table, error_table, return_code, return_message


def geospatial_close(geospatial_handle):
    """Close a geospatial processor, after all queries."""
    message_buffer = ctypes.create_string_buffer(1024)

    return_code = PXPOINTSC.GeoSpatialClose(
        geospatial_handle.handle,
        message_buffer,
        ctypes.sizeof(message_buffer)
    )
    return_message = message_buffer.value.decode(CHAR_SET_NAME).strip()
    return return_code, return_message

PXPOINTSC = load_dll()
