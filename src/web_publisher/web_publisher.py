"""
웹 게시 기능

생성된 지도와 차트를 웹사이트에 게시하는 기능을 제공합니다.
"""

import os
import shutil
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

from ..utils.config import config
from ..utils.logger import logger
from ..utils.helpers import format_datetime


class WebPublisher:
    """웹 게시 기능을 담당하는 클래스"""
    
    def __init__(self):
        self.web_dir = config.get_file_path('WEB_DIR')
        self.output_dir = config.get_file_path('OUTPUT_DIR')
        self.template_dir = os.path.join(self.web_dir, 'templates')
        self.static_dir = os.path.join(self.web_dir, 'static')
        
        # 웹 디렉토리 생성
        os.makedirs(self.web_dir, exist_ok=True)
        os.makedirs(self.template_dir, exist_ok=True)
        os.makedirs(self.static_dir, exist_ok=True)
        os.makedirs(os.path.join(self.static_dir, 'images'), exist_ok=True)
        os.makedirs(os.path.join(self.static_dir, 'css'), exist_ok=True)
        os.makedirs(os.path.join(self.static_dir, 'js'), exist_ok=True)
    
    def publish_map(self, map_file_path: str, title: str = "수질 모니터링 지도") -> str:
        """
        지도를 웹사이트에 게시합니다.
        
        Args:
            map_file_path: 게시할 지도 파일 경로
            title: 웹페이지 제목
            
        Returns:
            생성된 HTML 파일 경로
        """
        try:
            # 지도 파일을 static/images로 복사
            map_filename = os.path.basename(map_file_path)
            static_map_path = os.path.join(self.static_dir, 'images', map_filename)
            shutil.copy2(map_file_path, static_map_path)
            
            # HTML 파일 생성
            html_content = self._create_map_html(title, map_filename)
            html_filename = f"map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            html_path = os.path.join(self.web_dir, html_filename)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"지도가 웹사이트에 게시되었습니다: {html_path}")
            return html_path
            
        except Exception as e:
            logger.error(f"지도 게시 중 오류 발생: {str(e)}")
            return ""
    
    def publish_dashboard(self, chart_files: List[str], title: str = "수질 모니터링 대시보드") -> str:
        """
        대시보드를 웹사이트에 게시합니다.
        
        Args:
            chart_files: 게시할 차트 파일 경로 리스트
            title: 웹페이지 제목
            
        Returns:
            생성된 HTML 파일 경로
        """
        try:
            # 차트 파일들을 static/images로 복사
            chart_filenames = []
            for chart_file in chart_files:
                if os.path.exists(chart_file):
                    chart_filename = os.path.basename(chart_file)
                    static_chart_path = os.path.join(self.static_dir, 'images', chart_filename)
                    shutil.copy2(chart_file, static_chart_path)
                    chart_filenames.append(chart_filename)
            
            # HTML 파일 생성
            html_content = self._create_dashboard_html(title, chart_filenames)
            html_filename = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            html_path = os.path.join(self.web_dir, html_filename)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"대시보드가 웹사이트에 게시되었습니다: {html_path}")
            return html_path
            
        except Exception as e:
            logger.error(f"대시보드 게시 중 오류 발생: {str(e)}")
            return ""
    
    def create_index_page(self, map_html: str = None, dashboard_html: str = None) -> str:
        """
        메인 인덱스 페이지를 생성합니다.
        
        Args:
            map_html: 지도 HTML 파일 경로
            dashboard_html: 대시보드 HTML 파일 경로
            
        Returns:
            생성된 인덱스 HTML 파일 경로
        """
        try:
            html_content = self._create_index_html(map_html, dashboard_html)
            index_path = os.path.join(self.web_dir, 'index.html')
            
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"인덱스 페이지가 생성되었습니다: {index_path}")
            return index_path
            
        except Exception as e:
            logger.error(f"인덱스 페이지 생성 중 오류 발생: {str(e)}")
            return ""
    
    def open_in_browser(self, html_path: str) -> bool:
        """
        브라우저에서 HTML 파일을 엽니다.
        
        Args:
            html_path: 열 HTML 파일 경로
            
        Returns:
            성공 여부
        """
        try:
            # 절대 경로로 변환
            abs_path = os.path.abspath(html_path)
            file_url = f"file:///{abs_path.replace(os.sep, '/')}"
            
            webbrowser.open(file_url)
            logger.info(f"브라우저에서 파일을 열었습니다: {file_url}")
            return True
            
        except Exception as e:
            logger.error(f"브라우저에서 파일 열기 실패: {str(e)}")
            return False
    
    def _create_map_html(self, title: str, map_filename: str) -> str:
        """지도 HTML 템플릿을 생성합니다."""
        return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: 'Malgun Gothic', Arial, sans-serif;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}
        .content {{
            padding: 20px;
        }}
        .map-container {{
            text-align: center;
            margin: 20px 0;
        }}
        .map-image {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .info {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .footer {{
            background-color: #343a40;
            color: white;
            text-align: center;
            padding: 15px;
            font-size: 0.9em;
        }}
        .update-time {{
            color: #6c757d;
            font-size: 0.9em;
            text-align: center;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>질소·인 유출 위험 지역 지도</h1>
            <p>전국 수질 모니터링 시스템</p>
        </div>
        
        <div class="content">
            <div class="map-container">
                <img src="static/images/{map_filename}" alt="수질 모니터링 지도" class="map-image">
            </div>
            
            <div class="info">
                <h3>📊 지도 정보</h3>
                <p>이 지도는 전국의 수질 측정소 데이터를 기반으로 생성되었습니다.</p>
                <ul>
                    <li><strong>TP (총인):</strong> 가중치 0.99</li>
                    <li><strong>TN (총질소):</strong> 가중치 0.01</li>
                    <li><strong>위험도 구분:</strong> 낮음(녹색) ~ 매우높음(빨간색)</li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2024 수질 모니터링 시스템</p>
        </div>
    </div>
    
    <div class="update-time">
        마지막 업데이트: {format_datetime(datetime.now())}
    </div>
</body>
</html>"""
    
    def _create_dashboard_html(self, title: str, chart_filenames: List[str]) -> str:
        """대시보드 HTML 템플릿을 생성합니다."""
        chart_html = ""
        for i, filename in enumerate(chart_filenames):
            chart_html += f"""
            <div class="chart-item">
                <h3>차트 {i+1}</h3>
                <img src="static/images/{filename}" alt="차트 {i+1}" class="chart-image">
            </div>"""
        
        return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: 'Malgun Gothic', Arial, sans-serif;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .content {{
            padding: 20px;
        }}
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .chart-item {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .chart-item h3 {{
            margin-top: 0;
            color: #495057;
        }}
        .chart-image {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        .footer {{
            background-color: #343a40;
            color: white;
            text-align: center;
            padding: 15px;
            font-size: 0.9em;
        }}
        .update-time {{
            color: #6c757d;
            font-size: 0.9em;
            text-align: center;
            margin-top: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
        </div>
        
        <div class="content">
            <div class="charts-grid">
                {chart_html}
            </div>
        </div>
        
        <div class="footer">
            <p>© 2024 수질 모니터링 시스템</p>
        </div>
    </div>
    
    <div class="update-time">
        마지막 업데이트: {format_datetime(datetime.now())}
    </div>
</body>
</html>"""
    
    def _create_index_html(self, map_html: str = None, dashboard_html: str = None) -> str:
        """인덱스 HTML 템플릿을 생성합니다."""
        map_link = ""
        dashboard_link = ""
        
        if map_html:
            map_link = f'<a href="{os.path.basename(map_html)}" class="card">'
            map_link += '<div class="card-content">'
            map_link += '<h3>🗺️ 수질 모니터링 지도</h3>'
            map_link += '<p>전국 수질 측정소 데이터를 기반으로 한 지도</p>'
            map_link += '</div></a>'
        
        if dashboard_html:
            dashboard_link = f'<a href="{os.path.basename(dashboard_html)}" class="card">'
            dashboard_link += '<div class="card-content">'
            dashboard_link += '<h3>📊 수질 분석 대시보드</h3>'
            dashboard_link += '<p>수질 데이터 분석 결과 및 차트</p>'
            dashboard_link += '</div></a>'
        
        return f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>수질 모니터링 시스템</title>
    <style>
        body {{
            margin: 0;
            padding: 20px;
            font-family: 'Malgun Gothic', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 3em;
            margin-bottom: 10px;
        }}
        .header p {{
            margin: 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .content {{
            padding: 40px 20px;
        }}
        .cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin: 30px 0;
        }}
        .card {{
            background: white;
            border-radius: 15px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            padding: 30px;
            text-decoration: none;
            color: inherit;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 2px solid transparent;
        }}
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            border-color: #667eea;
        }}
        .card-content h3 {{
            margin: 0 0 15px 0;
            color: #333;
            font-size: 1.5em;
        }}
        .card-content p {{
            margin: 0;
            color: #666;
            line-height: 1.6;
        }}
        .info {{
            background-color: #f8f9fa;
            padding: 30px;
            border-radius: 15px;
            margin: 30px 0;
        }}
        .info h3 {{
            margin-top: 0;
            color: #495057;
        }}
        .footer {{
            background-color: #343a40;
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 0.9em;
        }}
        .update-time {{
            color: #6c757d;
            font-size: 0.9em;
            text-align: center;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌊 수질 모니터링 시스템</h1>
            <p>전국 수질 데이터 분석 및 시각화</p>
        </div>
        
        <div class="content">
            <div class="cards">
                {map_link}
                {dashboard_link}
            </div>
            
            <div class="info">
                <h3>📋 시스템 정보</h3>
                <p>이 시스템은 환경부 수질 DB API를 활용하여 전국의 수질 데이터를 수집하고 분석합니다.</p>
                <ul>
                    <li><strong>데이터 소스:</strong> 환경부 수질 DB API</li>
                    <li><strong>분석 항목:</strong> TP(총인), TN(총질소)</li>
                    <li><strong>가중치:</strong> TP 0.99, TN 0.01</li>
                    <li><strong>업데이트:</strong> 자동 스케줄링</li>
                </ul>
            </div>
        </div>
        
        <div class="footer">
            <p>© 2024 수질 모니터링 시스템</p>
        </div>
    </div>
    
    <div class="update-time">
        마지막 업데이트: {format_datetime(datetime.now())}
    </div>
</body>
</html>""" 