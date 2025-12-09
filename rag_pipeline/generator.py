# generator.py
from typing import List, Dict, Any, Optional
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline,
    StoppingCriteria,
    StoppingCriteriaList
)
import logging
from config import Config

logger = logging.getLogger(__name__)


class StopOnTokens(StoppingCriteria):
    """自定义停止条件"""

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        stop_ids = [self.tokenizer.eos_token_id]
        for stop_id in stop_ids:
            if input_ids[0][-1] == stop_id:
                return True
        return False


class ResponseGenerator:
    """响应生成器"""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or Config.GENERATION_MODEL
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        logger.info(f"加载生成模型: {self.model_name} (设备: {self.device})")

        # 加载tokenizer和模型
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None
        )

        # 设置填充token（如果需要）
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # 获取模型最大序列长度
        self.max_model_length = self.model.config.max_position_embeddings if hasattr(self.model.config, 'max_position_embeddings') else 1024

        logger.info("生成模型加载完成")

    def generate(
            self,
            prompt: str,
            max_length: int = None,
            temperature: float = None,
            top_p: float = None,
            do_sample: bool = True,
            num_return_sequences: int = 1
    ) -> str:
        """生成响应"""

        max_length = max_length or Config.MAX_NEW_TOKENS
        temperature = temperature or Config.TEMPERATURE
        top_p = top_p or Config.TOP_P

        # 编码输入
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
        ).to(self.device)
        
        # 确保输入不会超过模型的最大长度
        input_ids = inputs["input_ids"]
        if input_ids.shape[1] > self.max_model_length - max_length:
            # 截断输入以适应模型限制
            max_input_length = self.max_model_length - max_length
            input_ids = input_ids[:, -max_input_length:]
            inputs["input_ids"] = input_ids
            inputs["attention_mask"] = inputs["attention_mask"][:, -max_input_length:]

        # 生成参数
        generation_config = {
            "max_new_tokens": min(max_length, self.max_model_length - input_ids.shape[1]),
            "temperature": temperature,
            "top_p": top_p,
            "do_sample": do_sample,
            "num_return_sequences": num_return_sequences,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }

        # 生成文本
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                **generation_config
            )

        # 解码输出
        generated_text = self.tokenizer.decode(
            outputs[0][len(inputs["input_ids"][0]):],
            skip_special_tokens=True
        )

        return generated_text.strip()

    def generate_with_context(
            self,
            query: str,
            contexts: List[str],
            prompt_template: str = None
    ) -> Dict[str, Any]:
        """基于上下文生成响应"""

        prompt_template = prompt_template or Config.RAG_PROMPT_TEMPLATE

        # 合并上下文
        context_text = "\n\n".join([
            f"[上下文 {i + 1}]: {ctx}"
            for i, ctx in enumerate(contexts)
        ])

        # 构建prompt
        prompt = prompt_template.format(
            context=context_text,
            question=query
        )

        logger.info(f"生成提示词长度: {len(prompt)} 字符")
        logger.info(f"生成提示词: {prompt}")

        # 生成响应
        response = self.generate(prompt)

        # 提取引用信息
        citations = []
        for i, ctx in enumerate(contexts):
            citations.append({
                "source_id": i,
                "content_preview": ctx[:100] + "...",
                "relevance_score": None  # 可以在这里添加相关性分数
            })

        return {
            "query": query,
            "response": response,
            "contexts_used": len(contexts),
            "citations": citations,
            "prompt_length": len(prompt),
            "response_length": len(response)
        }