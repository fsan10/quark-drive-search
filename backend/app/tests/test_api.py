"""
API接口自动化测试脚本
使用SQLite内存数据库测试所有核心API
"""
import sys
import os
import time
import subprocess
import requests

# 确保可以导入app模块
BACKEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, BACKEND_DIR)

BASE_URL = "http://localhost:9001"
RESULTS = {"passed": 0, "failed": 0, "tests": []}
TOKEN = None


def log_test(name, passed, detail=""):
    status = "PASS" if passed else "FAIL"
    RESULTS["tests"].append({"name": name, "status": status, "detail": detail})
    RESULTS["passed" if passed else "failed"] += 1
    symbol = "✓" if passed else "✗"
    print(f"  {symbol} {name}" + (f" — {detail}" if detail else ""))


def auth_headers():
    return {"Authorization": f"Bearer {TOKEN}"}


def test_health():
    r = requests.get(f"{BASE_URL}/health")
    log_test("GET /health", r.status_code == 200 and r.json()["status"] == "healthy")


def test_root():
    r = requests.get(f"{BASE_URL}/")
    log_test("GET /", r.status_code == 200)


def test_auth():
    global TOKEN
    # 登录
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"username": "admin", "password": "admin123"})
    log_test("POST /api/auth/login (正确凭据)", r.status_code == 200 and "access_token" in r.json())
    TOKEN = r.json().get("access_token")

    # 错误密码
    r = requests.post(f"{BASE_URL}/api/auth/login", json={"username": "admin", "password": "wrong"})
    log_test("POST /api/auth/login (错误凭据)", r.status_code == 401)

    # 获取当前用户
    r = requests.get(f"{BASE_URL}/api/auth/me", headers=auth_headers())
    log_test("GET /api/auth/me", r.status_code == 200 and r.json()["role"] == "admin")

    # 无Token
    r = requests.get(f"{BASE_URL}/api/auth/me")
    log_test("GET /api/auth/me (无Token)", r.status_code == 403)

    # 注册
    r = requests.post(f"{BASE_URL}/api/auth/register", json={
        "username": "testuser", "email": "test@example.com", "password": "test123"
    }, headers=auth_headers())
    log_test("POST /api/auth/register", r.status_code == 200)

    # 重复注册
    r = requests.post(f"{BASE_URL}/api/auth/register", json={
        "username": "testuser", "email": "test2@example.com", "password": "test123"
    }, headers=auth_headers())
    log_test("POST /api/auth/register (重复)", r.status_code == 400)


def test_categories():
    # 创建
    r = requests.post(f"{BASE_URL}/api/admin/categories", json={
        "name": "视频", "description": "视频资源", "sort_order": 1
    }, headers=auth_headers())
    log_test("POST /api/admin/categories", r.status_code == 201)
    cat_id = r.json()["id"]

    # 列表
    r = requests.get(f"{BASE_URL}/api/admin/categories", headers=auth_headers())
    log_test("GET /api/admin/categories", r.status_code == 200 and len(r.json()) > 0)

    # 更新
    r = requests.put(f"{BASE_URL}/api/admin/categories/{cat_id}", json={"description": "更新描述"},
                     headers=auth_headers())
    log_test("PUT /api/admin/categories/{id}", r.status_code == 200)

    # 前台分类
    r = requests.get(f"{BASE_URL}/api/search/categories")
    log_test("GET /api/search/categories", r.status_code == 200)

    return cat_id


