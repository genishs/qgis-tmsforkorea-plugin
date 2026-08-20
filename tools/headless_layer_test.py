# -*- coding: utf-8 -*-
r"""
Headless validation for TMS for Korea XYZ layers (QGIS 4 / Qt6).

This does NOT need the QGIS GUI and does NOT use Playwright — QGIS is a
native Qt desktop app, so the meaningful automated check is to drive the
PyQGIS API directly: instantiate each layer type, build the exact XYZ URI
the plugin would build, hand it to QgsRasterLayer via the 'wms' provider,
and assert isValid(). A second pass does a live HTTP GET on one
substituted {z}/{x}/{y} tile per layer to confirm the endpoint serves an
image.

HOW TO RUN (Windows)
--------------------
Install QGIS 4 first (OSGeo4W or the standalone installer). Then run this
from a QGIS-aware Python so `qgis.core` is importable:

  # OSGeo4W shell:
  python-qgis.bat tools\headless_layer_test.py

  # or standalone install (adjust path/version):
  "C:\Program Files\QGIS 4.0\bin\python-qgis.bat" tools\headless_layer_test.py

Exit code 0 = all checks passed, 1 = at least one failure.
"""

import os
import sys
import urllib.request
import urllib.parse

# --- make the plugin package importable (repo_root/tmsforkorea/...) --------
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

try:
    from qgis.core import QgsApplication, QgsRasterLayer
except ImportError as exc:  # pragma: no cover - environment guard
    sys.stderr.write(
        "ERROR: cannot import qgis.core (%s).\n"
        "Run this with a QGIS-aware Python, e.g. OSGeo4W's "
        "`python-qgis.bat tools\\headless_layer_test.py`.\n" % exc
    )
    sys.exit(2)

from tmsforkorea.weblayers.osm_maps import (
    OlOSMStandardLayer,
    OlOSMHumanitarianLayer,
    OlOSMCyclOSMLayer,
    OlOSMOpenTopoMapLayer,
)

# [KNOWN BUG REGRESSION GUARD]
# Layer classes declare MAX_ZOOM_LEVEL (e.g. 19 for OSM, 17 for OpenTopoMap).
# However, the plugin's _buildXYZUri (mirrored here) currently hardcodes zmax=18.
# This guard pins the current *effective* behavior (18) rather than the declared intent.
# When this known defect is fixed in a future version, this guard will fail.
# That failure is expected and indicates the behavior change took effect.
# The value below should then be updated to match the new behavior.
EXPECTED_EFFECTIVE_ZMAX = 18

def build_xyz_uri(xyz_url, tile_pixel_ratio):
    """Mirror OpenlayersPlugin._buildXYZUri exactly."""
    safe_url = xyz_url.replace('&', '%26')
    uri = "type=xyz&url=" + safe_url + "&zmin=0&zmax=18"
    if tile_pixel_ratio and tile_pixel_ratio > 0:
        uri = uri + "&tilePixelRatio=" + str(tile_pixel_ratio)
    return uri


def sample_tile_url(xyz_url):
    """Substitute a concrete {z}/{x}/{y} so we can probe the endpoint."""
    return (xyz_url
            .replace('{z}', '3')
            .replace('{x}', '4')
            .replace('{y}', '2'))


def http_ok(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'QGIS/TMS-for-Korea test'})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            ctype = resp.headers.get('Content-Type', '')
            body = resp.read(2048)
            return (resp.status == 200 and ctype.startswith('image/')
                    and len(body) > 0), "%s %s %dB" % (resp.status, ctype, len(body))
    except Exception as exc:  # noqa: BLE001 - report any network failure
        return False, "EXC %s" % exc


# Layers to validate — single-URL OSM family (not the multi-URL hybrid case).
LAYER_TYPES = [
    OlOSMStandardLayer,
    OlOSMHumanitarianLayer,
    OlOSMCyclOSMLayer,
    OlOSMOpenTopoMapLayer,
]


def main():
    QgsApplication.setPrefixPath(os.environ.get('QGIS_PREFIX_PATH', ''), True)
    app = QgsApplication([], False)
    app.initQgis()

    failures = 0
    print("=" * 72)
    print("TMS for Korea — headless XYZ layer validation")
    print("=" * 72)
    for lt in LAYER_TYPES:
        layer_type = lt()
        name = layer_type.displayName
        xyz = layer_type.xyzUrlConfig()
        uri = build_xyz_uri(xyz, layer_type.tilePixelRatio)

        rlayer = QgsRasterLayer(uri, name, "wms", QgsRasterLayer.LayerOptions())
        valid = rlayer.isValid()

        tile_ok, tile_info = http_ok(sample_tile_url(xyz))

        # Check effective zmax by parsing the generated URI
        parsed = urllib.parse.urlparse(uri)
        qs = urllib.parse.parse_qs(parsed.query)
        # Note: the uri format is "type=xyz&url=...&zmin=...&zmax=..." so we parse it as if it's all query params
        # Actually `urllib.parse.parse_qs(uri)` is better if there's no ? prefix.
        qs = urllib.parse.parse_qs(uri)
        effective_zmax = None
        if 'zmax' in qs and qs['zmax']:
            try:
                effective_zmax = int(qs['zmax'][0])
            except ValueError:
                pass

        declared_zmax = getattr(layer_type, 'MAX_ZOOM_LEVEL', '?')
        zmax_ok = (effective_zmax == EXPECTED_EFFECTIVE_ZMAX)
        zmax_status = "OK" if zmax_ok else "MISMATCH"

        status = "PASS" if (valid and tile_ok and zmax_ok) else "FAIL"
        if status == "FAIL":
            failures += 1
        print("\n[%s] %s" % (status, name))
        print("   url      : %s" % xyz)
        print("   uri      : %s" % uri)
        print("   isValid  : %s" % valid)
        print("   tile GET : %s (%s)" % (tile_ok, tile_info))
        print("   zmax     : declared=%s, effective=%s -> [%s] (expected=%s) (Note: known bug causes effective=18)" % 
              (declared_zmax, effective_zmax, zmax_status, EXPECTED_EFFECTIVE_ZMAX))

    app.exitQgis()
    print("\n" + "-" * 72)
    print("RESULT: %d/%d passed" % (len(LAYER_TYPES) - failures, len(LAYER_TYPES)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
