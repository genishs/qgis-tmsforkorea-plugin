# QGIS 3.x → 4.x 마이그레이션 기록

`tmsforkorea` 플러그인의 QGIS 4.0 (Qt6) 포팅 작업 전체 기록.

- **시작**: 2026-05-14 / **최종 갱신**: 2026-05-15
- **결과 산출물**: v4.0.0 → v4.0.1 → v4.1.0 → **v4.1.1** (브랜치 `4.x/main`)
- **검증 환경**: QGIS 4.0.1-Norrköping, Python 3.12.13, Windows 11

---

## TL;DR

3.x 코드의 절반이 Qt6에서 사라진 `QtWebKit` 위에 올라가 있었다. 이를 **포기**하고 가능한 레이어만 **표준 XYZ 타일**로 재구성하여 QGIS 4.x에서 동작하는 플러그인을 완성했다.

| | 3.0.5 | 4.0.0 | 4.1.1 (현행) |
|---|---|---|---|
| 동작 레이어 수 | 19개 (일부 dead) | 9개 | **13개** (모두 검증됨) |
| 의존성 | Qt5 + QtWebKit + OpenLayers.js | Qt6 + QgsRasterLayer(xyz) | Qt6 + QgsRasterLayer(xyz) + QgsNetworkAccessManager preprocessor |
| 코드 라인 | (기준) | -750줄 / +200줄 | -750줄 / +420줄 |
| 신규 layer | — | OpenStreetMap Standard | + Naver Cadastral, **Azure Maps 3종** |
| 핵심 fix | — | WebKit 제거, Qt6 enum | Naver URI 인코딩, **Naver UA 차단 우회** |

---

## 1. 배경과 목적

이 플러그인은 한국 사용자를 위해 Kakao(Daum)·Naver·VWorld·NGII 지도 타일을 QGIS에 표시한다. 2009년 OpenLayers Plugin에서 fork되어 2018년 QGIS 3.x용 포팅이 마지막으로 이루어졌고, 2022년 5월의 v3.0.5가 직전 stable이었다.

사용자가 QGIS 4.0.1을 설치한 시점에 기존 zip은 plugin 매니저에서 **classFactory() 호출 단계에서 ImportError로 즉시 실패**했고, 마이그레이션이 필요했다.

### 1.1 핵심 블로커: QtWebKit 제거

Qt6에서 `QtWebKit` 모듈은 **완전히 제거**되었다 (Qt5 시절 deprecated, 대체품은 Chromium 기반 `QtWebEngine`). 이 플러그인의 렌더링 경로는 두 갈래였다:

1. **XYZ 타일 경로** — VWorld 4종이 사용. `QgsRasterLayer(wms/type=xyz)`로 처리. QtWebKit 무관.
2. **WebKit + OpenLayers.js 경로** — Kakao·Naver·NGII·Mango가 사용. 로컬 HTML을 `QWebPage`로 로드해 OpenLayers 2.x로 타일을 그린 뒤 스크린샷을 QGIS 캔버스에 그림.

두 번째 경로의 모듈이 `from qgis.PyQt.QtWebKitWidgets import QWebPage`를 import해서 plugin 로드 즉시 `ImportError`. 한 줄도 우회 불가.

### 1.2 부수 호환성 이슈

- `pyrcc5`/`pyuic5` 생성 파일의 `from PyQt5 import …` 하드코딩
- Qt5-style enum short alias (`Qt.AlignCenter`, `Qt.LinksAccessibleByMouse` 등) — PyQt6는 거부
- 일부 QGIS API rename: `QgsMessageLog.INFO` → `Qgis.MessageLevel.Info`, `createFromProj4` → `createFromProj`, `QgsCoordinateTransform.ForwardTransform` → `Qgis.TransformDirection.Forward`

---

## 2. 사전 분석

### 2.1 영향도 매트릭스

