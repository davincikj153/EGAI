네, 좋습니다\! 방금 분석해 드린 내용을 바탕으로 GitHub에 바로 사용할 수 있는 README.md 파일의 전체 내용을 제안해 드립니다.

아래 내용을 복사하여 `README.md` 파일에 붙여넣으시면 됩니다.

-----

# EGAI (Engine-sound AI) Project 🚗🔊

## 📖 프로젝트 개요 (Overview)

**EGAI**는 현대자동차 인증중고차 웹사이트에서 중고차 매물 정보를 수집하기 위해 제작된 파이썬 기반의 웹 크롤러입니다.

단순히 차량의 제원 정보만 수집하는 것을 넘어, 각 매물의 **엔진 소리(Audio) 데이터**까지 다운로드하여 AI 모델 학습을 위한 데이터셋 구축을 목표로 합니다. `Selenium`을 활용하여 동적 웹 페이지의 모든 데이터를 효과적으로 수집하고, 수집된 데이터는 체계적으로 CSV 파일과 에셋 폴더에 저장합니다.

## ✨ 주요 기능 (Key Features)

  - **동적 웹 페이지 크롤링**: `Selenium`을 사용하여 '더보기' 버튼 클릭과 같은 사용자 상호작용을 자동화하고, 동적으로 로드되는 모든 매물 정보를 수집합니다.
  - **설정 기반의 유연한 크롤링**: URL, CSS 선택자, 크롤링 딜레이 등 주요 설정값을 `config.json` 파일로 분리하여 코드 수정 없이 크롤링 대상을 변경하거나 유지보수할 수 있습니다.
  - **상세 데이터 추출**: 차량의 기본 정보(연식, 주행거리, 연료 등)는 물론, 특이사항, 진단 정보, 보증 기간 등 상세 페이지에 존재하는 대부분의 데이터를 정밀하게 추출합니다.
  - **엔진 오디오 데이터 수집**: 각 매물 상세 페이지에 있는 엔진 소리 오디오 파일(.mp3)을 자동으로 다운로드하여 로컬에 저장합니다.
  - **체계적인 데이터 관리**:
      - 수집된 모든 차량 메타데이터는 `car_audio_metadata.csv` 파일에 저장됩니다.
      - 크롤링할 매물 목록(`goodsNo`)과 수집 상태는 `goods_nos.csv` 파일로 관리하여 중복 수집을 방지하고 작업 재개 시 효율성을 높입니다.
      - 다운로드한 오디오 파일은 각 `goodsNo`별 폴더에 분리하여 저장합니다.

## 🏗️ 프로젝트 구조 (Project Structure)

```
EGAI/
├── config/
│   ├── default_config.json   # 기본 설정 파일
│   └── crawler_config.json   # (선택) 사용자 정의 설정 파일
│
├── data/
│   ├── goods_nos.csv             # 수집 대상 차량 번호 및 상태 관리
│   ├── car_audio_metadata.csv    # 최종 수집 데이터
│   └── vehicle_assets/           # 오디오 파일 저장 폴더
│       └── {goodsNo}/
│           └── audio.mp3
│
├── src/
│   ├── main_crawler.py       # 크롤러 실행 및 전체 흐름 제어
│   ├── config_loader.py      # 설정(JSON) 파일 로드 및 유효성 검사
│   ├── web_scraper.py        # 웹 페이지 HTML 요청/가져오기 (Selenium)
│   ├── page_parser.py        # HTML 파싱 및 데이터 추출 (BeautifulSoup)
│   ├── data_manager.py       # 데이터(CSV, 파일) 저장 및 관리
│   └── audio_downloader.py   # 오디오 파일 다운로드
│
└── main.py                     # 프로젝트 시작점
```

## ⚙️ 동작 원리 (How it Works)

1.  **설정 로드**: `ConfigLoader`가 `crawler_config.json` 또는 `default_config.json` 파일을 로드합니다.
2.  **리스트 페이지 로드**: `WebScraper`가 Selenium을 이용해 중고차 리스트 페이지에 접속합니다.
3.  **필터 적용 및 전체 리스트 로딩**: 설정에 따라 연료 필터를 클릭하고, 페이지 하단의 '더보기' 버튼이 사라질 때까지 반복 클릭하여 전체 매물을 로딩합니다.
4.  **차량 고유번호(goodsNo) 수집**: `PageParser`가 로드된 전체 페이지에서 각 매물의 고유번호(`goodsNo`)를 모두 추출합니다.
5.  **상세 페이지 순회 및 데이터 추출**:
      - `DataManager`가 이미 수집된 `goodsNo`를 확인하여, 신규 건에 대해서만 크롤링을 진행합니다.
      - 각 `goodsNo`에 해당하는 상세 페이지에 접속하여 차량 제원, 옵션, 오디오 파일 URL 등 모든 메타데이터를 추출합니다.
6.  **데이터 저장**:
      - `AudioDownloader`가 추출된 URL을 사용해 엔진 소리 오디오 파일을 `data/vehicle_assets/{goodsNo}/` 경로에 다운로드합니다.
      - `DataManager`가 추출된 모든 메타데이터와 오디오 파일 경로를 `car_audio_metadata.csv` 파일에 저장하고, `goods_nos.csv` 파일에 수집 완료 상태를 기록합니다.

## 🚀 시작하기 (Getting Started)

### 1\. 사전 준비 (Prerequisites)

  - Python 3.x
  - Google Chrome 브라우저

### 2\. 설치 (Installation)

```bash
# 1. 프로젝트를 컴퓨터로 복제합니다.
git clone https://github.com/davincikj153/EGAI.git

# 2. 프로젝트 폴더로 이동합니다.
cd EGAI

# 3. 필요한 파이썬 라이브러리를 설치합니다.
pip install pandas requests selenium beautifulsoup4 lxml webdriver-manager
```

### 3\. 설정 (Configuration)

기본 설정으로도 즉시 실행할 수 있습니다. 크롤링 대상을 변경하고 싶다면 `config/` 폴더에 `default_config.json` 파일을 복사하여 `crawler_config.json` 파일을 만들고 내용을 수정하세요. 프로그램은 `crawler_config.json`을 우선적으로 사용합니다.

### 4\. 실행 (Running the aplication)

```bash
python main.py
```

크롤러가 실행되면 Chrome 브라우저가 자동으로 열리고, 설정된 웹사이트에서 데이터 수집을 시작합니다. 모든 과정은 터미널에 로그로 출력됩니다.