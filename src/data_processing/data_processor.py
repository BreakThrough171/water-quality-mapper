import pandas as pd
import geopandas as gpd
import numpy as np
from config import TN_THRESHOLD, TP_THRESHOLD, RISK_LEVELS, SHAPEFILE_DIR

class WaterQualityProcessor:
    def __init__(self):
        self.tn_threshold = TN_THRESHOLD
        self.tp_threshold = TP_THRESHOLD
        self.risk_levels = RISK_LEVELS
        
    def calculate_risk_level(self, row):
        """
        TN, TP 값을 기반으로 위험도를 계산합니다.
        
        Args:
            row: DataFrame의 한 행 (TN, TP 컬럼 포함)
            
        Returns:
            str: 위험도 등급
        """
        try:
            tn_value = float(row.get('TN', 0))
            tp_value = float(row.get('TP', 0))
            
            # TN, TP 기준치 초과 여부로 위험도 판단
            tn_risk = 0
            tp_risk = 0
            
            # TN 위험도 계산
            if tn_value > self.tn_threshold * 3:
                tn_risk = 5  # 매우 위험
            elif tn_value > self.tn_threshold * 2:
                tn_risk = 4  # 위험
            elif tn_value > self.tn_threshold * 1.5:
                tn_risk = 3  # 보통
            elif tn_value > self.tn_threshold:
                tn_risk = 2  # 안전
            else:
                tn_risk = 1  # 매우 안전
                
            # TP 위험도 계산
            if tp_value > self.tp_threshold * 3:
                tp_risk = 5
            elif tp_value > self.tp_threshold * 2:
                tp_risk = 4
            elif tp_value > self.tp_threshold * 1.5:
                tp_risk = 3
            elif tp_value > self.tp_threshold:
                tp_risk = 2
            else:
                tp_risk = 1
                
            # TN, TP 중 더 높은 위험도를 선택
            max_risk = max(tn_risk, tp_risk)
            
            # 위험도 등급 반환
            for level, score in self.risk_levels.items():
                if score == max_risk:
                    return level
                    
            return '보통'  # 기본값
            
        except (ValueError, TypeError):
            return '보통'  # 데이터 오류 시 기본값
    
    def aggregate_by_region(self, df):
        """
        시군구별로 데이터를 집계합니다.
        
        Args:
            df: 수질 데이터 DataFrame
            
        Returns:
            pd.DataFrame: 시군구별 집계 데이터
        """
        if '시군구명' not in df.columns:
            print("시군구명 컬럼이 없습니다.")
            return None
            
        # 시군구별 평균값 계산
        agg_data = df.groupby('시군구명').agg({
            'TN': 'mean',
            'TP': 'mean'
        }).reset_index()
        
        # 위험도 계산
        agg_data['위험도'] = agg_data.apply(self.calculate_risk_level, axis=1)
        
        # 위험도 점수 추가
        agg_data['위험도점수'] = agg_data['위험도'].map(self.risk_levels)
        
        return agg_data
    
    def load_shapefile(self, shapefile_path=None):
        """
        시군구 SHP 파일을 로드합니다.
        
        Args:
            shapefile_path: SHP 파일 경로 (None이면 기본 경로 사용)
            
        Returns:
            gpd.GeoDataFrame: 지리 데이터
        """
        if shapefile_path is None:
            # 기본 SHP 파일 찾기
            import os
            if os.path.exists(SHAPEFILE_DIR):
                shp_files = [f for f in os.listdir(SHAPEFILE_DIR) if f.endswith('.shp')]
                if shp_files:
                    shapefile_path = os.path.join(SHAPEFILE_DIR, shp_files[0])
                else:
                    print("SHP 파일이 없습니다. data/shapefiles/ 폴더에 SHP 파일을 넣어주세요.")
                    return None
            else:
                print("SHP 파일 디렉토리가 없습니다.")
                return None
        
        try:
            gdf = gpd.read_file(shapefile_path, encoding='utf-8')
            print(f"SHP 파일 로드 완료: {len(gdf)}개 시군구")
            return gdf
        except Exception as e:
            print(f"SHP 파일 로드 실패: {str(e)}")
            return None
    
    def merge_data(self, water_data, shape_data):
        """
        수질 데이터와 지리 데이터를 결합합니다.
        
        Args:
            water_data: 수질 데이터 DataFrame
            shape_data: 지리 데이터 GeoDataFrame
            
        Returns:
            gpd.GeoDataFrame: 결합된 데이터
        """
        if water_data is None or shape_data is None:
            return None
            
        # 시군구명 컬럼 확인
        water_col = '시군구명'
        shape_col = None
        
        # SHP 파일의 시군구명 컬럼 찾기
        possible_names = ['시군구명', 'SIG_KOR_NM', 'SIG_ENG_NM', 'name', 'NAME']
        for col in possible_names:
            if col in shape_data.columns:
                shape_col = col
                break
                
        if shape_col is None:
            print("SHP 파일에서 시군구명 컬럼을 찾을 수 없습니다.")
            print("사용 가능한 컬럼:", shape_data.columns.tolist())
            return None
            
        # 데이터 결합
        try:
            merged_data = shape_data.merge(
                water_data, 
                left_on=shape_col, 
                right_on=water_col, 
                how='left'
            )
            
            print(f"데이터 결합 완료: {len(merged_data)}개 시군구")
            return merged_data
            
        except Exception as e:
            print(f"데이터 결합 실패: {str(e)}")
            return None
    
    def process_data(self, water_data):
        """
        전체 데이터 처리 과정을 수행합니다.
        
        Args:
            water_data: 원본 수질 데이터 DataFrame
            
        Returns:
            gpd.GeoDataFrame: 처리된 지리 데이터
        """
        print("데이터 처리 시작...")
        
        # 1. 시군구별 집계
        print("1. 시군구별 데이터 집계 중...")
        aggregated_data = self.aggregate_by_region(water_data)
        
        if aggregated_data is None:
            return None
            
        # 2. SHP 파일 로드
        print("2. SHP 파일 로드 중...")
        shape_data = self.load_shapefile()
        
        if shape_data is None:
            return None
            
        # 3. 데이터 결합
        print("3. 데이터 결합 중...")
        merged_data = self.merge_data(aggregated_data, shape_data)
        
        if merged_data is not None:
            print("데이터 처리 완료!")
            print(f"위험도 분포:")
            print(merged_data['위험도'].value_counts())
            
        return merged_data

# 테스트용 함수
def test_data_processing():
    """데이터 처리를 테스트합니다."""
    processor = WaterQualityProcessor()
    
    # 샘플 데이터 생성
    sample_data = pd.DataFrame({
        '시군구명': ['서울시 강남구', '서울시 서초구', '부산시 해운대구'],
        'TN': [0.5, 1.2, 2.1],
        'TP': [0.02, 0.06, 0.08]
    })
    
    print("샘플 데이터:")
    print(sample_data)
    
    # 위험도 계산 테스트
    print("\n위험도 계산 결과:")
    for idx, row in sample_data.iterrows():
        risk = processor.calculate_risk_level(row)
        print(f"{row['시군구명']}: {risk}")
    
    # 집계 테스트
    print("\n집계 결과:")
    aggregated = processor.aggregate_by_region(sample_data)
    print(aggregated)

if __name__ == "__main__":
    test_data_processing() 