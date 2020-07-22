import httpx

def fetch_code_time():
    return httpx.get(
        "https://gist.githubusercontent.com/0xcaffebabe/8ea5a71947543404d826b1a839b29398/raw/351d60fae06291fc5200c7cb5128439f9f5d794b/%25F0%259F%2593%258A%2520Weekly%2520development%2520breakdown"
    )

readme = "# Overview\n\n"+\
"📊 Weekly development breakdown\n\n"+\
"```text\n"+\
  fetch_code_time().text+\
"```"

print (readme)

open('./README.md','w').write(readme)
