#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Suggest 联想词抓取脚本
用途：输入一个种子词，自动遍历 a-z 获取 Google 搜索框联想词
数据来源：https://suggestqueries.google.com/complete/search?client=firefox&q=关键词
"""

import argparse
import csv
import json
import random
import sys
import time
from datetime import datetime
from urllib.parse import quote_plus

import requests


# Windows 终端默认 GBK，强制 UTF-8 输出避免乱码
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


DEFAULT_SEED = "build a soccer squad"
ALPHABET = "abcdefghijklmnopqrstuvwxyz"
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0",
]


def fetch_suggestions(keyword: str, timeout: int = 10, max_retries: int = 2) -> list[str]:
    """
    请求 Google Suggest API，返回联想词列表。
    遇到网络/SSL/超时错误会自动重试。
    """
    url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={quote_plus(keyword)}"
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            data = response.json()
            # Google 返回格式：[原始查询, [建议1, 建议2, ...], ...]
            suggestions = data[1] if len(data) > 1 and isinstance(data[1], list) else []
            return [s.strip() for s in suggestions if s.strip()]
        except requests.exceptions.Timeout:
            last_error = "timeout"
            print(f"  [WARN] 超时 (尝试 {attempt + 1}/{max_retries + 1}): {keyword}")
        except requests.exceptions.SSLError as e:
            last_error = f"ssl_error: {e}"
            print(f"  [WARN] SSL 错误 (尝试 {attempt + 1}/{max_retries + 1}): {keyword}")
        except requests.exceptions.RequestException as e:
            last_error = f"request_error: {e}"
            print(f"  [WARN] 请求失败 (尝试 {attempt + 1}/{max_retries + 1}): {keyword} -> {e}")
        except (json.JSONDecodeError, IndexError, ValueError) as e:
            print(f"  [WARN] 解析失败: {keyword} -> {e}")
            return []

        if attempt < max_retries:
            time.sleep(1.0)

    if last_error:
        print(f"  [SKIP] 最终失败: {keyword} ({last_error})")
    return []


def collect_suggestions(seed: str, delay_range: tuple[float, float] = (0.3, 0.8)) -> dict[str, list[str]]:
    """
    对种子词遍历 a-z，分别获取联想词
    返回: {查询词: [联想词列表]}
    """
    results: dict[str, list[str]] = {}
    queries = [seed] + [f"{seed} {char}" for char in ALPHABET]

    print(f"\n[SEED] 种子词: {seed}")
    print(f"[INFO] 准备查询 {len(queries)} 个关键词...\n")

    for idx, query in enumerate(queries, start=1):
        print(f"[{idx}/{len(queries)}] 查询: {query!r}")
        suggestions = fetch_suggestions(query)
        if suggestions:
            results[query] = suggestions
            print(f"  [OK] 获取 {len(suggestions)} 条")
        else:
            print(f"  [SKIP] 无结果")

        # 防止请求过快被限制，最后一轮不 sleep
        if idx < len(queries):
            sleep_time = random.uniform(*delay_range)
            time.sleep(sleep_time)

    return results


def deduplicate_all(results: dict[str, list[str]]) -> list[str]:
    """
    所有联想词去重，保持原始顺序
    """
    seen = set()
    unique = []
    for suggestions in results.values():
        for s in suggestions:
            if s.lower() not in seen:
                seen.add(s.lower())
                unique.append(s)
    return unique


def save_results(results: dict[str, list[str]], unique: list[str], seed: str, output_prefix: str):
    """
    保存为 JSON 和 CSV
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_seed = "".join(c if c.isalnum() else "_" for c in seed).strip("_")[:50]
    json_path = f"{output_prefix}_{safe_seed}_{timestamp}.json"
    csv_path = f"{output_prefix}_{safe_seed}_{timestamp}.csv"

    # JSON：包含原始分组和去重后的结果
    payload = {
        "seed": seed,
        "created_at": datetime.now().isoformat(),
        "total_queries": len(results),
        "total_unique_suggestions": len(unique),
        "by_query": results,
        "unique_suggestions": unique,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    # CSV：每行一个去重后的联想词
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["keyword"])
        for keyword in unique:
            writer.writerow([keyword])

    print(f"\n[SAVE] 结果已保存:")
    print(f"   JSON: {json_path}")
    print(f"   CSV:  {csv_path}")
    return json_path, csv_path


def main():
    parser = argparse.ArgumentParser(
        description="Google Suggest 联想词抓取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例: python google_suggest_scraper.py -s \"build a soccer squad\"",
    )
    parser.add_argument(
        "-s", "--seed",
        type=str,
        default=DEFAULT_SEED,
        help=f"种子关键词（默认: {DEFAULT_SEED!r}）",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="google_suggest",
        help="输出文件名前缀（默认: google_suggest）",
    )
    parser.add_argument(
        "--min-delay",
        type=float,
        default=0.3,
        help="请求间隔最小秒数（默认: 0.3）",
    )
    parser.add_argument(
        "--max-delay",
        type=float,
        default=0.8,
        help="请求间隔最大秒数（默认: 0.8）",
    )

    args = parser.parse_args()

    results = collect_suggestions(args.seed, delay_range=(args.min_delay, args.max_delay))
    unique = deduplicate_all(results)

    print("\n" + "=" * 50)
    print(f"[SUMMARY] 查询完成: {len(results)} 个关键词")
    print(f"[SUMMARY] 去重后共 {len(unique)} 条联想词")
    print("=" * 50)

    if unique:
        print("\n[TOP 20] 前 20 条联想词预览:")
        for idx, kw in enumerate(unique[:20], start=1):
            print(f"   {idx}. {kw}")

        save_results(results, unique, args.seed, args.output)
    else:
        print("\n[WARN] 没有获取到任何联想词，可能是网络问题或被限制了。")


if __name__ == "__main__":
    main()
