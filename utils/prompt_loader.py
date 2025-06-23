"""
提示词加载器 - 小红书起号助手
"""
import os
from typing import Dict, Any
from pathlib import Path

class PromptLoader:
    """提示词加载器"""
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(prompts_dir)
        self._cache = {}
    
    def load_prompt(self, prompt_name: str) -> str:
        """加载提示词模板"""
        if prompt_name in self._cache:
            return self._cache[prompt_name]
        
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        if not prompt_file.exists():
            raise FileNotFoundError(f"提示词文件不存在: {prompt_file}")
        
        with open(prompt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self._cache[prompt_name] = content
        return content
    
    def format_prompt(self, prompt_name: str, **kwargs) -> str:
        """加载并格式化提示词"""
        template = self.load_prompt(prompt_name)
        return template.format(**kwargs)
    
    def get_available_prompts(self) -> list:
        """获取所有可用的提示词"""
        return [f.stem for f in self.prompts_dir.glob("*.txt")]

# 全局提示词加载器实例
prompt_loader = PromptLoader() 