# 전국 수질 평가 시스템

환경부 수질 DB API를 활용하여 전국 시군구별 수질 상태를 평가하고 시각화하는 시스템입니다.

## 프로젝트 목적

기존 전라남도 지역 지도 생성기를 확장하여 전국으로 확장하고, 환경부 수질 DB API를 통해 각 시군구의 측정소에서 Tp(총인)와 Tn(총질소) 수치를 수집하여 가중치를 적용한 수질 평가 시스템을 구축합니다.

## 주요 기능

### 1. 전국 시군구 지도 생성
- 전국 모든 시군구 경계 표시
- 각 지역별 색상 매핑 (5단계 평가)

### 2. 환경부 수질 DB API 연동
- 측정소별 Tp(총인) 및 Tn(총질소) 데이터 수집
- 실시간 수질 데이터 조회

### 3. 가중치 기반 수질 평가
- Tp(총인): 0.99 가중치 적용
- Tn(총질소): 0.01 가중치 적용
- 가중 평균값 계산: `(Tp × 0.99) + (Tn × 0.01)`

### 4. 5단계 색상 매핑
- 각 시군구별 평가 결과를 20%씩 5단계로 분류
- 1단계 (0-20%): 초록색 - 수질 우수
- 2단계 (20-40%): 연초록색 - 수질 양호
- 3단계 (40-60%): 노란색 - 수질 보통
- 4단계 (60-80%): 주황색 - 수질 나쁨
- 5단계 (80-100%): 빨간색 - 수질 매우 나쁨

## 데이터 수집 구조

### 🔄 새로운 데이터 수집 흐름

```
1단계: API 서버에서 데이터 수집 시도
   ↓ (성공시)
2단계: 로컬 CSV 파일 업데이트
   ↓ (실패시)
3단계: 기존 CSV 파일 사용
```

#### 📊 데이터 수집 우선순위

1. **API 서버 이용** (1차 시도)
   - 환경부 수질 DB API에서 최신 데이터 수집
   - 실시간 데이터 조회 시도

2. **로컬 CSV 업데이트** (API 성공시)
   - API에서 수집한 데이터로 로컬 CSV 파일 업데이트
   - 기존 파일 백업 후 새 데이터 저장

3. **기존 CSV 파일 이용** (API 실패시)
   - API 서버 문제시 로컬에 저장된 CSV 파일 사용
   - 시스템 안정성 보장

#### 🔧 백업 시스템

- **자동 백업**: 기존 CSV 파일을 타임스탬프와 함께 백업
- **데이터 무결성**: 필수 컬럼 검증 및 데이터 형식 확인
- **오류 복구**: API 실패시에도 시스템 정상 운영

#### 📋 CSV 파일 데이터 범위

**다운로드 대상 데이터**:
- **농업용수 데이터**: 농업용수 수질 측정 데이터
- **하천 데이터**: 하천 수질 측정 데이터

**제외 대상 데이터**:
- 지하수 데이터
- 해양 수질 데이터
- 대기질 데이터
- 기타 환경 데이터

**데이터 소스**:
- 환경부 수질 DB API
- 공공데이터포털 수질 정보
- 국립환경과학원 수질 측정망 데이터

## 프로젝트 구조

```
miniproject/
├── src/                          # 소스 코드
│   ├── data_collection/          # API 데이터 수집
│   │   ├── __init__.py
│   │   ├── api_client.py         # API 통신
│   │   └── data_collector.py     # 데이터 수집기 (새로운 구조)
│   ├── data_processing/          # 데이터 전처리
│   │   ├── __init__.py
│   │   ├── preprocessor.py       # 원본 데이터 전처리
│   │   └── data_processor.py     # 데이터 처리
│   ├── risk_assessment/          # 고위험군 산정 알고리즘
│   │   ├── __init__.py
│   │   ├── risk_calculator.py    # 위험도 계산
│   │   └── alert_system.py       # 경보 시스템
│   ├── visualization/             # 지도 및 시각화
│   │   ├── __init__.py
│   │   ├── map_generator.py      # 지도 생성
│   │   └── chart_generator.py    # 차트 생성
│   ├── web_publisher/            # 웹 게시 기능
│   │   ├── __init__.py
│   │   └── web_publisher.py      # 웹 게시
│   └── utils/                    # 공통 유틸리티
│       ├── __init__.py
│       ├── config.py             # 설정 관리
│       ├── logger.py             # 로깅
│       └── helpers.py            # 헬퍼 함수
├── scripts/                      # 실행 스크립트
│   ├── main.py                   # 기존 메인 파일
│   └── run_pipeline.py           # 새로운 파이프라인 실행
├── tests/                        # 테스트 코드
├── docs/                         # 문서
├── data/                         # 데이터 폴더
│   ├── raw/                      # API 원본 데이터
│   │   ├── water_quality_data.csv    # 수질 데이터 (자동 업데이트)
│   │   └── measurement_stations.csv  # 측정소 정보 (자동 업데이트)
│   ├── processed/                # 전처리된 데이터
│   ├── shapefiles/               # 지리 데이터
│   └── output/                   # 최종 결과물
├── web/                          # 웹 게시 폴더
│   ├── static/                   # 정적 파일
│   │   ├── images/               # 이미지 파일
│   │   ├── css/                  # 스타일시트
│   │   └── js/                   # 자바스크립트
│   └── templates/                # HTML 템플릿
├── logs/                         # 로그 파일
├── requirements.txt
├── README.md
└── .env
```

