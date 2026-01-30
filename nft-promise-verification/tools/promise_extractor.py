"""
承诺提取工具

使用 LLM Few-Shot Prompting 从文本中提取项目承诺
输出 JSON 格式的结构化承诺数据
"""
import json
from typing import List, Dict, Optional
import structlog

logger = structlog.get_logger(__name__)


class PromiseExtractor:
    """承诺提取器"""

    def __init__(self, llm_manager):
        """
        初始化承诺提取器

        Args:
            llm_manager: LLM 管理器实例（来自 llm_config.py）
        """
        self.llm_manager = llm_manager

    def extract_promises(
        self,
        text: str,
        source_type: str,
        source_url: str,
        confidence_threshold: float = 0.7
    ) -> List[Dict]:
        """
        从文本中提取承诺

        Args:
            text: 输入文本（推文或网页内容）
            source_type: 来源类型 (twitter, website, whitepaper)
            source_url: 来源 URL
            confidence_threshold: 置信度阈值（0-1）

        Returns:
            承诺列表，每个承诺包含 content, category, confidence, source 等字段

        Raises:
            ValueError: 输入无效
            RuntimeError: 提取失败
        """
        if not text or not text.strip():
            raise ValueError("输入文本不能为空")

        if source_type not in ["twitter", "website", "whitepaper"]:
            raise ValueError(
                f"不支持的来源类型: {source_type}. "
                "支持的类型: twitter, website, whitepaper"
            )

        logger.info(
            "开始提取承诺",
            source_type=source_type,
            text_length=len(text)
        )

        try:
            # 构建 Few-Shot Prompt
            prompt = self._build_extraction_prompt(text, source_type)

            # 调用 LLM
            response = self.llm_manager.generate(
                prompt=prompt,
                temperature=0.3,  # 低温度以获得更确定的输出
                max_tokens=2000
            )

            # 解析 JSON 响应
            promises = self._parse_llm_response(
                response,
                source_url,
                confidence_threshold
            )

            logger.info(
                "承诺提取完成",
                source_type=source_type,
                promises_count=len(promises)
            )

            return promises

        except Exception as e:
            error_msg = f"提取承诺失败: {str(e)}"
            logger.error(
                error_msg,
                source_type=source_type,
                error=str(e)
            )
            raise RuntimeError(error_msg) from e

    def _build_extraction_prompt(
        self,
        text: str,
        source_type: str
    ) -> str:
        """构建 Few-Shot Prompt"""
        # Few-Shot 示例
        examples = """
示例 1:
输入: "We will launch our NFT collection on Ethereum mainnet in Q2 2024"
输出: {
  "promises": [
    {
      "content": "在 2024 年 Q2 在以太坊主网上线 NFT 系列",
      "category": "product_launch",
      "confidence": 0.95,
      "deadline": "2024-Q2",
      "verifiable": true
    }
  ]
}

示例 2:
输入: "Our team is committed to building the best community in Web3"
输出: {
  "promises": [
    {
      "content": "构建 Web3 中最好的社区",
      "category": "community",
      "confidence": 0.6,
      "deadline": null,
      "verifiable": false
    }
  ]
}

示例 3:
输入: "10% of mint proceeds will go to charity"
输出: {
  "promises": [
    {
      "content": "将 10% 的铸造收益捐赠给慈善机构",
      "category": "financial",
      "confidence": 0.9,
      "deadline": null,
      "verifiable": true
    }
  ]
}
"""

        prompt = f"""你是一个专业的 NFT 项目承诺提取器。请从以下文本中提取所有项目承诺。

承诺类别:
- product_launch: 产品发布承诺
- feature: 功能特性承诺
- financial: 财务相关承诺
- community: 社区建设承诺
- partnership: 合作伙伴承诺
- roadmap: 路线图承诺
- other: 其他承诺

{examples}

现在请提取以下文本中的承诺（来源类型: {source_type}）:

{text}

请以 JSON 格式输出，包含 promises 数组。每个承诺必须包含:
- content: 承诺内容（中文）
- category: 承诺类别
- confidence: 置信度（0-1）
- deadline: 截止时间（如果有）
- verifiable: 是否可验证（布尔值）

只输出 JSON，不要包含其他文字。
"""
        return prompt

    def _parse_llm_response(
        self,
        response: str,
        source_url: str,
        confidence_threshold: float
    ) -> List[Dict]:
        """解析 LLM 响应"""
        try:
            # 提取 JSON 部分
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            # 解析 JSON
            data = json.loads(response)
            promises = data.get("promises", [])

            # 过滤低置信度承诺并添加来源信息
            filtered_promises = []
            for promise in promises:
                if promise.get("confidence", 0) >= confidence_threshold:
                    promise["source_url"] = source_url
                    filtered_promises.append(promise)

            return filtered_promises

        except json.JSONDecodeError as e:
            logger.error(
                "解析 LLM 响应失败",
                response=response[:200],
                error=str(e)
            )
            return []

        except Exception as e:
            logger.error(
                "处理 LLM 响应失败",
                error=str(e)
            )
            return []
