#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
데이터 전처리 모듈
API에서 수집한 원본 데이터를 정리하고 전처리합니다.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import os

from ..utils.config import config
from ..utils.logger import logger
from ..utils.helpers import validate_water_quality_data, clean_station_name, extract_region_from_address

class DataPreprocessor:
    """데이터 전처리 클래스"""
    
    def __init__(self):
        self.raw_data_dir = config.get_file_path('RAW_DATA_DIR')
        self.processed_data_dir = config.get_file_path('PROCESSED_DATA_DIR')
        
        # 디렉토리 생성
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.processed_data_dir, exist_ok=True)
    
    def preprocess_water_quality_data(self, raw_data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        수질 데이터 전처리
        
        Args:
            raw_data: 원본 수질 데이터
            
        Returns:
            Optional[pd.DataFrame]: 전처리된 데이터
        """
        try:
            if raw_data is None or raw_data.empty:
                logger.warning("전처리할 데이터가 없습니다.")
                return None
            
            logger.info(f"데이터 전처리 시작: {len(raw_data)}개 레코드")
            
            # 1. 기본 컬럼 정리
            df = self._clean_columns(raw_data)
            
            # 2. 데이터 타입 변환
            df = self._convert_data_types(df)
            
            # 3. 결측값 처리
            df = self._handle_missing_values(df)
            
            # 4. 이상값 제거
            df = self._remove_outliers(df)
            
            # 5. 지역 정보 추가
            df = self._add_region_info(df)
            
            # 6. 측정소명 정리
            df = self._clean_station_names(df)
            
            # 7. 유효성 검사
            if not validate_water_quality_data(df):
                logger.error("전처리된 데이터가 유효하지 않습니다.")
                return None
            
            logger.info(f"전처리 완료: {len(df)}개 레코드")
            
            return df
            
        except Exception as e:
            logger.error(f"데이터 전처리 중 오류 발생: {str(e)}")
            return None
    
    def _clean_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """컬럼명 정리"""
        # 컬럼명을 소문자로 변환
        df.columns = df.columns.str.lower()
        
        # 필요한 컬럼만 선택
        required_columns = ['ptno', 'ptnm', 'addr', 'itemtp', 'itemtn', 'wmyr', 'wmod', 'wmcymd']
        available_columns = [col for col in required_columns if col in df.columns]
        
        if not available_columns:
            logger.error("필수 컬럼이 없습니다.")
            return pd.DataFrame()
        
        df = df[available_columns]
        
        # 컬럼명 표준화
        column_mapping = {
            'ptno': 'station_code',
            'ptnm': 'station_name',
            'addr': 'address',
            'itemtp': 'tp',
            'itemtn': 'tn',
            'wmyr': 'year',
            'wmod': 'month',
            'wmcymd': 'measurement_date'
        }
        
        df = df.rename(columns=column_mapping)
        
        return df
    
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """데이터 타입 변환"""
        # 수치형 데이터 변환
        numeric_columns = ['tp', 'tn']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 날짜 데이터 변환
        if 'measurement_date' in df.columns:
            df['measurement_date'] = pd.to_datetime(df['measurement_date'], errors='coerce')
        
        # 연도, 월 데이터 변환
        if 'year' in df.columns:
            df['year'] = pd.to_numeric(df['year'], errors='coerce')
        if 'month' in df.columns:
            df['month'] = pd.to_numeric(df['month'], errors='coerce')
        
        return df
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """결측값 처리"""
        # 수치형 데이터의 결측값을 0으로 처리 (측정되지 않음)
        numeric_columns = ['tp', 'tn']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].fillna(0)
        
        # 측정소명이 없는 경우 제거
        if 'station_name' in df.columns:
            df = df.dropna(subset=['station_name'])
        
        return df
    
    def _remove_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """이상값 제거"""
        # 음수 값 제거
        numeric_columns = ['tp', 'tn']
        for col in numeric_columns:
            if col in df.columns:
                df = df[df[col] >= 0]
        
        # 비정상적으로 큰 값 제거 (임계값: 1000)
        for col in numeric_columns:
            if col in df.columns:
                df = df[df[col] <= 1000]
        
        return df
    
    def _add_region_info(self, df: pd.DataFrame) -> pd.DataFrame:
        """지역 정보 추가"""
        if 'address' in df.columns:
            df['region'] = df['address'].apply(extract_region_from_address)
        else:
            df['region'] = 'Unknown'
        
        return df
    
    def _clean_station_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """측정소명 정리"""
        if 'station_name' in df.columns:
            df['station_name'] = df['station_name'].apply(clean_station_name)
        
        return df
    
    def save_raw_data(self, data: pd.DataFrame, filename: str = None) -> str:
        """
        원본 데이터 저장
        
        Args:
            data: 저장할 데이터
            filename: 파일명 (None이면 자동 생성)
            
        Returns:
            str: 저장된 파일 경로
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"raw_water_quality_{timestamp}.csv"
        
        filepath = os.path.join(self.raw_data_dir, filename)
        
        try:
            data.to_csv(filepath, index=False, encoding='utf-8-sig')
            logger.info(f"원본 데이터 저장: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"원본 데이터 저장 실패: {str(e)}")
            return ""
    
    def save_processed_data(self, data: pd.DataFrame, filename: str = None) -> str:
        """
        전처리된 데이터 저장
        
        Args:
            data: 저장할 데이터
            filename: 파일명 (None이면 자동 생성)
            
        Returns:
            str: 저장된 파일 경로
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"processed_water_quality_{timestamp}.csv"
        
        filepath = os.path.join(self.processed_data_dir, filename)
        
        try:
            data.to_csv(filepath, index=False, encoding='utf-8-sig')
            logger.info(f"전처리된 데이터 저장: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"전처리된 데이터 저장 실패: {str(e)}")
            return ""
    
    def load_latest_processed_data(self) -> Optional[pd.DataFrame]:
        """
        최신 전처리된 데이터 로드
        
        Returns:
            Optional[pd.DataFrame]: 최신 전처리된 데이터
        """
        try:
            if not os.path.exists(self.processed_data_dir):
                return None
            
            # 가장 최근 파일 찾기
            files = [f for f in os.listdir(self.processed_data_dir) if f.startswith('processed_')]
            if not files:
                return None
            
            latest_file = max(files, key=lambda x: os.path.getctime(os.path.join(self.processed_data_dir, x)))
            filepath = os.path.join(self.processed_data_dir, latest_file)
            
            df = pd.read_csv(filepath, encoding='utf-8-sig')
            logger.info(f"최신 전처리된 데이터 로드: {filepath}")
            
            return df
            
        except Exception as e:
            logger.error(f"전처리된 데이터 로드 실패: {str(e)}")
            return None 