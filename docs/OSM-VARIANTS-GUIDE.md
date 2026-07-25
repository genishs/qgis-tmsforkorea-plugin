# OSM 변형 레이어 추가 — 구동 및 검증 가이드

브랜치: `4.x/osm-variants`
작업: OpenStreetMap 그룹에 변형 스타일 3종(인도주의/HOT, 자전거/CyclOSM, 지형도/OpenTopoMap) 추가

---

## 1. 변경 요약

| 파일 | 변경 |
|---|---|
| `tmsforkorea/weblayers/osm_maps.py` | `OlOSMHumanitarianLayer`, `OlOSMCyclOSMLayer`, `OlOSMOpenTopoMapLayer` 3개 클래스 추가 |
| `tmsforkorea/openlayers_plugin.py` | 위 3개 import + `initGui()`에서 registry 등록 |
| `README.md` | 제공 레이어 표의 OpenStreetMap 행 갱신 |

모두 기존 `WebLayer3857` 기반의 **무인증 EPSG:3857 XYZ** 레이어로, VWorld/OSM 기본지도와 동일한 경로(`type=xyz` URI)로 동작합니다. 신규 배관·인증키·아이콘 재빌드가 필요 없습니다.

### 추가된 타일 엔드포인트

| 레이어 | URL 템플릿 | 비고 |
|---|---|---|
| OSM 인도주의(HOT) | `https://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png` | OpenStreetMap France 호스팅 |
| OSM 자전거(CyclOSM) | `https://a.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png` | 자전거 지향 스타일 |
| OSM 지형도(OpenTopoMap) | `https://a.tile.opentopomap.org/{z}/{x}/{y}.png` | 등고선/지형, 데이터 ~z17 |

> QGIS XYZ provider는 `{s}` 서브도메인 회전을 지원하지 않으므로 호스트를 `a.`로 고정했습니다.

---

## 2. 사전 검증 (이미 수행됨)

- 세 엔드포인트 모두 `200 OK` + `image/png` 응답 확인 (z3/4/2 타일)
- `python -m py_compile` 통과 (osm_maps.py, openlayers_plugin.py)

---

## 3. QGIS에서 구동 검증

1. **플러그인 갱신 설치**
   - 개발 클론을 직접 쓰는 경우: 이 브랜치를 QGIS 플러그인 폴더(`.../python/plugins/tmsforkorea`)에 반영 후 QGIS 재시작 또는 *Plugin Reloader*로 리로드.
   - zip로 설치하는 경우: 아래 4절에서 zip을 빌드한 뒤 **플러그인 관리 → ZIP에서 설치**.

2. **메뉴 확인**
   - QGIS 메뉴 `웹 → TMS for Korea → OpenStreetMap` 하위에 항목 4개가 보여야 함:
     - OSM 기본지도
     - OSM 인도주의(HOT)
     - OSM 자전거(CyclOSM)
     - OSM 지형도(OpenTopoMap)

3. **레이어 추가 및 타일 표시**
   - 각 항목 클릭 → 레이어 패널에 추가되고 캔버스에 타일이 그려지는지 확인.
   - HOT/CyclOSM은 z0~19, OpenTopoMap은 z0~17에서 타일이 정상 표시.

4. **진단 로그 (타일이 안 보일 때)**
   - `보기 → 패널 → 로그 메시지` → `TMS for Korea` 탭에서
     `Adding XYZ layer ... valid: True` 로그와 URL 템플릿을 확인.
   - `valid: False`거나 메시지 바에 경고가 뜨면 URL/네트워크 문제.

---

## 4. (선택) 설치용 zip 빌드

릴리스로 배포하려면 버전 결정 후 zip을 굽습니다. (현재 미수행 — 버전 번호 미정)

```bash
cd qgis-tmsforkorea-plugin
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

> 버전 번호를 정하면 `tmsforkorea/metadata.txt`의 `version=` 도 함께 갱신해야 합니다.

---

## 5. 남은 결정 (사용자 확인 대기)

- 버전 번호 bump 및 zip 빌드 여부 (예: v4.2.0)
- `MIGRATION.md`에 phase 기록 추가 여부
- push 시점 (현재까지 로컬 커밋만)
