document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const keywordInput = document.getElementById('keyword');
    const loadingElement = document.getElementById('loading');
    const errorContainer = document.getElementById('errorContainer');
    const errorMessage = document.getElementById('errorMessage');
    const suggestionMessage = document.getElementById('suggestionMessage');
    const suggestionExamples = document.getElementById('suggestionExamples');
    const resultsContainer = document.getElementById('resultsContainer');
    const resultCount = document.getElementById('resultCount');
    const resultsList = document.getElementById('resultsList');
    const aiAnalysis = document.getElementById('aiAnalysis');

    // 검색 폼 제출 이벤트 처리
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const keyword = keywordInput.value.trim();
        
        if (!keyword) {
            showError('검색어를 입력해주세요.');
            return;
        }
        
        performSearch(keyword);
    });

    // 검색 실행 함수
    function performSearch(keyword) {
        // UI 초기화
        showLoading(true);
        hideError();
        hideResults();
        
        // FormData 생성
        const formData = new FormData();
        formData.append('keyword', keyword);
        formData.append('page', 1);
        
        // 서버에 검색 요청
        fetch('/search', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            showLoading(false);
            
            if (data.error) {
                showError(data.error, data.suggestion);
                return;
            }
            
            displayResults(data);
        })
        .catch(error => {
            showLoading(false);
            showError('서버 연결 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.');
            console.error('Error:', error);
        });
    }

    // 로딩 표시 함수
    function showLoading(show) {
        if (show) {
            loadingElement.classList.remove('d-none');
        } else {
            loadingElement.classList.add('d-none');
        }
    }

    // 오류 표시 함수
    function showError(message, suggestion) {
        errorMessage.textContent = message;
        errorContainer.classList.remove('d-none');
        
        // 검색 제안이 있는 경우
        if (suggestion) {
            suggestionMessage.textContent = suggestion.message;
            suggestionExamples.innerHTML = '';
            
            suggestion.examples.forEach(example => {
                const li = document.createElement('li');
                li.textContent = example;
                suggestionExamples.appendChild(li);
            });
        } else {
            suggestionMessage.textContent = '';
            suggestionExamples.innerHTML = '';
        }
    }

    // 오류 숨기기 함수
    function hideError() {
        errorContainer.classList.add('d-none');
    }

    // 결과 숨기기 함수
    function hideResults() {
        resultsContainer.classList.add('d-none');
    }

    // 검색 결과 표시 함수
    function displayResults(data) {
        resultCount.textContent = data.total_count;
        resultsList.innerHTML = '';
        
        // 서점 정보 카드 생성
        data.stores.forEach(store => {
            const storeCard = createStoreCard(store);
            resultsList.appendChild(storeCard);
        });
        
        // AI 분석 표시
        aiAnalysis.textContent = data.ai_analysis || '분석 정보가 없습니다.';
        
        // 결과 컨테이너 표시
        resultsContainer.classList.remove('d-none');
    }

    // 서점 카드 생성 함수
    function createStoreCard(store) {
        const col = document.createElement('div');
        col.className = 'col-md-6 col-lg-4 mb-4';
        
        const card = document.createElement('div');
        card.className = 'card store-card h-100';
        
        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';
        
        // 서점 이름
        const title = document.createElement('h5');
        title.className = 'card-title';
        title.textContent = store.title;
        cardBody.appendChild(title);
        
        // 주소
        if (store.address) {
            const address = document.createElement('p');
            address.className = 'card-text';
            address.innerHTML = '<span class="store-info-label">📍 주소:</span>' + store.address;
            cardBody.appendChild(address);
        }
        
        // 연락처
        if (store.contact) {
            const contact = document.createElement('p');
            contact.className = 'card-text';
            contact.innerHTML = '<span class="store-info-label">☎️ 연락처:</span>' + store.contact;
            cardBody.appendChild(contact);
        }
        
        // 설명
        if (store.description) {
            const description = document.createElement('p');
            description.className = 'card-text';
            description.innerHTML = '<span class="store-info-label">ℹ️ 설명:</span>' + store.description;
            cardBody.appendChild(description);
        }
        
        // 상세 정보 (접을 수 있는 형태로)
        if (store.sub_description) {
            const detailsContainer = document.createElement('div');
            detailsContainer.className = 'mt-3';
            
            const detailsButton = document.createElement('button');
            detailsButton.className = 'btn btn-sm btn-outline-primary';
            detailsButton.setAttribute('type', 'button');
            detailsButton.setAttribute('data-bs-toggle', 'collapse');
            detailsButton.setAttribute('data-bs-target', `#details-${store.title.replace(/\s+/g, '-')}`);
            detailsButton.textContent = '상세 정보 보기';
            
            const detailsContent = document.createElement('div');
            detailsContent.className = 'collapse mt-2';
            detailsContent.id = `details-${store.title.replace(/\s+/g, '-')}`;
            
            const detailsText = document.createElement('p');
            detailsText.className = 'card-text small';
            detailsText.innerHTML = '<span class="store-info-label">🔍 상세정보:</span>' + store.sub_description;
            
            detailsContent.appendChild(detailsText);
            detailsContainer.appendChild(detailsButton);
            detailsContainer.appendChild(detailsContent);
            cardBody.appendChild(detailsContainer);
        }
        
        card.appendChild(cardBody);
        col.appendChild(card);
        
        return col;
    }
}); 