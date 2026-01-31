"""
FastAPI 主应用

提供 NFT 承诺验证的 RESTful API 接口
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path
import sys
from typing import Optional, List, Dict, Any
import structlog

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db import DatabaseManager
from demo import DemoRunner

logger = structlog.get_logger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="NFT Promise Verification API",
    description="NFT 项目承诺验证与画饼指数评估 API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库管理器
db_path = project_root / "data" / "promises.db"
if not db_path.exists():
    raise RuntimeError(
        "数据库不存在，请先运行: python mock_data_loader.py --clear"
    )

db_manager = DatabaseManager(str(db_path))
demo_runner = DemoRunner(db_manager)


@app.get("/")
async def root():
    """API 根路径"""
    return {
        "message": "NFT Promise Verification API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "projects": "/api/v1/projects",
            "search": "/api/v1/projects/search",
            "stats": "/api/v1/stats"
        }
    }


@app.get("/api/v1/projects")
async def list_projects(
    limit: int = 10,
    offset: int = 0
):
    """
    获取项目列表

    Args:
        limit: 返回数量限制（默认 10）
        offset: 偏移量（默认 0）

    Returns:
        项目列表
    """
    try:
        all_projects = db_manager.list_projects()

        # 为每个项目添加最新验证记录
        projects_with_scores = []
        for project in all_projects[offset:offset + limit]:
            verification_record = db_manager.get_latest_verification_record(project["id"])

            project_data = {
                "id": project["id"],
                "name": project["name"],
                "twitter_account": project.get("twitter_account"),
                "website_url": project.get("website_url"),
                "contract_address": project.get("contract_address"),
                "created_at": project["created_at"],
                "last_verified_at": project.get("last_verified_at")
            }

            if verification_record:
                project_data["promise_breaking_index"] = verification_record["promise_breaking_index"]
                project_data["comprehensive_score"] = 100 - verification_record["promise_breaking_index"]
                project_data["risk_level"] = demo_runner._get_risk_level(
                    verification_record["promise_breaking_index"]
                )
            else:
                project_data["promise_breaking_index"] = None
                project_data["comprehensive_score"] = None
                project_data["risk_level"] = None

            projects_with_scores.append(project_data)

        return {
            "success": True,
            "total": len(all_projects),
            "limit": limit,
            "offset": offset,
            "projects": projects_with_scores
        }

    except Exception as e:
        logger.error("获取项目列表失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/projects/search")
async def search_projects(
    q: str,
    limit: int = 5
):
    """
    搜索项目

    Args:
        q: 搜索关键词
        limit: 返回数量限制（默认 5）

    Returns:
        匹配的项目列表
    """
    try:
        all_projects = db_manager.list_projects()

        # 简单的关键词匹配
        matched_projects = []
        for project in all_projects:
            if (
                q.lower() in project["name"].lower()
                or (project.get("twitter_account") and q.lower() in project["twitter_account"].lower())
                or (project.get("contract_address") and q.lower() in project["contract_address"].lower())
            ):
                verification_record = db_manager.get_latest_verification_record(project["id"])

                project_data = {
                    "id": project["id"],
                    "name": project["name"],
                    "twitter_account": project.get("twitter_account"),
                    "website_url": project.get("website_url"),
                    "contract_address": project.get("contract_address")
                }

                if verification_record:
                    project_data["promise_breaking_index"] = verification_record["promise_breaking_index"]
                    project_data["risk_level"] = demo_runner._get_risk_level(
                        verification_record["promise_breaking_index"]
                    )

                matched_projects.append(project_data)

                if len(matched_projects) >= limit:
                    break

        return {
            "success": True,
            "query": q,
            "total": len(matched_projects),
            "projects": matched_projects
        }

    except Exception as e:
        logger.error("搜索项目失败", error=str(e), query=q)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/projects/{project_id}")
async def get_project_detail(project_id: str):
    """
    获取项目详情

    Args:
        project_id: 项目 ID

    Returns:
        项目详细信息，包括五维评分、承诺清单、验证历史
    """
    try:
        # 获取项目信息
        project = db_manager.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")

        # 获取承诺列表
        promises = db_manager.get_promises_by_project(project_id)

        # 获取最新验证记录
        verification_record = db_manager.get_latest_verification_record(project_id)

        # 获取所有验证历史
        verification_history = db_manager.get_verification_records_by_project(
            project_id,
            limit=10
        )

        # 构建响应数据
        response = {
            "success": True,
            "project": {
                "id": project["id"],
                "name": project["name"],
                "twitter_account": project.get("twitter_account"),
                "website_url": project.get("website_url"),
                "contract_address": project.get("contract_address"),
                "treasury_address": project.get("treasury_address"),
                "github_repo": project.get("github_repo"),
                "opensea_slug": project.get("opensea_slug"),
                "created_at": project["created_at"],
                "last_verified_at": project.get("last_verified_at")
            },
            "promises": promises,
            "verification_history": verification_history
        }

        # 如果有验证记录，添加评分信息
        if verification_record:
            response["scores"] = {
                "promise_breaking_index": verification_record["promise_breaking_index"],
                "comprehensive_score": 100 - verification_record["promise_breaking_index"],
                "risk_level": demo_runner._get_risk_level(
                    verification_record["promise_breaking_index"]
                ),
                "five_dimensions": {
                    "integrity": {
                        "score": verification_record["integrity_score"],
                        "weight": 30,
                        "status": demo_runner._get_score_status(verification_record["integrity_score"])
                    },
                    "fairness": {
                        "score": verification_record["fairness_score"],
                        "weight": 20,
                        "status": demo_runner._get_score_status(verification_record["fairness_score"])
                    },
                    "activity": {
                        "score": verification_record["activity_score"],
                        "weight": 20,
                        "status": demo_runner._get_score_status(verification_record["activity_score"])
                    },
                    "stability": {
                        "score": verification_record["stability_score"],
                        "weight": 15,
                        "status": demo_runner._get_score_status(verification_record["stability_score"])
                    },
                    "momentum": {
                        "score": verification_record["momentum_score"],
                        "weight": 15,
                        "status": demo_runner._get_score_status(verification_record["momentum_score"])
                    }
                },
                "verification_summary": {
                    "total": verification_record["total_promises"],
                    "fulfilled": verification_record["fulfilled_count"],
                    "unfulfilled": verification_record["unfulfilled_count"],
                    "unverifiable": verification_record["unverifiable_count"]
                },
                "recommendations": demo_runner._generate_recommendations(verification_record)
            }

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取项目详情失败", error=str(e), project_id=project_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/projects/{project_id}/report")
async def get_project_report(
    project_id: str,
    format: str = "json"
):
    """
    获取项目验证报告

    Args:
        project_id: 项目 ID
        format: 输出格式（json/text/markdown）

    Returns:
        验证报告
    """
    try:
        result = demo_runner.generate_report(project_id, format=format)

        if format == "json":
            return result["report"]
        else:
            return JSONResponse(
                content={"formatted": result["formatted"]},
                media_type="application/json"
            )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("生成报告失败", error=str(e), project_id=project_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stats")
async def get_stats():
    """
    获取统计数据

    Returns:
        系统统计信息
    """
    try:
        all_projects = db_manager.list_projects()

        # 统计各风险等级的项目数量
        risk_distribution = {
            "low": 0,
            "low-medium": 0,
            "medium": 0,
            "high": 0,
            "critical": 0
        }

        total_pbi = 0
        verified_count = 0

        for project in all_projects:
            verification_record = db_manager.get_latest_verification_record(project["id"])
            if verification_record:
                pbi = verification_record["promise_breaking_index"]
                total_pbi += pbi
                verified_count += 1

                risk_level = demo_runner._get_risk_level(pbi)["level"]
                risk_distribution[risk_level] += 1

        avg_pbi = total_pbi / verified_count if verified_count > 0 else 0

        return {
            "success": True,
            "total_projects": len(all_projects),
            "verified_projects": verified_count,
            "average_promise_breaking_index": round(avg_pbi, 2),
            "average_comprehensive_score": round(100 - avg_pbi, 2),
            "risk_distribution": risk_distribution
        }

    except Exception as e:
        logger.error("获取统计数据失败", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "database": "connected" if db_path.exists() else "disconnected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
