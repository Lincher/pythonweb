__author__ = 'Lincher'

import db
import field
import logging

# 魔术类，元数据类，创造类的类
#>>> Foo = type('Foo', (父类), {'bar':True})


class ModelMetaclass(type):
    #  类成员函数的第一个 都是this指针，当然名字你自己随便起，元类一般用cls
    '''
    __new__ 函数的参数 （this,furture_class_name,,furture_class_parent,furture_class_attribute）
    furture_class_attribute 是类的属性而不是实例属性，现在在 new阶段还没有 init
    '''
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)

        tableName = attrs.get('__table__', None) or name
        logging.info('found model:%s(table:%s)' % (name, tableName))

        mappings = dict()  # 空字典
        fields = []  # 空 list
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, field.Field):
                logging.info('found mapping: %s==>%s' % (k, v))
                mappings[k] = v  # 记录了某一个key是什么字段
                if v.primary_key:  # 一些和主键相关的判断
                    if primaryKey:
                        raise RuntimeError(
                            "Duplicate primary key for field:%s" % k)
                    primaryKey = k
                else:
                    fields.append(k)  # 如果不是主键 就这个键添加到 列表中

        for k in mappings.keys():  # 从属性列表中去掉 字段名到字段类的映射
            attrs.pop(k)

        if not primaryKey:  # meiyou zhujian
            raise RuntimeError("Primary key not found")

        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        '''map是一个高阶函数,用list()返回一个新的list
        '''
        attrs['__mappings__'] = mappings  # 保存属性和列的映射关系
        attrs['__table__'] = tableName  # 类名（表名）
        attrs['__primary_key__'] = primaryKey  # 主键属性名
        attrs['__fields__'] = fields  # 除主键外的属性名
        # 构造默认的SELECT, INSERT, UPDATE和DELETE语句:
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (
            primaryKey, ', '.join(escaped_fields), tableName)  # "x"join()用x来分割对象
        attrs['__select_all__'] = 'select * from `%s`' % tableName
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(
            escaped_fields), primaryKey, db.creat_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ', '.join(
            map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (
            tableName, primaryKey)
        # 其实这个元类的主要功能就是添加属性
        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    # __table__ = 'Model'

    def __init__(self, **kw):
        super().__init__(**kw)
        # super 把 self指针转换到 Model的父类

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            # raise AttributeError(r"'%s' object has no attribute '%s'"%(self.__table__,key))
            # 没事抛你大爷的异常
            self.key = None

    def __setattr__(self, key, value):
        self[key] = value

    def getValueOrDefault(self, key):  # 获取某个字段的值，如果没有就是用默认值
        value = getattr(self, key, None)

        if value is None:
            try:
                field = self.__mappings__[key]
            except KeyError:
                logging.ERROR("'%s' object has no attribute '%s'" %
                              (self.__class__.__name__, key))
                raise

            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s:%s' %
                              (key, str(value)))
                setattr(self, key, value)
        return value

# '''
# 既然@staticmethod和@classmethod都可以直接类名.方法名()来调用，那他们有什么区别呢
# 从它们的使用上来看,
# @staticmethod不需要表示自身对象的self和自身类的cls参数，就跟使用函数一样。
# @classmethod也不需要self参数，但第一个参数需要是表示自身类的cls参数。
# '''
# 使用在类中使用多行注释会引起错误的缩进bug?????????
    @classmethod
    async def find(cls, pk):
        "find object by primary key."
        rs = await db.select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__),
                             [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**[0])

    @classmethod
    async def findAll(cls, orderBy=None, sort='asc'):
        'find all'
        select_str = cls.__select_all__
        if orderBy != None:
            seq = [cls.__select_all__]
            seq.append('order by')
            seq.append(orderBy)
            seq.append(sort)
            select_str=' '.join(seq)

        rows = await db.select(select_str)
        if rows == {}:
            logging.info('found nothing in this table')
        return [cls(**r) for r in rows]  # 返回一个table对象

    @classmethod
    async def findNumber(cls, selectField, where=None, args=None):
        'find number by select and where'
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await db.select(''.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await db.execute(self.__insert__, args)
        if rows != 1:
            logging.warn('faild to insert record: affected rows:%s' % rows)

    async def update(self):
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await db.execute(self.__update__, args)
        if rows != 1:
            logging.warn(
                'failed to update by primary key :affected rows:%s' % rows)

    async def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = await db.execute(self.__delete__, args)
        if rows != 1:
            logging.warn(
                "failed to remove by primary key :affected rows:%s" % rows)
