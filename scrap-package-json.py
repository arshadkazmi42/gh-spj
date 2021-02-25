import sys
import requests
import time

from sys import stderr
from random import randrange


GITHUB_SEARCH_API = 'https://api.github.com/search/code?q='
START_PAGE_NUMBER = 1
SEARCH_QUERY = 'user%3A{}+filename%3Apackage.json+NOT+example+NOT+boilerplate&type=code&page='
GH_RESULTS_PER_PAGE = 30
GH_TOKEN = None
DEBUG = False



# HELPER FUNCTIONS

def _print(text):
    # TODO Add debug / verbose flag / accept from arg
    if DEBUG:
        print(text)

def _get_url(user):
    searchQuery = SEARCH_QUERY.format(user)
    return f'{GITHUB_SEARCH_API}{searchQuery}'

def _get_github_username():
    args = sys.argv

    if len(args) < 2:
        _print('Missing username!')
        exit()

    return args[1]

def _get_gh_token():
    args = sys.argv

    _print(args)
    _print(len(args))

    if len(args) < 3:
        _print('Missing token')
        return

    return args[2]

def _check_rate_limit(response):
    if response.status_code == 403:
        if 'X-RateLimit-Reset' in response.headers:
            reset_time = int(response.headers['X-RateLimit-Reset'])
            current_time = int(time.time())
            sleep_time = reset_time - current_time + 1
            _print(f'\n\nGitHub Search API rate limit reached. Sleeping for {sleep_time} seconds.\n\n')
            time.sleep(sleep_time)
            return True
    
    return False


def _get_url_result(url, token):

    headers = {}    

    if not token and GH_TOKEN:
        token = GH_TOKEN

    if token:
        headers['Authorization'] = f'token {token}'

    _print(headers)

    response = requests.get(url, headers=headers)

    # if rate limit reached
    # Check and wait for x seconds
    if response.status_code == 403:
        if _check_rate_limit(response):
            response = requests.get(url)

    if response.status_code != 200:
        _print(f'Failed with error code {response.status_code}')
        return {}
        
    return response.json()

def _get_total_pages(url, gh_token):

    result = _get_url_result(f'{url}{START_PAGE_NUMBER}', gh_token)

    total_count = 1
    if 'total_count' in result:
        total_count = result['total_count']

    if total_count > GH_RESULTS_PER_PAGE:
        return int(total_count / GH_RESULTS_PER_PAGE) + 1

    # If total results are less than the total results in one page
    # Return 2, since page_numbers starts with 1.
    # So it needs to do 1 iteration
    return 2


# MAIN CODE

gh_token = _get_gh_token()

user = _get_github_username()
url = _get_url(user)

total_urls = 0
total_pages = _get_total_pages(url, gh_token)

for page_number in range(START_PAGE_NUMBER, total_pages):
    
    # print(page_number)
    result = _get_url_result(f'{url}{page_number}', gh_token)

    if 'items' in result:
        items = result['items']

        for item in items:

            if 'html_url' in item:
                html_url = item['html_url']
                html_url = html_url.replace('https://github.com', 'https://raw.githubusercontent.com')
                html_url = html_url.replace('/blob/', '/')

                if html_url and 'node_modules' not in html_url:
                    total_urls = total_urls + 1
                    print(html_url)
