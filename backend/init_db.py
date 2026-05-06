"""数据库初始化脚本 - 创建初始管理员和默认分类"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import text, inspect
from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.category import Category
from app.utils.security import hash_password
from app.config import get_settings


def migrate_db():
    """检测并添加已有表中缺失的列"""
    migrations = [
        {
            "table": "users",
            "column": "wish_last_read_at",
            "type": "TIMESTAMP WITHOUT TIME ZONE",
            "nullable": True,
        },
    ]

    insp = inspect(engine)
    with engine.connect() as conn:
        for m in migrations:
            existing_columns = [col["name"] for col in insp.get_columns(m["table"])]
            if m["column"] not in existing_columns:
                sql = f'ALTER TABLE {m["table"]} ADD COLUMN {m["column"]} {m["type"]}'
                conn.execute(text(sql))
                conn.commit()
                print(f"已添加列: {m['table']}.{m['column']}")
            else:
                print(f"列已存在: {m['table']}.{m['column']}")


def init_db():
    """初始化数据库：创建表、迁移列、创建管理员、创建默认分类"""
    print("正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("数据库表创建完成")

    print("正在检查数据库迁移...")
    migrate_db()

    db = SessionLocal()
    try:
        # 创建初始管理员
        settings = get_settings()
        admin = db.query(User).filter(User.username == settings.ADMIN_USERNAME).first()
        if not admin:
            admin = User(
                username=settings.ADMIN_USERNAME,
                email="admin@example.com",
                hashed_password=hash_password(settings.ADMIN_PASSWORD),
                role="super_admin",
                is_active=True,
            )
            db.add(admin)
            print(f"已创建超级管理员账号: {settings.ADMIN_USERNAME} / {settings.ADMIN_PASSWORD}")
        else:
            if admin.role != "super_admin":
                admin.role = "super_admin"
                print(f"已升级管理员为超级管理员: {settings.ADMIN_USERNAME}")
            else:
                print(f"超级管理员账号已存在: {settings.ADMIN_USERNAME}")

        # 创建默认分类
        default_categories = [
            {"name": "视频", "description": "电影、电视剧、动漫等视频资源", "sort_order": 1},
            {"name": "音乐", "description": "音乐专辑、单曲等音频资源", "sort_order": 2},
            {"name": "软件", "description": "应用程序、工具软件等", "sort_order": 3},
            {"name": "游戏", "description": "游戏资源、模拟器等", "sort_order": 4},
            {"name": "文档", "description": "电子书、教程、文档等", "sort_order": 5},
            {"name": "图片", "description": "图片、壁纸、素材等", "sort_order": 6},
            {"name": "其他", "description": "其他类型资源", "sort_order": 99},
        ]

        for cat_data in default_categories:
            existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if not existing:
                category = Category(**cat_data, created_by=admin.id)
                db.add(category)
                print(f"已创建分类: {cat_data['name']}")
            else:
                print(f"分类已存在: {cat_data['name']}")

        db.commit()
        print("\n数据库初始化完成！")

    except Exception as e:
        db.rollback()
        print(f"初始化失败: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
