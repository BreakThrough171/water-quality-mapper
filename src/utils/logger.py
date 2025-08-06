#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
로깅 모듈
시스템 로그 관리를 담당합니다.
"""

import logging
import os
from datetime import datetime
from typing import Optional

from .config import config

def setup_logger(name: str = 'water_quality_system', 
                log_level: str = 'INFO',
                log_file: Optional[str] = None) -> logging.Logger:
    """
    로거 설정
    
    Args:
        name: 로거 이름
        log_level: 로그 레벨
        log_file: 로그 파일 경로 (None이면 콘솔만 출력)
        
    Returns:
        logging.Logger: 설정된 로거
    """
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 기존 핸들러 제거 (중복 방지)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 로그 포맷 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 파일 핸들러 (지정된 경우)
    if log_file:
        # 로그 디렉토리 생성
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_log_file_path() -> str:
    """로그 파일 경로 생성"""
    timestamp = datetime.now().strftime('%Y%m%d')
    log_dir = config.paths['LOGS_DIR']
    os.makedirs(log_dir, exist_ok=True)
    return os.path.join(log_dir, f'water_quality_{timestamp}.log')

# 기본 로거 생성
logger = setup_logger(
    name='water_quality_system',
    log_level=config.get_system_config('LOG_LEVEL'),
    log_file=get_log_file_path()
) 