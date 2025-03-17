# 전국 카페 서점 검색 시스템

전국의 카페가 있는 서점을 검색하고 정보를 제공하는 웹 애플리케이션입니다. 문화공공데이터 API를 활용하여 서점 정보를 가져오고, OpenAI API를 통해 검색 결과에 대한 AI 분석을 제공합니다.

## 기능

- 지역명이나 서점명으로 서점 검색
- 검색 결과에 대한 상세 정보 제공 (주소, 연락처, 설명 등)
- AI 분석을 통한 검색 결과 해석 및 추천
- 모바일 친화적인 반응형 디자인

## 설치 및 실행 방법

### 로컬 환경에서 실행하기

1. 저장소 클론하기
   ```
   git clone https://github.com/yourusername/cafe-bookstore-search.git
   cd cafe-bookstore-search
   ```

2. 가상환경 생성 및 활성화
   ```
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. 의존성 설치
   ```
   pip install -r requirements.txt
   ```

4. 환경 변수 설정
   `.env` 파일을 생성하고 다음 내용을 추가합니다:
   ```
   OPENAI_API_KEY=your_openai_api_key
   CULTURE_API_KEY=your_culture_api_key
   FLASK_SECRET_KEY=your_secret_key
   ```

5. 애플리케이션 실행
   ```
   python main.py
   ```

6. 웹 브라우저에서 `http://localhost:5000`으로 접속

### 배포 방법

#### Render.com에 배포하기

1. [Render.com](https://render.com)에 가입하고 로그인합니다.
2. 대시보드에서 "New Web Service" 버튼을 클릭합니다.
3. GitHub 저장소를 연결하거나 코드를 직접 업로드합니다.
4. 다음 설정을 입력합니다:
   - Name: cafe-bookstore-search (또는 원하는 이름)
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn main:app`
5. 환경 변수를 추가합니다:
   - OPENAI_API_KEY
   - CULTURE_API_KEY
   - FLASK_SECRET_KEY
6. "Create Web Service" 버튼을 클릭하여 배포를 시작합니다.

#### Vercel에 배포하기

1. [Vercel](https://vercel.com)에 가입하고 로그인합니다.
2. "New Project" 버튼을 클릭합니다.
3. GitHub 저장소를 가져옵니다.
4. 프로젝트 설정에서 다음을 구성합니다:
   - Framework Preset: Other
   - Build Command: `pip install -r requirements.txt`
   - Output Directory: `.`
   - Install Command: `pip install -r requirements.txt`
5. 환경 변수를 추가합니다:
   - OPENAI_API_KEY
   - CULTURE_API_KEY
   - FLASK_SECRET_KEY
6. "Deploy" 버튼을 클릭하여 배포를 시작합니다.

## API 키 발급 방법

### 문화공공데이터 API 키 발급

1. [문화공공데이터포털](http://api.kcisa.kr)에 접속하여 회원가입 및 로그인합니다.
2. "API 활용신청" 메뉴에서 "API_CIA_090" 서비스를 선택합니다.
3. 신청서를 작성하고 제출합니다.
4. 승인 후 발급된 API 키를 `.env` 파일의 `CULTURE_API_KEY` 값으로 설정합니다.

### OpenAI API 키 발급

1. [OpenAI 플랫폼](https://platform.openai.com)에 접속하여 회원가입 및 로그인합니다.
2. API 키 섹션에서 새 API 키를 생성합니다.
3. 생성된 API 키를 `.env` 파일의 `OPENAI_API_KEY` 값으로 설정합니다.

## 기술 스택

- Backend: Flask (Python)
- Frontend: HTML, CSS, JavaScript, Bootstrap
- APIs: 문화공공데이터 API, OpenAI API
- 배포: Render.com, Vercel

## 라이선스

MIT License

## 기여 방법

1. 이 저장소를 포크합니다.
2. 새 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`).
3. 변경사항을 커밋합니다 (`git commit -m 'Add some amazing feature'`).
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`).
5. Pull Request를 생성합니다. 