import lim
from lim.request_decorator import get,post

@get('/')
def jinja2_handlers(request):
    return web.Response(body=b'<h1>jinja2-Awesome</h1>')


print(jinja2_handlers.__name__)