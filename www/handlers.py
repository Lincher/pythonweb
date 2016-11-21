import logging
import time
from request_decorator import get, post
from models import User, Blog, Comment
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
             summary=summary, created_at=time.time() - 3600),
        Blog(id='3', name='Learn Swift', summary=summary,
             creat_at=time.time() - 7200)

    ]
    return{
        '__template__': "blogs.html",
        'blogs': blogs
    }

# @get('/api/users')
# async def api_get_users():
#     users =await User.findAll(orderBy='created_at',sort='desc')
#     for u in users:
#         u.passwd = '*******'
#     return dict(users=users)
_RE_EMAIL = re.compile(
    r'^[a-z0-9\.\-\_]+\@[a-z0-9\-\_]+(\.[a-z0-9\-\_]+){1,4}$')
_RE_SHA1 = re.compile(r'^[0-9a-f]{40}$')


@post('/api/users')
async def api_register_user(*, email, name, passwd):
    if not name or not name.strip():
        raise APIValueError('name')
    if not email or not _RE_EMAIL.match(email):
        raise APIValueError('email')
    if not passwd or not _RE_SHA1.match(passwd):
        raise APIValueError('passwd')
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, passwd)
    user = User(id=uid, name=name.strip(), email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % hashlib.md5(email.encode('utf-8')).hexdigest())
    await user.save()
    # make session cookie:
    r = web.Response()
    r.set_cookie(COOKIE_NAME,user2cookie(user,86400),max_age=86400,httpponly=True)
    user.passwd='*****'
    r.content_type='application/json'
    r.body =json.dumps(user,ensure_ascii=False).encode('utf-8')
    return r


@get('/api/users')
async def api_get_users(*, page='1'):  # 命名关键字参数
    page_index = get_page_index(page)
    num = await User.findNumber('count(id)')
    p = Page(num, page_index)
    if num == 0:
        return dict(page=p, users=())
    users = await User.findAll(orderBy='created_at desc', limit=(p.offset, p.limit))
    for u in users:
        u.passwd = '*******'
    return dict(page=p, users=users)


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
