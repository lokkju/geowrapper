#!/usr/bin/env python
#
# $Id: tableset.py 10059 2013-01-31 22:39:34Z tschutter $
#

"""Proxix::TableSet (geocoder/PxLib/TableSet.cpp) wrapper."""

import struct

import table
import variant

TABLESET_MAGIC_NUMBER=0x8c54ecce


class TableSet:
    """Proxix::TableSet (geocoder/PxLib/TableSet.cpp) wrapper."""
    def __init__(self):
        self.tables = dict()

    def deserialize(self, buff):
        """Deserialize the table from a bytearray."""
        offset = 0

        # Tableset magic number.
        (magic, ) = struct.unpack_from("<I", buff, offset)
        offset += 4
        if magic != TABLESET_MAGIC_NUMBER:
            raise ValueError(
                "Invalid tableset magic number. 0x%0x != 0x%0x" % (
                    magic,
                    TABLESET_MAGIC_NUMBER
                )
            )

        # Number of tables.
        (ntables, ) = struct.unpack_from("<i", buff, offset)
        offset += 4

        # Table names.
        table_names = list()
        for _ in range(ntables):
            table_name, _, offset = variant.Variant.deserialize(buff, offset)
            table_names.append(table_name)

        # Tables.
        for table_name in table_names:
            newtable = table.Table()
            offset = newtable.deserialize(buff, offset)
            self.tables[table_name] = newtable
