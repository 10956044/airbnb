from flask import Flask, render_template, jsonify, request
from database import get_db_connection
import psycopg2

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.json
        district = data.get('city')  # 現在接收的是區域名稱
        room_type = data.get('roomType')
        min_price = data.get('minPrice')
        max_price = data.get('maxPrice')
        min_rating = data.get('rating')
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 構建基本查詢
        query = """
            SELECT DISTINCT r.room_id, r.room_name, r.room_type, r.price, r.rating, r.description, c.city_name 
            FROM room r 
            JOIN cities c ON r.city_id = c.city_id 
            WHERE c.city_name = %s
        """
        params = [district]
        
        if room_type:
            query += " AND r.room_type = %s"
            params.append(room_type)
        
        if min_price:
            query += " AND r.price >= %s"
            params.append(min_price)
            
        if max_price:
            query += " AND r.price <= %s"
            params.append(max_price)
            
        if min_rating:
            query += " AND r.rating >= %s"
            params.append(min_rating)
            
        query += """
            GROUP BY r.room_id, r.room_name, r.room_type, r.price, r.rating, r.description, c.city_name
            ORDER BY r.rating DESC
        """
        
        print(f"執行的 SQL 查詢: {query}")  # 調試信息
        print(f"查詢參數: {params}")  # 調試信息
        
        cur.execute(query, params)
        results = cur.fetchall()
        print(f"查詢結果數量: {len(results)}")  # 調試信息
        
        formatted_results = []
        for row in results:
            formatted_results.append({
                'room_id': row[0],
                'room_name': row[1],
                'room_type': row[2],
                'price': row[3],
                'rating': row[4],
                'description': row[5],
                'city_name': row[6]
            })
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True, 
            'data': formatted_results
        })
    
    except Exception as e:
        print(f"搜尋錯誤: {str(e)}")  # 調試信息
        return jsonify({'success': False, 'error': str(e)})

@app.route('/test_db')
def test_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 測試查詢 cities 表
        cur.execute("SELECT * FROM cities")
        cities = cur.fetchall()
        
        # 測試查詢 room 表
        cur.execute("SELECT * FROM room LIMIT 5")
        rooms = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '資料庫連接成功',
            'cities': cities,
            'rooms': rooms
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/check_data')
def check_data():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 查 cities 表的內容
        cur.execute("SELECT * FROM cities")
        cities = cur.fetchall()
        
        # 檢查 room 表的內容
        cur.execute("""
            SELECT r.*, c.city_name 
            FROM room r 
            JOIN cities c ON r.city_id = c.city_id 
            LIMIT 5
        """)
        rooms = cur.fetchall()
        
        # 檢查表的結構
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'room'
        """)
        room_structure = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'cities': cities,
            'rooms': rooms,
            'room_structure': room_structure
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/reviews/<room_id>', methods=['GET'])
def get_reviews(room_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 先檢查是否有這個房間
        cur.execute("SELECT room_id FROM room WHERE room_id = %s", [room_id])
        if not cur.fetchone():
            return jsonify({
                'success': False,
                'error': f'找不到房間 ID: {room_id}'
            })
        
        # 查詢評價
        query = """
            SELECT review_id, room_id, user_name, review_text, rating
            FROM reviews 
            WHERE room_id = %s 
            ORDER BY review_id DESC
        """
        
        print(f"執行評價查詢: {query} 參數: {room_id}")  # 調試信息
        
        cur.execute(query, [room_id])
        reviews = cur.fetchall()
        print(f"找到 {len(reviews)} 條評價")  # 調試信息
        
        formatted_reviews = []
        for review in reviews:
            formatted_reviews.append({
                'review_id': review[0],
                'room_id': review[1],
                'reviewer_name': review[2],  # user_name
                'comments': review[3],       # review_text
                'rating': review[4]          # rating
            })
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': formatted_reviews
        })
        
    except Exception as e:
        print(f"評價查詢錯誤: {str(e)}")  # 調試信息
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/check_reviews_table')
def check_reviews_table():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 檢查表結構
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'reviews'
        """)
        columns = cur.fetchall()
        
        # 檢查示例數據
        cur.execute("SELECT * FROM reviews LIMIT 5")
        sample_data = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'table_structure': columns,
            'sample_data': sample_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run() 