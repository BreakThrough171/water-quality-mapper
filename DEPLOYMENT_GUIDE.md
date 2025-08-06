# 🚀 GitHub 배포 가이드

이 가이드는 전국 수질 평가 시스템을 GitHub에 업로드하고 Render의 Static Site를 이용해서 배포하는 방법을 설명합니다.

## 📋 사전 준비

### 1. GitHub 계정 및 저장소 준비
- GitHub 계정이 필요합니다
- 새로운 저장소를 생성하거나 기존 저장소를 사용합니다

### 2. 필수 파일 확인
배포 전에 다음 파일들이 있는지 확인하세요:
- `integrated_water_quality_map.png` (메인 지도 이미지)
- `index.html` (메인 웹페이지)
- `README.md` (프로젝트 설명)
- `.gitignore` (Git 제외 파일 설정)

## 🔧 GitHub 업로드 단계

### 1단계: Git 초기화 및 파일 추가

```bash
# Git 저장소 초기화
git init

# 모든 파일 추가 (제외 파일 제외)
git add .

# 첫 번째 커밋
git commit -m "Initial commit: 전국 수질 평가 시스템"

# GitHub 원격 저장소 연결 (YOUR_USERNAME과 YOUR_REPO_NAME을 실제 값으로 변경)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# 메인 브랜치로 푸시
git branch -M main
git push -u origin main
```

### 2단계: GitHub Pages 설정

1. **GitHub 저장소 페이지로 이동**
2. **Settings 탭 클릭**
3. **Pages 섹션 찾기**
4. **Source를 "Deploy from a branch"로 설정**
5. **Branch를 "main"으로 선택**
6. **Save 클릭**

### 3단계: 배포 확인

- GitHub Pages가 활성화되면 `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME`에서 접근 가능
- 배포에는 몇 분 정도 소요될 수 있습니다

## 🌐 Render Static Site 배포

### 1단계: Render 계정 생성
- [Render.com](https://render.com)에 가입
- GitHub 계정으로 로그인

### 2단계: 새 Static Site 생성

1. **Render 대시보드에서 "New +" 클릭**
2. **"Static Site" 선택**
3. **GitHub 저장소 연결**
4. **저장소 선택**

### 3단계: 배포 설정

**Build Command**: (비워두기)
```
(비워두기)
```

**Publish Directory**: 
```
.
```

**Environment Variables**: (필요시)
```
NODE_ENV=production
```

### 4단계: 배포 실행

1. **"Create Static Site" 클릭**
2. **배포 진행 상황 모니터링**
3. **배포 완료 후 제공되는 URL 확인**

## 📁 배포용 파일 구조

```
your-repo/
├── index.html                    # 메인 웹페이지
├── integrated_water_quality_map.png  # 메인 지도 이미지
├── README.md                     # 프로젝트 설명
├── .gitignore                    # Git 제외 파일
├── DEPLOYMENT_GUIDE.md          # 이 가이드
└── requirements.txt              # Python 의존성 (참고용)
```

## 🔍 배포 확인 사항

### 1. 이미지 파일 확인
- `integrated_water_quality_map.png` 파일이 저장소에 포함되어 있는지 확인
- 이미지 파일 크기가 적절한지 확인 (너무 크면 로딩이 느려질 수 있음)

### 2. HTML 파일 확인
- `index.html` 파일이 올바르게 작성되었는지 확인
- 이미지 경로가 정확한지 확인

### 3. 반응형 디자인 확인
- 모바일에서도 잘 보이는지 확인
- 다양한 화면 크기에서 테스트

## 🛠️ 문제 해결

### 이미지가 보이지 않는 경우
1. 이미지 파일명 확인
2. 이미지 경로 확인
3. 이미지 파일이 Git에 포함되었는지 확인

### 페이지가 로드되지 않는 경우
1. GitHub Pages 설정 확인
2. 브랜치 설정 확인
3. 배포 상태 확인

### Render 배포 실패 시
1. Build Command 확인
2. Publish Directory 확인
3. 로그 확인

## 📊 성능 최적화

### 이미지 최적화
```bash
# 이미지 압축 (선택사항)
# 온라인 도구나 이미지 편집 프로그램 사용
```

### 파일 크기 최적화
- 불필요한 파일 제거
- 큰 파일은 Git LFS 사용 고려

## 🔄 업데이트 방법

### 새로운 지도 이미지 업로드 시
```bash
# 새 이미지 생성 후
git add integrated_water_quality_map.png
git commit -m "Update water quality map"
git push origin main
```

### 웹페이지 수정 시
```bash
# HTML 파일 수정 후
git add index.html
git commit -m "Update website content"
git push origin main
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. GitHub 저장소 설정
2. Render 배포 로그
3. 브라우저 개발자 도구 콘솔

## 🎯 배포 완료 후

배포가 완료되면 다음 URL에서 접근 가능합니다:
- **GitHub Pages**: `https://YOUR_USERNAME.github.io/YOUR_REPO_NAME`
- **Render**: `https://YOUR_SITE_NAME.onrender.com`

---

**참고**: 이 가이드는 기본적인 배포 방법을 설명합니다. 필요에 따라 추가 설정이나 최적화를 진행하세요. 