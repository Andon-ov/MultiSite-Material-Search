
"""
Material Scout - Price comparison web scraper for Bulgarian hardware stores.
Scrapes product data from multiple hardware store websites and provides
unified search and comparison functionality.
"""

from django.shortcuts import render
from .forms import SearchForm
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import re
import logging
from typing import List, Dict, Optional

# Configure logging
logger = logging.getLogger(__name__)

# Constants
STORE_CONFIGS = {
    "toplivo": {
        "name": "Toplivo",
        "url_template": "https://toplivo.bg/rezultati-ot-tarsene/{query}"
    },
    "bricolage": {
        "name": "Mr.Bricolage",
        "url_template": "https://mr-bricolage.bg/search-list?query={query}"
    },
    "masterhaus": {
        "name": "Masterhaus",
        "url_template": "https://www.masterhaus.bg/bg/search?q={query}"
    },
    "praktiker": {
        "name": "Praktiker",
        "url_template": "https://praktiker.bg/bg/search/{query}"
    }
}

DEFAULT_SORT = 'name_asc'
DEFAULT_SEARCH_TYPE = 'simple'


def home(request):
    """Render the home page."""
    return render(request, 'material_scout/home.html')


def search_products(request):
    """
    Main search view that aggregates results from multiple stores.
    Handles filtering, sorting and rendering of search results.
    """
    results = []
    form = SearchForm()
    query = ""

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            sort_order = request.GET.get('sort', DEFAULT_SORT)
            search_type = request.GET.get('search_type', DEFAULT_SEARCH_TYPE)

            # Build URLs for all stores
            urls = {
                site: config["url_template"].format(query=query)
                for site, config in STORE_CONFIGS.items()
            }

            # Fetch data from all stores concurrently
            results = fetch_all_stores(urls, query, search_type)

            # Sort results based on user preference
            results = apply_sorting(results, sort_order)

    return render(request, 'material_scout/search_results.html', {
        'form': form,
        'results': results,
        'query': query
    })


def fetch_all_stores(urls: Dict[str, str], query: str, search_type: str) -> List[Dict]:
    """
    Fetch product data from all stores concurrently.

    Args:
        urls: Dictionary mapping store names to their search URLs
        query: Search query string
        search_type: Type of search filtering to apply

    Returns:
        List of product dictionaries from all stores
    """
    results = []

    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all requests concurrently
        future_to_store = {
            executor.submit(fetch_store_data, store, url): store
            for store, url in urls.items()
        }

        # Collect results as they complete
        for future in future_to_store:
            store = future_to_store[future]
            try:
                store_results = future.result(timeout=30)  # 30s timeout per store

                if search_type == 'simple':
                    store_results = filter_results_by_exact_match(store_results, query)

                results.extend(store_results)
                logger.info(f"Successfully fetched {len(store_results)} results from {store}")

            except Exception as e:
                logger.error(f"Error fetching results from {store}: {e}")

    return results


def fetch_store_data(store: str, url: str) -> List[Dict]:
    """
    Fetch and parse data from a single store.

    Args:
        store: Store identifier
        url: Store search URL

    Returns:
        List of product dictionaries
    """
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Route to appropriate parser based on store
        parsers = {
            "toplivo": parse_toplivo,
            "bricolage": parse_bricolage,
            "masterhaus": parse_masterhaus,
            "praktiker": parse_praktiker,
        }

        parser = parsers.get(store)
        if parser:
            return parser(soup)
        else:
            logger.warning(f"No parser found for store: {store}")
            return []

    except requests.RequestException as e:
        logger.error(f"Network error fetching {store}: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error parsing {store}: {e}")
        return []


def filter_results_by_exact_match(results: List[Dict], query: str) -> List[Dict]:
    """
    Filter results to include only exact word matches of the query.

    Args:
        results: List of product dictionaries
        query: Search query string

    Returns:
        Filtered list of products containing exact query matches
    """
    if not query:
        return results

    filtered_results = []
    query_pattern = re.compile(rf'\b{re.escape(query)}\b', re.IGNORECASE)

    for result in results:
        title = result.get('title', '')
        if query_pattern.search(title):
            filtered_results.append(result)

    return filtered_results


