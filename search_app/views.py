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
                "bricolage": f"https://mr-bricolage.bg/search-list?query={query}",
                "masterhaus": f"https://www.masterhaus.bg/bg/search?q={query}",
                "praktiker": f"https://praktiker.bg/bg/search/{query}",
            }

            # Използване на ThreadPoolExecutor за паралелни заявки
            with ThreadPoolExecutor() as executor:
                futures = []
                for site, url in urls.items():
                    print(f"[DEBUG] Submitting site='{site}' with url='{url}'")
                    future = executor.submit(fetch_site, site, url)
                    futures.append(future)

                for future in futures:
                    try:
                        site_results = future.result()

                        if search_type == 'simple':
                            site_results = filter_results_by_query(
                                site_results, query)

                        results.extend(site_results)
                    except Exception as e:
                        print(f"Error fetching results: {e}")

            # Сортиране на резултатите по дължината на заглавията с включена търсена дума
            results = sort_results(results, sort_order)

            # Сортиране на резултатите спрямо дължината на заглавията
            results = sort_by_title_length(results)

    return render(request, 'material_scout/search_results.html', {'form': form, 'results': results, 'query': query})


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
        # Връща броя думи в заглавието като ключ за сортиране
        return len(title)

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

        price_bgn = price_tag.get_text(
            strip=True) + " лв." if price_tag else "Няма цена"
        old_price_bgn = old_price_tag.get_text(
            strip=True) + " лв." if old_price_tag else None

        # Евро (само промо цена)
        euro_tag = item.select_one('.euroPrices .promocena .beforedot') if is_promo else item.select_one(
            '.euroPrices .cena .beforedot')
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

def process_bricolage(soup):
    results = []
    store_name = "Mr.Bricolage"

    for item in soup.select('.product'):
        title_tag = item.select_one('.product__title a')
        image_tag = item.select_one('.product__image img')
        image = image_tag['src'] if image_tag else None
        title = title_tag.get_text(strip=True) if title_tag else "Без заглавие"
        link = f"https://mr-bricolage.bg{title_tag['href']}" if title_tag else "#"

        # Извличане на ценови блокове
        price_blocks = item.select('.product__prices-block')
        is_promo = False
        price_bgn = None
        old_price_bgn = None
        price_eur = None

        if len(price_blocks) >= 2:
            # Първи блок: лева
            bgn_block = price_blocks[0]
            if bgn_block.select_one('.product__price--old'):
                is_promo = True
                old_tag = bgn_block.select_one('.product__price--old')
                new_tag = bgn_block.select_one('.product__price--new')
                old_price_bgn = extract_price(old_tag)
                price_bgn = extract_price(new_tag)
            else:
                standard_tag = bgn_block.select_one('.product__price')
                price_bgn = extract_price(standard_tag)

            # Втори блок: евро
            eur_block = price_blocks[1]
            if eur_block.select_one('.product__price--new'):
                price_eur = extract_price(
                    eur_block.select_one('.product__price--new'))
            else:
                price_eur = extract_price(
                    eur_block.select_one('.product__price'))

        results.append({
            'title': title,
            'price_bgn': price_bgn or "Няма цена в лева",
            'old_price_bgn': old_price_bgn,
            'price_eur': price_eur or "Няма цена в евро",
            'is_promo': is_promo,
            'link': link,
            'image': image,
            "store_name": store_name
        })

    return results

def extract_price(container):
    if not container:
        return None
    value = container.select_one('.product__price-value')
    fraction = container.select_one('.fraction')
    currency = container.select_one('.currency')
    if value and fraction and currency:
        return f"{value.get_text(strip=True)}.{fraction.get_text(strip=True)} {currency.get_text(strip=True)}"
    return None

