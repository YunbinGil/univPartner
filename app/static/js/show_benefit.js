function loadBenefit(targetId="benefitBox", userId, scopeStr, categoryId, btype){
    fetch('benefit/list')
    .then(res => res.json())
    .then(data => {
        const benefixBox = document.getElementById("benefitBox")
    })
}