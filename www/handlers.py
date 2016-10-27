from request_decorator import get,post

'''
import get host以后，这两个方法进去了这个模块的dir 名字空间
'''
@get('/')
def jinja2_handlers(request):
    return b'<h1>jinja2-Awesome</h1>'

__all__ = {'jinja2_handlers'}
# # unit test
# print(jinja2_handlers.__name__)