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
# The production URI builder itself. This test deliberately does NOT keep its
# own copy of the logic: a copy would keep passing after the real code changed,
# which is precisely the failure mode the guard below exists to prevent.
from tmsforkorea.openlayers_plugin import OpenlayersPlugin

# --- [KNOWN-DEFECT REGRESSION GUARD] — see issue #1 -----------------------
# Layer classes declare a MAX_ZOOM_LEVEL (19 for the OSM base class, 17 for
# OpenTopoMap). The URI actually handed to QGIS is built by
# OpenlayersPlugin._buildXYZUri(), which hardcodes `zmax=18` and ignores the
# declared value entirely. Declared intent and effective behaviour disagree.
#
# That mismatch is a KNOWN DEFECT, tracked as issue #1, and it was decided to
# fix it in a later version — NOT here. This guard does not fix it and must not
# be read as endorsing it.
#
# What this guard does: it pins the CURRENT EFFECTIVE behaviour (18) so the
# value cannot drift silently. The expected value below is the effective one,
# not the declared one.
#
# WHEN ISSUE #1 IS FIXED, THIS GUARD WILL FAIL — AND THAT IS CORRECT.
# A failure here means "the zoom policy change actually reached the code".
# The response is to update EXPECTED_EFFECTIVE_ZMAX (or make it derive from
# MAX_ZOOM_LEVEL, once that is what the plugin honours) — never to delete the
# guard and never to wrap it so it stops reporting.
EXPECTED_EFFECTIVE_ZMAX = 18
EXPECTED_EFFECTIVE_ZMIN = 0


def build_xyz_uri(xyz_url, tile_pixel_ratio):
    """Call the production builder — no local reimplementation on purpose."""
    return OpenlayersPlugin._buildXYZUri(xyz_url, tile_pixel_ratio)


def uri_zoom_bounds(uri):
    """Extract (zmin, zmax) from a plugin URI as ints.

    Returns None for a bound that is absent or not an integer; the caller
    treats that as a failure. We parse the parameter properly instead of
    substring-matching '18', which would also match a zoom-independent '18'
    occurring inside the tile URL template.
    """
    params = urllib.parse.parse_qs(uri, keep_blank_values=True)

    def as_int(key):
        values = params.get(key)
        if not values or not values[0].isdigit():
            return None
        return int(values[0])

    return as_int('zmin'), as_int('zmax')


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

        # --- known-defect regression guard (issue #1) ---------------------
        # A mismatch here is a real failure: it means the effective zoom
        # bounds moved. It is counted, printed as FAIL, and reflected in the
        # exit code. It is never caught, skipped, or downgraded.
        effective_zmin, effective_zmax = uri_zoom_bounds(uri)
        declared_zmax = getattr(layer_type, 'MAX_ZOOM_LEVEL', None)
        zoom_ok = (effective_zmax == EXPECTED_EFFECTIVE_ZMAX
                   and effective_zmin == EXPECTED_EFFECTIVE_ZMIN)
        zoom_status = "OK" if zoom_ok else "MISMATCH"

        status = "PASS" if (valid and tile_ok and zoom_ok) else "FAIL"
        if status == "FAIL":
            failures += 1
        print("\n[%s] %s" % (status, name))
        print("   url      : %s" % xyz)
        print("   uri      : %s" % uri)
        print("   isValid  : %s" % valid)
        print("   tile GET : %s (%s)" % (tile_ok, tile_info))
        print("   zoom     : effective zmin=%s zmax=%s -> [%s] (expected zmin=%s zmax=%s)"
              % (effective_zmin, effective_zmax, zoom_status,
                 EXPECTED_EFFECTIVE_ZMIN, EXPECTED_EFFECTIVE_ZMAX))
        # Informational only — the declared/effective disagreement is the
        # known defect (issue #1) and is NOT what makes this check fail.
        if declared_zmax is not None and declared_zmax != effective_zmax:
            print("   note     : declared MAX_ZOOM_LEVEL=%s != effective zmax=%s "
                  "(known defect, issue #1 — not fixed here)"
                  % (declared_zmax, effective_zmax))

    app.exitQgis()
    print("\n" + "-" * 72)
    print("RESULT: %d/%d passed" % (len(LAYER_TYPES) - failures, len(LAYER_TYPES)))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
