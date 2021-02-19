import sys
import requests
import time

from random import randrange


GITHUB_SEARCH_API = 'https://api.github.com/search/code?q='
START_PAGE_NUMBER = 1
SEARCH_QUERY = 'user%3A{}+filename%3Apackage.json+NOT+example+NOT+boilerplate&type=code&page='
GH_RESULTS_PER_PAGE = 30



# HELPER FUNCTIONS

def _get_url(user):
    searchQuery = SEARCH_QUERY.format(user)
    return f'{GITHUB_SEARCH_API}{searchQuery}'

def _get_github_username():
    args = sys.argv

    if len(args) < 2:
        print('Missing username!')
        exit()

    return args[1]


def _get_url_result(url):

    response = requests.get(url)

    if response.status_code != 200:
        print(f'Failed with error code {response.status_code}')
        return {}
        
    return response.json()

def _get_total_pages(url):

    result = _get_url_result(f'{url}{START_PAGE_NUMBER}')

    total_count = 1
    if 'total_count' in result:
        total_count = result['total_count']

    if total_count > GH_RESULTS_PER_PAGE:
        return int(total_count / GH_RESULTS_PER_PAGE)

    # If total results are less than the total results in one page
    # Return 2, since page_numbers starts with 1.
    # So it needs to do 1 iteration
    return 2


# MAIN CODE

user = _get_github_username()
url = _get_url(user)

total_urls = 0
total_pages = _get_total_pages(url)

for page_number in range(START_PAGE_NUMBER, total_pages):
    
#    print(page_number)
    result = _get_url_result(f'{url}{page_number}')

    items = []
    if 'items' in result:
        items = result['items']

    for item in items:

        if 'html_url' in item:
            html_url = item['html_url']
            html_url = html_url.replace('https://github.com', 'https://raw.githubusercontent.com')
            html_url = html_url.replace('/blob/', '/')

            if html_url:
                total_urls = total_urls + 1
                print(html_url)
    
    rand = randrange(20)
    time.sleep(rand)
