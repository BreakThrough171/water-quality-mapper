from flask import Flask, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <h1>수질 지도 웹 서버 테스트</h1>
    <p>서버가 정상적으로 실행 중입니다!</p>
    <p><a href="/gallery">이미지 갤러리</a></p>
    <p><a href="/static/images/integrated_water_quality_map.png">수질 지도 직접 보기</a></p>
    """

@app.route('/gallery')
def gallery():
    image_dir = 'web/static/images'
    images = []
    
    if os.path.exists(image_dir):
        for filename in os.listdir(image_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                images.append(filename)
    
    html = "<h1>이미지 갤러리</h1>"
    for img in images:
        html += f'<p><a href="/static/images/{img}">{img}</a></p>'
    
    return html

@app.route('/static/images/<filename>')
def serve_image(filename):
    return send_from_directory('web/static/images', filename)

if __name__ == '__main__':
    print("🌐 간단한 테스트 서버 시작...")
    print("📱 접속 주소: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False) 