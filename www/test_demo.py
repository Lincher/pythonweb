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