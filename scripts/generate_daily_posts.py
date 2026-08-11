from __future__ import annotations

import argparse
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


CHINA_TZ = timezone(timedelta(hours=8))
SITE_URL = "https://myanmarcasino.cloud/"
TL_SITE_URL = "https://tl8899.live/"
TL_BLOG_URL = "https://tl8899.live/blog/"
TL_CONTACT_URL = "https://tl8899.live/contact/"

GAMES = (
    {
        "slug": "baccarat",
        "name": "Baccarat",
        "zh": "百家乐",
        "guide": "baccarat-game/",
        "image": "baccarat-advanced-guide.svg",
        "rules_en": "Baccarat compares the Player and Banker hands. Cards 2–9 keep their value, 10/J/Q/K count as zero, A counts as one, and only the final digit of the total is used.",
        "rules_zh": "百家乐比较闲家与庄家的点数。2 至 9 按牌面计分，10、J、Q、K 计 0 点，A 计 1 点，总点数只保留个位数。",
    },
    {
        "slug": "dragon-tiger",
        "name": "Dragon Tiger",
        "zh": "龙虎",
        "guide": "dragon-tiger-game/",
        "image": "dragon-tiger-risk-guide.svg",
        "rules_en": "Dragon Tiger deals one card to Dragon and one to Tiger. The higher rank wins; Tie rules and payouts vary, so the live table rule panel matters.",
        "rules_zh": "龙虎由龙方和虎方各发一张牌，牌面较大者胜出。和局的结算与赔率可能不同，参与前应查看桌台规则。",
    },
    {
        "slug": "niu-niu",
        "name": "Niu Niu",
        "zh": "牛牛",
        "guide": "niu-niu-game/",
        "image": "niu-niu-hand-ranking-guide.svg",
        "rules_en": "Niu Niu uses five cards. Three cards should total a multiple of ten, while the remaining two determine the Niu value. Special hands and multipliers depend on the provider.",
        "rules_zh": "牛牛使用五张牌，其中三张牌组合为 10 的倍数，余下两张牌决定牛数。特殊牌型与倍数应以平台规则为准。",
    },
    {
        "slug": "sic-bo",
        "name": "Sic Bo",
        "zh": "骰宝",
        "guide": "articles/",
        "image": "dragon-tiger-risk-guide.svg",
        "rules_en": "Sic Bo uses three dice and offers bets on totals, combinations and specific results. Each bet type has a different probability and payout.",
        "rules_zh": "骰宝使用三颗骰子，可选择点数总和、组合或指定结果。不同投注项目的概率与赔率并不相同。",
    },
    {
        "slug": "blackjack",
        "name": "Blackjack",
        "zh": "二十一点",
        "guide": "articles/",
        "image": "baccarat-advanced-guide.svg",
        "rules_en": "Blackjack aims for a hand closer to 21 than the dealer without going over. Dealer rules, blackjack payouts, splitting and doubling rules vary by table.",
        "rules_zh": "二十一点的目标是在不爆牌的情况下比庄家更接近 21 点。庄家补牌、天然二十一点赔率、分牌及加倍规则可能因桌台而异。",
    },
)

