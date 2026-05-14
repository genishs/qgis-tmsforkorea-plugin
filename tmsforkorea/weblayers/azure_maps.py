# -*- coding: utf-8 -*-
"""
Azure Maps support for TMS for Korea.

Microsoft retired Bing Maps for Enterprise (no new keys after 2024-06-30,
existing keys end-of-life 2028-06-30). Azure Maps is the successor and uses
a standard {z}/{x}/{y} XYZ tile pattern that QGIS's native XYZ provider can
consume directly — no quadkey transform required.

A user-supplied subscription key is mandatory; the free S0 tier covers
casual map browsing. The key is stored in QSettings at
``Plugin-OpenLayers/azure_maps_key`` and read lazily so a key set after
plugin load takes effect without restart.
"""

from qgis.PyQt.QtCore import QSettings
from .weblayer import WebLayer3857


AZURE_MAPS_KEY_SETTING = "Plugin-OpenLayers/azure_maps_key"
AZURE_MAPS_API_VERSION = "2024-04-01"
AZURE_MAPS_SIGNUP_URL = "https://azure.microsoft.com/products/azure-maps"


def getAzureMapsKey():
    """Return the configured Azure Maps subscription key or an empty string."""
    return QSettings().value(AZURE_MAPS_KEY_SETTING, "", type=str)


def setAzureMapsKey(key):
    """Persist *key* in QSettings (or clear it when *key* is empty)."""
    QSettings().setValue(AZURE_MAPS_KEY_SETTING, key or "")


def buildAzureMapsUrl(tilesetId):
    """Construct the Azure Maps tile URL template for *tilesetId*.

    Returns ``None`` when no subscription key is configured so callers can
    surface a friendly UX instead of attempting an inevitable 401.
    """
    key = getAzureMapsKey()
    if not key:
        return None
    return (
        "https://atlas.microsoft.com/map/tile"
        "?api-version=" + AZURE_MAPS_API_VERSION +
        "&tilesetId=" + tilesetId +
        "&zoom={z}&x={x}&y={y}"
        "&subscription-key=" + key
    )


class OlAzureMapsLayer(WebLayer3857):
    """Base class for all Azure Maps tilesets (EPSG:3857)."""

    groupName = 'Azure Maps'
    groupIcon = 'openlayers.png'  # reuse existing resource; future: dedicated icon
    epsgList = [3857]
    fullExtent = [-20037508.34, -20037508.34, 20037508.34, 20037508.34]
    MIN_ZOOM_LEVEL = 0
    MAX_ZOOM_LEVEL = 22
    SCALE_ON_MAX_ZOOM = 13540
    emitsLoadEnd = False

    def __init__(self, name, tilesetId):
        self._tilesetId = tilesetId
        WebLayer3857.__init__(
            self,
            groupName=self.groupName,
            groupIcon=self.groupIcon,
            name=name,
            html=None,
            xyzUrl=buildAzureMapsUrl(tilesetId),
        )

    # Re-read the key on every access so users who configure the key after
    # plugin load do not need to restart QGIS.
    def hasXYZUrl(self):
        return buildAzureMapsUrl(self._tilesetId) is not None

    def xyzUrlConfig(self):
        return buildAzureMapsUrl(self._tilesetId)


class OlAzureRoadLayer(OlAzureMapsLayer):
    def __init__(self):
        OlAzureMapsLayer.__init__(self, name='Azure Road',
                                  tilesetId='microsoft.base.road')


class OlAzureSatelliteLayer(OlAzureMapsLayer):
    def __init__(self):
        OlAzureMapsLayer.__init__(self, name='Azure Satellite',
                                  tilesetId='microsoft.imagery')


class OlAzureHybridLayer(OlAzureMapsLayer):
    def __init__(self):
        OlAzureMapsLayer.__init__(self, name='Azure Hybrid',
                                  tilesetId='microsoft.base.hybrid')
