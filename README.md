TMS for Korea
=======================

한국 사용자를 위한 QGIS용 지도 타일 플러그인 (브이월드 · 네이버 · OpenStreetMap · Azure 지도).

> **QGIS 4.x 브랜치 (`4.x/main`) — v4.1.4**
> 이 브랜치는 QGIS 4 (Qt6) 포팅 버전입니다. 레거시 WebKit 렌더러는 표준 XYZ
> 타일 프로바이더로 교체되었습니다. `master` 브랜치는 여전히 QGIS 3.x (Qt5)
> 사용자를 위한 라인입니다.
>
> 설치: QGIS 플러그인 관리자에서 **플러그인 → 플러그인 관리 및 설치 →
> ZIP에서 설치** 후 `latest-binary/tmsforkorea-4.1.4.zip` 선택.
>
> - **v4.1.1**: 네이버 타일 미표시 버그 수정 — 네이버 CDN이 QGIS 기본
>   `User-Agent` 문자열을 차단하던 문제를 우회.
> - **v4.1.2**: 핫픽스 — Azure 키 설정 다이얼로그에서 `QLineEdit.Normal`
>   AttributeError가 발생하던 문제를 `QLineEdit.EchoMode.Normal`로 수정.
> - **v4.1.3**: 메뉴 UX 개선 — Azure 키 설정 항목을 Azure 지도 서브메뉴로
>   이동, 키 미설정 시 Azure 레이어 비활성화. 카카오 지도는 정책 차단
>   상태를 UI에 표시하는 placeholder 메뉴로 노출.
> - **v4.1.4**: UI 한글화 — 메뉴 라벨, 다이얼로그, 메시지 바, README를
>   한글 중심으로 번역. 내부 식별자는 영문 유지(프로젝트 호환성).


제공 레이어
------------------------------
| 그룹 | 레이어 | 비고 |
|---|---|---|
| 브이월드 (VWorld) | 일반지도, 흑백지도, 위성지도, 위성+레이블 | EPSG:3857, 인증키 불필요 |
| 네이버 지도 v5 | 일반지도, 위성+레이블, 위성지도, 지형도, 지적도 | EPSG:3857, 인증키 불필요 |
| OpenStreetMap | 기본지도, 인도주의(HOT), 자전거(CyclOSM), 지형도(OpenTopoMap) | EPSG:3857, 인증키 불필요, 글로벌 |
| Azure 지도 | 일반지도, 위성지도, 위성+레이블 | **구독 키 필요** (아래 안내) |


Azure 지도 사용법
------------------------------
1. https://azure.microsoft.com/products/azure-maps 에서 무료 S0 등급으로 가입 (개인 사용에 충분).
2. Azure 포털 → "Azure Maps" 리소스 생성 → "Authentication" 메뉴에서 **Primary Key** 복사.
3. QGIS 메뉴 `웹 → TMS for Korea → Azure 지도 → Azure 구독 키 설정…` 클릭, 키 입력.
4. 키가 저장되면 Azure 레이어 3종이 활성화됩니다. 미설정 상태에서는 회색으로 표시됩니다.
5. 키 변경/삭제 시 QGIS 재시작 불필요. 다이얼로그에서 값을 비우고 확인하면 키가 삭제됩니다.


지원되지 않는 지도 / 연기된 지도
------------------------------
| 지도 | 상태 | 사유 |
|---|---|---|
| 카카오(다음) 지도 | **사용 불가** (UI에 비활성 메뉴로 표시) | 카카오가 2025-10-20부터 타일 직접 접근을 차단. App Key + 공식 JS SDK만 허용. 복원하려면 QtWebEngine + JS SDK 임베드가 필요하며, 별도 phase로 추후 진행 예정 |
| Google 지도 | 범위 외 | Google Maps Tile API는 session-token + 결제 등록이 강제되어 정적 XYZ URI 방식과 호환 불가. 비공식 `mt0-mt3` 엔드포인트는 ToS 위반 |
| Bing 지도 | Azure 지도로 대체됨 | Microsoft가 Bing Maps for Enterprise 신규 키 발급을 2024-06-30 종료. 후속 Azure Maps로 v4.1.0부터 통합 |
| NGII (국토지리정보원) | 연기 | 비표준 EPSG:5179 타일 스킴 사용. GDAL TMS minidriver의 역방향 zoom 미지원이 블로커. 향후 phase에서 재시도 |
| Mango | 연기 | 업스트림 서버 응답 없음(ECONNREFUSED). 서버 복귀 시 재등록 가능 |


마이그레이션 기록
------------------------------
QGIS 3.x → 4.x 포팅의 전체 기록(목적, 계획, 단계별 실행 로그, 핫픽스, 회고,
향후 로드맵)은 [MIGRATION.md](MIGRATION.md)에 정리되어 있습니다.


공식 플러그인 저장소
------------------------------
 - http://plugins.qgis.org/plugins/tmsforkorea/


관련 프로젝트
------------------------------
 - 본 플러그인은 [qgis-openlayers-plugin](https://github.com/sourcepole/qgis-openlayers-plugin)에서 fork되었습니다.


라이선스
----------
GNU General Public License v2 또는 그 이후 버전 (FSF). 자유롭게 재배포 및 수정
가능합니다.


스크린샷
---------
![screenshot](https://github.com/mapplus/qgis-tmsforkorea-plugin/blob/master/images/tmsforkorea_overview.png?width=800)


---

For English users
------------------------------
This is a QGIS plugin that exposes Korean and international XYZ map tile
services (VWorld, Naver, OpenStreetMap, Azure Maps) inside the QGIS layer
panel. It is the QGIS 4.x (Qt6) port of the legacy tmsforkorea plugin;
the WebKit-based renderer was replaced with native XYZ tile providers.

Azure Maps is the only group that requires a user-supplied subscription
key (free S0 tier available). Kakao Maps is rendered as a disabled
placeholder because Kakao blocks direct tile access since 2025-10-20.
See [MIGRATION.md](MIGRATION.md) for the full porting record.
