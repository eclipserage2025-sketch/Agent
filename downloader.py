import os
import requests
import zipfile
import io

def download_xmrig_windows():
    print("[Downloader] Fetching latest XMRig Windows release...")
    url = "https://github.com/xmrig/xmrig/releases/download/v6.22.2/xmrig-6.22.2-msvc-win64.zip"

    try:
        if os.path.exists("xmrig.exe"):
            print("[Downloader] XMRig already exists.")
            return True

        response = requests.get(url, stream=True)
        if response.status_code == 200:
            print("[Downloader] Downloading...")
            z = zipfile.ZipFile(io.BytesIO(response.content))
            # Extract only xmrig.exe
            for info in z.infolist():
                if info.filename.endswith("xmrig.exe"):
                    info.filename = "xmrig.exe"
                    z.extract(info, ".")
                    print("[Downloader] Extracted xmrig.exe successfully.")
                    return True
        else:
            print(f"[Downloader] Failed to download. Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[Downloader] Error: {e}")
        return False

if __name__ == "__main__":
    download_xmrig_windows()
