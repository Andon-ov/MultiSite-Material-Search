from django.shortcuts import render
from .forms import SearchForm
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import re

def home(request):
    return render(request, 'material_scout/home.html')

def fetch_site(site, url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        if site == "toplivo":
            return process_toplivo(soup)
        elif site == "abc":
            return process_abc(soup)
        elif site == "bricolage":
            return process_bricolage(soup)
        elif site == "masterhaus":
            return process_masterhaus(soup)
        elif site == "praktiker":
            return process_praktiker(soup)

    return []

def search_products(request):
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            sort_order = request.GET.get('sort', 'name_asc')
            search_type = request.GET.get('search_type', 'simple')

            urls = {
                "toplivo": f"https://toplivo.bg/rezultati-ot-tarsene/{query}",
                # "abc": f"https://stroitelni-materiali.eu/search?query={query}",
                # "bricolage": f"https://mr-bricolage.bg/search-list?query={query}",
                # "masterhaus": f"https://www.masterhaus.bg/bg/search?q={query}",
                # "praktiker": f"https://praktiker.bg/bg/search/{query}",
            }

            # Използване на ThreadPoolExecutor за паралелни заявки
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(fetch_site, site, url)
                           for site, url in urls.items()]

                for future in futures:
                    try:
                        site_results = future.result()

                        # Ако е натиснат бутонът за стандартно търсене
                        if search_type == 'simple':
                            site_results = filter_results_by_query(
                                site_results, query)

                        # Добавяне на резултатите към списъка с всички резултати
                        results.extend(site_results)
                    except Exception as e:
                        print(f"Error fetching results: {e}")


               

            # Сортиране на резултатите по дължината на заглавията с включена търсена дума
            results = sort_results(results, sort_order)

            # Сортиране на резултатите спрямо дължината на заглавията
            results = sort_by_title_length(results)     

    return render(request, 'material_scout/search_results.html', {'form': form, 'results': results, 'query': query})

# def search_products(request):
#     results = []

#     if 'query' in request.GET:
#         form = SearchForm(request.GET)
#         if form.is_valid():
#             query = form.cleaned_data['query']
#             sort_order = request.GET.get('sort', 'name_asc')
#             search_type = request.GET.get('search_type', 'simple')

#             selected_sites = request.GET.getlist('stores')
#             print(selected_sites)
#             all_urls = {
#                 "toplivo": f"https://toplivo.bg/rezultati-ot-tarsene/{query}",
#                 "abc": f"https://stroitelni-materiali.eu/search?query={query}",
#                 "bricolage": f"https://mr-bricolage.bg/search-list?query={query}",
#                 "masterhaus": f"https://www.masterhaus.bg/bg/search?q={query}",
#                 "praktiker": f"https://praktiker.bg/bg/search/{query}",
#             }

#             if not selected_sites:
#                 selected_sites = list(all_urls.keys())

#             urls = {site: url for site, url in all_urls.items() if site in selected_sites}

#             with ThreadPoolExecutor() as executor:
#                 futures = [executor.submit(fetch_site, site, url)
#                            for site, url in urls.items()]

#                 for future in futures:
#                     try:
#                         site_results = future.result()
#                         if search_type == 'simple':
#                             site_results = filter_results_by_query(site_results, query)
#                         results.extend(site_results)
#                     except Exception as e:
#                         print(f"Error fetching results: {e}")

#             results = sort_results(results, sort_order)
#             results = sort_by_title_length(results)
#     else:
#         form = SearchForm()

#     return render(request, 'material_scout/search_results.html', {
#         'form': form,
#         'results': results,
#         'query': request.GET.get('query', ''),
#         'selected_sites': request.GET.getlist('stores')
#     })


def filter_results_by_query(results, query):
    filtered_results = []
    # A regular expression to match the word query exactly
    query_pattern = re.compile(rf'\b{re.escape(query)}\b', re.IGNORECASE)

    for result in results:
        title = result['title']

        # If the title contains an exact query match, we add it to the results
        if query_pattern.search(title):
            filtered_results.append(result)

    return filtered_results

def sort_by_title_length(results):
    # Функция за сортиране на резултатите спрямо дължината на заглавието
    def title_length_sort_key(result):
        title = result['title'].split()  # Разделя заглавието на думи
        return len(title)  # Връща броя думи в заглавието като ключ за сортиране

    # Сортиране на резултатите по дължината на заглавието (по-малко думи най-отгоре)
    return sorted(results, key=title_length_sort_key)

def sort_results(results, sort_order):
    if sort_order == 'price_asc':
        # Сортиране по цена във възходящ ред
        results.sort(key=lambda x: convert_price(x['price']))
    elif sort_order == 'price_desc':
        # Сортиране по цена в низходящ ред
        results.sort(key=lambda x: convert_price(x['price']), reverse=True)
    elif sort_order == 'name_asc':
        # Сортиране по име във възходящ ред
        results.sort(key=lambda x: x['title'].lower())
    elif sort_order == 'name_desc':
        # Сортиране по име в низходящ ред
        results.sort(key=lambda x: x['title'].lower(), reverse=True)
    return results

