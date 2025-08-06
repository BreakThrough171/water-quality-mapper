#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 설정 파일
실제 사용 시 API 키를 입력하세요.
"""

# API 설정
API_CONFIG = {
    # 발급받은 API 키를 여기에 입력하세요
    'SERVICE_KEY': 'pC3qRcSJ2t4Z0PbPxhZCCgpbpzacTnX8OaQNpVwaJuQ5v9QJprbXaOgGTilPra7JnZ9AyjnLxGN6VPhobYKJHw==',
    
    # API 기본 URL
    'BASE_URL': 'http://apis.data.go.kr/1480523/WaterQualityService',
    
    # API 엔드포인트
    'ENDPOINTS': {
        'LIST_POINT': '/listPoint',  # 측정소 목록 조회
        'GET_LIST': '/getList',       # 수질 데이터 조회
        'GET_RADIO_ACTIVE': '/getRadioActiveMaterList'  # 방사성 물질 데이터 조회
    },
    
    # 수질 측정 항목 코드
    'PARAMETERS': {
        'M01': '통신상태',
        'M05': 'DO (용존산소)',
        'M27': 'TN (총질소)',
        'M28': 'TP (총인)',
        'pH': '수소이온농도',
        'COD': '화학적산소요구량',
        'BOD': '생화학적산소요구량'
    },
    
    # 지역 코드
    'REGIONS': {
        '46': '전남',
        '47': '전북',
        '48': '경남',
        '49': '경북'
    },
    
    # 파일 경로
    'PATHS': {
        'SHAPEFILE': 'data/shapefiles/zeonam/LARD_ADM_SECT_SGG_46_202505.shp',
        'STATIONS_CSV': '물환경 수질측정망 운영결과 DB_물환경_코드_코드명.csv',
        'WATER_QUALITY_CSV': '물환경 수질자동측정망(실시간) 운영결과 DB_물 환경_코드_코드명.csv'
    }
}

# 수질 기준값 (예시)
WATER_QUALITY_STANDARDS = {
    'DO': {
        'excellent': 8.0,    # 우수
        'good': 6.0,         # 양호
        'fair': 4.0,         # 보통
        'poor': 2.0          # 나쁨
    },
    'pH': {
        'min': 6.5,
        'max': 8.5
    },
    'COD': {
        'excellent': 2.0,
        'good': 4.0,
        'fair': 6.0,
        'poor': 8.0
    }
}

# 색상 매핑
COLOR_MAPPING = {
    'excellent': 'green',
    'good': 'blue',
    'fair': 'yellow',
    'poor': 'orange',
    'very_poor': 'red'
}

def get_api_key():
    """API 키 반환"""
    return API_CONFIG['SERVICE_KEY']

def get_base_url():
    """기본 URL 반환"""
    return API_CONFIG['BASE_URL']

def get_endpoint(name):
    """엔드포인트 URL 반환"""
    return API_CONFIG['BASE_URL'] + API_CONFIG['ENDPOINTS'][name]

def get_parameter_name(code):
    """측정 항목 코드에 대한 이름 반환"""
    return API_CONFIG['PARAMETERS'].get(code, code)

def get_region_name(code):
    """지역 코드에 대한 이름 반환"""
    return API_CONFIG['REGIONS'].get(code, code)

def get_file_path(name):
    """파일 경로 반환"""
    return API_CONFIG['PATHS'][name]

def get_water_quality_color(value, parameter):
    """수질 값에 따른 색상 반환"""
    if parameter == 'DO':
        if value >= WATER_QUALITY_STANDARDS['DO']['excellent']:
            return COLOR_MAPPING['excellent']
        elif value >= WATER_QUALITY_STANDARDS['DO']['good']:
            return COLOR_MAPPING['good']
        elif value >= WATER_QUALITY_STANDARDS['DO']['fair']:
            return COLOR_MAPPING['fair']
        elif value >= WATER_QUALITY_STANDARDS['DO']['poor']:
            return COLOR_MAPPING['poor']
        else:
            return COLOR_MAPPING['very_poor']
    else:
        return COLOR_MAPPING['good']  # 기본값 