import os
import time
import json
import random

import requests
from yattag import Doc

from configuration import CONFIG

COMMENTS_URL = "https://m.weibo.cn/comments/hotflow?id=%s&mid=%s&max_id_type=0"

ARTICLE_URL = "http://card.weibo.com/article/aj/articleshow?cid=%s&vid=%s"

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
    return get_response(url_template.format(page_num)).json()


def get_response(url):
    if CONFIG.use_proxy:
        proxy = random.choice(CONFIG.proxy_list)
        print('Using proxy "%s" ...' % proxy)
        response = requests.get(url, headers=headers, proxies=proxy)
    else:
        response = requests.get(url, headers=headers)
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


def save_comments_json(mblog, comments_json):
    """Create folder `./comments` to save json contents"""

    # make directory
    if not os.path.exists('comments'):
        os.makedirs('comments')

    with open('comments/comments_%s_%s' % (mblog['id'], mblog['mid']), 'w+') as f:
        json.dump(comments_json, f)


def save_article_json(article_json, user_id, cid):
    """Create folder `./articles` to save json contents"""

    # make directory
    if not os.path.exists('articles'):
        os.makedirs('articles')

    with open('articles/articles_%s_%s' % (user_id, cid), 'w+') as f:
        json.dump(article_json, f)


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


def has_comments(response):
    if response is not None and 'data' in response and 'data' in response['data']:
        comments = response['data']['data']
        if len(comments) > 0:
            return comments
        else:
            print("No comments, response for retrieve comments: %s" % response)
    else:
        print("No comments, response for retrieve comments: %s" % response)
    return ""


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

                    # image
                    if 'pics' in mblog:
                        for pic in mblog['pics']:
                            with tag('span', klass='mblog_image'):
                                doc.stag('img', src=pic['url'], klass='span_image')

                    # my article
                    if 'page_info' in mblog:
                        page_info = mblog['page_info']
                        if 'page_url' in page_info:
                            object_id = mblog['page_info']['object_id']
                            if object_id is not None:
                                object_ids = object_id.split(':')
                                if len(object_ids) >= 2:
                                    cid = object_ids[1]
                                    user_id = mblog['user']['id']
                                    article_json_filename = 'articles_%s_%s' % (user_id, cid)
                                    if os.path.exists("articles") \
                                            and article_json_filename in os.listdir("articles"):
                                        with open("articles/" + article_json_filename, 'r') as f:
                                            response = json.loads(f.read())
                                    else:
                                        response = get_response(ARTICLE_URL % (cid, user_id)).json()
                                        save_article_json(response, user_id, cid)

                                    if response['msg'] == 'ok' and 'data' in response:
                                        doc.asis("<div>Article:</div>")
                                        data = response['data']
                                        article_text = data['article']
                                        with tag('div', klass='article_text'):
                                            doc.asis(article_text)

                    # comments
                    if mblog['comments_count'] > 0:
                        comment_json_filename = "comments_%s_%s" % (mblog['id'], mblog['mid'])
                        if os.path.exists('comments') \
                                and comment_json_filename in os.listdir('comments'):
                            with open("comments/" + comment_json_filename, 'r') as f:
                                response = json.loads(f.read())
                        else:
                            comments_url = COMMENTS_URL % (mblog['id'], mblog['mid'])
                            response = get_response(comments_url).json()
                            # Save all comments json files to avoid to retrieve comments data from Weibo
                            # whether has comment or not
                            save_comments_json(mblog, response)

                        comments = has_comments(response)
                        if len(comments) > 0:
                            doc.asis("<div>评论：</div>")
                            for comment in comments:
                                with tag('div', klass='comment_basic_info'):
                                    doc.asis('<a href="{}">{}</a> @ {}'.format(
                                        comment['user']['profile_url'],
                                        comment['user']['screen_name'],
                                        comment['created_at']))

                                comment_text = comment['text']
                                with tag('div', klass='comments_text'):
                                    doc.asis(comment_text)

                    # retweet
                    if 'retweeted_status' in mblog:
                        doc.asis("<div>转载内容：</div>")
                        retweet = mblog['retweeted_status']
                        if 'user' in retweet and retweet['user'] is not None:
                            profile_url = retweet['user']['profile_url']
                            screen_name = retweet['user']['screen_name']
                        else:
                            profile_url = ""
                            screen_name = "Failed to retrieve user name"

                        with tag('div', klass='retweet_info'):
                            doc.asis('@<a href="{}">{}</a> @ {}'.format(
                                profile_url,
                                screen_name,
                                retweet['created_at']))

                        with tag('div', klass='retweet_text'):
                            doc.asis(retweet['text'])

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
