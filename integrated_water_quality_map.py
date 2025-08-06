import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import warnings
import re
import time
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_collection.data_collector import WaterQualityCollector
from src.utils.config import config
from src.utils.logger import logger

warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def calculate_weighted_score(tp_value, tn_value, tp_weight=0.99, tn_weight=0.01):
    """가중치 기반 수질 점수 계산"""
    weighted_score = (tp_value * tp_weight) + (tn_value * tn_weight)
    return weighted_score

def calculate_alert_level_by_percentile(score, all_scores):
    """백분위 기반 5단계 경보 단계 계산"""
    if len(all_scores) == 0:
        return '1단계'
    
    # 백분위 계산
    percentile = (all_scores < score).sum() / len(all_scores) * 100
    
    # 5단계 분류 (20%씩)
    if percentile <= 20:
        return '1단계'  # 초록색 - 수질 우수
    elif percentile <= 40:
        return '2단계'  # 연초록색 - 수질 양호
    elif percentile <= 60:
        return '3단계'  # 노란색 - 수질 보통
    elif percentile <= 80:
        return '4단계'  # 주황색 - 수질 나쁨
    else:
        return '5단계'  # 빨간색 - 수질 매우 나쁨

def parse_coordinate(coord_str):
    """좌표 문자열을 도/분/초 형식에서 십진수로 변환 (실제 데이터 형식에 맞게 수정)"""
    try:
        coord_str = str(coord_str).strip()
        
        # 이미 십진수인 경우
        if coord_str.replace('.', '').replace('-', '').isdigit():
            return float(coord_str)
        
        # 실제 데이터 형식에 맞는 패턴들
        # 예: "128°40'35.4"" 또는 "128°20'.2"" 또는 "128°20'0.2""
        patterns = [
            r'(\d+)°(\d+)\'(\d+\.?\d*)\"',  # 128°40'35.4"
            r'(\d+)°(\d+)\'\.(\d+\.?\d*)\"',  # 128°20'.2" (분이 0인 경우)
            r'(\d+)°(\d+)\'(\d+)',          # 128°40'35
            r'(\d+)°(\d+)\'\.(\d+)',        # 128°20'.2 (분이 0인 경우)
        ]
        
        for pattern in patterns:
            match = re.match(pattern, coord_str)
            if match:
                degrees = float(match.group(1))
                minutes = float(match.group(2))
                seconds = float(match.group(3))
                
                # 십진수로 변환
                decimal = degrees + (minutes / 60) + (seconds / 3600)
                return decimal
        
        # 패턴이 맞지 않는 경우 None 반환
        print(f"좌표 변환 실패: {coord_str}")
        return None
        
    except Exception as e:
        print(f"좌표 변환 오류: {coord_str} -> {e}")
        return None

def load_real_water_quality_data():
    """README 구조에 맞는 모듈화된 데이터 수집기 사용"""
    print("모듈화된 데이터 수집기로 수질 데이터 로드 중...")
    
    try:
        # README 구조에 맞는 데이터 수집기 사용
        collector = WaterQualityCollector()
        water_quality_data = collector.collect_data()
        
        if water_quality_data is not None and not water_quality_data.empty:
            print(f"✅ 모듈화된 데이터 수집 완료: {len(water_quality_data)}개 측정소")
            
            # README 구조에 맞게 컬럼명 변환
            if 'ptNo' in water_quality_data.columns and 'ptNm' in water_quality_data.columns:
                # 이미 README 구조에 맞는 형태
                final_data = {
                    '측정소코드': water_quality_data['ptNo'].tolist(),
                    '측정소명': water_quality_data['ptNm'].tolist(),
                    '위도': water_quality_data['latDgr'].tolist() if 'latDgr' in water_quality_data.columns else [],
                    '경도': water_quality_data['lonDgr'].tolist() if 'lonDgr' in water_quality_data.columns else [],
                    '총인_TP_mgL': water_quality_data['itemTp'].tolist(),
                    '총질소_TN_mgL': water_quality_data['itemTn'].tolist()
                }
                
                return pd.DataFrame(final_data)
            else:
                print("❌ README 구조에 맞지 않는 데이터 형식")
                return None
        else:
            print("❌ 데이터 수집 실패")
            return None
            
    except Exception as e:
        print(f"데이터 로드 중 오류 발생: {e}")
        # 더미 데이터 반환
        return pd.DataFrame({
            '측정소코드': ['TEST001'],
            '측정소명': ['테스트측정소'],
            '위도': [35.0],
            '경도': [127.0],
            '총인_TP_mgL': [0.1],
            '총질소_TN_mgL': [1.0]
        })

