import json
from django.shortcuts import render
from .forms import SearchForm
import requests
from bs4 import BeautifulSoup

# # Зареждаме селекторите от JSON файла
# with open('selectors.json', 'r', encoding='utf-8') as f:
#     SELECTORS = json.load(f)
#
#
# def home(request):
#     return render(request, 'material_scout/home.html')
#
#
# def search_products(request):
#     form = SearchForm()
#     results = []
#
#     if 'query' in request.GET:
#         form = SearchForm(request.GET)
#         if form.is_valid():
#             query = form.cleaned_data['query']
#             urls = {
#                 # "abc": f"https://stroitelni-materiali.eu/search?query={query}",
#                 "toplivo": f"https://toplivo.bg/rezultati-ot-tarsene/{query}",
#
#                 # Добавете други сайтове тук
#             }
#
#             for site, url in urls.items():
#                 response = requests.get(url)
#                 if response.status_code == 200:
#                     soup = BeautifulSoup(response.text, 'html.parser')
#                     print(soup)
#                     site_config = SELECTORS.get(site, {})
#
#                     if site_config:
#                         for item in soup.select(site_config.get('parent_selector')):
#                             title_tag = item.select_one(
#                                 site_config.get('title_selector'))
#                             link_tag = item.select_one(
#                                 site_config.get('link_selector'))
#                             price_tag = item.select_one(
#                                 site_config.get('price_selector'))
#
#                             # new_price_tag = item.select_one(site_config.get('new_price_selector'))
#                             # old_price_tag = item.select_one(site_config.get('old_price_selector'))
#
#                             title = title_tag.get_text(
#                                 strip=True) if title_tag else 'Без заглавие'
#                             link = link_tag['href'] if link_tag else '#'
#                             # price = new_price_tag.get_text(strip=True) if new_price_tag else (price_tag.get_text(strip=True) if price_tag else 'Няма цена')
#                             price = price_tag.get_text(
#                                 strip=True) if price_tag else 'Няма цена'
#
#                             print(title, price, link)
#                             results.append({
#                                 'title': title,
#                                 'price': price,
#                                 'link': link
#                             })
#
#     return render(request, 'material_scout/search_results.html', {'form': form, 'results': results, 'query': query})


# def home(request):
#     return render(request, 'material_scout/home.html')
#
#
# def search_products(request):
#     form = SearchForm()
#     results = {
#         "toplivo": [],
#         "stroitelni-materiali": []
#     }
#
#     if 'query' in request.GET:
#         form = SearchForm(request.GET)
#         if form.is_valid():
#             urls = [
#                 "https://stroitelni-materiali.eu/search?query={query}",
#                 "https://toplivo.bg/rezultati-ot-tarsene/{query}"
#             ]
#             query = form.cleaned_data['query']
#
#             site_configs = {
#                 "toplivo": {
#                 "parent_selector": ".productWapper1.search",
#                 "title_selector": "div.productWapper1 > div:nth-child(1) > div:nth-child(2) > h3:nth-child(2) > a:nth-child(1) > span:nth-child(2)",
#                 "second_title_selector": ".ime",
#                 "link_selector": "div.productWapper1 > div:nth-child(1) > figure:nth-child(1) > a:nth-child(1)",
#                 "price_selector": ".cena .beforedot",
#                 "price_currency_selector": ".cena .edmiarka"
#                 },
#
#                 "stroitelni-materiali": {
#                     "parent_selector": "._product-info",
#                     "title_selector": "._product-name-tag a",
#                     "link_selector": "._product-name-tag a",
#                     "price_selector": "._product-price .price",
#                     "new_price_selector": "._product-price-compare",
#                     "old_price_selector": "._product-price-old"
#                 }
#             }
#
#             for url in urls:
#                 site_name = url.split('/')[2]
#                 site_name = site_name.split('.')[0]
#                 site_config = site_configs.get(site_name, {})
#                 print(site_name)
#
#                 response = requests.get(url.format(query=query))
#                 if response.status_code == 200:
#                     soup = BeautifulSoup(response.text, 'html.parser')
#                     # Отпечатайте HTML за отстраняване на проблеми
#                     # print(f"HTML за {site_name}:", soup.prettify())
#
#                     for item in soup.select(site_config.get('parent_selector','')):
#                         title_tag = item.select_one(
#                             site_config.get('title_selector', ''))
#                         link_tag = item.select_one(
#                             site_config.get('link_selector'))
#                         price_tag = item.select_one(
#                             site_config.get('price_selector'))
#                         new_price_tag = item.select_one(
#                             site_config.get('new_price_selector', ''))
#                         old_price_tag = item.select_one(
#                             site_config.get('old_price_selector', ''))
#
#                         title = title_tag.get_text(
#                             strip=True) if title_tag else 'Без заглавие'
#                         link = link_tag['href'] if link_tag else '#'
#                         price = new_price_tag.get_text(strip=True) if new_price_tag else (
#                             price_tag.get_text(strip=True) if price_tag else 'Няма цена')
#
#                         results[site_name].append({
#                             'title': title,
#                             'price': price,
#                             'link': link
#                         })
#
#     return render(request, 'material_scout/search_results.html', {'form': form, 'results': results})



