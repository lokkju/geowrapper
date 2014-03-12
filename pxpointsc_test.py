#!/usr/bin/env python


"""Test the PxPointSC API wrapper."""
# for debugging
# import pdb

import os
import sys

import pxcommon  # pylint: disable=F0401
import pxpointsc  # pylint: disable=F0401
import table  # pylint: disable=F0401

DEFAULT_LICENSE_FILE = r'f:\websites\license\pxpoint.lic'
LICENSE_KEY = 123456789
INPUT_ID_COL_NAME='Id'

OUTPUT_TABLE_COLUMNS_DEF = ';'.join(
    [
        'INPUT.{col_id}'.format(col_id=INPUT_ID_COL_NAME),
        '$Address',
        '$AddressLine',
        '$City',
        '$CityLine',
        '$County',
        '$Dataset',
        '$ExtraFound',
        '$IsIntersection',
        '$Latitude',
        '$Longitude',
        '$MatchCode',
        '$MatchDescription',
        '$Number',
        '$Postcode',
        '$State',
        '$StreetAddress',
        '$StreetName',
        '$StreetSide',
        '$UnitNumber'
    ])

ERROR_TABLE_COLUMNS_DEF = '$ErrorCode;$ErrorMessage'
FINDER_OPTIONS_DEF = '$CityPreference=Input;$ResolveMultiMatch=Both'

geocoder_handle = None
geospatial_handle = None
DATASET_ROOT = r'f:\pxse-data\geocode\PxPoint_2013_12'

def create_geocode_input_table(call_id, address_line, city_line=None):
    """Create an input table with a single row."""
    input_table = table.Table()
    input_table.append_col(INPUT_ID_COL_NAME)
    input_table.append_col('$AddressLine')
    if city_line == None:
        input_table.append_row((call_id, address_line, ))
    else:
        input_table.append_col('$CityLine')
        input_table.append_row((str(call_id), address_line, city_line))
    return input_table

def create_query_input_table(call_id, lat, lon):
    """Create an input table with a single row."""
    geometry = pxcommon.get_wkt_point_from_dec_coords(lat, lon)
    input_table = table.Table()
    input_table.append_col(INPUT_ID_COL_NAME)
    input_table.append_col('InputGeometry')
    input_table.append_row((str(call_id), geometry))
    return input_table

def setup():
    return pxpointsc.pxpointsc_init(r'f:\websites\datacatalog.xml', r'f:\pxse-data', pxpointsc.geocoder_init, pxpointsc.geospatial_init)
    """
    (geocoder_handle, return_code, return_message) = pxpointsc.geocoder_init(
        DATASET_ROOT,
        ['NavteqStreet', 'Parcel', 'USPS'],
        DEFAULT_LICENSE_FILE,
        LICENSE_KEY
    )
    if return_code != 0:
        raise RuntimeError('Code: {c}. Message: {m}'.format(c=return_code, m=return_message))
    (geospatial_handle, return_code, return_message) = pxpointsc.geospatial_init(
        r'f:\pxse-data',
        DEFAULT_LICENSE_FILE,
        LICENSE_KEY)
    if return_code != 0:
        raise RuntimeError('Code: {c}. Message: {m}'.format(c=return_code, m=return_message))
    return (geocoder_handle, geospatial_handle)
    """

def geocode(geocoder_handle, address_line, city_line):
    input_table = create_geocode_input_table(0, address_line, city_line)
    (output_table, error_table, return_code, return_message) = pxpointsc.geocoder_geocode(
        geocoder_handle,
        input_table,
        OUTPUT_TABLE_COLUMNS_DEF,
        ERROR_TABLE_COLUMNS_DEF,
        ''
    )
    if output_table != None and output_table.nrows > 0:
        print('Geocode OK')
    else:
        print(return_message)

