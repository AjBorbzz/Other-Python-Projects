import requests
from bs4 import BeautifulSoup

data = requests.get('https://www.schooleymitchell.com/offices/')
soup = BeautifulSoup(data.text, 'html.parser')

# get data by looking for each id='consultant_info'

for div in soup.find_all('div', {'class': 'consultant_info_container'}):
	value = [div.text for div in div.find_all('strong')]
	value2 = [div.text for div in div.find_all('p')]
	
	names.append(value)
	addr.append(value2)

