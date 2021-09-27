from imbox import Imbox
import threading
import datetime, requests, os
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
gauth = GoogleAuth()         
drive = GoogleDrive(gauth)

def uploading(folder_id, file_name):
        gfile = drive.CreateFile({'title': file_name,'parents': [{'id': folder_id}]})
        gfile.SetContentFile(file_name)
        gfile.Upload()
        print("UPLOADING:: completed uploading", file_name)
        return True


def drive_up(file_name, folder):
        print("in drive")
        file_list = drive.ListFile({'q': "'1j9aWdb4OHKv4hSXmxgd-x-fB1MB0bNsE' in parents and trashed=false"}).GetList()
        for x in file_list:
                if x['title'] == folder:
                        folder_id = "'" + x['id'] + "'"
                        print(folder_id)
                        file_list2 = drive.ListFile({'q': f"{folder_id} in parents and trashed=false"}).GetList()
                        for y in file_list2:
                                if y['title'] == file_name:
                                        print("already uploaded", file_name)
                                        return None
                        print("out to uploading")
                        uploading(x['id'], file_name)
                        return None
        drive_folder = drive.CreateFile({'title' : folder, 'mimeType' : 'application/vnd.google-apps.folder', 'parents': [{'id': '1j9aWdb4OHKv4hSXmxgd-x-fB1MB0bNsE'}]})
        drive_folder.Upload()
        drive_up(folder, file_name)
        return None

def download(url, folder):
        print("in download", url)
        get_response = requests.get(url,stream=True)
        file_name = url.split("/")[-1]
        if os.path.exists(file_name):
                print("already exists " , url)
        else:
                with open(file_name, 'wb') as f:
                        for chunk in get_response.iter_content(chunk_size=1024):
                                if chunk:
                                        f.write(chunk)
                print("done " , url)
        return drive_up(file_name, folder)
        
def run(data):
        count = 0
        print("in run")
        dicLink = dict()
        for uid, message in data:
                if ("3CX Meeting Report" in message.subject) and ("EXTN" in str(message.body)):
                        s = str(message.body)
                        folder = s[s.find("EXTN")+4:s.find(":\\r\\n\\r\\n")].replace(" ","")
                        url = s[s.find('https://files-as.3cx.net/'):s.find('.mp4') +4].replace(" ","")
                        ls2 = [int(x) for x in folder.split(",")]
                        ls2 = [str(x) for x in sorted(ls2, reverse=False)]
                        folder_name = "-".join(ls2)
                        if url != "":
                                count += 1
                                dicLink[url] = folder_name
        print(dicLink)
        downloadingThread(dicLink)

def downloadingThread(dicLink):
        threads = []
        for th in dicLink:
                t = threading.Thread(target=download, args=[th, dicLink[th]])
                print("to start")
                t.start()
                print("append start")
                threads.append(t)
        for ths in threads:
                print("to join")
                ths.join()
                print("after join")

def main():
        drive.ListFile({'q': "'1j9aWdb4OHKv4hSXmxgd-x-fB1MB0bNsE' in parents and trashed=false"}).GetList()
        month, day = int(input("Enter Month: ")), int(input("Enter date: "))
        for x, y in zip(['uprevolteam@gmail.com'], ['MZmX9&jCZK']):
                with Imbox('imap.gmail.com',
                        username=x,
                        password=y,
                        ssl=True,
                        ssl_context=None,
                        starttls=False) as imbox:
                        inbox_messages_received_on_date = imbox.messages(date__gt=datetime.date(2021, month, day))
                        run(inbox_messages_received_on_date)

main()
