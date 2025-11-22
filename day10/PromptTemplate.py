import dataclasses
from typing import List

from transformers import pipeline


@dataclasses.dataclass
class PromptTemplate:
    template : str
    input_variables : List[str]

    def format(self, **kwargs) -> str:
        missing = [var for var in self.input_variables if var not in kwargs]
        if missing:
            raise ValueError(f"Missing variables: {missing}")
        return self.template.format(**kwargs)

template_str = """
你是一名{role}。
任务:
-阅读下面的文本，并从一下标签中选择一个最合适的类别：
{labels}
要求：
1. 先在心里推理原因，但不要写出来。
2. 最终只输出一个标签名称。

文本内容：
{text}
"""

prompt = PromptTemplate(
    template=template_str,
    input_variables=["role", "labels", "text"],
)

filled = prompt.format(
    role="资深工控安全分析专家",
    labels="正常的业务流量，设备维护，故障诊断，可以攻击行为",
    text="在非生产时间段出现大量来自外部 IP 的写寄存器指令。",
)

print(filled)

def main():
    common_text = pipeline("text-generation", model="gpt2")
    # 2. 调用生成
    # max_new_tokens: 限制生成的长度
    # do_sample=True: 允许有一定的随机性
    result = common_text(filled,max_new_tokens=500,do_sample=True)
    print("prompt Result:")
    print(result)

if __name__ == "__main__":
    main()
