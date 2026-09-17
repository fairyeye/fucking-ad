# 贡献指南 (Contributing Guide)

欢迎参与维护 **fucking-ad (移动端流氓广告与诱导跳转实录)**！

移动端非规范广告与诱导跳转之所以屡见不鲜，很大程度上在于用户的注意力容易被遗忘效应冲淡。通过开源社区集体的力量客观留存每一次“反客为主”的商业交互，我们能让诱导营销在阳光下留存档案，把选择权与知情权还给消费者。

---

## 🛡️ 基本准则 (Code of Conduct)

为了保证项目的公信力、严肃性与客观性，所有提交必须遵守以下原则：

1. **真实客观，以图为证**：
   - **必须** 提供真实未篡改的现场屏幕截图、录屏或公开存证凭据。
   - 严禁出于商业竞争恶意捏造、抹黑或无中生有。无客观事实凭据的条目将不予收录。
2. **就事论事，克制理性**：
   - 记录聚焦于「具体的诱导跳转、假关闭按钮、滥用传感器」等客观行为表现，不进行人身攻击。
3. **改过即更新，鼓励良性商业循环**：
   - 若涉事产品/厂商已主动且彻底整改了相关违规行为（例如彻底移除了摇一摇跳转、规范了关闭按钮热区），可在验证属实后更新档案状态并下调避坑评级。

---

## 方式一：通过 Issue 提交案例（推荐普通用户）

如果你不想摆弄代码，只需 1 分钟在线提交：
1. 点击访问项目的 [New Issue](../../issues/new/choose)；
2. 选择 **「📢 提交流氓广告/诱导跳转案例」**；
3. 按照模板逐项填写广告品牌、受害宿主APP、上传截图凭据；
4. 提交后，机器人将自动校验并转录为结构化数据入库。

---

## 方式二：通过 Pull Request 提交（推荐开发者）

### 1. 准备工作
克隆你的 Fork 仓库并安装必要依赖：
```bash
git clone https://github.com/<your-username>/fucking-ad.git
cd fucking-ad
pip install pyyaml
```

### 2. 添加证据截图
将清晰的截图（建议压缩到 1MB 以内）放置在对应年份目录：
```text
screenshots/YYYY/brand-offense-01.png
```

### 3. 创建记录文件
在 `data/records/` 下新建一个 YAML 文件，命名规范为：
`YYYYMMDD-品牌名拼音或英文-手法关键词.yaml`

例如：`data/records/20260917-pinduoduo-shake.yaml`

#### 字段模板与规范：
```yaml
id: "20260917-pinduoduo-shake"         # 唯一标识符，必须与文件名一致（不含.yaml）
date: "2026-09-17"                     # 捕获日期，YYYY-MM-DD
advertiser:
  name: "拼多多"                       # 广告宣传的具体品牌名
  alias:                               # 别名/英文名
    - "Pinduoduo"
    - "PDD"
  parent_company: "上海寻梦信息技术有限公司" # 所属公司全称（可选）
  category: "电商购物"                  # 必须是预设品类（如：电商购物、金融借贷、网络游戏、二手车/房产、生活服务、工具清理等）
  boycott_level: 5                     # 建议避坑指数 (1:轻度不适, 3:体验极差, 5:坚决避坑)
host_app:
  name: "酷狗音乐"                      # 哪个宿主 APP 弹出的广告
  platform: "iOS"                      # iOS / Android / HarmonyOS / Windows / macOS / Web
  version: "12.0.1"                    # 版本号（选填）
offense_type:                          # 典型手法，可多选
  - "摇一摇跳转"
  - "开屏广告/全屏遮罩"
description: >-
  走路时稍微晃动手机，立即强行唤醒外部购物软件；返回原APP后发现关闭按钮延迟3秒才显示，属于典型诱导跳转。
evidence:
  images:
    - "screenshots/2026/pinduoduo_shake_01.png" # 本地截图相对路径，或可访问的公开图床URL
  video_url: ""                        # 录屏视频地址（选填）
host_alternatives:                    # 📲 推荐替换该宿主APP的干净产品
  - "椒盐音乐 (开源本地播放器)"
  - "Apple Music"
advertiser_alternatives:                # 🛒 替代该广告主的良心消费途径
  - "品牌官网直购 / 京东自营"
tags:
  - "摇一摇"
  - "流氓开屏"
```

### 4. 本地验证与构建
在提交代码前，请务必执行以下命令进行本地校验并重新生成 `README.md` 与静态检索站：

```bash
# 1. 校验数据格式与图片有效性
python3 scripts/lint_data.py

# 2. 重新编译 README.md
python3 scripts/build_readme.py

# 3. 重新生成检索站 (docs/)
python3 scripts/build_site.py
```

### 5. 提交 PR
确认 `git diff` 干净且校验全部通过后，推送分支并发起 Pull Request。CI 运行通过后即可快速合并！
