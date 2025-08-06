#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
차트 생성 모듈
수질 데이터를 기반으로 다양한 차트를 생성합니다.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import os
from datetime import datetime

from ..utils.config import config
from ..utils.logger import logger

class ChartGenerator:
    """차트 생성 클래스"""
    
    def __init__(self):
        self.output_dir = config.get_file_path('OUTPUT_DIR')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 한글 폰트 설정
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
    
    def create_risk_distribution_chart(self, data: pd.DataFrame, save_path: str = None) -> str:
        """
        위험도 분포 차트 생성
        
        Args:
            data: 수질 데이터
            save_path: 저장 경로
            
        Returns:
            str: 저장된 파일 경로
        """
        try:
            if data is None or data.empty:
                logger.warning("위험도 분포 차트 생성할 데이터가 없습니다.")
                return ""
            
            logger.info("위험도 분포 차트 생성 시작")
            
            # 위험도 레벨별 개수 계산
            risk_counts = data['risk_level'].value_counts()
            
            # 색상 매핑
            colors = {
                'low': '#2E8B57',
                'medium': '#90EE90', 
                'high': '#FFFF00',
                'very_high': '#FF0000'
            }
            
            # 파이 차트 생성
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # 파이 차트
            wedges, texts, autotexts = ax1.pie(
                risk_counts.values,
                labels=risk_counts.index,
                autopct='%1.1f%%',
                colors=[colors.get(level, '#808080') for level in risk_counts.index],
                startangle=90
            )
            ax1.set_title('위험도 레벨 분포', fontsize=14, fontweight='bold')
            
            # 막대 차트
            bars = ax2.bar(risk_counts.index, risk_counts.values, 
                          color=[colors.get(level, '#808080') for level in risk_counts.index])
            ax2.set_title('위험도 레벨별 측정소 수', fontsize=14, fontweight='bold')
            ax2.set_ylabel('측정소 수')
            
            # 막대 위에 값 표시
            for bar, count in zip(bars, risk_counts.values):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                        str(count), ha='center', va='bottom')
            
            plt.tight_layout()
            
            # 저장
            if save_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = os.path.join(self.output_dir, f"risk_distribution_{timestamp}.png")
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"위험도 분포 차트 생성 완료: {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"위험도 분포 차트 생성 중 오류 발생: {str(e)}")
            return ""
    
    def create_regional_comparison_chart(self, regional_data: pd.DataFrame, save_path: str = None) -> str:
        """
        지역별 비교 차트 생성
        
        Args:
            regional_data: 지역별 데이터
            save_path: 저장 경로
            
        Returns:
            str: 저장된 파일 경로
        """
        try:
            if regional_data is None or regional_data.empty:
                logger.warning("지역별 비교 차트 생성할 데이터가 없습니다.")
                return ""
            
            logger.info("지역별 비교 차트 생성 시작")
            
            # 상위 10개 지역만 선택
            top_regions = regional_data.nlargest(10, 'score_mean')
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # 평균 점수 차트
            bars1 = ax1.barh(top_regions['region'], top_regions['score_mean'],
                            color=[get_color_by_risk_level(level) for level in top_regions['risk_level']])
            ax1.set_title('지역별 평균 위험도 점수 (상위 10개)', fontsize=14, fontweight='bold')
            ax1.set_xlabel('평균 점수')
            
            # 측정소 수 차트
            bars2 = ax2.barh(top_regions['region'], top_regions['station_count'],
                            color='skyblue', alpha=0.7)
            ax2.set_title('지역별 측정소 수 (상위 10개)', fontsize=14, fontweight='bold')
            ax2.set_xlabel('측정소 수')
            
            plt.tight_layout()
            
            # 저장
            if save_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = os.path.join(self.output_dir, f"regional_comparison_{timestamp}.png")
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"지역별 비교 차트 생성 완료: {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"지역별 비교 차트 생성 중 오류 발생: {str(e)}")
            return ""
    
    def create_trend_chart(self, trend_data: Dict[str, Any], save_path: str = None) -> str:
        """
        트렌드 차트 생성
        
        Args:
            trend_data: 트렌드 분석 데이터
            save_path: 저장 경로
            
        Returns:
            str: 저장된 파일 경로
        """
        try:
            if trend_data is None or 'daily_stats' not in trend_data:
                logger.warning("트렌드 차트 생성할 데이터가 없습니다.")
                return ""
            
            logger.info("트렌드 차트 생성 시작")
            
            daily_stats = trend_data['daily_stats']
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
            
            # 일별 평균 점수 트렌드
            dates = pd.to_datetime(daily_stats.index)
            ax1.plot(dates, daily_stats['avg_score'], marker='o', linewidth=2, markersize=4)
            ax1.set_title('일별 평균 위험도 점수 트렌드', fontsize=14, fontweight='bold')
            ax1.set_ylabel('평균 점수')
            ax1.grid(True, alpha=0.3)
            
            # 트렌드 방향 표시
            trend_direction = trend_data.get('trend_direction', 'unknown')
            ax1.text(0.02, 0.98, f'트렌드: {trend_direction}', 
                    transform=ax1.transAxes, fontsize=12, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.7))
            
            # TP, TN 트렌드
            ax2.plot(dates, daily_stats['avg_tp'], marker='s', label='TP', linewidth=2)
            ax2.plot(dates, daily_stats['avg_tn'], marker='^', label='TN', linewidth=2)
            ax2.set_title('일별 TP, TN 평균값 트렌드', fontsize=14, fontweight='bold')
            ax2.set_ylabel('농도 (mg/L)')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # 저장
            if save_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = os.path.join(self.output_dir, f"trend_analysis_{timestamp}.png")
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"트렌드 차트 생성 완료: {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"트렌드 차트 생성 중 오류 발생: {str(e)}")
            return ""
    
    def create_correlation_heatmap(self, data: pd.DataFrame, save_path: str = None) -> str:
        """
        상관관계 히트맵 생성
        
        Args:
            data: 수질 데이터
            save_path: 저장 경로
            
        Returns:
            str: 저장된 파일 경로
        """
        try:
            if data is None or data.empty:
                logger.warning("상관관계 히트맵 생성할 데이터가 없습니다.")
                return ""
            
            logger.info("상관관계 히트맵 생성 시작")
            
            # 수치형 컬럼만 선택
            numeric_columns = ['tp', 'tn', 'weighted_score']
            correlation_data = data[numeric_columns].corr()
            
            plt.figure(figsize=(8, 6))
            sns.heatmap(correlation_data, annot=True, cmap='coolwarm', center=0,
                       square=True, linewidths=0.5)
            plt.title('수질 지표 간 상관관계', fontsize=14, fontweight='bold')
            
            # 저장
            if save_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = os.path.join(self.output_dir, f"correlation_heatmap_{timestamp}.png")
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"상관관계 히트맵 생성 완료: {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"상관관계 히트맵 생성 중 오류 발생: {str(e)}")
            return ""
    
    def create_summary_dashboard(self, data: pd.DataFrame, regional_data: pd.DataFrame = None,
                               trend_data: Dict[str, Any] = None, save_path: str = None) -> str:
        """
        종합 대시보드 생성
        
        Args:
            data: 수질 데이터
            regional_data: 지역별 데이터
            trend_data: 트렌드 데이터
            save_path: 저장 경로
            
        Returns:
            str: 저장된 파일 경로
        """
        try:
            if data is None or data.empty:
                logger.warning("대시보드 생성할 데이터가 없습니다.")
                return ""
            
            logger.info("종합 대시보드 생성 시작")
            
            fig = plt.figure(figsize=(16, 12))
            
            # 2x2 서브플롯
            gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
            
            # 1. 위험도 분포 (파이 차트)
            ax1 = fig.add_subplot(gs[0, 0])
            risk_counts = data['risk_level'].value_counts()
            colors = ['#2E8B57', '#90EE90', '#FFFF00', '#FF0000']
            ax1.pie(risk_counts.values, labels=risk_counts.index, autopct='%1.1f%%',
                   colors=colors[:len(risk_counts)], startangle=90)
            ax1.set_title('위험도 분포', fontweight='bold')
            
            # 2. TP vs TN 산점도
            ax2 = fig.add_subplot(gs[0, 1])
            scatter = ax2.scatter(data['tp'], data['tn'], c=data['weighted_score'], 
                                cmap='viridis', alpha=0.6)
            ax2.set_xlabel('TP (mg/L)')
            ax2.set_ylabel('TN (mg/L)')
            ax2.set_title('TP vs TN 산점도', fontweight='bold')
            plt.colorbar(scatter, ax=ax2, label='가중 점수')
            
            # 3. 지역별 평균 점수 (상위 5개)
            ax3 = fig.add_subplot(gs[1, 0])
            if regional_data is not None and not regional_data.empty:
                top_regions = regional_data.nlargest(5, 'score_mean')
                bars = ax3.barh(top_regions['region'], top_regions['score_mean'],
                               color='skyblue')
                ax3.set_title('지역별 평균 점수 (상위 5개)', fontweight='bold')
                ax3.set_xlabel('평균 점수')
            
            # 4. 트렌드 (있는 경우)
            ax4 = fig.add_subplot(gs[1, 1])
            if trend_data is not None and 'daily_stats' in trend_data:
                daily_stats = trend_data['daily_stats']
                dates = pd.to_datetime(daily_stats.index)
                ax4.plot(dates, daily_stats['avg_score'], marker='o', linewidth=2)
                ax4.set_title('일별 평균 점수 트렌드', fontweight='bold')
                ax4.set_ylabel('평균 점수')
                ax4.grid(True, alpha=0.3)
            else:
                # 대신 통계 요약
                summary_stats = [
                    f"총 측정소: {len(data)}",
                    f"평균 TP: {data['tp'].mean():.3f}",
                    f"평균 TN: {data['tn'].mean():.3f}",
                    f"평균 점수: {data['weighted_score'].mean():.3f}"
                ]
                ax4.text(0.1, 0.5, '\n'.join(summary_stats), 
                        transform=ax4.transAxes, fontsize=12,
                        bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue"))
                ax4.set_title('통계 요약', fontweight='bold')
                ax4.axis('off')
            
            plt.suptitle('수질 평가 종합 대시보드', fontsize=16, fontweight='bold')
            
            # 저장
            if save_path is None:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                save_path = os.path.join(self.output_dir, f"summary_dashboard_{timestamp}.png")
            
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"종합 대시보드 생성 완료: {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"종합 대시보드 생성 중 오류 발생: {str(e)}")
            return ""

def get_color_by_risk_level(risk_level: str) -> str:
    """위험도 레벨에 따른 색상 반환"""
    color_mapping = {
        'low': '#2E8B57',
        'medium': '#90EE90', 
        'high': '#FFFF00',
        'very_high': '#FF0000'
    }
    return color_mapping.get(risk_level, '#808080') 