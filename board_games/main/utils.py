from bs4 import BeautifulSoup
import urllib.request as request
import html5lib

page = 0
url = 'https://www.board-game.co.uk/category/board-games/'
#pages = 'https://www.board-game.co.uk/category/board-games/?page=2'


def extract_games():
    list_games = list()
    for p in range(1,51):
        list_page = extract_game(url+str((p-1)*24))
        list_games.extend(list_page)
    return list_games

def extract_game(url):
    l = list()
    f = request.urlopen(url)
    s = BeautifulSoup(f, 'html5lib')
    results = s.find('ul',class_='zg-products-list')
    list_game = results.find_all('li', class_='zg-product')
    for game in list_game:
        link = game.find('div', class_='zg-product-title').find('h1').a['href']
        f = request.urlopen(link)
        s = BeautifulSoup(f, 'html5lib')
        title = s.find('h1', class_='product-title').string
        price = s.find('span', id='woo_prices_reg').next_sibling.string
        aux = s.find('div', class_='p-single-images pr clear thumb-right')
        if aux:
            image = aux.find('img', class_='attachment-shop_single')
            img = image['data-src']
        else:
            img = None
        aux2 = s.find('div', class_='product-tabs')
        if aux2.find('section', id='perfect-products-description') == None:
            descr = aux2.find('div', class_='fl-rich-text').find_all('p')
        else:
            descr = aux2.find('section', id='perfect-products-description').find_all('p')
        description = ''
        for p in descr:
            if p.string != None:
                description += p.string + ' '
        if descr[-1].find('strong'):
            de = descr[-1].find_all('strong')
        caracteristics = list()
        for d in de:
            label = d.string
            carac = d.next_sibling
            caracteristics.append([label,carac])
        rating = list()
        aux3 = s.find('div', class_='zbr-tablet-content')
        rat = aux3.find_all('li', class_='zg-blog-bottom-rating')
        for r in rat:
            label = r.find('div', class_='zg-blog-bottom-rating-label').string
            scores = len(r.find_all('li', class_='zg-sidebar-meeple-orange'))
            rating.append([label,scores])
        l.append((title,price,img,caracteristics,rating))
    print(l)
    return l

extract_game(url)