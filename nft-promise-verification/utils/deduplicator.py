"""
去重逻辑模块

实现承诺数据的去重功能
- 完全相同文本合并
- 语义相似度 >0.9 合并
- 记录多来源信息
"""
from typing import List, Dict, Tuple
from difflib import SequenceMatcher
import structlog

logger = structlog.get_logger(__name__)


class Deduplicator:
    """去重器"""

    def __init__(self, similarity_threshold: float = 0.9):
        """
        初始化去重器

        Args:
            similarity_threshold: 语义相似度阈值（0-1）
        """
        self.similarity_threshold = similarity_threshold

    def deduplicate_promises(
        self,
        promises: List[Dict]
    ) -> List[Dict]:
        """
        对承诺列表进行去重

        Args:
            promises: 承诺列表

        Returns:
            去重后的承诺列表（新对象）
        """
        if not promises:
            return []

        logger.info(
            "开始去重",
            input_count=len(promises)
        )

        # 第一步: 完全相同文本合并
        exact_deduped = self._deduplicate_exact(promises)

        # 第二步: 语义相似度合并
        semantic_deduped = self._deduplicate_semantic(exact_deduped)

        logger.info(
            "去重完成",
            input_count=len(promises),
            output_count=len(semantic_deduped),
            removed_count=len(promises) - len(semantic_deduped)
        )

        return semantic_deduped

    def _deduplicate_exact(self, promises: List[Dict]) -> List[Dict]:
        """完全相同文本去重"""
        content_map = {}

        for promise in promises:
            content = promise.get("content", "").strip()

            if not content:
                continue

            if content in content_map:
                # 合并来源信息
                existing = content_map[content]
                existing = self._merge_sources(existing, promise)
                content_map[content] = existing
            else:
                # 初始化 sources 列表
                promise_copy = promise.copy()
                source_metadata = promise.get("metadata", {}) or {}
                if promise.get("source_id"):
                    source_metadata = {
                        **source_metadata,
                        "source_id": promise.get("source_id", "")
                    }
                promise_copy["sources"] = [{
                    "source_type": promise.get("source_type", ""),
                    "source_url": promise.get("source_url", ""),
                    "source_id": promise.get("source_id", ""),
                    "created_at": promise.get("created_at", ""),
                    "metadata": source_metadata
                }]
                content_map[content] = promise_copy

        return list(content_map.values())

    def _deduplicate_semantic(self, promises: List[Dict]) -> List[Dict]:
        """语义相似度去重"""
        if len(promises) <= 1:
            return promises

        # 使用简单的字符串相似度算法
        # 在生产环境中可以使用更复杂的语义相似度模型
        deduplicated = []
        processed_indices = set()

        for i, promise1 in enumerate(promises):
            if i in processed_indices:
                continue

            content1 = promise1.get("content", "").strip()
            merged_promise = promise1.copy()

            for j, promise2 in enumerate(promises[i + 1:], start=i + 1):
                if j in processed_indices:
                    continue

                content2 = promise2.get("content", "").strip()
                similarity = self._calculate_similarity(content1, content2)

                if similarity >= self.similarity_threshold:
                    # 合并相似承诺
                    merged_promise = self._merge_sources(
                        merged_promise,
                        promise2
                    )
                    processed_indices.add(j)

            deduplicated.append(merged_promise)
            processed_indices.add(i)

        return deduplicated

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度

        使用 SequenceMatcher 算法
        在生产环境中可以替换为更复杂的语义相似度模型
        """
        if not text1 or not text2:
            return 0.0

        return SequenceMatcher(None, text1, text2).ratio()

    def _merge_sources(
        self,
        promise1: Dict,
        promise2: Dict
    ) -> Dict:
        """
        合并两个承诺的来源信息

        Args:
            promise1: 第一个承诺（保留其内容）
            promise2: 第二个承诺（合并其来源）

        Returns:
            合并后的承诺（新对象）
        """
        merged = promise1.copy()

        # 确保 sources 列表存在
        if "sources" not in merged:
            merged["sources"] = [{
                "source_type": promise1.get("source_type", ""),
                "source_url": promise1.get("source_url", ""),
                "source_id": promise1.get("source_id", ""),
                "created_at": promise1.get("created_at", ""),
            }]

        # 添加第二个承诺的来源
        source2_metadata = promise2.get("metadata", {}) or {}
        if promise2.get("source_id"):
            source2_metadata = {
                **source2_metadata,
                "source_id": promise2.get("source_id", "")
            }
        source2 = {
            "source_type": promise2.get("source_type", ""),
            "source_url": promise2.get("source_url", ""),
            "source_id": promise2.get("source_id", ""),
            "created_at": promise2.get("created_at", ""),
            "metadata": source2_metadata
        }

        # 避免重复添加相同来源
        if source2 not in merged["sources"]:
            merged["sources"].append(source2)

        # 更新置信度（取最高值）
        merged["confidence"] = max(
            merged.get("confidence", 0.0),
            promise2.get("confidence", 0.0)
        )

        return merged
