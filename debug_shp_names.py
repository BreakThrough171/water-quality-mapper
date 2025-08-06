import geopandas as gpd
import pandas as pd

def debug_shp_names():
    """SHP 파일의 실제 시군구명 확인"""
    print("🔍 SHP 파일 시군구명 디버깅")
    print("=" * 50)
    
    # 모든 지역의 SHP 파일 경로
    shp_paths = [
        "행정구역SHP지도/LARD_ADM_SECT_SGG_서울/LARD_ADM_SECT_SGG_11_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_부산/LARD_ADM_SECT_SGG_26_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_대구/LARD_ADM_SECT_SGG_27_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_인천/LARD_ADM_SECT_SGG_28_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_광주/LARD_ADM_SECT_SGG_29_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_대전/LARD_ADM_SECT_SGG_30_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_울산/LARD_ADM_SECT_SGG_31_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_세종/LARD_ADM_SECT_SGG_36_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_경기/LARD_ADM_SECT_SGG_41_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_충북/LARD_ADM_SECT_SGG_43_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_충남/LARD_ADM_SECT_SGG_44_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_전북특별자치도/LARD_ADM_SECT_SGG_52_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_전남/LARD_ADM_SECT_SGG_46_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_경북/LARD_ADM_SECT_SGG_47_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_경남/LARD_ADM_SECT_SGG_48_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_제주/LARD_ADM_SECT_SGG_50_202505.shp",
        "행정구역SHP지도/LARD_ADM_SECT_SGG_강원특별자치도/LARD_ADM_SECT_SGG_51_202505.shp"
    ]
    
    all_sgg_names = []
    
    for i, shp_path in enumerate(shp_paths):
        try:
            print(f"\n📁 {shp_path}")
            gdf = gpd.read_file(shp_path)
            
            # 컬럼명 확인
            print(f"컬럼명: {list(gdf.columns)}")
            
            # 시군구명 컬럼 찾기
            sgg_column = None
            for col in gdf.columns:
                if 'SGG' in col.upper() or 'NM' in col.upper():
                    sgg_column = col
                    break
            
            if sgg_column:
                print(f"시군구명 컬럼: {sgg_column}")
                sgg_names = gdf[sgg_column].unique()
                print(f"시군구 목록 ({len(sgg_names)}개):")
                for name in sorted(sgg_names):
                    print(f"  - {name}")
                    all_sgg_names.append(name)
            else:
                print("❌ 시군구명 컬럼을 찾을 수 없음")
                print(f"사용 가능한 컬럼: {list(gdf.columns)}")
                
        except Exception as e:
            print(f"❌ 오류: {e}")
            continue
    
    print(f"\n📊 전체 시군구 수: {len(all_sgg_names)}")
    print("📋 전체 시군구 목록:")
    for i, name in enumerate(sorted(all_sgg_names), 1):
        print(f"{i:3d}. {name}")

if __name__ == "__main__":
    debug_shp_names() 