#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
위험도 계산 모듈
수질 데이터를 기반으로 고위험군을 산정합니다.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from ..utils.config import config
from ..utils.logger import logger
from ..utils.helpers import calculate_weighted_score, categorize_risk_level, get_color_by_risk_level

class RiskCalculator:
    """위험도 계산 클래스"""
    
    def __init__(self):
        self.tp_weight = config.get_weight('TP')
        self.tn_weight = config.get_weight('TN')
        
    def calculate_risk_scores(self, data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        위험도 점수 계산
        
        Args:
            data: 수질 데이터
            
        Returns:
            Optional[pd.DataFrame]: 위험도 점수가 추가된 데이터
        """
        try:
            if data is None or data.empty:
                logger.warning("위험도 계산할 데이터가 없습니다.")
                return None
            
            logger.info(f"위험도 계산 시작: {len(data)}개 레코드")
            
            # 복사본 생성
            df = data.copy()
            
            # 가중 평균 점수 계산
            df['weighted_score'] = df.apply(
                lambda row: calculate_weighted_score(
                    row.get('tp', 0), 
                    row.get('tn', 0),
                    self.tp_weight,
                    self.tn_weight
                ), axis=1
            )
            
            # 위험도 레벨 분류
            df['risk_level'] = df['weighted_score'].apply(categorize_risk_level)
            
            # 색상 매핑
            df['color'] = df['risk_level'].apply(get_color_by_risk_level)
            
            # 통계 정보 추가
            df = self._add_statistics(df)
            
            logger.info(f"위험도 계산 완료: {len(df)}개 레코드")
            
            return df
            
        except Exception as e:
            logger.error(f"위험도 계산 중 오류 발생: {str(e)}")
            return None
    
    def calculate_regional_risk(self, data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        지역별 위험도 계산
        
        Args:
            data: 수질 데이터
            
        Returns:
            Optional[pd.DataFrame]: 지역별 위험도 데이터
        """
        try:
            if data is None or data.empty:
                logger.warning("지역별 위험도 계산할 데이터가 없습니다.")
                return None
            
            logger.info("지역별 위험도 계산 시작")
            
            # 지역별 그룹화
            if 'region' not in data.columns:
                logger.error("지역 정보가 없습니다.")
                return None
            
            regional_stats = data.groupby('region').agg({
                'tp': ['mean', 'std', 'count'],
                'tn': ['mean', 'std'],
                'weighted_score': ['mean', 'std', 'min', 'max']
            }).round(4)
            
            # 컬럼명 정리
            regional_stats.columns = [
                'tp_mean', 'tp_std', 'tp_count',
                'tn_mean', 'tn_std',
                'score_mean', 'score_std', 'score_min', 'score_max'
            ]
            
            # 지역별 위험도 레벨 계산
            regional_stats['risk_level'] = regional_stats['score_mean'].apply(categorize_risk_level)
            regional_stats['color'] = regional_stats['risk_level'].apply(get_color_by_risk_level)
            
            # 측정소 수 추가
            regional_stats['station_count'] = regional_stats['tp_count']
            
            logger.info(f"지역별 위험도 계산 완료: {len(regional_stats)}개 지역")
            
            return regional_stats.reset_index()
            
        except Exception as e:
            logger.error(f"지역별 위험도 계산 중 오류 발생: {str(e)}")
            return None
    
    def identify_high_risk_areas(self, data: pd.DataFrame, threshold: float = 1.0) -> Optional[pd.DataFrame]:
        """
        고위험 지역 식별
        
        Args:
            data: 수질 데이터
            threshold: 위험도 임계값
            
        Returns:
            Optional[pd.DataFrame]: 고위험 지역 데이터
        """
        try:
            if data is None or data.empty:
                logger.warning("고위험 지역 식별할 데이터가 없습니다.")
                return None
            
            logger.info(f"고위험 지역 식별 시작 (임계값: {threshold})")
            
            # 임계값 이상인 지역 필터링
            high_risk_data = data[data['weighted_score'] >= threshold].copy()
            
            if high_risk_data.empty:
                logger.info("고위험 지역이 없습니다.")
                return None
            
            # 지역별 집계
            high_risk_areas = high_risk_data.groupby('region').agg({
                'station_code': 'count',
                'weighted_score': ['mean', 'max'],
                'tp': 'mean',
                'tn': 'mean'
            }).round(4)
            
            # 컬럼명 정리
            high_risk_areas.columns = [
                'station_count', 'avg_score', 'max_score', 'avg_tp', 'avg_tn'
            ]
            
            # 위험도 레벨 추가
            high_risk_areas['risk_level'] = high_risk_areas['avg_score'].apply(categorize_risk_level)
            high_risk_areas['color'] = high_risk_areas['risk_level'].apply(get_color_by_risk_level)
            
            # 정렬 (평균 점수 기준 내림차순)
            high_risk_areas = high_risk_areas.sort_values('avg_score', ascending=False)
            
            logger.info(f"고위험 지역 식별 완료: {len(high_risk_areas)}개 지역")
            
            return high_risk_areas.reset_index()
            
        except Exception as e:
            logger.error(f"고위험 지역 식별 중 오류 발생: {str(e)}")
            return None
    
    def calculate_trend_analysis(self, data: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """
        트렌드 분석
        
        Args:
            data: 수질 데이터
            
        Returns:
            Optional[Dict[str, Any]]: 트렌드 분석 결과
        """
        try:
            if data is None or data.empty:
                logger.warning("트렌드 분석할 데이터가 없습니다.")
                return None
            
            logger.info("트렌드 분석 시작")
            
            # 날짜별 집계
            if 'measurement_date' in data.columns:
                data['date'] = pd.to_datetime(data['measurement_date']).dt.date
                daily_stats = data.groupby('date').agg({
                    'weighted_score': ['mean', 'std'],
                    'tp': 'mean',
                    'tn': 'mean'
                }).round(4)
                
                daily_stats.columns = ['avg_score', 'score_std', 'avg_tp', 'avg_tn']
                
                # 트렌드 계산 (선형 회귀)
                dates = pd.to_datetime(daily_stats.index)
                scores = daily_stats['avg_score'].values
                
                if len(scores) > 1:
                    # 날짜를 숫자로 변환
                    date_nums = (dates - dates.min()).dt.days
                    
                    # 선형 회귀
                    coeffs = np.polyfit(date_nums, scores, 1)
                    trend_slope = coeffs[0]
                    trend_direction = 'increasing' if trend_slope > 0 else 'decreasing'
                    
                    trend_analysis = {
                        'trend_slope': trend_slope,
                        'trend_direction': trend_direction,
                        'daily_stats': daily_stats,
                        'total_days': len(daily_stats),
                        'avg_score_overall': float(scores.mean()),
                        'max_score': float(scores.max()),
                        'min_score': float(scores.min())
                    }
                    
                    logger.info(f"트렌드 분석 완료: {trend_direction} 트렌드")
                    return trend_analysis
                else:
                    logger.warning("트렌드 분석을 위한 충분한 데이터가 없습니다.")
                    return None
            else:
                logger.warning("날짜 정보가 없어 트렌드 분석을 수행할 수 없습니다.")
                return None
                
        except Exception as e:
            logger.error(f"트렌드 분석 중 오류 발생: {str(e)}")
            return None
    
    def _add_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """통계 정보 추가"""
        # 전체 통계
        total_stats = {
            'total_stations': len(df),
            'avg_tp': float(df['tp'].mean()),
            'avg_tn': float(df['tn'].mean()),
            'avg_score': float(df['weighted_score'].mean()),
            'max_score': float(df['weighted_score'].max()),
            'min_score': float(df['weighted_score'].min())
        }
        
        # 위험도 레벨별 통계
        risk_stats = df['risk_level'].value_counts().to_dict()
        
        # 통계 정보를 데이터프레임에 추가
        df['total_stations'] = total_stats['total_stations']
        df['avg_tp'] = total_stats['avg_tp']
        df['avg_tn'] = total_stats['avg_tn']
        df['avg_score'] = total_stats['avg_score']
        
        return df
    
    def get_risk_summary(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        위험도 요약 정보
        
        Args:
            data: 수질 데이터
            
        Returns:
            Dict[str, Any]: 위험도 요약 정보
        """
        try:
            if data is None or data.empty:
                return {}
            
            summary = {
                'total_stations': len(data),
                'avg_tp': float(data['tp'].mean()),
                'avg_tn': float(data['tn'].mean()),
                'avg_score': float(data['weighted_score'].mean()),
                'max_score': float(data['weighted_score'].max()),
                'min_score': float(data['weighted_score'].min()),
                'risk_level_distribution': data['risk_level'].value_counts().to_dict(),
                'high_risk_count': len(data[data['risk_level'] == 'very_high']),
                'medium_risk_count': len(data[data['risk_level'] == 'high']),
                'low_risk_count': len(data[data['risk_level'].isin(['low', 'medium'])])
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"위험도 요약 생성 중 오류 발생: {str(e)}")
            return {} 