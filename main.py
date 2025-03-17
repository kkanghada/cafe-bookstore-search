import os
import json
import requests
import xmltodict
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_cors import CORS
from colorama import Fore, Style, init

# Initialize colorama
init()

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # CORS 활성화
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default-secret-key")

# OpenAI 클라이언트 초기화 부분 주석 처리 (테스트를 위해)
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class BookstoreAPI:
    """문화공공데이터 API를 통해 카페가 있는 서점 정보를 가져오는 클래스"""
    
    def __init__(self):
        self.base_url = "http://api.kcisa.kr/openapi/API_CIA_090/request"
        self.api_key = os.getenv("CULTURE_API_KEY")
        self.cached_bookstores = {}
    
    def search_bookstores(self, keyword=None, page_no=1, num_of_rows=10):
        """서점을 검색합니다."""
        params = {
            "serviceKey": self.api_key,
            "numOfRows": str(num_of_rows),
            "pageNo": str(page_no)
        }
        
        if keyword:
            params["keyword"] = keyword
        
        try:
            # 디버깅을 위한 로그 추가
            print(f"API 요청 URL: {self.base_url}")
            print(f"API 요청 파라미터: {params}")
            
            # 타임아웃 설정 추가
            response = requests.get(self.base_url, params=params, timeout=10)
            
            # 응답 상태 코드 확인
            print(f"API 응답 상태 코드: {response.status_code}")
            
            if response.status_code != 200:
                return {"error": f"API 서버 오류: 상태 코드 {response.status_code}"}
            
            # 응답 내용 확인 (디버깅용)
            print(f"API 응답 내용 일부: {response.text[:200]}...")
            
            # XML을 딕셔너리로 변환
            data = xmltodict.parse(response.text)
            
            # 응답 확인
            if "response" in data:
                header = data["response"].get("header", {})
                result_code = header.get("resultCode")
                result_msg = header.get("resultMsg")
                
                # API 오류 확인
                if result_code != "0000":
                    return {"error": f"API 오류: {result_msg} (코드: {result_code})"}
                
                body = data["response"].get("body", {})
                total_count = int(body.get("totalCount", 0))
                
                if total_count == 0:
                    return {"error": "검색 결과가 없습니다."}
                
                items = body.get("items", {})
                if not items:
                    return {"error": "검색 결과가 없습니다."}
                
                item_list = items.get("item", [])
                if isinstance(item_list, dict):  # 단일 결과인 경우
                    item_list = [item_list]
                
                return {"stores": item_list, "total_count": total_count}
            
            return {"error": "API 응답 형식이 올바르지 않습니다."}
            
        except requests.exceptions.Timeout:
            return {"error": "API 서버 응답 시간 초과. 잠시 후 다시 시도해주세요."}
        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {str(e)}")
            return {"error": "네트워크 오류: API 서버에 연결할 수 없습니다."}
        except Exception as e:
            print(f"처리 중 오류 발생: {str(e)}")
            return {"error": f"처리 중 오류가 발생했습니다: {str(e)}"}
    
    def get_bookstore_details(self, store_id):
        """특정 서점의 상세 정보를 가져옵니다."""
        if store_id in self.cached_bookstores:
            return self.cached_bookstores[store_id]
        
        result = self.search_bookstores(keyword=store_id)
        if "stores" in result and result["stores"]:
            self.cached_bookstores[store_id] = result["stores"][0]
            return result["stores"][0]
        return None

def format_bookstore_info(store):
    """서점 정보를 보기 좋게 포맷팅합니다."""
    info = {}
    info["title"] = store.get('TITLE', '이름 없음')
    info["address"] = store.get('ADDRESS', '')
    info["contact"] = store.get('CONTACT_POINT', '')
    info["description"] = store.get('DESCRIPTION', '')
    info["sub_description"] = store.get('SUB_DESCRIPTION', '')
    info["coordinates"] = store.get('COORDINATES', '')
    
    return info

def create_assistant():
    """AI 어시스턴트를 생성합니다."""
    # assistant = client.beta.assistants.create(
    #     name="카페 서점 도우미",
    #     instructions="""당신은 전국의 카페가 있는 서점을 안내하는 AI 도우미입니다.
    #     사용자의 위치나 선호도에 따라 적절한 서점을 추천하고,
    #     각 서점의 특징과 시설에 대해 상세히 안내해줄 수 있습니다.
    #      
    #      다음과 같은 정보를 제공할 수 있습니다:
    #      - 지역별 카페 서점 검색
    #      - 서점 상세 정보 (주소, 연락처, 특징 등)
    #      - 시설 정보 및 이용 안내
    #      
    #      항상 친절하고 전문적으로 응답해주세요.""",
    #     tools=[
    #         {
    #             "type": "function",
    #             "function": {
    #                 "name": "search_bookstores",
    #                 "description": "전국의 카페가 있는 서점을 검색합니다",
    #                 "parameters": {
    #                     "type": "object",
    #                     "properties": {
    #                         "keyword": {
    #                             "type": "string",
    #                             "description": "검색어 (지역명, 서점명 등)"
    #                         },
    #                         "page_no": {
    #                             "type": "integer",
    #                             "description": "페이지 번호"
    #                         },
    #                         "num_of_rows": {
    #                             "type": "integer",
    #                             "description": "한 페이지당 결과 수"
    #                         }
    #                     }
    #                 }
    #             }
    #         }
    #     ],
    #     model="gpt-4-turbo-preview"
    # )
    # return assistant
    pass

