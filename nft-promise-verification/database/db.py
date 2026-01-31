"""
数据库操作模块

提供数据库连接管理和 CRUD 操作
"""

import sqlite3
import json
from typing import Optional, List
from pathlib import Path
from contextlib import contextmanager

from database.models import (
    NFTProject,
    Promise,
    VerificationRecord,
    PrivacyStorageRecord
)


def get_db_path() -> str:
    """获取数据库文件路径"""
    db_dir = Path(__file__).parent
    return str(db_dir / "promise_breaker.db")


@contextmanager
def get_db_connection(db_path: str = None):
    """
    获取数据库连接上下文管理器

    Args:
        db_path: 数据库文件路径

    Yields:
        sqlite3.Connection: 数据库连接对象
    """
    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # 返回字典格式
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ==================== Project CRUD ====================

def create_project(project: NFTProject, db_path: str = None) -> str:
    """创建项目"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO projects (
                id, name, twitter_account, website_url,
                whitepaper_url, contract_address, github_repo,
                treasury_address, created_at, last_verified_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            project.id, project.name, project.twitter_account,
            str(project.website_url) if project.website_url else None,
            str(project.whitepaper_url) if project.whitepaper_url else None,
            project.contract_address, project.github_repo,
            project.treasury_address, project.created_at.isoformat(),
            project.last_verified_at.isoformat() if project.last_verified_at else None
        ))
        return project.id


def get_project(project_id: str, db_path: str = None) -> Optional[dict]:
    """获取项目"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def list_projects(limit: int = 100, offset: int = 0, db_path: str = None) -> List[dict]:
    """列出项目"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM projects ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        return [dict(row) for row in cursor.fetchall()]


# ==================== Promise CRUD ====================

def create_promise(promise: Promise, db_path: str = None) -> str:
    """创建承诺"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO promises (
                id, project_id, content, sources, promise_type,
                target_date, verification_status, importance_weight, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            promise.id, promise.project_id, promise.content,
            json.dumps([str(s) for s in promise.sources]),  # 将 HttpUrl 转换为字符串
            promise.promise_type.value,
            promise.target_date.isoformat() if promise.target_date else None,
            promise.verification_status.value,
            promise.importance_weight,
            promise.created_at.isoformat()
        ))
        return promise.id


def get_promise(promise_id: str, db_path: str = None) -> Optional[dict]:
    """获取承诺"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM promises WHERE id = ?", (promise_id,))
        row = cursor.fetchone()
        if row:
            result = dict(row)
            # 解析 JSON 字段
            if result.get("sources"):
                result["sources"] = json.loads(result["sources"])
            return result
        return None


def get_promises_by_project(
    project_id: str,
    db_path: str = None
) -> List[dict]:
    """获取项目的所有承诺"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM promises WHERE project_id = ? ORDER BY created_at DESC",
            (project_id,)
        )
        results = []
        for row in cursor.fetchall():
            result = dict(row)
            # 解析 JSON 字段
            if result.get("sources"):
                result["sources"] = json.loads(result["sources"])
            results.append(result)
        return results


def update_promise_verification_status(
    promise_id: str,
    status: str,
    db_path: str = None
) -> bool:
    """更新承诺的验证状态"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE promises SET verification_status = ? WHERE id = ?",
            (status, promise_id)
        )
        return cursor.rowcount > 0


# ==================== VerificationRecord CRUD ====================

def create_verification_record(
    record: VerificationRecord,
    db_path: str = None
) -> str:
    """创建验证记录"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO verification_records (
                id, project_id, verification_time, promise_breaking_index,
                integrity_score, fairness_score, activity_score,
                stability_score, momentum_score, total_promises,
                fulfilled_count, unfulfilled_count, unverifiable_count,
                report_details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.id, record.project_id,
            record.verification_time.isoformat(),
            record.promise_breaking_index,
            record.integrity_score, record.fairness_score,
            record.activity_score, record.stability_score,
            record.momentum_score, record.total_promises,
            record.fulfilled_count, record.unfulfilled_count,
            record.unverifiable_count,
            json.dumps(record.report_details.model_dump())
        ))
        return record.id


