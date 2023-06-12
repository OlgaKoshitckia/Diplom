import sqlalchemy as sq
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import psycopg2
from config import PSD, DSN


def create_db():
    """Создание БД"""
    conn = psycopg2.connect(database='postgres', user='postgres', password=PSD)
    conn.set_session(autocommit=True)
    cur = conn.cursor()
    try:
        cur.execute("""CREATE DATABASE vkinder_db;""")
    except Exception:
        conn.rollback()
        conn.close()

class Base(DeclarativeBase): 
    """Наследуемся от базового класса"""
    pass

class Viewed(Base):
    """Создаем отношение просмотренных анкет"""
    __tablename__ = 'viewed'
    profile_id = sq.Column(sq.Integer, primary_key=True)
    worksheet_id = sq.Column(sq.Integer, primary_key=True)

class VkEngine:
    def __init__(self):
        self._engine = sq.create_engine(DSN)
        Session = sessionmaker(bind=self._engine)
        self._session = Session()
        Base.metadata.create_all(bind=self._engine)
    
    def add_view(self, profile_id, worksheet_id):
        """Добавляем анкеты в просмотренные"""
        self._session.add(Viewed(profile_id=profile_id, worksheet_id=worksheet_id))
        self._session.commit()

    def search_id(self, profile_id, worksheet_id):
        """Проверяет есть ли такие данные в БД"""
        return bool(self._session.query(Viewed).filter(Viewed.profile_id==profile_id, 
                                                Viewed.worksheet_id == worksheet_id).first())


if __name__ == '__main__':
    db = VkEngine()
    db.add_view(1, 1)
    db.add_view(1, 2)
    print(db.search_id(2, 1))
    print(db.search_id(1, 1))