# API 클라이언트 초기화
api = BookstoreAPI()

# 어시스턴트 생성 (실제 배포 시에는 ID를 저장하고 재사용하는 것이 좋습니다)
assistant_id = os.getenv("ASSISTANT_ID")
if not assistant_id:
    # assistant = create_assistant()
    # assistant_id = assistant.id
    # print(f"새 어시스턴트 생성됨: {assistant_id}")
    print("OpenAI 어시스턴트 기능 비활성화됨")
else:
    print(f"기존 어시스턴트 사용: {assistant_id}")

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    """서점 검색 API"""
    keyword = request.form.get('keyword', '')
    page = int(request.form.get('page', 1))
    
    if not keyword:
        return jsonify({"error": "검색어를 입력해주세요."})
    
    # 디버깅 메시지 추가
    print(f"검색 요청: 키워드='{keyword}', 페이지={page}")
    
    # 테스트용 더미 데이터 (API가 작동하지 않을 경우 사용)
    use_dummy_data = os.getenv("USE_DUMMY_DATA", "false").lower() == "true"
    
    if use_dummy_data:
        print("더미 데이터 사용 중...")
        dummy_data = get_dummy_data(keyword)
        return jsonify(dummy_data)
    
    # 실제 API 호출
    result = api.search_bookstores(keyword=keyword, page_no=page)
    
    if "error" in result:
        print(f"검색 오류: {result['error']}")
        return jsonify({"error": result["error"], "suggestion": get_search_suggestion()})
    
    # 검색 결과 포맷팅
    formatted_stores = []
    for store in result["stores"]:
        formatted_stores.append(format_bookstore_info(store))
    
    print(f"검색 결과: {len(formatted_stores)}개 항목 찾음")
    
    # AI 분석 비활성화
    ai_analysis = "AI 분석 기능이 비활성화되었습니다. 검색 결과만 표시합니다."
    
    return jsonify({
        "stores": formatted_stores,
        "total_count": result["total_count"],
        "ai_analysis": ai_analysis
    })

def get_search_suggestion():
    """검색 제안을 반환합니다."""
    return {
        "message": "더 간단한 키워드로 다시 시도해보세요.",
        "examples": [
            "'구로' (O), '구로구' (X)",
            "'강남' (O), '강남구' (X)",
            "'서울', '부산'과 같은 도시명"
        ]
    }

def get_dummy_data(keyword):
    """테스트용 더미 데이터를 반환합니다."""
    dummy_stores = [
        {
            "title": f"{keyword} 북카페",
            "address": "서울특별시 강남구 테헤란로 123",
            "contact": "02-123-4567",
            "description": "아늑한 분위기의 북카페입니다. 다양한 책과 함께 커피를 즐길 수 있습니다.",
            "sub_description": "영업시간: 10:00-22:00, 주차 가능, 와이파이 제공",
            "coordinates": "37.123456,127.123456"
        },
        {
            "title": f"책과 커피 {keyword}점",
            "address": "서울특별시 마포구 홍대로 456",
            "contact": "02-456-7890",
            "description": "다양한 장르의 책과 맛있는 커피를 함께 즐길 수 있는 공간입니다.",
            "sub_description": "영업시간: 11:00-23:00, 주차 불가, 와이파이 제공, 콘센트 완비",
            "coordinates": "37.654321,127.654321"
        },
        {
            "title": f"북스토리 {keyword}",
            "address": "서울특별시 종로구 인사동길 789",
            "contact": "02-789-0123",
            "description": "전통과 현대가 어우러진 공간에서 책과 차를 즐길 수 있습니다.",
            "sub_description": "영업시간: 09:00-21:00, 주차 가능(유료), 와이파이 제공, 전통차 전문",
            "coordinates": "37.987654,127.987654"
        }
    ]
    
    return {
        "stores": dummy_stores,
        "total_count": len(dummy_stores),
        "ai_analysis": f"'{keyword}'에 대한 검색 결과입니다. 더미 데이터를 사용하고 있습니다."
    }

def get_ai_analysis(keyword, stores):
    """AI 분석을 요청합니다."""
    # AI 분석 비활성화
    return "AI 분석 기능이 비활성화되었습니다."

@app.route('/exit')
def exit_app():
    """앱 종료 (웹 애플리케이션에서는 로그아웃 또는 홈으로 리디렉션)"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    # 템플릿 디렉토리 생성
    os.makedirs('templates', exist_ok=True)
    
    # 정적 파일 디렉토리 생성
    os.makedirs('static', exist_ok=True)
    
    # 개발 서버 실행
    app.run(debug=True) 