def home(request):
    return render(request, 'material_scout/home.html')

def search_products(request):
    form = SearchForm()
    query = ""  # Инициализирай query с празен низ
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            urls = {
                "toplivo": f"https://toplivo.bg/rezultati-ot-tarsene/{query}",
                "abc":f"https://stroitelni-materiali.eu/search?query={query}",
            }

            for site, url in urls.items():
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    if site == "toplivo":
                        site_results = process_toplivo(soup)
                    elif site == "abc":
                        site_results = process_abc(soup)
                    else:
                        site_results = []

                    results.extend(site_results)

    return render(request, 'material_scout/search_results.html', {'form': form, 'results': results, 'query': query})



def process_toplivo(soup):
    results = []
    store_name = "Toplivo"  # Името на магазина

    for item in soup.select('.productWapper1.search'):
        # Първо се опитваме да вземем основното заглавие
        title_tag = item.select_one('div.productWapper1 > div:nth-child(1) > div:nth-child(2) > h3:nth-child(2) > a:nth-child(1) > span:nth-child(2)')

        # Проверка за наличност на второ и трето заглавие
        second_title = item.select_one('div.productWapper1 > div:nth-child(1) > div:nth-child(2) > h3:nth-child(3) > a:nth-child(1) > span:nth-child(1)')
        three_title = item.select_one('div.productWapper1 > div:nth-child(1) > div:nth-child(2) > h3:nth-child(3) > a:nth-child(1) > span:nth-child(2)')

        subtitle = item.select_one('div.productWapper1 > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)')

        # Ако заглавието не е налично, опитай с второ и трето заглавие
        if title_tag:
            title = title_tag.get_text(strip=True)
        else:
            second_title_text = second_title.get_text(strip=True) if second_title else ''

            subtitle_text = subtitle.get_text(strip=True) if subtitle else ''
            three_title_text = three_title.get_text(strip=True) if three_title else ''
            title = f"{subtitle_text} {second_title_text} {three_title_text}".strip()
            if not title:
                title = "Без заглавие"

        link_tag = item.select_one('figure.img > a')

        price_tag = item.select_one('.cena .beforedot')
        red_price_tag = item.select_one(('div.productWapper1 > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > span:nth-child(1)'))
        new_price_tag = item.select_one(('div.productWapper1 > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > span:nth-child(1)'))


        link = link_tag['href'] if link_tag else '#'

        # Извличане на текстовете за различните цени
        red_price = red_price_tag.get_text(strip=True) if red_price_tag else None
        new_price = new_price_tag.get_text(strip=True) if new_price_tag else None
        valid_price = price_tag.get_text(strip=True) if price_tag else None

        # Логика за приоритет на цените: първо проверява valid_price, след това red_price, и накрая new_price
        price = valid_price or red_price or new_price or 'Няма цена'


        results.append({'title': title, 'price': price, 'link': link, 'store_name': store_name})

    return results


def process_abc(soup):
    results = []
    store_name = "ABC"  # Името на магазина
    for item in soup.select('._product-info'):
        title_tag = item.select_one('._product-name-tag a')
        link_tag = item.select_one('._product-name-tag a')
        price_tag = item.select_one('._product-price .price')
        new_price_tag = item.select_one('._product-price-compare')
        old_price_tag = item.select_one('._product-price-old')

        title = title_tag.get_text(strip=True) if title_tag else 'Без заглавие'
        link = link_tag['href'] if link_tag else '#'
        new_price = new_price_tag.get_text(strip=True) if new_price_tag else 'Няма цена'
        price = price_tag.get_text(strip=True) if price_tag else new_price

        results.append({'title': title, 'price': price, 'link': link, "store_name":store_name})
    return results





