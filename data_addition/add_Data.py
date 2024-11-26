import psycopg2
import time
import random
import string

db_config = {
    'dbname': 'kafkadatabase',
    'user': 'kafkauser',
    'password': 'kafkapassword',
    'host': 'postgres', 
    'port': 5432,
}

def generate_random_data():
    """
    Rastgele bir isim ve değer oluştur.
    """
    name = ''.join(random.choices(string.ascii_letters, k=10))  
    value = random.randint(1, 1000)  
    return name, value

def insert_data():
    """
    PostgreSQL'e her 10 saniyede bir rastgele veri ekle.
    """
    while True:
        try:
            
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            
            data = generate_random_data()

            
            insert_query = """
            INSERT INTO sample_table (name, value) VALUES (%s, %s);
            """
            
            
            cursor.execute(insert_query, data)
            conn.commit()

            print(f"Veri eklendi: {data}")

        except Exception as e:
            print(f"Hata oluştu: {e}")

        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

        
        time.sleep(10)

if __name__ == "__main__":
    insert_data()
