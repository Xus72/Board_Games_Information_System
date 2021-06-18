import re
from bs4 import BeautifulSoup
import urllib.request as request
from urllib.request import Request
import html5lib, lxml
import time, os, shutil
from whoosh.fields import Schema, TEXT, ID, DATETIME, KEYWORD, NUMERIC
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup

url = 'https://www.board-game.co.uk/category/board-games/'
header = {'User-Agent':'Mozilla/5.0'}

def load():
    storage_data()

#Función que extrae todas las páginas de la web
def extract_games():
    list_games = list()
    for p in range(1,50):
        list_page = extract_game(url+'?page='+str(p))
        list_games.extend(list_page)
        time.sleep(70)
        print(p)
    return list_games

#Función que extrae todos los juegos de una pagina
def extract_game(url):
    l = list()
    try:
        #req = Request(url, headers=header)
        f = request.urlopen(url)
        s = BeautifulSoup(f, 'html5lib')
    except:
        print('Exception at url: {}'.format(url))
    results = s.find('ul',class_='zg-products-list')
    #Lista con todos los juegos de la página
    list_game = results.find_all('li', class_='zg-product')
    for game in list_game:
        #Enlace del juego
        link = game.find('div', class_='zg-product-title').find('h1').a['href']
        #Abrir la página del juego
        #reql = Request(link, headers=header)
        f = request.urlopen(link)
        r = BeautifulSoup(f, 'lxml')
        #Titulo del juego
        title = r.find('h1', class_='product-title').string
        #print(title)
        #Si el juego está en oferta
        if r.find('span', id='woo_prices_reg'):
            price = r.find('span', id='woo_prices_reg').next_sibling.string
        #Si el juego no está en oferta
        elif r.find('span', id='woo_prices_now'):
            price = r.find('span', id='woo_prices_now').next_sibling.string
        else:
            price = r.find('span', id='woo_prices_sale').next_sibling.string
        aux = r.find('div', class_='p-single-images pr clear thumb-right')
        #Existen juegos que no tienen imágenes
        if aux:
            image = aux.find('img', class_='attachment-shop_single')
            #Imagen del juego
            img = image['data-src']
        else:
            img = None
        aux2 = r.find('div', class_='product-tabs')
        if aux2.find('section', id='perfect-products-description'):
            descr = aux2.find('section', id='perfect-products-description').find_all('p')
        elif (aux2.find('div', class_='fl-rich-text')):
            descr = aux2.find('div', class_='fl-rich-text').find_all('p')
        else:
            descr = aux2.find('div',id='tab-description').find_all('p')
        #Descripción del juego
        description = ''
        for p in descr:
            if p.string != None:
                description += p.string + ' '
        #Características del juego
        de = list()
        if descr[-1].find('strong'):
            de = descr[-1].find_all('strong')
        caracteristics = list()
        for d in de:
            label = d.string
            carac = d.next_sibling
            caracteristics.append([label,carac])
        #Puntuación del juego
        rating = list()
        if s.find('div', class_='zbr-tablet-content'):
            aux3 = s.find('div', class_='zbr-tablet-content')
            rat = aux3.find_all('li', class_='zg-blog-bottom-rating')
            for r in rat:
                label = r.find('div', class_='zg-blog-bottom-rating-label').string
                scores = len(r.find_all('li', class_='zg-sidebar-meeple-orange'))
                rating.append([label,scores])
        #Lista con todos los juegos de la página
        l.append([title,price,img,description,caracteristics,rating])
    return l

def storage_data():
    #Define el esquema de información
    schema = Schema(title=TEXT(stored=True), price=TEXT(stored=True), image=ID, description=TEXT, n_players=TEXT(stored=True), time=TEXT(stored=True),
                    age=TEXT(stored=True), artwork=NUMERIC(stored=True), complexity=NUMERIC(stored=True), replayability=NUMERIC(stored=True),
                    player_interaction=NUMERIC(stored=True), component_quality=NUMERIC(stored=True))
    #Eliminamos el directorio si existe
    if os.path.exists('Index'):
        shutil.rmtree('Index')
    os.mkdir('Index')

    #Creamos el index
    ix = create_in('Index', schema=schema)
    #Añadimos los documentos
    writer = ix.writer()
    it = 0
    l = extract_games()
    for game in l:
        n_pl = None
        ti = None
        a = None
        t=game[0]
        p=game[1]
        i=game[2]
        d=game[3]
        if len(game[4]) == 0:
            n_pl = None
            ti = None
            a = None
        elif len(game[4]) == 1:
            if game[4][0][0] == 'Player Count':
                n_pl = game[4][0][1]
            elif game[4][0][0] == 'Time':
                ti = game[4][0][1]
            else:
                a = game[4][0][1]
        elif len(game[4]) == 2:
            if game[4][1][0] == 'Player Count':
                n_pl = game[4][1][1]
            elif game[4][1][0] == 'Time':
                ti = game[4][1][1]
            else:
                a = game[4][1][1]
        else:
            if game[4][2][0] == 'Player Count':
                n_pl = game[4][2][1]
            elif game[4][2][0] == 'Time':
                ti = game[4][2][1]
            else:
                a = game[4][2][1]
        if len(game[5]) == 0:
            art = 0
            c = 0
            r = 0
            pl = 0
            com = 0
        else:
            art = game[5][0][1]
            c = game[5][1][1]
            r = game[5][2][1]
            pl = game[5][3][1]
            com = game[5][4][1]
        #print([t,p,i,d,n_pl,ti,a,art,c,r,pl,com])
        writer.add_document(title=str(t),price=str(p),image=i,description=str(d),n_players=str(n_pl),time=str(ti),age=str(a),artwork=art,complexity=c,replayability=r,player_interaction=pl,component_quality=com)
        it+=1
    writer.commit()