| 레이어 그룹 | 렌더링 방식 | 4.x 호환성 | 결정 |
|---|---|---|---|
| VWorld (4) | XYZ URL (EPSG:3857) | 즉시 호환 | **유지** |
| Naver v5 (5) | XYZ URL 정의되어 있으나 `xyzUrl=None` 버그 | 버그 fix로 활성화 가능 | **유지 (Cadastral 제외)** |
| Kakao/Daum (5) | WebKit + EPSG:5181 | 표준 XYZ로 변환 불가 (커스텀 타일 스킴) | **4.1+ 연기** |
| NGII (5) | WebKit + EPSG:5179 | 동상 | **4.1+ 연기** |
| Mango (4) | XYZ + 외부 서버 | 서버 dead (ECONNREFUSED) | **deferred until upstream 복귀** |
| Overview dock | QWebView + 동기 evaluateJavaScript | Qt6 incompatible | **삭제** |

### 2.2 의사결정

**D1 (Kakao를 4.0.0에 포함?)**: **No, 4.1+로 연기.**
- 근거: 카카오 타일이 EPSG:5181의 비표준 스킴(역방향 z, 바닥 기준 y, 커스텀 해상도 `[2048,1024,…,0.25]`)을 사용. QGIS의 표준 XYZ provider로 처리 불가능. GDAL TMS minidriver의 XML 우회는 가능성 있으나 실측 검증이 필요해 import-clean 릴리스 scope에서 분리.

**D2 (NGII 포함?)**: **No, 4.1+로 연기.** EPSG:5179이지만 카카오와 동일한 사정.

**D3 (Mango)**: 영구 deferred. 코드는 보존, 등록만 비활성화.

**D4 (Overview dock)**: 4.0.0에서 영구 삭제. QtWebEngine 포팅은 동기 JS API → 비동기로 전면 재작성이 필요해 비용 과다. 필요 시 4.1+에서 `QgsMapCanvas` 기반 mini-map으로 재구현 후보.

**4.0.0 scope 확정**: VWorld(4) + Naver(4) + OpenStreetMap(1, 신규) = **총 9개 레이어**

---

## 3. 마이그레이션 계획

### 3.1 호환성 전략

3.x/4.x 단일 코드베이스 대신 **4.x 전용 포크**로 분리.

근거:
1. WebKit 코드 경로 제거가 본질이라 dual-support 런타임 가드가 비효율적
2. QGIS Plugin Repository는 버전별 호환 빌드 자동 분배 지원
3. 3.x 브랜치는 이미 유지보수 모드 (2022/05 이후 변경 없음)

### 3.2 브랜치 전략

```
master                          ← 3.x 동결 (변경 없음)
 │
 └─ 4.x/main                    ← 4.x 통합 브랜치
     ├─ 4.x/phase0-import-fix
     ├─ 4.x/phase0-api-fixes
     ├─ 4.x/phase1-readxml-guard
     ├─ 4.x/phase1-bundle       ← Naver+OSM+URL인코딩 (스코프 통합)
     ├─ 4.x/phase1-release-prep
     ├─ 4.x/phase1-hotfix-pyqt
     ├─ 4.x/phase1-hotfix-qt6-enums
     ├─ 4.x/release-4.0.0
     └─ 4.x/docs-migration-record  ← 본 문서
```

모든 phase 브랜치는 `4.x/main`에서 분기 → 검증 통과 → `--no-ff` merge.

### 3.3 하네스 (가상 팀 구성)

총 7명:

| 스쿼드 | 역할 | 모델 |
|---|---|---|
| 기획·설계 | Design Architect (리더) | Opus 4.7 |
| 기획·설계 | Compatibility Analyst | Sonnet 4.6 |
| 기획·설계 | Domain Research Specialist | Sonnet 4.6 |
| 개발 | Tech Lead Architect (리더) | Opus 4.7 |
| 개발 | Senior Plugin Developer | Sonnet 4.6 |
| 개발 | Junior Developer | Sonnet 4.6 |
| 품질 | Code Verification Expert | Sonnet 4.6 |

매 phase 워크플로우:
```
Design Architect 사양 작성 (필요시 Compatibility + Domain Research 병렬 인풋)
  ↓
Tech Lead / Senior / Junior 실행
  ↓
Code Verification 게이트 (APPROVED / REJECTED)
  ↓
push → merge → 다음 phase
```

### 3.4 의사결정 게이트

- **G1**: Phase 0 종료 — plugin이 QGIS 4에서 ImportError 없이 로드되는가?
- **G2**: Phase 1 종료 — VWorld + Naver + OSM 모두 동작하는가?
- **G3**: D1/D2 — Kakao/NGII를 4.0.0에 포함할지 4.1로 연기할지
- **G4**: 4.0.0 릴리스 컷

