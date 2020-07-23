import httpx

def fetch_code_time():
    return httpx.get(
        "https://gist.githubusercontent.com/0xcaffebabe/8ea5a71947543404d826b1a839b29398/raw"
    )

readme = "# Overview\n\n"+\
"📊 Weekly development breakdown\n\n"+\
"```text\n"+\
  fetch_code_time().text+"\n"+\
"```"

print (readme)

open('./README.md','w').write(readme)
