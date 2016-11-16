import logging
import time
from request_decorator import get, post
from models import User,Blog,Comment
from aiohttp import web
'''
import get host以后，这两个方法进去了这个模块的dir 名字空间

协程的本质是函数调用，但是它保存了函数执行的状态（中断），以至于函数能顺序往下执行

'''


@get('/')
def jinja2_handlers(request):
    logging.info('request:%s %s' % (request.method, request.path))

    return web.Response(body=b'<h1>jinja2-Awesome</h1>,content_type="text/html",charset="UTF-8"')

# ValueError, request parameter must be the last named parameter in
# function: test(request, a, *b)


@post('/test')
async def test(a, request):
    logging.info('request:%s %s' % (request.method, request.path))
    users = await models.User.findAll()
    return {
        '__template__': 'test.html',
        'users': users
    }


@get('/')
def index(request):
    summary = ' Lorem ipsum dolor sit amet ,consectetur adipissicing elit,sed do\
    eisusmod tempor incididunt ut labore at dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary,
             created_at=time.time() - 120),
        Blog(id='2', name='Something New',
             summary=summary, created_at=time.time()-3600),
        Blog(id='3', name='Learn Swift', summary=summary,
             creat_at=time.time() - 7200)

    ]
    return{
        '__template__': "blogs.html",
        'blogs': blogs
    }

'''
__file__ 代表的是当前文本，用getattr获得的是 字符串对象
'''
mod = __import__(__name__, globals(), locals())  # 获得本模块
__all__ = []
for k in dir():
    if not k.startswith('_'):
        fn = getattr(mod, k)
        if hasattr(fn, '__method__') and hasattr(fn, '__route__'):
            __all__.append(k)
