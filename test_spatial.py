#!/usr/bin/env python
#
# $Id$
#

""" Test of SpatialAPI. """

import spatialapi
import json

config = {}
execfile('spatialapi.conf', config)
sapi = spatialapi.SpatialAPI(config)
"""
result = sapi.get_location('17', '2477 55 St Boulder CO')
r = json.loads(result)
# print(json.dumps(r, indent=4, sort_keys=True, separators=(',', ': ')))
print(sapi._datacatalog.spatial_layers.keys())
first = sapi.query_layer('18', 'County', 40, -105, 0)
f = json.loads(first)
print(json.dumps(f, indent=4, sort_keys=True, separators=(',', ': ')))
# result = sapi.query_layer('18', 'County', 40, -105)
#r = json.loads(result)
#print(json.dumps(r, indent=4, sort_keys=True, separators=(',', ': ')))
"""
