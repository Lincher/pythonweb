'''
async web application
'''

import logging; 
logging.basicConfig(level=logging.INFO)
import functools.partial
from datetime import datetime

import asyncio, os, json, time,inspect
from aiohttp import web
from jinja2 import Environment.FileSystemLoader

import orm
from coroweb import add_route,add_static

def init_jinja2(app,**kw):
    logging.info('init jinja2...')

    def dict_inital(d):
        for key in d.keys():
            d[key] = kw.get(key,d[key])

    options = dict(
        autoescape = True,
        block_start_string = '{%',
        block_end_string = '%}',
        variable_start_string = '{{',
        variable_end_string = '}}',
        auto_reload = True
    )
    dict_inital(options)
    
    path =kw.get('path',None)
    if path is None:
        path =os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates')
    logging.info('set jinja2 templates path:%s' %path)
    env = Environment(loader=FileSystemLoader(path),**options)
    filters = ke.get('filters',None)
    if filters is not  None:
        for name ,f  in filters.items():
            env.filters[name] = f
    app['__templating__'] = env
    
    
def __request(path,*,method):
    '''
    define decorator request(get post)
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*a,*k):
            return func(*a,**k)
        wrapper.__method__ = method
        wrapper.__route__ = path
        return wrapper
    return decorator

get = functools.partial(__request,method = 'GET')
post = functools.partial(__request,method = 'POST')

class RequestHandler(object):

    def __init__(self,app,fn):
        self._app =app
        self._func=fn

    @asyncio.coroutine
    def __call__(self,request): #定义了这个方法，对象可以像函数一样调用
        kw = ...abs
        r = yield from self._func(**kw)
        return r

@asyncio.coroutine
def logger_factory(app,handler):
    @asyncio.coroutine
    def logger(request):
        #jilu zizhi
        logging.info('request:%s %s'%(request.method,request.path))

        return (yield from handler(request))
    return logger

async def data_factory(app,handler):
    async def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = await request.json()
                logging.info('requset json:%s'% str(requset.__data__))
            elif request.content_type.startswith('application/x-www-from-urlencoded'):
@asyncio.coroutine
def response_factory(app,handler):
    @asyncio.coroutine
    def response(request):
        r = yield from handler(request)
        if isinstance(r,web.StreamResponse):
            return r 
        if isinstance(r,bytes):
            resp = web.Response(body=r)
            resp.content_type ='application/octet-steam'
            return resp
        if isinstance(r.str):
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html:charset=utf-8'
            return resp
        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
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

def index(request):
    return web.Response(body=b'<h1>Awesome</h1>')

@asyncio.coroutine
def init(loop):
    app = web.Application(loop=loop,middlewares=[logger_factory,responser_factory])
    init_jinja2(app,filters=dict(datetime=datetime_filter))
    # app.router.add_route('GET', '/', index)
    add_routes(app,'handlers')
    add_static(app)
    srv = yield from loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()