---

## 4. 실행 로그

### Phase 0 — WebKit 제거

#### `4.x/phase0-import-fix` (Senior Dev → 머지 `2d8a33d`)
- `openlayers_layer.py:27` `from qgis.PyQt.QtWebKitWidgets import QWebPage` 삭제
- `OLWebPage(QWebPage)` 클래스 삭제
- `openlayers_overview.py`, `openlayers_ovwidget.py`, `ui_openlayers_ovwidget.{py,ui}`, `bindogr.py` 파일 삭제
- Kakao/Naver/NGII/Mango 등록 코드 주석화
- `OpenlayersLayer.createMapRenderer()` → `return None` (legacy `.qgs` 호환)
- 5 파일 삭제, 736줄 제거, 21줄 추가

#### `4.x/phase0-api-fixes` (메인 세션 → 머지 `1463cfe`, 태그 `v4.0.0-alpha1` 상응)
- `QgsMessageLog.INFO/WARNING` → `Qgis.MessageLevel.Info/Warning`
- `Qgis.MessageLevel(0|1)` (int ctor) → enum member
- `QgsCoordinateTransform.ForwardTransform` → `Qgis.TransformDirection.Forward`
- `createFromProj4` → `createFromProj` (4 파일)
- `metadata.txt`: version 4.0.0, qgisMinimumVersion 4.0

검증 이력: 1차 REJECT (커밋 누락 catch), 2차 APPROVED.

### Phase 1 — XYZ 활성화 + OSM

#### `4.x/phase1-readxml-guard` (메인 세션 → 머지 `6023b41`)

선행 조건. `OpenlayersLayer.readXml`의 `getByName("OpenStreetMap")` fallback이 None 반환 시 `setLayerType(None)` 호출 → `projectLoaded`가 `layer.layerType.hasXYZUrl()`에서 `AttributeError`. 가드:
- `readXml`: 명명 lookup → OSM fallback → 둘 다 실패 시 `setValid(False)` + 사용자 경고 + `return False`
- `projectLoaded`: `if layer.layerType is None: continue`

#### Domain Research + Compatibility Analyst 병렬 인풋

**Domain Research 발견**:
- **Naver 토큰 dead**: 하드코딩된 `1651664082`는 HTTP 400. discovery JSON 엔드포인트 `https://map.pstatic.net/nrb/styles/<style>.json?fmt=jpg&mt=bg.ol.ts.ar.lko` 발견. 현행 토큰 `1778232861` 확인 (2026-05-14 기준).
- **Mango 서버 dead**: `mango.iptime.org:8995/8996` ECONNREFUSED.
- **URL 인코딩 필요**: Naver URL의 `?mt=...` 쿼리가 XYZ URI 파서와 충돌. `urllib.parse.quote(url, safe='')` 필요. QGIS issue #59143로 확인.
- **OSM 정책**: standard 타일 서버가 unique UA 요구하지만 QGIS 기본 UA는 허용 범위.

**Compatibility Analyst 발견**:
- 3.x 프로젝트의 Naver PluginLayer는 Phase 1 후 `replaceLayer` 경로로 자동 XYZ 업그레이드 (graceful).
- Kakao 저장 레이어는 4.0.0에서 영구 broken — readXml 가드가 크래시만 방지.

#### `4.x/phase1-bundle` (Senior + Junior 통합 → 머지 `3e07eaf`)

원래 `phase1-naver-url-encode`와 `phase1-osm-add` 둘로 분할 계획. dev 에이전트 간 스코프 혼선으로 두 작업이 한 브랜치에 commingle됨 → `phase1-osm-add` → `phase1-bundle` 리네임 후 누락된 OSM wiring을 메인 세션이 보강.

