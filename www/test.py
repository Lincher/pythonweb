import models,db
def test():
    yield from db.creat_pool(user='www-data',password='www-data',
    database='awesome')

    u = User(name='Test',email='test@example.com',
    passwd='1234567890',image='about:blank')

    yield from u.save()


test()
