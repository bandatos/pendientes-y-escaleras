import pandas as pd
from bs4 import BeautifulSoup

# read map
with open('Mexico_City_metro.svg', 'r') as fp:
    soup = BeautifulSoup(fp, 'xml')

# read reports
df = pd.read_csv('reportes_toy_data.csv')

# update nodes
for i in df.index:    
    soup.find(id=df.id[i])['style'] = soup\
    .find(id=df.id[i])['style']\
    .replace('fill:#ffffff','fill:#B72727').replace('stroke:#ffffff','stroke:#B72727')

# overwrite map
with open('Mexico_City_metro.svg', 'w', encoding='utf-8') as f:
    f.write(str(soup))