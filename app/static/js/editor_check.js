function editor_check() {
    document.addEventListener("DOMContentLoaded", () => {
        fetch('/fetch/editor-info')
            .then(res => res.json())
            .then(data => {
                const msg = document.getElementById('scopeMessage');
                const adminBox = document.getElementById('adminScopeBox');

                if (data.error) {
                    msg.textContent = '인증된 편집자 또는 관리자만 사용 가능합니다.';
                    msg.className = 'error';
                    return;
                }

                if (data.role === 'admin') {
                    msg.textContent = '관리자 모드 - 범위를 수동 지정하세요.';
                    msg.className = 'success';
                    adminBox.style.display = 'block';
                    loadUnivList(); // 셀렉트박스 초기화
                } else {
                    // 승인된 편집자
                    const { univ, college, major, aff_council } = data;
                    let fullScope = univ;
                    if (aff_council === 'college') fullScope = `${univ} ${college}`;
                    else if (aff_council === 'major') fullScope = `${univ} ${college} ${major}`;
                    msg.textContent = `혜택 적용 범위: ${fullScope}`;
                    msg.className = 'success';
                }
            });
    });
}