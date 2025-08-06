#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
환경부 수질 DB API 클라이언트
API 통신 및 데이터 수집 기능을 담당합니다.
"""

import requests
import pandas as pd
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
import logging

from ..utils.config import config
from ..utils.logger import logger

class WaterQualityAPIClient:
    """환경부 수질 DB API 클라이언트"""
    
    def __init__(self):
        self.api_key = config.api_config['SERVICE_KEY']
        self.base_url = config.api_config['BASE_URL']
        self.endpoints = config.api_config['ENDPOINTS']
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WaterQualitySystem/1.0'
        })
    
    def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict]:
        """
        API 요청 수행
        
        Args:
            endpoint: API 엔드포인트
            params: 요청 파라미터
            
        Returns:
            Optional[Dict]: API 응답 데이터
        """
        try:
            url = f"{self.base_url}{endpoint}"
            params['serviceKey'] = self.api_key
            params['resultType'] = 'xml'
            
            logger.info(f"API 요청: {url}")
            logger.info(f"파라미터: {params}")
            
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            logger.info(f"API 응답 상태: {response.status_code}")
            
            # XML 응답 파싱
            root = ET.fromstring(response.content)
            
            # 응답 헤더 확인
            header = root.find('header')
            if header is not None:
                result_code = header.find('resultCode')
                result_msg = header.find('resultMsg')
                
                if result_code is not None and result_code.text != '00':
                    logger.error(f"API 오류: {result_code.text} - {result_msg.text if result_msg is not None else 'Unknown error'}")
                    return None
            
            # 응답 바디 파싱
            body = root.find('body')
            if body is not None:
                items = body.find('items')
                if items is not None:
                    return self._parse_items(items)
            
            logger.warning("API 응답에 데이터가 없습니다.")
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API 요청 실패: {e}")
            return None
        except ET.ParseError as e:
            logger.error(f"XML 파싱 실패: {e}")
            return None
        except Exception as e:
            logger.error(f"API 요청 중 예외 발생: {e}")
            return None
    
    def _parse_items(self, items_element) -> List[Dict]:
        """
        XML items 요소를 파싱하여 데이터 리스트 반환
        
        Args:
            items_element: XML items 요소
            
        Returns:
            List[Dict]: 파싱된 데이터 리스트
        """
        data_list = []
        
        for item in items_element.findall('item'):
            item_data = {}
            
            # 모든 하위 요소를 딕셔너리로 변환
            for child in item:
                item_data[child.tag] = child.text if child.text else ''
            
            data_list.append(item_data)
        
        logger.info(f"파싱된 데이터: {len(data_list)}개")
        return data_list
    
    def get_measurement_stations(self) -> Optional[pd.DataFrame]:
        """
        측정소 목록 조회
        
        Returns:
            Optional[pd.DataFrame]: 측정소 정보 데이터프레임
        """
        logger.info("측정소 목록 조회 시작")
        
        params = {
            'numOfRows': 1000,
            'pageNo': 1
        }
        
        data = self._make_api_request(self.endpoints['LIST_POINT'], params)
        
        if data:
            df = pd.DataFrame(data)
            logger.info(f"측정소 목록 조회 완료: {len(df)}개")
            return df
        else:
            logger.error("측정소 목록 조회 실패")
            return None
    
    def get_water_quality_data(self, start_date: str, end_date: str, 
                              pt_no_list: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        수질 데이터 조회
        
        Args:
            start_date: 시작 날짜 (YYYYMMDD)
            end_date: 종료 날짜 (YYYYMMDD)
            pt_no_list: 측정소 코드 리스트 (콤마로 구분)
            
        Returns:
            Optional[pd.DataFrame]: 수질 데이터 데이터프레임
        """
        logger.info(f"수질 데이터 조회 시작: {start_date} ~ {end_date}")
        
        params = {
            'numOfRows': 1000,
            'pageNo': 1,
            'wmyrList': start_date[:4],  # 연도
            'wmodList': start_date[4:6]  # 월
        }
        
        if pt_no_list:
            params['ptNoList'] = pt_no_list
        
        data = self._make_api_request(self.endpoints['GET_WATER_MEASURING_LIST'], params)
        
        if data:
            df = pd.DataFrame(data)
            
            # 날짜 필터링
            if 'wmcymd' in df.columns:
                df['wmcymd'] = pd.to_datetime(df['wmcymd'], format='%Y.%m.%d', errors='coerce')
                df = df[(df['wmcymd'] >= pd.to_datetime(start_date)) & 
                       (df['wmcymd'] <= pd.to_datetime(end_date))]
            
            logger.info(f"수질 데이터 조회 완료: {len(df)}개")
            return df
        else:
            logger.error("수질 데이터 조회 실패")
            return None
    
    def get_real_time_water_quality(self, pt_no_list: Optional[str] = None) -> Optional[pd.DataFrame]:
        """
        실시간 수질 데이터 조회
        
        Args:
            pt_no_list: 측정소 코드 리스트 (콤마로 구분)
            
        Returns:
            Optional[pd.DataFrame]: 실시간 수질 데이터 데이터프레임
        """
        logger.info("실시간 수질 데이터 조회 시작")
        
        params = {
            'numOfRows': 1000,
            'pageNo': 1
        }
        
        if pt_no_list:
            params['ptNoList'] = pt_no_list
        
        data = self._make_api_request(self.endpoints['GET_REAL_TIME_WATER_QUALITY_LIST'], params)
        
        if data:
            df = pd.DataFrame(data)
            logger.info(f"실시간 수질 데이터 조회 완료: {len(df)}개")
            return df
        else:
            logger.error("실시간 수질 데이터 조회 실패")
            return None
    
    def test_api_connection(self) -> bool:
        """
        API 연결 테스트
        
        Returns:
            bool: 연결 성공 여부
        """
        logger.info("API 연결 테스트 시작")
        
        try:
            # 간단한 요청으로 연결 테스트
            params = {
                'numOfRows': 1,
                'pageNo': 1
            }
            
            data = self._make_api_request(self.endpoints['LIST_POINT'], params)
            
            if data:
                logger.info("✅ API 연결 성공")
                return True
            else:
                logger.error("❌ API 연결 실패")
                return False
                
        except Exception as e:
            logger.error(f"❌ API 연결 테스트 실패: {e}")
            return False
    
    def get_all_water_quality_data(self, days_back: int = 30) -> Optional[pd.DataFrame]:
        """
        최근 N일간의 모든 수질 데이터 조회
        
        Args:
            days_back: 조회할 일수
            
        Returns:
            Optional[pd.DataFrame]: 통합 수질 데이터
        """
        logger.info(f"최근 {days_back}일간 수질 데이터 조회 시작")
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        all_data = []
        
        # 날짜별로 데이터 수집
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime('%Y%m%d')
            
            logger.info(f"날짜별 데이터 수집: {date_str}")
            
            data = self.get_water_quality_data(date_str, date_str)
            if data is not None and not data.empty:
                all_data.append(data)
            
            # API 호출 간격 조절
            time.sleep(0.1)
            current_date += timedelta(days=1)
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            logger.info(f"전체 수질 데이터 수집 완료: {len(combined_df)}개")
            return combined_df
        else:
            logger.error("수질 데이터 수집 실패")
            return None 