ANGLES = (
    {
        "slug": "beginner-rules",
        "title": "Beginner rules to check before joining a table",
        "zh_title": "新手入桌前应确认的规则",
        "focus_en": "Start with the basic settlement rules. A familiar game name does not guarantee that every provider uses the same payout table or special-hand priority.",
        "focus_zh": "应先了解基本结算规则。即使游戏名称相同，不同平台的赔率表、特殊牌型顺序及结算方式也可能不同。",
    },
    {
        "slug": "table-limits",
        "title": "How to read table limits and stake ranges",
        "zh_title": "如何查看桌台限额与投注范围",
        "focus_en": "Check the minimum and maximum stake before entering. Side bets can have separate limits, and a fast table can make a session cost rise more quickly than expected.",
        "focus_zh": "进入桌台前应确认最低及最高投注额。附加投注可能有独立限额，快速桌也会令娱乐预算消耗得更快。",
    },
    {
        "slug": "payout-panel",
        "title": "A practical payout-panel reading checklist",
        "zh_title": "实用赔率表阅读清单",
        "focus_en": "Read the payout panel line by line, including commission, push and tie conditions. A larger headline payout usually comes with a lower probability or stricter condition.",
        "focus_zh": "应逐项阅读赔率表，包括佣金、和局及退回条件。较高的显示赔率通常代表较低概率或更严格的成立条件。",
    },
    {
        "slug": "common-mistakes",
        "title": "Common beginner mistakes and how to avoid them",
        "zh_title": "常见新手误区及避免方法",
        "focus_en": "Common mistakes include skipping the rules, increasing stakes after losses and treating recent results as a prediction. Each round remains uncertain.",
        "focus_zh": "常见误区包括忽略规则、输钱后提高投注额，以及把近期结果当成预测依据。每一局的结果仍具有不确定性。",
    },
    {
        "slug": "provider-differences",
        "title": "Why provider and table differences matter",
        "zh_title": "为什么平台与桌台差异很重要",
        "focus_en": "Compare game speed, dealing procedure, payout notes and special rules. Use the information panel for the exact table instead of relying on a rule summary from another provider.",
        "focus_zh": "应比较游戏速度、发牌流程、赔率说明及特别规则，并以当前桌台的信息面板为准，不要直接套用其他平台的规则。",
    },
    {
        "slug": "session-budget",
        "title": "Setting a session budget before play",
        "zh_title": "开始前如何设定单次预算",
        "focus_en": "Choose a fixed entertainment amount and a time limit before the session. Do not use money needed for bills, savings or debt payments, and never treat a game as income.",
        "focus_zh": "开始前应设定固定娱乐预算与时间限制，不应使用生活费、储蓄或还债资金，也不要把游戏视为收入来源。",
    },
    {
        "slug": "side-bet-risk",
        "title": "Understanding the extra risk in side bets",
        "zh_title": "了解附加投注的额外风险",
        "focus_en": "Side bets may look attractive because of their large payouts, but they normally depend on less frequent outcomes. Review the probability and settlement rule separately from the main game.",
        "focus_zh": "附加投注常以较高赔率吸引注意，但通常依赖较少出现的结果。应把它与主游戏分开评估，并查看概率与结算条件。",
    },
    {
        "slug": "game-speed",
        "title": "How game speed changes session risk",
        "zh_title": "游戏速度如何影响单次风险",
        "focus_en": "A small stake can still add up when rounds are fast. Estimate the number of rounds, use time reminders and pause before changing the planned stake.",
        "focus_zh": "即使单局金额较小，快速连续进行也可能累积较高支出。可预估局数、设置时间提醒，并在改变原定金额前暂停考虑。",
    },
    {
        "slug": "history-roadmaps",
        "title": "What result histories can and cannot tell you",
        "zh_title": "路单与历史结果可以说明什么",
        "focus_en": "History panels record previous outcomes; they do not make the next independent outcome predictable. Use them as records, not as a promise of a pattern.",
        "focus_zh": "历史面板只记录过去结果，并不能保证预测下一次独立结果。它适合作为记录工具，而不是趋势承诺。",
    },
    {
        "slug": "promotion-terms",
        "title": "Reading promotion terms before accepting a bonus",
        "zh_title": "接受优惠前应阅读哪些条款",
        "focus_en": "Check wagering requirements, eligible games, maximum stake, expiry and withdrawal conditions. A promotion is not useful when its conditions do not fit your planned play.",
        "focus_zh": "应查看流水要求、适用游戏、最高投注额、有效期及提款条件。如果条款不符合原定娱乐计划，优惠未必适合使用。",
    },
    {
        "slug": "stop-signals",
        "title": "Recognising practical signals to stop",
        "zh_title": "识别应该停止的实际信号",
        "focus_en": "Stop when the budget or time limit is reached, or when play affects mood, sleep, work or family. Taking a break is part of responsible entertainment.",
        "focus_zh": "当预算或时间达到上限，或娱乐开始影响情绪、睡眠、工作及家庭时，应立即停止。适时休息是理性娱乐的一部分。",
    },
    {
        "slug": "mobile-checklist",
        "title": "A mobile-player safety and rules checklist",
        "zh_title": "手机参与者的安全与规则清单",
        "focus_en": "Use a stable connection, keep account security enabled and avoid hurried decisions on a small screen. Reopen the rule panel whenever a table or provider changes.",
        "focus_zh": "应使用稳定网络、启用账户安全功能，并避免在小屏幕上仓促决定。更换桌台或平台后应重新打开规则说明。",
    },
)

