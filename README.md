## 微博备份脚本


### Prerequisites

**Python 3.6**

### Installing

1. Clone this repository

    ```bash
    cd /path/to/anywhere/you/like
    git clone https://github.com/zengyu714/weibo-backup
    ```
    Now the directory looks like
    
    ```bash
    .
    ├── README.md
    ├── configuration.py
    ├── main.py
    ├── requirements.txt
    ├── demo  [directory]
    └── pages [directory]
        └── README.md
    └── articles [directory]
    └── comments [directory]
 
    ```
    
2. Install dependencies

    ```python
    pip install -r requirements.txt
    ```

### Running
1. 修改配置文件`configuration.py`
    + `CONFIG.url_template`
        1. 登录微博[触屏版](https://m.weibo.cn/)
            ![image](demo/get_url.jpg)
            得到**URL**, E.g, [https://m.weibo.cn/u/2146965345](https://m.weibo.cn/u/2146965345)
        2. 点击进入，打开浏览器调试工具
        ![image](demo/inspect_1.jpg)
        ![image](demo/inspect_2.jpg)
        3. 将复制得到的`Request URL`粘贴到
        `CONFIG.url_template = `'**your_url**'
        E.g.,  
        `CONFIG.url_template = 'https://m.weibo.cn/api/container/getIndex?type=uid&value=2146965345&containerid=1076032146965345'`
    + `CONFIG.cookie` 
        1. 同样是在调试界面，在`Headers`栏往下翻到`Cookie` 
        ![image](demo/cookie.jpg)
        2. 右键复制内容（目的是发送登录状态）
        3. 将复制得到的`Cookie`粘贴到
        `CONFIG.cookie = `'**your_cookie**'
        
1. 注意看`configuration.py`中的参数配置，适时调整参数
+ 一般的，首次使用时，应将CONFIG.model改为'save_json_first'
+ 从微博获取的数据会以json格式保存在pages文件夹中，所以之后应将CONFIG.model设置为空即''
+ 如不想使用代理，将CONFIG.use_proxy设置为False
1. 运行`main.py`脚本
    ```python
        python main.py
    ```

**Note**
+ 自动生成`pages`文件夹保存微博json文件
+ 自动生成`articles`文件夹保存原创或转载文章json文件
+ 自动生成`comments`文件夹保存微博评论json文件
+ 自动生成**结果文件**`mblog_backup_<current_date>.html`,可以在浏览器打开并打印成PDF

### TODO
- [x] 对于长文(>140)，评论，点赞详情没有记录
- [x] 优化备份页面排版
- [X] 保存转载的微博
- [X] 保存原创或转载长文
- [ ] 备份页面html从单行分成多行
- [x] 保存评论
- [ ] 点赞

### What can this tool do?
- 保存基本信息
- 保存所有原创微博内容
- 保存所有转载微博内容
- 保存所有评论
- 保存原创或转载长文
- 保存微博附加的图片

### License
This project is licensed under the MIT License

### Reference
[https://www.zhihu.com/question/20339936](https://www.zhihu.com/question/20339936)
