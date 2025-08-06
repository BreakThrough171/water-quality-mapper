import http.server
import socketserver
import os
import webbrowser
from urllib.parse import urlparse

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # URL 파싱
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # 루트 경로 처리
        if path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            # HTML 응답 생성
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>수질 지도 서버</title>
                <meta charset="utf-8">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .image-link { display: block; margin: 10px 0; padding: 10px; 
                                background: #f0f0f0; text-decoration: none; color: #333; }
                    .image-link:hover { background: #e0e0e0; }
                    img { max-width: 100%; height: auto; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🌊 수질 지도 웹 서버</h1>
                    <p>서버가 정상적으로 실행 중입니다!</p>
                    
                    <h2>📁 이미지 파일 목록</h2>
            """
            
            # 이미지 파일 목록 생성
            image_dir = 'web/static/images'
            if os.path.exists(image_dir):
                for filename in os.listdir(image_dir):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                        html += f'<a href="/web/static/images/{filename}" class="image-link">📷 {filename}</a>'
            
            html += """
                </div>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode('utf-8'))
            return
        
        # 정적 파일 서빙
        return super().do_GET()

def main():
    PORT = 8080
    
    # 현재 디렉토리를 웹 루트로 설정
    os.chdir('.')
    
    with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
        print(f"🌐 수질 지도 웹 서버 시작 중...")
        print(f"📱 접속 주소: http://localhost:{PORT}")
        print(f"🗺️ 수질 지도: http://localhost:{PORT}/web/static/images/integrated_water_quality_map.png")
        print("=" * 50)
        
        # 브라우저 자동 열기
        try:
            webbrowser.open(f'http://localhost:{PORT}')
        except:
            pass
        
        httpd.serve_forever()

if __name__ == '__main__':
    main() 