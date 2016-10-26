import functools

def __request(path,*,method):
    '''
    define decorator request(get post)
    '''
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*a,**k):
            return func(*a,**k)
        wrapper.__method__ = method
        wrapper.__route__ = path
        return wrapper
    return decorator


# get = functools.partial(__request,method = 'GET')
# post = functools.partial(__request,method = 'POST')

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