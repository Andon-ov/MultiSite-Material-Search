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
                # "toplivo": f"https://toplivo.bg/rezultati-ot-tarsene/{query}",
                # "abc": f"https://stroitelni-materiali.eu/search?query={query}",
                # "bricolage": f"https://mr-bricolage.bg/search-list?query={query}",
                "masterhaus": f"https://www.masterhaus.bg/bg/search?q={query}",

            }

            for site, url in urls.items():
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    if site == "toplivo":
                        site_results = process_toplivo(soup)
                    elif site == "abc":
                        site_results = process_abc(soup)
                    elif site == "bricolage":
                        site_results = process_bricolage(soup)
                    elif site == "masterhaus":
                        site_results = process_masterhaus(soup)
                    else:
                        site_results = []

                    results.extend(site_results)

    return render(request, 'material_scout/search_results.html', {'form': form, 'results': results, 'query': query})


def process_toplivo(soup):
    results = []
    store_name = "Toplivo"  # Името на магазина

    for item in soup.select('.productWapper1.search'):
        # Първо се опитваме да вземем основното заглавие
        title_tag = item.select_one(
            'div.productWapper1 > div:nth-child(1) > div:nth-child(2) > h3:nth-child(2) > a:nth-child(1) > span:nth-child(2)')

        # Проверка за наличност на второ и трето заглавие
        second_title = item.select_one(
            'div.productWapper1 > div:nth-child(1) > div:nth-child(2) > h3:nth-child(3) > a:nth-child(1) > span:nth-child(1)')
        three_title = item.select_one(
            'div.productWapper1 > div:nth-child(1) > div:nth-child(2) > h3:nth-child(3) > a:nth-child(1) > span:nth-child(2)')

        subtitle = item.select_one(
            'div.productWapper1 > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)')

        # Ако заглавието не е налично, опитай с второ и трето заглавие
        if title_tag:
            title = title_tag.get_text(strip=True)
        else:
            second_title_text = second_title.get_text(
                strip=True) if second_title else ''

            subtitle_text = subtitle.get_text(strip=True) if subtitle else ''
            three_title_text = three_title.get_text(
                strip=True) if three_title else ''
            title = f"{subtitle_text} {second_title_text} {
                three_title_text}".strip()
            if not title:
                title = "Без заглавие"

        link_tag = item.select_one('figure.img > a')

        price_tag = item.select_one('.cena .beforedot')
        red_price_tag = item.select_one(
            ('div.productWapper1 > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > span:nth-child(1)'))
        new_price_tag = item.select_one(
            ('div.productWapper1 > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(2) > span:nth-child(1)'))

        link = link_tag['href'] if link_tag else '#'

        # Извличане на текстовете за различните цени
        red_price = red_price_tag.get_text(
            strip=True) if red_price_tag else None
        new_price = new_price_tag.get_text(
            strip=True) if new_price_tag else None
        valid_price = price_tag.get_text(strip=True) if price_tag else None

        # Логика за приоритет на цените: първо проверява valid_price, след това red_price, и накрая new_price
        price = valid_price or red_price or new_price or 'Няма цена'

        results.append({'title': title, 'price': price,
                       'link': link, 'store_name': store_name})

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
        new_price = new_price_tag.get_text(
            strip=True) if new_price_tag else 'Няма цена'
        price = price_tag.get_text(strip=True) if price_tag else new_price

        results.append({'title': title, 'price': price,
                       'link': link, "store_name": store_name})
    return results


def process_bricolage(soup):
    results = []
    store_name = "Mr.Bricolage"  # Името на магазина
    for item in soup.select('.product'):
        title_tag = item.select_one('.product__title a')
        link_tag = item.select_one('.product__title a')
        first_price_tag = item.select_one('.product__price-value')
        second_price_tag = item.select_one('.fraction')

        # new_price_tag = item.select_one('._product-price-compare')
        # old_price_tag = item.select_one('._product-price-old')

        title = title_tag.get_text(strip=True) if title_tag else 'Без заглавие'
        link = link_tag['href'] if link_tag else '#'
        link = f"https://mr-bricolage.bg{link}"

        first_price = first_price_tag.get_text(
            strip=True) if first_price_tag else 'Няма цена'
        second_price = second_price_tag.get_text(
            strip=True) if second_price_tag else 'Няма цена'

        price = f"{first_price}.{second_price}"

        results.append({'title': title, 'price': price,
                       'link': link, "store_name": store_name})
    return results


