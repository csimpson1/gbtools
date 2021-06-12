import mariadb
import sys
#connect to old DB

def connect(db):
    try:
        conn = mariadb.connect(
            user='root',
            host='localhost',
            port=3306,
            database=db
            )
        
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(-1)
    
    cur = conn.cursor()
    print("connected!")
    return (conn, cur)


if __name__ == '__main__':
        """
        Compare the old DB against the new one, and note if there are any mismatches found
        """
        query = """select * from opcodes_v"""
        
        (oldDBConn, oldDBCur) = connect('gameboy_opcodes')
        oldDBCur.execute(query)
        oldResults = oldDBCur.fetchall()
        
        oldDBCur.close()
        oldDBConn.close()
        
        (newDBConn, newDBCur) = connect('MDB_GBDB')
        newDBCur.execute(query)
        newResults = newDBCur.fetchall()
        
        newDBCur.close()
        newDBConn.close()
        
        print(f'Old DB Size: {len(oldResults)}, New DB Size: {len(newResults)}')
        
        mismatches = {}
        
        for i, row in enumerate(oldResults):
            newRow = newResults[i]
            oldRow = oldResults[i]
            
            for j in range(len(oldRow)):
                if newRow[j] != oldRow[j]:
                    print(f'Mismatch found in row {j} of result sets. Old: {oldRow[j]} New: {newRow[j]}')
        
        