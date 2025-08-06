# 🚀 빠른 배포 가이드

## 📋 배포 준비 완료 ✅

모든 필수 파일이 준비되었습니다:
- ✅ `integrated_water_quality_map.png` (메인 지도)
- ✅ `index.html` (웹페이지)
- ✅ `README.md` (프로젝트 설명)
- ✅ `.gitignore` (Git 설정)
- ✅ `deploy.sh` / `deploy.bat` (배포 스크립트)

## 🔧 1단계: GitHub 저장소 생성

1. GitHub에서 새 저장소 생성
2. 저장소 이름: `water-quality-system` (또는 원하는 이름)
3. Public으로 설정

## 🚀 2단계: 로컬에서 업로드

### Windows 사용자:
```cmd
deploy.bat
```

### Mac/Linux 사용자:
```bash
chmod +x deploy.sh
./deploy.sh
```

### 수동 업로드:
```bash
git init
git add .
git commit -m "Initial commit: 전국 수질 평가 시스템"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

## 🌐 3단계: GitHub Pages 활성화

1. GitHub 저장소 페이지로 이동
2. **Settings** 탭 클릭
3. **Pages** 섹션 찾기
4. **Source**: "Deploy from a branch" 선택
5. **Branch**: "main" 선택
6. **Save** 클릭

## 🎯 4단계: Render 배포 (선택사항)

1. [Render.com](https://render.com) 가입
2. **New +** → **Static Site**
3. GitHub 저장소 연결
4. **Build Command**: (비워두기)
5. **Publish Directory**: `.`
6. **Create Static Site** 클릭

## 📊 배포 완료 후

### GitHub Pages URL:
```
https://YOUR_USERNAME.github.io/YOUR_REPO_NAME
```

### Render URL:
```
https://YOUR_SITE_NAME.onrender.com
```

## 🔄 업데이트 방법

새로운 지도 이미지가 생성되면:
```bash
# 새 이미지 생성
python integrated_water_quality_map.py

# 업로드
git add integrated_water_quality_map.png
git commit -m "Update water quality map"
git push origin main
```

## 🛠️ 문제 해결

### 이미지가 보이지 않는 경우:
- 이미지 파일명 확인: `integrated_water_quality_map.png`
- 이미지 경로 확인: `index.html`에서 `src="integrated_water_quality_map.png"`

### 페이지가 로드되지 않는 경우:
- GitHub Pages 설정 확인
- 브랜치 설정 확인 (main)
- 배포 상태 확인 (Settings > Pages)

## 📞 지원

- 📖 자세한 가이드: `DEPLOYMENT_GUIDE.md`
- 🐛 문제 해결: GitHub Issues
- 📧 문의: GitHub 저장소 Discussions

---

**🎉 축하합니다!** 전국 수질 평가 시스템이 성공적으로 배포되었습니다. 