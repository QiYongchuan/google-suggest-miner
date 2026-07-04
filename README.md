# Google Suggest Miner

Google Suggest 关键词挖掘器 —— 基于 Google 搜索框自动补全，快速扩展关键词、挖掘长尾搜索需求。

A Claude Code skill that mines Google autocomplete suggestions by traversing `seed keyword + a-z`. Useful for SEO, content ideation, and game/app feature research.

---

## 功能 / Features

- 输入一个种子词，自动遍历 `a-z` 获取 Google 联想词
- 对结果去重，保持原始顺序
- 输出 CSV（关键词列表）和 JSON（完整数据）
- 内置请求延迟和重试机制，降低被限制风险
- 无需 API Key，无需代理即可使用

- Input one seed keyword, automatically traverse `a-z` to collect Google suggestions
- Deduplicate while preserving order
- Export CSV (keyword list) and JSON (full data)
- Built-in delay and retry logic to avoid rate limiting
- No API key or proxy required

---

## 安装 / Install

```bash
claude skills add google-suggest-miner https://github.com/QiYongchuan/google-suggest-miner
```

或者手动克隆到 Claude Code skills 目录：

```bash
cd ~/.claude/skills
git clone https://github.com/QiYongchuan/google-suggest-miner.git
```

---

## 使用方法 / Usage

安装 skill 后，在 Claude Code 中直接说：

```
帮我挖一下 'build a soccer squad' 的 Google 联想词
```

或：

```
关键词扩展：best free AI tool
```

Claude 会自动调用脚本并返回结果。

---

## 直接使用脚本 / Use the script directly

```bash
python scripts/google_suggest_scraper.py -s "build a soccer squad"
```

### 参数 / Parameters

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-s, --seed` | 种子关键词 | `build a soccer squad` |
| `-o, --output` | 输出文件名前缀 | `google_suggest` |
| `--min-delay` | 请求间隔最小秒数 | `0.3` |
| `--max-delay` | 请求间隔最大秒数 | `0.8` |

### 示例 / Example

```bash
python scripts/google_suggest_scraper.py -s "best roblox game" --min-delay 0.5 --max-delay 1.2
```

---

## 输出文件 / Output

脚本会在当前目录生成两个文件：

- `google_suggest_<seed>_<timestamp>.csv` — 去重后的关键词列表
- `google_suggest_<seed>_<timestamp>.json` — 包含原始分组和元数据

示例 CSV：

```csv
keyword
build a soccer squad code
build a soccer squad roblox
build a soccer squad game
build a soccer squad random
```

---

## 注意事项 / Notes

- Google Suggest API 无需认证，但有访问频率限制，建议不要调得过快
- 如果大量请求失败，可能是 IP 被临时限制，可增大 `--min-delay`/`--max-delay`
- Windows 终端若显示乱码，先运行 `chcp 65001` 切换到 UTF-8

---

## 许可证 / License

MIT

---

Made with vibe coding by [QiYongchuan](https://github.com/QiYongchuan).