def process_masterhaus(soup):
    results = []
    store_name = "Masterhaus"

    for item in soup.select('ul.products > li'):
        title_tag = item.select_one('h2 a')
        image_tag = item.select_one('a img')
        price_tag = item.select_one('strong.price')
        link_tag = item.select_one('a')

        title = title_tag.get_text(strip=True) if title_tag else 'Без заглавие'
        link = f"https://www.masterhaus.bg{link_tag['href']}" if link_tag else '#'
        # image = f"https://www.masterhaus.bg{image_tag['src']}" if image_tag and image_tag.has_attr('src') else None
        image = get_primary_image(item)


        # Инициализация на цените
        price_bgn = None
        old_price_bgn = None
        price_eur = None
        is_promo = False
        promo_type = None

        if price_tag:
            classes = price_tag.get('class', [])
            if 'promo' in classes or 'top' in classes:
                is_promo = True
                promo_type = 'от брошура' if 'promo' in classes else 'винаги ниска цена'

                # Стара цена (ако има)
                del_tag = price_tag.select_one('del')
                if del_tag:
                    old_main = del_tag.select_one('span')
                    old_sup = del_tag.select_one('sup')
                    old_currency = del_tag.select_one('abbr')
                    if old_main and old_sup and old_currency:
                        old_price_bgn = f"{old_main.get_text(strip=True)}.{old_sup.get_text(strip=True)} {old_currency.get_text(strip=True)}"

                # Нова цена в лева
                actual_tag = price_tag.select_one('.price-actual')
                if actual_tag:
                    main = actual_tag.contents[0].strip() if actual_tag.contents else ""
                    sup = actual_tag.select_one('sup')
                    currency = actual_tag.select_one('abbr')
                    if sup and currency:
                        price_bgn = f"{main}.{sup.get_text(strip=True)} {currency.get_text(strip=True)}"

                # Цена в евро
                euro_tag = price_tag.select_one('.price-second')
                if euro_tag:
                    euro_main = euro_tag.contents[0].strip() if euro_tag.contents else ""
                    euro_sup = euro_tag.select_one('sup')
                    euro_currency = euro_tag.select_one('abbr')
                    if euro_sup and euro_currency:
                        price_eur = f"{euro_main}.{euro_sup.get_text(strip=True)} {euro_currency.get_text(strip=True)}"
            else:
                # Стандартна цена
                actual_tag = price_tag.select_one('.price-actual')
                euro_tag = price_tag.select_one('.price-second')

                if actual_tag:
                    main = actual_tag.contents[0].strip() if actual_tag.contents else ""
                    sup = actual_tag.select_one('sup')
                    currency = actual_tag.select_one('abbr')
                    if sup and currency:
                        price_bgn = f"{main}.{sup.get_text(strip=True)} {currency.get_text(strip=True)}"

                if euro_tag:
                    euro_main = euro_tag.contents[0].strip() if euro_tag.contents else ""
                    euro_sup = euro_tag.select_one('sup')
                    euro_currency = euro_tag.select_one('abbr')
                    if euro_sup and euro_currency:
                        price_eur = f"{euro_main}.{euro_sup.get_text(strip=True)} {euro_currency.get_text(strip=True)}"

        results.append({
            'title': title,
            'price_bgn': price_bgn,
            'old_price_bgn': old_price_bgn,
            'price_eur': price_eur,
            'is_promo': is_promo,
            'promo_type': promo_type,
            'link': link,
            'image': image,
            'store_name': store_name
        })

    return results

def get_primary_image(item):
    # Взимаме всички <img> тагове в линка
    image_tags = item.select('a img')
    for img in image_tags:
        # Пропускаме снимки с клас photo-second
        if 'photo-second' not in img.get('class', []):
            src = img.get('src')
            if src:
                return f"https://www.masterhaus.bg{src}"
    # Ако няма подходяща снимка, връщаме None
    return None

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
            'old_price_bgn': old_price_bgn,
            'price_bgn': price_bgn,
            'price_eur': price_eur,
            'link': link,
            'image': image,
            'store_name': store_name
        })

    return results

def extract_prices(item):
    old_price_tag = item.select_one(
        '.product-price--old .product-price__value')
    new_price_tags = item.select(
        '.product-price:not(.product-price--old) .product-price__value')

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
