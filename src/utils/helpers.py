#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
공통 헬퍼 함수들
데이터 처리, 유효성 검사, 변환 등의 유틸리티 함수
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import re

def validate_water_quality_data(data: pd.DataFrame) -> bool:
    """
    수질 데이터 유효성 검사
    
    Args:
        data: 검사할 데이터프레임
        
    Returns:
        bool: 유효성 여부
    """
    if data.empty:
        return False
    
    required_columns = ['ptNo', 'ptNm', 'itemTp', 'itemTn']
    missing_columns = [col for col in required_columns if col not in data.columns]
    
    if missing_columns:
        return False
    
    # 수치형 데이터 검사
    numeric_columns = ['itemTp', 'itemTn']
    for col in numeric_columns:
        if col in data.columns:
            # 음수 값이나 비정상적으로 큰 값 제거
            data[col] = pd.to_numeric(data[col], errors='coerce')
            data = data[data[col] >= 0]
            data = data[data[col] <= 1000]  # 임계값 설정
    
    return not data.empty

def calculate_weighted_score(tp_value: float, tn_value: float, 
                           tp_weight: float = 0.99, tn_weight: float = 0.01) -> float:
    """
    가중 평균 점수 계산
    
    Args:
        tp_value: 총인 값
        tn_value: 총질소 값
        tp_weight: 총인 가중치
        tn_weight: 총질소 가중치
        
    Returns:
        float: 가중 평균 점수
    """
    if pd.isna(tp_value) or pd.isna(tn_value):
        return np.nan
    
    return (tp_value * tp_weight) + (tn_value * tn_weight)

def categorize_risk_level(score: float) -> str:
    """
    위험도 레벨 분류
    
    Args:
        score: 가중 평균 점수
        
    Returns:
        str: 위험도 레벨
    """
    if pd.isna(score):
        return 'unknown'
    
    if score <= 0.5:
        return 'low'
    elif score <= 1.0:
        return 'medium'
    elif score <= 2.0:
        return 'high'
    else:
        return 'very_high'

def get_color_by_risk_level(risk_level: str) -> str:
    """
    위험도 레벨에 따른 색상 반환
    
    Args:
        risk_level: 위험도 레벨
        
    Returns:
        str: 색상 코드
    """
    color_mapping = {
        'low': '#2E8B57',      # 초록색
        'medium': '#90EE90',    # 연초록색
        'high': '#FFFF00',      # 노란색
        'very_high': '#FF0000', # 빨간색
        'unknown': '#808080'    # 회색
    }
    return color_mapping.get(risk_level, '#808080')

def extract_region_from_address(address: str) -> str:
    """
    주소에서 지역명 추출
    
    Args:
        address: 주소 문자열
        
    Returns:
        str: 지역명
    """
    if pd.isna(address):
        return 'Unknown'
    
    # 시군구 패턴 매칭
    patterns = [
        r'([가-힣]+시\s*[가-힣]+구)',
        r'([가-힣]+시\s*[가-힣]+군)',
        r'([가-힣]+도\s*[가-힣]+시)',
        r'([가-힣]+도\s*[가-힣]+군)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, address)
        if match:
            return match.group(1)
    
    return 'Unknown'

def format_datetime(dt: datetime) -> str:
    """
    날짜시간 포맷팅
    
    Args:
        dt: datetime 객체
        
    Returns:
        str: 포맷된 문자열
    """
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def calculate_statistics(data: pd.DataFrame, column: str) -> Dict[str, float]:
    """
    통계 계산
    
    Args:
        data: 데이터프레임
        column: 계산할 컬럼명
        
    Returns:
        Dict[str, float]: 통계 정보
    """
    if column not in data.columns:
        return {}
    
    numeric_data = pd.to_numeric(data[column], errors='coerce').dropna()
    
    if numeric_data.empty:
        return {}
    
    return {
        'mean': float(numeric_data.mean()),
        'median': float(numeric_data.median()),
        'std': float(numeric_data.std()),
        'min': float(numeric_data.min()),
        'max': float(numeric_data.max()),
        'count': int(len(numeric_data))
    }

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    안전한 나눗셈
    
    Args:
        numerator: 분자
        denominator: 분모
        default: 기본값
        
    Returns:
        float: 나눗셈 결과
    """
    if denominator == 0 or pd.isna(denominator):
        return default
    return numerator / denominator

def clean_station_name(name: str) -> str:
    """
    측정소명 정리
    
    Args:
        name: 측정소명
        
    Returns:
        str: 정리된 측정소명
    """
    if pd.isna(name):
        return 'Unknown'
    
    # 불필요한 문자 제거
    cleaned = re.sub(r'[^\w\s가-힣]', '', str(name))
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned if cleaned else 'Unknown' 