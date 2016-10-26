try:
    import coroweb  # Will also be exported.
except SystemError:
    from . import coroweb

__all__ = {'coroweb'}


'''
包里面的引用如果需要暴露给外部，必须用 . 的格式，这样别人引用的时候才能找得到具体某个模块的路径
因为导第三方的包，包必须在搜索路径下，
如果导自己写的又不在工程目录下的包，必须将这个目录导入到搜索路径中
但是如果包里面有包，不可能把所有的路径都写进去，
所以在自己写的库中 import 自己写的子模块时一定要显式的指明相对路径
''' 