def test_resources(cat_id):
    # 创建
    r = requests.post(f"{BASE_URL}/api/admin/resources", json={
        "title": "测试视频 4K.mp4",
        "link": "https://pan.quark.cn/s/test123abc",
        "link_type": "quark",
        "extraction_code": "ab12",
        "category_id": cat_id,
        "is_visible": True,
    }, headers=auth_headers())
    log_test("POST /api/admin/resources", r.status_code == 201)
    res_id = r.json()["id"]

    # 列表
    r = requests.get(f"{BASE_URL}/api/admin/resources", headers=auth_headers())
    log_test("GET /api/admin/resources", r.status_code == 200 and r.json()["total"] >= 1)

    # 更新
    r = requests.put(f"{BASE_URL}/api/admin/resources/{res_id}", json={"title": "更新标题"},
                     headers=auth_headers())
    log_test("PUT /api/admin/resources/{id}", r.status_code == 200)

    # 批量创建
    r = requests.post(f"{BASE_URL}/api/admin/resources/batch", json={
        "resources": [
            {"title": "批量1", "link": "https://pan.baidu.com/s/b1", "link_type": "baidu"},
            {"title": "批量2", "link": "https://www.aliyundrive.com/s/a1", "link_type": "alibaba"},
        ]
    }, headers=auth_headers())
    log_test("POST /api/admin/resources/batch", r.status_code == 201 and r.json()["success_count"] == 2)

    return res_id


def test_search():
    r = requests.get(f"{BASE_URL}/api/search", params={"keyword": "测试"})
    log_test("GET /api/search (关键词)", r.status_code == 200)

    r = requests.get(f"{BASE_URL}/api/search", params={"keyword": "测试", "link_type": "quark"})
    log_test("GET /api/search (类型筛选)", r.status_code == 200)

    r = requests.get(f"{BASE_URL}/api/search/hot")
    log_test("GET /api/search/hot", r.status_code == 200)


def test_csv_import():
    csv_content = "title,link,link_type,extraction_code,description,file_size\n"
    csv_content += "CSV测试1,https://pan.quark.cn/s/csv1,quark,,描述1,1GB\n"
    csv_content += "CSV测试2,https://pan.baidu.com/s/csv2,baidu,c2,描述2,2GB\n"
    r = requests.post(f"{BASE_URL}/api/admin/resources/import/csv",
                      files={"file": ("test.csv", csv_content.encode("utf-8"), "text/csv")},
                      headers=auth_headers())
    log_test("POST /api/import/csv", r.status_code == 200 and r.json()["success_count"] == 2)


def test_ai_parse():
    text = '我用夸克网盘给你分享了「142 4K.mp4」\n链接：https://pan.quark.cn/s/588be7f1b99c'
    r = requests.post(f"{BASE_URL}/api/admin/ai/parse", json={"text": text}, headers=auth_headers())
    data = r.json()
    log_test("POST /api/admin/ai/parse", r.status_code == 200 and len(data["parsed"]) >= 1
             and data["parsed"][0]["title"] == "142 4K.mp4")

    batch = '分享「A.mp4」\n链接：https://pan.quark.cn/s/aaa\n\n分享「B.mp4」\n链接：https://pan.quark.cn/s/bbb'
    r = requests.post(f"{BASE_URL}/api/admin/ai/parse-batch", json={"text": batch}, headers=auth_headers())
    log_test("POST /api/admin/ai/parse-batch", r.status_code == 200 and r.json()["success_count"] == 2)


def test_stats():
    r = requests.get(f"{BASE_URL}/api/admin/stats/overview", headers=auth_headers())
    data = r.json()
    log_test("GET /api/admin/stats/overview", r.status_code == 200 and "total_resources" in data)
    print(f"    → 资源:{data['total_resources']} 用户:{data['total_users']} 搜索:{data['total_searches']} 今日:{data['today_searches']}")


def test_users():
    r = requests.get(f"{BASE_URL}/api/admin/users", headers=auth_headers())
    log_test("GET /api/admin/users", r.status_code == 200 and r.json()["total"] >= 1)

    users = r.json()["items"]
    test_user = next((u for u in users if u["username"] == "testuser"), None)
    if test_user:
        r = requests.delete(f"{BASE_URL}/api/admin/users/{test_user['id']}", headers=auth_headers())
        log_test("DELETE /api/admin/users/{id}", r.status_code == 200)


