function toggleBookmark(partnerId) {
    fetch('/bookmark/toggle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `partner_id=${partnerId}`
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'added') {
            alert("북마크에 추가됨!");
        } else if (data.status === 'removed') {
            alert("북마크에서 제거됨!");
        } else if (data.error) {
            alert("⚠️ " + data.error);
        }
    });
}

function openBookmarkDialog(partnerId) {
    const overlay = document.getElementById('bookmarkModalOverlay');
    const modal = document.getElementById('bookmarkModal');
    overlay.classList.add('active');
    overlay.dataset.partnerId = partnerId;

    // 폴더 목록 불러오기
    fetch('/bookmark/folders')
        .then(res => res.json())
        .then(folders => {
            const select = document.getElementById('folder-select');
            select.innerHTML = '';
            folders.forEach(name => {
                const opt = document.createElement('option');
                opt.value = name;
                opt.textContent = name;
                select.appendChild(opt);
            });
        });
}

function closeBookmarkModal() {
    document.getElementById('bookmarkModalOverlay').classList.remove('active');
}



function confirmBookmark() {
    const partnerId = document.getElementById('bookmarkModalOverlay').dataset.partnerId;
    const folderSelect = document.getElementById('folder-select');
    const folderName = folderSelect.value || document.getElementById('new-folder-input').value;

    if (!folderName.trim()) {
        alert("폴더명을 입력하세요.");
        return;
    }

    fetch('/bookmark/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: new URLSearchParams({
            partner_id: partnerId,
            folder_name: folderName
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'added') {
            alert("북마크에 추가됨!");
        } else if (data.status === 'removed') {
            alert("북마크에서 제거됨!");
        } else if (data.error) {
            alert("⚠️ " + data.error);
        }

        closeBookmarkModal();
    });
}

function deleteBookmark() {
    const partnerId = document.getElementById('bookmarkModalOverlay').dataset.partnerId;
    const folderSelect = document.getElementById('folder-select');
    const folderName = folderSelect.value;

    if (!folderName) {
        alert("삭제할 폴더를 선택하세요.");
        return;
    }

    fetch('/bookmark/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
            partner_id: partnerId,
            folder_name: folderName
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'deleted') {
            alert("북마크에서 삭제됨!");
        } else if (data.error) {
            alert("⚠️ " + data.error);
        }

        closeBookmarkModal();
    });
}

function addNewFolderOption() {
    const input = document.getElementById('new-folder-input');
    const folderName = input.value.trim();
    if (!folderName) {
        alert("폴더명을 입력하세요.");
        return;
    }

    const select = document.getElementById('folder-select');
    
    // 중복 방지
    for (let opt of select.options) {
        if (opt.value === folderName) {
            alert("이미 존재하는 폴더입니다.");
            return;
        }
    }

    const opt = document.createElement('option');
    opt.value = folderName;
    opt.textContent = folderName;
    opt.selected = true;
    select.appendChild(opt);

    input.value = '';
    select.focus();  // ✨ 폴더 선택박스로 포커스 옮기기
}



