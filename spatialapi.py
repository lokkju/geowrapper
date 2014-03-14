#!/usr/bin/env python
#
# $Id$
#

"""CoreLogic GeoSpatial API module.

Two classes are exposed by this module:

    GeoSpatial
    StatusCode

GeoSpatial is a thin client to the PxPointSC wrapper (pxpointsc.py).

"""
# for logging information about calls
import logging
import socket
import datetime
# geocoder and spatial analyzer
import pxpointsc
# supporting libs for pxpointsc
import pxcommon
import table
# supporting lib for spatialapi
import json
import datacatalog

# Standard status codes
class _StatusCode:
    OK = "OK"
    NO_RESULTS = "NO_RESULTS"
    INVALID_REQUEST = "INVALID_REQUEST"
    SERVER_ERROR = "SERVER_ERROR"

class GeoSpatial:
    """Conducts geocoding and spatial operations on addresses and points.

    Instances must be initialized with a path to a data catalog, and the root 
    directory for where shapefiles are located. These are used to initialize 
    the PxPointSC object that performs all geocoding and spatial operations.

    For example:
        geo_spatial = GeoSpatial(r"f:\websites\datacatalog.xml", "f:\pxse-data")
    """

    # Static member fields

    __INPUT_ID_COL_NAME = "Id"

    __INPUT_GEOMETRY_COL_NAME = "InputGeometry"

    __INPUT_ADDRESS_COL_NAME = "$Address"

    __ERROR_TABLE_COLS = "$ErrorCode;$ErrorMessage"

    __GEOCODING_OUTPUT_COLS = ";".join(
        [
            "INPUT.{col_id}".format(col_id=__INPUT_ID_COL_NAME),
            "$AddressLine",
            "$City",
            "$CityLine",
            "$County",
            "$Dataset",
            "$ExtraFound",
            "$IsIntersection",
            "$Latitude",
            "$Longitude",
            "$MatchCode",
            "$MatchDescription",
            "$Number",
            "$Postcode",
            "$State",
            "$StreetAddress",
            "$StreetName",
            "$StreetSide",
            "$UnitNumber"
        ])


    def __init__(
            self, data_catalog_path=r"f:\websites\datacatalog.xml", 
            shapefile_root_dir=r"f:\pxse-data"):
        self.__data_catalog = datacatalog.DataCatalog(data_catalog_path, 
            shapefile_root_dir)
        # geocoder and spatial processors are lazily initialized
        self.__geocoder_handle = None
        self.__geospatial_handle = None


    @staticmethod
    def create_address_input_table(self, call_id, address):
        """Creates an input table with a single row containing an address."""
        input_table = table.Table()
        input_table.append_col(Spatial.__INPUT_ID_COL_NAME)
        input_table.append_col(Spatial.__INPUT_ADDRESS_COL_NAME)
        input_table.append_row((call_id, address))
        return input_table


    @staticmethod
    def create_server_error_json_result(message):
        """Creates a JSON string from a server error message."""
        status = _StatusCode.SERVER_ERROR
        return_obj = {}
        return_obj["result"] = []
        return_obj["status"] = status
        return_obj["message"] = message
        return (status, json.dumps(return_obj, sort_keys=True))

    @staticmethod
    def create_json_result_with_status(
            self, output_table, error_table, return_code, max_results=-1):
        """Creates a JSON string from a PxPointSC result."""
        result = []
        status = _StatusCode.OK
        message = ""
        if return_code == pxcommon.PXP_SUCCESS:
            if (output_table is None or output_table.nrows == 0):
                status  = _StatusCode.SERVER_ERROR
                message = "Output table is empty, despite successful geocode"
            else:
                for i in range(output_table.nrows()):
                    current = {}
                    row = output_table.rows[i]
                    for j in range(output_table.ncols()):
                        current[output_table.col_names[j]] = str(row[j]).encode(
                            "unicode_escape")
                    result.append(current)
                    if i == max_results:
                        break
        elif error_table is None or error_table.nrows == 0:
            status  = _StatusCode.SERVER_ERROR
            message = "Error table is empty, despite apparent error"
        else:
            error_row = error_table.rows[0]
            error_code = str(error_row[0])
            error_message = str(error_row[1])
            if return_code == pxcommon.PXP_INVALID_ARGUMENT:
                status = _StatusCode.INVALID_REQUEST
            else:
                status, error_message = self.get_error_status_from_code(error_code)
            message = "Code: {c}. Message: {m}".format(c=error_code, m=error_message)
        return_obj = {}
        return_obj["result"] = result
        return_obj["status"] = status
        return_obj["message"] = message
        return status, json.dumps(return_obj, sort_keys=True) 

    def get_location(self, call_id, address):
        """Geocodes an address, by matching it to a location record.

        Args:
            call_id (str): A geocode call identifier, for logging purposes.
            address (str): An address (e.g., '123 main st, boulder co').

        Returns:
            A JSON-formatted string containing results and a status code.
        """


        # Lazily initialize the geocoder handle.
        if self.__geocoder_handle is None:
            self.__geocoder_handle = pxpointsc.geocoder_init(
                self.__data_catalog)

        # Create an input table from the call id and the address
        input_table = self.create_address_input_table(call_id, address)

        # Call the geocoder and get the results
        output_table, error_table, return_code, _ = pxpointsc.geocoder_geocode(
            self.__geocoder_handle,
            input_table,
            GeoSpatial.__GEOCODING_OUTPUT_COLS,
            GeoSpatial.__ERROR_TABLE_COLS,
            "" # we don't use any processing options right now
        )

        # Build and return the JSON encoding of the results
        status, json_results = self.create_json_results_with_status(
            output_table, error_table, return_code)
        return json_results


    def query_layer(
            self, call_id, layer_name, lat, lon, output_fields=None, 
            where_clause=None, search_dist_meters=0, max_results=1):
        """Queries a layer about a location.

        Args:
            call_id (str): A layer query identifier, for logging purposes.
            layer_name (str): The name of the layer to be queried. This name
                must be a key to the spatial_layers dictionary of the data 
                catalog supplied to this instance's constructor.
            lat (float): The location's latitude, a double in decimal degrees.
            lon (float): The location's longitude, a double in decimal degrees.
            output_fields (str, optional): The desired metadata fields from the 
                layer. The default value, None, means all fields should be 
                returned.
            where_clause (str, optional): A SQL or codebase where-clause for
                filtering results. The default value, None, means no 
                where-clause.
            search_dist_meters (int, optional): the maximum distance from the 
                location, in meters, to search for features in the layer.
        Returns:
            A JSON-formatted string containing results and a status code.
        """
        pass


