from request_decorator import get,post
from aiohttp import web
'''
import get host以后，这两个方法进去了这个模块的dir 名字空间
'''
@get('/')
def jinja2_handlers(request):
    return web.Response(body=b'<h1>jinja2-Awesome</h1>,content_type="text/html",charset="UTF-8"')

@post('/')
def test(request,a,*b):
    return 'hahah'

__all__ = {'jinja2_handlers'}
# # unit test
# print(jinja2_handlers.__name__)