def group_by_administrative_region(water_quality_df):
    """좌표 기반으로 시군구별로 측정소 데이터를 그룹화하고 평균 계산"""
    print("좌표 기반 시군구별 데이터 그룹화 중...")
    
    # 좌표 기반 시군구 매칭 함수 (시군구 단위로 세분화)
    def find_region_by_coordinates(lat, lon):
        """좌표를 기반으로 시군구 찾기 (시군구 단위 세분화)"""
        try:
            # 시군구 단위 좌표 범위 (더 세분화)
            region_ranges = {
                # 서울시 (25개 구)
                '강남구': {'lat': (37.5, 37.6), 'lon': (127.0, 127.1)},
                '강동구': {'lat': (37.5, 37.6), 'lon': (127.1, 127.2)},
                '강북구': {'lat': (37.6, 37.7), 'lon': (127.0, 127.1)},
                '강서구': {'lat': (37.5, 37.6), 'lon': (126.8, 126.9)},
                '관악구': {'lat': (37.4, 37.5), 'lon': (126.9, 127.0)},
                '광진구': {'lat': (37.5, 37.6), 'lon': (127.1, 127.2)},
                '구로구': {'lat': (37.4, 37.5), 'lon': (126.8, 126.9)},
                '금천구': {'lat': (37.4, 37.5), 'lon': (126.9, 127.0)},
                '노원구': {'lat': (37.6, 37.7), 'lon': (127.0, 127.1)},
                '도봉구': {'lat': (37.6, 37.7), 'lon': (127.0, 127.1)},
                '동대문구': {'lat': (37.5, 37.6), 'lon': (127.0, 127.1)},
                '동작구': {'lat': (37.4, 37.5), 'lon': (126.9, 127.0)},
                '마포구': {'lat': (37.5, 37.6), 'lon': (126.9, 127.0)},
                '서대문구': {'lat': (37.5, 37.6), 'lon': (126.9, 127.0)},
                '서초구': {'lat': (37.4, 37.5), 'lon': (127.0, 127.1)},
                '성동구': {'lat': (37.5, 37.6), 'lon': (127.0, 127.1)},
                '성북구': {'lat': (37.5, 37.6), 'lon': (127.0, 127.1)},
                '송파구': {'lat': (37.5, 37.6), 'lon': (127.1, 127.2)},
                '양천구': {'lat': (37.5, 37.6), 'lon': (126.8, 126.9)},
                '영등포구': {'lat': (37.5, 37.6), 'lon': (126.9, 127.0)},
                '용산구': {'lat': (37.5, 37.6), 'lon': (126.9, 127.0)},
                '은평구': {'lat': (37.6, 37.7), 'lon': (126.9, 127.0)},
                '종로구': {'lat': (37.5, 37.6), 'lon': (127.0, 127.1)},
                '중구': {'lat': (37.5, 37.6), 'lon': (127.0, 127.1)},
                '중랑구': {'lat': (37.5, 37.6), 'lon': (127.1, 127.2)},
                
                # 경기도 주요 시군구
                '수원시': {'lat': (37.2, 37.3), 'lon': (126.9, 127.0)},
                '성남시': {'lat': (37.4, 37.5), 'lon': (127.1, 127.2)},
                '용인시': {'lat': (37.2, 37.3), 'lon': (127.1, 127.2)},
                '부천시': {'lat': (37.5, 37.6), 'lon': (126.7, 126.8)},
                '안산시': {'lat': (37.3, 37.4), 'lon': (126.8, 126.9)},
                '안양시': {'lat': (37.3, 37.4), 'lon': (126.9, 127.0)},
                '평택시': {'lat': (36.9, 37.0), 'lon': (127.1, 127.2)},
                '시흥시': {'lat': (37.3, 37.4), 'lon': (126.8, 126.9)},
                '김포시': {'lat': (37.6, 37.7), 'lon': (126.6, 126.7)},
                '광명시': {'lat': (37.4, 37.5), 'lon': (126.8, 126.9)},
                '광주시': {'lat': (37.4, 37.5), 'lon': (127.2, 127.3)},
                '군포시': {'lat': (37.3, 37.4), 'lon': (126.9, 127.0)},
                '하남시': {'lat': (37.5, 37.6), 'lon': (127.2, 127.3)},
                '오산시': {'lat': (37.1, 37.2), 'lon': (127.0, 127.1)},
                '이천시': {'lat': (37.2, 37.3), 'lon': (127.4, 127.5)},
                '안성시': {'lat': (37.0, 37.1), 'lon': (127.2, 127.3)},
                '의왕시': {'lat': (37.3, 37.4), 'lon': (127.0, 127.1)},
                '양평군': {'lat': (37.4, 37.5), 'lon': (127.4, 127.5)},
                '여주시': {'lat': (37.2, 37.3), 'lon': (127.6, 127.7)},
                '과천시': {'lat': (37.4, 37.5), 'lon': (127.0, 127.1)},
                '고양시': {'lat': (37.6, 37.7), 'lon': (126.8, 126.9)},
                '남양주시': {'lat': (37.6, 37.7), 'lon': (127.2, 127.3)},
                '파주시': {'lat': (37.8, 37.9), 'lon': (126.7, 126.8)},
                '의정부시': {'lat': (37.7, 37.8), 'lon': (127.0, 127.1)},
                '양주시': {'lat': (37.8, 37.9), 'lon': (127.0, 127.1)},
                '구리시': {'lat': (37.5, 37.6), 'lon': (127.1, 127.2)},
                '포천시': {'lat': (37.8, 37.9), 'lon': (127.2, 127.3)},
                '동두천시': {'lat': (37.9, 38.0), 'lon': (127.0, 127.1)},
                '가평군': {'lat': (37.8, 37.9), 'lon': (127.4, 127.5)},
                '연천군': {'lat': (38.0, 38.1), 'lon': (127.0, 127.1)},
                
                # 부산시 주요 구
                '중구': {'lat': (35.1, 35.2), 'lon': (129.0, 129.1)},
                '서구': {'lat': (35.1, 35.2), 'lon': (129.0, 129.1)},
                '동구': {'lat': (35.1, 35.2), 'lon': (129.0, 129.1)},
                '영도구': {'lat': (35.0, 35.1), 'lon': (129.0, 129.1)},
                '부산진구': {'lat': (35.1, 35.2), 'lon': (129.0, 129.1)},
                '동래구': {'lat': (35.2, 35.3), 'lon': (129.0, 129.1)},
                '남구': {'lat': (35.1, 35.2), 'lon': (129.0, 129.1)},
                '북구': {'lat': (35.2, 35.3), 'lon': (129.0, 129.1)},
                '해운대구': {'lat': (35.1, 35.2), 'lon': (129.1, 129.2)},
                '사하구': {'lat': (35.0, 35.1), 'lon': (129.0, 129.1)},
                '금정구': {'lat': (35.2, 35.3), 'lon': (129.0, 129.1)},
                '강서구': {'lat': (35.2, 35.3), 'lon': (128.9, 129.0)},
                '연제구': {'lat': (35.2, 35.3), 'lon': (129.0, 129.1)},
                '수영구': {'lat': (35.1, 35.2), 'lon': (129.1, 129.2)},
                '사상구': {'lat': (35.1, 35.2), 'lon': (128.9, 129.0)},
                '기장군': {'lat': (35.2, 35.3), 'lon': (129.2, 129.3)},
                
                # 대구시 주요 구
                '중구': {'lat': (35.8, 35.9), 'lon': (128.5, 128.6)},
                '동구': {'lat': (35.8, 35.9), 'lon': (128.6, 128.7)},
                '서구': {'lat': (35.8, 35.9), 'lon': (128.5, 128.6)},
                '남구': {'lat': (35.8, 35.9), 'lon': (128.5, 128.6)},
                '북구': {'lat': (35.8, 35.9), 'lon': (128.5, 128.6)},
                '수성구': {'lat': (35.8, 35.9), 'lon': (128.6, 128.7)},
                '달서구': {'lat': (35.8, 35.9), 'lon': (128.5, 128.6)},
                '달성군': {'lat': (35.7, 35.8), 'lon': (128.4, 128.5)},
                
                # 인천시 주요 구
                '중구': {'lat': (37.4, 37.5), 'lon': (126.5, 126.6)},
                '동구': {'lat': (37.4, 37.5), 'lon': (126.6, 126.7)},
                '미추홀구': {'lat': (37.4, 37.5), 'lon': (126.6, 126.7)},
                '연수구': {'lat': (37.4, 37.5), 'lon': (126.6, 126.7)},
                '남동구': {'lat': (37.4, 37.5), 'lon': (126.7, 126.8)},
                '부평구': {'lat': (37.5, 37.6), 'lon': (126.7, 126.8)},
                '계양구': {'lat': (37.5, 37.6), 'lon': (126.7, 126.8)},
                '서구': {'lat': (37.5, 37.6), 'lon': (126.6, 126.7)},
                '강화군': {'lat': (37.7, 37.8), 'lon': (126.4, 126.5)},
                '옹진군': {'lat': (37.4, 37.5), 'lon': (126.3, 126.4)},
                
                # 기타 주요 도시들 (시도 단위로 유지)
                '광주시': {'lat': (35.1, 35.2), 'lon': (126.8, 126.9)},
                '대전시': {'lat': (36.2, 36.4), 'lon': (127.3, 127.5)},
                '울산시': {'lat': (35.4, 35.6), 'lon': (129.2, 129.4)},
                '세종시': {'lat': (36.4, 36.6), 'lon': (127.2, 127.4)},
                '제주시': {'lat': (33.4, 33.6), 'lon': (126.5, 126.7)},
                '강원도': {'lat': (37.0, 38.5), 'lon': (127.5, 129.5)},
                '충청북도': {'lat': (36.0, 37.5), 'lon': (127.0, 128.5)},
                '충청남도': {'lat': (35.5, 37.0), 'lon': (126.0, 127.5)},
                '전라북도': {'lat': (35.5, 36.5), 'lon': (126.5, 127.8)},
                '전라남도': {'lat': (34.5, 36.0), 'lon': (126.0, 127.5)},
                '경상북도': {'lat': (35.5, 37.5), 'lon': (128.0, 129.5)},
                '경상남도': {'lat': (34.5, 36.0), 'lon': (127.5, 129.0)}
            }
            
            for region, ranges in region_ranges.items():
                if (ranges['lat'][0] <= lat <= ranges['lat'][1] and 
                    ranges['lon'][0] <= lon <= ranges['lon'][1]):
                    return region
            
            # 매칭되지 않으면 좌표 기반으로 추정 (시도 단위)
            if 37.0 <= lat <= 38.0 and 126.5 <= lon <= 127.5:
                return '경기도_기타'
            elif 35.5 <= lat <= 36.5 and 127.0 <= lon <= 128.5:
                return '충청북도_기타'
            elif 35.0 <= lat <= 36.0 and 128.0 <= lon <= 129.0:
                return '경상북도_기타'
            else:
                return '기타'
                
        except Exception as e:
            print(f"좌표 매칭 오류: {lat}, {lon} -> {e}")
            return '기타'
    
    # 좌표 기반 시군구 정보 추가
    water_quality_df['시군구'] = water_quality_df.apply(
        lambda row: find_region_by_coordinates(row['위도'], row['경도']), 
        axis=1
    )
    
    # 시군구별 평균 계산
    region_averages = water_quality_df.groupby('시군구').agg({
        '총인_TP_mgL': 'mean',
        '총질소_TN_mgL': 'mean',
        '위도': 'mean',
        '경도': 'mean'
    }).reset_index()
    
    # 가중치 점수 계산
    region_averages['가중치_점수'] = region_averages.apply(
        lambda row: calculate_weighted_score(row['총인_TP_mgL'], row['총질소_TN_mgL']), 
        axis=1
    )
    
    # 모든 가중치 점수로 백분위 계산
    all_scores = region_averages['가중치_점수'].values
    
    # 각 시군구별 경보 단계 계산
    region_averages['경보_단계'] = region_averages['가중치_점수'].apply(
        lambda score: calculate_alert_level_by_percentile(score, all_scores)
    )
    
    print(f"시군구별 평균 계산 완료: {len(region_averages)}개 시군구")
    print("시군구별 경보 단계 분포:")
    print(region_averages['경보_단계'].value_counts())
    
    return region_averages