## 설치

```bash
pip install -r requirements.txt
```

## 사용법

### 1. 기본 설정
```bash
# API 키 설정
cp env_example.txt .env
# .env 파일에서 환경부 API 키 설정
```

### 2. 새로운 파이프라인 실행
```bash
# 1회 실행
python scripts/run_pipeline.py

# 스케줄 실행 (30분마다)
python scripts/run_pipeline.py --mode schedule

# 테스트 모드
python scripts/run_pipeline.py --test
```

### 3. 기존 방식 실행
```bash
# 기존 메인 파일
python scripts/main.py
```

### 4. 개별 모듈 실행
```bash
# 데이터 수집
python -m src.data_collection.data_collector

# 데이터 처리
python -m src.data_processing.data_processor

# 위험도 계산
python -m src.risk_assessment.risk_calculator

# 지도 생성
python -m src.visualization.map_generator
```

## 모듈별 기능

### 📊 데이터 수집 (`src/data_collection/`)
- **API 클라이언트**: 환경부 수질 DB API와의 통신
- **데이터 수집기**: 새로운 구조로 API → CSV 업데이트 → 기존 CSV 이용

### 🔧 데이터 처리 (`src/data_processing/`)
- **전처리기**: 원본 데이터 정리 및 전처리
- **데이터 프로세서**: 가중치 계산 및 데이터 변환

### ⚠️ 위험도 평가 (`src/risk_assessment/`)
- **위험도 계산기**: 가중 평균 기반 위험도 산정
- **경보 시스템**: 고위험 지역 경보 생성

### 📈 시각화 (`src/visualization/`)
- **지도 생성기**: 수질 상태별 지도 생성
- **차트 생성기**: 다양한 분석 차트 생성

### 🌐 웹 게시 (`src/web_publisher/`)
- **웹 게시기**: 생성된 지도와 차트를 웹사이트에 게시
- **HTML 생성**: 반응형 웹 페이지 자동 생성
- **브라우저 연동**: 자동으로 브라우저에서 결과 확인

### 🛠️ 유틸리티 (`src/utils/`)
- **설정 관리**: API 키, 시스템 설정 관리
- **로깅**: 시스템 로그 관리
- **헬퍼 함수**: 공통 유틸리티 함수

## 출력 결과

### 지도 파일
- `integrated_water_quality_map.png`: 전국 수질 평가 지도
- `zeonam_water_quality_map.png`: 전라남도 수질 평가 지도

### 차트 파일
- `risk_distribution_*.png`: 위험도 분포 차트
- `regional_comparison_*.png`: 지역별 비교 차트
- `trend_analysis_*.png`: 트렌드 분석 차트
- `correlation_heatmap_*.png`: 상관관계 히트맵
- `summary_dashboard_*.png`: 종합 대시보드

### 웹 파일
- `web/index.html`: 메인 인덱스 페이지
- `web/map_*.html`: 수질 모니터링 지도 페이지
- `web/dashboard_*.html`: 수질 분석 대시보드 페이지
- `web/static/images/`: 게시된 이미지 파일들
- `sample_result.html`: 웹 기반 시각화 결과

## API 활용

### 🌐 공식 API EndPoint 정보

#### 📋 공식 문서 및 기본 URL
- **공식 문서**: https://www.data.go.kr/data/1480523/WaterQualityService
- **기본 URL**: `https://apis.data.go.kr/1480523/WaterQualityService`
- **서비스명**: 국립환경과학원 수질 정보 OpenAPI
- **서비스 ID**: `WaterQualityService`

#### 📋 사용 가능한 EndPoint 목록
| EndPoint | 설명 | 사용 여부 | 상태 |
|----------|------|-----------|------|
| `/listPoint` | 측정소 목록 조회 | ✅ 사용 중 | 정상 |
| `/getWaterMeasuringList` | 수질 데이터 조회 | ✅ 사용 중 | 정상 |
| `/getRealTimeWaterQualityList` | 실시간 수질 데이터 조회 | ✅ 사용 중 | 정상 |
| `/getRadioActiveMaterList` | 방사성 물질 데이터 조회 | ⚠️ 미사용 | 대기 |

### 환경부 수질 DB API 활용 가이드

