import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 환경부 수질측정망 API 설정
# 실제 API 키는 .env 파일에 저장하세요
WATER_API_KEY = os.getenv('WATER_API_KEY', 'your_api_key_here')
WATER_API_BASE_URL = "http://apis.data.go.kr/B500001/water_quality/"

# 데이터 경로 설정
DATA_DIR = "data"
SHAPEFILE_DIR = os.path.join(DATA_DIR, "shapefiles")
WATER_QUALITY_DIR = os.path.join(DATA_DIR, "water_quality")
OUTPUT_DIR = os.path.join(DATA_DIR, "output")

# 수질 기준치 (환경부 기준 - 실제 기준으로 수정 필요)
TN_THRESHOLD = 1.0  # mg/L (총질소)
TP_THRESHOLD = 0.05  # mg/L (총인)

# 위험도 등급 설정
RISK_LEVELS = {
    '매우 안전': 1,
    '안전': 2, 
    '보통': 3,
    '위험': 4,
    '매우 위험': 5
}

# 지도 설정
MAP_CENTER = [36.5, 127.5]  # 한국 중심 좌표
MAP_ZOOM = 7
MAP_TITLE = "한국 하천 수질 고위험 지역 지도"

# 자동 갱신 설정
UPDATE_TIME = "02:00"  # 매일 새벽 2시에 갱신 