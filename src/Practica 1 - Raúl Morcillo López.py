import requests
from bs4 import BeautifulSoup
import re
import pandas as pd


# Cambiem l'agent
headers={"User-Agent":"Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36 Edg/99.0.1150.52"}

# Accedim al home de la web
web="https://www.transfermarkt.es/"
# Descarreguem l'html del home
page=requests.get(web,headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')

# Localitzem "Ver mejores 100" per a obtenir l'enllaç dels jugadors més valuosos
link=soup.find_all('a',string="Ver mejores 100")[0].get("href")
page = requests.get(web+link,headers=headers)
soup = BeautifulSoup(page.content, 'html.parser')

# Aquí guardarem la informació dels jugadors
directorio={}


# Anem iterant en cada una de les pàgines (20 en total) on anem raspant la informació dels jugadors

while True:
    
    tabla=soup.find_all('table',class_="items")
    filas=tabla[0].find_all("tr",attrs={'class':True})
    
    for jugador in filas:
        Ranking=jugador.find_all("td",attrs={"class":"zentriert"})[0].text
        busqueda=jugador.find_all("td",attrs={"class":"hauptlink"})
        Nombre=busqueda[0].text
        Foto=jugador.find_all("img",attrs={"class":"bilderrahmen-fixed"})[0].get("src")
        Valor=busqueda[1].text
        link=web+busqueda[0].find("a")['href'][1:]        
        Posicion=jugador.find_all("td",attrs={"class":False})[1].text
        Edad=jugador.find_all("td",attrs={"class":"zentriert"})[1].text
        Club=jugador.find_all("img",attrs={"class":""})[0]['alt']
        Escudo=jugador.find_all("img",attrs={"class":""})[0].get("src")
        Nacionalidad= [i['alt'] for i in jugador.find_all("img",attrs={"class":"flaggenrahmen"})]
        Bandera= [i.get('src') for i in jugador.find_all("img",attrs={"class":"flaggenrahmen"})]
        
         # Taula de les estadístiques de l'any actual
        page_personal = requests.get(link,headers=headers)
        page_personal = BeautifulSoup(page_personal.content, 'html.parser')
        summary=page_personal.find_all('table',class_="items")[0].find_all('tfoot',attrs={"class":False})[0].find_all('td')
        
        if Posicion!="Portero":
            
            _, _, Partidos_jugados, Goles, Asistencias, Min_gol, Min_jugados=(i.text for i in summary)
            
            directorio[Ranking]={"Nombre":Nombre,
                                "Foto":Foto,
                                "Valor":Valor,
                                "Posicion":Posicion,
                                "Edad":Edad,
                                "Club":Club,
                                "Escudo":Escudo,
                                "Nacionalidad":Nacionalidad,
                                "Bandera":Bandera,
                                "Partidos_jugados":Partidos_jugados,
                                "Goles":Goles,
                                "Asistencias":Asistencias,
                                "Min_gol":Min_gol,
                                "Min_jugados":Min_jugados}
        
        else:
            
            _, _, Partidos_jugados, Goles_encajados, Partidos_cero, Min_jugados=(i.text for i in summary)
            
            directorio[Ranking]={"Nombre":Nombre,
                                "Foto":Foto,
                                "Valor":Valor,
                                "Posicion":Posicion,
                                "Edad":Edad,
                                "Club":Club,
                                "Escudo":Escudo,
                                "Nacionalidad":Nacionalidad,
                                "Bandera":Bandera,
                                "Partidos_jugados":Partidos_jugados,
                                "Goles_encajados":Goles_encajados,
                                "Partidos_cero":Partidos_cero,
                                "Min_jugados":Min_jugados}
        
                        
    next_page=soup.find_all("li",attrs={"class":re.compile(r"next-page")})
        
    if len(next_page)==0:
        break

    else:
        link=web+next_page[0].find_all("a")[0]['href'][1:]
        page = requests.get(link,headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')

# Convertim el diccionari amb la informació dels jugadors en un dataframe

df = pd.DataFrame.from_dict(directorio, orient="index")

# Fem una neteja de les variables numeriques

df.Valor=df['Valor'].str.replace(",00 mill. €","")
df.Valor=df['Valor'].str.replace("\xa0","")
df.Goles=df['Goles'].str.replace("-","")
df.Edad=df['Edad'].str.replace("-","")
df.Partidos_jugados=df['Partidos_jugados'].str.replace("-","")
df.Asistencias=df['Asistencias'].str.replace("-","")
df.Min_gol=df['Min_gol'].str.replace("-","")
df.Min_jugados=df['Min_jugados'].str.replace("-","")
df.Goles_encajados=df['Goles_encajados'].str.replace("-","")
df.Partidos_cero=df['Partidos_cero'].str.replace("-","")
df.Nombre=df['Nombre'].str.replace("ć","c")

# Exportem el dataframe a csv

df.to_csv("Jugadors més valuosos.csv",encoding="latin-1")
