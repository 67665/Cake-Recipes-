# kod python
import requests
import urllib.request
from bs4 import *
from collections import OrderedDict  # dla obrazkow zeby sie nie powtarzaly
import urllib

interpunkcje = "!'#$%&()*+,-./:;<=>?®@[\\]^_`{|}~"


def tokenizacja(s):
    for znak in interpunkcje:
        s = s.replace(znak, " ")
    slowa = s.strip().split()
    return slowa


def get_slownik():
    strona = urllib.request.urlopen("https://lewoniewski.info/diffs.txt")
    linie = [linia.decode("utf-8") for linia in strona.readlines()]

    slownik = {}
    for linia in linie:
        klucz, wartosc = linia.split()
        slownik[klucz] = wartosc
    return slownik


# znalezione słowa pogrubione jak jest eggs to egg
# tf-idf
# levenstein

slownik = get_slownik()


def lematyzacja(slowa):
    return [slownik.get(slowo, slowo) for slowo in slowa]


# for slowo in list(slownik)[:15]:
#   print(slowo,slownik[slowo])

# def pobierz_przepis(link):
#     html = requests.get(link).text
#     soup = BeautifulSoup(html, "html.parser")
#     obrazek = soup.find('img')
#     tytul = soup.find('.title')
#     return Przepis(link, obrazek, tytul, skladniki, tresc)
# przepisy = [pobierz_przepis(link) for link in linki]

link = "https://www.allrecipes.com/recipes/276/desserts/cakes/"
page = urllib.request.urlopen(link)
kod = page.read().decode('utf-8')

soup = BeautifulSoup(kod, 'html.parser')
linki = []
elements = soup.find_all('a', attrs={'id': lambda x: x and x.startswith('mntl-card-list-items_')})
for element in elements:
    linki.append(element['href'])
# print(len(linki))

obrazki = OrderedDict()
img_tags = soup.find_all('img', class_='card__img')
for img in img_tags:
    url = img.get('src', img.get('data-src'))
    obrazki[url] = None
obrazki = list(obrazki.keys())

# print(obrazki)

span_tags = soup.find_all('span', class_='card__title-text')
tytuly = [span.text for span in span_tags]

sklad = []
for link in linki:
    sublist_s = []
    html = requests.get(link).text
    soup = BeautifulSoup(html, "html.parser")
    skl = soup.find_all("li", class_="mntl-structured-ingredients__list-item")
    for s in skl:
        skladn = s.text.replace("\n", "")
        sublist_s.append(skladn)
    sklad.append(sublist_s)
# print(sklad)

wykonanie = []
for link in linki:
    sublist_w = []
    html = requests.get(link).text
    soup = BeautifulSoup(html, "html.parser")
    soup1 = soup.find("div", class_="comp recipe__steps mntl-block")
    steps = soup1.find_all("p", class_="mntl-sc-block-html")
    for st in steps:
        step = st.text.replace("\n", "")
        sublist_w.append(step)
    wykonanie.append(sublist_w)
# print(wykonanie)

skladniki = []
for link in linki:
    page1 = urllib.request.urlopen(link)
    kod = page1.read().decode('utf-8')
    soup = BeautifulSoup(kod, 'html.parser')
    s_html = soup.find_all("span", {"data-ingredient-name": "true"})
    skladniki_przepis = []
    for s in s_html:
        s_przepis = s.text.lower()
        s_przepis = tokenizacja(s_przepis)
        [skladniki_przepis.append(skladnik) for skladnik in s_przepis]
    skladniki_przepis = lematyzacja(skladniki_przepis)
    skladniki.append(skladniki_przepis)


# print(skladniki)


class Przepis:
    def __init__(self, link, obrazek, tytul, skladniki, skl, wyk):
        self.link = link
        self.obrazek = obrazek
        self.tytul = tytul
        self.skladniki = skladniki
        self.skl = skl
        self.wyk = wyk
        # self.ingredients = ['eggs', 'milk', 'salt', 'pepper']

    def czy_zawiera_skladniki(self, ingredients):
        return set(ingredients).issubset(self.skladniki)

    def drukuj(self):
        print("Tytul: ", self.tytul)
        print("Obrazek: ", self.obrazek)
        print("Link: ", self.link)
        print("Składniki: ", self.skl)
        print("Wykonanie: ", self.wyk)


print("Podaj składniki: ")

przepisy = []
for link, obrazek, tytul, skladnik, skl, wyk in zip(linki, obrazki, tytuly, skladniki, sklad, wykonanie):
    przepis = Przepis(link, obrazek, tytul, skladnik, skl, wyk)
    przepisy.append(przepis)
# print(przepisy)
#
#
# # link1 = 'https://www.allrecipes.com' # img1 =
# 'https://www.allrecipes.com/thmb/XiHPj7KI9zM_FkABAS4wGgrNmTg=/750x0/filters:no_upscale():max_bytes(
# 150000):strip_icc():format(webp)/Italian-Olive-Oil-Cake-4x3-1-2000-7b4ef4d9708a472491cf4df637919493.jpg' # img2 =
# 'https://replit.com/cdn-cgi/image/width=32,quality=80,
# format=auto/https://storage.googleapis.com/replit/images/1664475603315_1442b3c69cc612aff6ef60cce0c69328.jpeg' #
# przepisy = [ #     Przepis(link1, img1, 'tytul1', set(['egg', 'milk', 'water', 'lemon']), 'tresc1'), #     Przepis(
# 'link2', img2, 'tytul2', set(['egg', 'milk', 'water', 'bread']), 'tresc2'), #     Przepis('link3', 'img3',
# 'tytul3', set(['egg', 'water']), 'tresc3'), #     Przepis('link4', 'img4', 'tytul4', set(['milk', 'water']),
# 'tresc4') # ]
#
#
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/search')
def search():
    raw_ingredients = request.args.get('ingredients')
    ingredients = tokenizacja(raw_ingredients.lower())
    ingredients = lematyzacja(ingredients)
    f_przepisy = [p for p in przepisy if p.czy_zawiera_skladniki(ingredients)]
    return render_template('index.html', przepisy=f_przepisy, ingredients=raw_ingredients, search=True)


if __name__ == "__main__":
    app.run(debug=True)
