import psycopg2

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host='lallah.db.elephantsql.com',
            database='sedogkif',
            user='sedogkif',
            password='qLh1jqvjo-y4ofkkGp2bYsNQ94NbX_ZS'
        )
        print("資料庫連接成功！")
        return conn
    except Exception as e:
        print(f"資料庫連接錯誤：{str(e)}")
        raise e

# 測試連接
if __name__ == "__main__":
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 測試查詢
        cur.execute("SELECT * FROM cities LIMIT 1")
        result = cur.fetchone()
        print("測試查詢結果：", result)
        
        cur.close()
        conn.close()
        print("資料庫連接測試完成")
    except Exception as e:
        print(f"測試失敗：{str(e)}") 