def convert_price(price_str):
    # Премахва символа за валута и интервалите и конвертира в число
    clean_price = price_str.replace('лв.', '').strip()
    try:
        return float(clean_price)
    except ValueError:
        return 0.0  # Ако има проблем с преобразуването, връща 0.0


def process_toplivo(soup):
    results = []
    store_name = "Toplivo"

    for item in soup.select('.productWapper1'):
        title_tag = item.select_one('.model')
        title = title_tag.get_text(strip=True) if title_tag else "Без заглавие"

        # Проверка дали продуктът е промоционален
        is_promo = item.select_one('.top-produkt.promo') is not None

        # Лева
        if is_promo:
            price_tag = item.select_one('.cenaWapper .promocena .beforedot')
            old_price_tag = item.select_one('.cenaWapper .staracena')
        else:
            price_tag = item.select_one('.cenaWapper .cena .beforedot')
            old_price_tag = None

        price_bgn = price_tag.get_text(strip=True) + " лв." if price_tag else "Няма цена"
        old_price_bgn = old_price_tag.get_text(strip=True) + " лв." if old_price_tag else None

        # Евро (само промо цена)
        euro_tag = item.select_one('.euroPrices .promocena .beforedot') if is_promo else item.select_one('.euroPrices .cena .beforedot')
        price_eur = euro_tag.get_text(strip=True) + " €" if euro_tag else None

        # Линк и изображение
        link_tag = item.select_one('figure.img a')
        link = link_tag['href'] if link_tag else '#'

        image_tag = item.select_one('img.produkt')
        image = image_tag['src'] if image_tag else None

        results.append({
            'title': title,
            'price_bgn': price_bgn,
            'old_price_bgn': old_price_bgn,
            'price_eur': price_eur,
            'is_promo': is_promo,
            'link': link,
            'store_name': store_name,
            'image': image
        })

    return results



def process_abc(soup):
    results = []
    store_name = "ABC"

    for item in soup.select('._product'):

        image_tag = item.select_one('._product-image img')

        image = image_tag.get(
            'data-first-src') or image_tag.get('src') if image_tag else None

        info_tag = item.select_one('._product-info')
        title_tag = info_tag.select_one(
            '._product-name-tag a') if info_tag else None
        link_tag = info_tag.select_one(
            '._product-name-tag a') if info_tag else None
        price_tag = info_tag.select_one(
            '._product-price .price') if info_tag else None
        new_price_tag = info_tag.select_one(
            '._product-price-compare') if info_tag else None

        title = title_tag.get_text(strip=True) if title_tag else 'Без заглавие'
        link = link_tag['href'] if link_tag else '#'
        new_price = new_price_tag.get_text(
            strip=True) if new_price_tag else 'Няма цена'
        price = price_tag.get_text(strip=True) if price_tag else new_price
        price = price.replace(',', '.')

        results.append({
            'title': title,
            'price': price,
            'link': link,
            "store_name": store_name,
            "image": image
        })

    return results

def process_bricolage(soup):
    results = []
    store_name = "Mr.Bricolage"
    for item in soup.select('.product'):
        title_tag = item.select_one('.product__title a')
        link_tag = item.select_one('.product__title a')
        first_price_tag = item.select_one('.product__price-value')
        second_price_tag = item.select_one('.fraction')

        image_tag = item.select_one('.product__image img')
        image = image_tag['src'] if image_tag else None

        title = title_tag.get_text(strip=True) if title_tag else 'Без заглавие'
        link = link_tag['href'] if link_tag else '#'
        link = f"https://mr-bricolage.bg{link}"

        first_price = first_price_tag.get_text(
            strip=True) if first_price_tag else 'Няма цена'
        second_price = second_price_tag.get_text(
            strip=True) if second_price_tag else 'Няма цена'

        price = f"{first_price}.{second_price} лв."

        results.append({
            'title': title,
            'price': price,
            'link': link,
            'image': image,
            "store_name": store_name
        })
    return results

