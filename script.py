
# Importing libraries :

import requests
from bs4 import BeautifulSoup
from slimit import ast
from slimit.parser import Parser
from slimit.visitors import nodevisitor
import pandas as pd


# Lists to store the scraped data in
addressLocality=[]
addressRegion=[]
categorys=[]
product_id=[]
telephones=[]
publicationType=[]
names=[]
prices=[]
pages = [str(i) for i in range(2,10000)]

for page in pages:
    
    url="https://www.avito.ma/fr/maroc/%C3%A0_vendre?o="+page
    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=20)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    pg=session.get(url)
   
    
    if pg.status_code != 200:
        break
    
    html_soup=BeautifulSoup(pg.text,'html.parser')
    
    # Extracting the url of each product :
    
    items_list=html_soup.find(class_="listing listing-thumbs").findAll("div",class_="item-info ctext1 mls")
    items_urls=[i.find('a', href=True)['href'] for i in items_list] 
     
    
    for url in items_urls:
        
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(max_retries=20)
        session.mount('https://', adapter)
        session.mount('http://', adapter)
        response=session.get(url)
        
        data={}
        
        if response.status_code != 200:
            break
        
        html_soup=BeautifulSoup(response.text,"html.parser")
        
        price=html_soup.find("div", class_="panel-body").span.string
        
        script=html_soup.find("div",class_="container mbm").find_all("script",{"type":"text/javascript"})[-1]
        
        price=html_soup.find("div", class_="panel-body").span.string
        parser = Parser()
        tree = parser.parse(script.string)
        for node in nodevisitor.visit(tree):
            if isinstance(node, ast.Assign):
                data = {getattr(node.left, 'value','' ): getattr(node.right, 'value','' )
                        for node in nodevisitor.visit(tree)
                        if isinstance(node, ast.Assign)}
       # If the data is not nan , then extract:
        if data :      
            prices.append(price) #the price
            addressLocality.append(data["addressLocality"]) #Local adress
            addressRegion.append(data["addressRegion"])     # Region adress
            categorys.append(data["category"])              #category
            telephones.append(data["telephone"])            #telephones
            publicationType.append(data["publisherType"])   #publication type
            names.append(data["name"])                      #the product name
            product_id.append(data["id"])                   #product_id

#Save our data in excel file :
dataset=pd.DataFrame({"Product_name":names,"Product_id":product_id,"Product_Category":categorys,"price":prices,"Phone_number":telephones,"Professional_Publication":publicationType,"Region_address":addressRegion,"Local_address":addressLocality})
dataset.to_excel("Avito_Dataset.xlsx")
