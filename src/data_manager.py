# src/data_manager.py

import os
import pandas as pd
from typing import List, Dict, Union, Any


class DataManager:
    """
    크롤링된 데이터를 관리하고 저장하는 클래스입니다.
    CSV 파일 저장, goodsNo 목록 관리, 디버깅 HTML 저장 등을 담당합니다.
    """

    def __init__(self):
        # 현재 스크립트 파일의 디렉토리
        current_script_dir = os.path.dirname(os.path.abspath(__file__))
        # 프로젝트 루트 디렉토리 (src의 부모 디렉토리)
        self.project_root_dir = os.path.normpath(os.path.join(current_script_dir, '..'))

        self.data_dir = os.path.join(self.project_root_dir, 'data')
        self.debug_html_dir = os.path.join(self.data_dir, 'debug_html')
        self.goods_nos_csv_path = os.path.join(self.data_dir, 'goods_nos.csv')
        self.metadata_csv_path = os.path.join(self.data_dir, 'car_audio_metadata.csv')
        self.vehicle_assets_dir = os.path.join(self.data_dir, 'vehicle_assets')  # MP3 저장 경로

        # 필요한 디렉토리 생성
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.debug_html_dir, exist_ok=True)
        os.makedirs(self.vehicle_assets_dir, exist_ok=True)

        # 초기 설계 메타데이터 컬럼 순서 정의
        self.metadata_columns_order = [
            "audio_file_path", "data_label", "goodsNo", "vehicle_name",
            "first_registration_date", "year", "current_mileage_km",
            "vehicle_type", "seating_capacity", "fuel_type", "displacement_cc",
            "drivetrain", "transmission_type", "exterior_color", "interior_color",
            "vehicle_number", "popular_package_applied", "certified_inspection_passed",
            "inspection_date", "oil_filter_changed", "ac_filter_changed",
            "wiper_blades_changed", "washer_fluid_replenished",
            "warranty_remaining_km", "warranty_remaining_months",
            "my_car_damage_reported", "owner_changed", "liens_encumbrances_exist",
            "overall_score", "mid_freq_score", "low_high_freq", "audible_range_score", # <-- 여기에 추가!
            "regularity", "irregularity", "specific_anomaly", "jessino"
        ]

    def get_base_data_path(self) -> str:
        """데이터 저장 기본 경로를 반환합니다."""
        return self.data_dir

    def load_goods_nos_with_status(self) -> pd.DataFrame:
        """
        goods_nos.csv 파일에서 goodsNo와 처리 상태를 로드합니다.
        파일이 없으면 빈 DataFrame을 반환하고, 필요한 컬럼을 추가합니다.
        """
        if os.path.exists(self.goods_nos_csv_path):
            df = pd.read_csv(self.goods_nos_csv_path)
            # 필요한 컬럼이 없으면 추가하고 기본값 설정
            if 'data_collected' not in df.columns:
                df['data_collected'] = False
            if 'mp3_downloaded' not in df.columns:
                df['mp3_downloaded'] = False
            return df
        else:
            # 파일이 없으면 goodsNo, data_collected, mp3_downloaded 컬럼을 가진 빈 DataFrame 생성
            return pd.DataFrame(columns=['goodsNo', 'data_collected', 'mp3_downloaded'])

    def save_goods_nos_with_status(self, df: pd.DataFrame):
        """
        goodsNo DataFrame을 goods_nos.csv 파일에 저장합니다.
        """
        df.to_csv(self.goods_nos_csv_path, index=False)

    def add_new_goods_nos_to_df(self, existing_df: pd.DataFrame,
                                new_goods_nos_list: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        새로 발견된 goodsNo 목록을 기존 DataFrame에 추가합니다.
        data_collected와 mp3_downloaded는 False로 초기화됩니다.
        """
        if not new_goods_nos_list:
            return existing_df

        new_df = pd.DataFrame(new_goods_nos_list)

        # 기존 DataFrame과 합치기 전에 중복 제거
        combined_df = pd.concat([existing_df, new_df]).drop_duplicates(subset=['goodsNo'], keep='first')

        # 필요한 컬럼이 없으면 추가 (방어적 코딩)
        if 'data_collected' not in combined_df.columns:
            combined_df['data_collected'] = False
        if 'mp3_downloaded' not in combined_df.columns:
            combined_df['mp3_downloaded'] = False

        return combined_df

    def update_goods_no_status(self, df: pd.DataFrame, goods_no: str, column: str, status: bool) -> pd.DataFrame:
        """
        특정 goodsNo의 처리 상태 (data_collected 또는 mp3_downloaded)를 업데이트합니다.
        """
        if goods_no in df['goodsNo'].values:
            df.loc[df['goodsNo'] == goods_no, column] = status
        else:
            # goodsNo가 DataFrame에 없으면 새로 추가 (이 경우 data_collected, mp3_downloaded는 False로 시작)
            new_row = pd.DataFrame([{'goodsNo': goods_no, 'data_collected': False, 'mp3_downloaded': False}])
            new_row.loc[0, column] = status  # 새로 추가된 행의 특정 컬럼만 업데이트
            df = pd.concat([df, new_row], ignore_index=True)
            print(f"  [정보] goodsNo {goods_no}가 goods_nos.csv에 새로 추가되었습니다.")
        return df

    def save_metadata_to_csv(self, data: Dict[str, Any]):
        """
        추출된 상세 메타데이터를 car_audio_metadata.csv 파일에 저장합니다.
        초기 설계 컬럼 순서를 따르고, 누락된 값은 None으로 채웁니다.
        """
        # 데이터 정규화: 모든 컬럼을 포함하고 순서를 맞춤
        row_data = {col: data.get(col) for col in self.metadata_columns_order}

        # DataFrame으로 변환
        new_df = pd.DataFrame([row_data])

        # 파일이 이미 존재하는지 확인
        if os.path.exists(self.metadata_csv_path):
            # 기존 CSV 파일 로드
            existing_df = pd.read_csv(self.metadata_csv_path)

            # goodsNo를 기준으로 중복 확인 및 업데이트
            if data['goodsNo'] in existing_df['goodsNo'].values:
                # 기존 행 업데이트
                existing_df.loc[existing_df['goodsNo'] == data['goodsNo']] = new_df.values
                print(f"    [정보] goodsNo {data['goodsNo']}의 메타데이터가 업데이트되었습니다.")
            else:
                # 새 행 추가
                existing_df = pd.concat([existing_df, new_df], ignore_index=True)
                print(f"    [정보] goodsNo {data['goodsNo']}의 메타데이터가 새로 추가되었습니다.")

            # 저장
            existing_df.to_csv(self.metadata_csv_path, index=False)
        else:
            # 파일이 없으면 새로 생성
            new_df.to_csv(self.metadata_csv_path, index=False)
            print(f"    [정보] car_audio_metadata.csv 파일이 새로 생성되었습니다.")

    def save_debug_html(self, goods_no: str, html_content: str, filename_suffix: str = ""):
        """
        디버깅을 위해 HTML 콘텐츠를 파일로 저장합니다.
        """
        filename = f"debug_{filename_suffix}_{goods_no}.html" if filename_suffix else f"debug_{goods_no}.html"
        filepath = os.path.join(self.debug_html_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"  [디버그] HTML을 '{filepath}'에 저장했습니다.")

    def create_vehicle_asset_dir(self, goods_no: str) -> str:
        """
        특정 goodsNo에 대한 vehicle_assets 서브 디렉토리를 생성하고 경로를 반환합니다.
        """
        asset_dir = os.path.join(self.vehicle_assets_dir, goods_no)
        os.makedirs(asset_dir, exist_ok=True)
        return asset_dir