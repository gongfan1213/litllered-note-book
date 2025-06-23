"""
LLM客户端 - 小红书起号助手
"""
import asyncio
from typing import Dict, Any, Optional, List
from langchain_core.language_models import BaseLLM
from langchain_openai import ChatOpenAI
from config import config
from models import ModelConfig

class LLMClient:
    """LLM客户端管理器"""
    
    def __init__(self):
        self._clients: Dict[str, BaseLLM] = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """初始化各种LLM客户端"""
        # 使用新的LLM API配置
        llm_config = config.get_llm_config()
        
        # 默认模型 - Claude 3.5 Sonnet
        self._clients["default"] = ChatOpenAI(
            model=config.DEFAULT_MODEL,
            openai_api_base=llm_config["base_url"],
            openai_api_key=llm_config["api_key"],
            temperature=0.7,
            max_tokens=4000,
            timeout=llm_config["timeout"]
        )
        
        # 思考模型
        self._clients["thinking"] = ChatOpenAI(
            model=config.THINKING_MODEL,
            openai_api_base=llm_config["base_url"],
            openai_api_key=llm_config["api_key"],
            temperature=0.3,
            max_tokens=4400,
            timeout=llm_config["timeout"]
        )
        
        # 视觉模型
        self._clients["vision"] = ChatOpenAI(
            model=config.VISION_MODEL,
            openai_api_base=llm_config["base_url"],
            openai_api_key=llm_config["api_key"],
            temperature=0.7,
            max_tokens=4000,
            timeout=llm_config["timeout"]
        )
        
        # 为每个可用模型创建客户端
        for model_name in config.AVAILABLE_MODELS[:5]:  # 只创建前5个常用模型
            try:
                self._clients[model_name] = ChatOpenAI(
                    model=model_name,
                    openai_api_base=llm_config["base_url"],
                    openai_api_key=llm_config["api_key"],
                    temperature=0.7,
                    max_tokens=4000,
                    timeout=llm_config["timeout"]
                )
            except Exception as e:
                print(f"警告: 无法初始化模型 {model_name}: {e}")
    
    def get_client(self, model_name: str = "default") -> Optional[BaseLLM]:
        """获取指定的LLM客户端"""
        return self._clients.get(model_name, self._clients.get("default"))
    
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        return list(self._clients.keys())
    
    async def generate_text(
        self, 
        model_name: str = "default", 
        prompt: str = "", 
        model_config: Optional[ModelConfig] = None
    ) -> str:
        """生成文本"""
        client = self.get_client(model_name)
        if not client:
            raise ValueError(f"未找到模型: {model_name}")
        
        # 应用模型配置
        if model_config:
            if hasattr(client, 'temperature'):
                client.temperature = model_config.temperature
            if hasattr(client, 'max_tokens'):
                client.max_tokens = model_config.max_tokens
            if hasattr(client, 'max_output_tokens'):
                client.max_output_tokens = model_config.max_tokens
        
        try:
            # 使用asyncio运行同步的LLM调用
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: client.invoke(prompt)
            )
            return response.content
        except Exception as e:
            raise Exception(f"LLM调用失败 ({model_name}): {str(e)}")
    
    async def generate_with_system_prompt(
        self,
        model_name: str = "default",
        system_prompt: str = "",
        user_prompt: str = "",
        model_config: Optional[ModelConfig] = None
    ) -> str:
        """使用系统提示词生成文本"""
        from langchain_core.messages import SystemMessage, HumanMessage
        
        client = self.get_client(model_name)
        if not client:
            raise ValueError(f"未找到模型: {model_name}")
        
        # 应用模型配置
        if model_config:
            if hasattr(client, 'temperature'):
                client.temperature = model_config.temperature
            if hasattr(client, 'max_tokens'):
                client.max_tokens = model_config.max_tokens
            if hasattr(client, 'max_output_tokens'):
                client.max_output_tokens = model_config.max_tokens
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: client.invoke(messages)
            )
            return response.content
        except Exception as e:
            raise Exception(f"LLM调用失败 ({model_name}): {str(e)}")

# 全局LLM客户端实例
llm_client = LLMClient() 