from bs4 import BeautifulSoup
import requests
import json

source = requests.get("https://www.zalando.nl/america-today-winterjas-redblue-amk21u00v-g11").text
soup = BeautifulSoup(source, "lxml")
scr = soup.find("script", id = "z-vegas-pdp-props").text

data = json.loads(scr.lstrip('<![CDATA').rstrip(']>'))
desired_data = dict(data['model']['articleInfo'])
print(desired_data)