#Consultas whoosh
#Buscar juegos por titulo
def search_title(terms):
    res = list()
    #Abrimos el índice
    ix = open_dir("Index")
    with ix.searcher() as searcher:
        query = QueryParser("title", ix.schema).parse(str(terms))
        results = searcher.search(query)
        for result in results:
            res.append([result['title'],result['price']])
    print(res)
    return res

def search_artwork(terms):
    res = list()
    ix = open_dir("Index")
    with ix.searcher() as searcher:
        if(not re.match("\d{1} \d{1}", terms)):
            print("Formato del rango de fecha incorrecto")
        aux = terms.split()
        range_artwork = '[' + aux[0] + ' TO ' + aux[1] + ']'
        query = QueryParser('artwork', ix.schema).parse(range_artwork)
        results = searcher.search(query)
        for result in results:
            res.append([result['title'],result['price'],result['artwork']])
    return res

def search_complexity(terms):
    res = list()
    ix = open_dir("Index")
    with ix.searcher() as searcher:
        if (not re.match("\d{1} \d{1}", terms)):
            print("Formato del rango de fecha incorrecto")
        aux = terms.split()
        range_complexity = '[' + aux[0] + ' TO ' + aux[1] + ']'
        query = QueryParser('complexity', ix.schema).parse(range_complexity)
        results = searcher.search(query)
        for result in results:
            res.append([result['title'], result['price'], result['complexity']])
    return res

def search_replayability(terms):
    res = list()
    ix = open_dir("Index")
    with ix.searcher() as searcher:
        if(not re.match("\d{1} \d{1}", terms)):
            print("Formato del rango de fecha incorrecto")
        aux = terms.split()
        range_replayability = '[' + aux[0] + ' TO ' + aux[1] + ']'
        query = QueryParser('replayability', ix.schema).parse(range_replayability)
        results = searcher.search(query)
        for result in results:
            res.append([result['title'],result['price'],result['replayability']])
    return res

def search_pl_interaction(terms):
    res = list()
    ix = open_dir("Index")
    with ix.searcher() as searcher:
        if(not re.match("\d{1} \d{1}", terms)):
            print("Formato del rango de fecha incorrecto")
        aux = terms.split()
        range_pl_interaction = '[' + aux[0] + ' TO ' + aux[1] + ']'
        query = QueryParser('replayability', ix.schema).parse(range_pl_interaction)
        results = searcher.search(query)
        for result in results:
            res.append([result['title'],result['price'],result['player_interaction']])
    return res

def search_pl_interaction(terms):
    res = list()
    ix = open_dir("Index")
    with ix.searcher() as searcher:
        if(not re.match("\d{1} \d{1}", terms)):
            print("Formato del rango de fecha incorrecto")
        aux = terms.split()
        range_pl_interaction = '[' + aux[0] + ' TO ' + aux[1] + ']'
        query = QueryParser('replayability', ix.schema).parse(range_pl_interaction)
        results = searcher.search(query)
        for result in results:
            res.append([result['title'],result['price'],result['player_interaction']])
    return res

def search_price(terms):
    res = list()
    ix = open_dir("Index")
    with ix.searcher() as searcher:
        if(not re.match('\d+\.\d+', terms)):
            print("Formato del rango de precio incorrecto")
        aux = terms.split()
        range_price = '[' + aux[0] + ' TO ' + aux[1] + ']'
        query = QueryParser('price', ix.schema).parse(range_price)
        results = searcher.search(query)
        for result in results:
            res.append([result['title'], result['price']])
    print(res)
    return res

storage_data()
