<div align="center">

# 搬运工 · Question Bank Porter

**一句话把审题成果精准归档到进度仓库的 Cursor / Claude Agent Skill**

[![Skill](https://img.shields.io/badge/Agent-Skill-2b7?style=flat-square)](https://github.com/0565cx/question-bank-porter)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square)](https://www.python.org/)

</div>

审题 skill（`batch-interview-question-audit`）每轮会产出一堆表格和看板，手动按「行业 / 岗位 / 文件类型 / 轮次」分门别类传到进度仓库既繁琐又容易传错。**搬运工**把这一步自动化：在对话框里喊一声，它就把每轮的保留题目表、重新出题表、重新出答案表、HTML 看板，以及待审核题目、语言问题审核表，精准送进 [`ai-question-review-progress`](https://github.com/0565cx/ai-question-review-progress) 仓库对应岗位的文件夹里。

## 功能

- **精准归位** — 自动解析文件的子行业、岗位、类型、轮次，按岗位目录归档，岗位路径以仓库 `data/positions.csv` 为准。
- **自动改名** — 文件命名不规范时先规范化再上传，统一命名风格。
- **预演优先** — 默认先输出搬运计划（含改名与无法识别项），确认无误才真正复制。
- **看板联动** — 推送后仓库 GitHub Actions 自动刷新 `进度看板.md` 与 `index.html`。
- **全类型覆盖** — 每轮三表 + 看板、待审核题目、语言问题审核四类，一并支持。

## 工作方式

每轮（一二轮视为一轮）审核完，使用者调用搬运工 skill，搬运工就自动从需要重新出的文件夹里找到三个表（保留题目表、重新出题表、重新出答案表）上传到这个仓库的对应文件夹里，在 X 轮审核结果汇总文件夹里找到 html 格式的看板上传到这个仓库的审核结果看板里。使用者重新出完题后或者最后汇总完后，在对话框里调用搬运工，可以自动精准上传待审核的题目到对应文件夹，如果文件命名不规范，先帮他改明再上传。语言问题审核表也支持使用者调用搬运工后自动精准上传到对应位置。

## 安装

把整个仓库放到个人 skills 目录：

```bash
git clone https://github.com/0565cx/question-bank-porter.git \
  ~/.cursor/skills/question-bank-porter
```

装好后，在 Cursor 对话框里直接说「调用搬运工」「把这轮审核结果传上去」即可触发。

> [!NOTE]
> 本 skill 依赖 Python 3.8+ 和已配置好 GitHub 认证的 `git`。脚本只用到标准库，无需额外安装依赖。

## 归档规则

每个岗位目录下的落点：

| 文件类型 | 目标文件夹 |
|---|---|
| 待审核题目 | `1_待审核题目/` |
| 保留题目表 | `2_保留题目/` |
| 需重新出题表 | `3_需重新出题/` |
| 重新出答案表 | `4_需重新出答案/` |
| HTML 审核看板 | `5_审核结果看板/` |
| 收尾题目（知识审核最后一轮重出） | `6_收尾题目/` |
| 知识审核后汇总保留题目 | `7_知识审核后汇总/` |
| 待语言问题审核 | `8_语言问题审核/1_待语言问题审核/` |
| 语言问题一审结果 | `8_语言问题审核/2_一审结果/` |
| 语言问题待重出 | `8_语言问题审核/3_待重出/` |
| 语言问题重出结果 | `8_语言问题审核/4_重出结果/` |
| 最终汇总保留题目（语言审核也完成后） | `9_最终汇总/` |

类型由文件名关键词识别，轮次从「待X轮审核」「X轮_」「第X轮」解析（支持中文数字）。子行业、岗位先从文件名取，取不到再从父目录路径推断。

## 手动使用脚本

skill 通常自动调用脚本，也可以手动跑：

```bash
# 1) 预演：只打印搬运计划，不复制任何文件
python3 ~/.cursor/skills/question-bank-porter/scripts/port.py \
  --repo <进度仓库路径> \
  --src "<审题产出目录或文件>"

# 2) 确认计划无误后，加 --apply 执行复制
python3 ~/.cursor/skills/question-bank-porter/scripts/port.py \
  --repo <进度仓库路径> \
  --src "<审题产出目录或文件>" --apply
```

`--src` 可重复传多个；目录会递归扫描其中的 `.xlsx` / `.html` 文件。预演输出分「搬运计划」和「⚠️ 无法识别（需人工确认）」两部分。

> [!IMPORTANT]
> 执行 `--apply` 前务必先看一遍搬运计划。无法识别的文件不会被随意归档，需要人工确认或先重命名源文件。

## 典型流程

```
- [ ] 1. 确认源路径与进度仓库路径
- [ ] 2. git pull 同步仓库，再预演输出搬运计划
- [ ] 3. 检查无法识别项，必要时改名 / 补全
- [ ] 4. 确认计划后执行 --apply
- [ ] 5. git 提交并推送
- [ ] 6. 等待 Actions 自动刷新看板
```

> [!WARNING]
> 目标仓库为 private，含敏感题目内容，请勿外发。搬运前先 `git pull`，避免与看板自动提交机器人产生冲突。

## 相关项目

- [`ai-question-review-progress`](https://github.com/0565cx/ai-question-review-progress) — 各岗位 AI 审题进度仓库（搬运目标）
- `batch-interview-question-audit` — 多模型批量审题 skill（搬运来源）

更多搬运工作流细节见 [SKILL.md](./SKILL.md)。
