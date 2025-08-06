import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def create_basic_map(output_file='map.png'):
    """
    백지도 위에 각 군 이름, 경계, 색을 나타내는 기본 지도를 생성합니다.
    """
    
    # SHP 파일 로드
    shp_path = "data/shapefiles/zeonam/LARD_ADM_SECT_SGG_46_202505.shp"
    gdf = gpd.read_file(shp_path)
    
    # CRS를 WGS84 (EPSG:4326)로 변환
    print(f"원본 CRS: {gdf.crs}")
    if gdf.crs is not None and "4326" not in str(gdf.crs):
        print("CRS를 WGS84로 변환 중...")
        gdf = gdf.to_crs(epsg=4326)
        print(f"변환된 CRS: {gdf.crs}")
    
    # 전남 지역 데이터
    jeonnam_gdf = gdf.copy()
    
    # 지오메트리 간소화 (성능 향상)
    print("지오메트리 간소화 중...")
    jeonnam_gdf['geometry'] = jeonnam_gdf['geometry'].simplify(0.01, preserve_topology=False)
    
    # 각 지역에 랜덤 색상 할당 (1~5단계)
    np.random.seed(42)  # 재현성을 위한 시드 설정
    jeonnam_gdf['color_level'] = np.random.randint(1, 6, size=len(jeonnam_gdf))
    
    # 5단계 컬러맵 생성 (초록-노랑-빨강)
    colors = ['#2E8B57', '#90EE90', '#FFFF00', '#FFA500', '#FF0000']  # 초록-연초록-노랑-주황-빨강
    n_bins = 5
    cmap = plt.cm.colors.LinearSegmentedColormap.from_list('color_cmap', colors, N=n_bins)
    
    # 지도 생성
    fig, ax = plt.subplots(1, 1, figsize=(8, 10))
    
    # 지도 그리기
    jeonnam_gdf.plot(
        column='color_level',
        cmap=cmap,
        edgecolor='black',
        linewidth=0.5,
        ax=ax,
        legend=False
    )
    
    # 각 지역 이름 추가
    print("지역 이름 추가 중...")
    for idx, row in jeonnam_gdf.iterrows():
        try:
            # 각 지역의 중심점 계산
            centroid = row['geometry'].centroid
            sgg_name = row['SGG_NM']
            
            # 지역 이름에서 '전라남도 ' 부분 제거하여 간단하게 표시
            if sgg_name.startswith('전라남도 '):
                display_name = sgg_name.replace('전라남도 ', '')
            else:
                display_name = sgg_name
            
            # 텍스트 추가 (검은색 글자 + 흰색 배경)
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
            print(f"지역 이름 추가 중 오류 ({sgg_name}): {e}")
            continue
    
    # 색상 범례 추가
    legend_elements = [
        plt.Rectangle((0,0),1,1, facecolor='#FF0000', edgecolor='black', linewidth=0.5, label='5단계'),
        plt.Rectangle((0,0),1,1, facecolor='#FFA500', edgecolor='black', linewidth=0.5, label='4단계'),
        plt.Rectangle((0,0),1,1, facecolor='#FFFF00', edgecolor='black', linewidth=0.5, label='3단계'),
        plt.Rectangle((0,0),1,1, facecolor='#90EE90', edgecolor='black', linewidth=0.5, label='2단계'),
        plt.Rectangle((0,0),1,1, facecolor='#2E8B57', edgecolor='black', linewidth=0.5, label='1단계')
    ]
    
    ax.legend(handles=legend_elements, loc='upper right', fontsize=8, title='색상 단계', title_fontsize=9)
    
    # 제목 설정
    ax.set_title('전라남도 지역 지도', fontsize=14, fontweight='bold')
    
    # 축 제거
    ax.set_axis_off()
    
    # 여백 제거
    plt.tight_layout(pad=0)
    
    # 지도 저장
    print("지도 저장 중...")
    plt.savefig(output_file, dpi=300, bbox_inches='tight', pad_inches=0, facecolor='white')
    plt.close()
    
    print(f"지도가 '{output_file}'로 저장되었습니다.")
    print(f"처리된 지역 수: {len(jeonnam_gdf)}")
    print("지역별 색상 단계:")
    for idx, row in jeonnam_gdf.iterrows():
        print(f"  {row['SGG_NM']}: {row['color_level']}단계")
    
    return jeonnam_gdf

if __name__ == "__main__":
    # 기본 지도 생성
    create_basic_map() 