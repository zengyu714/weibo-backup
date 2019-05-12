import os
import time
import json
import random

import requests
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
    response = get_response_by_page_number(1)

    if 'data' in response:
        data = response['data']
        entries_nums = data['cardlistInfo']['total']
        return entries_nums
    else:
        print('"%s" contains no "data"' % response)
        exit(-1)


def get_response_by_page_number(page_num):
    if CONFIG.use_proxy:
        proxy = random.choice(CONFIG.proxy_list)
        print('Using proxy "%s" ...' % proxy)
        response = requests.get(url_template.format(page_num),
                                headers=headers,
                                proxies=proxy).json()
    else:
        response = requests.get(url_template.format(page_num),
                                headers=headers).json()
    return response


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
    for page_i in range(1, pages_num + 1):
        print('Processing page: %d' % page_i)
        response = get_response_by_page_number(page_i)

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
        'text'           : mblog['text']
                            # remove escape characters
                            .replace('\\', '')
                            # fix invalidated url issue
                            .replace('//h5.sinaimg', 'https://h5.sinaimg'),
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
                    json_data = json.loads(f.read())
                    if 'data' in json_data:
                        contents = json_data['data']['cards']
                    else:
                        print('"%s" contains no "data" key' % json_data)
                        continue

                for card in contents:
                    # fix KeyError: 'mblog'
                    if 'mblog' not in card:
                        continue

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
                        # Use doc.asis() to add html, See: https://www.yattag.org/
                        doc.asis(info['text'])
                        # retweet TODO

                    # image
                    if 'pics' in mblog:
                        for pic in mblog['pics']:
                            with tag('span', klass='mblog_image'):
                                doc.stag('img', src=pic['url'], klass='span_image')
                    # deliminator
                    doc.stag('hr')

                    # TODO: enable parse details
                    # details = _parse_details(info) if info['is_long'] or info['comments_count'] else None
                    # print('details: "%s"' % details)
    backup = doc.getvalue()
    with open('mblog_backup_{}.html'.format(
            time.strftime("%Y%m%d", time.localtime())), 'w+', encoding='utf-8') as f:
        f.write(backup)


def main():
    if CONFIG.model == 'save_json_first':
        save_pages_json()

    generate_html()
    print("Done")


if __name__ == '__main__':
    main()
