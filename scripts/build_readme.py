#!/usr/bin/env python3
"""
Compile data/records/*.yaml into a rich, structured, and beautifully formatted README.md
"""

import sys
import argparse
from pathlib import Path
from collections import Counter, defaultdict

try:
    import yaml
except ImportError:
    print("❌ 错误: 未安装 PyYAML，请运行 pip install pyyaml 安装。")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RECORDS_DIR = PROJECT_ROOT / "data" / "records"
README_FILE = PROJECT_ROOT / "README.md"

STARS = {
    1: "⭐☆☆☆☆ (轻度骚扰)",
    2: "⭐⭐☆☆☆ (中度反感)",
    3: "⭐⭐⭐☆☆ (严重流氓)",
    4: "⭐⭐⭐⭐☆ (极度恶劣)",
    5: "⭐⭐⭐⭐⭐ (终身拉黑/坚决不买)"
}

def load_records():
    records = []
    if not RECORDS_DIR.exists():
        return records

    for file_path in sorted(RECORDS_DIR.glob("*.yaml")) + sorted(RECORDS_DIR.glob("*.yml")):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = yaml.safe_load(f)
                if isinstance(data, dict) and data.get("id"):
                    data["_file"] = file_path.name
                    records.append(data)
            except Exception as e:
                print(f"⚠️ 跳过解析失败文件 {file_path.name}: {e}")
    return records

