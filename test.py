"""
定时批量发送 HTTP 请求脚本
- 支持指定精确时间触发
- fire-and-forget 并行发送，不等待响应
- 支持配置总发送次数
"""

import time
import requests
import threading
from datetime import datetime


# ========================== 配置区 ==========================

# 1. 定时触发时间（格式: YYYY-MM-DD HH:MM:SS）
SCHEDULED_TIME = "2026-03-07 13:25:45"

# 2. 发送总次数（同一个请求模板重复发送的次数）
TOTAL_SENDS = 10

# 3. 公共配置（所有请求共享的 headers / 凭证）
COMMON_HEADERS = {
    "service-game": "pubg",
    "service-lang": "zh-cn",
    "service-namespace": "PUBG_OFFICIAL",
    "service-url": "https://www.pubg.com/zh-cn/events/redeem",
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiJ9.eyJwYXlsb2FkIjoieXkwNkMwU2ZNRzNFWkg2bzVtcmNKR3FodTFCczNJSks1QkJjSGtVenlMbkxnRCtYcTlSQ1dmV05CWSsvcXBFbVVnd1g2NGtYREE3dU9nMlNPdzVzRFZ6eVVYNUNZNjdoWTZzZVNPZCtqem1oQWN3RXI0M3h4UTJRaERDYmlEaHBTck83U0hHWGdsSzRSY25QMXo3WTU2ZEZ0UEhBZHFZUFpHN240eHNjQ3d5YjVFSG5vcTF6WG9LSTdIcUxMTUVhcitScDRKazE2R3NqZFVpbHdKdG1qeFh3blpUTSsrSFczWDJ5WlhDUnRGNmJWVVJvcmhBVnhleThNQ0hvWmxmS3NwNElFVTVKZkxXZHhyZjRHY1pwVzA5dnpWTVdndXEvS2FkRGFuZkFMUHRHM0RIYW0xeUkzM1c3SmhrNzdJZnRnZG8zVzdrc3ZiNXA4SGFZL3Y1elBwZE1OTHkzZ3hDV29DVmM3Tlk0ZGdnPSIsImlhdCI6MTc3Mjg2MDY1MCwiZXhwIjoxNzcyODY0MjUwfQ.mBHd-jGKQ-zPTXb8P6YA52aNl47O2aaVkd93vL1gmTk",
}

# 4. 请求模板
REQUEST_TEMPLATE = {
    "method": "POST",
    "url": "https://api-foc.krafton.com/redeem/v3/register",
    "json": {
        "lang": "zh-cn",
        "namespace": "PUBG_OFFICIAL",
        "platformType": "STEAM",
        "nickName": "gyjeoz6ppm",
        "redeemCode": "CHICKENPARTY9999",
    },
}

# 5. 请求超时（秒）
REQUEST_TIMEOUT = 30


# ========================== 核心逻辑 ==========================

def fire_request(index: int):
    """发送单个请求（fire-and-forget，在独立线程中运行）"""
    cfg = REQUEST_TEMPLATE
    method = cfg.get("method", "GET").upper()
    url = cfg.get("url", "")
    headers = {**COMMON_HEADERS, **cfg.get("headers", {})}

    try:
        resp = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=cfg.get("params"),
            json=cfg.get("json"),
            data=cfg.get("data"),
            timeout=REQUEST_TIMEOUT,
        )
        print(f"  [✓] #{index} -> {resp.status_code} {resp.text[:200]}")
    except Exception as e:
        print(f"  [✗] #{index} -> 错误: {e}")


def fire_all():
    """一次性并行启动所有请求线程，不等待结果"""
    print(f"\n🚀 并行发射 {TOTAL_SENDS} 个请求 (fire-and-forget)\n")

    threads = []
    for i in range(TOTAL_SENDS):
        t = threading.Thread(target=fire_request, args=(i,), daemon=True)
        threads.append(t)

    # 所有线程同时启动
    for t in threads:
        t.start()

    fired_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    print(f"✅ 已发射全部 {TOTAL_SENDS} 个线程 @ {fired_time}")
    print("⏳ 等待响应回调打印中...\n")

    # 等待所有线程结束（仅为了看到打印结果）
    for t in threads:
        t.join(timeout=REQUEST_TIMEOUT + 5)

    print(f"\n📊 全部完成。")


def wait_until_scheduled_time():
    """等待到指定时间"""
    target = datetime.strptime(SCHEDULED_TIME, "%Y-%m-%d %H:%M:%S")
    now = datetime.now()

    if target <= now:
        print(f"⚠️  指定时间 {SCHEDULED_TIME} 已过去，将立即执行。")
        return

    diff = (target - now).total_seconds()
    print(f"⏰ 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 目标时间: {SCHEDULED_TIME}")
    print(f"⏳ 等待 {diff:.1f} 秒 ({diff/60:.1f} 分钟)...\n")

    while True:
        now = datetime.now()
        remaining = (target - now).total_seconds()
        if remaining <= 0:
            break
        if remaining > 60:
            print(f"   剩余 {remaining:.0f} 秒...")
            time.sleep(min(remaining - 1, 30))
        elif remaining > 5:
            time.sleep(min(remaining - 1, 5))
        else:
            time.sleep(remaining)
            break

    print(f"⏰ 时间到！当前: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# ========================== 入口 ==========================

if __name__ == "__main__":
    print("=" * 50)
    print("   定时批量 HTTP 请求发送器 (Fire-and-Forget)")
    print("=" * 50)
    print(f"   总发送次数: {TOTAL_SENDS}")
    print("=" * 50)

    wait_until_scheduled_time()
    fire_all()