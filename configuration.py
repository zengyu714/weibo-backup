from easydict import EasyDict

CONFIG = EasyDict()

# Compulsory
CONFIG.url_template = 'your_weibo_url'
CONFIG.cookie = 'your_cookie'

# Optional
CONFIG.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) ' \
                    'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                    'Chrome/66.0.3359.117 Safari/537.36'

CONFIG.proxy_list = [{"http": "116.8.83.3:8118"},
                     {"http": "116.8.83.3:8118"},
                     {"http": "113.89.59.161:8118"},
                     {"http": "113.67.183.196:8118"},
                     {"http": "180.155.135.224:31425"},
                     {"http": "123.161.153.238:22593"}]

# Whether use proxy
CONFIG.use_proxy = True

# 'save_json_first' means to retrieve data from Weibo and save as json in 'pages' folder first
# CONFIG.model = 'save_json_first'

# Set CONFIG.model to '' to skip to retrieve data from Weibo
CONFIG.model = ''
