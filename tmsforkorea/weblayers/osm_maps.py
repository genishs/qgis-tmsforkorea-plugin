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

    def __init__(self, name, xyzUrl):
        WebLayer3857.__init__(self, groupName=self.groupName, groupIcon=self.groupIcon,
                              name=name, html=None, xyzUrl=xyzUrl)


class OlOSMStandardLayer(OlOSMLayer):

    def __init__(self):
        OlOSMLayer.__init__(self, name='OSM Standard',
                            xyzUrl='https://tile.openstreetmap.org/{z}/{x}/{y}.png')
