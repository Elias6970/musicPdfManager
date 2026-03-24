# Source - https://stackoverflow.com/a/73443824
# Posted by Chris, modified by community. See post 'Timeline' for change history
# Retrieved 2026-03-24, License - CC BY-SA 4.0

import os

import httpx
import time
from urllib.parse import quote

url = 'http://127.0.0.1:8000/api/v1/uploads/staging'
filename = "D:\\22\\programacion\\archivo\\ArchivoDigital\\4-APOSTOL POETA\\partituras\\Apostol poeta Marcha Cristiana Doçaina.pdf"
filename = "C:\\Users\\Elias6970\\Desktop\\Video Monteverdi.mp4"
headers = {'filename': quote(filename), 'content-length': str(os.path.getsize(filename))}
start = time.time()

with open(filename, "rb") as f:
    r = httpx.post(url=url, data=f, headers=headers) #type: ignore
    
end = time.time()
print(f'Time elapsed: {end - start}s')
print(r.json())
