# 搬运工（question-bank-porter）

把审题 skill（`batch-interview-question-audit`）每轮产出的文件，精准搬运并上传到「各岗位AI审题进度」仓库（`ai-question-review-progress`）对应岗位文件夹的 Cursor / Claude Agent Skill。

## 能做什么

每轮审核完（一二轮视为一轮）、重新出完题、最后汇总完、或做完语言问题审核后，调用本 skill 即可把以下文件自动归位并上传：

| 来源文件 | 目标文件夹 |
|---|---|
| 保留题目表 | `2_保留题目/` |
| 需重新出题表 | `3_需重新出题/` |
| 重新出答案表 | `4_需重新出答案/` |
| HTML 审核看板 | `5_审核结果看板/` |
| 最终汇总保留题目 | `6_汇总/` |
| 待审核题目 | `1_待审核题目/` |
| 语言问题审核（四类） | `7_语言问题审核/` 对应子文件夹 |

文件命名不规范时会先自动改名再上传，岗位路径以目标仓库 `data/positions.csv` 为准。

## 安装

把整个仓库放到个人 skills 目录：

```bash
git clone https://github.com/0565cx/question-bank-porter.git \
  ~/.cursor/skills/question-bank-porter
```

之后在 Cursor 对话框里调用「搬运工」即可。

## 脚本用法

```bash
# 预演（只打印搬运计划，不复制）
python3 ~/.cursor/skills/question-bank-porter/scripts/port.py \
  --repo <仓库路径> --src "<源目录或文件>"

# 确认无误后执行
python3 ~/.cursor/skills/question-bank-porter/scripts/port.py \
  --repo <仓库路径> --src "<源目录或文件>" --apply
```

详细工作流见 [SKILL.md](./SKILL.md)。
