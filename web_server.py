from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash
import os
from datetime import datetime
import shutil

# 디버그 정보 출력
print(f"현재 작업 디렉토리: {os.getcwd()}")
print(f"템플릿 폴더 경로: {os.path.abspath('web/templates')}")
print(f"템플릿 폴더 존재 여부: {os.path.exists('web/templates')}")
print(f"index.html 존재 여부: {os.path.exists('web/templates/index.html')}")

# Render 환경에서의 경로 설정
template_dir = os.path.abspath('web/templates')
static_dir = os.path.abspath('web/static')

app = Flask(__name__, 
           template_folder=template_dir,
           static_folder=static_dir)
app.secret_key = 'water_quality_monitor_2024'  # 플래시 메시지용

# 이미지 업로드 설정
UPLOAD_FOLDER = os.path.join(static_dir, 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_latest_map_info():
    """최신 지도 정보를 가져옵니다."""
    try:
        web_images_dir = UPLOAD_FOLDER
        if not os.path.exists(web_images_dir):
            return None
        
        # integrated_water_quality_map.png 파일 찾기
        latest_map = os.path.join(web_images_dir, 'integrated_water_quality_map.png')
        
        if os.path.exists(latest_map):
            file_size = os.path.getsize(latest_map)
            file_date = datetime.fromtimestamp(os.path.getmtime(latest_map))
            
            return {
                'filename': 'integrated_water_quality_map.png',
                'url': '/static/images/integrated_water_quality_map.png',
                'size': f'{file_size / 1024 / 1024:.1f} MB',
                'date': file_date.strftime('%Y-%m-%d %H:%M:%S'),
                'exists': True
            }
        else:
            return {'exists': False}
            
    except Exception as e:
        print(f"지도 정보 가져오기 오류: {e}")
        return {'exists': False}

@app.route('/')
def index():
    """메인 페이지"""
    # 최신 지도 정보 가져오기
    latest_map_info = get_latest_map_info()
    return render_template('index.html', map_info=latest_map_info)

@app.route('/map')
def map_view():
    """수질 지도 페이지"""
    return render_template('map.html')

@app.route('/dashboard')
def dashboard():
    """대시보드 페이지"""
    return render_template('dashboard.html')

@app.route('/gallery')
def gallery():
    """이미지 갤러리 페이지"""
    # 이미지 파일 목록 가져오기
    image_dir = UPLOAD_FOLDER
    images = []
    
    if os.path.exists(image_dir):
        for filename in os.listdir(image_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                # 파일 정보 가져오기
                file_path = os.path.join(image_dir, filename)
                file_size = os.path.getsize(file_path)
                file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                images.append({
                    'filename': filename,
                    'url': f'/static/images/{filename}',
                    'size': f'{file_size / 1024 / 1024:.1f} MB',
                    'date': file_date.strftime('%Y-%m-%d %H:%M:%S')
                })
    
    # 날짜순으로 정렬 (최신순)
    images.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('gallery.html', images=images)

@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    """이미지 업로드 페이지"""
    if request.method == 'POST':
        # 파일이 없으면 에러
        if 'file' not in request.files:
            flash('파일이 선택되지 않았습니다.', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # 파일명이 없으면 에러
        if file.filename == '':
            flash('파일이 선택되지 않았습니다.', 'error')
            return redirect(request.url)
        
        # 파일 확장자 확인
        if file and allowed_file(file.filename):
            # 안전한 파일명으로 저장
            filename = file.filename
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            
            # 파일 저장
            file.save(file_path)
            flash(f'이미지 {filename}이 성공적으로 업로드되었습니다.', 'success')
            return redirect(url_for('gallery'))
        else:
            flash('허용되지 않는 파일 형식입니다. PNG, JPG, JPEG, GIF만 업로드 가능합니다.', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/static/images/<filename>')
def serve_image(filename):
    """이미지 파일 서빙"""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/api/status')
def api_status():
    """API 상태 확인"""
    return {
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'message': '수질 모니터링 시스템이 정상적으로 실행 중입니다.',
        'images_count': len([f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))])
    }

@app.route('/api/images')
def api_images():
    """이미지 목록 API"""
    image_dir = UPLOAD_FOLDER
    images = []
    
    if os.path.exists(image_dir):
        for filename in os.listdir(image_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                file_path = os.path.join(image_dir, filename)
                file_size = os.path.getsize(file_path)
                file_date = datetime.fromtimestamp(os.path.getmtime(file_path))
                
                images.append({
                    'filename': filename,
                    'url': f'/static/images/{filename}',
                    'size': file_size,
                    'size_mb': f'{file_size / 1024 / 1024:.1f}',
                    'date': file_date.isoformat(),
                    'date_formatted': file_date.strftime('%Y-%m-%d %H:%M:%S')
                })
    
    return {'images': images}

if __name__ == '__main__':
    print("🌐 수질 지도 웹 서버 시작 중...")
    
    # Render 환경에서 포트 설정
    port = int(os.environ.get('PORT', 5000))
    
    print(f"📱 접속 주소: http://localhost:{port}")
    print("🗺️ 지도 보기: http://localhost:5000/map")
    print("📊 대시보드: http://localhost:5000/dashboard")
    print("🖼️ 이미지 갤러리: http://localhost:5000/gallery")
    print("📤 이미지 업로드: http://localhost:5000/upload")
    print("=" * 50)
    
    # 개발 모드로 실행 (외부 접속 허용)
    app.run(host='0.0.0.0', port=port, debug=False) 