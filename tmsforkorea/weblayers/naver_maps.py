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

import requests
from qgis.core import (Qgis, QgsCoordinateReferenceSystem, QgsMessageLog)
from .weblayer import WebLayer3857

# Verified live 2026-05-14
NAVER_FALLBACK_VERSION = "1778232861"

# Per-style version cache (populated on first successful fetch per session)
_NAVER_VERSION_CACHE = {}

# Tracks which styles have already emitted a fetch-failure warning this session
_NAVER_FETCH_FAILED = set()


def _resolveNaverVersion(style):
    """Return the live Naver tile version token for *style*, falling back to
    NAVER_FALLBACK_VERSION if the discovery endpoint is unreachable or the
    response cannot be parsed.  Results are cached per-style for the lifetime
    of the Python interpreter session."""
    if style in _NAVER_VERSION_CACHE:
        return _NAVER_VERSION_CACHE[style]

    try:
        url = (
            f"https://map.pstatic.net/nrb/styles/{style}.json"
            f"?fmt=jpg&mt=bg.ol.ts.ar.lko"
        )
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        version = response.json()["version"]
        _NAVER_VERSION_CACHE[style] = version
        return version
    except Exception:
        if style not in _NAVER_FETCH_FAILED:
            _NAVER_FETCH_FAILED.add(style)
            QgsMessageLog.logMessage(
                "Naver: could not fetch live version for style '%s', using fallback '%s'. "
                "Tiles may degrade if Naver rotates the token." % (style, NAVER_FALLBACK_VERSION),
                "OpenLayers Plugin",
                Qgis.MessageLevel.Warning,
            )
        return NAVER_FALLBACK_VERSION


class OlNaverMapsLayer(WebLayer3857):

    # Group in menu
    groupName = 'Naver Maps v5'

    # Group icon in menu
    groupIcon = 'naver_icon.png'

    # Supported EPSG projections, ordered by preference
    epsgList = [3857]

    # WGS84 bounds
    fullExtent = [124.41714675, 33.0022776231, 131.971482078, 38.6568782776]

    MIN_ZOOM_LEVEL = 6

    MAX_ZOOM_LEVEL = 17

    # QGIS scale for 72 dpi
    SCALE_ON_MAX_ZOOM = 13540

    emitsLoadEnd = False

    def __init__(self, name, html, xyzUrl, tilePixelRatio=2):
        WebLayer3857.__init__(self, groupName=self.groupName, groupIcon=self.groupIcon,
                              name=name, html=html, xyzUrl=xyzUrl, tilePixelRatio=tilePixelRatio)


class OlNaverStreetLayer(OlNaverMapsLayer):
    # style=basic, mt=bg.ol.ts.lko

    def __init__(self):
        version = _resolveNaverVersion("basic")
        tmsUrl = f"https://map.pstatic.net/nrb/styles/basic/{version}/{{z}}/{{x}}/{{y}}@2x.png?mt=bg.ol.ts.lko"
        OlNaverMapsLayer.__init__(self, name="Naver Street", html="naver_street.html", xyzUrl=tmsUrl)


class OlNaverHybridLayer(OlNaverMapsLayer):
    # style=satellite, mt=bg.ol.ts.lko (satellite base + label overlay)

    def __init__(self):
        version = _resolveNaverVersion("satellite")
        tmsUrl = f"https://map.pstatic.net/nrb/styles/satellite/{version}/{{z}}/{{x}}/{{y}}@2x.png?mt=bg.ol.ts.lko"
        OlNaverMapsLayer.__init__(self, name="Naver Hybrid", html="naver_hybrid.html", xyzUrl=tmsUrl)


class OlNaverSatelliteLayer(OlNaverMapsLayer):
    # style=satellite, mt=bg.ol.ts

    def __init__(self):
        version = _resolveNaverVersion("satellite")
        tmsUrl = f"https://map.pstatic.net/nrb/styles/satellite/{version}/{{z}}/{{x}}/{{y}}@2x.png?mt=bg.ol.ts"
        OlNaverMapsLayer.__init__(self, name="Naver Satellite", html="naver_satellite.html", xyzUrl=tmsUrl)


class OlNaverPhysicalLayer(OlNaverMapsLayer):
    # style=terrain, mt=bg.ol.ts.lko

    def __init__(self):
        version = _resolveNaverVersion("terrain")
        tmsUrl = f"https://map.pstatic.net/nrb/styles/terrain/{version}/{{z}}/{{x}}/{{y}}@2x.png?mt=bg.ol.ts.lko"
        OlNaverMapsLayer.__init__(self, name="Naver Physical", html="naver_physical.html", xyzUrl=tmsUrl)


class OlNaverCadastralLayer(OlNaverMapsLayer):
    # DEFERRED to 4.1
    # style=basic, mt=bg.ol.ts.lp

    def __init__(self):
        version = _resolveNaverVersion("basic")
        tmsUrl = f"https://map.pstatic.net/nrb/styles/basic/{version}/{{z}}/{{x}}/{{y}}@2x.png?mt=bg.ol.ts.lp"
        OlNaverMapsLayer.__init__(self, name="Naver Cadastral", html="naver_cadastral.html", xyzUrl=tmsUrl)