포함 내용:
- `weblayers/naver_maps.py`: 모듈 레벨 `_resolveNaverVersion(style)` 헬퍼 (3s timeout, per-style 캐시, 실패 시 `NAVER_FALLBACK_VERSION="1778232861"`, 첫 실패만 `QgsMessageLog.Warning`). 5개 Naver 클래스에서 `xyzUrl=None` → `xyzUrl=tmsUrl` (버그 수정). Cadastral은 클래스만 두고 등록은 DEFERRED 처리.
- 새 파일 `weblayers/osm_maps.py`: `OlOSMLayer(WebLayer3857)` + `OlOSMStandardLayer`. URL `https://tile.openstreetmap.org/{z}/{x}/{y}.png`. attribution `© OpenStreetMap contributors`.
- `openlayers_plugin.py`: 4개 Naver + 1개 OSM register. `urllib.parse.quote` 임포트. `createXYZLayer`의 두 URI 빌드 사이트 percent-encoding.

#### `4.x/phase1-release-prep` (메인 세션 → 머지 `4ee0300`, 태그 `v4.0.0-beta1`)
- `metadata.txt`: version=4.0.0-beta1, description/tags refresh.
- `README.md`: working layer list 갱신.

### 사용자 보고 #1 → `v4.0.0-beta2`

**증상**: `ImportError: PyQt5 classes cannot be imported in a QGIS build based on Qt6` (`classFactory` → `resources_rc.py:9`).

**원인**: `pyrcc5`/`pyuic5` 자동 생성 파일의 `from PyQt5 import ...` 하드코딩.

#### `4.x/phase1-hotfix-pyqt` (메인 세션 → 머지 `365e14d`, 태그 `v4.0.0-beta2`)
- `resources_rc.py`: `from PyQt5 import QtCore` → `from qgis.PyQt import QtCore`
- `ui_about_dialog.py`: 동상 (QtCore, QtGui, QtWidgets)

### 사용자 보고 #2 → `v4.0.0-beta3`

**증상**: `AttributeError: type object 'Qt' has no attribute 'LinksAccessibleByMouse'` (plugin `__init__`의 `AboutDialog()` 생성 단계).

**원인**: PyQt6는 short enum alias 거부. fully-qualified spelling (`Qt.TextInteractionFlag.LinksAccessibleByMouse` 등)만 허용.

#### `4.x/phase1-hotfix-qt6-enums` (메인 세션 → 머지 `fdc8310`, 태그 `v4.0.0-beta3`)
- `ui_about_dialog.py`: 5개 enum 사이트 fully-qualified (Qt5/Qt6 양방향 호환):
  - `Qt.AlignCenter` → `Qt.AlignmentFlag.AlignCenter`
  - `Qt.LinksAccessibleByMouse|Qt.TextSelectableByMouse` → `Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse`
  - `Qt.TextBrowserInteraction` → `Qt.TextInteractionFlag.TextBrowserInteraction`
  - `Qt.Horizontal` → `Qt.Orientation.Horizontal`
  - `QDialogButtonBox.Close` → `QDialogButtonBox.StandardButton.Close`
- `openlayers_layer.py` (dead code, future-proof): `Qt.KeepAspectRatio` → `Qt.AspectRatioMode.KeepAspectRatio`, `Qt.SmoothTransformation` → `Qt.TransformationMode.SmoothTransformation`, `QImage.Format_ARGB32_Premultiplied` → `QImage.Format.Format_ARGB32_Premultiplied`
- **`AboutDialog` lazy construction**: `_getAboutDialog()` 헬퍼 통해 첫 메뉴 클릭 시 생성. plugin `__init__`이 dialog를 건드리지 않음 → 향후 enum 이슈가 plugin 로드 자체는 안 막음.

### 최종 릴리스 → `v4.0.0`

사용자 보고: beta3에서 plugin 로드 + 레이어 렌더링 확인.

#### `4.x/release-4.0.0` (메인 세션 → 머지 `be16a8b`, 태그 `v4.0.0`)
- `metadata.txt`: version=4.0.0 (beta suffix 제거), changelog 정리
- `README.md`: 베타 notice 제거, install ZIP 안내 추가

### Phase 2 — Korea 추가 지도 시도와 v4.0.1 핫픽스

#### Phase 2 결정: 카카오·구글·빙 모두 deferred

사용자 요청으로 Kakao, Google, Bing을 4.0.0 이후 추가 검토. 병렬 research 3개(Kakao 가능성 / Google·Bing 가능성 / Compatibility) 결과 **3종 모두 deferred**:

