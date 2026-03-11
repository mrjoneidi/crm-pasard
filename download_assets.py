import os
import urllib.request

def download(url, dest):
    print(f"Downloading {url} to {dest}")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    urllib.request.urlretrieve(url, dest)

download("https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.rtl.min.css", "static/css/bootstrap.rtl.min.css")
download("https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js", "static/js/bootstrap.bundle.min.js")
download("https://unpkg.com/feather-icons@4.29.0/dist/feather.min.js", "static/js/feather.min.js")
download("https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css", "static/css/Vazirmatn-font-face.css")

fonts = [
    "Thin", "ExtraLight", "Light", "Regular", "Medium", "SemiBold", "Bold", "ExtraBold", "Black"
]
for weight in fonts:
    download(f"https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/webfonts/Vazirmatn-{weight}.woff2", f"static/css/fonts/webfonts/Vazirmatn-{weight}.woff2")

print("Done")