def generate_markdown(records):
    total_records = len(records)
    
    # Aggregations
    advertisers_map = defaultdict(lambda: {
        "count": 0,
        "max_level": 0,
        "parent_company": set(),
        "categories": set(),
        "hosts": set(),
        "offenses": Counter()
    })
    
    hosts_map = defaultdict(lambda: {
        "count": 0,
        "platforms": set(),
        "advertisers": set(),
        "offenses": Counter()
    })

    offense_counter = Counter()
    host_alternatives_map = defaultdict(set)       # host_name -> set of alternatives
    advertiser_alternatives_map = defaultdict(set) # category -> set of alternatives

    for r in records:
        adv = r.get("advertiser", {})
        adv_name = adv.get("name", "未知品牌")
        category = adv.get("category", "其他")
        parent = adv.get("parent_company")
        level = adv.get("boycott_level", 3)
        
        host = r.get("host_app", {})
        host_name = host.get("name", "未知APP")
        platform = host.get("platform", "未知")

        offenses = r.get("offense_type", [])
        for off in offenses:
            offense_counter[off] += 1
            advertisers_map[adv_name]["offenses"][off] += 1
            hosts_map[host_name]["offenses"][off] += 1

        advertisers_map[adv_name]["count"] += 1
        advertisers_map[adv_name]["max_level"] = max(advertisers_map[adv_name]["max_level"], level)
        advertisers_map[adv_name]["categories"].add(category)
        if parent:
            advertisers_map[adv_name]["parent_company"].add(parent)
        advertisers_map[adv_name]["hosts"].add(host_name)

        hosts_map[host_name]["count"] += 1
        hosts_map[host_name]["platforms"].add(platform)
        hosts_map[host_name]["advertisers"].add(adv_name)

        # Host alternatives
        h_alts = r.get("host_alternatives", [])
        if not h_alts and "suggested_alternatives" in r:
            h_alts = r.get("suggested_alternatives", [])
        for h_alt in h_alts:
            if h_alt.strip():
                host_alternatives_map[host_name].add(h_alt.strip())

        # Advertiser alternatives
        a_alts = r.get("advertiser_alternatives", [])
        for a_alt in a_alts:
            if a_alt.strip():
                advertiser_alternatives_map[category].add(a_alt.strip())

    unique_advertisers = len(advertisers_map)
    unique_hosts = len(hosts_map)

    # Sort records chronologically (descending), tie-break with id
    sorted_records = sorted(records, key=lambda x: (str(x.get("date", "")), str(x.get("id", ""))), reverse=True)

    lines = []
    lines.append("# 🛑 fucking-ad (流氓弹窗广告恶行录)")
    lines.append("")
    lines.append("> 🌐 **在线避雷检索站（移动端友好 · 毫秒级搜索）**：**[https://fairyeye.github.io/fucking-ad/](https://fairyeye.github.io/fucking-ad/)**  ")
    lines.append("> 💬 **「每一次你被弹窗恶心后记住的品牌，都是流氓营销的得逞。」**  ")
    lines.append("> ⚡ **「互联网没有记忆，但 Git 有。既然你敢弹窗骚扰，我就永远拉黑你家产品。」**")
    lines.append("")
    lines.append("[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)")
    lines.append("[![Online Portal](https://img.shields.io/badge/Online%20Web-在线检索站-rose.svg)](https://fairyeye.github.io/fucking-ad/)")
    lines.append(f"![Total Records](https://img.shields.io/badge/收录恶行-{total_records}条-red.svg)")
    lines.append(f"![Boycotted Brands](https://img.shields.io/badge/抵制品牌-{unique_advertisers}个-orange.svg)")
    lines.append(f"![Host Apps](https://img.shields.io/badge/宿主APP-{unique_hosts}款-critical.svg)")
    lines.append("[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🎯 项目初衷 (Manifesto)")
    lines.append("")
    lines.append("你是否也经历过这些令人崩溃的瞬间？")
    lines.append("- 走在路上刚掏出手机，手腕稍微一晃，立马触发 **「摇一摇 / 扭一扭」** 强行唤醒并跳转到某个购物或网贷软件；")
    lines.append("- 弹窗上的关闭按键是伪装的假图标，或者小到只有几个像素，点上去直接触发全屏静默下载；")
    lines.append("- 弹窗伪装成「微信红包到账」、「系统严重警告」或「好友发来未读消息」，专骗长辈和普通用户点击；")
    lines.append("- 明明付了会员费，打开 APP 依然要被强制看 5 秒全屏广告。")
    lines.append("")
    lines.append("很多人在心里暗下决心：*“这家公司的东西我一辈子都不买！”*  ")
    lines.append("但广告心理学就是利用了人类的**遗忘效应**：几个月后你忘了当初是在流氓弹窗里见过的它，只觉得这个品牌「很耳熟、知名度高」，于是在超市或网购时不自觉下了单——**流氓营销得逞了。**")
    lines.append("")
    lines.append("**本项目旨在建立一份永久、公开、可查证的「流氓弹窗黑名单」**。")
    lines.append("1. **记录在案**：把每次侵扰记录成代码，沉淀真实截图佐证，永久固定其恶行。")
    lines.append("2. **消费避雷**：当你要购买某类商品或服务时，来这里搜一下，把钱投给真正尊重用户的良心品牌。")
    lines.append("3. **反制工具**：提供干净软件替代品清单，帮助大家卸载作恶宿主 APP。")
    lines.append("4. **社区共建**：人人的手机都是监控探头，让流氓投放无所遁形。")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📊 恶行总览与数据统计")
    lines.append("")
    lines.append(f"- 📝 **已收录恶行记录**：`{total_records}` 次")
    lines.append(f"- 🚫 **上榜抵制品牌数**：`{unique_advertisers}` 家")
    lines.append(f"- 📲 **纵容作恶宿主 APP**：`{unique_hosts}` 款")
    lines.append("")
    lines.append("### 🔥 最常见流氓作恶手法分布")
    lines.append("")
    lines.append("| 恶行类型 | 出现次数 | 占比 | 典型特征 |")
    lines.append("| :--- | :---: | :---: | :--- |")
    sorted_offenses = sorted(offense_counter.items(), key=lambda x: (-x[1], x[0]))
    for off_name, off_count in sorted_offenses:
        pct = f"{(off_count / total_records * 100):.1f}%" if total_records > 0 else "0%"
        lines.append(f"| **{off_name}** | `{off_count}` | {pct} | 滥用传感器、微小假关闭按钮、视觉欺诈 |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🛑 广告主黑榜 (坚决不买 / 终身抵制)")
    lines.append("")
    lines.append("> 提示：消费即投票。当你需要消费时，请尽量避开以下投放流氓广告的品牌及旗下关联产品。")
    lines.append("")
    lines.append("| 抵制品牌 | 所属母公司 / 关联主体 | 涉及品类 | 作恶次数 | 抵制指数 | 常勾结的宿主APP |")
    lines.append("| :--- | :--- | :--- | :---: | :--- | :--- |")

    # Sort advertisers by count desc, max_level desc, then name
    sorted_advs = sorted(advertisers_map.items(), key=lambda x: (x[1]["count"], x[1]["max_level"], x[0]), reverse=True)
    for adv_name, info in sorted_advs:
        parent_str = "、".join(sorted(info["parent_company"])) if info["parent_company"] else "未知"
        cat_str = "、".join(sorted(info["categories"]))
        level_str = STARS.get(info["max_level"], "⭐⭐⭐☆☆")
        hosts_list = sorted(list(info["hosts"]))
        hosts_str = "、".join(hosts_list[:3]) + (" 等" if len(hosts_list) > 3 else "")
        lines.append(f"| **{adv_name}** | {parent_str} | {cat_str} | `{info['count']}` | {level_str} | {hosts_str} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📱 宿主 APP 作恶榜 (流氓弹窗高发地)")
    lines.append("")
    lines.append("| 宿主 APP | 平台 | 纵容投放次数 | 主要流氓手法 | 频繁推送的广告主 | 推荐替换方案 |")
    lines.append("| :--- | :---: | :---: | :--- | :--- | :--- |")
    
    sorted_hosts = sorted(hosts_map.items(), key=lambda x: (x[1]["count"], x[0]), reverse=True)
    for host_name, info in sorted_hosts:
        plat_str = " / ".join(sorted(info["platforms"]))
        sorted_host_offenses = sorted(info["offenses"].items(), key=lambda x: (-x[1], x[0]))
        top_offenses = "、".join([k for k, _ in sorted_host_offenses[:2]])
        advs_list = sorted(list(info["advertisers"]))
        top_advs = "、".join(advs_list[:3])
        alts = host_alternatives_map.get(host_name, set())
        sorted_alts = sorted(list(alts))
        alt_str = "、".join(sorted_alts[:2]) if sorted_alts else "寻找纯净替代"
        lines.append(f"| **{host_name}** | {plat_str} | `{info['count']}` | {top_offenses} | {top_advs} | {alt_str} |")

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 📋 最近收录的恶行证据档案")
    lines.append("")
    lines.append("<details>")
    lines.append("<summary><b>👉 点击展开查看所有收录的历史恶行细节（按日期倒序）</b></summary>")
    lines.append("")

    for r in sorted_records:
        rid = r.get("id")
        date = r.get("date")
        adv = r.get("advertiser", {})
        host = r.get("host_app", {})
        offenses = "、".join([f"`{o}`" for o in r.get("offense_type", [])])
        desc = r.get("description", "")
        level = adv.get("boycott_level", 3)
        level_star = STARS.get(level, "⭐⭐⭐☆☆")
        evidence = r.get("evidence", {})
        images = evidence.get("images", [])

        lines.append(f"### 📍 [{date}] {adv.get('name')} 侵扰事件 (`{rid}`)")
        lines.append(f"- **作恶广告主**：{adv.get('name')}（{adv.get('category')} / 母公司：{adv.get('parent_company', '未知')}）")
        lines.append(f"- **抵制推荐指数**：{level_star}")
        lines.append(f"- **受害宿主 APP**：{host.get('name')} ({host.get('platform', '未知')} {host.get('version', '')})")
        lines.append(f"- **作恶类型**：{offenses}")
        lines.append(f"- **详细恶行描述**：{desc}")
        
        if images:
            img_links = []
            for img in images:
                if img.startswith("http"):
                    img_links.append(f"[查看网络截图]({img})")
                else:
                    img_links.append(f"[查看截图证据]({img})")
            lines.append(f"- **证据留存**：{' ｜ '.join(img_links)}")
        
        h_alts = r.get("host_alternatives", [])
        if h_alts:
            lines.append(f"- **📲 推荐卸载并替换该宿主 APP 为**：{'、'.join(h_alts)}")

        a_alts = r.get("advertiser_alternatives", [])
        if a_alts:
            lines.append(f"- **🛒 抵制该广告主的良心消费途径**：{'、'.join(a_alts)}")

        lines.append(f"- **原始数据源**：[`data/records/{r['_file']}`](data/records/{r['_file']})")
        lines.append("")
        lines.append("---")

    lines.append("</details>")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 💡 良心替代品推荐库 (以良币驱逐劣币)")
    lines.append("")
    lines.append("抵制劣质商业模式的最强武器，就是支持那些**干净、清爽、尊重用户**的产品与渠道：")
    lines.append("")

    lines.append("### 1. 纯净宿主软件替代品（远离流氓弹窗）")
    lines.append("")
    if host_alternatives_map:
        for h_name, alts in sorted(host_alternatives_map.items()):
            lines.append(f"- **替代【{h_name}】**：{'、'.join(sorted(alts))}")
    lines.append("")

    lines.append("### 2. 良心消费途径推荐（避开流氓投放商）")
    lines.append("")
    if advertiser_alternatives_map:
        for cat, alts in sorted(advertiser_alternatives_map.items()):
            lines.append(f"- **{cat}品类**：{'、'.join(sorted(alts))}")
    lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("## 🤝 如何参与贡献？")
    lines.append("")
    lines.append("欢迎所有受害者共同维护这个黑名单！可以通过以下两种方式提交：")
    lines.append("")
    lines.append("### 方式一：直接提 Issue 举报（推荐，免写代码）")
    lines.append("1. 进入项目的 [Issues](../../issues/new?template=report_ad.yml) 页面；")
    lines.append("2. 选择 **「举报流氓弹窗广告」** 模板；")
    lines.append("3. 按照提示填写：广告品牌、宿主APP、截图凭证；")
    lines.append("4. 维护者审核后会自动转化为数据并合入主分支。")
    lines.append("")
    lines.append("### 方式二：提交 Pull Request（开发者通道）")
    lines.append("1. Fork 本仓库并克隆到本地；")
    lines.append("2. 将截图放入 `screenshots/YYYY/` 目录下；")
    lines.append("3. 在 `data/records/` 下按照格式新增一条 `YYYYMMDD-品牌名-手法.yaml`；")
    lines.append("4. 本地运行校验和编译：")
    lines.append("   ```bash")
    lines.append("   python3 scripts/lint_data.py")
    lines.append("   python3 scripts/build_readme.py")
    lines.append("   ```")
    lines.append("5. 提交 PR，CI 会自动检查格式。")
    lines.append("")
    lines.append("详细规范请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## ⚖️ 客观性与免责声明")
    lines.append("")
    lines.append("1. **事实优先**：所有入库记录必须有真实截屏、录屏或网络公开报道等客观证据支撑，拒绝毫无根据的捏造与恶意中伤。")
    lines.append("2. **就事论事**：记录针对的是「具体的流氓广告投放与诱导行为」，旨在维护消费者的知情权与选择权。")
    lines.append("3. **改过即更新**：若某产品/品牌已全面下架整改此类流氓广告，可提交 Issue 并附上整改证据，项目将在记录中标记「已整改」并调整评级。")
    lines.append("")
    lines.append("---")
    lines.append("### License")
    lines.append("本项目代码遵循 [MIT License](LICENSE)，数据与文档采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh) 协议共享。")
    lines.append("")

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description="Build or check README.md from YAML records.")
    parser.add_argument("--check", action="store_true", help="Check if README.md is up-to-date without writing.")
    args = parser.parse_args()

    records = load_records()
    print(f"📖 读取到 {len(records)} 条恶行记录...")

    new_content = generate_markdown(records)

    if args.check:
        if not README_FILE.exists():
            print("❌ README.md 不存在！")
            sys.exit(1)
        current_content = README_FILE.read_text(encoding="utf-8")
        if current_content != new_content:
            print("❌ README.md 与 data/records/ 数据不同步！请运行 `python scripts/build_readme.py` 更新。")
            sys.exit(1)
        else:
            print("✅ README.md 已经与数据保持最新！")
            sys.exit(0)

    README_FILE.write_text(new_content, encoding="utf-8")
    print(f"🎉 成功更新 {README_FILE}！")

if __name__ == "__main__":
    main()
