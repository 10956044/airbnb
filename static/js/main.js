// 添加顯示和隱藏 loading 的函數
function showLoading() {
    document.getElementById('loading').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

document.getElementById('searchBtn').addEventListener('click', async () => {
    const city = document.getElementById('cityInput').value.trim();
    
    // 檢查是否輸入行政區
    if (!city) {
        alert('請輸入行政區');
        return;
    }
    
    // 檢查是否為有效的台北市行政區
    const validDistricts = [
        '內湖區', '北投區', '南港區', '士林區', 
        '大同區', '大安區', '文山區', '松山區', 
        '萬華區', '中山區', '中正區', '信義區'
    ];
    
    if (!validDistricts.includes(city)) {
        alert('請輸入有效的台北市行政區（如：大安區、中正區等）');
        return;
    }
    
    const roomType = document.getElementById('roomType').value;
    const minPrice = document.getElementById('minPrice').value;
    const maxPrice = document.getElementById('maxPrice').value;
    const rating = document.getElementById('rating').value;
    
    try {
        // 顯示 loading 動畫
        showLoading();
        
        const response = await fetch('/api/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                city,
                roomType,
                minPrice,
                maxPrice,
                rating
            })
        });
        
        const data = await response.json();
        
        // 隱藏 loading 動畫
        hideLoading();
        
        if (data.success) {
            displayResults(data.data);
        } else {
            alert('搜尋發生錯誤：' + data.error);
        }
    } catch (error) {
        // 發生錯誤時也要隱藏 loading 動畫
        hideLoading();
        alert('發生錯誤：' + error);
    }
});

function displayResults(results) {
    const resultsContainer = document.getElementById('results');
    resultsContainer.innerHTML = '';
    
    if (results.length === 0) {
        resultsContainer.innerHTML = '<div class="no-results">此區域目前沒有符合條件的房源</div>';
        return;
    }
    
    results.forEach(room => {
        const roomElement = document.createElement('div');
        roomElement.className = 'room-card';
        roomElement.innerHTML = `
            <h3 class="room-title" data-room-id="${room.room_id}">${room.room_name}</h3>
            <p class="room-type">房型：${getRoomTypeName(room.room_type)}</p>
            <p class="price">價格：NT$ ${formatPrice(room.price)}</p>
            <p class="rating">評分：${getStarRating(room.rating)} ${room.rating}</p>
            <p class="description">${room.description || ''}</p>
            <p class="location">地點：${room.city_name}</p>
        `;
        resultsContainer.appendChild(roomElement);
        
        // 為飯店名稱添加點擊事件
        const titleElement = roomElement.querySelector('.room-title');
        titleElement.addEventListener('click', () => showReviews(room.room_id, room.room_name));
    });
    
    // 平滑滾動到結果區域
    resultsContainer.scrollIntoView({ behavior: 'smooth' });
}

function getRoomTypeName(type) {
    const types = {
        'Entire home apt': 'Entire home apt',
        'Private room': 'Private room',
        'Shared room': 'Shared room',
        'Hotel room': 'Hotel room'
    };
    return types[type] || type;
}

function formatPrice(price) {
    return price.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

// 添加顯示評價的函數
async function showReviews(roomId, roomName) {
    try {
        const response = await fetch(`/api/reviews/${roomId}`);
        const data = await response.json();
        
        if (data.success) {
            const modal = document.getElementById('reviewModal');
            const content = document.getElementById('reviewsContent');
            
            if (data.data.length === 0) {
                // 如果沒有評價
                content.innerHTML = '<div class="no-reviews">目前尚無住客評價</div>';
            } else {
                // 如果有評價
                content.innerHTML = data.data.map(review => `
                    <div class="review-item">
                        <div class="reviewer-name">${review.reviewer_name}</div>
                        <div class="review-rating">${getStarRating(review.rating)} ${review.rating}</div>
                        <div class="review-comment">${review.comments}</div>
                    </div>
                `).join('');
            }
            
            modal.style.display = 'block';
        } else {
            alert('獲取評價失敗：' + data.error);
        }
    } catch (error) {
        alert('發生錯誤：' + error);
    }
}

// 添加關閉懸浮視窗事件處理
document.querySelector('.close-modal').addEventListener('click', () => {
    document.getElementById('reviewModal').style.display = 'none';
});

// 點擊懸浮視窗外部時關閉
document.getElementById('reviewModal').addEventListener('click', (e) => {
    if (e.target.className === 'modal-overlay') {
        e.target.style.display = 'none';
    }
});

// 添加一個新的函數來轉換評分為星星顯示
function getStarRating(rating) {
    // 將10分制轉換為5星制，並無條件捨去
    const stars = Math.floor(rating / 2);
    return "⭐".repeat(stars);
} 