#### 📋 서비스 개요
- **서비스명**: 국립환경과학원 수질 정보 OpenAPI
- **서비스 ID**: `WaterQualityService`
- **인증 방식**: 서비스 Key 인증 (GPKI)
- **데이터 형식**: XML, JSON
- **운영환경 URL**: http://apis.data.go.kr/1480523/WaterQualityService
- **데이터 갱신 주기**: 수질자동측정망 월 1회 (3개월 전 데이터 공개)

#### 🔧 주요 오퍼레이션

| 오퍼레이션명 | 설명 | 활용 목적 |
|-------------|------|-----------|
| `getWaterMeasuringList` | 물환경 수질측정망 운영결과 DB | Tp(총인), Tn(총질소) 데이터 수집 |
| `getRealTimeWaterQualityList` | 수질자동측정망 운영결과 DB | 실시간 수질 데이터 조회 |
| `getSgisDrinkWaterQualityList` | 토양지하수 먹는물 공동시설 운영결과 DB | 추가 수질 정보 |

#### 📊 수질 측정 항목

| 항목명 | 설명 | 단위 | 가중치 |
|--------|------|------|--------|
| `itemTp` | 총인(T-P) | mg/L | 0.99 |
| `itemTn` | 총질소(T-N) | mg/L | 0.01 |
| `itemDoc` | 용존산소(DO) | mg/L | - |
| `itemBod` | 생화학적산소요구량(BOD) | mg/L | - |
| `itemCod` | 화학적산소요구량(COD) | mg/L | - |

#### 🔗 API 요청 예시

**물환경 수질측정망 운영결과 DB**
```http
GET http://apis.data.go.kr/1480523/WaterQualityService/getWaterMeasuringList?
numOfRows=10&pageNo=1&serviceKey=YOUR_API_KEY&resultType=xml
```

**수질자동측정망 운영결과 DB**
```http
GET http://apis.data.go.kr/1480523/WaterQualityService/getRealTimeWaterQualityList?
numOfRows=10&pageNo=1&serviceKey=YOUR_API_KEY&resultType=xml
```

**서비스 URL**: `http://apis.data.go.kr/1480523/WaterQualityService`

#### 📨 요청 파라미터

| 파라미터 (영문) | 파라미터 (국문) | 크기 | 필수/선택 | 샘플 데이터 | 설명 |
|-----------------|-----------------|------|----------|-------------|------|
| `ServiceKey`    | 서비스키        | 99   | 필수     | -           | 공공데이터포털에서 받은 인증키 |
| `pageNo`        | 페이지 번호     | 4    | 선택     | 1           | 페이지 번호 (기본 값: 1) |
| `numOfRows`     | 한 페이지 결과 수 | 4    | 선택     | 10          | 페이지 크기 (기본 값: 10) |
| `resultType`    | 결과형식        | 4    | 선택     | XML         | 결과형식(XML/JSON) |
| `ptNoList`      | 검색조건 기관   | 100  | 선택     | 3008A40,2012F50 | 측정소 다건 검색시 콤마(,)로 구분 (예시: ptNoList=3008A40,2012F50) 물환경_코드_코드명 엑셀 파일 참조 |
| `wmyrList`      | 검색조건 연도   | 100  | 선택     | 2012,2013   | 측정년도 다건 검색시 콤마(,)로 구분 (예시: wmyrList=2012,2013) |
| `wmodList`      | 검색조건 월     | 100  | 선택     | 01,02,03    | 측정월 다건 검색시 콤마(,)로 구분 (예시: wmodList=01,02,03) (1~9월까지는 '01'~'09'로 표시) |

#### 🔑 인증키 설정

**발급받은 인증키**: `fHcQ3zRYg8x%2BtsTv5ip4R6FzOFHvm9AFtsZfq%2Bbr5vnk9T5y2twHxbKaVdWAcUntjaUo9whb6vbS4LpxMrUbFg%3D%3D`

**인코딩된 인증키**: `fHcQ3zRYg8x%2BtsTv5ip4R6FzOFHvm9AFtsZfq%2Bbr5vnk9T5y2twHxbKaVdWAcUntjaUo9whb6vbS4LpxMrUbFg%3D%3D`

**디코딩된 인증키**: `fHcQ3zRYg8x+tsTv5ip4R6FzOFHvm9AFtsZfq+br5vnk9T5y2twHxbKaVdWAcUntjaUo9whb6vbS4LpxMrUbFg==`

#### 🔧 API 키 사용법

**1단계: 인코딩키 우선 사용**
```python
# 권장 방법 (공식 문서 기준)
api_key = "fHcQ3zRYg8x%2BtsTv5ip4R6FzOFHvm9AFtsZfq%2Bbr5vnk9T5y2twHxbKaVdWAcUntjaUo9whb6vbS4LpxMrUbFg%3D%3D"
```