def load_national_map():
    """전국 지도 데이터 로드 (성능 최적화)"""
    print("전국 지도 데이터 로드 중...")
    
    # 모든 지역의 SHP 파일 경로
    shp_paths = [
        "행정구역SHP지도/LARD_ADM_SECT_SGG_서울/LARD_ADM_SECT_SGG_11_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_부산/LARD_ADM_SECT_SGG_26_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_대구/LARD_ADM_SECT_SGG_27_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_인천/LARD_ADM_SECT_SGG_28_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_광주/LARD_ADM_SECT_SGG_29_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_대전/LARD_ADM_SECT_SGG_30_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_울산/LARD_ADM_SECT_SGG_31_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_세종/LARD_ADM_SECT_SGG_36_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_경기/LARD_ADM_SECT_SGG_41_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_충북/LARD_ADM_SECT_SGG_43_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_충남/LARD_ADM_SECT_SGG_44_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_전북특별자치도/LARD_ADM_SECT_SGG_52_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_전남/LARD_ADM_SECT_SGG_46_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_경북/LARD_ADM_SECT_SGG_47_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_경남/LARD_ADM_SECT_SGG_48_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_제주/LARD_ADM_SECT_SGG_50_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_강원특별자치도/LARD_ADM_SECT_SGG_51_202505.shp"
    ]
    
    # 모든 지역 데이터 통합 (메모리 효율적으로)
    all_gdfs = []
    for i, shp_path in enumerate(shp_paths):
        try:
            print(f"로드 중 ({i+1}/{len(shp_paths)}): {shp_path}")
            gdf = gpd.read_file(shp_path)
            
            # CRS 변환
            if gdf.crs is not None and "4326" not in str(gdf.crs):
                gdf = gdf.to_crs(epsg=4326)
            
            # 지오메트리 간소화 (성능 향상)
            print(f"지오메트리 간소화 중: {shp_path}")
            gdf['geometry'] = gdf['geometry'].simplify(0.001, preserve_topology=False)
            
            all_gdfs.append(gdf)
            print(f"로드 완료: {shp_path} ({len(gdf)}개 지역)")
            
        except Exception as e:
            print(f"로드 실패: {shp_path} - {e}")
            continue
    
    if all_gdfs:
        # 모든 지역 데이터 통합
        print("전국 지도 데이터 통합 중...")
        national_gdf = pd.concat(all_gdfs, ignore_index=True)
        print(f"전국 지도 데이터 통합 완료: {len(national_gdf)}개 지역")
        return national_gdf
    else:
        # 실패 시 기본 전라남도 지도 사용
        print("전국 지도 로드 실패, 기본 지도 사용")
        return gpd.read_file("data/shapefiles/zeonam/LARD_ADM_SECT_SGG_46_202505.shp").to_crs(epsg=4326)

