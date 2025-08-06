#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
지도 생성 모듈
수질 데이터를 기반으로 전국 시군구별 수질 평가 지도를 생성합니다.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import warnings
from typing import Optional, Dict, List, Any
from datetime import datetime

warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class MapGenerator:
    """지도 생성 클래스"""
    
    def __init__(self):
        self.shapefiles_dir = "행정구역SHP지도"
        self.output_dir = "data/output"
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 색상 매핑
        self.colors = {
            'low': '#2E8B57',      # 초록색 - 수질 우수
            'medium': '#90EE90',    # 연초록색 - 수질 양호
            'high': '#FFFF00',      # 노란색 - 수질 보통
            'very_high': '#FF0000', # 빨간색 - 수질 매우 나쁨
            'unknown': '#808080'    # 회색 - 알 수 없음
        }
        
        # 위험도 분류 기준
        self.risk_thresholds = {
            'low': 0.5,
            'medium': 1.0,
            'high': 2.0,
            'very_high': float('inf')
        }
    
    def load_national_shapefiles(self) -> Optional[gpd.GeoDataFrame]:
        """
        전국 시군구 shapefile들을 로드하고 통합합니다.
        
        Returns:
            Optional[gpd.GeoDataFrame]: 통합된 전국 지리 데이터
        """
        try:
            print("전국 시군구 shapefile 로드 중...")
            
            # 모든 시도별 shapefile 경로
            shapefile_paths = {
                '서울': f"{self.shapefiles_dir}/LARD_ADM_SECT_SGG_서울/LARD_ADM_SECT_SGG_11_202505.shp",
                '부산': f"{self.shapefiles_dir}/LARD_ADM_SECT_SGG_부산/LARD_ADM_SECT_SGG_26_202505.shp",
                '대구': f"{self.shapefiles_dir}/LARD_ADM_SECT_SGG_대구/LARD_ADM_SECT_SGG_27_202505.shp",
                '인천': f"{self.shapefiles_dir}/LARD_ADM_SECT_SGG_인천/LARD_ADM_SECT_SGG_28_202505.shp",
                '광주': f"{self.shapefiles_dir}/LARD_ADM_SECT_SGG_광주/LARD_ADM_SECT_SGG_29_202505.shp",
                '대전': f"{self.shapefiles_dir}/LARD_ADM_SECT_SGG_대전/LARD_ADM_SECT_SGG_30_202505.shp",
                '울산': f"{self.shapefiles_dir}/LARD_ADM_SECT_SGG_울산/LARD_ADM_SECT_SGG_31_202505.shp",
                '세종': f"{self.shapefiles_dir}/LARD_ADM_SECT_SGG_세종/LARD_ADM_SECT_SGG_36_202505.shp",
                '경기': f"{self.shapefiles_dir}/LARD_ADM_SECT_SGG_경기/LARD_ADM_SECT_SGG_41_202505.shp",
                '강원': f"{self.shapefiles_dir}/LARD_ADM_SECT_SGG_강원특별자치도/LARD_ADM_SECT_SGG_51_202505.shp",
                '충북': f"{self.shapefiles_dir}/LARD_ADM_SECT_SGG_충북/LARD_ADM_SECT_SGG_43_202505.shp",
                '충남': f"{self.shapefiles_dir}/LARD_ADM_SECT_SGG_충남/LARD_ADM_SECT_SGG_44_202505.shp",
                '전북': f"{self.shapefiles_dir}/LARD_ADM_SECT_SGG_전북특별자치도/LARD_ADM_SECT_SGG_52_202505.shp",
                '전남': f"{self.shapefiles_dir}/LARD_ADM_SECT_SGG_전남/LARD_ADM_SECT_SGG_46_202505.shp",
                '경북': f"{self.shapefiles_dir}/LARD_ADM_SECT_SGG_경북/LARD_ADM_SECT_SGG_47_202505.shp",
                '경남': f"{self.shapefiles_dir}/LARD_ADM_SECT_SGG_경남/LARD_ADM_SECT_SGG_48_202505.shp",
                '제주': f"{self.shapefiles_dir}/LARD_ADM_SECT_SGG_제주/LARD_ADM_SECT_SGG_50_202505.shp"
            }
            
            all_gdfs = []
            
            for region_name, shp_path in shapefile_paths.items():
                if os.path.exists(shp_path):
                    try:
                        print(f"  {region_name} 로드 중...")
                        gdf = gpd.read_file(shp_path)
                        
                        # CRS를 WGS84로 변환
                        if gdf.crs is not None and "4326" not in str(gdf.crs):
                            gdf = gdf.to_crs(epsg=4326)
                        
                        # 지오메트리 간소화 (성능 향상)
                        gdf['geometry'] = gdf['geometry'].simplify(0.001, preserve_topology=False)
                        
                        # 지역명 추가
                        gdf['region_name'] = region_name
                        
                        all_gdfs.append(gdf)
                        print(f"  {region_name} 로드 완료: {len(gdf)}개 시군구")
                        
                    except Exception as e:
                        print(f"  {region_name} 로드 실패: {str(e)}")
                        continue
                else:
                    print(f"  {region_name} shapefile 없음: {shp_path}")
            
            if not all_gdfs:
                print("로드된 shapefile이 없습니다.")
                return None
            
            # 모든 GeoDataFrame 통합
            print("전국 데이터 통합 중...")
            national_gdf = pd.concat(all_gdfs, ignore_index=True)
            
            print(f"전국 지도 로드 완료: {len(national_gdf)}개 시군구")
            return national_gdf
            
        except Exception as e:
            print(f"전국 shapefile 로드 중 오류 발생: {str(e)}")
            return None
    
    def create_integrated_map(self, risk_data: pd.DataFrame, regional_data: pd.DataFrame = None) -> str:
        """
        통합 수질 평가 지도 생성
        
        Args:
            risk_data: 위험도 데이터
            regional_data: 지역별 데이터
            
        Returns:
            str: 생성된 지도 파일 경로
        """
        try:
            print("통합 수질 평가 지도 생성 시작...")
            
            # 1. 전국 shapefile 로드
            national_gdf = self.load_national_shapefiles()
            if national_gdf is None:
                print("전국 shapefile 로드 실패")
                return ""
            
            # 2. 위험도 데이터와 병합
            if risk_data is not None and not risk_data.empty:
                print("위험도 데이터와 지리 데이터 병합 중...")
                
                # 지역명 매핑을 위한 데이터 전처리
                risk_data_processed = self._process_risk_data(risk_data)
                
                # 지리 데이터와 병합
                merged_data = self._merge_with_geodata(national_gdf, risk_data_processed)
            else:
                print("위험도 데이터가 없어 기본 지도 생성")
                merged_data = national_gdf
                merged_data['weighted_score'] = np.nan
                merged_data['risk_level'] = 'unknown'
            
            # 3. 지도 생성
            output_file = self._create_map_visualization(merged_data)
            
            print(f"통합 지도 생성 완료: {output_file}")
            return output_file
            
        except Exception as e:
            print(f"통합 지도 생성 중 오류 발생: {str(e)}")
            return ""
    
    def _process_risk_data(self, risk_data: pd.DataFrame) -> pd.DataFrame:
        """
        위험도 데이터 전처리
        
        Args:
            risk_data: 원본 위험도 데이터
            
        Returns:
            pd.DataFrame: 전처리된 데이터
        """
        processed_data = risk_data.copy()
        
        # 지역명 추출 및 정규화
        if 'addr' in processed_data.columns:
            processed_data['region_name'] = processed_data['addr'].apply(self._extract_region_name)
        
        # 위험도 레벨 분류
        if 'weighted_score' in processed_data.columns:
            processed_data['risk_level'] = processed_data['weighted_score'].apply(self._classify_risk_level)
        
        return processed_data
    
    def _extract_region_name(self, address: str) -> str:
        """
        주소에서 지역명 추출
        
        Args:
            address: 주소 문자열
            
        Returns:
            str: 추출된 지역명
        """
        if pd.isna(address):
            return 'Unknown'
        
        # 시도명 매핑
        region_mapping = {
            '서울': '서울',
            '부산': '부산',
            '대구': '대구',
            '인천': '인천',
            '광주': '광주',
            '대전': '대전',
            '울산': '울산',
            '세종': '세종',
            '경기': '경기',
            '강원': '강원',
            '충북': '충북',
            '충남': '충남',
            '전북': '전북',
            '전남': '전남',
            '경북': '경북',
            '경남': '경남',
            '제주': '제주'
        }
        
        for key, value in region_mapping.items():
            if key in address:
                return value
        
        return 'Unknown'
    
    def _classify_risk_level(self, score: float) -> str:
        """
        위험도 점수를 레벨로 분류
        
        Args:
            score: 위험도 점수
            
        Returns:
            str: 위험도 레벨
        """
        if pd.isna(score):
            return 'unknown'
        
        for level, threshold in self.risk_thresholds.items():
            if score <= threshold:
                return level
        
        return 'very_high'
    
    def _merge_with_geodata(self, geodata: gpd.GeoDataFrame, risk_data: pd.DataFrame) -> gpd.GeoDataFrame:
        """
        지리 데이터와 위험도 데이터 병합
        
        Args:
            geodata: 지리 데이터
            risk_data: 위험도 데이터
            
        Returns:
            gpd.GeoDataFrame: 병합된 데이터
        """
        # 지역별 평균 위험도 계산
        if 'region_name' in risk_data.columns and 'weighted_score' in risk_data.columns:
            regional_risk = risk_data.groupby('region_name')['weighted_score'].mean().reset_index()
            regional_risk['risk_level'] = regional_risk['weighted_score'].apply(self._classify_risk_level)
            
            # 지리 데이터와 병합
            merged_data = geodata.merge(regional_risk, on='region_name', how='left')
        else:
            merged_data = geodata.copy()
            merged_data['weighted_score'] = np.nan
            merged_data['risk_level'] = 'unknown'
        
        return merged_data
    
    def _create_map_visualization(self, merged_data: gpd.GeoDataFrame) -> str:
        """
        지도 시각화 생성
        
        Args:
            merged_data: 병합된 데이터
            
        Returns:
            str: 생성된 파일 경로
        """
        # 지도 생성
        fig, ax = plt.subplots(1, 1, figsize=(16, 12))
        
        # NaN 값 처리
        merged_data['risk_level'] = merged_data['risk_level'].fillna('unknown')
        
        # 색상 매핑
        color_mapping = merged_data['risk_level'].map(self.colors)
        
        # NaN 색상 처리
        color_mapping = color_mapping.fillna(self.colors['unknown'])
        
        # 지도 그리기
        merged_data.plot(
            color=color_mapping,
            edgecolor='black',
            linewidth=0.3,
            ax=ax,
            legend=False
        )
        
        # 지역명 표시 (주요 도시만)
        major_cities = ['서울', '부산', '대구', '인천', '광주', '대전', '울산']
        for idx, row in merged_data.iterrows():
            if row['region_name'] in major_cities:
                try:
                    centroid = row['geometry'].centroid
                    ax.annotate(
                        row['region_name'],
                        xy=(centroid.x, centroid.y),
                        xytext=(0, 0),
                        textcoords='offset points',
                        ha='center',
                        va='center',
                        fontsize=10,
                        fontweight='bold',
                        color='black',
                        bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8, edgecolor='black', linewidth=0.5)
                    )
                except Exception as e:
                    continue
        
        # 범례 생성
        legend_elements = [
            plt.Rectangle((0,0),1,1, facecolor=self.colors['low'], edgecolor='black', linewidth=0.5, label='우수 (0.0-0.5)'),
            plt.Rectangle((0,0),1,1, facecolor=self.colors['medium'], edgecolor='black', linewidth=0.5, label='양호 (0.5-1.0)'),
            plt.Rectangle((0,0),1,1, facecolor=self.colors['high'], edgecolor='black', linewidth=0.5, label='보통 (1.0-2.0)'),
            plt.Rectangle((0,0),1,1, facecolor=self.colors['very_high'], edgecolor='black', linewidth=0.5, label='매우 나쁨 (2.0+)'),
            plt.Rectangle((0,0),1,1, facecolor=self.colors['unknown'], edgecolor='black', linewidth=0.5, label='데이터 없음')
        ]
        
        ax.legend(handles=legend_elements, loc='upper right', fontsize=12, title='수질 평가 등급', title_fontsize=14)
        
        # 제목 설정
        timestamp = datetime.now().strftime('%Y년 %m월 %d일 %H:%M')
        ax.set_title(f'질소·인 유출 위험 지역 지도\n({timestamp})', fontsize=18, fontweight='bold', pad=20)
        
        # 축 제거
        ax.set_axis_off()
        
        # 여백 제거
        plt.tight_layout(pad=0)
        
        # 파일 저장
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(self.output_dir, f'integrated_water_quality_map_{timestamp}.png')
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight', pad_inches=0.1, facecolor='white')
        plt.close()
        
        return output_file
    
    def create_basic_map(self, output_file='map.png'):
        """
        기본 지도 생성 (기존 함수 호환성 유지)
        """
        print("기본 지도 생성 중...")
        
        # 전라남도 shapefile 사용
        shp_path = "data/shapefiles/zeonam/LARD_ADM_SECT_SGG_46_202505.shp"
        
        if not os.path.exists(shp_path):
            print(f"Shapefile을 찾을 수 없습니다: {shp_path}")
            return None
        
        gdf = gpd.read_file(shp_path)
        
        # CRS를 WGS84로 변환
        if gdf.crs is not None and "4326" not in str(gdf.crs):
            gdf = gdf.to_crs(epsg=4326)
        
        # 지오메트리 간소화
        gdf['geometry'] = gdf['geometry'].simplify(0.01, preserve_topology=False)
        
        # 랜덤 색상 할당
        np.random.seed(42)
        gdf['color_level'] = np.random.randint(1, 6, size=len(gdf))
        
        # 색상 매핑
        colors = ['#2E8B57', '#90EE90', '#FFFF00', '#FFA500', '#FF0000']
        cmap = plt.cm.colors.LinearSegmentedColormap.from_list('color_cmap', colors, N=5)
        
        # 지도 생성
        fig, ax = plt.subplots(1, 1, figsize=(8, 10))
        
        gdf.plot(
            column='color_level',
            cmap=cmap,
            edgecolor='black',
            linewidth=0.5,
            ax=ax,
            legend=False
        )
        
        # 지역명 추가
        for idx, row in gdf.iterrows():
            try:
                centroid = row['geometry'].centroid
                sgg_name = row['SGG_NM']
                
                if sgg_name.startswith('전라남도 '):
                    display_name = sgg_name.replace('전라남도 ', '')
                else:
                    display_name = sgg_name
                
                ax.annotate(
                    display_name,
                    xy=(centroid.x, centroid.y),
                    xytext=(0, 0),
                    textcoords='offset points',
                    ha='center',
                    va='center',
                    fontsize=8,
                    fontweight='bold',
                    color='black',
                    bbox=dict(boxstyle='round,pad=0.1', facecolor='white', alpha=0.9, edgecolor='black', linewidth=0.5)
                )
            except Exception as e:
                continue
        
        # 범례 추가
        legend_elements = [
            plt.Rectangle((0,0),1,1, facecolor='#2E8B57', edgecolor='black', linewidth=0.5, label='1단계'),
            plt.Rectangle((0,0),1,1, facecolor='#90EE90', edgecolor='black', linewidth=0.5, label='2단계'),
            plt.Rectangle((0,0),1,1, facecolor='#FFFF00', edgecolor='black', linewidth=0.5, label='3단계'),
            plt.Rectangle((0,0),1,1, facecolor='#FFA500', edgecolor='black', linewidth=0.5, label='4단계'),
            plt.Rectangle((0,0),1,1, facecolor='#FF0000', edgecolor='black', linewidth=0.5, label='5단계')
        ]
        
        ax.legend(handles=legend_elements, loc='upper right', fontsize=10, title='경보 단계', title_fontsize=12)
        ax.set_title('질소·인 유출 위험 지역 지도', fontsize=16, fontweight='bold')
        ax.set_axis_off()
        
        plt.tight_layout(pad=0)
        plt.savefig(output_file, dpi=300, bbox_inches='tight', pad_inches=0, facecolor='white')
        plt.close()
        
        print(f"기본 지도가 '{output_file}'로 저장되었습니다.")
        return gdf

def create_basic_map(output_file='map.png'):
    """
    기본 지도 생성 함수 (기존 호환성 유지)
    """
    generator = MapGenerator()
    return generator.create_basic_map(output_file)

if __name__ == "__main__":
    # 테스트: 기본 지도 생성
    create_basic_map()
    
    # 테스트: 통합 지도 생성 (데이터가 있는 경우)
    generator = MapGenerator()
    # generator.create_integrated_map(None)  # 실제 데이터로 테스트 