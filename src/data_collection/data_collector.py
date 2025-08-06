#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
수질 데이터 수집기
새로운 구조: API → CSV 업데이트 → 기존 CSV 사용
"""

import pandas as pd
import os
import shutil
from datetime import datetime, timedelta
from typing import Optional, Tuple
import logging

from .api_client import WaterQualityAPIClient
from ..utils.config import config
from ..utils.logger import logger

class WaterQualityCollector:
    """수질 데이터 수집기 (새로운 구조)"""
    
    def __init__(self):
        self.api_client = WaterQualityAPIClient()
        self.data_dir = config.paths['DATA_DIR']
        self.raw_dir = config.paths['RAW_DATA_DIR']
        self.backup_dir = os.path.join(self.data_dir, 'backup')
        
        # Local_Water_CSV 디렉토리 경로 (설정 파일에서 가져오기)
        self.local_csv_dir = config.paths['LOCAL_CSV_DIR']
        
        # 디렉토리 생성
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def collect_data(self) -> Optional[pd.DataFrame]:
        """
        새로운 데이터 수집 흐름 실행
        README에 명시된 우선순위: API → CSV 업데이트 → 기존 CSV
        
        Returns:
            Optional[pd.DataFrame]: 수집된 수질 데이터
        """
        logger.info("=" * 60)
        logger.info("수질 데이터 수집 시작 (새로운 구조)")
        logger.info("우선순위: API → CSV 업데이트 → 기존 CSV")
        logger.info("=" * 60)
        
        # 1단계: API 서버에서 데이터 수집 시도
        logger.info("\n1단계: API 서버에서 데이터 수집 시도")
        api_data = self._try_api_collection()
        
        if api_data is not None and not api_data.empty:
            logger.info("✅ API 데이터 수집 성공")
            
            # 2단계: 로컬 CSV 파일 업데이트
            logger.info("\n2단계: 로컬 CSV 파일 업데이트")
            success = self._update_csv_files(api_data)
            
            if success:
                logger.info("✅ CSV 파일 업데이트 완료")
                return api_data
            else:
                logger.warning("⚠️ CSV 업데이트 실패, API 데이터 사용")
                return api_data
        else:
            logger.warning("⚠️ API 데이터 수집 실패")
            
            # 3단계: 기존 CSV 파일 사용 (Local_Water_CSV 포함)
            logger.info("\n3단계: 기존 CSV 파일 사용")
            csv_data = self._load_existing_csv()
            
            if csv_data is not None and not csv_data.empty:
                logger.info("✅ 기존 CSV 파일 로드 성공")
                return csv_data
            else:
                logger.error("❌ 사용 가능한 데이터가 없습니다.")
                return None
    
    def _try_api_collection(self) -> Optional[pd.DataFrame]:
        """
        API 서버에서 데이터 수집 시도
        
        Returns:
            Optional[pd.DataFrame]: API에서 수집된 데이터
        """
        try:
            # API 연결 테스트
            logger.info("API 연결 테스트 중...")
            if not self.api_client.test_api_connection():
                logger.error("API 연결 실패")
                return None
            
            # 최근 30일간 데이터 수집
            logger.info("최근 30일간 수질 데이터 수집 중...")
            data = self.api_client.get_all_water_quality_data(days_back=30)
            
            if data is not None and not data.empty:
                # 데이터 검증
                if self._validate_api_data(data):
                    logger.info(f"✅ API 데이터 수집 완료: {len(data)}개 레코드")
                    return data
                else:
                    logger.error("❌ API 데이터 검증 실패")
                    return None
            else:
                logger.warning("⚠️ API에서 데이터를 가져올 수 없습니다.")
                return None
                
        except Exception as e:
            logger.error(f"API 데이터 수집 중 오류 발생: {str(e)}")
            return None
    
    def _validate_api_data(self, data: pd.DataFrame) -> bool:
        """
        API 데이터 검증
        
        Args:
            data: 검증할 데이터
            
        Returns:
            bool: 검증 결과
        """
        try:
            # 필수 컬럼 확인
            required_columns = ['ptNo', 'ptNm', 'itemTp', 'itemTn']
            missing_columns = [col for col in required_columns if col not in data.columns]
            
            if missing_columns:
                logger.error(f"필수 컬럼 누락: {missing_columns}")
                return False
            
            # 데이터 타입 확인
            if not data['itemTp'].apply(lambda x: isinstance(x, (int, float)) or pd.isna(x)).all():
                logger.error("TP 데이터 타입 오류")
                return False
            
            if not data['itemTn'].apply(lambda x: isinstance(x, (int, float)) or pd.isna(x)).all():
                logger.error("TN 데이터 타입 오류")
                return False
            
            # 데이터 범위 확인
            tp_data = pd.to_numeric(data['itemTp'], errors='coerce')
            tn_data = pd.to_numeric(data['itemTn'], errors='coerce')
            
            if (tp_data < 0).any() or (tn_data < 0).any():
                logger.warning("음수 값이 포함되어 있습니다.")
            
            logger.info("✅ API 데이터 검증 완료")
            return True
            
        except Exception as e:
            logger.error(f"데이터 검증 중 오류: {str(e)}")
            return False
    
    def _update_csv_files(self, api_data: pd.DataFrame) -> bool:
        """
        API 데이터로 CSV 파일 업데이트
        
        Args:
            api_data: API에서 수집된 데이터
            
        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            # 기존 파일 백업
            self._backup_existing_files()
            
            # 수질 데이터 저장
            water_quality_path = os.path.join(self.raw_dir, 'water_quality_data.csv')
            api_data.to_csv(water_quality_path, index=False, encoding='utf-8')
            logger.info(f"✅ 수질 데이터 저장: {water_quality_path}")
            
            # 측정소 정보 추출 및 저장
            stations_data = api_data[['ptNo', 'ptNm', 'addr', 'latDgr', 'lonDgr']].drop_duplicates()
            stations_path = os.path.join(self.raw_dir, 'measurement_stations.csv')
            stations_data.to_csv(stations_path, index=False, encoding='utf-8')
            logger.info(f"✅ 측정소 정보 저장: {stations_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"CSV 파일 업데이트 중 오류: {str(e)}")
            return False
    
    def _backup_existing_files(self):
        """기존 CSV 파일 백업"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 수질 데이터 백업
            water_quality_path = os.path.join(self.raw_dir, 'water_quality_data.csv')
            if os.path.exists(water_quality_path):
                backup_path = os.path.join(self.backup_dir, f'water_quality_data_{timestamp}.csv')
                shutil.copy2(water_quality_path, backup_path)
                logger.info(f"✅ 수질 데이터 백업: {backup_path}")
            
            # 측정소 정보 백업
            stations_path = os.path.join(self.raw_dir, 'measurement_stations.csv')
            if os.path.exists(stations_path):
                backup_path = os.path.join(self.backup_dir, f'measurement_stations_{timestamp}.csv')
                shutil.copy2(stations_path, backup_path)
                logger.info(f"✅ 측정소 정보 백업: {backup_path}")
                
        except Exception as e:
            logger.error(f"백업 중 오류: {str(e)}")
    
    def _load_existing_csv(self) -> Optional[pd.DataFrame]:
        """
        기존 CSV 파일 로드 (README 구조에 맞게)
        
        Returns:
            Optional[pd.DataFrame]: 로드된 데이터
        """
        try:
            # 1. README 구조의 data/raw/ 파일들 확인
            water_quality_path = os.path.join(self.raw_dir, 'water_quality_data.csv')
            stations_path = os.path.join(self.raw_dir, 'measurement_stations.csv')
            
            if os.path.exists(water_quality_path):
                logger.info("README 구조의 수질 데이터 파일 발견")
                data = pd.read_csv(water_quality_path, encoding='utf-8')
                logger.info(f"✅ README 구조 데이터 로드: {len(data)}개 레코드")
                return data
            
            # 2. Local_Water_CSV 파일들 확인 (README에서 명시된 대로)
            logger.info("Local_Water_CSV 파일들 확인 중...")
            local_data = self._load_local_csv_files()
            
            if local_data is not None and not local_data.empty:
                logger.info(f"✅ Local_Water_CSV 데이터 로드: {len(local_data)}개 레코드")
                return local_data
            
            logger.warning("기존 CSV 파일이 없습니다.")
            return None
            
        except Exception as e:
            logger.error(f"기존 CSV 파일 로드 중 오류: {str(e)}")
            return None
    
    def _load_local_csv_files(self) -> Optional[pd.DataFrame]:
        """
        Local_Water_CSV 파일들 로드 (README에서 명시된 하천 + 농업용수 + 도시관류 데이터)
        
        Returns:
            Optional[pd.DataFrame]: 통합된 데이터
        """
        try:
            # 설정 파일에서 Local_Water_CSV 파일 경로 가져오기
            local_csv_files = config.get_local_csv_files()
            river_file = local_csv_files['river']
            agricultural_file = local_csv_files['agricultural']
            urban_file = local_csv_files['urban']
            industrial_file = local_csv_files['industrial']
            reservoir_file = local_csv_files['reservoir']
            
            combined_data = None
            
            # 하천 데이터 처리
            if os.path.exists(river_file):
                logger.info("하천 수질 데이터 로드 중...")
                river_data = pd.read_csv(river_file, encoding='cp949')
                logger.info(f"하천 데이터: {len(river_data)}개 측정소")
                
                # 컬럼명 정리
                river_data.columns = ['측정소코드', '측정소명', '년도', '월', '경도', '위도', 'TN_mgL', 'TP_mgL']
                combined_data = river_data
            
            # 농업용수 데이터 처리
            if os.path.exists(agricultural_file):
                logger.info("농업용수 수질 데이터 로드 중...")
                agricultural_data = pd.read_csv(agricultural_file, encoding='cp949')
                logger.info(f"농업용수 데이터: {len(agricultural_data)}개 측정소")
                
                # 컬럼명 정리
                agricultural_data.columns = ['측정소코드', '측정소명', '년도', '월', '경도', '위도', 'TN_mgL', 'TP_mgL']
                
                # 데이터 통합
                if combined_data is not None:
                    combined_data = pd.concat([combined_data, agricultural_data], ignore_index=True)
                else:
                    combined_data = agricultural_data
            
            # 도시관류 데이터 처리
            if os.path.exists(urban_file):
                logger.info("도시관류 수질 데이터 로드 중...")
                urban_data = pd.read_csv(urban_file, encoding='cp949')
                logger.info(f"도시관류 데이터: {len(urban_data)}개 측정소")
                
                # 도시관류 데이터 컬럼명 매핑 (실제 컬럼명에 맞게)
                urban_data = urban_data.rename(columns={
                    '분류번호': '측정소코드',
                    '측정소명': '측정소명',
                    '년': '년도',
                    '월': '월',
                    '경도': '경도',
                    '위도': '위도',
                    'TN(㎎/L)': 'TN_mgL',
                    'TP(㎎/L)': 'TP_mgL'
                })
                
                # 빈 값이 있는 행 제거 (도시관류 데이터에 빈 값이 있음)
                urban_data = urban_data.dropna(subset=['TN_mgL', 'TP_mgL'])
                logger.info(f"유효한 도시관류 데이터: {len(urban_data)}개 측정소")
                
                # 데이터 통합
                if combined_data is not None:
                    combined_data = pd.concat([combined_data, urban_data], ignore_index=True)
                else:
                    combined_data = urban_data
            
            # 산단하천 데이터 처리
            if os.path.exists(industrial_file):
                logger.info("산단하천 수질 데이터 로드 중...")
                industrial_data = pd.read_csv(industrial_file, encoding='cp949')
                logger.info(f"산단하천 데이터: {len(industrial_data)}개 측정소")
                
                # 산단하천 데이터 컬럼명 매핑 (실제 컬럼명에 맞게)
                industrial_data = industrial_data.rename(columns={
                    '분류번호': '측정소코드',
                    '측정소명': '측정소명',
                    '년': '년도',
                    '월': '월',
                    '경도': '경도',
                    '위도': '위도',
                    'TN(㎎/L)': 'TN_mgL',
                    'TP(㎎/L)': 'TP_mgL'
                })
                
                # 빈 값이 있는 행 제거 (산단하천 데이터에 빈 값이 있을 수 있음)
                industrial_data = industrial_data.dropna(subset=['TN_mgL', 'TP_mgL'])
                logger.info(f"유효한 산단하천 데이터: {len(industrial_data)}개 측정소")
                
                # 데이터 통합
                if combined_data is not None:
                    combined_data = pd.concat([combined_data, industrial_data], ignore_index=True)
                else:
                    combined_data = industrial_data
            
            # 호소 데이터 처리
            if os.path.exists(reservoir_file):
                logger.info("호소 수질 데이터 로드 중...")
                reservoir_data = pd.read_csv(reservoir_file, encoding='cp949')
                logger.info(f"호소 데이터: {len(reservoir_data)}개 측정소")
                
                # 호소 데이터 컬럼명 매핑 (실제 컬럼명에 맞게)
                reservoir_data = reservoir_data.rename(columns={
                    '분류번호': '측정소코드',
                    '측정소명': '측정소명',
                    '년': '년도',
                    '월': '월',
                    '경도': '경도',
                    '위도': '위도',
                    'TN(㎎/L)': 'TN_mgL',
                    'TP(㎎/L)': 'TP_mgL'
                })
                
                # 빈 값이 있는 행 제거 (호소 데이터에 빈 값이 있을 수 있음)
                reservoir_data = reservoir_data.dropna(subset=['TN_mgL', 'TP_mgL'])
                logger.info(f"유효한 호소 데이터: {len(reservoir_data)}개 측정소")
                
                # 데이터 통합
                if combined_data is not None:
                    combined_data = pd.concat([combined_data, reservoir_data], ignore_index=True)
                else:
                    combined_data = reservoir_data
            
            if combined_data is not None and not combined_data.empty:
                # 좌표 변환
                logger.info("좌표 변환 중...")
                combined_data['경도_변환'] = combined_data['경도'].apply(self._parse_coordinate)
                combined_data['위도_변환'] = combined_data['위도'].apply(self._parse_coordinate)
                
                # 유효한 좌표만 필터링
                valid_data = combined_data.dropna(subset=['경도_변환', '위도_변환'])
                logger.info(f"유효한 좌표 데이터: {len(valid_data)}개")
                
                # README 구조에 맞게 변환
                final_data = {
                    'ptNo': valid_data['측정소코드'].tolist(),
                    'ptNm': valid_data['측정소명'].tolist(),
                    'latDgr': valid_data['위도_변환'].tolist(),
                    'lonDgr': valid_data['경도_변환'].tolist(),
                    'itemTp': valid_data['TP_mgL'].tolist(),
                    'itemTn': valid_data['TN_mgL'].tolist()
                }
                
                return pd.DataFrame(final_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Local_Water_CSV 파일 로드 중 오류: {str(e)}")
            return None
    
    def _parse_coordinate(self, coord_str):
        """좌표 문자열을 도/분/초 형식에서 십진수로 변환"""
        try:
            coord_str = str(coord_str).strip()
            
            # 이미 십진수인 경우
            if coord_str.replace('.', '').replace('-', '').isdigit():
                return float(coord_str)
            
            # 도/분/초 형식 처리
            import re
            patterns = [
                r'(\d+)°(\d+)\'(\d+\.?\d*)\"',  # 128°40'35.4"
                r'(\d+)°(\d+)\'\.(\d+\.?\d*)\"',  # 128°20'.2"
                r'(\d+)°(\d+)\'(\d+)',          # 128°40'35
                r'(\d+)°(\d+)\'\.(\d+)',        # 128°20'.2
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
            
            logger.warning(f"좌표 변환 실패: {coord_str}")
            return None
            
        except Exception as e:
            logger.error(f"좌표 변환 오류: {coord_str} -> {e}")
            return None
    
    def get_latest_data(self) -> Optional[pd.DataFrame]:
        """최신 데이터 조회"""
        return self.collect_data()
    
    def get_water_quality_data(self, start_date: str, end_date: str) -> Optional[pd.DataFrame]:
        """
        특정 기간의 수질 데이터 조회
        
        Args:
            start_date: 시작 날짜 (YYYY-MM-DD)
            end_date: 종료 날짜 (YYYY-MM-DD)
            
        Returns:
            Optional[pd.DataFrame]: 해당 기간의 수질 데이터
        """
        try:
            data = self.collect_data()
            
            if data is None or data.empty:
                return None
            
            # 날짜 필터링 (날짜 컬럼이 있는 경우)
            if 'measurement_date' in data.columns:
                data['measurement_date'] = pd.to_datetime(data['measurement_date'])
                filtered_data = data[
                    (data['measurement_date'] >= start_date) & 
                    (data['measurement_date'] <= end_date)
                ]
                return filtered_data
            else:
                # 날짜 정보가 없는 경우 전체 데이터 반환
                logger.warning("날짜 정보가 없어 전체 데이터를 반환합니다.")
                return data
                
        except Exception as e:
            logger.error(f"기간별 데이터 조회 중 오류: {str(e)}")
            return None
    
    def get_statistics(self) -> dict:
        """
        데이터 통계 정보 반환
        
        Returns:
            dict: 통계 정보
        """
        try:
            data = self.collect_data()
            
            if data is None or data.empty:
                return {
                    'total_records': 0,
                    'total_stations': 0,
                    'data_sources': [],
                    'date_range': None
                }
            
            stats = {
                'total_records': len(data),
                'total_stations': data['ptNo'].nunique() if 'ptNo' in data.columns else 0,
                'data_sources': ['Local_Water_CSV'],  # 현재는 로컬 CSV만 사용
                'date_range': None
            }
            
            # TP, TN 통계
            if 'itemTp' in data.columns:
                tp_data = pd.to_numeric(data['itemTp'], errors='coerce')
                stats['tp_stats'] = {
                    'mean': tp_data.mean(),
                    'min': tp_data.min(),
                    'max': tp_data.max(),
                    'std': tp_data.std()
                }
            
            if 'itemTn' in data.columns:
                tn_data = pd.to_numeric(data['itemTn'], errors='coerce')
                stats['tn_stats'] = {
                    'mean': tn_data.mean(),
                    'min': tn_data.min(),
                    'max': tn_data.max(),
                    'std': tn_data.std()
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"통계 정보 생성 중 오류: {str(e)}")
            return {} 