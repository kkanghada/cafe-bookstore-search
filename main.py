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
    
    # 테스트용 더미 데이터 설정 (기본값: false)
    use_dummy_data = os.getenv("USE_DUMMY_DATA", "false").lower() == "true"
    
    # 실제 API 호출 (더미 데이터 모드가 아닌 경우)
    if not use_dummy_data:
        print("실제 API 호출 중...")
        result = api.search_bookstores(keyword=keyword, page_no=page)
        
        # API 호출 성공 시 실제 데이터 반환
        if "error" not in result:
            # 검색 결과 포맷팅
            formatted_stores = []
            for store in result["stores"]:
                formatted_stores.append(format_bookstore_info(store))
            
            print(f"API 검색 결과: {len(formatted_stores)}개 항목 찾음")
            
            # AI 분석 비활성화
            ai_analysis = "AI 분석 기능이 비활성화되었습니다. 검색 결과만 표시합니다."
            
            return jsonify({
                "stores": formatted_stores,
                "total_count": result["total_count"],
                "ai_analysis": ai_analysis,
                "data_source": "real_api"
            })
        else:
            print(f"API 오류: {result['error']} - 더미 데이터로 폴백")
    else:
        print("더미 데이터 모드 활성화됨")
    
    # API 호출 실패 또는 더미 데이터 모드인 경우 더미 데이터 사용
    dummy_data = get_dummy_data(keyword)
    dummy_data["data_source"] = "dummy"
    return jsonify(dummy_data)

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
    # 검색어에 따라 다른 데이터 반환
    if '응암' in keyword:
        dummy_stores = [
            {
                "title": "응암 북카페",
                "address": "서울특별시 은평구 응암동 579-1",
                "contact": "02-123-4567",
                "description": "응암동에 위치한 아늑한 분위기의 북카페입니다. 다양한 책과 함께 커피를 즐길 수 있습니다.",
                "sub_description": "영업시간: 10:00-22:00, 주차 가능, 와이파이 제공",
                "coordinates": "37.5839,126.9149"
            },
            {
                "title": "응암동 책방",
                "address": "서울특별시 은평구 응암동 427-5",
                "contact": "02-372-8901",
                "description": "조용한 분위기에서 독서를 즐길 수 있는 응암동의 작은 책방입니다.",
                "sub_description": "영업시간: 11:00-20:00, 주차 불가, 와이파이 제공, 독서모임 운영",
                "coordinates": "37.5841,126.9152"
            },
            {
                "title": "은평 북스페이스",
                "address": "서울특별시 은평구 응암로 172",
                "contact": "02-383-4567",
                "description": "은평구에 위치한 복합문화공간으로, 책과 함께 다양한 문화 활동을 즐길 수 있습니다.",
                "sub_description": "영업시간: 09:00-21:00, 주차 가능, 와이파이 제공, 문화 프로그램 운영",
                "coordinates": "37.5830,126.9160"
            }
        ]
    elif '강남' in keyword:
        dummy_stores = [
            {
                "title": "강남 책방",
                "address": "서울특별시 강남구 역삼동 테헤란로 152",
                "contact": "02-555-7890",
                "description": "강남역 인근에 위치한 모던한 분위기의 북카페입니다.",
                "sub_description": "영업시간: 09:00-23:00, 주차 가능(유료), 와이파이 제공, 스터디룸 보유",
                "coordinates": "37.5002,127.0365"
            },
            {
                "title": "책과 커피 강남점",
                "address": "서울특별시 강남구 논현동 학동로 212",
                "contact": "02-512-9876",
                "description": "다양한 장르의 책과 맛있는 커피를 함께 즐길 수 있는 공간입니다.",
                "sub_description": "영업시간: 11:00-22:00, 주차 불가, 와이파이 제공, 콘센트 완비",
                "coordinates": "37.5114,127.0216"
            },
            {
                "title": "북스토리 강남",
                "address": "서울특별시 강남구 삼성동 테헤란로 87길 22",
                "contact": "02-567-3456",
                "description": "IT, 경영, 자기계발 서적을 중심으로 한 전문 서점입니다.",
                "sub_description": "영업시간: 10:00-22:00, 주차 가능, 와이파이 제공, 세미나 공간 대여",
                "coordinates": "37.5080,127.0579"
            },
            {
                "title": "리딩라운지 강남",
                "address": "서울특별시 강남구 신사동 가로수길 43",
                "contact": "02-541-8765",
                "description": "트렌디한 가로수길에 위치한 감성 북카페입니다.",
                "sub_description": "영업시간: 12:00-23:00, 주차 불가, 와이파이 제공, 디저트 전문",
                "coordinates": "37.5209,127.0227"
            }
        ]
    elif '홍대' in keyword:
        dummy_stores = [
            {
                "title": "홍대 책방",
                "address": "서울특별시 마포구 서교동 와우산로 123",
                "contact": "02-332-5678",
                "description": "홍대 인근에 위치한 독립서점으로, 다양한 독립출판물을 만나볼 수 있습니다.",
                "sub_description": "영업시간: 13:00-22:00, 주차 불가, 와이파이 제공, 독립출판 워크샵 운영",
                "coordinates": "37.5536,126.9235"
            },
            {
                "title": "아트북스 홍대",
                "address": "서울특별시 마포구 서교동 어울마당로 92",
                "contact": "02-323-7890",
                "description": "예술, 디자인 서적을 전문으로 하는 북카페입니다.",
                "sub_description": "영업시간: 12:00-22:00, 주차 불가, 와이파이 제공, 아트 전시 공간 운영",
                "coordinates": "37.5525,126.9245"
            },
            {
                "title": "카페 북스테이",
                "address": "서울특별시 마포구 연남동 동교로 203",
                "contact": "02-336-4567",
                "description": "연남동에 위치한 아늑한 분위기의 북카페입니다.",
                "sub_description": "영업시간: 11:00-23:00, 주차 불가, 와이파이 제공, 수제 디저트 판매",
                "coordinates": "37.5605,126.9245"
            }
        ]
    elif '구로' in keyword:
        dummy_stores = [
            {
                "title": "구로 북스토리",
                "address": "서울특별시 구로구 구로동 디지털로 300",
                "contact": "02-868-1234",
                "description": "구로디지털단지 인근에 위치한 IT 특화 북카페입니다.",
                "sub_description": "영업시간: 09:00-21:00, 주차 가능, 와이파이 제공, IT 관련 도서 특화",
                "coordinates": "37.4833,126.8982"
            },
            {
                "title": "구로 책마을",
                "address": "서울특별시 구로구 신도림동 경인로 662",
                "contact": "02-864-5678",
                "description": "신도림역 인근에 위치한 가족 친화적 북카페입니다.",
                "sub_description": "영업시간: 10:00-20:00, 주차 가능, 와이파이 제공, 어린이 도서 특화",
                "coordinates": "37.5087,126.8909"
            },
            {
                "title": "디지털 북센터",
                "address": "서울특별시 구로구 구로동 디지털로 273",
                "contact": "02-856-7890",
                "description": "최신 IT 트렌드와 디지털 관련 서적을 만나볼 수 있는 공간입니다.",
                "sub_description": "영업시간: 09:00-22:00, 주차 가능, 와이파이 제공, 코딩 스터디 모임 운영",
                "coordinates": "37.4845,126.8965"
            }
        ]
    elif '서울' in keyword:
        dummy_stores = [
            {
                "title": "서울책방",
                "address": "서울특별시 중구 세종대로 110",
                "contact": "02-120",
                "description": "서울시청 1층에 위치한 공공 북카페로, 서울 관련 도서를 중심으로 다양한 책을 만나볼 수 있습니다.",
                "sub_description": "영업시간: 09:00-21:00, 주차 가능(유료), 와이파이 제공, 서울 관련 도서 특화",
                "coordinates": "37.5662,126.9785"
            },
            {
                "title": "서울북스",
                "address": "서울특별시 종로구 종로 19",
                "contact": "02-722-5678",
                "description": "종로에 위치한 대형 서점으로, 다양한 장르의 책과 함께 카페를 운영합니다.",
                "sub_description": "영업시간: 10:00-22:00, 주차 가능(유료), 와이파이 제공, 문화행사 개최",
                "coordinates": "37.5707,126.9825"
            },
            {
                "title": "청계천 북카페",
                "address": "서울특별시 중구 청계천로 40",
                "contact": "02-2268-7890",
                "description": "청계천 인근에 위치한 아늑한 분위기의 북카페입니다.",
                "sub_description": "영업시간: 11:00-21:00, 주차 불가, 와이파이 제공, 청계천 뷰 보유",
                "coordinates": "37.5689,126.9845"
            },
            {
                "title": "광화문 책사랑",
                "address": "서울특별시 종로구 세종로 175",
                "contact": "02-735-4567",
                "description": "광화문 광장 인근에 위치한 역사, 문화 특화 북카페입니다.",
                "sub_description": "영업시간: 09:00-20:00, 주차 불가, 와이파이 제공, 역사 관련 도서 특화",
                "coordinates": "37.5725,126.9768"
            }
        ]
    else:
        # 기본 더미 데이터 (여러 개 생성)
        dummy_stores = [
            {
                "title": f"{keyword} 북카페",
                "address": f"서울특별시 {keyword} 인근 123번지",
                "contact": "02-123-4567",
                "description": f"{keyword} 지역에 위치한 아늑한 분위기의 북카페입니다.",
                "sub_description": "영업시간: 10:00-22:00, 주차 가능, 와이파이 제공",
                "coordinates": "37.5665,126.9780"
            },
            {
                "title": f"책과 커피 {keyword}점",
                "address": f"서울특별시 {keyword} 인근 456번지",
                "contact": "02-456-7890",
                "description": f"{keyword} 지역에서 다양한 장르의 책과 맛있는 커피를 즐길 수 있는 공간입니다.",
                "sub_description": "영업시간: 11:00-23:00, 주차 불가, 와이파이 제공, 콘센트 완비",
                "coordinates": "37.5670,126.9785"
            },
            {
                "title": f"{keyword} 리딩라운지",
                "address": f"서울특별시 {keyword} 인근 789번지",
                "contact": "02-789-0123",
                "description": f"{keyword} 지역의 조용한 분위기에서 독서를 즐길 수 있는 공간입니다.",
                "sub_description": "영업시간: 12:00-21:00, 주차 가능(유료), 와이파이 제공, 독서모임 운영",
                "coordinates": "37.5675,126.9790"
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