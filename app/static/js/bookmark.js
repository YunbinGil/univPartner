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


