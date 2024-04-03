import requests
from loguru import logger
from lxml import html


def get_holidays(url):
    html_content = requests.get(url).content
    tree = html.fromstring(html_content)

    # Extract holiday information
    holidays = []
    for li_element in tree.xpath('/html/body/div[1]/main/div[1]/article/section[1]/ul/li'):
        holiday_info = {}
        holiday_name = li_element[0].text
        likes = li_element.xpath('.//form/button/span')[0].text
        holiday_info['name'] = holiday_name
        holiday_info['likes'] = int(likes)
        holidays.append(holiday_info)

    sorted_holidays: list[dict] = sorted(holidays, key=lambda x: x['likes'], reverse=True)
    logger.info(sorted_holidays)
    logger.info(f'Get from {url} {len(sorted_holidays)} holidays')

    return '\n'.join([holiday['name'] for holiday in sorted_holidays[:5]])
