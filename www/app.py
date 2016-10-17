import logging;logging.basicConfig(level=logging.INFO)

import asyncio,os,json,time
from datetime import datetime

from aiohttp import web

def index(request):
    return web.Response(body=b"<h1>Awesome</h1>")
    # 返回网站的响应

# 这是一个协程
@asyncio.coroutine
def init(loop1): #参数是一个消息循环
    app =web.Application(loop=loop1) 
    # 得到一个网站应用对象
    app.router.add_route("GET","/",index)
    #初始化对象，增加请求和响应
    srv = yield from loop1.create_server(app.make_handler(),"127.0.0.1",9000)
    # 等待创建服务器的协程
    logging.info("server started at http://127.0.0.1:9000...")
    return srv

def a():#s
    pass
    
loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()