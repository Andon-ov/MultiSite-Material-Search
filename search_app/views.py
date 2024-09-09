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
            urls = {
                "toplivo": f"https://toplivo.bg/rezultati-ot-tarsene/{query}",
                "abc": f"https://stroitelni-materiali.eu/search?query={query}",
                "bricolage": f"https://mr-bricolage.bg/search-list?query={query}",
                "masterhaus": f"https://www.masterhaus.bg/bg/search?q={query}",
                "praktiker": f"https://praktiker.bg/bg/search/{query}",

            }

            # Using ThreadPoolExecutor for parallel requests
            with ThreadPoolExecutor() as executor:
                futures = [executor.submit(fetch_site, site, url) for site, url in urls.items()]

                for future in futures:
                    try:
                        site_results = future.result()

                        # Filter the results
                        filtered_results = filter_results_by_query(site_results, query)

                        results.extend(filtered_results)
                    except Exception as e:
                        print(f"Error fetching results: {e}")

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


def process_toplivo(soup):
    results = []
    store_name = "Toplivo"  # The name of the store

    for item in soup.select('.productWapper1.search'):
        title_tag = item.select_one(
            'div.productWapper1 > div:nth-child(1) > div:nth-child(2) > h3:nth-child(2) > a:nth-child(1) > span:nth-child(2)')

        second_title = item.select_one(
            'div.productWapper1 > div:nth-child(1) > div:nth-child(2) > h3:nth-child(3) > a:nth-child(1) > span:nth-child(1)')
        three_title = item.select_one(
            'div.productWapper1 > div:nth-child(1) > div:nth-child(2) > h3:nth-child(3) > a:nth-child(1) > span:nth-child(2)')

        subtitle = item.select_one(
            'div.productWapper1 > div:nth-child(1) > div:nth-child(2) > div:nth-child(1)')

        # If the title is not available, try a second and third title
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

        # Extract the texts for the different prices
        red_price = red_price_tag.get_text(
            strip=True) if red_price_tag else None
        new_price = new_price_tag.get_text(
            strip=True) if new_price_tag else None
        valid_price = price_tag.get_text(strip=True) if price_tag else None
        
        if red_price or new_price or valid_price:
            valid_price = f"{valid_price} лв."

        # Price priority logic: checks valid_price first, then red_price, and finally new_price
        price = valid_price or red_price or new_price or 'Няма цена'

        results.append({'title': title, 'price': price,
                       'link': link, 'store_name': store_name})

    return results


def process_abc(soup):
    results = []
    store_name = "ABC"
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
        price = price.replace(',', '.')

        results.append({'title': title, 'price': price,
                       'link': link, "store_name": store_name})
    return results


def process_bricolage(soup):
    results = []
    store_name = "Mr.Bricolage"
    for item in soup.select('.product'):
        title_tag = item.select_one('.product__title a')
        link_tag = item.select_one('.product__title a')
        first_price_tag = item.select_one('.product__price-value')
        second_price_tag = item.select_one('.fraction')

        title = title_tag.get_text(strip=True) if title_tag else 'Без заглавие'
        link = link_tag['href'] if link_tag else '#'
        link = f"https://mr-bricolage.bg{link}"

        first_price = first_price_tag.get_text(
            strip=True) if first_price_tag else 'Няма цена'
        second_price = second_price_tag.get_text(
            strip=True) if second_price_tag else 'Няма цена'

        price = f"{first_price}.{second_price} лв."

        results.append({'title': title, 'price': price,
                       'link': link, "store_name": store_name})
    return results


def process_masterhaus(soup):
    results = []
    store_name = "Masterhaus"
    for item in soup.select('ul.products > li'):
        title_tag = item.select_one('h2 a')
        link_tag = item.select_one('ul.products > li > div > a')
        price_tag = item.select_one('strong.price')


        title = title_tag.get_text(strip=True) if title_tag else 'Без заглавие'
        link = link_tag['href'] if link_tag else '#'
        link = f"https://www.masterhaus.bg{link}"


        if price_tag:
            # Checking if it's a promotional price
            if 'promo' in price_tag.get('class', []):
                # Retrieve the old price
                del_tag = price_tag.find('del')
                if del_tag:
                    original_price_main = del_tag.select_one('span').get_text(strip=True) if del_tag.select_one(
                        'span') else ""
                    original_price_sup = del_tag.select_one('sup').get_text(strip=True) if del_tag.select_one(
                        'sup') else ""
                    original_price = f"{original_price_main}.{original_price_sup} лв."

                # Get the promotional price
                promo_text_nodes = [node for node in price_tag.contents if isinstance(node, str) and node.strip()]
                promo_price_main = promo_text_nodes[0].strip() if promo_text_nodes else ""
                promo_price_sup = price_tag.find_all('sup')[1].get_text(strip=True) if len(
                    price_tag.find_all('sup')) > 1 else ""

                price = f"Промо: {promo_price_main}.{promo_price_sup} лв. (стара цена: {original_price})"
            else:
                # Derivation of the ordinary price
                price_main = price_tag.contents[0].strip() if price_tag.contents and isinstance(price_tag.contents[0],
                                                                                                str) else ""
                price_sup = price_tag.find('sup').get_text(strip=True) if price_tag.find('sup') else ""
                price = f"{price_main}.{price_sup} лв."
        else:
            price = "Няма цена"

        results.append({'title': title, 'price': price, 'link': link, "store_name":store_name})
    return results

def process_praktiker(soup):
    results = []
    store_name = "Praktiker"
    for item in soup.select('.product-grid-box.products-grid__item'):
        title_tag = item.select_one('.product-item__title a')
        link_tag = item.select_one('.product-item__title a')
        price_whole_tag = item.select_one('.price__value')
        price_fraction_tag = item.select_one('sup')

        title = title_tag.get_text(strip=True) if title_tag else 'Без заглавие'
        link = link_tag['href'] if link_tag else '#'
        
        # Combine the whole number and pennies for the price
        price_whole = price_whole_tag.get_text(strip=True) if price_whole_tag else 'Няма цена'
        price_fraction = price_fraction_tag.get_text(strip=True) if price_fraction_tag else '00'
        price = f"{price_whole}.{price_fraction} лв.".replace(',', '.')

        results.append({'title': title, 'price': price, 'link': link, "store_name": store_name})
    return results


