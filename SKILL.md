---
name: google-suggest-miner
description: |
  Use this skill whenever the user wants to mine Google search suggestions,
  keyword ideas, long-tail keywords, autocomplete suggestions, or expand a seed
  keyword. Trigger for phrases like "挖掘联想词", "Google Suggest",
  "keyword suggestions", "autocomplete", "长尾词", "关键词扩展",
  "search suggestions", "find related keywords", or any request to discover
  what real users search for on Google. Also trigger when the user wants to
  quickly validate content ideas, SEO angles, or game/app feature demand by
  looking at actual search behavior.
---

# Google Suggest Miner

挖掘 Google 搜索框自动补全联想词，基于真实用户搜索行为扩展关键词。

## When to use

- 用户给了一个种子词，想要扩展出更多相关搜索词
- 用户说 "挖一下这个词的联想词"、"Google Suggest"、"关键词扩展" 等
- 用户在做 SEO/内容选题/游戏站选题，需要真实搜索需求
- 用户想验证某个主题的热度或周边需求

## How to run

1. 从用户消息中提取 **种子关键词**（seed keyword）。
2. 在当前工作目录运行脚本：
   ```bash
   python "<skill-dir>\scripts\google_suggest_scraper.py" -s "种子关键词"
   ```
   - Windows 路径示例：`C:\Users\Qyc\.claude\skills\google-suggest-miner\scripts\google_suggest_scraper.py`
3. 脚本会自动：
   - 查询种子词本身
   - 遍历 `a-z`（如 `种子词 a`, `种子词 b` ...）
   - 对结果去重
   - 在当前目录保存 `google_suggest_<seed>_<timestamp>.csv` 和 `.json`
4. 运行完成后，向用户汇报：
   - 种子词
   - 查询了多少个关键词
   - 去重后拿到多少条
   - 保存的文件路径
   - 前 10-20 条联想词预览

## Parameters

- `-s, --seed`：种子关键词（必填，通常从用户消息中提取）
- `-o, --output`：输出文件名前缀（默认 `google_suggest`）
- `--min-delay`：请求间隔最小秒数（默认 0.3）
- `--max-delay`：请求间隔最大秒数（默认 0.8）

如果用户要求更快或更慢，调整 `--min-delay` 和 `--max-delay`。

## Output files

- **CSV**：每行一个去重后的联想词，可直接用于关键词分析、内容规划
- **JSON**：包含原始分组数据和元信息（查询时间、查询数量、去重数量）

## Notes

- Google Suggest API 无需认证，但有访问频率限制。默认延迟 0.3-0.8s 通常安全。
- 如果返回为空或大量失败，可能是网络、IP 限制或种子词太冷门。建议换词、加代理或增大延迟。
- 脚本输出使用 UTF-8。Windows 终端若显示乱码，可先运行 `chcp 65001`。

## Example user prompts

- "帮我挖一下 'build a soccer squad' 的 Google 联想词"
- "关键词扩展：AI image generator"
- "用 Google Suggest 看看 'roblox game' 大家搜什么"
- "长尾词挖掘：best free website builder"
