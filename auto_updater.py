#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
자동 지도 업데이트 스케줄러
일주일에 한 번 통합 수질 지도를 자동으로 업데이트합니다.
"""

import schedule
import time
import os
import sys
import logging
from datetime import datetime
import shutil

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_updater.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def update_integrated_map():
    """통합 지도를 업데이트합니다."""
    try:
        logger.info("🔄 통합 지도 업데이트 시작...")
        
        # integrated_water_quality_map.py 실행
        from integrated_water_quality_map import create_integrated_water_quality_map
        
        # 지도 생성
        result = create_integrated_water_quality_map()
        
        if result:
            logger.info("✅ 통합 지도 업데이트 완료!")
            
            # 웹 폴더로 지도 복사
            web_images_dir = 'web/static/images'
            if not os.path.exists(web_images_dir):
                os.makedirs(web_images_dir)
            
            # 최신 지도를 웹 폴더로 복사
            source_file = 'integrated_water_quality_map.png'
            if os.path.exists(source_file):
                # 타임스탬프가 포함된 파일명으로 복사
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                dest_file = f'integrated_water_quality_map_{timestamp}.png'
                dest_path = os.path.join(web_images_dir, dest_file)
                
                shutil.copy2(source_file, dest_path)
                logger.info(f"📁 지도가 웹 폴더로 복사됨: {dest_file}")
                
                # 최신 지도를 기본 파일명으로도 복사
                latest_file = os.path.join(web_images_dir, 'integrated_water_quality_map.png')
                shutil.copy2(source_file, latest_file)
                logger.info("📁 최신 지도가 기본 파일명으로 복사됨")
                
                return True
            else:
                logger.error("❌ 지도 파일을 찾을 수 없습니다.")
                return False
        else:
            logger.error("❌ 지도 생성에 실패했습니다.")
            return False
            
    except Exception as e:
        logger.error(f"❌ 지도 업데이트 중 오류 발생: {str(e)}")
        return False

def cleanup_old_maps():
    """오래된 지도 파일들을 정리합니다 (최근 10개만 유지)."""
    try:
        web_images_dir = 'web/static/images'
        if not os.path.exists(web_images_dir):
            return
        
        # integrated_water_quality_map_*.png 파일들 찾기
        map_files = []
        for filename in os.listdir(web_images_dir):
            if filename.startswith('integrated_water_quality_map_') and filename.endswith('.png'):
                file_path = os.path.join(web_images_dir, filename)
                map_files.append((file_path, os.path.getmtime(file_path)))
        
        # 날짜순으로 정렬 (최신순)
        map_files.sort(key=lambda x: x[1], reverse=True)
        
        # 10개 이상이면 오래된 파일들 삭제
        if len(map_files) > 10:
            for file_path, _ in map_files[10:]:
                os.remove(file_path)
                logger.info(f"🗑️ 오래된 지도 파일 삭제: {os.path.basename(file_path)}")
                
    except Exception as e:
        logger.error(f"❌ 파일 정리 중 오류 발생: {str(e)}")

def run_scheduler():
    """스케줄러를 실행합니다."""
    logger.info("🚀 자동 지도 업데이트 스케줄러 시작")
    
    # 매주 일요일 오전 9시에 지도 업데이트
    schedule.every().sunday.at("09:00").do(update_integrated_map)
    
    # 매주 일요일 오전 9시 30분에 오래된 파일 정리
    schedule.every().sunday.at("09:30").do(cleanup_old_maps)
    
    # 테스트용: 1분마다 실행 (개발 시에만 사용)
    # schedule.every(1).minutes.do(update_integrated_map)
    
    logger.info("📅 스케줄 설정 완료:")
    logger.info("   - 매주 일요일 오전 9:00: 지도 업데이트")
    logger.info("   - 매주 일요일 오전 9:30: 오래된 파일 정리")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 체크

def run_once():
    """한 번만 지도를 업데이트합니다 (테스트용)."""
    logger.info("🔄 즉시 지도 업데이트 실행...")
    success = update_integrated_map()
    if success:
        cleanup_old_maps()
        logger.info("✅ 즉시 업데이트 완료!")
    else:
        logger.error("❌ 즉시 업데이트 실패!")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='자동 지도 업데이트 스케줄러')
    parser.add_argument('--once', action='store_true', help='한 번만 실행 (테스트용)')
    
    args = parser.parse_args()
    
    if args.once:
        run_once()
    else:
        run_scheduler() 