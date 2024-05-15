import asyncio
import csv
import aiohttp
import itertools
import time
import json
import re
from bs4 import BeautifulSoup
from aiohttp import BasicAuth

user_agents_file = './user_agents.csv'

proxies = [
        {
            'ip': '216.185.47.51',
            'port': 50100,
            'username': 'skotarenko13802NDV',
            'password': 'mrmcIFWs2S'
        },
        {
            'ip': '181.215.184.198',
            'port': 50100,
            'username': 'skotarenko13802NDV',
            'password': 'mrmcIFWs2S'
        }
    ]

async def collect_csv(file_path, column=None):
    data_from_file = []
    with open(file_path, newline='') as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            if column:
                data_from_file.append(row[column])
            else:
                data_from_file.append(row)

    return data_from_file


async def collect_txt(file_path):
    with open(file_path, 'r') as file:
        data_from_file = file.readlines()

    data = [i.replace('\n', '') for i in data_from_file]

    return data


async def to_file(path, data):
    with open(path, 'w') as file:
        file.write(data)


async def read_jsoh(file_path):
    with open(file_path, 'r') as file:
        json_data = json.load(file)

    return json_data


async def auth_proxy(proxy_dict):
    username = proxy_dict.get('username')
    password = proxy_dict.get('password')
    ip = proxy_dict.get('ip')
    port = proxy_dict.get('port')

    authed_proxy = BasicAuth(username, password)
    proxy_url = f'http://{username}:{password}@{ip}:{port}'

    return {'auth': authed_proxy, 'url': proxy_url}


async def not_latin(text):
    pattern = re.compile(r'[\u4E00-\u9FFF\u3400-\u4DBF\u3040-\u30FF\uAC00-\uD7AF]', re.IGNORECASE)
    return bool(pattern.search(text))


async def aiohttp_get(cookies, url, user_agents, proxies, count):
    user_agent = next(user_agents)
    proxy = next(proxies)

    headers = {
            'User_Agent': user_agent
        }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, cookies=cookies, proxy=proxy['url'], proxy_auth=proxy['auth'], headers=headers) as response:
            page = await response.text()

            # soup = BeautifulSoup(page, 'lxml')
            # price = soup.find('div', class_='x-price-primary')
            #
            # if price:
            #     print(price.text)
            # else:
            #     if 'We looked everywhere.' not in page:
            #         print(f'No price in {url}')
            #
            #         with open(f'./responses/{time.time()}.html', 'w') as file:
            #             file.write(page)

            is_latin_check = await not_latin(page)
            if is_latin_check:
                print(f'{count}. NO LATIN')
            else:
                print(f'{count}. OK')



async def multi_get_req(file_path_url):
    proxies_auth = []
    for proxy in proxies:
        authed_proxy = await auth_proxy(proxy)
        proxies_auth.append(authed_proxy)


    user_agents = await collect_csv(user_agents_file, 1)
    urls = await collect_txt(file_path_url)

    agents_iter = itertools.cycle(user_agents)
    proxies_iter = itertools.cycle(proxies_auth)

    cookies = await read_jsoh('./cookies.json')
    # cookies = {}
    count = 1
    while urls:
        current_urls = urls[:10]
        urls = urls[10:]

        tasks = []

        for url in current_urls:
            tasks.append(aiohttp_get(cookies, url, agents_iter, proxies_iter, count))
            count += 1

        await asyncio.gather(*tasks)


if '__main__' == __name__:
    asyncio.run(multi_get_req('./urls.txt'))




