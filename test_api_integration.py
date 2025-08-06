#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 연동 기능 테스트 스크립트
"""

import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_collection.api_client import WaterQualityAPIClient
from src.data_collection.data_collector import WaterQualityCollector

def test_api_client():
    """API 클라이언트 테스트"""
    print("=" * 60)
    print("API 클라이언트 테스트")
    print("=" * 60)
    
    client = WaterQualityAPIClient()
    
    # API 연결 테스트
    print("\n1. API 연결 테스트")
    connection_success = client.test_api_connection()
    print(f"API 연결 결과: {'성공' if connection_success else '실패'}")
    
    if connection_success:
        # 측정소 목록 조회 테스트
        print("\n2. 측정소 목록 조회 테스트")
        stations = client.get_measurement_stations()
        if stations is not None:
            print(f"측정소 수: {len(stations)}개")
            print("측정소 샘플:")
            print(stations.head())
        else:
            print("측정소 목록 조회 실패")
        
        # 수질 데이터 조회 테스트
        print("\n3. 수질 데이터 조회 테스트")
        water_data = client.get_water_quality_data('20241201', '20241201')
        if water_data is not None:
            print(f"수질 데이터 수: {len(water_data)}개")
            print("수질 데이터 샘플:")
            print(water_data.head())
        else:
            print("수질 데이터 조회 실패")
    else:
        print("API 연결 실패로 인해 추가 테스트를 건너뜁니다.")

def test_data_collector():
    """데이터 수집기 테스트"""
    print("\n" + "=" * 60)
    print("데이터 수집기 테스트 (새로운 구조)")
    print("=" * 60)
    
    collector = WaterQualityCollector()
    
    # 데이터 수집 테스트
    print("\n데이터 수집 시작...")
    data = collector.collect_data()
    
    if data is not None and not data.empty:
        print(f"✅ 데이터 수집 성공: {len(data)}개 레코드")
        print("데이터 샘플:")
        print(data.head())
        
        # 통계 정보 출력
        stats = collector.get_statistics()
        print("\n📊 데이터 통계:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    else:
        print("❌ 데이터 수집 실패")

def main():
    """메인 테스트 함수"""
    print("🌊 전국 수질 평가 시스템 - API 연동 테스트")
    print("=" * 60)
    
    try:
        # API 클라이언트 테스트
        test_api_client()
        
        # 데이터 수집기 테스트
        test_data_collector()
        
        print("\n" + "=" * 60)
        print("✅ 테스트 완료!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 