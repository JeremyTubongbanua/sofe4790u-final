import requests, zipfile, io, os, shutil

url = 'https://github.com/JeremyTubongbanua/sofe4790u-final/raw/main/dataset.zip'

response = requests.get(url)
if response.status_code == 200:
    with zipfile.ZipFile(io.BytesIO(response.content)) as the_zip:
        the_zip.extractall('.')
    
    # Delete any .DS_Store files and __MACOSX folders
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file == '.DS_Store':
                os.remove(os.path.join(root, file))
        for dir in dirs:
            if dir == '__MACOSX':
                shutil.rmtree(os.path.join(root, dir))
else:
    print(f"Failed to download file: {response.status_code}")