RULE_TABLES = {
    "baccarat": (
        ("庄", "常见为较低优势选项，但可能采用佣金或免佣规则。"),
        ("闲", "流程直观，常见赔付为 1:1，仍应查看桌台说明。"),
        ("和", "显示赔率较高但出现频率较低，不应把高赔率理解为更容易出现。"),
    ),
    "dragon-tiger": (
        ("龙 / 虎", "双方各一张牌，比较牌面大小，A 通常最小、K 最大。"),
        ("和局", "赔率较高且波动较大，具体结算以当前桌台为准。"),
        ("节奏", "回合速度快，固定预算和时间限制尤其重要。"),
    ),
    "niu-niu": (
        ("三张成十", "先找三张点数合计为 10 的倍数的牌。"),
        ("牛数", "剩余两张牌的个位数用于判断牛一至牛牛。"),
        ("特殊牌型", "五花牛、炸弹等名称和倍数可能因平台而异。"),
    ),
    "sic-bo": (
        ("大 / 小", "先确认三颗骰子的点数范围及围骰例外规则。"),
        ("点数", "指定总点数的概率与赔率各不相同。"),
        ("围骰", "显示赔率通常较高，同时伴随更高波动。"),
    ),
    "blackjack": (
        ("要牌 / 停牌", "根据当前点数与庄家明牌作决定，但结果仍不确定。"),
        ("分牌 / 加倍", "允许条件、投注限制与后续要牌规则因桌台而异。"),
        ("Blackjack 赔率", "先确认天然二十一点采用 3:2、6:5 或其他赔付。"),
    ),
}


def parse_day(value: str | None) -> date:
    return date.fromisoformat(value) if value else datetime.now(CHINA_TZ).date()


def render_post(
    day: date,
    game: dict[str, str],
    angle: dict[str, str],
    repository: str,
    sequence: int,
) -> str:
    image_url = f"https://raw.githubusercontent.com/{repository}/main/assets/{game['image']}"
    guide_url = f"{SITE_URL}{game['guide']}"
    title = f"腾龙公司：{game['zh']}｜{angle['zh_title']}（第{sequence}篇）"
    description = (
        f"{game['zh']}中文指南：{angle['zh_title']}，包含基础规则、桌台检查、新手误区与负责任娱乐提醒。"
    )
    table_rows = "\n".join(f"| {label} | {detail} |" for label, detail in RULE_TABLES[game["slug"]])
    keywords = "、".join(("腾龙公司", "TL8899 LIVE", game["zh"], "真人娱乐", "规则指南", "负责任娱乐"))
    return f"""<!--
title: {title}
description: {description}
date: {day.isoformat()}
language: zh-CN
-->

# {title}

**{game['name']} Rules & Responsible Play Guide**

**发布日期：** {day.isoformat()}（Asia/Shanghai）
**主题：** {game['zh']} / {game['name']} · 腾龙公司 TL8899 LIVE

![{title} 真人娱乐规则配图]({image_url})

> **负责任娱乐提示：** 本文仅供成年人了解规则与风险，不承诺盈利，不提供保证结果的方法，也不建议追亏或冲动加注。

## 内容摘要

{description} 即使游戏名称相同，不同平台的赔率、限额和特殊规则也可能不同，参与前应以当前桌台的信息面板为准。

## {game['zh']}玩法重点

{game['rules_zh']}

| 项目 | 说明 |
| --- | --- |
{table_rows}

详细规则可以继续阅读 [{game['zh']}规则指南]({guide_url})，并在实际桌台重新确认赔付、限额和供应商差异。

## 今日主题：{angle['zh_title']}

{angle['focus_zh']}

### 新手检查清单

- 先打开桌台信息，确认赔率、限额及特别规则。
- 第一局开始前设定娱乐预算与时间上限。
- 不追损、不因压力提高投注额，也不要把历史结果当成预测。
- 达到原定限制后立即停止。

## 搜索标签

{keywords}。关键词用于内容分类与搜索发现，本站不声明与其他品牌存在官方关系。

## English summary

**{game['name']} — {angle['title']}**

{game['rules_en']} {angle['focus_en']} Always check the live provider rule panel, set a budget and time limit, and stop when play no longer feels controlled.

## 相关页面

- [TL8899 LIVE 中文文章]({TL_BLOG_URL})
- [腾龙公司首页]({TL_SITE_URL})
- [联系方式]({TL_CONTACT_URL})
- [Myanmar Casino Guide 规则资料]({SITE_URL})

---

**18+ Responsible notice / 理性娱乐提醒：** Gambling outcomes are uncertain. Follow local laws and platform terms, never treat games as income, and stop if play affects sleep, work, health or family. / 游戏结果具有不确定性，请遵守当地法律与平台条款，切勿把游戏当作收入来源；如娱乐影响睡眠、工作、健康或家庭，应立即停止。
"""


