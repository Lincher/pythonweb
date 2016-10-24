import asyncio, os, inspect, logging, functools

from urllib import parse

from aiohttp import web

from apis import APIError

def get(path):
    '''
    Define decorator @get('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator

def post(path):
    '''
    Define decorator @post('/path')
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator

def get_required_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
    return tuple(args)

def get_named_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
    return tuple(args)

def has_named_kw_args(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True

def has_var_kw_arg(fn):
    params = inspect.signature(fn).parameters
    for name, param in params.items():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True

def has_request_arg(fn):
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False
    for name, param in params.items():
        if name == 'request':
            found = True
            continue
        if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError('request parameter must be the last named parameter in function: %s%s' % (fn.__name__, str(sig)))
    return found

'''
我遇到的第二个难点就是RequestHandler，因为RequestHandler看起来是一个类，但又不是一个类，从本质上来说，它是一个函数，那问题来了，这个函数的作用到底是什么呢？
如果大家有仔细看day2的hello world的例子的话，就会发现在那个index函数里是包含了一个request参数的，但我们新定义的很多函数中，request参数都是可以被省略掉的，那是因为新定义的函数最终都是被RequestHandler处理，自动加上一个request参数，从而符合app.router.add_route第三个参数的要求，所以说RequestHandler起到统一标准化接口的作用。
接口是统一了，但每个函数要求的参数都是不一样的，那又要如何解决呢？得益于factory的理念，我们很容易找一种解决方案，就如同response_factory一样把任何类型的返回值最后都统一封装成一个web.Response对象。RequestHandler也可以把任何参数都变成self._func(**kw)的形式。那问题来了，那kw的参数到底要去哪里去获取呢？
request.match_info的参数： match_info主要是保存像@get('/blog/{id}')里面的id，就是路由路径里的参数
GET的参数： 像例如/?page=2
POST的参数： api的json或者是网页中from
request参数： 有时需要验证用户信息就需要获取request里面的数据
说到这里应该很清楚了吧，RequestHandler的主要作用就是构成标准的app.router.add_route第三个参数，还有就是获取不同的函数的对应的参数，就这两个主要作用。只要你实现了这个作用基本上是随你怎么写都行的，当然最好加上参数验证的功能，否则出错了却找不到出错的消息是一件很头痛的是事情。在这个难点的我没少参考同学的注释，但觉得还是把这部分的代码太过复杂化了，所以我用自己的方式重写了RequestHandler，从老师的先检验再获取转换成先获取再统一验证，从逻辑上应该是没有问题，但大幅度简化了程序。
'''
class RequestHandler(object):

    def __init__(self, app, fn):
        self._app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)

    async def __call__(self, request):#定义了这个方法，对象可以像函数一样调用
        kw = None
        if self._has_var_kw_arg or self._has_named_kw_args or self._required_kw_args:
            if request.method == 'POST':
                if not request.content_type:
                    return web.HTTPBadRequest('Missing Content-Type.')
                ct = request.content_type.lower()
                if ct.startswith('application/json'):
                    params = await request.json()
                    if not isinstance(params, dict):
                        return web.HTTPBadRequest('JSON body must be object.')
                    kw = params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    params = await request.post()
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest('Unsupported Content-Type: %s' % request.content_type)
            if request.method == 'GET':
                qs = request.query_string
                if qs:
                    kw = dict()
                    for k, v in parse.parse_qs(qs, True).items():
                        kw[k] = v[0]
        if kw is None:
            kw = dict(**request.match_info)
        else:
            if not self._has_var_kw_arg and self._named_kw_args:
                # remove all unamed kw:
                copy = dict()
                for name in self._named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            # check named arg:
            for k, v in request.match_info.items():
                if k in kw:
                    logging.warning('Duplicate arg name in named arg and kw args: %s' % k)
                kw[k] = v
        if self._has_request_arg:
            kw['request'] = request
        # check required kw:
        if self._required_kw_args:
            for name in self._required_kw_args:
                if not name in kw:
                    return web.HTTPBadRequest('Missing argument: %s' % name)
        logging.info('call with args: %s' % str(kw))
        try:
            r = await self._func(**kw)
            return r
        except APIError as e:
            return dict(error=e.error, data=e.data, message=e.message)

def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.router.add_static('/static/', path)
    logging.info('add static %s => %s' % ('/static/', path))

def add_route(app, fn):
    method = getattr(fn, '__method__', None)  # 获得 fn的 __method__
    path = getattr(fn, '__route__', None)
    if path is None or method is None: #如果为空
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):#判断函数类型
        fn = asyncio.coroutine(fn) #手动装饰
    logging.info('add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn))#     # app.router.add_route('GET', '/', index)


def add_routes(app, module_name):
    n = module_name.rfind('.')#从后往前 找‘.’
    if n == (-1):#找不到'.'
        mod = __import__(module_name, globals(), locals())# 添加模块 module_name
    else:
        name = module_name[n+1:] # 名字是 aname.bname 点之后的部分
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)# 添加模块 aname.bname
    for attr in dir(mod): #将模块中的所有属性（方法也是属性）按照 list输出
        if attr.startswith('_'): #如果 attr以 _ 开始
            continue # 开始下一次循环(因为这是私有属性)
        fn = getattr(mod, attr)  # 获得 指针（可能是方法也可能是属性）
        if callable(fn):    # 如果 能call
            add_route(app, fn)  #把这个 这个 fn添加到app中