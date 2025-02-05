import asyncio
import re
import requests
from telethon import TelegramClient, events
from telethon.sessions import StringSession

# 配置信息
API_ID = 9269545
API_HASH = "5fa82903cf82b14e4e17c125a3a8bf80"
SESSION_STRING = (
    "1AZWarzsBu5Qb4V8qYzUo3xyJllH1X4meBDxMqCCGLlBy74KjxHMBwdgF9q76vbuD32yqTpyYvopSe3w03mEdBdN0Gwb7bNZ4AdXkMkrvsd-B5FUrhSESLA6cUsmdha58qxuBs77CcsU8E1w9Z5n9B_P2UVxpihMii-6-LF-dA8ZPQcN30de6eF-XZzv015ShjxkjH86js7bOWC72GoXI24kax8Ub2Uw-SPSNW8_27myMxFlftf0v8Y7o_Kb3QIaKTvsRArIztBrVfiUduJm-HaCFPOjKuV7WtqaLR9SNZvW8SEr1wYqqsvpUNuhKq21eaRLaHMKL1orRroKEOvvviuyzVUem8q4="
)

# Telegram 群组 ID
GROUP_ID = -1002273543161

# 转发消息的 API 接口地址
API_URL = "http://111.231.26.210:7755/qianxun/httpapi?wxid=wxid_5du2b25cz8jx22"

client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)


def process_message(text: str):
    # 按行分割，过滤空行
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    
    # 检查是否为多信号Call格式（包含关键词“多信号Call”）
    if any("多信号Call" in line for line in lines):
        # 使用字典保存所需字段
        data = {
            "header": "",       # 多信号Call（通常第一行）
            "signal_qty": "",
            "name": "",
            "address": "",
            "call_source": "",
            "market_cap": "",
            "liquidity": ""
        }
        for line in lines:
            if "多信号Call" in line:
                data["header"] = "⚠️多信号Call,"
            elif line.startswith("信号数量:"):
                data["signal_qty"] = line
            elif line.startswith("代币名称:"):
                data["name"] = line
            elif line.startswith("代币地址:"):
                data["address"] = line
            elif line.startswith("⭐️ Call信号源:"):
                data["call_source"] = line
            elif line.startswith("📊市值:"):
                data["market_cap"] = line.split(":", 1)[1].strip()
            elif line.startswith("💦流动性:"):
                data["liquidity"] = line.split(":", 1)[1].strip()
        # 构造最终输出内容
        final_lines = []
        if data["header"]:
            final_lines.append(data["header"])
        if data["signal_qty"]:
            final_lines.append(data["signal_qty"])
        if data["name"]:
            final_lines.append(data["name"])
        if data["address"]:
            final_lines.append(data["address"])
        if data["call_source"]:
            final_lines.append(data["call_source"])
        # 添加市值和流动性，各自独立为一行
        if data["market_cap"] and data["liquidity"]:
            final_lines.append(f"📊市值: {data['market_cap']}, 💦流动性: {data['liquidity']}")

        final_message = "\n".join(final_lines)
        address_message = data["address"].split(":", 1)[1].strip() if data["address"] else ""
        return final_message, address_message

    else:
        # 非多信号Call格式，按原先的字段规则进行解析
        data = {
            "name": "",
            "address": "",
            "chain": "",
            "source": "",
            "basic": "",
            "market_cap": "",
            "liquidity": "",
            "social": "",
            "risk": ""
        }
        for line in lines:
            if line.startswith("代币名称:"):
                data["name"] = line.split(":", 1)[1].strip()
            elif line.startswith("代币地址:"):
                data["address"] = line.split(":", 1)[1].strip()
            elif line.startswith("所在链:"):
                data["chain"] = line.split(":", 1)[1].strip()
            elif line.startswith("报警来源:"):
                data["source"] = line.split(":", 1)[1].strip()
            elif line.startswith("基本信息:"):
                data["basic"] = line.split(":", 1)[1].strip()
            elif line.startswith("📊市值:"):
                data["market_cap"] = line.split(":", 1)[1].strip()
            elif line.startswith("💦流动性:"):
                data["liquidity"] = line.split(":", 1)[1].strip()
            elif line.startswith("💬官方社交:"):
                data["social"] = line.split(":", 1)[1].strip()
            elif line.startswith("🔐代币风险项检测:"):
                data["risk"] = line.split(":", 1)[1].strip()
        
        # 构造最终消息内容
        final_lines = []
        if data["name"]:
            final_lines.append(f"代币名称: {data['name']}")
        if data["address"]:
            final_lines.append(f"代币地址: {data['address']}")
        if data["source"]:
            final_lines.append(f"报警来源: {data['source']}")
        if data["social"]:
            final_lines.append(f"💬官方社交: {data['social']}")
        if data["market_cap"] and data["liquidity"]:
            final_lines.append(f"📊市值: {data['market_cap']}, 💦流动性: {data['liquidity']}")
        
        final_message = "\n".join(final_lines)
        address_message = data["address"]
        return final_message, address_message


@client.on(events.NewMessage(chats=GROUP_ID))
async def new_message_handler(event):
    """
    监听群组新消息，进行格式处理后调用 API 转发消息。
    同时单独转发代币地址。
    """
    raw_text = event.message.message
    print("接收到新消息：", raw_text)
    
    # 对消息文本进行格式转换处理
    final_message, address_message = process_message(raw_text)
    print("转换后的消息：", final_message)
    print("单独代币地址：", address_message)
    
    # 构造发送 API 的公共数据
    common_payload = {
        "type": "sendText",
        "data": {
            "wxid": "50565759304@chatroom"
        }
    }
    
    # 第一次调用：转发处理后的完整消息
    payload_full = common_payload.copy()
    payload_full["data"]["msg"] = final_message
    try:
        response_full = requests.post(API_URL, json=payload_full)
        print("转发完整消息，API返回：", response_full.text)
    except Exception as e:
        print("调用 API 转发完整消息时发生异常：", e)
    
    # 第二次调用：单独转发代币地址（如果存在）
    if address_message:
        payload_address = common_payload.copy()
        payload_address["data"]["msg"] = address_message
        try:
            response_addr = requests.post(API_URL, json=payload_address)
            print("转发代币地址，API返回：", response_addr.text)
        except Exception as e:
            print("调用 API 转发代币地址时发生异常：", e)


async def main():
    print("开始监听 Telegram 群组的消息...")
    await client.run_until_disconnected()


if __name__ == '__main__':
    client.start()
    client.loop.run_until_complete(main())