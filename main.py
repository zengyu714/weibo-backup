import os
import time
import json
import random

import requests
from tqdm import tqdm
from yattag import Doc

from configuration import CONFIG

url_template = CONFIG.url_template + '&page={}'
headers = {
    'User-Agent': CONFIG.user_agent,
    'cookie'    : CONFIG.cookie
}
proxy_list = CONFIG.proxy_list


def get_entries_num():
    """Get total num of weibo entries"""
    response = requests.get(url_template.format(1),
                            headers=headers,
                            proxies=random.choice(proxy_list)).json()
    entries_nums = response['data']['cardlistInfo']['total']
    return entries_nums


def save_pages_json():
    """Create folder `./pages` to save json contents"""

    # make directory
    if not os.path.exists('pages'):
        os.makedirs('pages')

    # calculate entries nums
    entries_num = get_entries_num()
    pages_num = entries_num // 10 + 1
    print('==> Saving {} entries (default {} pages)'.format(entries_num, pages_num))

    # make url requests
    for page_i in tqdm(range(1, pages_num + 1)):
        response = requests.get(url_template.format(page_i),
                                headers=headers,
                                proxies=random.choice(proxy_list)).json()

        with open('pages/content_page_{:03d}'.format(page_i), 'w+') as f:
            json.dump(response, f)

        # randomly sleep [0, 1] second
        time.sleep(random.random())


def _parse_info(mblog):
    base = {
        'name'           : mblog['user']['screen_name'],
        'source'         : mblog['source'],
        'create_time'    : mblog['created_at'],
        'mid'            : mblog['mid'],
        'text'           : mblog['text'],
        'comments_count' : mblog['comments_count'],
        'attitudes_count': mblog['attitudes_count'],
        'is_long'        : mblog['isLongText']
    }
    if 'pics' in mblog:
        base.update({'pics': mblog['pics']})
    return base


def _parse_details(info):
    """Check details if the micro blog is longer than 140 or has comments"""

    detailed_url = 'https://m.weibo.cn/status/{}'.format(info['mid'])
    detailed_header = dict(headers)
    detailed_header.update({'Referer': detailed_url})
    details = requests.get(detailed_url, headers=detailed_header).json()
    return details


def generate_html():
    pages = sorted([os.path.join('pages', i)
                    for i in os.listdir('pages') if i.startswith('content')])

    doc, tag, text, line = Doc().ttl()
    doc.asis('<!DOCTYPE html>')

    with tag('html'):
        with tag('body'):
            line('h3', 'Backup @ {}'.format(time.ctime()))

            for p in pages:
                with open(p, 'r') as f:
                    contents = json.loads(f.read())['data']['cards']
                for card in contents:
                    mblog = card['mblog']
                    info = _parse_info(mblog)

                    # deliminator
                    doc.stag('hr')

                    # basic information
                    with tag('div', klass='mblog_info'):
                        text('{} @ {} << {}'.format(
                                info['name'], info['create_time'], info['source']))
                    # text
                    with tag('div', klass='mblog_text'):
                        text(mblog['text'])
                    # image
                    if 'pics' in mblog:
                        for pic in mblog['pics']:
                            with tag('span', klass='mblog_image'):
                                doc.stag('img', src=pic['url'], klass='span_image')
                    # deliminator
                    doc.stag('hr')

                    # TODO: enable parse details
                    # details = _parse_details(info) if info['is_long'] or info['comments_count'] else None
    backup = doc.getvalue()
    with open('mblog_backup_{}.html'.format(
            time.strftime("%Y%m%d", time.localtime())), 'w+', encoding='utf-8') as f:
        f.write(backup)


def main():
    # save_pages_json()
    generate_html()


if __name__ == '__main__':
    main()