def get_verification_record(
    record_id: str,
    db_path: str = None
) -> Optional[dict]:
    """获取验证记录"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM verification_records WHERE id = ?",
            (record_id,)
        )
        row = cursor.fetchone()
        if row:
            result = dict(row)
            # 解析 JSON 字段
            if result.get("report_details"):
                result["report_details"] = json.loads(result["report_details"])
            return result
        return None


def get_verification_records_by_project(
    project_id: str,
    limit: int = 10,
    db_path: str = None
) -> List[dict]:
    """获取项目的验证记录历史"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM verification_records
            WHERE project_id = ?
            ORDER BY verification_time DESC
            LIMIT ?
        """, (project_id, limit))
        results = []
        for row in cursor.fetchall():
            result = dict(row)
            # 解析 JSON 字段
            if result.get("report_details"):
                result["report_details"] = json.loads(result["report_details"])
            results.append(result)
        return results


def get_latest_verification_record(
    project_id: str,
    db_path: str = None
) -> Optional[dict]:
    """获取项目的最新验证记录"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM verification_records
            WHERE project_id = ?
            ORDER BY verification_time DESC
            LIMIT 1
        """, (project_id,))
        row = cursor.fetchone()
        if row:
            result = dict(row)
            # 解析 JSON 字段
            if result.get("report_details"):
                result["report_details"] = json.loads(result["report_details"])
            return result
        return None


def update_project_last_verified_at(
    project_id: str,
    verified_at: str,
    db_path: str = None
) -> bool:
    """更新项目的最后验证时间"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE projects SET last_verified_at = ? WHERE id = ?",
            (verified_at, project_id)
        )
        return cursor.rowcount > 0


# ==================== DatabaseManager 类 ====================

class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: str = None):
        """
        初始化数据库管理器

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path or get_db_path()

    # Project 方法
    def create_project(self, **kwargs) -> str:
        """创建项目"""
        project = NFTProject(**kwargs)
        return create_project(project, self.db_path)

    def get_project(self, project_id: str) -> Optional[dict]:
        """获取项目"""
        return get_project(project_id, self.db_path)

    def list_projects(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """列出项目"""
        return list_projects(limit, offset, self.db_path)

    # Promise 方法
    def create_promise(self, **kwargs) -> str:
        """创建承诺"""
        promise = Promise(**kwargs)
        return create_promise(promise, self.db_path)

    def get_promise(self, promise_id: str) -> Optional[dict]:
        """获取承诺"""
        return get_promise(promise_id, self.db_path)

    def get_promises_by_project(self, project_id: str) -> List[dict]:
        """获取项目的所有承诺"""
        return get_promises_by_project(project_id, self.db_path)

    def update_promise_verification_status(
        self,
        promise_id: str,
        status: str
    ) -> bool:
        """更新承诺的验证状态"""
        return update_promise_verification_status(
            promise_id,
            status,
            self.db_path
        )

    # VerificationRecord 方法
    def create_verification_record(self, **kwargs) -> str:
        """创建验证记录"""
        record = VerificationRecord(**kwargs)
        return create_verification_record(record, self.db_path)

    def get_verification_record(self, record_id: str) -> Optional[dict]:
        """获取验证记录"""
        return get_verification_record(record_id, self.db_path)

    def get_verification_records_by_project(
        self,
        project_id: str,
        limit: int = 10
    ) -> List[dict]:
        """获取项目的验证记录历史"""
        return get_verification_records_by_project(
            project_id,
            limit,
            self.db_path
        )

    def get_latest_verification_record(
        self,
        project_id: str
    ) -> Optional[dict]:
        """获取项目的最新验证记录"""
        return get_latest_verification_record(project_id, self.db_path)

    def update_project_last_verified_at(
        self,
        project_id: str,
        verified_at: str
    ) -> bool:
        """更新项目的最后验证时间"""
        return update_project_last_verified_at(
            project_id,
            verified_at,
            self.db_path
        )
