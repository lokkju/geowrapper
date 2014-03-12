#!/usr/bin/env python
#
# $Id: table.py 10059 2013-01-31 22:39:34Z tschutter $
#

"""Proxix::Table (geocoder/PxLib/Table.cpp) wrapper."""

import struct

import variant

TABLE_MAGIC_NUMBER=0xab13254
DEBUG_COL_TYPES = False


class Table:
    """Proxix::Table (geocoder/PxLib/Table.cpp) wrapper."""
    def __init__(self):
        self.col_names = list()
        self.col_var_types = list()
        self.rows = list()

    def append_col(self, col_name, col_var_type=None):
        """Append a column to the table."""
        self.col_names.append(col_name)
        if col_var_type == None:
            self.col_var_types.append(variant.VarType.String)
        else:
            self.col_var_types.append(col_var_type)

    def ncols(self):
        """Return number of columns."""
        return len(self.col_names)

    def append_row(self, row):
        """Append a row to the table."""
        self.rows.append(row)

    def nrows(self):
        """Return number of rows."""
        return len(self.rows)

    def is_empty(self):
        """Return True if the table has no rows."""
        return len(self.rows) == 0

    def row(self, index):
        """Return row by index."""
        return self.rows[index]

    def serialize(self):
        """Serialize the table to a bytearray that will be read by
        Table::Deserialize() in geocoder/PxLib/Table.cpp."""
        nrows = len(self.rows)
        ncolumns = len(self.col_names)
        if ncolumns == 0:
            raise ValueError("Table contains no columns")

        buff = bytearray(4 * 1024 * 1024)
        offset = 0

        # Table magic number.
        struct.pack_into("<I", buff, offset, TABLE_MAGIC_NUMBER)
        offset += 4

        # Number of columns.
        struct.pack_into("<i", buff, offset, ncolumns)
        offset += 4

        # Number of rows.
        struct.pack_into("<i", buff, offset, len(self.rows))
        offset += 4

        # Column data types.
        col_variants = list()
        for col_var_type in self.col_var_types:
            col_variants.append(variant.Variant(col_var_type))
            struct.pack_into("B", buff, offset, col_var_type)
            offset += 1

        # Column names.
        string_variant = variant.Variant(variant.VarType.String)
        for col_name in self.col_names:
            offset = string_variant.serialize(buff, offset, col_name)

        # Cell values.
        for row in self.rows:
            for col_variant, value in zip(col_variants, row):
                offset = col_variant.serialize(buff, offset, value)

        return (buff, offset)

    def deserialize(self, buff, offset):
        """Deserialize the table from a bytearray created by
        Table::Serialize() in geocoder/PxLib/Table.cpp. and
        ByteWriter::writeVariant in geocoder/PxLib/ByteWriter.cpp"""

        # Table magic number.
        (magic, ) = struct.unpack_from("<I", buff, offset)
        offset += 4
        if magic != TABLE_MAGIC_NUMBER:
            raise ValueError(
                "Invalid table magic number. %0x != %0x" % (
                    magic, TABLE_MAGIC_NUMBER
                )
            )

        # Number of columns.
        (ncolumns, ) = struct.unpack_from("<i", buff, offset)
        offset += 4

        # Number of rows.
        (nrows, ) = struct.unpack_from("<i", buff, offset)
        offset += 4

        # Column data types.
        col_variants = list()
        for _ in range(ncolumns):
            (col_var_type, ) = struct.unpack_from("B", buff, offset)
            offset += 1
            self.col_var_types.append(col_var_type)
            col_variants.append(variant.Variant(col_var_type))
        if DEBUG_COL_TYPES:
            print "  col_var_types =", self.col_var_types

        # Column names.
        for _ in range(ncolumns):
            col_name, _, offset = variant.Variant.deserialize(buff, offset)
            self.col_names.append(str(col_name))
        if DEBUG_COL_TYPES:
            print "  col_names =", self.col_names

        # Cell values.
        for rownum in range(nrows):
            row = list()
            for colnum, col_variant in enumerate(col_variants):
                value, var_type, offset = variant.Variant.deserialize(
                    buff,
                    offset
                )
                row.append(value)
                if col_variant.var_type != var_type:
                    raise AssertionError(
                        "  Cell[%i][%i] type=%s does not match col type=%s" % (
                            rownum,
                            colnum,
                            var_type,
                            col_variant.var_type
                        )
                    )
            self.rows.append(row)

        # Return the current offset.
        return offset

    def __str__(self):
        """Create human-readable representation of the table."""
        # Determine the column widths.
        max_widths = [0] * len(self.col_names)
        for col, name in enumerate(self.col_names):
            max_widths[col] = max(max_widths[col], len(name))
        for row in self.rows:
            for col, value in enumerate(row):
                max_widths[col] = max(
                    max_widths[col],
                    len("%s" % str(value).encode("unicode_escape"))
                )

        # Create a horizontal divider.
        divider = "+%s+\n" % "+".join(
            "-" * (max_width + 2) for max_width in max_widths
        )

        string = (
            divider +
            "| %s |\n" % " | ".join(
                "%-*s" % (max_widths[col], value)
                for col, value in enumerate(self.col_names)
            ) +
            divider +
            "".join(
                "| %s |\n" % " | ".join(
                    "%-*s" % (
                        max_widths[col],
                        str(value).encode("unicode_escape")
                    )
                    for col, value in enumerate(row)
                )
                for row in self.rows
            ) +
            divider
        )

        return string

    def str_csv(self, delimiter=None):
        """Create CSV representation of the table."""
        if delimiter == None:
            delimiter = "|"
        string = "\n".join(
            delimiter.join(
                str(value).encode("unicode_escape")
                for col, value in enumerate(row)
            )
            for row in self.rows
        ) + "\n"
        return string
