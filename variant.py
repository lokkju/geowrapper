#!/usr/bin/env python
#
# $Id: variant.py 10059 2013-01-31 22:39:34Z tschutter $
#

"""Proxix::VarObject (geocoder/PxLib/Variant.h) wrapper."""

import struct


MISSING_VALUE = 128  # PxVariant::MissingValue in geocoder/PxLib/PxVariant.cpp


class VarType(object):
    """Proxix::VarType (geocoder/PxLib/basetype.h)."""
    Double = 0
    Int64 = 1
    UInt64 = 2
    Int32 = 3
    UInt32 = 4
    String = 5
    Date = 6
    Bool = 7
    Bytes = 8
    Geometry = 9
    Byte = 10


def serialize_string(buff, offset, value):
    """Serialize string value into buffer[offset], returning a new
    offset."""
    # Encode the value as UTF8.
    encoded = value.encode("utf_8")
    enclen = len(encoded)

    # Pack the length.
    struct.pack_into("<i", buff, offset, enclen)
    offset += 4

    # Pack the encoded bytes.
    buff[offset:offset + enclen] = encoded
    offset += enclen

    return offset


def deserialize_string(buff, offset):
    """Deserialize string value from buffer[offset], returning value
    and a new offset."""

    # Unpack the length.
    (enclen, ) = struct.unpack_from("<i", buff, offset)
    offset += 4

    # Unpack the encoded bytes.
    encoded = buff[offset:offset + enclen]
    offset += enclen

    # Decode the value as UTF8.
    value = encoded.decode("utf_8")

    return (value, offset)


class Variant:
    """Variable serializer/deserializer."""
    def __init__(self, var_type):
        self.var_type = var_type
        self.fmt = {
            VarType.Double: "<d",
            VarType.Int64: "<q",
            VarType.UInt64: "<Q",
            VarType.Int32: "<i",
            VarType.UInt32: "<I",
            VarType.String: None,  # never used
            VarType.Bool: "<?",
            VarType.Geometry: None  # never used
        }[var_type]
        if self.fmt == None:
            self.struct_obj = None
        else:
            self.struct_obj = struct.Struct(self.fmt)

    def serialize(self, buff, offset, value):
        """Serialize variant value into buffer[offset], returning a
        new offset."""
        # Pack the VarType.
        var_type = self.var_type
        if value == None:
            var_type |= MISSING_VALUE
        struct.pack_into("B", buff, offset, var_type)
        offset += 1

        if value != None:
            if self.var_type == VarType.String:
                offset = serialize_string(buff, offset, value)
            elif self.var_type == VarType.Geometry:
                raise NotImplementedError("serialize VarType.Geometry")
            else:
                self.struct_obj.pack_into(buff, offset, value)
                offset += self.struct_obj.size

        return offset

    @staticmethod
    def deserialize(buff, offset):
        """Deserialize variant value from buffer[offset], returning
        value and a new offset."""

        # Unpack the VarType.
        (var_type, ) = struct.unpack_from("B", buff, offset)
        offset += 1

        # Unpack the value.
        if var_type & MISSING_VALUE != 0:
            value = None
        else:
            variant = VARTYPE_TO_VARIANT[var_type]
            if variant.var_type == VarType.String:
                value, offset = deserialize_string(buff, offset)
            elif variant.var_type == VarType.Geometry:
                # See PxLib/Wks.cpp ExportToWKB
                # See http://en.wikipedia.org/wiki/Well-known_binary
                raise NotImplementedError("deserialize VarType.Geometry")
            else:
                (value, ) = variant.struct_obj.unpack_from(buff, offset)
                offset += variant.struct_obj.size

        return (value, var_type, offset)

#  Date(6, java.util.Date.class) {
#          out.setLong(offset, ((java.util.Date)value).getTime());
#          return offset + 4L;
#          return new java.util.Date(buffer.getLong());
#
#  Bytes(8, Byte[].class){
#          out.write(offset, bytes, 0, bytes.length);
#          int length = buffer.getInt();
#          byte[] bytes = new byte[length];
#          return buffer.get(bytes);
#      }
#  Geometry(9, Object.class) {
#      @Override
#      protected long write(ByteBufferResource out, Object value,
#              long offset, boolean useWKT) throws IOException {
#          if (!useWKT) {
#              return super.write(out, value, offset, useWKT);
#          } else {
#              return writeWKT(out, value, offset);
#          }
#      }
#      @Override
#      protected Object read(ByteBuffer buffer, boolean useWKT) {
#          if (!useWKT) {
#              return super.read(buffer, useWKT);
#          } else {
#              return readWKT(buffer);
#          }
#      }
#      @Override
#          byte[] bytes = ((com.proxix.pxpoint.Geometry)value).
#              getWellKnownBinary();
#          out.write(offset, bytes, 0, bytes.length);
#          return offset + bytes.length;
#      }
#
#      @Override
#      protected Object read(ByteBuffer buffer) {
#          try {
#              int length = buffer.getInt();
#              byte[] wkb = new byte[length];
#              buffer.get(wkb);
#              return com.proxix.pxpoint.Geometry.createFromWKB(
#                wkb,
#       com.proxix.pxpoint.Geometry.CoordinateSystem.Default.toString());
#      }
#      long writeWKT(ByteBufferResource out, Object value, long offset) {
#     com.proxix.pxpoint.Geometry g = (com.proxix.pxpoint.Geometry) value;
#          return writeString(out, g.getWellKnownText(), offset, true);
#      }
#      protected Object readWKT(ByteBuffer buffer) {
#          try {
#              String wkt = readString(buffer);
#              return com.proxix.pxpoint.Geometry.createFromWKT(
#                wkt,
#     com.proxix.pxpoint.Geometry.CoordinateSystem.Default.toString());
#          } catch (Exception e) {
#              return null;
#          }
#      }
#  },
#  Byte(10, Byte.class) {
#    protected long write(ByteBufferResource out, Object value, long offset) {
#          out.setByte(offset, ((Byte)value).byteValue());
#          return offset + 1L;
#      }
#
#      @Override
#      protected Object read(ByteBuffer buffer) {
#          return buffer.get();
#      }
#  };

# Dict of VarType to Variant.
VARTYPE_TO_VARIANT = {
    VarType.Double: Variant(VarType.Double),
    VarType.Int64: Variant(VarType.Int64),
    VarType.UInt64: Variant(VarType.UInt64),
    VarType.Int32: Variant(VarType.Int32),
    VarType.UInt32: Variant(VarType.UInt32),
    VarType.String: Variant(VarType.String),
    #VarType.Date: Variant(VarType.Date),
    VarType.Bool: Variant(VarType.Bool),
    #VarType.Bytes: Variant(VarType.Bytes),
    VarType.Geometry: Variant(VarType.Geometry),
    #VarType.Byte: Variant(VarType.Byte)
}
