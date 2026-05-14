TMS for Korea
=======================

> **QGIS 4.x branch (`4.x/main`) — v4.0.0**
> This branch is the QGIS 4 (Qt6) port. The legacy WebKit-based renderer
> has been replaced with XYZ tile providers. The `master` branch remains
> the QGIS 3.x release line for users still on Qt5 builds.
>
> Install via QGIS plugin manager: **Plugins → Manage and Install →
> Install from ZIP** with `latest-binary/tmsforkorea-4.0.0.zip`.


QGIS TMS Plugin for Korean users
------------------------------
 - VWorld(Street, Gray, Satellite, Hybrid) Maps
 - Naver(Street, Hybrid, Satellite, Physical) Maps — Cadastral deferred to 4.1
 - OpenStreetMap Standard
 - Kakao(Daum), NGII — deferred to 4.1+ (Qt6 has no QtWebKit; restoring these
   needs the GDAL TMS minidriver for EPSG:5181/5179)
 - Mango — upstream server unreachable as of 2026-05-14


Migration record
------------------------------
 - 3.x → 4.x 포팅 전체 기록: [MIGRATION.md](MIGRATION.md) — 목적, 계획, 단계별 실행 로그, 핫픽스, 회고, 4.1 로드맵.


Plugins Repository
------------------------------
 - http://plugins.qgis.org/plugins/tmsforkorea/

Related Projects
------------------------------
 - ported from qgis-openlayers-plugin[https://github.com/sourcepole/qgis-openlayers-plugin]

License
----------
 - tmsforkorea plugin is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version.

Gallery
---------

![screenshot](https://github.com/mapplus/qgis-tmsforkorea-plugin/blob/master/images/tmsforkorea_overview.png?width=800)

