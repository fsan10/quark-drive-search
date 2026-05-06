import io
import csv
from sqlalchemy.orm import Session
from app.models.resource import Resource
from app.schemas.resource import ResourceCreate


def import_csv(db: Session, file_content: bytes, user_id: int) -> dict:
    """从CSV文件导入资源

    CSV格式要求（表头）：
    title,link,link_type,extraction_code,description,file_size
    """
    try:
        text = file_content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = file_content.decode("gbk")

    reader = csv.DictReader(io.StringIO(text))

    success_count = 0
    fail_count = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):
        try:
            if not row.get("title") or not row.get("link"):
                errors.append(f"第{row_num}行: 标题和链接不能为空")
                fail_count += 1
                continue

            resource = Resource(
                title=row["title"].strip(),
                link=row["link"].strip(),
                link_type=row.get("link_type", "other").strip(),
                extraction_code=row.get("extraction_code", "").strip() or None,
                description=row.get("description", "").strip() or None,
                file_size=row.get("file_size", "").strip() or None,
                created_by=user_id,
                is_visible=True,
            )
            db.add(resource)
            success_count += 1
        except Exception as e:
            errors.append(f"第{row_num}行: {str(e)}")
            fail_count += 1

    if success_count > 0:
        db.commit()

    return {
        "success_count": success_count,
        "fail_count": fail_count,
        "errors": errors[:20],  # 最多返回20条错误
    }
