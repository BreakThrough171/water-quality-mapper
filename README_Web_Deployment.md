# 🌐 수질 모니터링 시스템 웹 배포 가이드

## 📋 개요
생성된 수질 지도를 외부인들도 볼 수 있도록 웹에 배포하는 방법을 안내합니다.

## 🚀 현재 상태
- ✅ Flask 웹 서버 생성 완료
- ✅ 메인 페이지, 지도 페이지, 대시보드 페이지 생성 완료
- ✅ 반응형 디자인 적용 완료
- ✅ 한글 지원 완료

## 🌍 웹 접속 방법

### 1. 로컬 접속 (개발용)
```bash
# 웹 서버 실행
python web_server.py

# 접속 주소
http://localhost:5000
http://127.0.0.1:5000
```

### 2. 외부 접속 (같은 네트워크)
```bash
# 웹 서버가 실행 중인 컴퓨터의 IP 주소 확인
ipconfig  # Windows
ifconfig  # Mac/Linux

# 접속 주소 (예시)
http://192.168.1.100:5000
```

### 3. 인터넷 공개 배포

#### 방법 1: ngrok 사용 (추천)
```bash
# 1. ngrok 설치
# https://ngrok.com/ 에서 다운로드

# 2. ngrok 실행
ngrok http 5000

# 3. 제공되는 공개 URL 사용
# 예: https://abc123.ngrok.io
```

#### 방법 2: Heroku 배포
```bash
# 1. Heroku CLI 설치
# https://devcenter.heroku.com/articles/heroku-cli

# 2. Heroku 앱 생성
heroku create water-quality-monitor

# 3. 배포
git add .
git commit -m "Initial deployment"
git push heroku main
```

#### 방법 3: PythonAnywhere 배포
1. https://www.pythonanywhere.com/ 에서 계정 생성
2. Files 탭에서 프로젝트 파일 업로드
3. Web 탭에서 Flask 앱 설정
4. 도메인 제공 (예: username.pythonanywhere.com)

## 📱 웹 페이지 구성

### 🏠 메인 페이지 (/)
- 시스템 소개
- 네비게이션 카드
- 실시간 상태 확인

### 🗺️ 수질 지도 페이지 (/map)
- 전국 행정구역별 수질 평가 지도
- 경보 단계별 색상 범례
- 지도 다운로드 기능
- 상세 정보 제공

### 📊 대시보드 페이지 (/dashboard)
- 실시간 통계 데이터
- 경보 단계별 분포 차트
- 상세 데이터 테이블
- 데이터 새로고침 기능

### 🔍 API 상태 페이지 (/api/status)
- 시스템 상태 확인
- JSON 형태의 API 응답

## 🔧 설정 파일

### web_server.py
```python
# 외부 접속 허용 설정
app.run(host='0.0.0.0', port=5000, debug=True)

# 보안을 위해 프로덕션에서는 debug=False로 설정
```

### 환경 변수 설정
```bash
# Windows
set FLASK_ENV=production
set FLASK_DEBUG=0

# Mac/Linux
export FLASK_ENV=production
export FLASK_DEBUG=0
```

## 🔒 보안 고려사항

### 1. 프로덕션 환경 설정
```python
# web_server.py 수정
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

### 2. 방화벽 설정
- 포트 5000 열기
- 필요한 경우 HTTPS 설정

### 3. 접근 제어
```python
# 필요한 경우 인증 추가
from functools import wraps
from flask import request, Response

def check_auth(username, password):
    return username == 'admin' and password == 'password'

def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated
```

## 📊 모니터링 및 로그

### 로그 설정
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/status')
def api_status():
    logger.info('API status requested')
    return {
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'visitors': get_visitor_count()
    }
```

### 접속 통계
```python
from collections import defaultdict
visitor_stats = defaultdict(int)

@app.before_request
def log_request():
    visitor_stats[request.remote_addr] += 1
    logger.info(f'Request from {request.remote_addr}: {request.path}')
```

## 🚀 성능 최적화

### 1. 이미지 최적화
```python
# 이미지 압축 및 캐싱
from PIL import Image
import io

def optimize_image(image_path):
    img = Image.open(image_path)
    img_io = io.BytesIO()
    img.save(img_io, 'PNG', optimize=True)
    return img_io.getvalue()
```

### 2. 정적 파일 캐싱
```python
# Flask-Caching 사용
from flask_caching import Cache

cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

@app.route('/static/images/<filename>')
@cache.cached(timeout=3600)  # 1시간 캐시
def serve_image(filename):
    return send_from_directory('web/static/images', filename)
```

## 📞 지원 및 문의

### 문제 해결
1. 포트 충돌: `netstat -ano | findstr :5000`
2. 방화벽 설정 확인
3. 로그 확인: `python web_server.py > server.log 2>&1`

### 추가 기능 요청
- 실시간 데이터 업데이트
- 사용자 인증 시스템
- 데이터베이스 연동
- 모바일 앱 연동

## 🎯 다음 단계

1. **도메인 설정**: 고정 도메인 주소 확보
2. **SSL 인증서**: HTTPS 보안 연결 설정
3. **데이터베이스**: 사용자 데이터 및 로그 저장
4. **실시간 업데이트**: WebSocket을 통한 실시간 데이터 전송
5. **모바일 최적화**: PWA(Progressive Web App) 구현

---

**🌊 수질 모니터링 시스템이 성공적으로 웹에 배포되었습니다!**

외부인들이 `http://your-ip:5000` 또는 ngrok URL을 통해 접속하여 수질 지도를 확인할 수 있습니다. 