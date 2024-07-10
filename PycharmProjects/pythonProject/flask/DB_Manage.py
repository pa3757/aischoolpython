import cx_Oracle

def db_conn() :
    try:
        conn = cx_Oracle.connect('hr','12345','localhost:1521/xe')
        cur = conn.cursor()
        print("DB 연결 성공")
        return conn, cur
    except cx_Oracle.DatabaseError as e:
        print(e)

def db_disconn(conn, cur) :
    try:
        cur.close()
        conn.close()
        print("DB 연결 종료")
    except cx_Oracle.DatabaseError as e:
        print(e)

def db_search(cur, id_val, pw_val):
    try:
        sql = f"select code,name,age from member_tb1 where id='{id_val}' and pw='{pw_val}'"
        cur.execute(sql)
        return cur.fetchone()
    except cx_Oracle.DatabaseError as e:
        print(e)
