from kafka import KafkaProducer, KafkaConsumer
import psycopg2
import json
import time
import logging
import threading


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)


db_config = {
    'dbname': 'kafkadatabase',
    'user': 'kafkauser',
    'password': 'kafkapassword',
    'host': 'postgres',
    'port': 5432,
}


producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


consumer = KafkaConsumer(
    'back_to',
    bootstrap_servers='kafka:9092',
    auto_offset_reset='earliest',
    group_id='test-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)


def setup_database():
    try:
        conn = psycopg2.connect(**db_config)
        return conn
    except Exception as e:
        logging.error(f"Veritabanı ayarlanırken hata oluştu: {e}")
        raise


def producer_task():
    """
    Producer işlevi: Veritabanından yeni verileri alır ve Kafka'ya gönderir.
    """
    last_id = 0  

    while True:
        try:
            logging.info('Veriler fetch ediliyor...')
            data = fetch_data(last_id)  
            if data:
                for row in data:
                    message = {'id': row[0], 'name': row[1], 'value': row[2]}
                    producer.send('sample_topic', message) 
                    logging.info(f'Mesaj gönderildi: {message}')  

                    
                    last_id = max(last_id, row[0])
            else:
                logging.info('Yeni veri bulunamadı.')
            time.sleep(10)  
        except Exception as e:
            logging.error(f"Producer işlevi sırasında hata oluştu: {e}")


def fetch_data(last_id):
    """
    Veritabanından sadece yeni verileri çek.
    """
    try:
        conn = setup_database()
        cursor = conn.cursor()
        query = "SELECT id, name, value FROM sample_table WHERE id > %s ORDER BY id ASC;"
        cursor.execute(query, (last_id,))
        rows = cursor.fetchall()
        logging.info(f'{len(rows)} yeni veri fetch edildi.')  
    except Exception as e:
        logging.error(f'Fetch sırasında hata oluştu: {e}')
        rows = []
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
    return rows


def consumer_task():
    """
    Consumer işlevi: Kafka'dan gelen mesajları işler ve veritabanına kaydeder.
    """
    conn = setup_database()
    cursor = conn.cursor()
    try:
        logging.info("Kafka Consumer başlatılıyor...")
        for message in consumer:
            logging.info(f"Mesaj alındı: {message.value}")
            data = message.value

            
            combined_column = f"{data['name']}{data['value']}_Furkan_Marifoğlu"
            new_value = data['value'] * 4
            processed_data = (data['name'], new_value, combined_column)

            
            cursor.execute('''
                INSERT INTO third_table (name, value, combined_column)
                VALUES (%s, %s, %s);
            ''', processed_data)
            conn.commit()
            logging.info(f"Veritabanına eklendi: {processed_data}")
    except Exception as e:
        logging.error(f"Tüketim sırasında hata oluştu: {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
   
    producer_thread = threading.Thread(target=producer_task, daemon=True)
    consumer_thread = threading.Thread(target=consumer_task, daemon=True)

   
    producer_thread.start()
    consumer_thread.start()

   
    while True:
        time.sleep(1)
