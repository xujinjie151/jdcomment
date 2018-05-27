import datetime
from sqlalchemy import Column, Integer, String, TEXT, Date, Float
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# import io
# import sys
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8')

# 数据库的配置变量
HOSTNAME = '127.0.0.1'
PORT = '3306'
DATABASE = 'tushu'
USERNAME = 'root'
PASSWORD = '123456'
DB_URI = 'mysql+mysqldb://{}:{}@{}:{}/{}?charset=utf8'.format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)

engine = create_engine(DB_URI, echo=True)
sessionDb1 = sessionmaker(bind=engine)
sessionDb = sessionDb1()
from datetime import datetime,timezone,timedelta
# 所有的类都要继承自`declarative_base`这个函数生成的基类
Base = declarative_base(engine)


# name, title, product_id, itemurl, reallyPrice, originalPrice, url, commentcount, desc

class ma_myitems1(Base):
    __tablename__ = 'ma_myitems1'

    id = Column(Integer, primary_key=True)
    shopname = Column(TEXT(), nullable=True)
    title = Column(TEXT(), nullable=True)
    product_id = Column(String(length=100), unique=True)
    itemurl = Column(TEXT(), nullable=True)
    reallyPrice = Column(Float(), nullable=True)
    originalPrice = Column(Float(), nullable=True)
    url = Column(TEXT(), nullable=True)
    commentcount = Column(Integer(), nullable=True)
    desc2 = Column(TEXT(), nullable=True)
    shop_id = Column(TEXT(), nullable=True)
    categorie = Column(TEXT(), nullable=True)
    # mark = Column(Integer(),default=0)




class ma_comment(Base):
    __tablename__ = 'ma_comment'
    id = Column(Integer, primary_key=True)
    product_id = Column(String(length=100))
    content = Column(TEXT())
    score = Column(Integer())

def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == '__main__':
    Base.metadata.create_all()
    # ed_user = User(no='123',password='123')
    # sessionDb.add(ed_user)
    # sessionDb.commit()
