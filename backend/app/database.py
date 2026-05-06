from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 🔥 直接写死数据库地址（彻底绕过中文路径/编码错误！）
# 连接你本地Docker的PostgreSQL，和你的docker-compose完全一致
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/clouddrive"

# 固定空字典，永不出错
connect_args = {}

# 创建引擎（无任何编码风险）
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()