def process_masterhaus(soup):
    results = []
    store_name = "Masterhaus"  # Името на магазина
    for item in soup.select('ul.products > li'):
        title_tag = item.select_one('h2 a')
        link_tag = item.select_one('ul.products > li > div > a')
        price_tag = item.select_one('ul.products > li > div:nth-child(1) > strong:nth-child(2)')
        second_price_tag = item.select_one('.price sup')

        promo_price_tag = item.select_one('.price.promo')
        promo_second_price_tag = item.select_one('ul.products > li > div:nth-child(1) > strong:nth-child(2) > sup:nth-child(2)')


        title = title_tag.get_text(strip=True) if title_tag else 'Без заглавие'
        link = link_tag['href'] if link_tag else '#'
        link = f"https://www.masterhaus.bg{link}"

        price_main = price_tag.contents[0].strip() if price_tag.contents else ""
        second_price = second_price_tag.contents[0].strip() if price_tag.contents else ""


        if promo_price_tag:
            price = promo_price_tag.get_text(strip=True) if promo_price_tag else 'Няма цена'
            promo_price_main = promo_price_tag.contents[-1].strip()

            print('tuk', price, promo_price_main)
            # price_main = promo_price_tag.contents[0].strip() if promo_price_tag.contents else ""
            # second_price = promo_second_price_tag.contents[0].strip() if promo_second_price_tag.contents else ""

        else:
            price = price_tag.get_text(strip=True) if price_tag else 'Няма цена'

        # second_price = second_price_tag.get_text(
        #     strip=True) if second_price_tag else 'Няма цена'

        price = f"{price_main}.{second_price}"
        print(price)

        results.append({'title': title, 'price': price, 'link': link, "store_name":store_name})
    return results




#
# def process_masterhaus(soup):
#     results = []
#     store_name = "Masterhaus"  # Името на магазина
#
#     for item in soup.select('ul.products > li'):
#         title_tag = item.select_one('h2 a')
#         price_tag = item.select_one('strong.price:not(.promo)')
#         promo_price_tag = item.select_one('strong.price.promo')
#
#         # Проверка за title_tag
#         if title_tag is None:
#             print("Title tag is None")
#             continue  # Пропускане на текущия елемент, ако няма заглавие
#
#         title = title_tag.get_text(strip=True)
#
#         link = title_tag['href'] if title_tag else '#'
#         if not link.startswith('http'):
#             link = f"https://www.masterhaus.bg{link}"
#
#         if price_tag:
#             price_main = price_tag.contents[0].strip() if price_tag.contents else ""
#             price_sup = price_tag.find('sup').get_text(strip=True) if price_tag.find('sup') else ""
#             price = f"{price_main}{price_sup} лв."
#             print(price)
#         else:
#             price = "Няма цена"
#
#         if promo_price_tag:
#             del_tag = promo_price_tag.find('del')
#             if del_tag:
#                 original_price_main = del_tag.select_one('span').get_text(strip=True) if del_tag.select_one('span') else ""
#                 original_price_sup = del_tag.select_one('sup').get_text(strip=True) if del_tag.select_one('sup') else ""
#                 original_price = f"{original_price_main}.{original_price_sup} лв."
#                 print(original_price)
#             else:
#                 original_price = "Няма стара цена"
#
#             promo_price_main = promo_price_tag.contents[-2].strip() if len(promo_price_tag.contents) > 1 else ""
#             print(promo_price_main)
#             promo_price_sup = promo_price_tag.find('sup').get_text(strip=True) if promo_price_tag.find('sup') else ""
#             promo_price = f"{promo_price_main}.{promo_price_sup} лв."
#
#             price = promo_price or original_price or "има грешка" # Предпочитаме промоционалната цена
#
#         results.append({
#             'title': title,
#             'price': price,
#             'link': link,
#             'store_name': store_name
#         })
#
#     return results
