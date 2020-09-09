# -*- coding: utf-8 -*-
"""
Created on Sun Aug 23 12:07:06 2020

@author: ISAAC
"""

import pandas as pd
#import os
import sources
import config
import re
import time
import math
from selenium import webdriver
import urllib.parse
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from datetime import date
#from selenium.webdriver.support.ui import WebDriverWait
#from selenium.webdriver.support import expected_conditions as EC
#from selenium.webdriver.common.by import By
#from bs4 import BeautifulSoup
#import requests
from selenium.common.exceptions import StaleElementReferenceException

caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "eager"  #['eager','normal','none']
driver = webdriver.Chrome(desired_capabilities=caps, executable_path=r"./chromedriver.exe")

temp_departamento = None
products = []
today = date.today()
for link in sources.links_sv:
    link_without_server = link[21:]        
    estructura = link_without_server.split('/');        
    departamento = estructura[0];
    if temp_departamento is not None and temp_departamento != departamento:
        ex = pd.DataFrame(products, columns=config.columns)
        ex.to_csv(temp_departamento+'.csv', sep='\t', index=False,encoding='utf-8-sig')
        products = []
    
    temp_departamento = departamento
    currentPage = 1
    driver.get(link+'?fuzzy=0&operator=and&page='+str(currentPage))
    time.sleep(5)
    #page_history = []
    #page_history.append(0)
    __articulos__ = driver.find_elements_by_css_selector('a.vtex-product-summary-2-x-clearLink')
    total_articulos = driver.find_element_by_css_selector("div.vtex-search-result-3-x-totalProducts--layout span").get_attribute('innerHTML') 
    total_articulos = int(re.search('(\d+)',total_articulos).group(0))
    total_paginas = math.ceil(total_articulos/21)
    ExistNextPage = True
    while ExistNextPage:
        for i in range(len(__articulos__)):
            try:
                item = []
                link_articulo = urllib.parse.unquote(__articulos__[i].get_attribute('href'))
                art_key = link_articulo[21:len(link_articulo)-2]
                __producto__ = driver.execute_script("return __STATE__['Product:"+art_key+"']")
                categorias_str = __producto__["categories"]["json"][0]
                categorias = categorias_str[1:len(categorias_str)-2].split('/')
                pId = __producto__["productId"]
                psku = __producto__["productReference"]
                name = __producto__["productName"]
                desc = __producto__["description"]
                marca = __producto__["brand"]
                precio_lista_max = driver.execute_script("return __STATE__['$Product:"+art_key+".priceRange.listPrice']['highPrice']")
                precio_lista_min = driver.execute_script("return __STATE__['$Product:"+art_key+".priceRange.listPrice']['lowPrice']")
                precio_venta_max = driver.execute_script("return __STATE__['$Product:"+art_key+".priceRange.sellingPrice']['highPrice']")
                precio_venta_min = driver.execute_script("return __STATE__['$Product:"+art_key+".priceRange.sellingPrice']['lowPrice']")
                genero = None
                modelo = None
                for pindex in range(len(__producto__["properties"])):
                    __property__ = driver.execute_script("return __STATE__['Product:"+art_key+".properties."+str(pindex)+"']")
                    if __property__["name"] == "Género":
                        genero = __property__["values"]["json"][0]
                    if __property__["name"] == "Modelo":
                        modelo = __property__["values"]["json"][0]
                item.append(today)
                item.append(config.empresa.upper().strip())
                item.append(categorias[0].upper().strip()) #DEPARTAMENTO
                item.append(categorias[1].upper().strip() if len(categorias)> 1 else 'N/A') #CATEGORIA
                item.append(categorias[2].upper().strip() if len(categorias) > 2 else 'N/A') #SUBCATEGORIA
                item.append(pId.upper().strip()) #ID
                item.append(psku.upper().strip()) #SKU
                item.append(name.upper().strip()) #NOMBRE
                item.append(desc.upper().strip()) #DESCRIPCION
                item.append(marca.upper().strip() if marca is not None else 'N/A') #MARCA
                item.append("{:.2f}".format(precio_lista_max) if precio_lista_max is not None else '0.00') #PL-MAX
                item.append("{:.2f}".format(precio_lista_min) if precio_lista_min is not None else '0.00') #PL-MIN
                item.append("{:.2f}".format(precio_venta_max) if precio_venta_max is not None else '0.00') #PV-MAX
                item.append("{:.2f}".format(precio_venta_min) if precio_venta_min is not None else '0.00') #PV-MIN
                item.append(modelo.upper().strip() if modelo is not None else 'N/A') #MODELO
                item.append(genero.upper().strip() if genero is not None else 'N/A') #GENERO
                products.append(item)
                print("Articulo #"+str(len(products)))
            except StaleElementReferenceException:
                print("ERROR ARTICULO")    
            
        nexpage = driver.find_elements_by_css_selector('div.vtex-search-result-3-x-buttonShowMore button')
        if len(nexpage) > 0:
            currentPage+=1
            driver.get(link+'?fuzzy=0&operator=and&page='+str(currentPage))
            time.sleep(4)
            __articulos__ = driver.find_elements_by_css_selector('a.vtex-product-summary-2-x-clearLink')
        else:
            ExistNextPage = False
            
df = pd.DataFrame(products, columns=config.columns)
df.to_csv(temp_departamento+'.csv', sep='\t', index=False,encoding='utf-8-sig')
                

          
