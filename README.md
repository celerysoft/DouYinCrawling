# 抖音爬虫

## 特性

 * 根据个人主页的URL，得到该用户所有的无水印视频链接并下载到本地
 
## 项目初始化

### 设置虚拟环境

#### VirtualEnv

```
pip install virtualenv
virtualenv -p python3 --no-site-packages /path/to/new/virtual/environment 
```
	
#### venv

```
python3 -m venv /path/to/new/virtual/environment
```

### 安装依赖

```
pip install -r requirements.txt
```

## 运行

```
python app.py
或者包含抖音用户个人主页的链接地址
python app.py https://v.douyin.com/J1tgwoB/
```

第一次运行的时候，可能需要下载**chromium**，文件较大，需耐心等待

    