def test_delete(res_id, cat_id):
    # 先测试删除有关联资源的分类（应失败）
    r = requests.delete(f"{BASE_URL}/api/admin/categories/{cat_id}", headers=auth_headers())
    log_test("DELETE /api/admin/categories/{id} (有关联)", r.status_code == 400)

    # 再删除资源
    r = requests.delete(f"{BASE_URL}/api/admin/resources/{res_id}", headers=auth_headers())
    log_test("DELETE /api/admin/resources/{id}", r.status_code == 200)


USER_TOKEN = None


def test_wish_flow():
    global USER_TOKEN
    print("\n[许愿功能测试]")

    r = requests.post(f"{BASE_URL}/api/auth/register", json={
        "username": "wishuser", "email": "wish@example.com", "password": "wish123"
    })
    log_test("注册许愿测试用户", r.status_code == 200)

    r = requests.post(f"{BASE_URL}/api/auth/login", json={"username": "wishuser", "password": "wish123"})
    log_test("许愿用户登录", r.status_code == 200 and "access_token" in r.json())
    USER_TOKEN = r.json().get("access_token")
    user_headers = {"Authorization": f"Bearer {USER_TOKEN}"}

    r = requests.post(f"{BASE_URL}/api/wishes", json={"content": "我想要一份Python教程"}, headers=user_headers)
    log_test("创建许愿", r.status_code == 200 and r.json()["content"] == "我想要一份Python教程")
    wish_id = r.json()["id"]

    r = requests.get(f"{BASE_URL}/api/wishes/my", headers=user_headers)
    log_test("获取我的许愿列表", r.status_code == 200 and len(r.json()) >= 1)
    wish_data = r.json()[0]
    log_test("许愿内容正确显示", wish_data["content"] == "我想要一份Python教程")
    log_test("许愿包含回复列表", "replies" in wish_data and isinstance(wish_data["replies"], list))

    r = requests.get(f"{BASE_URL}/api/wishes/unread-count", headers=user_headers)
    log_test("获取未读回复数(初始为0)", r.status_code == 200 and r.json()["count"] == 0)

    r = requests.post(f"{BASE_URL}/api/admin/wishes/{wish_id}/reply", json={
        "content": "已为你找到Python教程",
        "resource_link": "https://pan.quark.cn/s/python123",
        "resource_link_type": "quark",
        "resource_title": "Python入门教程"
    }, headers=auth_headers())
    log_test("管理员回复许愿", r.status_code == 200 and r.json()["content"] == "已为你找到Python教程")

    r = requests.get(f"{BASE_URL}/api/wishes/unread-count", headers=user_headers)
    log_test("获取未读回复数(回复后为1)", r.status_code == 200 and r.json()["count"] == 1)

    r = requests.get(f"{BASE_URL}/api/wishes/replies", headers=user_headers)
    log_test("获取许愿回复列表", r.status_code == 200 and len(r.json()) >= 1)
    reply_data = r.json()[0]
    log_test("回复内容正确显示", reply_data["reply_content"] == "已为你找到Python教程")
    log_test("回复关联许愿内容", reply_data["wish_content"] == "我想要一份Python教程")
    log_test("回复包含资源链接", reply_data["resource_link"] == "https://pan.quark.cn/s/python123")

    r = requests.post(f"{BASE_URL}/api/wishes/mark-read", headers=user_headers)
    log_test("标记回复已读", r.status_code == 200)

    r = requests.get(f"{BASE_URL}/api/wishes/unread-count", headers=user_headers)
    log_test("已读后未读数归零", r.status_code == 200 and r.json()["count"] == 0)

    r = requests.get(f"{BASE_URL}/api/wishes/my", headers=user_headers)
    log_test("许愿详情含回复数据", r.status_code == 200 and len(r.json()[0]["replies"]) >= 1)

    r = requests.get(f"{BASE_URL}/api/admin/wishes", headers=auth_headers())
    log_test("管理员获取许愿列表", r.status_code == 200 and len(r.json()) >= 1)