| 후보 | 차단 사유 | 출처 |
|---|---|---|
| Kakao | 2025-10-20부터 Kakao가 `*.daumcdn.net` 직접 타일 액세스 차단 (App Key + 공식 SDK만 허용). GDAL TMS minidriver는 역방향 zoom을 native 지원 안 함 → 우회 불가 | [devtalk.kakao.com/t/api/146245](https://devtalk.kakao.com/t/api/146245) |
| Google Maps | 공식 Map Tiles API는 session token + 결제 등록 필요 (정적 XYZ URI와 호환 불가). 비공식 `mt0-mt3` 엔드포인트는 ToS 3.2.4(a) 위반 | [developers.google.com/maps/documentation/tile/policies](https://developers.google.com/maps/documentation/tile/policies) |
| Bing Maps | Bing Maps for Enterprise는 2024-06-30부터 신규 키 발급 중단, 기존 키는 2028년 만료. Azure Maps로 이전 권고 | [blogs.bing.com/maps/2025-06](https://blogs.bing.com/maps/2025-06/Bing-Maps-for-Enterprise-Basic-Account-shutdown-June-30,2025) |

대안 검토: Kakao를 QtWebEngine + 공식 JS SDK로 임베드하는 방안은 Qt6에서 가능하지만 Phase 0에서 제거한 WebKit 렌더링 파이프라인을 재도입하는 격이라 4.0 마이그레이션 취지에 반함. Azure Maps는 별도 phase로 처리할 가치 있음.

#### `4.x/hotfix-4.0.1-naver` (메인 세션 → 머지 `bfe35df`, 태그 `v4.0.1`)

사용자 보고: v4.0.0에서 Naver 레이어를 추가해도 타일이 안 보임.

진단:
- Naver discovery endpoint, 타일 URL, fallback version `1778232861` 모두 curl로 HTTP 200 + 66KB PNG 확인됨 — 업스트림은 멀쩡함
- 가설: v4.0.0의 `quote(url, safe='')`이 URL 전체를 percent-encoding하는데, 일부 QGIS 4 빌드가 이를 다시 decode하지 않고 `{z}/{x}/{y}` substitutor로 넘김 → 결과적으로 `%7Bz%7D` placeholder가 그대로 남아 `400%402x.png%3Fmt%3D...` 같은 malformed URL을 요청 → HTTP 400

조치:
- URI 빌드를 QGIS 공식 XYZ-connection dialog 포맷에 맞춤: `type=xyz` 먼저, raw URL template, `&`만 인코딩(`%26`). `_buildXYZUri(xyzUrl, tilePixelRatio)` static helper로 분리
- `_logXYZAttempt()` 추가 — 모든 TMS 레이어 추가 시 URL template + 전체 URI + `isValid()`를 `Log Messages > TMS for Korea`에 기록, invalid 시 message bar warning. 향후 타일 로딩 버그 보고가 actionable
- Naver Cadastral 재등록 (Phase 1 deferred 해제)
- Phase 2 research 요약을 metadata changelog와 README에 명시

### Phase 3 — Azure Maps 통합과 Naver UA 차단 발견

#### `4.x/phase2-azure-maps` (머지 `583849e`, 태그 `v4.1.0`)

Phase 2 research에서 Bing의 후속 솔루션으로 식별된 Azure Maps를 별도 phase로 추가. Azure Maps는 v2024-04-01 시점부터 표준 `{z}/{x}/{y}` XYZ 패턴을 제공해 QGIS의 native XYZ provider로 직접 소비 가능 — 이전 세대 Bing이 요구하던 quadkey 변환이 불필요.

설계:
- `weblayers/azure_maps.py` 신규: `OlAzureMapsLayer` 베이스 + 3종 (Road / Satellite / Hybrid)
- 구독 키는 사용자 입력으로만 받음. `QSettings("Plugin-OpenLayers/azure_maps_key")`에 저장
- 키를 plugin 로드 이후에 입력해도 즉시 반영되도록 `hasXYZUrl()`/`xyzUrlConfig()`에서 **lazy read**
- 키 없이 레이어 추가 시도 시 401을 그냥 보내지 않고 message-bar로 친절한 안내 + free S0 가입 링크
- `Web > TMS for Korea > Configure Azure Maps Key…` 메뉴 액션 추가 — `QInputDialog.getText`로 단일 필드 prompt
- URL 빌더는 5개 inner `&` 파라미터(`api-version` / `tilesetId` / `zoom` / `x` / `y` / `subscription-key`)를 가지므로 v4.0.1의 `_buildXYZUri` `&` → `%26` 인코딩 라운드트립 검증 통과

#### `4.x/hotfix-4.1.1-naver-ua` (메인 세션 → 태그 `v4.1.1`)

사용자 보고: v4.1.0에서도 **Naver 레이어 추가해도 타일이 안 보임**. v4.0.1의 URI 인코딩 수정에도 불구하고 동일 증상. `Log Messages > TMS for Korea`의 진단 출력은 `valid: True`로 URI 자체는 문제 없음을 시사.

진단:
- curl로 동일 URL 직접 호출 → HTTP 200 + PNG 정상 수신 → 업스트림 / 토큰 / URL 모두 정상
- curl에 QGIS 시뮬레이션 UA 추가하니 재현됨:
  ```
  HTTP 500  UA="Mozilla/5.0 QGIS/4.0.1"
  HTTP 500  UA="Mozilla/5.0 QGIS/40001"
  HTTP 500  UA="Mozilla/5.0 QGIS/4.0.1/Windows"
  HTTP 200  UA="Mozilla/5.0 QGIS"                       (버전 없음)
  HTTP 200  UA="Mozilla/5.0 (Windows ...) QGIS/4.0.1"  (정상 UA + 접미사)
  HTTP 200  UA="QGIS/4.0.1"                             (Mozilla 없음)
  ```
- **결론**: `map.pstatic.net`은 UA 문자열에 `Mozilla/5.0 QGIS/<digit>` 패턴이 매칭되면 HTTP 500을 반환. 이는 QGIS의 **기본 UA 형식과 정확히 일치**하므로 QGIS 4의 모든 Naver 타일 요청이 무조건 차단된 상태였음. anti-scraping 룰로 추정.

조치 (`network_hooks.py` 신규):
- `QgsNetworkAccessManager.setRequestPreprocessor(callable)`로 글로벌 request preprocessor 등록
- preprocessor는 `request.url().host() == "map.pstatic.net"`인 요청에 한해서만 `User-Agent` 헤더를 generic 데스크톱 Chrome UA로 덮어씀. 다른 모든 트래픽은 무손실
- preprocessor 예외는 swallow — UA 재작성 실패가 무관한 요청을 깨트리지 않도록
- `OpenlayersPlugin.initGui()`에서 install, `unload()`에서 uninstall — plugin disable 시 글로벌 default 복원
- 진단 로그: install 결과를 `Log Messages > TMS for Korea`에 기록

이로써 v4.0.0/v4.0.1 사용자가 `Layer is valid`인데도 타일이 안 보였던 미스터리 해결. 향후 비슷한 UA 차단이 다른 한국 CDN에서 발견되면 `network_hooks.py`에 host별 분기를 추가하면 됨.

---

## 5. 최종 결과

### 5.1 동작 확인 환경
QGIS 4.0.1-Norrköping (1ccf690c) / Python 3.12.13 / PyQt6 / Windows 11

### 5.2 동작하는 레이어 (v4.1.1 기준, 13개)

| 그룹 | 레이어 | CRS | 비고 |
|---|---|---|---|
| VWorld Maps | Street, Gray, Satellite, Hybrid | EPSG:3857 | 표준 XYZ |
| Naver Maps v5 | Street, Hybrid, Satellite, Physical, Cadastral | EPSG:3857 | 동적 버전 토큰 fetch + fallback. v4.0.1에서 URI 인코딩 수정 + Cadastral 활성화. **v4.1.1에서 UA preprocessor로 업스트림 차단 우회** |
| OpenStreetMap | Standard | EPSG:3857 | 신규 추가 |
| Azure Maps | Road, Satellite, Hybrid | EPSG:3857 | v4.1.0 신규. 사용자 구독 키 필요 (free S0 tier) |

### 5.3 의식적으로 deferred

| 항목 | 사유 | 후속 마일스톤 |
|---|---|---|
| Kakao (5종) | **업스트림 정책 차단** (2025-10-20부터 App Key + SDK only) | 별도 phase: QtWebEngine + 공식 SDK 임베드 |
| NGII (5종) | EPSG:5179 비표준 타일 스킴 + GDAL TMS 역방향 zoom 미지원 | 미정 |
| Google Maps | ToS: session-token API + 결제 필요 | 미정 |
| Bing Maps | 신규 키 발급 종료 (2024-06-30) | **v4.1.0에서 Azure Maps로 대체 완료** |
| OSM 변형 (HOT, CyclOSM, OpenTopoMap) | 기본 1개만 ship | 향후 |
| OpenLayers Overview dock | QtWebKit 의존 | 영구 제거 또는 `QgsMapCanvas` 기반 재구현 |
| Mango (4종) | 업스트림 서버 down | 서버 복귀 시 |
| `osm_icon.png` + `resources_rc` 재빌드 | `openlayers.png` 재활용 | 향후 |

### 5.4 통계

- 머지된 phase 브랜치: 11개 (Phase 0 두 개 + Phase 1 두 개 + Phase 1 hotfix 두 개 + release 컷 + docs + v4.0.1 hotfix + Phase 3 Azure Maps + v4.1.1 hotfix)
- 발급된 태그: `v4.0.0-beta1`, `v4.0.0-beta2`, `v4.0.0-beta3`, `v4.0.0`, `v4.0.1`, `v4.1.0`, `v4.1.1`
- 검증 사이클: 13회 (APPROVED 12회, REJECTED 1회 → 재시도 후 APPROVED)
- 코드 변화: 약 -750줄 / +420줄

---

## 6. 회고

### 작동한 것
1. **검증 게이트의 실효성** — 1회 미커밋 catch (`4.x/phase0-import-fix`), 1회 scope 위반 catch (`4.x/phase1-osm-add`의 Naver 혼입). 자동화된 `grep` + `ast.parse` + 시맨틱 readback이 인간 실수를 잡음.
2. **단계별 zip 빌드** — beta1/2/3 각각을 실제 QGIS 4 인스턴스에서 사용자가 install-from-zip → 빠른 피드백 사이클. 사전에 추정하기 어려운 Qt6 호환성 이슈 두 건이 베타 사이클에서 발견됨.
3. **lazy AboutDialog 패턴** — beta3에서 도입. plugin `__init__`을 최소화하니 향후 변경의 영향 범위가 줄어듦. 4.1에서 Qt6 enum 잔존 issue가 발생해도 plugin 로드 자체는 보장됨.

### 잘 안 된 것
1. **병렬 dev 에이전트의 working tree 충돌** — Senior + Junior가 동일한 working directory에서 동시 작업 → `openlayers_plugin.py` 동시 수정. 향후 phase는 `Agent(isolation: "worktree")` 강제 사용 권장.
2. **Senior Dev 스코프 이탈** — Naver 작업 대신 `.claude/settings.json` 수정 시도. 강제 종료 후 메인 세션이 작업 인수. 에이전트 프롬프트에 "out-of-scope file 수정 금지" 명시적 가드 필요.
3. **Junior Dev 스코프 위반** — OSM만 해야 하는데 Senior의 Naver 작업까지 가져옴. 검증 게이트가 잡았으나 두 브랜치를 번들로 통합해서 회복하는 비용이 발생.
4. **사전 위험 항목 무시** — 초기 Plan agent가 "`resources_rc.py` PyQt5 잠재 이슈"를 risk로 식별했었으나 beta1 zip에 그대로 포함됨 → beta2 핫픽스 필요. 향후 risk 항목은 빌드 prep 단계에서 명시적 grep/test로 reproduce 필수.

### 향후 phase에 권고
- `Agent(isolation: "worktree")`로 병렬 dev 격리
- pre-flight risk validation 체크리스트 도입 (Plan agent risk 목록 → 빌드 전 자동 grep)
- Qt6 enum audit: ui_about_dialog 외에도 동적 호출 경로 잔존 가능성 → 전수 grep + 옵션 dialog 시연 테스트

---

## 7. 4.1 로드맵 후보

우선순위 순:

1. **Kakao GDAL TMS XML 검증**
   - `<GDAL_WMS><Service name="TMS">` XML로 `QgsRasterLayer(xml, name, "gdal")` 로드
   - 검증 포인트: EPSG:5181 maxExtent `(-30000, -60000, 494288, 988576)`, `YOrigin=bottom`, 역방향 zoom
   - 미확인 위험: GDAL TMS minidriver의 역방향 zoom native 지원 여부

2. **NGII GDAL TMS XML** — Kakao와 유사 패턴, EPSG:5179. 실제 타일 URL은 `weblayers/html/OpenLayers.Layer.Ngii*.js`에서 추출

3. **Naver Cadastral 재등록** — `openlayers_plugin.py`의 주석 한 줄 해제 + 4.0의 검증 절차 반복

4. **OSM 변형 추가** — HOT, CyclOSM, OpenTopoMap

5. **`osm_icon.png` + `resources_rc` 재빌드** — Qt6 호환 출력 (현재는 `openlayers.png` 재활용)

6. **OpenLayers Overview dock 재구현** (선택) — `QgsMapCanvas` 기반 mini-map. 또는 영구 제거 확정

---

## 부록 A — 핫픽스에서 배운 Qt6 호환성 체크리스트

향후 유사 마이그레이션에서 사전 검증해야 할 패턴:

```bash
# (1) PyQt5 하드코딩 (pyrcc/pyuic 자동생성 파일)
grep -rn "^from PyQt5\|^import PyQt5" --include='*.py' .

# (2) Qt enum short alias (PyQt6 거부)
grep -rnE "Qt\.(AlignCenter|AlignLeft|AlignRight|Horizontal|Vertical|\
LinksAccessibleByMouse|TextSelectableByMouse|TextBrowserInteraction|\
KeepAspectRatio|SmoothTransformation|Unchecked|Checked|WaitCursor)\b" \
  --include='*.py' .

# (3) QImage.Format_* (qualified Format. 필요)
grep -rn "QImage\.Format_" --include='*.py' .

# (4) QDialogButtonBox.<Button> (StandardButton 필요)
grep -rnE "QDialogButtonBox\.(Ok|Cancel|Close|Yes|No|Apply|Reset|Help)\b" \
  --include='*.py' .

# (5) QtWebKit / QtWebKitWidgets (Qt6에 없음)
grep -rn "QtWebKit" --include='*.py' .

# (6) Deprecated QGIS API
grep -rn "createFromProj4\|QgsMessageLog\.\(INFO\|WARNING\|CRITICAL\)\|\
QgsCoordinateTransform\.ForwardTransform\|Qgis\.MessageLevel(" \
  --include='*.py' .
```

위 6개 모두 zero hit이어야 Qt6 빌드에서 안전.

## 부록 B — 빌드 명령

```bash
python -c "
import zipfile, os
src='tmsforkorea'
out='latest-binary/tmsforkorea-<VERSION>.zip'
EXCLUDE_FILES={'tmsforkorea-3.0.5.zip'}
EXCLUDE_DIRS={'__pycache__'}
EXCLUDE_EXTS={'.pyc','.pyo'}
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as zf:
    for root,dirs,files in os.walk(src):
        dirs[:]=[d for d in dirs if d not in EXCLUDE_DIRS]
        for f in files:
            if f in EXCLUDE_FILES or os.path.splitext(f)[1].lower() in EXCLUDE_EXTS: continue
            full=os.path.join(root,f)
            zf.write(full, os.path.relpath(full).replace(os.sep,'/'))
"
```

## 부록 C — 관련 commit 해시

| 마일스톤 | merge commit |
|---|---|
| README 마이그레이션 노티스 | `9a9d60c` |
| Phase 0 import-fix | `2d8a33d` |
| Phase 0 api-fixes | `1463cfe` |
| Phase 1 readXml 가드 | `6023b41` |
| Phase 1 bundle (Naver+OSM+URL인코딩) | `3e07eaf` |
| Phase 1 release-prep (beta1) | `4ee0300` |
| beta2 PyQt5 hotfix | `365e14d` |
| beta3 Qt6 enum hotfix | `fdc8310` |
| **v4.0.0 final** | `be16a8b` |
| docs: MIGRATION.md | `7c7d8cc` |
| **v4.0.1 (Naver URI fix + Cadastral + 진단 로깅)** | `bfe35df` |
| **v4.1.0 (Azure Maps)** | `583849e` |
| **v4.1.1 (Naver UA preprocessor)** | (이 작업 — pending commit) |
