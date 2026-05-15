TMS for Korea
=======================

> **QGIS 4.x branch (`4.x/main`) — v4.1.2**
> This branch is the QGIS 4 (Qt6) port. The legacy WebKit-based renderer
> has been replaced with XYZ tile providers. The `master` branch remains
> the QGIS 3.x release line for users still on Qt5 builds.
>
> Install via QGIS plugin manager: **Plugins → Manage and Install →
> Install from ZIP** with `latest-binary/tmsforkorea-4.1.2.zip`.
>
> - **v4.1.1**: Fix Naver tile loading by working around an upstream
>   `User-Agent` filter that rejected QGIS's default UA string.
> - **v4.1.2**: Hotfix — "Configure Azure Maps Key…" raised
>   `AttributeError: QLineEdit.Normal` under PyQt6; replaced with the
>   fully-qualified `QLineEdit.EchoMode.Normal`.


QGIS TMS Plugin for Korean users
------------------------------
 - VWorld(Street, Gray, Satellite, Hybrid) Maps
 - Naver(Street, Hybrid, Satellite, Physical, Cadastral) Maps
 - OpenStreetMap Standard
 - Azure Maps (Road, Satellite, Hybrid) — requires user-supplied subscription key.
   Free S0 tier at https://azure.microsoft.com/products/azure-maps . Configure via
   `Web → TMS for Korea → Configure Azure Maps Key…`
 - Kakao(Daum) — unavailable: Kakao blocks direct tile access since 2025-10-20 (App Key + SDK only)
 - NGII — deferred (custom EPSG:5179 tile scheme, needs GDAL TMS work)
 - Google Maps — out of scope (ToS requires session-token API + billing)
 - Bing Maps — replaced by Azure Maps (Bing program closed to new keys 2024-06-30)
 - Mango — upstream server unreachable


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