def test_announcement_flow():
    print("\n[公告功能测试]")

    r = requests.post(f"{BASE_URL}/api/admin/announcements", json={
        "title": "系统升级公告",
        "content": "## 升级通知\n\n系统将于**今晚**进行升级维护。\n\n- 功能1\n- 功能2\n\n[点击查看](https://example.com)",
        "is_published": True,
        "sort_order": 1
    }, headers=auth_headers())
    log_test("创建公告(Markdown)", r.status_code == 200 or r.status_code == 201)
    ann_id = r.json()["id"]

    r = requests.get(f"{BASE_URL}/api/announcements")
    log_test("前台获取公告列表", r.status_code == 200 and len(r.json()) >= 1)
    log_test("公告内容包含Markdown", "## 升级通知" in r.json()[0]["content"])

    r = requests.put(f"{BASE_URL}/api/admin/announcements/{ann_id}", json={
        "title": "更新后的公告",
        "content": "### 新内容\n\n- 更新1\n- 更新2",
        "is_published": True
    }, headers=auth_headers())
    log_test("更新公告", r.status_code == 200)

    r = requests.delete(f"{BASE_URL}/api/admin/announcements/{ann_id}", headers=auth_headers())
    log_test("删除公告", r.status_code == 200)


def test_donation_flow():
    print("\n[打赏功能测试]")

    r = requests.get(f"{BASE_URL}/api/donation")
    log_test("获取打赏配置", r.status_code == 200 and "content" in r.json())

    r = requests.put(f"{BASE_URL}/api/admin/donation", json={
        "content": "## 感谢支持\n\n![二维码](https://example.com/qr.png)\n\n> 扫码打赏"
    }, headers=auth_headers())
    log_test("更新打赏配置(Markdown)", r.status_code == 200)

    r = requests.get(f"{BASE_URL}/api/donation")
    log_test("验证打赏内容更新", r.status_code == 200 and "感谢支持" in r.json()["content"])


def main():
    print("=" * 60)
    print("  云盘资源搜索系统 - API 接口自动化测试")
    print("=" * 60)

    # 设置环境变量为SQLite（同步驱动，用于测试）
    os.environ["DATABASE_URL"] = "sqlite:///./test_api.db"

    print("\n启动测试服务器...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9001"],
        cwd=BACKEND_DIR,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    # 等待服务器启动
    for i in range(10):
        time.sleep(1)
        try:
            requests.get(f"{BASE_URL}/health", timeout=1)
            break
        except:
            continue

    try:
        print("\n开始测试...\n")

        print("[1] 基础接口")
        test_health()
        test_root()

        print("\n[2] 认证接口")
        test_auth()

        print("\n[3] 分类管理")
        cat_id = test_categories()

        print("\n[4] 资源管理")
        res_id = test_resources(cat_id)

        print("\n[5] 搜索功能")
        test_search()

        print("\n[6] CSV导入")
        test_csv_import()

        print("\n[7] AI识别")
        test_ai_parse()

        print("\n[8] 统计接口")
        test_stats()

        print("\n[9] 用户管理")
        test_users()

        print("\n[10] 删除操作")
        test_delete(res_id, cat_id)

        print("\n[11] 许愿功能")
        test_wish_flow()

        print("\n[12] 公告功能")
        test_announcement_flow()

        print("\n[13] 打赏功能")
        test_donation_flow()

    finally:
        proc.terminate()
        proc.wait()
        db_path = os.path.join(BACKEND_DIR, "test_api.db")
        if os.path.exists(db_path):
            os.remove(db_path)

    print("\n" + "=" * 60)
    total = RESULTS["passed"] + RESULTS["failed"]
    print(f"  测试结果: {RESULTS['passed']}/{total} 通过")
    print("=" * 60)

    if RESULTS["failed"] > 0:
        print("\n失败的测试:")
        for t in RESULTS["tests"]:
            if t["status"] == "FAIL":
                print(f"  ✗ {t['name']} — {t['detail']}")
        sys.exit(1)
    else:
        print("\n所有测试通过!")


if __name__ == "__main__":
    main()
