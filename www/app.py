'''
async web application
'''
import asyncio
import inspect
import json
import logging
import os
import sys
import time
import jinja2
import config
import db
# sys.path.append(os.path.dirname(os.path.realpath(__file__))+'\..\\lim')
import std
import lim
import orm

from datetime import datetime
from functools import partial
from aiohttp import web
from handlers import user2cookie, COOKIE_NAME
'''
Jinja2 is a template engine written in pure Python.  It provides a
    Django inspired non-XML syntax but supports inline expressions and
    an optional sandboxed environment.
'''
# from jinja2 import Environment.FileSystemLoader

# print(os.path.dirname(os.path.realpath(__file__))+'\..\\')  #当前文件所在的目录

# from db import db.aiomysql
# 可以通过导的包访问 导的包导入的包，但是bu'
# from .import . 代表的是 __init__.py所在文件夹


def init_jinja2(app, **kw):
    logging.info('init jinja2...')

    def dict_inital(d):
        for key in d.keys():
            d[key] = kw.get(key, d[key])

    options = dict(
        autoescape=True,
        block_start_string='{%',
        block_end_string='%}',
        variable_start_string='{{',
        variable_end_string='}}',
        auto_reload=True
    )
    dict_inital(options)

    path = kw.get('path', None)
    if path is None:
        # 如果url路径为空，把路径改为templataes 目录
        '''
            os.path.abspath(__file__) 获得当前的绝对路径
            os.path.dirname 获得当前文件的文件夹
            os.path.join 路径拼接
        '''
        path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), 'templates')
    logging.info('set jinja2 templates path:%s' % path)
    # 这个环境对象很关键
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    # app 类属性
    app['__templating__'] = env
'''
# middleware 回调函数 参数(服务器端的web对象，请求处理函数)
'''


@asyncio.coroutine
def logger_factory(app, handler):
    @asyncio.coroutine
    def logger(request):
        logging.info('request:%s %s' % (request.method, request.path))
        logging.info('handler: %s' % (handler.__name__))
        return (yield from handler(request))
    return logger

async def data_factory(app, handler):
    async def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = await request.json()
                logging.info('requset json:%s' % str(requset.__data__))
            elif request.content_type.startswith('application/x-www-from-urlencoded'):
                request.__data__ = await request.post()
                logging.info('request frion : %s' % str(request.__data__))
        return (await handler(request))
    return parse_data


@asyncio.coroutine
def response_factory(app, handler):
    @asyncio.coroutine
    def response(request):
        r = yield from handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-steam'
            return resp
        if isinstance(r, str):
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html:charset=utf-8'
            return resp
        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(body=json.dumps(
                    r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                resp = web.Response(body=app['__templating__'].get_template(
                    template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(r, int) and r >= 100 and r < 600:
            return web.Response(r)
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and t >= 100 and t < 600:
                return web.Response(t, str(m))
        # default:
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp
    return response


async def auth_factory(app, handler):
    async def auth(request):
        logging.info('check user: %s %s' % (request.method, request.path))
        request.__user__ = None
        cookie_str = request.cookies.get(COOKIE_NAME)
        if cookie_str:
            user = await cookie2user(cookie_str)
            if user:
                logging.info('set current user: %s' % user.email)
                request.__user__ = user
        return (await handler(request))
    return auth

async def cookie2user(cookie_str):
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = await User.find(uid)
        if user is None:
            return None
        s = "%s-%s-%s-%s" % (uid, user.passwd, expires, __COOKIE_KEY)
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None


def datatime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


@asyncio.coroutine
def init(loop):
    yield from db.creat_pool(loop=loop, **config.config_default.configs['db'])

    # 获取数据库连接池
    # 获取web应用对象,中间件用来绑定请求和请求处理
    app = web.Application(loop=loop, middlewares=[
                          logger_factory, response_factory, data_factory, auth_factory])
    init_jinja2(app, filters=dict(datetime=datatime_filter))
    # app.router.add_route('GET', '/', index)
    # help(app.router.add_route)
    lim.coroweb.add_routes(app, 'handlers')
    lim.coroweb.add_static(app)
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
# 回调函数调用了对象
loop.run_forever()
