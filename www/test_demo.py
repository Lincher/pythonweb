d = {'a':1,'b':2}

def change(d):
    for k in d.keys():
        d[k] = 3

change(d)
print(str(d))

module_name = 'aname.bbname'

n  =  module_name.rfind('a')
name = module_name[n+1:]
print(name)

class a(object):

    def fuck():
        pass

    __demo__ = None

print(dir(a))


class B(dict):

    a = "这是类属性"
    def __init__(self,a):
        self.a = a
    def __getattr__(self,key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"object has no attribute")

b = B('这是实例属性')
print(B.a)
print(b.a)