#!/usr/bin/env python
#
# $Id: pxcommon.py 10059 2013-01-31 22:39:34Z tschutter $
#

"""geocoder/PxCommon.h API wrapper."""

import ctypes
import re

# Error and status return codes.
ERROR_CODE_MAP = {
    0: "SUCCESS",
    -1: "ERROR",
    -2: "GEOMETRY",
    -3: "NULLGEOMETRY",
    -4: "INVALIDGEOMETRY",
    -5: "DATUMSHIFT",
    -6: "INVALIDSPATIALREFERENCE",
    -7: "NOTIMPLEMENTED",
    -8: "IOEXCEPTION",
    -9: "FILEREAD",
    -10: "FILEWRITE",
    -11: "DISKFULL",
    -12: "FILELOCKING",
    -13: "LOCKING",
    -14: "SQL",
    -15: "CONNECTION",
    -16: "FILE",
    -17: "COMMIT",
    -18: "ROLLBACK",
    -19: "CREATETABLE",
    -20: "CREATEINDEX",
    -21: "DROPTABLE",
    -22: "UPDATERECORD",
    -23: "DELETERECORD",
    -24: "ADDRECORD",
    -25: "DUPLICATETABLENAME",
    -26: "DUPLICATELAYERNAME",
    -27: "DUPLICATEFIELDNAME",
    -28: "RECORDNOTFOUND",
    -29: "TABLENOTFOUND",
    -30: "INDEXNOTFOUND",
    -31: "MEMONOTFOUND",
    -32: "SPATIALINDEXNOTFOUND",
    -33: "GEOMETRYTABLENOTFOUND",
    -34: "INVALIDTABLE",
    -35: "INVALIDGEOMETRYTABLE",
    -36: "INVALIDINDEX",
    -37: "INVALIDMEMO",
    -38: "INVALIDSPATIALINDEX",
    -39: "INVALIDPRIMARYKEY",
    -40: "QUERY",
    -41: "EVALUATE",
    -42: "SYNTAX",
    -43: "INVALIDFORMAT",
    -44: "INVALIDBINARY",
    -45: "INVALIDTEXT",
    -46: "INVALIDFIELDTYPE",
    -47: "INVALIDGEOMETRYFIELD",
    -48: "INVALIDIDENTIFIER",
    -49: "PXYFILENOTFOUND",
    -50: "DBMS",
    -51: "DATABASE",
    -52: "NAMEINUSE",
    -53: "NOTFOUND",
    -54: "INVALIDDATA",
    -55: "INVALIDQUERY",
    -56: "SYSTEM",
    -57: "NOTSUPPORTED",
    -58: "INVALIDARGUMENT",
    -59: "INVALIDOPERATION",
    -60: "INVALIDDIRECTORY",
    -61: "FILESYSTEM",
    -62: "XML",
    -63: "INVALIDRANGE",
    -64: "NULLPOINTER",
    -65: "PARSE",
    -66: "LICENSE",
    -67: "BADALLOC",
    -68: "DOMAINERROR",
    -69: "OUTOFRANGE",
    -70: "OVERFLOW",
    -71: "RANGEERROR",
    -72: "UNDERFLOW",
    -73: "UNEXPECTED",
    -74: "FILEREADONLY",
    -76: "INVALIDCONTEXT",
    -77: "INVALIDHANDLE",
    -78: "INVALIDSTREET",
    -79: "FILENOTFOUND",
    -80: "INVALIDFILE",
    -81: "SHARING",
    -82: "READONLY",
    -83: "INVALIDTYPE",
    -84: "INCORRECT_DATSET_VERSION",
    -85: "OBJECTCREATION",
    -86: "INVALIDCOUNTRY"
}

WKT_POINT_FORMAT = 'POINT ( {x} {y} )'

# Enumeration of spatial relations, for specifying geospatial operations
class SpatialRelation:
    NONE, INTERSECTS, TOUCHES, OVERLAPS, CONTAINS, WITHIN, CROSSES, DISJOINT, EQUALS, NEAR, EXTENTS = range(11)
    
def get_spatial_relation_spec(relation):
    return 'Relation={r}'.format(r=relation)

def error_code_to_str(error_code):
    """Return the string representation of an integer error_code."""
    if error_code in ERROR_CODE_MAP:
        return ERROR_CODE_MAP[error_code]
    else:
        return str(error_code)


def error_str_to_code(error_str):
    """Return the integer representation of a string error_str."""
    for key, val in ERROR_CODE_MAP.items():
        if error_str == val:
            return key
    return 999

def get_wkt_point_from_dec_coords(lat, lon):
    """Returns the WKT for a point, given a lat/lon pair"""
    return WKT_POINT_FORMAT.format(x=lon, y=lat)

def translate_incorrect_dataset_version_message(message):
    """Translate the message associated with error_code = -84 to a
    one-liner."""
    try:
        gdx_filename = re.search("gdx file: (.+)\n", message).group(1)
        gdx_version = re.search(
            "Version in file: ([0-9.]+)",
            message
        ).group(1)
        dll_version = re.search(
            "Software version: ([0-9.]+)",
            message
        ).group(1)
        message = "%s version %s != DLL version %s" % (
            gdx_filename,
            gdx_version,
            dll_version
        )
    except AttributeError:
        pass
    return message

# Commonly used ctypes for PxPoint value types
PxpBytePtr = ctypes.c_char_p
PxpConstUTF8Ptr = ctypes.c_char_p
PxpHandle = ctypes.c_void_p
PxpInt32 = ctypes.c_int32
PxpInt32Ptr = ctypes.POINTER(ctypes.c_int32)
PxpUTF8Ptr = ctypes.c_char_p
PxpUint32 = ctypes.c_uint32
PxpUint64 = ctypes.c_uint64

# Common return codes
PXP_SUCCESS = error_str_to_code("SUCCESS")
PXP_INVALID_ARGUMENT = error_str_to_code("INVALIDARGUMENT")


class PxpHandleWrapper:
    """Wrapper around a PxpHandle (void *)."""
    def __init__(self, handle):
        self.handle = ctypes.c_void_p(handle)


def serialize_table(tabl):
    """Serialize an input table.  We should be able to pass the
    bytearray returned by table.serialize() directly, but as of
    2012-05-08, ctypes does not that.
    """
    (tabl_ba, tabl_ba_len) = tabl.serialize()
    tabl_c_byte_array = ctypes.c_byte * tabl_ba_len
    tabl_c_byte_instance = tabl_c_byte_array.from_buffer(tabl_ba)
    return ctypes.cast(tabl_c_byte_instance, PxpBytePtr)
