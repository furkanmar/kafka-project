from kafka import KafkaConsumer, KafkaProducer
import psycopg2
import json
import logging
import time
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


consumer = KafkaConsumer(
    'sample_topic',
    bootstrap_servers='kafka:9092',
    auto_offset_reset='latest',
    group_id='test-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    
)


producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def setup_database():
    """
    Veritabanı bağlantısını hazırlar.
    """
    try:
        conn = psycopg2.connect(**db_config)
        return conn
    except Exception as e:
        logging.error(f"Veritabanı ayarlanırken hata oluştu: {e}")
        raise

def process_message(data):
    """
    Kafka mesajını işler ve veritabanına ekler.
    """
    conn = setup_database()
    cursor = conn.cursor()
    try:
        # Yeni veriler oluştur
        combined_column = f"{data['name']}{data['value']}"
        new_value = data['value'] + 100
        processed_data = {
            'name': data['name'],
            'value': new_value,
            'combined_column': combined_column
        }

        # Veritabanına ekle
        cursor.execute('''
            INSERT INTO processed_data (name, value, combined_column)
            VALUES (%s, %s, %s);
        

                       
        ''', (processed_data['name'], processed_data['value'], processed_data['combined_column']))
        conn.commit()
        logging.info(f"Veritabanına eklendi: {processed_data}")

        # Kafka'ya geri gönder
        send_to_back(processed_data)
    except Exception as e:
        logging.error(f"Mesaj işlenirken hata oluştu: {e}")
    finally:
        cursor.close()
        conn.close()

def send_to_back(data):
    """
    Kafka'ya geri mesaj gönderir.
    """
    try:
        # Geri gönderilecek mesaj
        message = {
            'name': data['name'],
            'value': data['value'],
            'combined_column': data['combined_column']
        }
        producer.send('back_to', message)
        logging.info(f"Mesaj işlendi ve geri gönderildi: {message}")
    except Exception as e:
        logging.error(f"Mesaj gönderiminde hata oluştu: {e}")

def consume_messages():
    """
    Kafka'dan mesajları dinler ve işler.
    """
    logging.info("Kafka Consumer başlatılıyor...")
    for message in consumer:
        try:
            logging.info(f"Mesaj alındı: {message.value}")
            process_message(message.value)
        except Exception as e:
            logging.error(f"Mesaj tüketimi sırasında hata oluştu: {e}")

def producer_task():
    """
    Producer işlevi: Veritabanından yeni verileri alır ve Kafka'ya gönderir.
    """
    last_id = 0

    while True:
        try:
            logging.info('Producer: Veriler fetch ediliyor...')
            data = fetch_data(last_id) 
            if data:
                for row in data:
                    message = {'id': row[0], 'name': row[1], 'value': row[2]}
                    producer.send('sample_topic', message)  
                    logging.info(f'Producer: Mesaj gönderildi: {message}')  

                    # Son ID'yi güncelle
                    last_id = max(last_id, row[0])
            else:
                logging.info('Producer: Yeni veri bulunamadı.')
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

if __name__ == '__main__':
    
    producer_thread = threading.Thread(target=producer_task, daemon=True)
    consumer_thread = threading.Thread(target=consume_messages, daemon=True)

    
    producer_thread.start()
    consumer_thread.start()

    
    while True:
        time.sleep(1)
