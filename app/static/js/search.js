let selectedScopes = new Set();
let selectedTypes = new Set();
let selectedCategory = null;

let typeOptions = ["할인", "제공", "이벤트", "새내기 혜택"];  // 예시
let categoryOptions = ["건강", "교육", "엔터", "미용", "의류", "주거", "카페", "음식점", "호프"];
let benefitTypeMap = {
  "할인": 1, "제공": 2, "이벤트": 3, "새내기 혜택": 4
};

function openModal() {
    document.getElementById('modalOverlay').style.display = 'block';
    document.getElementById('conditionModal').classList.add('active');
}

function closeModal() {
    document.getElementById('modalOverlay').style.display = 'none';
    document.getElementById('conditionModal').classList.remove('active');
}

function renderScopeButtons(scopeData) {
    const container = document.getElementById("scope-buttons");
    container.innerHTML = "";

    const options = [
        scopeData.univ,
        `${scopeData.univ} ${scopeData.college}`,
        `${scopeData.univ} ${scopeData.college} ${scopeData.major}`
    ];

    options.forEach(option => {
        const btn = document.createElement("button");
        btn.className = "toggle-btn";
        btn.textContent = option;
        btn.onclick = () => {
            if (selectedScopes.has(option)) {
                selectedScopes.delete(option);
                btn.classList.remove("active");
            } else {
                selectedScopes.add(option);
                btn.classList.add("active");
            }
            document.getElementById('scope-count').textContent = `(${selectedScopes.size}/3)`;
        };
        container.appendChild(btn);
    });
}

function createToggleButtons(containerId, options, mode, onSelect, countSpanId = null) {
    const container = document.getElementById(containerId);
    container.innerHTML = "";

    options.forEach(option => {
        const btn = document.createElement("button");
        btn.className = "toggle-btn";
        btn.textContent = option;

        btn.onclick = () => {
            if (mode === "single") {
                onSelect(option);
                [...container.children].forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
            } else {
                if (selectedTypes.has(option)) {
                    selectedTypes.delete(option);
                    btn.classList.remove("active");
                } else {
                    selectedTypes.add(option);
                    btn.classList.add("active");
                }
                if (countSpanId) {
                    const countSpan = document.getElementById(countSpanId);
                    countSpan.textContent = `(${selectedTypes.size}/${options.length})`;
                }
            }
        };

        container.appendChild(btn);
    });

    // 초기화 시 count도 세팅
    if (mode === "multi" && countSpanId) {
        document.getElementById(countSpanId).textContent = `(0/${options.length})`;
    }
}

function resetFilters() {
    selectedScopes.clear();
    selectedTypes.clear();
    selectedCategory = null;

    createToggleButtons('type-buttons', typeOptions, "multi", null, "type-count");
    createToggleButtons('category-buttons', categoryOptions, "single", val => selectedCategory = val);


    fetch('/fetch/scope-info')
        .then(res => res.json())
        .then(data => {
            if (!data.error) {
                renderScopeButtons(data);  // ✅ 유저 scope 렌더링
            }
        });
}

function applyFilters() {
    const typeIds = [...selectedTypes].map(name => benefitTypeMap[name]);
    sessionStorage.setItem('selectedTypeIds', JSON.stringify(typeIds));
    console.log("benefitTypeMap:", benefitTypeMap);

    sessionStorage.setItem('selectedScopes', JSON.stringify([...selectedScopes]));
    sessionStorage.setItem('selectedCategory', selectedCategory);

    closeModal();

    // 👇 여기 부분은 페이지에 따라 커스터마이즈 필요
    if (typeof loadMarkers === 'function') {
        loadMarkers();  // 💡 지도 페이지일 경우
    } else {
        GoSearch();     // 🔎 검색 페이지일 경우
    }
    alert("적용된 조건:\n" + JSON.stringify({
        scope: [...selectedScopes],
        type_ids: [typeIds],
        category: selectedCategory
    }, null, 2));

}

function GoSearch() {
    const keyword = document.getElementById('searchInput').value.trim();
    sessionStorage.setItem('searchWord', keyword);
    const searchTarget = document.getElementById('searchTarget').value;
    sessionStorage.setItem('target', searchTarget);
    // 조건 저장

    const scopes = sessionStorage.getItem('selectedScopes');
    const typeIds = sessionStorage.getItem('selectedTypeIds');
    const category = sessionStorage.getItem('selectedCategory');

    // ✅ form 생성해서 POST 전송
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/search';

    const appendField = (name, value) => {
        if (value) {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = name;
            input.value = value;
            form.appendChild(input);
        }
    };

    if (keyword) appendField('keyword', keyword);
    if (searchTarget) appendField('target', searchTarget);
    if (scopes) appendField('scopes', scopes);
    if (typeIds) appendField('type_ids', typeIds);
    if (category) appendField('category', category);

    document.body.appendChild(form);
    form.submit();
}

function insertConditionModal() {
    const modalHtml = `
    <div class="modal-overlay" id="modalOverlay" onclick="closeModal()">
        <div class="modal" id="conditionModal" onclick="event.stopPropagation()">
            <div class="modal-header">상세조건 설정</div>

            <div class="filter-group">
                <span>제휴 범위 (복수 선택 가능)<span id="scope-count">(0/3)</span></span><br>
                <div id="scope-buttons"></div>
            </div>

            <div class="filter-group">
                <span>혜택 형태 (복수 선택 가능)<span id="type-count">(0/4)</span></span><br>
                <div id="type-buttons"></div>
            </div>

            <div class="filter-group">
                <span>카테고리 (1개 선택)</span><br>
                <div id="category-buttons"></div>
            </div>

            <button onclick="resetFilters()">초기화</button>
            <button onclick="applyFilters()">적용하기</button>
        </div>
    </div>`;
    document.body.insertAdjacentHTML('beforeend', modalHtml);
}