def generate_posts(output_root: Path, day: date, count: int, repository: str) -> list[Path]:
    posts_dir = output_root / "posts"
    posts_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    day_offset = day.toordinal()
    existing = sorted(posts_dir.glob(f"{day.isoformat()}-*.md"))
    missing = max(0, count - len(existing))
    slot = len(existing)

    while len(created) < missing:
        game = GAMES[slot % len(GAMES)]
        cycle = slot // len(GAMES)
        angle = ANGLES[(day_offset + slot * 3 + cycle) % len(ANGLES)]
        path = posts_dir / f"{day.isoformat()}-{game['slug']}-{angle['slug']}.md"
        slot += 1
        if path.exists():
            continue
        with path.open("w", encoding="utf-8", newline="\n") as file:
            file.write(render_post(day, game, angle, repository, len(existing) + len(created) + 1))
        created.append(path)
        print(f"Created: {path.as_posix()}")

    if not created:
        print(f"Complete: {day.isoformat()} already has {len(existing)} post(s).")
    return created


def iter_days(start: date, end: date):
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate idempotent daily responsible-play Markdown posts.")
    parser.add_argument("--count", type=int, default=5, help="Number of posts to create (1-10).")
    parser.add_argument("--date", help="China-local publication date in YYYY-MM-DD format; defaults to today.")
    parser.add_argument("--start-date", help="First date to backfill in YYYY-MM-DD format.")
    parser.add_argument("--end-date", help="Last date to backfill in YYYY-MM-DD format.")
    parser.add_argument("--output-root", type=Path, default=Path.cwd(), help="Repository root containing posts/.")
    args = parser.parse_args()

    if not 1 <= args.count <= 10:
        parser.error("--count must be between 1 and 10")

    if bool(args.start_date) != bool(args.end_date):
        parser.error("--start-date and --end-date must be used together")
    if args.date and args.start_date:
        parser.error("--date cannot be combined with --start-date/--end-date")

    repository = os.environ.get("GITHUB_REPOSITORY", "andrewjack00007-pixel/my-content-repo")
    output_root = args.output_root.resolve()
    if args.start_date:
        start = parse_day(args.start_date)
        end = parse_day(args.end_date)
        if start > end:
            parser.error("--start-date must not be later than --end-date")
        days = iter_days(start, end)
    else:
        days = (parse_day(args.date),)

    total = 0
    for day in days:
        total += len(generate_posts(output_root, day, args.count, repository))
    print(f"Done: {total} new Chinese-first post(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
