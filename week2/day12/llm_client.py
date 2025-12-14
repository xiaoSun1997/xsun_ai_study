from typing import Optional, List, Dict, Generator

import openai
from openai import base_url
from pyexpat.errors import messages


class LLMClient:
    def __init__(self,
                 api_key: str,
                 model: str = "qwen-plus",
                 base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
                 temperature: float = 0.7):
        '''
        本处使用的是阿里云百炼平台千问模型 ，每个人注册都有免费额度，可以直接去开通一个进行编码测试
        :param api_key: API密钥
        :param model:
        :param base_url:
        :param temperature:
        '''
        self.client = openai.Client(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature

    def chat(self, prompt: str,
             system_prompt: str = "你是一个乐于助人的助手，请根据要求进行回复",
             history: Optional[List[Dict]] = None) -> str:
        '''
        :param prompt:用户的当前问题
        :param system_prompt:系统人设
        :param history:历史对话 （后续需要限制 最近多少条，否则token消耗的会很快）
        :return:
        '''
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        # 追加历史对话
        if history:
            messages.extend(history)

        # 追加当前用户的问题
        messages.append({"role": "user", "content": prompt})
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(e)
            raise Exception("请求失败")

    def set_model(self, model: str):
        """
        设置切换模型
        :param model:
        :return:
        """
        self.model = model

    def chat_stream(self, prompt: str,
                   system_prompt: str = "你是一个乐于助人的助手，请根据要求进行回复",
                   history: Optional[List[Dict]] = None) -> Generator[str, None, None]:
        """
        流式对话接口
       :return: 一个生成器，每次 yield 一个字符或片段
        """
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=self.temperature,
            )
            for chunk in response:
                yield chunk.choices[0].delta.content
        except Exception as e:
            print(e)
            raise Exception("请求失败")