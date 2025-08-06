#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
전국 수질 평가 시스템 파이프라인
전체 시스템을 실행하는 메인 스크립트입니다.
"""

import sys
import os
from datetime import datetime
import schedule
import time
from typing import List, Dict
import pandas as pd

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_collection.api_client import WaterQualityAPIClient
from src.data_collection.data_collector import WaterQualityCollector
from src.data_processing.preprocessor import DataPreprocessor
from src.data_processing.data_processor import WaterQualityProcessor
from src.risk_assessment.risk_calculator import RiskCalculator
from src.risk_assessment.alert_system import AlertSystem
from src.visualization.map_generator import MapGenerator
from src.visualization.chart_generator import ChartGenerator
from src.web_publisher.web_publisher import WebPublisher
from src.utils.config import config
from src.utils.logger import logger

class WaterQualityPipeline:
    """수질 평가 파이프라인 클래스"""
    
    def __init__(self):
        self.api_client = WaterQualityAPIClient()
        self.collector = WaterQualityCollector()
        self.preprocessor = DataPreprocessor()
        self.processor = WaterQualityProcessor()
        self.risk_calculator = RiskCalculator()
        self.alert_system = AlertSystem()
        self.map_generator = MapGenerator()
        self.chart_generator = ChartGenerator()
        self.web_publisher = WebPublisher()
    
    def run_full_pipeline(self) -> bool:
        """
        전체 파이프라인 실행
        
        Returns:
            bool: 실행 성공 여부
        """
        try:
            logger.info("=" * 60)
            logger.info("전국 수질 평가 시스템 파이프라인 시작")
            logger.info(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info("=" * 60)
            
            # 1. 데이터 수집 (새로운 구조: API → CSV 업데이트 → 기존 CSV)
            logger.info("\n1단계: 데이터 수집")
            raw_data = self.collector.collect_data()
            
            if raw_data is None or raw_data.empty:
                logger.error("사용 가능한 데이터가 없습니다.")
                return False
            
            logger.info(f"✅ 수집된 데이터: {len(raw_data)}개 측정소")
            
            # 2. 데이터 전처리
            logger.info("\n2단계: 데이터 전처리")
            processed_data = self.preprocessor.preprocess_water_quality_data(raw_data)
            
            if processed_data is None:
                logger.error("데이터 전처리 실패.")
                return False
            
            logger.info(f"✅ 전처리된 데이터: {len(processed_data)}개 레코드")
            
            # 3. 위험도 계산
            logger.info("\n3단계: 위험도 계산")
            risk_data = self.risk_calculator.calculate_risk_scores(processed_data)
            
            if risk_data is None:
                logger.error("위험도 계산 실패.")
                return False
            
            logger.info(f"✅ 위험도 계산 완료: {len(risk_data)}개 레코드")
            
            # 4. 지역별 위험도 계산
            logger.info("\n4단계: 지역별 위험도 계산")
            regional_data = self.risk_calculator.calculate_regional_risk(risk_data)
            
            if regional_data is None:
                logger.warning("지역별 위험도 계산 실패. 기본 데이터 사용.")
                regional_data = risk_data
            
            # 5. 고위험 지역 식별
            logger.info("\n5단계: 고위험 지역 식별")
            high_risk_areas = self.risk_calculator.identify_high_risk_areas(risk_data)
            
            if high_risk_areas is not None:
                logger.info(f"✅ 고위험 지역 식별: {len(high_risk_areas)}개 지역")
            else:
                logger.warning("고위험 지역 식별 실패.")
            
            # 6. 경보 생성
            logger.info("\n6단계: 경보 시스템")
            alerts = self.alert_system.generate_alerts(risk_data, high_risk_areas)
            
            if alerts:
                logger.info(f"✅ 경보 생성: {len(alerts)}개")
            else:
                logger.info("경보 없음")
            
            # 7. 지도 생성
            logger.info("\n7단계: 지도 생성")
            map_file = self._generate_map(risk_data, regional_data)
            
            if map_file:
                logger.info(f"✅ 지도 생성 완료: {map_file}")
            else:
                logger.error("지도 생성 실패.")
                return False
            
            # 8. 차트 생성
            logger.info("\n8단계: 차트 생성")
            chart_files = self._generate_charts(risk_data, regional_data)
            
            if chart_files:
                logger.info(f"✅ 차트 생성 완료: {len(chart_files)}개")
            else:
                logger.warning("차트 생성 실패.")
            
            # 9. 웹 게시
            logger.info("\n9단계: 웹 게시")
            web_files = self._publish_to_web(map_file, chart_files)
            
            if web_files:
                logger.info(f"✅ 웹 게시 완료: {len(web_files)}개 파일")
            else:
                logger.warning("웹 게시 실패.")
            
            # 10. 결과 요약
            logger.info("\n10단계: 결과 요약")
            self._print_summary(risk_data, regional_data, high_risk_areas, alerts)
            
            logger.info("\n" + "=" * 60)
            logger.info("✅ 파이프라인 실행 완료")
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(f"파이프라인 실행 중 오류 발생: {str(e)}")
            return False
    
    def _generate_map(self, risk_data: pd.DataFrame, regional_data: pd.DataFrame = None) -> str:
        """
        지도 생성
        
        Args:
            risk_data: 위험도 데이터
            regional_data: 지역별 데이터
            
        Returns:
            str: 생성된 지도 파일 경로
        """
        try:
            map_file = self.map_generator.create_integrated_map(risk_data, regional_data)
            return map_file
        except Exception as e:
            logger.error(f"지도 생성 중 오류: {str(e)}")
            return None
    
    def _generate_charts(self, risk_data: pd.DataFrame, regional_data: pd.DataFrame = None,
                        trend_data: Dict = None) -> List[str]:
        """
        차트 생성
        
        Args:
            risk_data: 위험도 데이터
            regional_data: 지역별 데이터
            trend_data: 트렌드 데이터
            
        Returns:
            List[str]: 생성된 차트 파일 경로 리스트
        """
        try:
            chart_files = []
            
            # 위험도 분포 차트
            risk_chart = self.chart_generator.create_risk_distribution_chart(risk_data)
            if risk_chart:
                chart_files.append(risk_chart)
            
            # 지역별 비교 차트
            if regional_data is not None:
                regional_chart = self.chart_generator.create_regional_comparison_chart(regional_data)
                if regional_chart:
                    chart_files.append(regional_chart)
            
            # 트렌드 분석 차트
            if trend_data:
                trend_chart = self.chart_generator.create_trend_analysis_chart(trend_data)
                if trend_chart:
                    chart_files.append(trend_chart)
            
            # 상관관계 히트맵
            correlation_chart = self.chart_generator.create_correlation_heatmap(risk_data)
            if correlation_chart:
                chart_files.append(correlation_chart)
            
            # 종합 대시보드
            dashboard_chart = self.chart_generator.create_summary_dashboard(risk_data, regional_data)
            if dashboard_chart:
                chart_files.append(dashboard_chart)
            
            return chart_files
            
        except Exception as e:
            logger.error(f"차트 생성 중 오류: {str(e)}")
            return []
    
    def _publish_to_web(self, map_file: str, chart_files: List[str]) -> List[str]:
        """
        웹 게시
        
        Args:
            map_file: 지도 파일 경로
            chart_files: 차트 파일 경로 리스트
            
        Returns:
            List[str]: 게시된 웹 파일 경로 리스트
        """
        try:
            web_files = self.web_publisher.publish_results(map_file, chart_files)
            return web_files
        except Exception as e:
            logger.error(f"웹 게시 중 오류: {str(e)}")
            return []
    
    def _print_summary(self, risk_data: pd.DataFrame, regional_data: pd.DataFrame = None,
                      high_risk_areas: pd.DataFrame = None, alerts: List = None):
        """
        결과 요약 출력
        
        Args:
            risk_data: 위험도 데이터
            regional_data: 지역별 데이터
            high_risk_areas: 고위험 지역
            alerts: 경보 리스트
        """
        try:
            logger.info("\n📊 결과 요약")
            logger.info("-" * 40)
            
            # 기본 통계
            if risk_data is not None:
                logger.info(f"📈 총 측정소 수: {len(risk_data)}개")
                logger.info(f"📊 평균 위험도 점수: {risk_data['weighted_score'].mean():.4f}")
                logger.info(f"📊 최대 위험도 점수: {risk_data['weighted_score'].max():.4f}")
                logger.info(f"📊 최소 위험도 점수: {risk_data['weighted_score'].min():.4f}")
            
            # 지역별 통계
            if regional_data is not None:
                logger.info(f"🗺️ 분석 지역 수: {len(regional_data)}개")
            
            # 고위험 지역
            if high_risk_areas is not None and not high_risk_areas.empty:
                logger.info(f"⚠️ 고위험 지역 수: {len(high_risk_areas)}개")
                for idx, row in high_risk_areas.head().iterrows():
                    logger.info(f"   - {row.get('ptNm', 'Unknown')}: {row.get('weighted_score', 0):.4f}")
            
            # 경보
            if alerts:
                logger.info(f"🚨 활성 경보 수: {len(alerts)}개")
                for alert in alerts[:3]:  # 최대 3개만 표시
                    logger.info(f"   - {alert}")
            
            logger.info("-" * 40)
            
        except Exception as e:
            logger.error(f"결과 요약 출력 중 오류: {str(e)}")
    
    def run_scheduled_pipeline(self):
        """스케줄된 파이프라인 실행"""
        logger.info(f"🕐 스케줄 실행: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.run_full_pipeline()
    
    def setup_scheduler(self):
        """스케줄러 설정"""
        update_time = config.get_update_time()
        schedule.every(update_time).minutes.do(self.run_scheduled_pipeline)
        
        logger.info(f"⏰ 스케줄러 설정 완료: {update_time}분마다 실행")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크

def main():
    """메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description='전국 수질 평가 시스템 파이프라인')
    parser.add_argument('--mode', choices=['run', 'schedule', 'test'], 
                       default='run', help='실행 모드')
    parser.add_argument('--test', action='store_true', help='테스트 모드')
    
    args = parser.parse_args()
    
    pipeline = WaterQualityPipeline()
    
    if args.mode == 'schedule':
        logger.info("🔄 스케줄 모드로 실행")
        pipeline.setup_scheduler()
    elif args.mode == 'test' or args.test:
        logger.info("🧪 테스트 모드로 실행")
        # 테스트용 간단한 실행
        success = pipeline.run_full_pipeline()
        if success:
            logger.info("✅ 테스트 성공")
        else:
            logger.error("❌ 테스트 실패")
    else:
        logger.info("▶️ 일반 모드로 실행")
        success = pipeline.run_full_pipeline()
        if success:
            logger.info("✅ 파이프라인 실행 성공")
        else:
            logger.error("❌ 파이프라인 실행 실패")

if __name__ == "__main__":
    main() 