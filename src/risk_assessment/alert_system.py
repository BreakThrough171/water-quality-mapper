import pandas as pd
import numpy as np
from datetime import datetime

class WaterQualityAlertCalculator:
    """수질 경보기준 계산기 - TP, TN 가중치 적용"""
    
    def __init__(self):
        # 가중치 설정
        self.tp_weight = 0.99067  # 총인 가중치
        self.tn_weight = 0.00933  # 총질소 가중치
        
        # 5단계 경보기준 (20%p씩)
        self.alert_levels = {
            '1단계': 0.2,    # 20%
            '2단계': 0.4,    # 40%
            '3단계': 0.6,    # 60%
            '4단계': 0.8,    # 80%
            '5단계': 1.0     # 100%
        }
        
        # 기준값 (예시 - 실제 기준값으로 수정 필요)
        self.standard_values = {
            'TP_standard': 0.1,  # 총인 기준값 (mg/L)
            'TN_standard': 2.0   # 총질소 기준값 (mg/L)
        }
    
    def calculate_weighted_index(self, tp_value, tn_value):
        """
        가중치를 적용한 수질 지수 계산
        
        Args:
            tp_value (float): 총인 값 (mg/L)
            tn_value (float): 총질소 값 (mg/L)
            
        Returns:
            float: 가중치 적용된 수질 지수
        """
        if tp_value is None or tn_value is None:
            return None
        
        try:
            # 가중치 적용 계산
            weighted_index = (tp_value * self.tp_weight) + (tn_value * self.tn_weight)
            return weighted_index
        except (ValueError, TypeError):
            return None
    
    def calculate_alert_level(self, tp_value, tn_value):
        """
        경보 단계 계산
        
        Args:
            tp_value (float): 총인 값 (mg/L)
            tn_value (float): 총질소 값 (mg/L)
            
        Returns:
            dict: 경보 정보
        """
        weighted_index = self.calculate_weighted_index(tp_value, tn_value)
        
        if weighted_index is None:
            return {
                'alert_level': '데이터 없음',
                'weighted_index': None,
                'tp_ratio': None,
                'tn_ratio': None,
                'description': '유효하지 않은 데이터'
            }
        
        # 기준값 대비 비율 계산
        tp_ratio = tp_value / self.standard_values['TP_standard'] if self.standard_values['TP_standard'] > 0 else 0
        tn_ratio = tn_value / self.standard_values['TN_standard'] if self.standard_values['TN_standard'] > 0 else 0
        
        # 가중치 적용된 비율
        weighted_ratio = (tp_ratio * self.tp_weight) + (tn_ratio * self.tn_weight)
        
        # 경보 단계 결정
        alert_level = '정상'
        for level, threshold in self.alert_levels.items():
            if weighted_ratio >= threshold:
                alert_level = level
        
        # 경보 설명
        alert_descriptions = {
            '정상': '수질이 양호한 상태입니다.',
            '1단계': '수질에 주의가 필요한 상태입니다.',
            '2단계': '수질에 경계가 필요한 상태입니다.',
            '3단계': '수질에 경보가 필요한 상태입니다.',
            '4단계': '수질에 심각한 경보가 필요한 상태입니다.',
            '5단계': '수질에 매우 심각한 경보가 필요한 상태입니다.'
        }
        
        return {
            'alert_level': alert_level,
            'weighted_index': weighted_index,
            'weighted_ratio': weighted_ratio,
            'tp_ratio': tp_ratio,
            'tn_ratio': tn_ratio,
            'tp_weighted': tp_value * self.tp_weight,
            'tn_weighted': tn_value * self.tn_weight,
            'description': alert_descriptions.get(alert_level, '알 수 없는 상태')
        }
    
    def process_dataframe(self, df, tp_column='총인_TP_mgL', tn_column='총질소_TN_mgL'):
        """
        DataFrame에 경보 정보 추가
        
        Args:
            df (DataFrame): 수질 데이터 DataFrame
            tp_column (str): 총인 컬럼명
            tn_column (str): 총질소 컬럼명
            
        Returns:
            DataFrame: 경보 정보가 추가된 DataFrame
        """
        if df.empty:
            return df
        
        # 결과를 저장할 리스트
        alert_results = []
        
        for idx, row in df.iterrows():
            tp_value = row.get(tp_column)
            tn_value = row.get(tn_column)
            
            alert_info = self.calculate_alert_level(tp_value, tn_value)
            alert_results.append(alert_info)
        
        # 결과를 DataFrame으로 변환
        alert_df = pd.DataFrame(alert_results)
        
        # 원본 DataFrame과 결합
        result_df = pd.concat([df.reset_index(drop=True), alert_df], axis=1)
        
        return result_df
    
    def get_alert_summary(self, df):
        """
        경보 단계별 요약 통계
        
        Args:
            df (DataFrame): 경보 정보가 포함된 DataFrame
            
        Returns:
            DataFrame: 경보 단계별 요약
        """
        if 'alert_level' not in df.columns:
            return pd.DataFrame()
        
        summary = df.groupby('alert_level').agg({
            'weighted_index': ['count', 'mean', 'std', 'min', 'max'],
            'weighted_ratio': ['mean', 'std', 'min', 'max'],
            'tp_ratio': ['mean', 'std', 'min', 'max'],
            'tn_ratio': ['mean', 'std', 'min', 'max']
        }).round(3)
        
        # 컬럼명 정리
        summary.columns = [
            '측정횟수', '가중지수_평균', '가중지수_표준편차', '가중지수_최소값', '가중지수_최대값',
            '가중비율_평균', '가중비율_표준편차', '가중비율_최소값', '가중비율_최대값',
            'TP비율_평균', 'TP비율_표준편차', 'TP비율_최소값', 'TP비율_최대값',
            'TN비율_평균', 'TN비율_표준편차', 'TN비율_최소값', 'TN비율_최대값'
        ]
        
        return summary.reset_index()
    
    def update_standard_values(self, tp_standard, tn_standard):
        """
        기준값 업데이트
        
        Args:
            tp_standard (float): 총인 기준값 (mg/L)
            tn_standard (float): 총질소 기준값 (mg/L)
        """
        self.standard_values['TP_standard'] = tp_standard
        self.standard_values['TN_standard'] = tn_standard
        print(f"✅ 기준값 업데이트 완료:")
        print(f"   총인 기준값: {tp_standard} mg/L")
        print(f"   총질소 기준값: {tn_standard} mg/L")
    
    def get_calculation_info(self):
        """
        계산 정보 출력
        """
        print("🔍 수질 경보 계산 정보")
        print("=" * 50)
        print(f"📊 가중치:")
        print(f"   총인(TP) 가중치: {self.tp_weight:.5f}")
        print(f"   총질소(TN) 가중치: {self.tn_weight:.5f}")
        print(f"   가중치 합계: {self.tp_weight + self.tn_weight:.5f}")
        print()
        print(f"📊 기준값:")
        print(f"   총인 기준값: {self.standard_values['TP_standard']} mg/L")
        print(f"   총질소 기준값: {self.standard_values['TN_standard']} mg/L")
        print()
        print(f"📊 경보 단계:")
        for level, threshold in self.alert_levels.items():
            print(f"   {level}: {threshold*100:.0f}%")

def main():
    """메인 실행 함수 (예시)"""
    
    # 계산기 초기화
    calculator = WaterQualityAlertCalculator()
    
    # 계산 정보 출력
    calculator.get_calculation_info()
    
    # 기준값 업데이트 (실제 기준값으로 수정)
    # calculator.update_standard_values(tp_standard=0.1, tn_standard=2.0)
    
    # 예시 데이터로 테스트
    print("\n🧪 예시 계산 테스트")
    print("=" * 30)
    
    test_cases = [
        (0.05, 1.0, "양호한 수질"),
        (0.1, 2.0, "기준값"),
        (0.15, 3.0, "경계 수준"),
        (0.2, 4.0, "경보 수준"),
        (0.25, 5.0, "심각 수준")
    ]
    
    for tp, tn, description in test_cases:
        result = calculator.calculate_alert_level(tp, tn)
        print(f"\n📊 {description}:")
        print(f"   TP: {tp} mg/L, TN: {tn} mg/L")
        print(f"   경보단계: {result['alert_level']}")
        print(f"   가중지수: {result['weighted_index']:.4f}")
        print(f"   가중비율: {result['weighted_ratio']:.2f}")

if __name__ == "__main__":
    main() 