def create_integrated_water_quality_map(output_file='integrated_water_quality_map.png'):
    """수질 측정소가 마킹된 전국 통합 지도 생성 (공간 조인 방식)"""
    
    print("🌊 수질 측정소 통합 지도 생성 시작 (공간 조인 방식)")
    print("=" * 50)
    
    start_time = time.time()
    
    # 1. SHP 파일 로드 (전국 지도)
    print("1️⃣ SHP 파일 로드 중...")
    national_gdf = load_national_map()
    print(f"SHP 로드 완료: {time.time() - start_time:.2f}초")
    
    # 2. README 구조에 맞는 수질 데이터 준비
    print("2️⃣ README 구조에 맞는 수질 데이터 준비 중...")
    water_quality_df = load_real_water_quality_data()
    print(f"수질 데이터 로드 완료: {time.time() - start_time:.2f}초")
    
    # 3. 측정소 데이터를 GeoDataFrame으로 변환
    print("3️⃣ 측정소 데이터를 GeoDataFrame으로 변환 중...")
    from shapely.geometry import Point
    
    # 유효한 좌표만 필터링
    valid_data = water_quality_df[
        (water_quality_df['위도'].notna()) & 
        (water_quality_df['경도'].notna()) &
        (water_quality_df['위도'] != 0) & 
        (water_quality_df['경도'] != 0)
    ].copy()
    
    # Point 지오메트리 생성
    valid_data['geometry'] = valid_data.apply(
        lambda row: Point(row['경도'], row['위도']), axis=1
    )
    
    # GeoDataFrame 생성
    points_gdf = gpd.GeoDataFrame(
        valid_data, 
        geometry='geometry',
        crs='EPSG:4326'
    )
    
    print(f"유효한 측정소 수: {len(points_gdf)}개")
    print(f"공간 조인 완료: {time.time() - start_time:.2f}초")
    
    # 4. 공간 조인으로 각 행정구역에 속하는 측정소 찾기
    print("4️⃣ 공간 조인으로 행정구역별 측정소 매칭 중...")
    
    # 공간 조인 수행
    joined_gdf = gpd.sjoin(
        points_gdf, 
        national_gdf, 
        how='left', 
        predicate='within'
    )
    
    print(f"공간 조인 완료: {len(joined_gdf)}개 매칭")
    print(f"공간 조인 완료: {time.time() - start_time:.2f}초")
    
    # 5. 행정구역별 수질 데이터 집계
    print("5️⃣ 행정구역별 수질 데이터 집계 중...")
    
    # 매칭된 데이터만 사용
    matched_data = joined_gdf[joined_gdf['index_right'].notna()].copy()
    
    if len(matched_data) == 0:
        print("❌ 공간 조인으로 매칭된 데이터가 없습니다!")
        return None
    
    # 행정구역별 평균 계산
    region_stats = matched_data.groupby('SGG_NM').agg({
        '총인_TP_mgL': 'mean',
        '총질소_TN_mgL': 'mean',
        '위도': 'mean',
        '경도': 'mean'
    }).reset_index()
    
    # 가중치 점수 계산
    region_stats['가중치_점수'] = region_stats.apply(
        lambda row: calculate_weighted_score(row['총인_TP_mgL'], row['총질소_TN_mgL']), 
        axis=1
    )
    
    # 모든 가중치 점수로 백분위 계산
    all_scores = region_stats['가중치_점수'].values
    
    # 각 행정구역별 경보 단계 계산
    region_stats['경보_단계'] = region_stats['가중치_점수'].apply(
        lambda score: calculate_alert_level_by_percentile(score, all_scores)
    )
    
    print(f"행정구역별 평균 계산 완료: {len(region_stats)}개 행정구역")
    print("행정구역별 경보 단계 분포:")
    print(region_stats['경보_단계'].value_counts())
    print(f"집계 완료: {time.time() - start_time:.2f}초")
    
    # 6. 지도 생성
    print("6️⃣ 지도 생성 중...")
    fig, ax = plt.subplots(1, 1, figsize=(12, 14))
    
    # 기본 지도 그리기 (회색 배경)
    national_gdf.plot(
        color='lightgray',
        edgecolor='black',
        linewidth=0.5,
        ax=ax,
        alpha=0.3
    )
    print(f"기본 지도 그리기 완료: {time.time() - start_time:.2f}초")
    
    # 경보 단계별 색상 매핑
    alert_colors = {
        '정상': '#2E8B57',      # 초록
        '1단계': '#90EE90',     # 연초록
        '2단계': '#FFFF00',     # 노랑
        '3단계': '#FFA500',     # 주황
        '4단계': '#FF6347',     # 토마토
        '5단계': '#FF0000'      # 빨강
    }
    
    # 7. 행정구역별 지도 영역 색칠
    print("7️⃣ 행정구역별 지도 영역 색칠 중...")
    
    # 매칭 딕셔너리 생성
    region_dict = {}
    for _, row in region_stats.iterrows():
        region_name = row['SGG_NM']
        region_dict[region_name] = row
    
    print(f"데이터가 있는 행정구역 수: {len(region_dict)}")
    print("데이터가 있는 행정구역 목록:")
    for region_name in list(region_dict.keys())[:10]:  # 처음 10개만 출력
        print(f"  - {region_name}: {region_dict[region_name]['경보_단계']}")
    
    matched_count = 0
    unmatched_count = 0
    
    for idx, map_row in national_gdf.iterrows():
        try:
            sgg_name = map_row['SGG_NM']
            
            # 해당 행정구역에 데이터가 있는지 확인
            if sgg_name in region_dict:
                matched_count += 1
                # 경보 단계에 따른 색상
                alert_level = region_dict[sgg_name]['경보_단계']
                color = alert_colors.get(alert_level, '#808080')  # 기본값: 회색
                
                # 행정구역 영역 색칠
                try:
                    temp_gdf = gpd.GeoDataFrame([map_row], geometry='geometry', crs=national_gdf.crs)
                    temp_gdf.plot(
                        ax=ax,
                        color=color,
                        alpha=0.8,
                        edgecolor='black',
                        linewidth=0.5,
                        zorder=3
                    )
                except Exception as e:
                    print(f"지오메트리 플롯 오류 (무시): {e}")
                    continue
                
                # 행정구역명 표시 (모든 이름 표시)
                try:
                    centroid = map_row['geometry'].centroid
                    
                    # SHP 파일의 SGG_NM 컬럼에서 시도명 제거
                    display_name = sgg_name
                    if '전라남도 ' in display_name:
                        display_name = display_name.replace('전라남도 ', '')
                    elif '전라북도 ' in display_name:
                        display_name = display_name.replace('전라북도 ', '')
                    elif '경상남도 ' in display_name:
                        display_name = display_name.replace('경상남도 ', '')
                    elif '경상북도 ' in display_name:
                        display_name = display_name.replace('경상북도 ', '')
                    elif '충청남도 ' in display_name:
                        display_name = display_name.replace('충청남도 ', '')
                    elif '충청북도 ' in display_name:
                        display_name = display_name.replace('충청북도 ', '')
                    elif '강원도 ' in display_name:
                        display_name = display_name.replace('강원도 ', '')
                    elif '강원특별자치도 ' in display_name:
                        display_name = display_name.replace('강원특별자치도 ', '')
                    elif '경기도 ' in display_name:
                        display_name = display_name.replace('경기도 ', '')
                    elif '서울특별시 ' in display_name:
                        display_name = display_name.replace('서울특별시 ', '')
                    elif '부산광역시 ' in display_name:
                        display_name = display_name.replace('부산광역시 ', '')
                    elif '대구광역시 ' in display_name:
                        display_name = display_name.replace('대구광역시 ', '')
                    elif '인천광역시 ' in display_name:
                        display_name = display_name.replace('인천광역시 ', '')
                    elif '광주광역시 ' in display_name:
                        display_name = display_name.replace('광주광역시 ', '')
                    elif '대전광역시 ' in display_name:
                        display_name = display_name.replace('대전광역시 ', '')
                    elif '울산광역시 ' in display_name:
                        display_name = display_name.replace('울산광역시 ', '')
                    elif '세종특별자치시 ' in display_name:
                        display_name = display_name.replace('세종특별자치시 ', '')
                    elif '제주특별자치도 ' in display_name:
                        display_name = display_name.replace('제주특별자치도 ', '')
                    elif '전북특별자치도 ' in display_name:
                        display_name = display_name.replace('전북특별자치도 ', '')
                    elif '전북특별차지도 ' in display_name:
                        display_name = display_name.replace('전북특별차지도 ', '')
                    
                    # 주요 도시는 더 크게 표시
                    major_cities = ['서울', '부산', '대구', '인천', '광주', '대전', '울산', '제주']
                    is_major_city = any(city in display_name for city in major_cities)
                    
                    # 서울시 내부 구는 작게 표시
                    seoul_districts = ['강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', 
                                     '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', 
                                     '성동구', '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', 
                                     '종로구', '중구', '중랑구']
                    is_seoul_district = any(district in display_name for district in seoul_districts)
                    
                    # 띄어쓰기된 이름 처리 (예: 용인시 기흥구 → 기흥구)
                    if ' ' in display_name:
                        display_name = display_name.split(' ')[-1]  # 마지막 부분만 사용
                    
                    # 시군구 크기에 따른 폰트 크기 조정
                    if is_major_city:
                        font_size = 5   # 주요 도시 (7 → 5)
                    elif is_seoul_district:
                        font_size = 2   # 서울시 내부 구 (3 → 2)
                    else:
                        # 시군구 크기에 따라 폰트 크기 조정
                        if len(display_name) <= 3:  # 작은 시군구 (예: 강남구)
                            font_size = 3
                        elif len(display_name) <= 5:  # 중간 시군구 (예: 수원시)
                            font_size = 4
                        else:  # 큰 시군구 (예: 고성군)
                            font_size = 5
                    
                    ax.annotate(
                        display_name,
                        xy=(centroid.x, centroid.y),
                        xytext=(0, 0),
                        textcoords='offset points',
                        ha='center',
                        va='center',
                        fontsize=font_size,
                        fontweight='bold',
                        color='black',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.9, edgecolor='black', linewidth=0.5)
                    )
                except Exception as e:
                    print(f"행정구역명 표시 오류 (무시): {e}")
                    continue
            else:
                unmatched_count += 1
                # 데이터가 없는 행정구역은 회색으로 표시
                try:
                    temp_gdf = gpd.GeoDataFrame([map_row], geometry='geometry', crs=national_gdf.crs)
                    temp_gdf.plot(
                        ax=ax,
                        color='lightgray',
                        alpha=0.5,
                        edgecolor='black',
                        linewidth=0.3,
                        zorder=2
                    )
                except Exception as e:
                    print(f"매칭되지 않은 행정구역 플롯 오류 (무시): {e}")
                    continue
                
        except Exception as e:
            print(f"행정구역 색칠 중 오류: {e}")
            continue
    
    print(f"데이터가 있는 행정구역 수: {matched_count}")
    print(f"데이터가 없는 행정구역 수: {unmatched_count}")
    print(f"행정구역 색칠 완료: {time.time() - start_time:.2f}초")
    
    # 8. 범례 추가
    print("8️⃣ 범례 추가 중...")
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=8, label=level)
        for level, color in alert_colors.items()
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', fontsize=8, title='경보 단계', title_fontsize=10)
    
    # 9. 제목 및 설정
    ax.set_title('질소·인 유출 위험 지역 지도\n(공간 조인 기반 가중치 평가)', fontsize=14, fontweight='bold', pad=20)
    ax.set_xlabel('경도', fontsize=6)
    ax.set_ylabel('위도', fontsize=6)
    
    # 축 범위 설정 (전국에 맞게)
    ax.set_xlim(124.0, 132.0)
    ax.set_ylim(33.0, 39.0)
    
    # 10. 지도 저장
    print("9️⃣ 지도 저장 중...")
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✅ 지도 저장 완료: {output_file}")
    print(f"총 실행 시간: {time.time() - start_time:.2f}초")
    
    # 11. 요약 정보 출력
    print("\n📊 행정구역별 수질 평가 요약:")
    alert_summary = region_stats['경보_단계'].value_counts()
    print(alert_summary)
    
    print("\n📊 가중치 점수 통계:")
    print(f"평균 가중치 점수: {region_stats['가중치_점수'].mean():.4f}")
    print(f"최소 가중치 점수: {region_stats['가중치_점수'].min():.4f}")
    print(f"최대 가중치 점수: {region_stats['가중치_점수'].max():.4f}")
    
    print(f"\n📊 공간 조인 결과:")
    print(f"전체 측정소 수: {len(water_quality_df)}")
    print(f"유효한 좌표 측정소 수: {len(points_gdf)}")
    print(f"행정구역에 매칭된 측정소 수: {len(matched_data)}")
    print(f"데이터가 있는 행정구역 수: {len(region_stats)}")
    
    return region_stats

def main():
    """메인 실행 함수"""
    
    try:
        # 통합 지도 생성 (README 구조 적용)
        water_quality_data = create_integrated_water_quality_map()
        
        print("\n🎉 수질 측정소 통합 지도 생성 완료! (공간 조인 방식)")
        print("📁 생성된 파일: integrated_water_quality_map.png")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 