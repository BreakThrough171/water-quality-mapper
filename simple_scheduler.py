#!/usr/bin/env python3
import schedule
import time
import os
import shutil
from datetime import datetime

def update_map():
    """지도를 업데이트하고 웹 폴더로 복사합니다."""
    print(f"🔄 지도 업데이트 시작: {datetime.now()}")
    
    try:
        # integrated_water_quality_map.py 실행
        os.system("python integrated_water_quality_map.py")
        
        # 지도 파일을 웹 폴더로 복사
        source = "integrated_water_quality_map.png"
        dest = "web/static/images/integrated_water_quality_map.png"
        
        if os.path.exists(source):
            shutil.copy2(source, dest)
            print(f"✅ 지도 업데이트 완료: {datetime.now()}")
        else:
            print("❌ 지도 파일을 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

def main():
    print("🚀 자동 지도 업데이트 스케줄러 시작")
    print("📅 매주 일요일 오전 9시에 지도 업데이트")
    
    # 매주 일요일 오전 9시에 실행
    schedule.every().sunday.at("09:00").do(update_map)
    
    # 테스트용: 5분마다 실행 (개발 시에만 사용)
    # schedule.every(5).minutes.do(update_map)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--now":
        # 즉시 실행
        update_map()
    else:
        # 스케줄러 실행
        main() 