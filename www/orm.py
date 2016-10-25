__author__ ='Lincher'

import db,field,logging

#魔术类，元数据类，创造类的类
#>>> Foo = type('Foo', (父类), {'bar':True})
class ModelMetaclass(type):
    #  类成员函数的第一个 都是this指针，当然名字你自己随便起，元类一般用cls
    '''
    __new__ 函数的参数 （this,furture_class_name,,furture_class_parent,furture_class_attribute）
    '''
    def __new__(cls,name,bases,attrs):
        if name=='Model':
            return type.__new__(cls, name, bases, attrs)

        tableName = attrs.get('__table__',None) or name
        logging.info('found model:%s(table:%s)'%(name,tableName))

        mappings = dict()#空字典
        fields= [] #空 list
        primaryKey = None
        for k,v in attrs.items():
            if isinstance(v,field.Field):
                logging.info('found mapping: %s==>%s'%(k,v))
                mappings[k]=v  #记录了某一个key是什么字段
                if v.primary_key: #一些和主键相关的判断
                    if primaryKey:
                        raise RuntimeError("Duplicate primary key for field:%s"%k)
                    primaryKey =k #
                else:
                    fields.append(k) #如果不是主键 就这个键添加到 列表中
        
        if not primaryKey:#meiyou zhujian 
            raise RuntimeError("Primary key not found")

        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        '''map是一个高阶函数,用list()返回一个新的list
        '''
        attrs['__mappings__'] = mappings # 保存属性和列的映射关系
        attrs['__table__'] = tableName  #类名（表名）
        attrs['__primary_key__'] = primaryKey # 主键属性名
        attrs['__fields__'] = fields # 除主键外的属性名
        # 构造默认的SELECT, INSERT, UPDATE和DELETE语句:
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primaryKey, ', '.join(escaped_fields), tableName)#  "x"join()用x来分割对象
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields), primaryKey, db.creat_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName, ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)), primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (tableName, primaryKey)
        # 其实这个元类的主要功能就是添加属性
        return type.__new__(cls, name, bases, attrs)  



class Model(dict,metaclass=ModelMetaclass):
    # __table__ = 'Model'

    def __init__(self,**kw):
        super().__init__(**kw)
        # super 把 self指针转换到 Model的父类 
    
    def __getattr__(self,key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'%s' object has no attribute '%s'"%(self.__table__,key))
    
    def __setattr__(self,key,value):
        self[key] = value
    
    def getValue(self,key):
        return getattr(self,key,None)

    def getValueOrDefault(self,key): #获取某个字段的值，如果没有就是用默认值
        value = getattr(self,key,None) #相当于 self.__getattr__()
        
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s:%s'% (key,str(value)))
                setattr(self,key,value)
        return value

    @classmethod
    async def find(cls,pk):
        "find object by primary key."
        rs = await select('%s where `%s`=?'%(cls.__select__,cls.__primary_key__),
        [pk],1)
        if len(rs) == 0:
            return None
        return cls(**[0])

    async def save(self):
        args = list(map(self.getValueOrDefault,self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await db.execute(self.__insert__,args)
        if rows != 1:
            logging.warn('faild to insert record: affected rows:%s'%rows)

    async def update(self):
        args = list(map(self.getValue,self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await db.execute(self.__update__,args)
        if rows !=1:
            logging.warn('failed to update by primary key :affected rows:%s'%rows)

    async def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = await db.execute(self.__delete__,args)
        if rows!=1:
            logging.warn("failed to remove by primary key :affected rows:%s"%rows)

    @classmethod
    async def findAll(parameter_list):
        pass

        







  