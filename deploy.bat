@echo off
chcp 65001 >nul

REM 🚀 GitHub 배포 스크립트 (Windows)
REM 전국 수질 평가 시스템을 GitHub에 업로드하는 스크립트

echo 🌊 전국 수질 평가 시스템 GitHub 배포 시작
echo ==========================================

REM 1. 필수 파일 확인
echo 📋 필수 파일 확인 중...

if not exist "integrated_water_quality_map.png" (
    echo ❌ 오류: integrated_water_quality_map.png 파일이 없습니다!
    echo    먼저 지도를 생성해주세요: python integrated_water_quality_map.py
    pause
    exit /b 1
)

if not exist "index.html" (
    echo ❌ 오류: index.html 파일이 없습니다!
    pause
    exit /b 1
)

if not exist "README.md" (
    echo ❌ 오류: README.md 파일이 없습니다!
    pause
    exit /b 1
)

echo ✅ 모든 필수 파일이 확인되었습니다.

REM 2. Git 초기화 (이미 초기화된 경우 무시)
if not exist ".git" (
    echo 🔧 Git 저장소 초기화 중...
    git init
    echo ✅ Git 저장소가 초기화되었습니다.
) else (
    echo ℹ️  Git 저장소가 이미 초기화되어 있습니다.
)

REM 3. 파일 추가
echo 📁 파일 추가 중...
git add .

REM 4. 커밋
echo 💾 커밋 중...
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YY=%dt:~2,2%" & set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"
set "datestamp=%YYYY%-%MM%-%DD% %HH%:%Min%:%Sec%"

git commit -m "Update: 전국 수질 평가 시스템 - %datestamp%"

REM 5. 원격 저장소 연결 확인
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo ⚠️  원격 저장소가 설정되지 않았습니다.
    echo 다음 명령어로 원격 저장소를 설정해주세요:
    echo git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
    echo.
    echo 설정 후 다음 명령어로 푸시하세요:
    echo git branch -M main
    echo git push -u origin main
) else (
    echo 🚀 원격 저장소로 푸시 중...
    git branch -M main
    git push origin main
    echo ✅ 푸시가 완료되었습니다!
)

echo.
echo 🎉 배포 준비가 완료되었습니다!
echo.
echo 📋 다음 단계:
echo 1. GitHub 저장소에서 Settings ^> Pages 설정
echo 2. Source를 'Deploy from a branch'로 설정
echo 3. Branch를 'main'으로 선택
echo 4. Save 클릭
echo.
echo 🌐 배포 후 접근 URL:
echo https://YOUR_USERNAME.github.io/YOUR_REPO_NAME
echo.
echo 📖 자세한 배포 가이드는 DEPLOYMENT_GUIDE.md를 참조하세요.

pause 