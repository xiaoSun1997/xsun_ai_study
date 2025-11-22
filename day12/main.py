from typing import final

from llm_client import LLMClient

API_KEY = "sk-6a2ef267de654bd8b26500d8bd3a5f9b"

bot = LLMClient(API_KEY,"qwen-plus", "https://dashscope.aliyuncs.com/compatible-mode/v1",0.7)

print("--普通对话--")
answer = bot.chat("你叫什么名字,你能干什么？解释一下冬天为什么这么冷？")
print("AI ans:",answer)

# --- 场景 B: 结合 Few-shot CoT (day11) ---
print("--- Few-shot CoT 推理 ---")

# 定义系统提示词
sys_prompt = "你是一个逻辑严密的数学助手，请按照示例的思维过程进行回答。"

# 定义 Few-shot 历史 (作为 history 传入)
few_shot_examples = [
    {"role": "user", "content": "小红有 2 个咕噜币，能换多少硬币？(1咕噜=3咔嚓, 1咔嚓=5硬币, >5咕噜奖励10硬币)"},
    {"role": "assistant",
     "content": "思维过程：\n1. 2咕噜 * 3 = 6咔嚓\n2. 6咔嚓 * 5 = 30硬币\n3. 2咕噜<5，无奖励。\n答案：30硬币"},
    {"role": "user", "content": "大壮有 10 个咕噜币，能换多少硬币？"},
    {"role": "assistant",
     "content": "思维过程：\n1. 10咕噜 * 3 = 30咔嚓\n2. 30咔嚓 * 5 = 150硬币\n3. 10咕噜>5，奖励10硬币。\n4. 150+10=160。\n答案：160硬币"}
]

user_question = "小明有 6 个咕噜币，能换多少硬币？"

final_answer = bot.chat(user_question, sys_prompt, few_shot_examples)
print("AI ans:",final_answer)

print("--- 普通对话 流式输出 ---")
for chunk in bot.chat_stream("你叫什么名字,你能干什么？解释一下冬天为什么这么冷？"):
    print(chunk, end="", flush=True)

