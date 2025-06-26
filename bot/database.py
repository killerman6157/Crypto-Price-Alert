import sqlite3
import os

# Sunan fayil din database. Zai kasance a cikin jakar "bot".
DB_NAME = 'crypto_alerts.db'
# Hanyar cikakkiyar zuwa fayil din database
# Wannan yana tabbatar cewa database din yana cikin jakar "bot"
DB_PATH = os.path.join(os.path.dirname(__file__), DB_NAME)

def init_db():
    """
    Wannan aikin zai fara database kuma ya kirkiri tebur (table) idan bai riga ya wanzu ba.
    Ya kamata a kira shi sau daya a farkon bot din ku (misali, a cikin main.py).
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                crypto_symbol TEXT NOT NULL,
                target_price REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        print(f"Database '{DB_NAME}' initialized successfully.")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        if conn:
            conn.close()

def add_alert(user_id: int, crypto_symbol: str, target_price: float) -> int | None:
    """
    Wannan aikin zai kara sabon faɗakarwa a database.
    Yana dawo da ID na faɗakarwar da aka ƙara, ko None idan akwai kuskure.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO alerts (user_id, crypto_symbol, target_price)
            VALUES (?, ?, ?)
        ''', (user_id, crypto_symbol, target_price))
        conn.commit()
        alert_id = cursor.lastrowid
        print(f"Alert added: User {user_id}, Crypto {crypto_symbol}, Target {target_price}. ID: {alert_id}")
        return alert_id
    except sqlite3.Error as e:
        print(f"Error adding alert: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_user_alerts(user_id: int) -> list[dict]:
    """
    Wannan aikin zai dawo da duk faɗakarwa (alerts) na wani mai amfani.
    Yana dawo da jerin dictionaries, inda kowane dictionary yake wakiltar faɗakarwa.
    """
    conn = None
    alerts = []
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row # Wannan yana sa row din ya dawo a matsayin dictionary-like object
        cursor = conn.cursor()
        cursor.execute('SELECT id, crypto_symbol, target_price FROM alerts WHERE user_id = ?', (user_id,))
        rows = cursor.fetchall()
        for row in rows:
            alerts.append(dict(row)) # Koma da kowane row zuwa dictionary
        print(f"Retrieved {len(alerts)} alerts for user {user_id}.")
    except sqlite3.Error as e:
        print(f"Error retrieving alerts for user {user_id}: {e}")
    finally:
        if conn:
            conn.close()
    return alerts

def delete_alert_from_db(alert_id: int, user_id: int) -> bool:
    """
    Wannan aikin zai share wata faɗakarwa daga database, yana tabbatar da cewa
    mai amfani ne mai mallakar faɗakarwar.
    Yana dawo da True idan an yi nasarar sharewa, ko False idan akwai kuskure.
    """
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM alerts WHERE id = ? AND user_id = ?', (alert_id, user_id))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Alert ID {alert_id} deleted successfully for user {user_id}.")
            return True
        else:
            print(f"No alert found with ID {alert_id} for user {user_id}, or not authorized.")
            return False
    except sqlite3.Error as e:
        print(f"Error deleting alert ID {alert_id} for user {user_id}: {e}")
        return False
    finally:
        if conn:
            conn.close()

# Misalin yadda zaka iya gwada ayyukan
if __name__ == '__main__':
    # Kira init_db don tabbatar da database da table sun wanzu
    init_db()

    # Misalin amfani:
    test_user_id = 12345
    test_crypto = "BTC"
    test_price = 70000.0

    print("\n--- Adding alerts ---")
    add_alert(test_user_id, "BTC", 70000.0)
    add_alert(test_user_id, "ETH", 4000.0)
    add_alert(test_user_id + 1, "ADA", 0.5) # Wani mai amfani

    print("\n--- Getting user alerts ---")
    alerts = get_user_alerts(test_user_id)
    print(f"Alerts for user {test_user_id}: {alerts}")

    print("\n--- Deleting an alert ---")
    if alerts:
        alert_to_delete_id = alerts[0]['id']
        delete_alert_from_db(alert_to_delete_id, test_user_id)
        print(f"Alerts after deletion: {get_user_alerts(test_user_id)}")
    else:
        print("No alerts to delete for this user.")

    print("\n--- Attempting to delete a non-existent or unauthorized alert ---")
    delete_alert_from_db(9999, test_user_id) # ID wanda bai wanzu ba
    delete_alert_from_db(1, test_user_id + 1) # Yana kokarin share na wani mai amfani
  
