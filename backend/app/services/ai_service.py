"""
AI识别服务 - 集成通义千问大模型 + 正则兜底
支持识别国内主流网盘分享文本，提取标题、链接、提取码
"""
import json
import re
import logging
from typing import Optional

from openai import OpenAI

from app.config import get_settings
from app.utils.link_parser import parse_links

logger = logging.getLogger(__name__)

settings = get_settings()

# 支持的网盘类型映射
LINK_TYPE_MAP = {
    "quark": "quark",
    "夸克": "quark",
    "夸克网盘": "quark",
    "baidu": "baidu",
    "百度": "baidu",
    "百度网盘": "baidu",
    "alibaba": "alibaba",
    "阿里": "alibaba",
    "阿里云盘": "alibaba",
    "xunlei": "xunlei",
    "迅雷": "xunlei",
    "迅雷云盘": "xunlei",
    "123pan": "123pan",
    "123云盘": "123pan",
    "lanzou": "lanzou",
    "蓝奏": "lanzou",
    "蓝奏云": "lanzou",
}

# AI系统提示词
SYSTEM_PROMPT = """你是一个网盘分享链接识别助手。用户会粘贴网盘分享文本，你需要从中提取以下信息：

1. title: 资源标题（文件名或分享内容名称）
2. link: 网盘链接URL
3. link_type: 网盘类型，只能是以下值之一：quark(夸克网盘)、baidu(百度网盘)、alibaba(阿里云盘)、xunlei(迅雷云盘)、123pan(123云盘)、lanzou(蓝奏云)、other(其他)
4. extraction_code: 提取码（如果没有则为null）

支持的网盘域名：
- pan.quark.cn → quark
- pan.baidu.com → baidu
- aliyundrive.com → alibaba
- pan.xunlei.com → xunlei
- 123pan.com → 123pan
- lanzou*.com → lanzou

请严格以JSON数组格式返回结果，不要添加任何其他文字。
示例输入：
我用夸克网盘给你分享了「142 4K.mp4」，点击链接或复制整段内容，打开「夸克APP」即可获取。
链接：https://pan.quark.cn/s/588be7f1b99c

示例输出：
[{"title": "142 4K.mp4", "link": "https://pan.quark.cn/s/588be7f1b99c", "link_type": "quark", "extraction_code": null}]

如果文本中包含多条分享链接，请全部提取。
如果无法识别出任何有效链接，返回空数组 []。"""


def _get_ai_client() -> Optional[OpenAI]:
    """获取AI客户端（如果配置了API Key）"""
    if not settings.AI_API_KEY:
        return None
    try:
        client = OpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_API_BASE,
        )
        return client
    except Exception as e:
        logger.warning(f"AI客户端初始化失败: {e}")
        return None


def _normalize_link_type(link_type: str) -> str:
    """标准化网盘类型"""
    if not link_type:
        return "other"
    return LINK_TYPE_MAP.get(link_type.lower().strip(), link_type.lower().strip())


def _call_ai_parse(text: str, model: str | None = None) -> list[dict]:
    """调用AI大模型解析分享文本"""
    client = _get_ai_client()
    if not client:
        return []

    use_model = model or settings.AI_MODEL

    try:
        response = client.chat.completions.create(
            model=use_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=0.1,
            max_tokens=2000,
        )
        content = response.choices[0].message.content.strip()

        # 提取JSON（可能被```json包裹）
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if not json_match:
            logger.warning(f"AI返回内容无法解析为JSON: {content[:200]}")
            return []

        results = json.loads(json_match.group())

        # 标准化结果
        normalized = []
        for item in results:
            if not item.get("link"):
                continue
            normalized.append({
                "title": item.get("title", "未识别标题"),
                "link": item["link"],
                "link_type": _normalize_link_type(item.get("link_type", "other")),
                "extraction_code": item.get("extraction_code") or None,
            })
        return normalized

    except json.JSONDecodeError as e:
        logger.error(f"AI返回JSON解析失败: {e}")
        return []
    except Exception as e:
        logger.error(f"AI调用失败: {e}")
        return []


def parse_share_text(text: str, model: str | None = None) -> list[dict]:
    """识别网盘分享文本（AI优先，正则兜底）

    策略：
    1. 如果配置了AI API Key，优先使用AI解析
    2. 如果AI解析失败或未配置，使用正则表达式兜底
    """
    # 尝试AI解析
    ai_results = _call_ai_parse(text, model=model)
    if ai_results:
        logger.info(f"AI解析成功，识别 {len(ai_results)} 条结果")
        return ai_results

    # 正则兜底
    logger.info("AI不可用，使用正则表达式兜底")
    regex_results = parse_links(text)
    if regex_results:
        logger.info(f"正则解析成功，识别 {len(regex_results)} 条结果")
    return regex_results


def batch_parse_share_text(text: str, model: str | None = None) -> dict:
    """批量识别多条分享文本

    支持多种分隔方式：
    - 空行分隔
    - 连续粘贴多条分享文本
    """
    # 先尝试整体交给AI处理（AI能自动识别多条）
    ai_results = _call_ai_parse(text, model=model)
    if ai_results:
        return {
            "success_count": len(ai_results),
            "fail_count": 0,
            "results": ai_results,
        }

    # 正则兜底：按空行分段
    segments = re.split(r'\n\s*\n', text)
    all_results = []
    fail_count = 0

    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue
        parsed = parse_links(segment)
        if parsed:
            all_results.extend(parsed)
        else:
            fail_count += 1

    return {
        "success_count": len(all_results),
        "fail_count": fail_count,
        "results": all_results,
    }


def ai_parse_and_save(text: str, user_id: int, db, model: str | None = None) -> dict:
    """AI识别并直接入库

    Args:
        text: 分享文本
        user_id: 当前管理员ID
        db: 数据库会话
        model: 可选的AI模型

    Returns:
        {"success_count": int, "fail_count": int, "results": list}
    """
    from app.models.resource import Resource

    parsed = parse_share_text(text, model=model)
    success_count = 0
    fail_count = 0
    results = []

    for item in parsed:
        try:
            resource = Resource(
                title=item["title"],
                link=item["link"],
                link_type=item["link_type"],
                extraction_code=item.get("extraction_code"),
                created_by=user_id,
                is_visible=True,
            )
            db.add(resource)
            db.flush()
            success_count += 1
            results.append({
                "id": resource.id,
                "title": resource.title,
                "link": resource.link,
                "link_type": resource.link_type,
            })
        except Exception as e:
            fail_count += 1
            logger.error(f"入库失败: {e}")

    if success_count > 0:
        db.commit()
    else:
        db.rollback()

    return {
        "success_count": success_count,
        "fail_count": fail_count,
        "results": results,
    }
