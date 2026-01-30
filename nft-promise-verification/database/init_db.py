#!/usr/bin/env python3
"""
数据库初始化脚本

创建 SQLite 数据库表结构和索引
"""

import sqlite3
import os
from pathlib import Path


def get_db_path() -> str:
    """获取数据库文件路径"""
    # 默认路径: database/promise_breaker.db
    db_dir = Path(__file__).parent
    db_path = db_dir / "promise_breaker.db"
    return str(db_path)


def init_database(db_path: str = None) -> None:
    """
    初始化数据库表结构

    Args:
        db_path: 数据库文件路径,默认为 database/promise_breaker.db
    """
    if db_path is None:
        db_path = get_db_path()

    # 确保数据库目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 创建 projects 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                twitter_account TEXT,
                website_url TEXT,
                whitepaper_url TEXT,
                contract_address TEXT,
                github_repo TEXT,
                treasury_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_verified_at TIMESTAMP
            )
        """)

        # 创建 promises 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS promises (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                content TEXT NOT NULL,
                sources TEXT NOT NULL,
                promise_type TEXT NOT NULL,
                target_date DATE,
                verification_status TEXT DEFAULT 'pending',
                importance_weight REAL DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # 创建 verification_records 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS verification_records (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                verification_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                promise_breaking_index REAL NOT NULL,
                integrity_score REAL NOT NULL,
                fairness_score REAL NOT NULL,
                activity_score REAL NOT NULL,
                stability_score REAL NOT NULL,
                momentum_score REAL NOT NULL,
                total_promises INTEGER NOT NULL,
                fulfilled_count INTEGER NOT NULL,
                unfulfilled_count INTEGER NOT NULL,
                unverifiable_count INTEGER NOT NULL,
                report_details TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # 创建 privacy_storage_records 表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS privacy_storage_records (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                storage_type TEXT NOT NULL,
                storage_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tx_hash TEXT,
                privacy_address TEXT,
                data_hash TEXT NOT NULL,
                storage_status TEXT DEFAULT 'pending',
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
            )
        """)

        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_promises_project_id
            ON promises(project_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_promises_verification_status
            ON promises(verification_status)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_verification_records_project_id
            ON verification_records(project_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_verification_records_time
            ON verification_records(verification_time DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_privacy_storage_project_id
            ON privacy_storage_records(project_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_privacy_storage_status
            ON privacy_storage_records(storage_status)
        """)

        # 提交事务
        conn.commit()
        print(f"✅ 数据库初始化成功: {db_path}")
        print("✅ 已创建表: projects, promises, verification_records, privacy_storage_records")
        print("✅ 已创建索引: 6 个索引")

    except Exception as e:
        conn.rollback()
        print(f"❌ 数据库初始化失败: {e}")
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    init_database()
