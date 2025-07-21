function loadUnivList(targetId = "univ") {
    fetch('/api/univ-list')
    .then(res => res.json())
    .then(data => {
        const select = document.getElementById(targetId);
        select.innerHTML = '<option value="">대학교 선택</option>';
        data.forEach(univ => {
            const opt = document.createElement('option');
            opt.value = univ;
            opt.textContent = univ;
            select.appendChild(opt);
        });
    });
}

function updateCollegeOptions(univId = "univ", collegeId = "college") {
    const univ = document.getElementById(univId).value;
    fetch(`/api/college-list?univ=${encodeURIComponent(univ)}`)
    .then(res => res.json())
    .then(data => {
        const select = document.getElementById(collegeId);
        select.innerHTML = '<option value="">단과대학 선택</option>';
        data.forEach(college => {
            const opt = document.createElement('option');
            opt.value = college;
            opt.textContent = college;
            select.appendChild(opt);
        });
    });
}

function updateMajorOptions(univId = "univ", collegeId = "college", majorId = "major") {
    const univ = document.getElementById(univId).value;
    const college = document.getElementById(collegeId).value;
    fetch(`/api/major-list?univ=${encodeURIComponent(univ)}&college=${encodeURIComponent(college)}`)
    .then(res => res.json())
    .then(data => {
        const select = document.getElementById(majorId);
        select.innerHTML = '<option value="">학과 선택</option>';
        data.forEach(major => {
            const opt = document.createElement('option');
            opt.value = major;
            opt.textContent = major;
            select.appendChild(opt);
        });
    });
}
