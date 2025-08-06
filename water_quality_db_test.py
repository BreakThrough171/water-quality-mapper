#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
물환경 수질측정 운영결과 DB 테스트 프로그램
환경부 수질측정망 API를 사용하여 데이터를 수집하고 테스트합니다.
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import os
import sys

class WaterQualityDBTest:
    def __init__(self):
        # API 설정
        self.api_key = 'pC3qRcSJ2t4Z0PbPxhZCCgpbpzacTnX8OaQNpVwaJuQ5v9QJprbXaOgGTilPra7JnZ9AyjnLxGN6VPhobYKJHw=='
        self.base_url = 'http://apis.data.go.kr/1480523/WaterQualityService'
        
        # API 엔드포인트
        self.endpoints = {
            'list_point': '/listPoint',  # 측정소 목록 조회
            'get_list': '/getList',       # 수질 데이터 조회
            'get_radio_active': '/getRadioActiveMaterList'  # 방사성 물질 데이터 조회
        }
        
        # 수질 측정 항목 코드
        self.parameters = {
            'M01': '통신상태',
            'M05': 'DO (용존산소)',
            'M27': 'TN (총질소)',
            'M28': 'TP (총인)',
            'pH': '수소이온농도',
            'COD': '화학적산소요구량',
            'BOD': '생화학적산소요구량'
        }
        
        # 지역 코드
        self.regions = {
            '46': '전남',
            '47': '전북',
            '48': '경남',
            '49': '경북'
        }
    
    def test_api_connection(self):
        """API 연결 테스트"""
        print("=== API 연결 테스트 ===")
        
        # 측정소 목록 조회 테스트
        print("\n1. 측정소 목록 조회 테스트")
        try:
            params = {
                'serviceKey': self.api_key,
                'pageNo': 1,
                'numOfRows': 10,
                'dataType': 'JSON'
            }
            
            response = requests.get(
                f"{self.base_url}{self.endpoints['list_point']}",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API 연결 성공 (상태코드: {response.status_code})")
                print(f"응답 데이터 구조: {list(data.keys()) if isinstance(data, dict) else '응답 형식 확인 필요'}")
                
                # 응답 데이터 상세 확인
                if 'response' in data:
                    print(f"response 키 존재: ✅")
                    if 'body' in data['response']:
                        print(f"body 키 존재: ✅")
                        if 'items' in data['response']['body']:
                            items = data['response']['body']['items']
                            print(f"측정소 개수: {len(items) if isinstance(items, list) else 'N/A'}")
                        else:
                            print("items 키 없음")
                    else:
                        print("body 키 없음")
                else:
                    print("response 키 없음")
                    
            else:
                print(f"❌ API 연결 실패 (상태코드: {response.status_code})")
                print(f"응답 내용: {response.text}")
                
        except Exception as e:
            print(f"❌ API 연결 중 오류 발생: {str(e)}")
    
    def get_measurement_stations(self, region_code='46'):
        """측정소 목록 조회"""
        print(f"\n=== 측정소 목록 조회 (지역: {self.regions.get(region_code, region_code)}) ===")
        
        try:
            params = {
                'serviceKey': self.api_key,
                'pageNo': 1,
                'numOfRows': 100,
                'dataType': 'JSON',
                'regionCode': region_code
            }
            
            response = requests.get(
                f"{self.base_url}{self.endpoints['list_point']}",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'response' in data and 'body' in data['response']:
                    items = data['response']['body']['items']
                    
                    if isinstance(items, list) and items:
                        df = pd.DataFrame(items)
                        print(f"✅ 측정소 {len(df)}개 조회 성공")
                        print(f"컬럼: {list(df.columns)}")
                        
                        # 첫 5개 측정소 정보 출력
                        if len(df) > 0:
                            print("\n첫 5개 측정소 정보:")
                            display_columns = ['측정소명', '시도명', '시군구명', '측정소코드']
                            available_columns = [col for col in display_columns if col in df.columns]
                            
                            if available_columns:
                                print(df[available_columns].head())
                            else:
                                print("표시할 컬럼이 없습니다.")
                        
                        return df
                    else:
                        print("❌ 측정소 데이터가 없습니다.")
                        return None
                else:
                    print("❌ API 응답 형식이 올바르지 않습니다.")
                    return None
            else:
                print(f"❌ API 호출 실패 (상태코드: {response.status_code})")
                return None
                
        except Exception as e:
            print(f"❌ 측정소 목록 조회 중 오류 발생: {str(e)}")
            return None
    
    def get_water_quality_data(self, start_date=None, end_date=None, region_code='46'):
        """수질 데이터 조회"""
        print(f"\n=== 수질 데이터 조회 ===")
        
        if not start_date:
            # 기본값: 어제 날짜
            yesterday = datetime.now() - timedelta(days=1)
            start_date = yesterday.strftime('%Y%m%d')
            
        if not end_date:
            end_date = start_date
            
        print(f"조회 기간: {start_date} ~ {end_date}")
        print(f"지역: {self.regions.get(region_code, region_code)}")
        
        try:
            params = {
                'serviceKey': self.api_key,
                'pageNo': 1,
                'numOfRows': 1000,
                'dataType': 'JSON',
                'startDate': start_date,
                'endDate': end_date,
                'regionCode': region_code
            }
            
            response = requests.get(
                f"{self.base_url}{self.endpoints['get_list']}",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if 'response' in data and 'body' in data['response']:
                    items = data['response']['body']['items']
                    
                    if isinstance(items, list) and items:
                        df = pd.DataFrame(items)
                        print(f"✅ 수질 데이터 {len(df)}개 조회 성공")
                        print(f"컬럼: {list(df.columns)}")
                        
                        # 데이터 샘플 출력
                        if len(df) > 0:
                            print("\n첫 5개 데이터 샘플:")
                            display_columns = ['측정소명', '측정일시', 'TN', 'TP', 'DO', 'pH']
                            available_columns = [col for col in display_columns if col in df.columns]
                            
                            if available_columns:
                                print(df[available_columns].head())
                            else:
                                print("표시할 컬럼이 없습니다.")
                        
                        return df
                    else:
                        print("❌ 수질 데이터가 없습니다.")
                        return None
                else:
                    print("❌ API 응답 형식이 올바르지 않습니다.")
                    return None
            else:
                print(f"❌ API 호출 실패 (상태코드: {response.status_code})")
                return None
                
        except Exception as e:
            print(f"❌ 수질 데이터 조회 중 오류 발생: {str(e)}")
            return None
    
    def save_test_data(self, df, filename):
        """테스트 데이터를 CSV 파일로 저장"""
        if df is not None and len(df) > 0:
            # data 디렉토리 생성
            if not os.path.exists('data'):
                os.makedirs('data')
            
            filepath = os.path.join('data', filename)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            print(f"✅ 데이터 저장 완료: {filepath}")
            return filepath
        else:
            print("❌ 저장할 데이터가 없습니다.")
            return None
    
    def run_comprehensive_test(self):
        """종합 테스트 실행"""
        print("=" * 60)
        print("물환경 수질측정 운영결과 DB 테스트 프로그램")
        print("=" * 60)
        
        # 1. API 연결 테스트
        self.test_api_connection()
        
        # 2. 측정소 목록 조회 테스트
        stations_df = self.get_measurement_stations()
        if stations_df is not None:
            self.save_test_data(stations_df, 'measurement_stations_test.csv')
        
        # 3. 수질 데이터 조회 테스트
        water_quality_df = self.get_water_quality_data()
        if water_quality_df is not None:
            self.save_test_data(water_quality_df, 'water_quality_data_test.csv')
        
        print("\n" + "=" * 60)
        print("테스트 완료!")
        print("=" * 60)

def main():
    """메인 함수"""
    try:
        # 필요한 라이브러리 확인
        required_packages = ['requests', 'pandas', 'json']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ 필요한 패키지가 설치되지 않았습니다: {missing_packages}")
            print("다음 명령어로 설치하세요:")
            print(f"pip install {' '.join(missing_packages)}")
            return
        
        # 테스트 실행
        tester = WaterQualityDBTest()
        tester.run_comprehensive_test()
        
    except Exception as e:
        print(f"❌ 프로그램 실행 중 오류 발생: {str(e)}")

if __name__ == "__main__":
    main() 