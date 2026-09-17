#!/usr/bin/env python3
"""
Convert GitHub Issue Form markdown body into a structured YAML record in data/records/
"""

import os
import sys
import re
import json
from pathlib import Path
from datetime import datetime

try:
    import yaml
except ImportError:
    print("❌ 未安装 PyYAML")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RECORDS_DIR = PROJECT_ROOT / "data" / "records"

ALLOWED_OFFENSES = [
    ("摇一摇", "摇一摇跳转"),
    ("扭一扭", "扭一扭/倾斜跳转"),
    ("倾斜", "扭一扭/倾斜跳转"),
    ("开屏", "开屏广告/全屏遮罩"),
    ("全屏遮罩", "开屏广告/全屏遮罩"),
    ("假关闭", "假关闭按钮/像素级诱导"),
    ("诱导", "假关闭按钮/像素级诱导"),
    ("系统通知", "伪装系统通知/红包/短信"),
    ("红包", "伪装系统通知/红包/短信"),
    ("短信", "伪装系统通知/红包/短信"),
    ("自动下载", "自动下载/静默安装"),
    ("静默安装", "自动下载/静默安装"),
    ("无法关闭", "无法关闭/强制倒计时"),
    ("倒计时", "无法关闭/强制倒计时"),
    ("悬浮窗", "应用内悬浮窗/流氓弹窗"),
    ("恐吓", "恐吓欺诈/假冒杀毒清理"),
    ("杀毒", "恐吓欺诈/假冒杀毒清理"),
    ("扣费", "诱导付费/隐蔽扣费")
]

ALLOWED_CATEGORIES = [
    "电商购物", "金融借贷", "网络游戏", "二手车/房产",
    "生活服务", "社交娱乐", "工具清理", "在线教育/培训",
    "医疗健康/保健", "其他"
]

KNOWN_BRANDS = {
    "拼多多": {"parent": "上海寻梦信息技术有限公司", "category": "电商购物", "level": 5},
    "pdd": {"parent": "上海寻梦信息技术有限公司", "category": "电商购物", "level": 5},
    "快手": {"parent": "北京快手科技有限公司", "category": "社交娱乐", "level": 4},
    "快手极速版": {"parent": "北京快手科技有限公司", "category": "社交娱乐", "level": 4},
    "360借条": {"parent": "奇富科技股份有限公司 (原360数科)", "category": "金融借贷", "level": 5},
    "奇富科技": {"parent": "奇富科技股份有限公司", "category": "金融借贷", "level": 5},
    "抖音": {"parent": "北京字节跳动科技有限公司", "category": "社交娱乐", "level": 4},
    "抖音极速版": {"parent": "北京字节跳动科技有限公司", "category": "社交娱乐", "level": 4},
    "今日头条": {"parent": "北京字节跳动科技有限公司", "category": "社交娱乐", "level": 4},
    "得物": {"parent": "上海识装信息科技有限公司", "category": "电商购物", "level": 4},
    "瓜子二手车": {"parent": "车好多旧机动车经纪（北京）有限公司", "category": "二手车/房产", "level": 4},
    "转转": {"parent": "北京转转精神科技有限责任公司", "category": "二手车/房产", "level": 4},
    "淘宝": {"parent": "阿里巴巴（中国）网络技术有限公司", "category": "电商购物", "level": 4},
    "淘特": {"parent": "阿里巴巴（中国）网络技术有限公司", "category": "电商购物", "level": 4},
    "京东": {"parent": "北京京东世纪贸易有限公司", "category": "电商购物", "level": 4},
    "京东金条": {"parent": "京东科技控股股份有限公司", "category": "金融借贷", "level": 5},
    "京东白条": {"parent": "京东科技控股股份有限公司", "category": "金融借贷", "level": 5},
    "度小满": {"parent": "度小满科技（北京）有限公司", "category": "金融借贷", "level": 5},
    "有钱花": {"parent": "度小满科技（北京）有限公司", "category": "金融借贷", "level": 5},
    "美团": {"parent": "北京三快科技有限公司", "category": "生活服务", "level": 3}
}

def parse_issue_markdown(body: str) -> dict:
    """Parse sections delimited by ### Title"""
    sections = {}
    current_key = None
    current_lines = []

    for line in body.splitlines():
        if line.startswith("### "):
            if current_key:
                sections[current_key] = "\n".join(current_lines).strip()
            current_key = line[4:].strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_key:
        sections[current_key] = "\n".join(current_lines).strip()

    return sections

def clean_val(val: str, default="") -> str:
    if not val:
        return default
    val = val.strip()
    if val in ["_No response_", "无", "暂无", "未知", "none", "None"]:
        return default
    return val

def extract_field(sections: dict, keywords: list, default="") -> str:
    for sec_name, content in sections.items():
        for kw in keywords:
            if kw in sec_name:
                return clean_val(content, default)
    return default

