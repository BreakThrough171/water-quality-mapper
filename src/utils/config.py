#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
설정 관리 모듈
API 설정, 시스템 설정, 경로 설정 등을 관리합니다.
"""

import os
from typing import Dict, Any

class Config:
    """설정 관리 클래스"""
    
    def __init__(self):
        self.api_config = self._load_api_config()
        self.system_config = self._load_system_config()
        self.paths = self._load_paths()
    
    def _load_api_config(self) -> Dict[str, Any]:
        """API 설정 로드"""
        return {
            # 발급받은 API 키를 여기에 입력하세요
            'SERVICE_KEY': 'fHcQ3zRYg8x+tsTv5ip4R6FzOFHvm9AFtsZfq+br5vnk9T5y2twHxbKaVdWAcUntjaUo9whb6vbS4LpxMrUbFg==',
            
            # API 기본 URL
            'BASE_URL': 'http://apis.data.go.kr/1480523/WaterQualityService',
            
            # API 엔드포인트
            'ENDPOINTS': {
                'LIST_POINT': '/listPoint',  # 측정소 목록 조회
                'GET_WATER_MEASURING_LIST': '/getWaterMeasuringList',  # 수질 데이터 조회
                'GET_REAL_TIME_WATER_QUALITY_LIST': '/getRealTimeWaterQualityList',  # 실시간 수질 데이터 조회
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
            }
        }
    
    def _load_system_config(self) -> Dict[str, Any]:
        """시스템 설정 로드"""
        return {
            # 로깅 설정
            'LOG_LEVEL': 'INFO',
            'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            
            # 데이터 처리 설정
            'MAX_RECORDS': 10000,
            'BATCH_SIZE': 1000,
            
            # 가중치 설정
            'TP_WEIGHT': 0.99,  # 총인 가중치
            'TN_WEIGHT': 0.01,  # 총질소 가중치
            
            # 위험도 분류 기준
            'RISK_THRESHOLDS': {
                'LOW': 0.5,
                'MEDIUM': 1.0,
                'HIGH': 2.0
            },
            
            # 시각화 설정
            'MAP_DPI': 300,
            'CHART_DPI': 150,
            'FIGURE_SIZE': (12, 8)
        }
    
    def _load_paths(self) -> Dict[str, str]:
        """경로 설정 로드 (README 구조에 맞게)"""
        # 프로젝트 루트 디렉토리
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        return {
            'PROJECT_ROOT': project_root,
            'DATA_DIR': os.path.join(project_root, 'data'),
            'RAW_DATA_DIR': os.path.join(project_root, 'data', 'raw'),
            'PROCESSED_DATA_DIR': os.path.join(project_root, 'data', 'processed'),
            'OUTPUT_DIR': os.path.join(project_root, 'data', 'output'),
            'SHAPEFILES_DIR': os.path.join(project_root, 'data', 'shapefiles'),
            'WEB_DIR': os.path.join(project_root, 'web'),
            'LOGS_DIR': os.path.join(project_root, 'logs'),
            'TEMPLATES_DIR': os.path.join(project_root, 'web', 'templates'),
            'STATIC_DIR': os.path.join(project_root, 'web', 'static'),
            'IMAGES_DIR': os.path.join(project_root, 'web', 'static', 'images'),
            'CSS_DIR': os.path.join(project_root, 'web', 'static', 'css'),
            'JS_DIR': os.path.join(project_root, 'web', 'static', 'js'),
            # README에서 명시된 Local_Water_CSV 디렉토리 추가
            'LOCAL_CSV_DIR': os.path.join(project_root, 'Local_Water_CSV'),
            # 행정구역 SHP 파일 디렉토리
            'ADMIN_SHP_DIR': os.path.join(project_root, '행정구역SHP지도')
        }
    
    def get_api_key(self) -> str:
        """API 키 반환"""
        return self.api_config['SERVICE_KEY']
    
    def get_base_url(self) -> str:
        """API 기본 URL 반환"""
        return self.api_config['BASE_URL']
    
    def get_endpoint(self, endpoint_name: str) -> str:
        """API 엔드포인트 반환"""
        return self.api_config['ENDPOINTS'].get(endpoint_name, '')
    
    def get_parameter(self, param_name: str) -> str:
        """수질 측정 항목 코드 반환"""
        return self.api_config['PARAMETERS'].get(param_name, '')
    
    def get_region(self, region_code: str) -> str:
        """지역 코드 반환"""
        return self.api_config['REGIONS'].get(region_code, '')
    
    def get_system_config(self, key: str) -> Any:
        """시스템 설정 반환"""
        return self.system_config.get(key)
    
    def get_path(self, path_name: str) -> str:
        """경로 반환"""
        return self.paths.get(path_name, '')
    
    def get_csv_data_path(self) -> str:
        """수질 데이터 CSV 파일 경로 반환 (README 구조)"""
        return os.path.join(self.paths['RAW_DATA_DIR'], 'water_quality_data.csv')
    
    def get_stations_data_path(self) -> str:
        """측정소 정보 CSV 파일 경로 반환 (README 구조)"""
        return os.path.join(self.paths['RAW_DATA_DIR'], 'measurement_stations.csv')
    
    def get_file_path(self, file_type: str) -> str:
        """파일 타입별 경로 반환"""
        file_paths = {
            'water_quality': self.get_csv_data_path(),
            'stations': self.get_stations_data_path(),
            'output_map': os.path.join(self.paths['OUTPUT_DIR'], 'integrated_water_quality_map.png'),
            'output_chart': os.path.join(self.paths['OUTPUT_DIR'], 'risk_distribution_chart.png'),
            'web_index': os.path.join(self.paths['WEB_DIR'], 'index.html'),
            'web_map': os.path.join(self.paths['WEB_DIR'], 'map.html'),
            'web_dashboard': os.path.join(self.paths['WEB_DIR'], 'dashboard.html')
        }
        return file_paths.get(file_type, '')
    
    def get_weight(self, param: str) -> float:
        """가중치 반환"""
        if param.upper() == 'TP':
            return self.system_config['TP_WEIGHT']
        elif param.upper() == 'TN':
            return self.system_config['TN_WEIGHT']
        else:
            return 0.0
    
    def get_risk_threshold(self, level: str) -> float:
        """위험도 임계값 반환"""
        return self.system_config['RISK_THRESHOLDS'].get(level.upper(), 0.0)
    
    def get_local_csv_files(self) -> Dict[str, str]:
        """Local_Water_CSV 파일 경로들 반환 (README에서 명시된 대로)"""
        local_csv_dir = self.paths['LOCAL_CSV_DIR']
        return {
            'river': os.path.join(local_csv_dir, '자료 조회_하천_20250806.csv'),
            'agricultural': os.path.join(local_csv_dir, '자료 조회_농업용수_20250806.csv'),
            'urban': os.path.join(local_csv_dir, '도시관류.csv'),
            'industrial': os.path.join(local_csv_dir, '산단하천.csv'),
            'reservoir': os.path.join(local_csv_dir, '호소.csv')
        }

# 전역 설정 인스턴스
config = Config() 