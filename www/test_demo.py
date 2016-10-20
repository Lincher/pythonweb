d = {'a':1,'b':2}

def change(d):
    for k in d.keys():
        d[k] = 3

change(d)
print(str(d))