def process_issue(issue_data: dict, issue_number: int) -> Path:
    body = issue_data.get("body", "")
    sections = parse_issue_markdown(body)

    # 1. Advertiser name
    adv_name = extract_field(sections, ["作恶广告主", "品牌名称"], "未知品牌")
    # Clean possible markdown bold/links
    adv_name = re.sub(r"[*_`]", "", adv_name).strip()

    # 2. Parent company
    parent_company = extract_field(sections, ["母公司", "公司全称"], "")
    parent_company = re.sub(r"[*_`]", "", parent_company).strip()

    # 3. Category
    raw_cat = extract_field(sections, ["品类", "业务品类"], "其他")
    category = "其他"
    for cat in ALLOWED_CATEGORIES:
        if cat in raw_cat:
            category = cat
            break

    # 4. Boycott level
    raw_level = extract_field(sections, ["抵制程度", "星级"], "5")
    match_level = re.search(r"\b([1-5])\b", raw_level)
    boycott_level = int(match_level.group(1)) if match_level else 5

    # Auto-fill from KNOWN_BRANDS if missing
    for brand_key, brand_info in KNOWN_BRANDS.items():
        if brand_key.lower() in adv_name.lower() or adv_name.lower() in brand_key.lower():
            if not parent_company:
                parent_company = brand_info.get("parent", "")
            if category == "其他":
                category = brand_info.get("category", "其他")
            break

    # 5. Host app & platform
    raw_host = extract_field(sections, ["宿主 APP", "受害宿主"], "未知应用")
    host_name = raw_host
    platform = "Android"  # default
    if "ios" in raw_host.lower() or "iphone" in raw_host.lower() or "ipad" in raw_host.lower():
        platform = "iOS"
    elif "harmony" in raw_host.lower() or "鸿蒙" in raw_host:
        platform = "HarmonyOS"
    elif "windows" in raw_host.lower():
        platform = "Windows"
    elif "mac" in raw_host.lower():
        platform = "macOS"

    # Clean host name (e.g. "酷狗音乐 (iOS 17.5)" -> "酷狗音乐")
    host_name = re.split(r"[\(（\s]", host_name)[0].strip()
    if not host_name:
        host_name = "未知应用"

    # 6. Offense types
    raw_offenses = extract_field(sections, ["作恶类型", "流氓手法", "恶劣行为"], "")
    detected_offenses = set()
    for line in raw_offenses.splitlines():
        if "[x]" in line.lower() or "✓" in line:
            for kw, std_name in ALLOWED_OFFENSES:
                if kw in line:
                    detected_offenses.add(std_name)

    # If none detected from checkboxes, scan raw text
    if not detected_offenses:
        for kw, std_name in ALLOWED_OFFENSES:
            if kw in raw_offenses or kw in body:
                detected_offenses.add(std_name)
    if not detected_offenses:
        detected_offenses.add("其他恶劣行为")

    # 7. Description
    description = extract_field(sections, ["详细恶行描述", "详细描述", "经历"], "")
    if len(description) < 10:
        description = f"在 {host_name} 遇到来自 {adv_name} 的流氓广告弹窗，严重打断用户正常使用体验。"

    # 8. Evidence Images
    raw_evidence = extract_field(sections, ["证据截图", "截图", "证据"], "")
    image_urls = re.findall(r'https?://[^\s\)]+?\.(?:png|jpe?g|gif|webp)(?:\?[^\s\)]*)?', raw_evidence, re.IGNORECASE)
    # Also find github user-attachment urls without extension
    github_attachments = re.findall(r'https?://(?:github\.com|github-production-user-asset-[^\s\)]+|user-images\.githubusercontent\.com)[^\s\)]+', raw_evidence)
    all_images = list(dict.fromkeys(image_urls + github_attachments))

    # 9. Host Alternatives
    raw_host_alts = extract_field(sections, ["替换该宿主", "替换宿主", "干净软件"], "")
    host_alternatives = [a.strip() for a in re.split(r"[,，、\n]+", raw_host_alts) if a.strip() and a.strip() not in ["_No response_", "无"]]

    # 10. Advertiser Alternatives
    raw_adv_alts = extract_field(sections, ["替代该广告主", "良心消费途径", "购买渠道"], "")
    adv_alternatives = [a.strip() for a in re.split(r"[,，、\n]+", raw_adv_alts) if a.strip() and a.strip() not in ["_No response_", "无"]]

    # Generate record ID
    date_str = datetime.now().strftime("%Y-%m-%d")
    date_compact = datetime.now().strftime("%Y%m%d")
    clean_brand = re.sub(r"[^\w]+", "", adv_name) or "ad"
    record_id = f"{date_compact}-issue{issue_number}-{clean_brand}"

    record = {
        "id": record_id,
        "date": date_str,
        "advertiser": {
            "name": adv_name,
            "category": category,
            "boycott_level": boycott_level
        },
        "host_app": {
            "name": host_name,
            "platform": platform
        },
        "offense_type": sorted(list(detected_offenses)),
        "description": description,
        "evidence": {
            "images": all_images,
            "video_url": ""
        }
    }

    if parent_company:
        record["advertiser"]["parent_company"] = parent_company
    if host_alternatives:
        record["host_alternatives"] = host_alternatives
    if adv_alternatives:
        record["advertiser_alternatives"] = adv_alternatives
    record["tags"] = [category] + [o.split("/")[0] for o in record["offense_type"][:2]]

    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = RECORDS_DIR / f"{record_id}.yaml"
    with open(out_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(record, f, allow_unicode=True, sort_keys=False)

    return out_file

def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/issue_to_record.py <path_to_github_event.json> 或从 GITHUB_EVENT_PATH 读取")
        sys.exit(1)

    event_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(os.environ.get("GITHUB_EVENT_PATH", ""))
    if not event_path.exists():
        print(f"❌ 找不到事件文件: {event_path}")
        sys.exit(1)

    with open(event_path, "r", encoding="utf-8") as f:
        event = json.load(f)

    issue = event.get("issue")
    if not issue:
        print("❌ 事件中不包含 issue 对象")
        sys.exit(1)

    issue_number = issue.get("number", 0)
    out_path = process_issue(issue, issue_number)
    print(f"🎉 成功由 Issue #{issue_number} 转化并生成记录文件: {out_path.name}")
    print(f"::set-output name=record_file::{out_path.name}")
    print(f"::set-output name=record_id::{out_path.stem}")

if __name__ == "__main__":
    main()
