from bs4 import BeautifulSoup
import urllib.request as request
import html5lib
import time

url = 'https://www.board-game.co.uk/category/board-games/'

#Función que extrae todas las páginas de la web
def extract_games():
    list_games = list()
    for p in range(1,51):
        list_page = extract_game(url+'?page='+str(p))
        list_games.extend(list_page)
        time.sleep(20)
    return list_games

#Función que extrae todos los juegos de una pagina
def extract_game(url):
    l = list()
    f = request.urlopen(url)
    s = BeautifulSoup(f, 'html5lib')
    results = s.find('ul',class_='zg-products-list')
    #Lista con todos los juegos de la página
    list_game = results.find_all('li', class_='zg-product')
    for game in list_game:
        #Enlace del juego
        link = game.find('div', class_='zg-product-title').find('h1').a['href']
        #Abrir la página del juego
        f = request.urlopen(link)
        s = BeautifulSoup(f, 'html5lib')
        #Titulo del juego
        title = s.find('h1', class_='product-title').string
        print(title)
        #Si el juego está en oferta
        if s.find('span', id='woo_prices_reg'):
            price = s.find('span', id='woo_prices_reg').next_sibling.string
        #Si el juego no está en oferta
        elif s.find('span', id='woo_prices_now'):
            price = s.find('span', id='woo_prices_now').next_sibling.string
        else:
            price = s.find('span', id='woo_prices_sale').next_sibling.string
        aux = s.find('div', class_='p-single-images pr clear thumb-right')
        #Existen juegos que no tienen imágenes
        if aux:
            image = aux.find('img', class_='attachment-shop_single')
            #Imagen del juego
            img = image['data-src']
        else:
            img = None
        aux2 = s.find('div', class_='product-tabs')
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

extract_games()