def apply_sorting(results: List[Dict], sort_order: str) -> List[Dict]:
    """
    Sort results based on the specified order.

    Args:
        results: List of product dictionaries
        sort_order: Sorting criteria ('price_asc', 'price_desc', 'name_asc', 'name_desc')

    Returns:
        Sorted list of products
    """
    if sort_order == 'price_asc':
        results.sort(key=lambda x: (convert_price_to_float(x['price_bgn']), len(x['title'].split())))
    elif sort_order == 'price_desc':
        results.sort(key=lambda x: convert_price_to_float(x['price_bgn']), reverse=True)
    elif sort_order == 'name_asc':
        results.sort(key=lambda x: x['title'].lower())
    elif sort_order == 'name_desc':
        results.sort(key=lambda x: x['title'].lower(), reverse=True)
    elif sort_order == 'title_length':
        results.sort(key=lambda x: len(x['title'].split()))

    # Debug logging for price sorting
    if sort_order in ['price_asc', 'price_desc'] and results:
        logger.debug(f"Sorted {len(results)} results by {sort_order}")
        for i, result in enumerate(results[:5]):  # Log first 5 results
            price_val = convert_price_to_float(result['price_bgn'])
            logger.debug(f"  {i + 1}. {result['title'][:40]} - {result['price_bgn']} ({price_val})")

    return results


def convert_price_to_float(price_str: str) -> float:
    """
    Convert price string to float for sorting purposes.

    Args:
        price_str: Price string (e.g., "10.50 лв.")

    Returns:
        Float value or infinity for invalid prices
    """
    if not price_str or price_str == "Няма цена" or price_str == "No price":
        return float('inf')  # Products without price go to bottom

    # Extract numbers and decimal separators using regex
    numbers = re.findall(r'[\d,\.]+', price_str)

    if not numbers:
        logger.debug(f"No numbers found in price: '{price_str}'")
        return float('inf')

    clean_price = numbers[0]

    # Handle decimal separators
    if ',' in clean_price and '.' in clean_price:
        # Both comma and dot - comma is thousands separator
        clean_price = clean_price.replace(',', '')
    elif ',' in clean_price:
        # Only comma - could be decimal separator
        if clean_price.count(',') == 1 and len(clean_price.split(',')[1]) <= 2:
            clean_price = clean_price.replace(',', '.')
        else:
            clean_price = clean_price.replace(',', '')

    try:
        return float(clean_price)
    except (ValueError, TypeError):
        logger.debug(f"Failed to convert price: '{price_str}' -> '{clean_price}'")
        return float('inf')


def parse_toplivo(soup) -> List[Dict]:
    """
    Parse product data from Toplivo website.

    Args:
        soup: BeautifulSoup object of the page

    Returns:
        List of product dictionaries
    """
    results = []
    store_name = STORE_CONFIGS["toplivo"]["name"]

    for item in soup.select('.productWapper1'):
        # Extract title
        title_tag = item.select_one('.model')
        title = title_tag.get_text(strip=True) if title_tag else "No title"

        # Check if product is on promotion
        is_promo = item.select_one('.top-produkt.promo') is not None

        # Extract prices based on promotion status
        if is_promo:
            price_tag = item.select_one('.cenaWapper .promocena .beforedot')
            old_price_tag = item.select_one('.cenaWapper .staracena')
            all_beforedots = item.select('.cenaWapper .promocena .beforedot')
        else:
            price_tag = item.select_one('.cenaWapper .cena .beforedot')
            old_price_tag = None
            all_beforedots = item.select('.cenaWapper .cena .beforedot')

        # Extract BGN price
        price_text = price_tag.get_text(strip=True) if price_tag else None
        price_bgn = f"{price_text} лв." if price_text else "No price"

        # Extract old price if exists
        old_price_text = old_price_tag.get_text(strip=True) if old_price_tag else None
        old_price_bgn = f"{old_price_text} лв." if old_price_text else None

        # Extract EUR price (second .beforedot element)
        euro_text = None
        if len(all_beforedots) > 1:
            euro_text = all_beforedots[1].get_text(strip=True)
        price_eur = f"{euro_text} €" if euro_text else None

        # Extract link and image
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