def process_masterhaus(soup):
    results = []
    store_name = "Masterhaus"

    # Избор на продуктите в списъка
    for item in soup.select('ul.products > li'):
        title_tag = item.select_one('h2 a')
        link_tag = item.select_one('ul.products > li > div > a')
        price_tag = item.select_one('strong.price')

        # Намиране на изображението и вземане на атрибута src
        image_tag = item.select_one('a img')
        image = f"https://www.masterhaus.bg{
            image_tag['src']}" if image_tag else None

        title = title_tag.get_text(strip=True) if title_tag else 'Без заглавие'
        link = link_tag['href'] if link_tag else '#'
        link = f"https://www.masterhaus.bg{link}"

        # Извличане на цената
        if price_tag:
            # Проверка дали е промоционална цена
            if 'promo' in price_tag.get('class', []):
                del_tag = price_tag.find('del')
                if del_tag:
                    original_price_main = del_tag.select_one('span').get_text(strip=True) if del_tag.select_one(
                        'span') else ""
                    original_price_sup = del_tag.select_one('sup').get_text(strip=True) if del_tag.select_one(
                        'sup') else ""
                    original_price = f"{original_price_main}.{
                        original_price_sup} лв."

                promo_text_nodes = [node for node in price_tag.contents if isinstance(
                    node, str) and node.strip()]
                promo_price_main = promo_text_nodes[0].strip(
                ) if promo_text_nodes else ""
                promo_price_sup = price_tag.find_all('sup')[1].get_text(strip=True) if len(
                    price_tag.find_all('sup')) > 1 else ""

                price = f"{promo_price_main}.{promo_price_sup} лв."
            else:
                price_main = price_tag.contents[0].strip() if price_tag.contents and isinstance(
                    price_tag.contents[0], str) else ""
                price_sup = price_tag.find('sup').get_text(
                    strip=True) if price_tag.find('sup') else ""
                price = f"{price_main}.{price_sup} лв."
        else:
            price = "Няма цена"

        # Добавяне на резултатите, включително и изображението
        results.append({
            'title': title,
            'price': price,
            'link': link,
            'image': image,  # Ново поле за изображението
            'store_name': store_name
        })

    return results

# def process_praktiker(soup):
#     results = []
#     store_name = "Praktiker"

#     # Избор на продуктите в списъка
#     for item in soup.select('.product-grid-box.products-grid__item'):
#         title_tag = item.select_one('.product-item__title a')
#         link_tag = item.select_one('.product-item__title a')
#         price_whole_tag = item.select_one('.price__value')
#         price_fraction_tag = item.select_one('sup')

#         # Намиране на изображението и вземане на атрибута src
#         image_tag = item.select_one('img')
#         image = image_tag['src'] if image_tag else None

#         title = title_tag.get_text(strip=True) if title_tag else 'Без заглавие'
#         link = link_tag['href'] if link_tag else '#'
#         if link:
#             link = f"https://praktiker.bg/{link}"

#         # Комбиниране на цялата част и стотинките за цената
#         price_whole = price_whole_tag.get_text(
#             strip=True) if price_whole_tag else 'Няма цена'
#         price_fraction = price_fraction_tag.get_text(
#             strip=True) if price_fraction_tag else '00'
#         price = f"{price_whole}.{price_fraction} лв.".replace(',', '.')

#         # Добавяне на резултатите, включително и изображението
#         results.append({
#             'title': title,
#             'price': price,
#             'link': link,
#             'image': image,  # Ново поле за изображението
#             'store_name': store_name
#         })

#     return results
def process_praktiker(soup):
    results = []
    price_dict = {}
    store_name = "Praktiker"

    for item in soup.select('.product-grid-box.products-grid__item'):

        price_dict = extract_prices(item)
        old_price_bgn = price_dict.get('old_price_bgn')
        price_bgn = price_dict['price_bgn']
        price_eur = price_dict['price_eur']

        title_tag = item.select_one('.product-item__title a')
        link_tag = item.select_one('.product-item__title a')
        image_tag = item.select_one('.product-item__picture img')
        price_tags = item.select('.product-price__value')

        title = title_tag.get_text(strip=True) if title_tag else 'Без заглавие'
        link = link_tag['href'] if link_tag else '#'
        if link:
            link = f"https://praktiker.bg/{link}"

        image = image_tag['src'] if image_tag else None

        # # Очакваме първата цена да е в лева, втората в евро
        # price_bgn = price_tags[0].get_text(strip=True) + " лв." if len(price_tags) > 0 else 'Няма цена'
        # price_eur = price_tags[1].get_text(strip=True) + " €" if len(price_tags) > 1 else None

        results.append({
            'title': title,
            'old_price_bgn':old_price_bgn,
            'price_bgn': price_bgn,
            'price_eur': price_eur,
            'link': link,
            'image': image,
            'store_name': store_name
        })

    return results



def extract_prices(item):
    old_price_tag = item.select_one('.product-price--old .product-price__value')
    new_price_tags = item.select('.product-price:not(.product-price--old) .product-price__value')

    if old_price_tag and len(new_price_tags) >= 2:
        return {
            'old_price_bgn': old_price_tag.get_text(strip=True) + " лв.",
            'price_bgn': new_price_tags[0].get_text(strip=True) + " лв.",
            'price_eur': new_price_tags[1].get_text(strip=True) + " €"
        }
    else:
        # Стандартен продукт
        price_tags = item.select('.product-price__value')
        return {
            'old_price_bgn': None,
            'price_bgn': price_tags[0].get_text(strip=True) + " лв." if len(price_tags) > 0 else None,
            'price_eur': price_tags[1].get_text(strip=True) + " €" if len(price_tags) > 1 else None
        }