**2단계: 인코딩키 오류 시 디코딩키 사용**
```python
# 대안 방법 (인코딩키 오류 시)
api_key = "fHcQ3zRYg8x+tsTv5ip4R6FzOFHvm9AFtsZfq+br5vnk9T5y2twHxbKaVdWAcUntjaUo9whb6vbS4LpxMrUbFg=="
```

> **참고**: 
> - **공식 문서 권장**: API 요청 시 인코딩된 키를 우선 사용하세요.
> - **인코딩키 사용 불가 시**: 디코딩된 키를 대안으로 사용할 수 있습니다.
> - **인코딩키**: URL 인코딩이 적용된 상태로, 대부분의 경우 정상 작동합니다.
> - **디코딩키**: 인코딩키 사용 시 오류가 발생하면 이 키를 사용해보세요.

#### 📩 응답 데이터 구조

```xml
<response>
  <header>
    <resultCode>00</resultCode>
    <resultMsg>NORMAL SERVICE</resultMsg>
  </header>
  <body>
    <items>
      <item>
        <ptNo>측정소코드</ptNo>
        <ptNm>측정소명</ptNm>
        <addr>주소</addr>
        <itemTp>0.884</itemTp>
        <itemTn>13.824</itemTn>
        <latDgr>37</latDgr>
        <lonDgr>127</lonDgr>
      </item>
    </items>
  </body>
</response>
```

### 🚨 API 서버 문제 시 대안: 로컬 CSV 파일 사용

**현재 상황**: API 서버 문제로 인해 API 키 등록이 실패하고 있습니다.

#### 📁 로컬 CSV 파일 구조

API 서버 문제 시 사용할 로컬 CSV 파일을 `data/raw/` 폴더에 배치하세요.

**필요한 CSV 파일**:
- `water_quality_data.csv` - 수질 데이터
- `measurement_stations.csv` - 측정소 정보

**CSV 파일 형식**:

**water_quality_data.csv**
```csv
ptNo,ptNm,addr,itemTp,itemTn,latDgr,lonDgr,measurement_date
3008A40,한강수계-팔당,경기도 가평군 청평면,0.884,13.824,37.123,127.456,2024-01-15
2012F50,낙동강수계-구미,경상북도 구미시,1.234,15.678,36.789,128.123,2024-01-15
...
```

**measurement_stations.csv**
```csv
ptNo,ptNm,addr,latDgr,lonDgr,region_code,region_name
3008A40,한강수계-팔당,경기도 가평군 청평면,37.123,127.456,41,경기도
2012F50,낙동강수계-구미,경상북도 구미시,36.789,128.123,47,경상북도
...
```

#### 🔧 로컬 CSV 사용 설정

**1. 설정 파일 수정**
```python
# src/utils/config.py
# USE_LOCAL_CSV 설정이 제거되었습니다. 새로운 구조에서는 자동으로 처리됩니다.
```

**2. 데이터 수집기 수정**
```python
# src/data_collection/data_collector.py
def collect_data(self):
    # 새로운 구조: API → CSV 업데이트 → 기존 CSV
    # 자동으로 우선순위에 따라 처리됩니다.
```

**3. 실행 방법**
```bash
# 새로운 구조로 자동 실행
python scripts/run_pipeline.py

# 테스트 모드
python scripts/run_pipeline.py --test
```

#### 📋 CSV 파일 준비 가이드

**1. 데이터 수집**
- 환경부 수질 DB에서 직접 다운로드
- 공공데이터포털에서 CSV 형태로 내려받기
- 기존 API 응답 데이터를 CSV로 변환

**2. 파일 위치**
```
data/
├── raw/
│   ├── water_quality_data.csv    # 수질 데이터
│   └── measurement_stations.csv  # 측정소 정보
```

**3. 데이터 형식 확인**
- UTF-8 인코딩 사용
- 쉼표(,)로 구분
- 헤더 행 포함
- 필수 컬럼: ptNo, ptNm, addr, itemTp, itemTn, latDgr, lonDgr

#### ⚠️ 주의사항

- **데이터 갱신**: 로컬 CSV 파일은 정기적으로 업데이트 필요
- **데이터 정확성**: API 데이터와 동일한 형식으로 준비
- **파일 경로**: 절대 경로 또는 상대 경로 정확히 설정
- **인코딩**: UTF-8 인코딩으로 저장

#### 📊 응답 데이터 항목 상세