def parse_bricolage(soup) -> List[Dict]:
    """Parse product data from Mr.Bricolage website."""
    results = []
    store_name = STORE_CONFIGS["bricolage"]["name"]

    for item in soup.select('.product'):
        # Extract basic info
        title_tag = item.select_one('.product__title a')
        image_tag = item.select_one('.product__image img')

        title = title_tag.get_text(strip=True) if title_tag else "No title"
        link = f"https://mr-bricolage.bg{title_tag['href']}" if title_tag else "#"
        image = image_tag['src'] if image_tag else None

        # Extract price information
        price_blocks = item.select('.product__prices-block')
        is_promo = False
        price_bgn = None
        old_price_bgn = None
        price_eur = None

        if len(price_blocks) >= 2:
            # First block: BGN prices
            bgn_block = price_blocks[0]
            if bgn_block.select_one('.product__price--old'):
                is_promo = True
                old_tag = bgn_block.select_one('.product__price--old')
                new_tag = bgn_block.select_one('.product__price--new')
                old_price_bgn = extract_price_from_container(old_tag)
                price_bgn = extract_price_from_container(new_tag)
            else:
                standard_tag = bgn_block.select_one('.product__price')
                price_bgn = extract_price_from_container(standard_tag)

            # Second block: EUR prices
            eur_block = price_blocks[1]
            if eur_block.select_one('.product__price--new'):
                price_eur = extract_price_from_container(eur_block.select_one('.product__price--new'))
            else:
                price_eur = extract_price_from_container(eur_block.select_one('.product__price'))

        results.append({
            'title': title,
            'price_bgn': price_bgn or "No price in BGN",
            'old_price_bgn': old_price_bgn,
            'price_eur': price_eur or "No price in EUR",
            'is_promo': is_promo,
            'link': link,
            'image': image,
            'store_name': store_name
        })

    return results


def extract_price_from_container(container) -> Optional[str]:
    """Extract price from Bricolage price container."""
    if not container:
        return None

    value = container.select_one('.product__price-value')
    fraction = container.select_one('.fraction')
    currency = container.select_one('.currency')

    if value and fraction and currency:
        return f"{value.get_text(strip=True)}.{fraction.get_text(strip=True)} {currency.get_text(strip=True)}"
    return None


def parse_masterhaus(soup) -> List[Dict]:
    """Parse product data from Masterhaus website."""
    results = []
    store_name = STORE_CONFIGS["masterhaus"]["name"]

    for item in soup.select('ul.products > li'):
        # Extract basic information
        title_tag = item.select_one('h2 a')
        link_tag = item.select_one('a')
        price_tag = item.select_one('strong.price')

        title = title_tag.get_text(strip=True) if title_tag else 'No title'
        link = f"https://www.masterhaus.bg{link_tag['href']}" if link_tag else '#'
        image = extract_primary_image(item)

        # Initialize price variables
        price_bgn = None
        old_price_bgn = None
        price_eur = None
        is_promo = False
        promo_type = None

        if price_tag:
            classes = price_tag.get('class', [])
            if 'promo' in classes or 'top' in classes:
                is_promo = True
                promo_type = 'брошура' if 'promo' in classes else 'винаги ниска цена'

                # Extract old price
                del_tag = price_tag.select_one('del')
                if del_tag:
                    old_price_parts = extract_masterhaus_price_parts(del_tag)
                    if old_price_parts:
                        old_price_bgn = format_price(*old_price_parts)

                # Extract current price in BGN
                actual_tag = price_tag.select_one('.price-actual')
                if actual_tag:
                    bgn_parts = extract_masterhaus_price_parts(actual_tag, use_contents=True)
                    if bgn_parts:
                        price_bgn = format_price(*bgn_parts)

                # Extract EUR price
                euro_tag = price_tag.select_one('.price-second')
                if euro_tag:
                    eur_parts = extract_masterhaus_price_parts(euro_tag, use_contents=True)
                    if eur_parts:
                        price_eur = format_price(*eur_parts)
            else:
                # Standard pricing
                actual_tag = price_tag.select_one('.price-actual')
                euro_tag = price_tag.select_one('.price-second')

                if actual_tag:
                    bgn_parts = extract_masterhaus_price_parts(actual_tag, use_contents=True)
                    if bgn_parts:
                        price_bgn = format_price(*bgn_parts)

                if euro_tag:
                    eur_parts = extract_masterhaus_price_parts(euro_tag, use_contents=True)
                    if eur_parts:
                        price_eur = format_price(*eur_parts)

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


