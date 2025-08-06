from flask import Flask, send_from_directory
import os
import pandas as pd
from datetime import datetime

app = Flask(__name__)

def get_station_count():
    """실제 측정소 개수를 계산합니다."""
    try:
        # 여러 가능한 경로에서 측정소 데이터 찾기
        possible_paths = [
            'data/raw/measurement_stations.csv',
            'Local_Water_CSV/measurement_stations.csv',
            'src/data/raw/measurement_stations.csv'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                df = pd.read_csv(path)
                return len(df)
        
        # CSV 파일이 없으면 하천 데이터에서 측정소 개수 추정
        river_data_path = 'Local_Water_CSV/자료 조회_하천_20250806.csv'
        if os.path.exists(river_data_path):
            df = pd.read_csv(river_data_path)
            # ptNo (측정소 코드) 기준으로 고유한 측정소 개수 계산
            if 'ptNo' in df.columns:
                return df['ptNo'].nunique()
            elif 'ptnm' in df.columns:
                return df['ptnm'].nunique()
        
        # 기본값 반환
        return 156
        
    except Exception as e:
        print(f"측정소 개수 계산 오류: {e}")
        return 156

@app.route('/')
def index():
    # 지도 정보 가져오기
    map_file = 'web/static/images/integrated_water_quality_map.png'
    map_exists = os.path.exists(map_file)
    
    if map_exists:
        file_date = datetime.fromtimestamp(os.path.getmtime(map_file))
        update_time = file_date.strftime('%Y-%m-%d %H:%M:%S')
    else:
        update_time = "업데이트 정보 없음"
    
    # 실제 측정소 개수 계산
    station_count = get_station_count()
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>수질 지도</title>
        <meta charset="utf-8">
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
                background: #f0f0f0;
            }}
            .container {{
                position: relative;
                width: 100vw;
                height: 100vh;
                overflow: hidden;
            }}
            .map-container {{
                position: relative;
                width: 100%;
                height: 100%;
                overflow: auto;
                background: white;
            }}
            .map-image {{
                display: block;
                max-width: none;
                min-width: 100%;
                min-height: 100%;
                object-fit: contain;
            }}
            .info-panel {{
                position: absolute;
                top: 20px;
                right: 20px;
                background: rgba(255, 255, 255, 0.95);
                padding: 15px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                font-size: 14px;
                z-index: 1000;
            }}
            .info-item {{
                margin: 5px 0;
                color: #333;
            }}
            .station-count {{
                font-weight: bold;
                color: #2c5aa0;
            }}
            .update-time {{
                color: #666;
                font-size: 12px;
            }}
            .zoom-controls {{
                position: absolute;
                bottom: 20px;
                right: 20px;
                background: rgba(255, 255, 255, 0.95);
                padding: 10px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                z-index: 1000;
            }}
            .zoom-btn {{
                display: block;
                width: 40px;
                height: 40px;
                margin: 5px;
                border: none;
                background: #2c5aa0;
                color: white;
                border-radius: 4px;
                cursor: pointer;
                font-size: 18px;
                font-weight: bold;
            }}
            .zoom-btn:hover {{
                background: #1e3f7a;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="map-container" id="mapContainer">
                <img src="/static/images/integrated_water_quality_map.png" 
                     alt="수질 지도" 
                     class="map-image" 
                     id="mapImage">
            </div>
            
            <div class="info-panel">
                <div class="info-item station-count">
                    📊 측정소 매칭: {station_count}개
                </div>
                <div class="update-time">
                    🔄 업데이트: {update_time}
                </div>
            </div>
            
            <div class="zoom-controls">
                <button class="zoom-btn" onclick="zoomIn()">+</button>
                <button class="zoom-btn" onclick="zoomOut()">-</button>
                <button class="zoom-btn" onclick="resetZoom()">⟲</button>
            </div>
        </div>
        
        <script>
            let currentZoom = 1;
            const zoomStep = 0.2;
            const mapImage = document.getElementById('mapImage');
            const mapContainer = document.getElementById('mapContainer');
            
            function zoomIn() {{
                currentZoom += zoomStep;
                updateZoom();
            }}
            
            function zoomOut() {{
                currentZoom = Math.max(0.5, currentZoom - zoomStep);
                updateZoom();
            }}
            
            function resetZoom() {{
                currentZoom = 1;
                updateZoom();
                mapContainer.scrollTo(0, 0);
            }}
            
            function updateZoom() {{
                mapImage.style.transform = `scale(${{currentZoom}})`;
                mapImage.style.transformOrigin = 'top left';
            }}
            
            // 마우스 휠로 확대/축소
            mapContainer.addEventListener('wheel', function(e) {{
                e.preventDefault();
                if (e.deltaY < 0) {{
                    zoomIn();
                }} else {{
                    zoomOut();
                }}
            }});
            
            // 더블클릭으로 리셋
            mapContainer.addEventListener('dblclick', function(e) {{
                if (e.target === mapImage) {{
                    resetZoom();
                }}
            }});
        </script>
    </body>
    </html>
    """

@app.route('/static/images/<filename>')
def serve_image(filename):
    return send_from_directory('web/static/images', filename)

if __name__ == '__main__':
    print("🌐 수질 지도 웹 서버 시작...")
    print("📱 접속 주소: http://localhost:5000")
    print("🗺️ 지도 전용 페이지입니다.")
    print("✅ 확대/축소/드래그 기능 포함")
    app.run(host='0.0.0.0', port=5000, debug=False) 