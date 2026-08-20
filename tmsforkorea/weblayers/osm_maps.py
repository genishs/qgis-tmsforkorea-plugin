# -*- coding: utf-8 -*-
"""
/***************************************************************************
OpenLayers Plugin
A QGIS plugin

                             -------------------
begin                : 2018-11-23
copyright            : (C) 2009 by Minpa Lee, MangoSystem
email                : mapplus at gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from .weblayer import WebLayer3857


class OlOSMLayer(WebLayer3857):

    # Group in menu
    groupName = 'OpenStreetMap'

    # Group icon in menu (reuses existing resource, no new bake required)
    groupIcon = 'openlayers.png'

    # Supported EPSG projections, ordered by preference
    epsgList = [3857]

    # Web Mercator world bounds
    fullExtent = [-20037508.34, -20037508.34, 20037508.34, 20037508.34]

    MIN_ZOOM_LEVEL = 0

    MAX_ZOOM_LEVEL = 19

    # QGIS scale for 72 dpi
    SCALE_ON_MAX_ZOOM = 13540

    emitsLoadEnd = False

    attribution = "© OpenStreetMap contributors"

    def __init__(self, name, xyzUrl, displayName=None):
        WebLayer3857.__init__(self, groupName=self.groupName, groupIcon=self.groupIcon,
                              name=name, html=None, xyzUrl=xyzUrl,
                              displayName=displayName)


class OlOSMStandardLayer(OlOSMLayer):

    def __init__(self):
        OlOSMLayer.__init__(self, name='OSM Standard',
                            xyzUrl='https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                            displayName='OSM 기본지도')


class OlOSMHumanitarianLayer(OlOSMLayer):
    # Humanitarian (HOT) style, served by OpenStreetMap France. Subdomains
    # a/b/c exist; QGIS's XYZ provider has no {s} rotation, so pin one host.
    attribution = "© OpenStreetMap contributors, Humanitarian OSM Team, " \
                  "tiles courtesy of OpenStreetMap France"

    def __init__(self):
        OlOSMLayer.__init__(self, name='OSM Humanitarian',
                            xyzUrl='https://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
                            displayName='OSM 인도주의(HOT)')


class OlOSMCyclOSMLayer(OlOSMLayer):
    # CyclOSM — bicycle-oriented style, also hosted by OpenStreetMap France.
    attribution = "© OpenStreetMap contributors, CyclOSM, " \
                  "tiles courtesy of OpenStreetMap France"

    def __init__(self):
        OlOSMLayer.__init__(self, name='OSM CyclOSM',
                            xyzUrl='https://a.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png',
                            displayName='OSM 자전거(CyclOSM)')


class OlOSMOpenTopoMapLayer(OlOSMLayer):
    # OpenTopoMap — topographic style. Tile data tops out around z17.
    MAX_ZOOM_LEVEL = 17
    attribution = "© OpenStreetMap contributors, SRTM | map style: " \
                  "© OpenTopoMap (CC-BY-SA)"

    def __init__(self):
        OlOSMLayer.__init__(self, name='OSM OpenTopoMap',
                            xyzUrl='https://a.tile.opentopomap.org/{z}/{x}/{y}.png',
                            displayName='OSM 지형도(OpenTopoMap)')