def extract_primary_image(item) -> Optional[str]:
    """Extract primary product image from Masterhaus item."""
    image_tags = item.select('a img')
    for img in image_tags:
        if 'photo-second' not in img.get('class', []):
            src = img.get('src')
            if src:
                return f"https://www.masterhaus.bg{src}"
    return None


def extract_masterhaus_price_parts(container, use_contents=False) -> Optional[tuple]:
    """Extract price components from Masterhaus price container."""
    if not container:
        return None

    if use_contents:
        main = container.contents[0].strip() if container.contents else ""
    else:
        main_tag = container.select_one('span')
        main = main_tag.get_text(strip=True) if main_tag else ""

    sup = container.select_one('sup')
    currency = container.select_one('abbr')

    if sup and currency:
        return (main, sup.get_text(strip=True), currency.get_text(strip=True))
    return None


def format_price(main: str, fraction: str, currency: str) -> str:
    """Format price components into a single price string."""
    return f"{main}.{fraction} {currency}"


def parse_praktiker(soup) -> List[Dict]:
    """Parse product data from Praktiker website."""
    results = []
    store_name = STORE_CONFIGS["praktiker"]["name"]

    for item in soup.select('.product-grid-box.products-grid__item'):
        # Extract basic information
        title_tag = item.select_one('.product-item__title a')
        link_tag = item.select_one('.product-item__title a')
        image_tag = item.select_one('.product-item__picture img')

        title = title_tag.get_text(strip=True) if title_tag else 'No title'
        link = f"https://praktiker.bg/{link_tag['href']}" if link_tag else '#'
        image = image_tag['src'] if image_tag else None

        # Extract price information
        price_data = extract_praktiker_prices(item)

        results.append({
            'title': title,
            'old_price_bgn': price_data.get('old_price_bgn'),
            'price_bgn': price_data['price_bgn'],
            'price_eur': price_data['price_eur'],
            'link': link,
            'image': image,
            'store_name': store_name
        })

    return results


def extract_praktiker_prices(item) -> Dict[str, Optional[str]]:
    """Extract price information from Praktiker product item."""
    old_price_tag = item.select_one('.product-price--old .product-price__value')
    new_price_tags = item.select('.product-price:not(.product-price--old) .product-price__value')

    if old_price_tag and len(new_price_tags) >= 2:
        # Promotional product with old price
        return {
            'old_price_bgn': f"{old_price_tag.get_text(strip=True)} лв.",
            'price_bgn': f"{new_price_tags[0].get_text(strip=True)} лв.",
            'price_eur': f"{new_price_tags[1].get_text(strip=True)} €"
        }
    else:
        # Standard product
        price_tags = item.select('.product-price__value')
        return {
            'old_price_bgn': None,
            'price_bgn': f"{price_tags[0].get_text(strip=True)} лв." if len(price_tags) > 0 else None,
            'price_eur': f"{price_tags[1].get_text(strip=True)} €" if len(price_tags) > 1 else None
        }