| 항목명(국문)     | 항목명(영문)   | 항목크기 | 항목구분 | 샘플데이터             | 항목설명       |
|------------------|----------------|-----------|----------|------------------------|----------------|
| 결과코드         | resultCode     | 2         | 필       | 00                     | 결과코드       |
| 결과메시지       | resultMsg      | 50        | 필       | NORMAL SERVICE         | 결과메시지     |
| 한 페이지 결과 수 | numOfRows      | 4         | 필       | 10                     | 한 페이지 결과 수 |
| 페이지 번호       | pageNo         | 4         | 필       | 1                      | 페이지번호     |
| 전체 결과 수     | totalCount     | 4         | 필       | 460261                 | 전체 결과 수   |
| 행번호           | rowno          | 4         | 필       | 1                      | 행번호         |
| 조사지점코드     | ptNo           | 21        | 필       | 2012F50                | 조사지점코드   |
| 조사지점명       | ptNm           | 60        | 필       | 달서천                 | 조사지점명     |
| 조사지점 주소    | addr           | 200       | 필       | 대구광역시 서구 비산동 | 조사지점 주소  |
| 조사기관명       | orgNm          | 300       | 필       | 대구광역시 보건환경연구원 | 조사기관명  |
| 측정년도         | wmyr           | 12        | 필       | 2012                   | 측정년도       |
| 검사본기/회차    | wmod           | 6         | 필       | 02                     | 검사본기/회차  |
| 검사회차         | wmwk           | 6         | 필       | 1회차                  | 검사회차       |
| 경도-도          | lonDgr         | 8         | 옵       |                        | 경도-도        |
| 경도-분          | lonMin         | 7         | 옵       |                        | 경도-분        |
| 경도-초          | lonSec         | 7         | 옵       |                        | 경도-초        |
| 위도-도          | latDgr         | 7         | 옵       |                        | 위도-도        |
| 위도-분          | latMin         | 7         | 옵       |                        | 위도-분        |
| 위도-초          | latSec         | 7         | 옵       |                        | 위도-초        |
| 검사일자         | wmcymd         | 255       | 필       | 2012.02.03             | 검사일자       |
| 측정값(총질소) (단위: mg/L)  | itemTn       | 19        | 옵       | 13.824       | 측정값(총질소) (단위: mg/L)        |
| 측정값(총인) (단위: mg/L)    | itemTp       | 19        | 옵       | 0.884        | 측정값(총인) (단위: mg/L)          |

#### ⚠️ 에러 코드 및 대응

| 에러코드 | 에러메시지                                         | 설명                           |
|----------|----------------------------------------------------|--------------------------------|
| 1        | APPLICATION_ERROR                                   | 어플리케이션 에러              |
| 4        | HTTP_ERROR                                          | HTTP 에러                      |
| 12       | NO_OPENAPI_SERVICE_ERROR                            | 해당 오픈 API 서비스가 없거나 폐기됨 |
| 20       | SERVICE_ACCESS_DENIED_ERROR                         | 서비스 접근거부                 |
| 22       | LIMITED_NUMBER_OF_SERVICE_REQUESTS_EXCEEDS_ERROR    | 서비스 요청제한횟수 초과에러     |
| 23       | LIMITED_NUMBER_OF_SERVICE_REQUESTS_PER_SECOND_EXCEEDS_ERROR | 최대동시 요청수 초과에러       |
| 30       | SERVICE_KEY_IS_NOT_REGISTERED_ERROR                 | 등록되지 않은 서비스키         |
| 31       | DEADLINE_HAS_EXPIRED_ERROR                          | 활용기간 만료                  |
| 32       | UNREGISTERED_IP_ERROR                               | 등록되지 않은 IP               |
| 99       | UNKNOWN_ERROR                                       | 기타에러                       |

### 가중치 적용 공식
```
수질 평가 점수 = (Tp × 0.99) + (Tn × 0.01)
```

#### 📚 수질측정망 관련 자료

**측정소 코드 참조 자료**
- **파일명**: `물환경 수질측정망 운영결과 DB_물 환경_코드_코드명.csv`
- **용도**: 전국 수질측정소 코드 및 명칭 참조
- **포함 정보**: 측정소 코드, 측정소명, 주소, 위도, 경도

**측정소 코드 사용 예시**
```python
# 측정소 코드 리스트 예시
ptNoList = "3008A40,2012F50,3008A41,2012F51"

# API 요청 시 사용
url = f"http://apis.data.go.kr/1480523/WaterQualityService/getWaterMeasuringList?ptNoList={ptNoList}&serviceKey={api_key}"
```

**데이터 검색 팁**
- **측정소 다건 검색**: 콤마(,)로 구분하여 여러 측정소 동시 조회
- **연도별 검색**: `wmyrList=2023,2024` 형태로 다년도 데이터 조회
- **월별 검색**: `wmodList=01,02,03` 형태로 다월 데이터 조회 (1~9월은 '01'~'09' 형식)
- **결과 형식**: XML 또는 JSON 선택 가능

## Tp/Tn 알고리즘 및 시각화

### 🔬 Tp/Tn 가중치 알고리즘

#### 📊 수학적 원리

**가중 평균 공식**:
```
수질 평가 점수 = (Tp × 0.99) + (Tn × 0.01)
```