def do(gs_handle, layer_alias, lat, lon, search_dist_meters):
    input_table = create_query_input_table(7, lat, lon)

    layer_alias_field_map = pxpointsc.geospatial_prepare(gs_handle, r'f:\websites\datacatalog.xml', r'f:\pxse-data', [ layer_alias ])
    output_columns = '[{a}]INPUT.Id;'.format(a=layer_alias) + ';'.join(layer_alias_field_map[layer_alias])

    proc_opts = 'InputGeoColumn=InputGeometry'
    if search_dist_meters <= 0:
        proc_opts = ';'.join([proc_opts, '[{a}]{o}'.format(a=layer_alias, o=pxcommon.get_spatial_relation_spec(pxcommon.SpatialRelation.WITHIN))])
    else:
        proc_opts = ';'.join([proc_opts, '[{a}]{o}'.format(a=layer_alias, o='FindNearest=T;[{a}]Distance={m}'.format(a=layer_alias, m=search_dist_meters))])

    error_cols = ERROR_TABLE_COLUMNS_DEF.replace('$', '[{a}]$'.format(a=layer_alias))
    (output_table, error_table, return_code, return_message) = pxpointsc.geospatial_query(
        gs_handle,
        input_table,
        output_columns,
        error_cols,
        proc_opts
    )
    if output_table != None and output_table.nrows > 0:
        print('Query OK')
        for i in range(output_table.nrows()):
            row = output_table.rows[i]
            for j in range(output_table.ncols()):
                print(output_table.col_names[j] + ': ' + str(row[j]))
    else:
        print(return_message)

def query(gs_handle, layer_path, layer_alias, lat, lon, search_dist_meters, attach=True):
    input_table = create_query_input_table(7, lat, lon)
    print(input_table.ncols())
    print(input_table.rows[0])
    # attach the layer
    if attach:
        (return_code, return_message) = pxpointsc.geospatial_attach_layer(gs_handle, layer_path, layer_alias)
        if return_code != 0:
            raise RuntimeError('Code: {c}. Message: {m}'.format(c=return_code, m=return_message))

    # get the layer attributes
    fields = pxpointsc.geospatial_layer_info(gs_handle, layer_alias)
    fields = ['[{a}]{f}'.format(a=layer_alias, f=x) for x in fields]
    output_columns = '[County]INPUT.Id;' + ';'.join(fields)

    # pdb.set_trace()
    # query using these attributes
    proc_opts = 'InputGeoColumn=InputGeometry'
    if search_dist_meters <= 0:
        proc_opts = ';'.join([proc_opts, '[{a}]{o}'.format(a=layer_alias, o=pxcommon.get_spatial_relation_spec(pxcommon.SpatialRelation.WITHIN))])
    else:
        proc_opts = ';'.join([proc_opts, '[{a}]{o}'.format(a=layer_alias, o='FindNearest=T;[{a}]Distance={m}'.format(a=layer_alias, m=search_dist_meters))])

    error_cols = ERROR_TABLE_COLUMNS_DEF.replace('$', '[{a}]$'.format(a=layer_alias))
    print('Output cols: ' + output_columns)
    print('Query options: ' + proc_opts)
    print('Error cols: ' + error_cols)
    (output_table, error_table, return_code, return_message) = pxpointsc.geospatial_query(
        gs_handle,
        input_table,
        output_columns,
        error_cols,
        proc_opts
    )
    if output_table != None and output_table.nrows > 0:
        print('Query OK')
        for i in range(output_table.nrows()):
            row = output_table.rows[i]
            for j in range(output_table.ncols()):
                print(output_table.col_names[j] + ': ' + str(row[j]))
    else:
        print(return_message)


(geocoder_handle, geospatial_handle) = setup()
geocode(geocoder_handle, '2477 55 St', 'Boulder, CO')
do(geospatial_handle, 'County', 40, -105, 0)
#query(geospatial_handle, r'f:\pxse-data\political\County_2013_10\County_2013_10.shp', 'County', 40, -105, 0)
#query(geospatial_handle, r'f:\pxse-data\political\County_2013_10\County_2013_10.shp', 'County', 40, -105, 100000, False)
