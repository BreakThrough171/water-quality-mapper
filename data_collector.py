import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import os
from config import WATER_API_KEY, WATER_API_BASE_URL, WATER_QUALITY_DIR

class WaterQualityCollector:
    def __init__(self):
        self.api_key = WATER_API_KEY
        self.base_url = WATER_API_BASE_URL
        
    def get_water_quality_data(self, start_date=None, end_date=None):
        """
        환경부 수질측정망 API에서 데이터를 수집합니다.
        
        Args:
            start_date (str): 시작일 (YYYYMMDD)
            end_date (str): 종료일 (YYYYMMDD)
            
        Returns:
            pd.DataFrame: 수질 데이터
        """
        if not start_date:
            # 기본값: 어제 날짜
            yesterday = datetime.now() - timedelta(days=1)
            start_date = yesterday.strftime('%Y%m%d')
            
        if not end_date:
            end_date = start_date
            
        print(f"수질 데이터 수집 중... ({start_date} ~ {end_date})")
        
        # API 파라미터 설정
        params = {
            'serviceKey': self.api_key,
            'pageNo': 1,
            'numOfRows': 1000,
            'dataType': 'JSON',
            'startDate': start_date,
            'endDate': end_date
        }
        
        try:
            # API 호출
            response = requests.get(
                f"{self.base_url}getWaterQuality",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # 응답 데이터 확인
                if 'response' in data and 'body' in data['response']:
                    items = data['response']['body']['items']
                    
                    if items:
                        # DataFrame으로 변환
                        df = pd.DataFrame(items)
                        
                        # 필요한 컬럼만 선택 (실제 API 응답에 따라 수정 필요)
                        required_columns = ['측정소명', '측정일시', 'TN', 'TP', '시도명', '시군구명']
                        available_columns = [col for col in required_columns if col in df.columns]
                        
                        if available_columns:
                            df = df[available_columns]
                            
                            # 데이터 저장
                            self.save_data(df, start_date)
                            
                            print(f"데이터 수집 완료: {len(df)}개 측정소")
                            return df
                        else:
                            print("필요한 컬럼이 없습니다. API 응답을 확인해주세요.")
                            print("사용 가능한 컬럼:", df.columns.tolist())
                            return None
                    else:
                        print("수집된 데이터가 없습니다.")
                        return None
                else:
                    print("API 응답 형식이 올바르지 않습니다.")
                    return None
                    
            else:
                print(f"API 호출 실패: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"데이터 수집 중 오류 발생: {str(e)}")
            return None
    
    def save_data(self, df, date_str):
        """수집된 데이터를 파일로 저장합니다."""
        if not os.path.exists(WATER_QUALITY_DIR):
            os.makedirs(WATER_QUALITY_DIR)
            
        filename = f"water_quality_{date_str}.csv"
        filepath = os.path.join(WATER_QUALITY_DIR, filename)
        
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        print(f"데이터 저장 완료: {filepath}")
    
    def load_latest_data(self):
        """가장 최근 데이터를 로드합니다."""
        if not os.path.exists(WATER_QUALITY_DIR):
            return None
            
        files = [f for f in os.listdir(WATER_QUALITY_DIR) if f.endswith('.csv')]
        
        if not files:
            return None
            
        # 가장 최근 파일 찾기
        latest_file = max(files)
        filepath = os.path.join(WATER_QUALITY_DIR, latest_file)
        
        return pd.read_csv(filepath, encoding='utf-8-sig')

# 테스트용 함수
def test_api_connection():
    """API 연결을 테스트합니다."""
    collector = WaterQualityCollector()
    
    # 오늘 날짜로 테스트
    today = datetime.now().strftime('%Y%m%d')
    
    print("API 연결 테스트 중...")
    data = collector.get_water_quality_data(today, today)
    
    if data is not None:
        print("API 연결 성공!")
        print(f"수집된 데이터 샘플:")
        print(data.head())
    else:
        print("API 연결 실패. API 키와 URL을 확인해주세요.")

if __name__ == "__main__":
    test_api_connection() 