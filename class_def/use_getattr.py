#-*- coding: utf-8 -*-

class Chain(object):
    def __init__(self, path=''):
        self._path = path
        self.name = 'Chain'

    def __getattr__(self, path):
        ''' Python在调用类实例的属性时，如果类没有该属性，则
        默认调用__getattr__() '''
        print(path)
        return Chain('%s/%s' % (self._path, path))

    def __str__(self):
        return self._path

    __repr__ = __str__

print(Chain().status.user.timeline)
print(Chain('test').name)
