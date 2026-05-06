import re
from typing import Optional

LINK_PATTERNS = {
    "quark": r"https?://pan\.quark\.cn/s/[a-zA-Z0-9]+",
    "baidu": r"https?://pan\.baidu\.com/s/[a-zA-Z0-9_\-]+",
    "alibaba": r"https?://[a-zA-Z0-9.\-]*aliyundrive\.com/s/[a-zA-Z0-9]+",
    "xunlei": r"https?://pan\.xunlei\.com/s/[a-zA-Z0-9]+",
    "123pan": r"https?://www\.123pan\.com/s/[a-zA-Z0-9]+",
    "lanzou": r"https?://[a-zA-Z0-9.\-]*lanzou[a-zA-Z]*\.com/[a-zA-Z0-9]+",
}

EXTRACTION_CODE_PATTERNS = [
    r"提取码[：:]\s*([a-zA-Z0-9]{4})",
    r"密码[：:]\s*([a-zA-Z0-9]{4})",
    r"code[：:]\s*([a-zA-Z0-9]{4})",
]


def parse_links(text: str) -> list[dict]:
    results = []
    for link_type, pattern in LINK_PATTERNS.items():
        matches = re.findall(pattern, text)
        for link in matches:
            extraction_code = None
            for code_pattern in EXTRACTION_CODE_PATTERNS:
                code_match = re.search(code_pattern, text)
                if code_match:
                    extraction_code = code_match.group(1)
                    break
            title = extract_title(text, link)
            results.append({
                "title": title,
                "link": link,
                "link_type": link_type,
                "extraction_code": extraction_code,
            })
    return results


def extract_title(text: str, link: str) -> str:
    # 尝试从「」中提取标题
    match = re.search(r"[「『](.+?)[」』]", text)
    if match:
        return match.group(1)
    # 尝试从标题行提取
    match = re.search(r"分享[了给].*?「(.+?)」", text)
    if match:
        return match.group(1)
    return "未识别标题"