**가중치 설정 이유**:
- **Tp(총인) 가중치 0.99**: 수질 오염의 주요 지표로, 부영양화 현상의 핵심 원인
- **Tn(총질소) 가중치 0.01**: 보조 지표로, Tp와 함께 수질 상태를 종합적으로 평가

#### 🔧 알고리즘 구현

```python
def calculate_weighted_score(tp_value: float, tn_value: float, 
                           tp_weight: float = 0.99, tn_weight: float = 0.01) -> float:
    """
    가중 평균 점수 계산
    
    Args:
        tp_value: 총인 값 (mg/L)
        tn_value: 총질소 값 (mg/L)
        tp_weight: 총인 가중치 (0.99)
        tn_weight: 총질소 가중치 (0.01)
        
    Returns:
        float: 가중 평균 점수
    """
    if pd.isna(tp_value) or pd.isna(tn_value):
        return np.nan
    
    return (tp_value * tp_weight) + (tn_value * tn_weight)
```

#### 📈 위험도 분류 기준

| 위험도 레벨 | 점수 범위 | 색상 | 의미 |
|-------------|-----------|------|------|
| Low | 0.0 - 0.5 | 초록색 (#2E8B57) | 수질 우수 |
| Medium | 0.5 - 1.0 | 연초록색 (#90EE90) | 수질 양호 |
| High | 1.0 - 2.0 | 노란색 (#FFFF00) | 수질 보통 |
| Very High | 2.0+ | 빨간색 (#FF0000) | 수질 매우 나쁨 |

### 🎨 시각화 시스템

#### 📊 1. 지도 시각화

**지리적 분포 지도**:
- **GeoPandas** 사용하여 시군구 경계 표시
- **좌표 기반 점 마킹**으로 측정소 위치 표시
- **5단계 색상 매핑**으로 수질 상태 시각화
- **지역명 표시** 및 **범례** 포함
- **SHP 파일과 좌표계 맞춤** (WGS84 EPSG:4326)

```python
def create_integrated_water_quality_map(output_file='integrated_water_quality_map.png'):
    """
    수질 측정소가 마킹된 전라남도 통합 지도 생성
    
    Returns:
        pd.DataFrame: 처리된 수질 데이터
    """
    # 1. SHP 파일 로드 및 좌표계 변환
    gdf = gpd.read_file(shp_path)
    if gdf.crs is not None and "4326" not in str(gdf.crs):
        gdf = gdf.to_crs(epsg=4326)  # WGS84로 변환
    
    # 2. 수질 데이터 준비 및 경보 계산
    water_quality_df = create_sample_water_quality_data()
    water_quality_df['alert_level'] = water_quality_df.apply(
        lambda row: calculate_alert_level(row['총인_TP_mgL'], row['총질소_TN_mgL']), 
        axis=1
    )
    
    # 3. GeoDataFrame으로 변환 (좌표 기반)
    water_quality_gdf = gpd.GeoDataFrame(
        water_quality_df,
        geometry=gpd.points_from_xy(water_quality_df['경도'], water_quality_df['위도']),
        crs="EPSG:4326"
    )
    
    # 4. 지도 생성 및 측정소 마킹
    fig, ax = plt.subplots(1, 1, figsize=(12, 14))
    
    # 기본 지도 그리기
    jeonnam_gdf.plot(color='lightgray', edgecolor='black', linewidth=0.5, ax=ax, alpha=0.7)
    
    # 측정소별로 작은 점 마킹 (좌표 기반)
    for idx, row in water_quality_gdf.iterrows():
        x, y = row['경도'], row['위도']
        alert_level = row['alert_level']
        color = alert_colors.get(alert_level, '#808080')
        
        # 작은 원형 점으로 마킹
        ax.scatter(x, y, c=color, s=50, alpha=0.9, edgecolors='black', linewidth=0.5, zorder=5)
    
    return water_quality_df
```

**주요 변경사항**:
- ✅ **측정소 명 제거**: 텍스트 정보 없이 좌표 기반 점 마킹
- ✅ **작은 점 크기**: s=50으로 설정하여 깔끔한 시각화
- ✅ **SHP 좌표계 맞춤**: WGS84 (EPSG:4326)로 통일
- ✅ **단순화된 마킹**: 복잡한 텍스트 대신 색상으로 경보 단계 구분

#### 📈 2. 차트 시각화

**위험도 분포 차트**:
- **파이 차트**: 위험도 레벨별 비율
- **막대 차트**: 위험도 레벨별 측정소 수
- **색상 코딩**: 레벨별 일관된 색상 사용

```python
def create_risk_distribution_chart(data: pd.DataFrame):
    """
    위험도 분포 차트 생성
    
    Args:
        data: 수질 데이터
        
    Returns:
        str: 생성된 차트 파일 경로
    """
    # 1. 위험도 레벨별 개수 계산
    risk_counts = data['risk_level'].value_counts()
    
    # 2. 색상 매핑
    colors = {
        'low': '#2E8B57',      # 초록색
        'medium': '#90EE90',    # 연초록색
        'high': '#FFFF00',      # 노란색
        'very_high': '#FF0000'  # 빨간색
    }
    
    # 3. 파이 차트 + 막대 차트 생성
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # 파이 차트
    ax1.pie(risk_counts.values, labels=risk_counts.index, 
            autopct='%1.1f%%', colors=[colors.get(level, '#808080') for level in risk_counts.index])
    
    # 막대 차트
    bars = ax2.bar(risk_counts.index, risk_counts.values, 
                   color=[colors.get(level, '#808080') for level in risk_counts.index])
    
    return save_path
```

**지역별 비교 차트**:
- **박스플롯**: 지역별 수질 점수 분포
- **평균값 비교**: 지역별 평균 위험도 점수
- **표준편차**: 지역별 변동성 표시

**상관관계 히트맵**:
- **Tp vs Tn**: 두 지표 간의 상관관계
- **지역별 상관관계**: 지역간 수질 패턴 비교
- **시계열 상관관계**: 시간에 따른 변화 패턴

#### 🌐 3. 웹 시각화

**반응형 대시보드**:
- **HTML/CSS/JavaScript** 조합
- **Folium** 지도 라이브러리 사용
- **실시간 업데이트** 기능

```python
def create_web_dashboard(risk_data: pd.DataFrame, map_file: str, chart_files: List[str]):
    """
    웹 대시보드 생성
    
    Args:
        risk_data: 위험도 데이터
        map_file: 지도 파일 경로
        chart_files: 차트 파일 경로 리스트
        
    Returns:
        str: 생성된 HTML 파일 경로
    """
    # 1. HTML 템플릿 생성
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>전국 수질 평가 대시보드</title>
        <style>
            .dashboard {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                padding: 20px;
            }}
            .map-container {{
                grid-column: 1 / -1;
            }}
        </style>
    </head>
    <body>
        <div class="dashboard">
            <div class="map-container">
                <img src="{map_file}" alt="수질 평가 지도" style="width: 100%;">
            </div>
            {''.join([f'<div><img src="{chart}" alt="차트" style="width: 100%;"></div>' for chart in chart_files])}
        </div>
    </body>
    </html>
    """
    
    return save_html_file(html_content)
```

### 🎯 시각화 특징

#### 📊 데이터 표현 방식

1. **색상 기반 분류**:
   - **5단계 색상 체계**: 초록 → 연초록 → 노랑 → 주황 → 빨강
   - **직관적 이해**: 색상으로 수질 상태 즉시 파악
   - **일관성**: 모든 시각화에서 동일한 색상 체계 사용

2. **통계적 표현**:
   - **평균값**: 지역별 평균 수질 점수
   - **표준편차**: 지역별 변동성
   - **백분위수**: 상위/하위 수질 지역 식별

3. **지리적 표현**:
   - **시군구 경계**: 정확한 행정구역 표시
   - **측정소 위치**: 실제 측정소 좌표 반영
   - **지역명 표시**: 사용자 친화적 지역명

#### 🔧 기술적 구현

1. **데이터 전처리**:
   ```python
   # 결측값 처리
   data = data.dropna(subset=['itemTp', 'itemTn'])
   
   # 이상값 제거
   data = data[(data['itemTp'] >= 0) & (data['itemTp'] <= 1000)]
   data = data[(data['itemTn'] >= 0) & (data['itemTn'] <= 1000)]
   ```

2. **색상 매핑**:
   ```python
   def get_color_by_risk_level(risk_level: str) -> str:
       color_mapping = {
           'low': '#2E8B57',      # 초록색
           'medium': '#90EE90',    # 연초록색
           'high': '#FFFF00',      # 노란색
           'very_high': '#FF0000', # 빨간색
           'unknown': '#808080'    # 회색
       }
       return color_mapping.get(risk_level, '#808080')
   ```

3. **범례 생성**:
   ```python
   legend_elements = [
       plt.Rectangle((0,0),1,1, facecolor='#2E8B57', label='우수'),
       plt.Rectangle((0,0),1,1, facecolor='#90EE90', label='양호'),
       plt.Rectangle((0,0),1,1, facecolor='#FFFF00', label='보통'),
       plt.Rectangle((0,0),1,1, facecolor='#FFA500', label='나쁨'),
       plt.Rectangle((0,0),1,1, facecolor='#FF0000', label='매우 나쁨')
   ]
   ```

### 📋 출력 파일 형식

#### 🗺️ 지도 파일
- **형식**: PNG (고해상도 300 DPI)
- **크기**: 12×8 인치 (가로형)
- **포함 요소**: 지도, 범례, 제목, 지역명

#### 📊 차트 파일
- **위험도 분포**: 파이 차트 + 막대 차트
- **지역별 비교**: 박스플롯 + 평균값 차트
- **상관관계**: 히트맵
- **종합 대시보드**: 모든 차트 통합

#### 🌐 웹 파일
- **메인 페이지**: index.html
- **지도 페이지**: map_YYYYMMDD_HHMMSS.html
- **대시보드 페이지**: dashboard_YYYYMMDD_HHMMSS.html
- **반응형 디자인**: 모바일, 태블릿, 데스크톱 지원

## 웹 게시 기능

### 🌐 자동 웹 게시
파이프라인 실행 시 생성된 지도와 차트가 자동으로 웹사이트에 게시됩니다.

#### 📁 웹 디렉토리 구조
```
web/
├── index.html                    # 메인 인덱스 페이지
├── map_YYYYMMDD_HHMMSS.html     # 수질 모니터링 지도
├── dashboard_YYYYMMDD_HHMMSS.html # 수질 분석 대시보드
└── static/
    ├── images/                   # 게시된 이미지 파일들
    ├── css/                      # 스타일시트
    └── js/                       # 자바스크립트
```

#### 🎨 웹 페이지 특징
- **반응형 디자인**: 모바일, 태블릿, 데스크톱 지원
- **현대적 UI**: 그라데이션 배경과 카드 레이아웃
- **자동 브라우저 열기**: 결과 생성 후 자동으로 브라우저에서 확인
- **실시간 업데이트**: 파이프라인 실행 시마다 최신 결과 반영

#### 📊 게시되는 콘텐츠
1. **수질 모니터링 지도**: 전국 수질 상태 시각화
2. **위험도 분포 차트**: 지역별 위험도 분석
3. **지역별 비교 차트**: 시군구별 수질 비교
4. **트렌드 분석 차트**: 시간별 수질 변화
5. **상관관계 히트맵**: 수질 항목 간 상관관계
6. **종합 대시보드**: 모든 분석 결과 통합

#### 🔧 웹 게시 사용법
```bash
# 파이프라인 실행 (웹 게시 포함)
python scripts/run_pipeline.py

# 웹 파일 확인
ls web/
# - index.html
# - map_20241201_143022.html
# - dashboard_20241201_143022.html
```

## 기술 스택

- **Python**: 메인 프로그래밍 언어
- **GeoPandas**: 지리 데이터 처리
- **Matplotlib**: 지도 시각화
- **Folium**: 웹 기반 지도 생성
- **Requests**: API 통신
- **Pandas**: 데이터 처리
- **Seaborn**: 통계 시각화
- **Schedule**: 스케줄링
- **HTML/CSS**: 웹 페이지 생성

## 설치 및 사용 방법

### 📋 필수 요구사항

- Python 3.8 이상
- pip (Python 패키지 관리자)
- 인터넷 연결 (API 데이터 수집용)

### 🔧 설치 방법

1. **저장소 클론**
```bash
git clone https://github.com/your-username/water-quality-assessment.git
cd water-quality-assessment
```

2. **가상환경 생성 (권장)**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. **의존성 설치**
```bash
pip install -r requirements.txt
```

4. **환경 변수 설정**
```bash
# env_example.txt를 참고하여 .env 파일 생성
cp env_example.txt .env
# .env 파일에서 API 키 설정
```

### 🚀 사용 방법

1. **기본 실행**
```bash
python main.py
```

2. **전체 파이프라인 실행**
```bash
python scripts/run_pipeline.py
```

3. **웹 서버 실행**
```bash
python web_server.py
```

4. **개별 모듈 실행**
```bash
# 데이터 수집
python src/data_collection/data_collector.py

# 데이터 처리
python src/data_processing/data_processor.py

# 지도 생성
python src/visualization/map_generator.py
```

### 📊 결과 확인

- **지도 파일**: `integrated_water_quality_map.png`
- **웹 페이지**: `web/` 폴더 내 HTML 파일들
- **로그 파일**: `logs/` 폴더

## 프로젝트 확장 계획

1. **전국 시군구 shapefile 확보**
2. **환경부 API 키 발급 및 설정**
3. **전국 측정소 데이터 수집**
4. **가중치 기반 평가 알고리즘 구현**
5. **5단계 색상 매핑 시스템 구축**
6. **웹 기반 대시보드 개발**

## 기존 프로젝트에서의 확장

- **지역 확장**: 전라남도 → 전국
- **데이터 소스**: 기존 API → 환경부 수질 DB API
- **평가 방식**: 단순 색상 → 가중치 기반 수질 평가
- **시각화**: 기본 지도 → 수질 상태별 색상 매핑
- **구조 개선**: 단일 파일 → 모듈화된 폴더 구조
- **데이터 수집**: 새로운 우선순위 구조 (API → CSV 업데이트 → 기존 CSV) 