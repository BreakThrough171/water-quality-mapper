import os
import schedule
import time
from datetime import datetime
from data_collector import WaterQualityCollector
from data_processor import WaterQualityProcessor
from map_generator import MapGenerator
from config import UPDATE_TIME

def run_full_pipeline():
    """
    전체 파이프라인을 실행합니다:
    1. 수질 데이터 수집
    2. 데이터 처리 및 위험도 계산
    3. 지도 생성
    """
    print(f"\n{'='*50}")
    print(f"수질 고위험 지역 시각화 시스템 실행")
    print(f"실행 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")
    
    try:
        # 1. 데이터 수집
        print("\n1단계: 수질 데이터 수집")
        collector = WaterQualityCollector()
        
        # 어제 데이터 수집 (실제 운영 시에는 최신 데이터)
        yesterday = datetime.now().strftime('%Y%m%d')
        water_data = collector.get_water_quality_data(yesterday, yesterday)
        
        if water_data is None:
            print("데이터 수집 실패. 기존 데이터를 사용합니다.")
            water_data = collector.load_latest_data()
            
        if water_data is None:
            print("사용 가능한 데이터가 없습니다.")
            return False
            
        print(f"수집된 데이터: {len(water_data)}개 측정소")
        
        # 2. 데이터 처리
        print("\n2단계: 데이터 처리 및 위험도 계산")
        processor = WaterQualityProcessor()
        processed_data = processor.process_data(water_data)
        
        if processed_data is None:
            print("데이터 처리 실패.")
            return False
            
        print(f"처리된 데이터: {len(processed_data)}개 시군구")
        
        # 3. 지도 생성
        print("\n3단계: 지도 생성")
        generator = MapGenerator()
        m = generator.create_summary_map(processed_data)
        
        if m is None:
            print("지도 생성 실패.")
            return False
            
        # 지도 저장
        filepath = generator.save_map(m)
        
        if filepath:
            print(f"\n✅ 시스템 실행 완료!")
            print(f"생성된 지도: {filepath}")
            return True
        else:
            print("지도 저장 실패.")
            return False
            
    except Exception as e:
        print(f"시스템 실행 중 오류 발생: {str(e)}")
        return False

def run_test():
    """테스트 모드를 실행합니다."""
    print("테스트 모드 실행...")
    
    # 샘플 데이터로 테스트
    import pandas as pd
    import geopandas as gpd
    from shapely.geometry import Point
    
    # 샘플 수질 데이터
    sample_water_data = pd.DataFrame({
        '시군구명': ['서울시 강남구', '서울시 서초구', '부산시 해운대구', '대구시 수성구'],
        'TN': [0.5, 1.2, 2.1, 0.8],
        'TP': [0.02, 0.06, 0.08, 0.03]
    })
    
    # 샘플 지리 데이터
    sample_geo_data = pd.DataFrame({
        '시군구명': ['서울시 강남구', '서울시 서초구', '부산시 해운대구', '대구시 수성구'],
        'geometry': [
            Point(127.0, 37.5),  # 서울
            Point(127.1, 37.4),  # 서울
            Point(129.2, 35.2),  # 부산
            Point(128.6, 35.9)   # 대구
        ]
    })
    
    gdf = gpd.GeoDataFrame(sample_geo_data)
    
    # 데이터 처리
    processor = WaterQualityProcessor()
    processed_data = processor.merge_data(
        processor.aggregate_by_region(sample_water_data),
        gdf
    )
    
    if processed_data is not None:
        # 지도 생성
        generator = MapGenerator()
        m = generator.create_summary_map(processed_data)
        
        if m is not None:
            filepath = generator.save_map(m, "test_map.html")
            print(f"테스트 지도 생성 완료: {filepath}")
            return True
    
    print("테스트 실패.")
    return False

def setup_scheduler():
    """자동 갱신 스케줄러를 설정합니다."""
    schedule.every().day.at(UPDATE_TIME).do(run_full_pipeline)
    
    print(f"자동 갱신 스케줄 설정 완료: 매일 {UPDATE_TIME}")
    print("스케줄러를 중지하려면 Ctrl+C를 누르세요.")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

def main():
    """메인 함수"""
    print("한국 하천 수질 고위험 지역 시각화 시스템")
    print("=" * 50)
    print("1. 전체 파이프라인 실행")
    print("2. 테스트 모드 실행")
    print("3. 자동 갱신 모드 실행")
    print("4. 종료")
    print("=" * 50)
    
    while True:
        try:
            choice = input("\n선택하세요 (1-4): ").strip()
            
            if choice == '1':
                success = run_full_pipeline()
                if success:
                    print("\n✅ 파이프라인 실행 완료!")
                else:
                    print("\n❌ 파이프라인 실행 실패!")
                    
            elif choice == '2':
                success = run_test()
                if success:
                    print("\n✅ 테스트 완료!")
                else:
                    print("\n❌ 테스트 실패!")
                    
            elif choice == '3':
                print(f"\n자동 갱신 모드를 시작합니다. 매일 {UPDATE_TIME}에 실행됩니다.")
                print("중지하려면 Ctrl+C를 누르세요.")
                setup_scheduler()
                
            elif choice == '4':
                print("시스템을 종료합니다.")
                break
                
            else:
                print("잘못된 선택입니다. 1-4 중에서 선택해주세요.")
                
        except KeyboardInterrupt:
            print("\n\n시스템을 종료합니다.")
            break
        except Exception as e:
            print(f"오류 발생: {str(e)}")

if __name__ == "__main__":
    main() 