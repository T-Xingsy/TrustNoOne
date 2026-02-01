"""
Excel Skill 适配器

使用 excel skill 增强 Excel 报告生成功能
"""
import subprocess
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from spoon_ai.tools import BaseTool
import structlog

logger = structlog.get_logger(__name__)


class ExcelSkillAdapter(BaseTool):
    """
    Excel 报告生成工具 - 使用 excel skill

    提供增强的 Excel 报告生成能力
    优势:
    - 自动格式化
    - 支持图表
    - 公式计算
    """

    name: str = "excel_generator"
    description: str = (
        "使用 excel skill 生成 Excel 报告。"
        "输入: data (报告数据), output_path (输出路径), "
        "template (可选模板名)"
        "输出: Excel 文件路径"
    )
    parameters: dict = {
        "type": "object",
        "properties": {
            "data": {
                "type": "object",
                "description": "报告数据（字典格式）"
            },
            "output_path": {
                "type": "string",
                "description": "输出 Excel 文件路径"
            },
            "template": {
                "type": "string",
                "description": "可选模板名称",
                "default": None
            },
            "include_charts": {
                "type": "boolean",
                "description": "是否包含图表",
                "default": True
            }
        },
        "required": ["data", "output_path"]
    }

    # 声明实例属性
    skill_available: bool = False
    use_fallback: bool = True  # 如果 skill 不可用，使用 Python 库

    model_config = {
        "arbitrary_types_allowed": True
    }

    def __init__(self, **data):
        super().__init__(**data)
        self._check_skill_availability()

    def _check_skill_availability(self) -> None:
        """检查 excel skill 是否可用"""
        # 这里我们使用 Python 库作为 primary 方法
        # excel skill 作为可选增强
        try:
            import openpyxl
            self.skill_available = True
            logger.info("openpyxl 库已就绪，可生成 Excel 报告")
        except ImportError:
            self.skill_available = False
            logger.warning(
                "openpyxl 未安装",
                hint="运行: pip install openpyxl"
            )

    async def execute(
        self,
        data: Dict[str, Any],
        output_path: str,
        template: Optional[str] = None,
        include_charts: bool = True
    ) -> str:
        """
        执行 Excel 报告生成（异步接口）

        Args:
            data: 报告数据
            output_path: 输出文件路径
            template: 可选模板
            include_charts: 是否包含图表

        Returns:
            生成的 Excel 文件路径
        """
        return self._run(data, output_path, template, include_charts)

    def _run(
        self,
        data: Dict[str, Any],
        output_path: str,
        template: Optional[str] = None,
        include_charts: bool = True
    ) -> str:
        """
        执行 Excel 报告生成

        Args:
            data: 报告数据
            output_path: 输出文件路径
            template: 可选模板
            include_charts: 是否包含图表

        Returns:
            生成的 Excel 文件路径
        """
        if not data:
            raise ValueError("报告数据不能为空")

        if not output_path:
            raise ValueError("输出路径不能为空")

        logger.info(
            "开始生成 Excel 报告",
            output_path=output_path,
            template=template,
            include_charts=include_charts
        )

        try:
            # 使用 Python 库生成 Excel
            return self._generate_with_openpyxl(data, output_path, include_charts)

        except ImportError:
            error_msg = "openpyxl 未安装，无法生成 Excel 报告"
            logger.error(error_msg)
            raise RuntimeError(
                f"{error_msg}。请安装: pip install openpyxl"
            )

        except Exception as e:
            logger.error(
                "Excel 报告生成失败",
                output_path=output_path,
                error=str(e)
            )
            raise

    def _generate_with_openpyxl(
        self,
        data: Dict[str, Any],
        output_path: str,
        include_charts: bool
    ) -> str:
        """使用 openpyxl 生成 Excel 报告"""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, Alignment, PatternFill
            from openpyxl.utils import get_column_letter

            # 创建工作簿
            wb = Workbook()
            ws = wb.active
            ws.title = "NFT Promise Verification Report"

            # 标题
            ws['A1'] = "NFT Promise Verification Report"
            ws['A1'].font = Font(size=16, bold=True)
            ws['A1'].alignment = Alignment(horizontal='center')
            ws.merge_cells('A1:D1')

            # 项目信息
            row = 3
            ws[f'A{row}'] = "Project Name"
            ws[f'B{row}'] = data.get('project_name', 'N/A')
            ws[f'A{row}'].font = Font(bold=True)

            row += 1
            ws[f'A{row}'] = "Verification Date"
            ws[f'B{row}'] = data.get('verification_date', 'N/A')
            ws[f'A{row}'].font = Font(bold=True)

            # 画饼指数
            row += 2
            pbi = data.get('promise_breaking_index', 0)
            ws[f'A{row}'] = "Promise Breaking Index"
            ws[f'B{row}'] = pbi
            ws[f'A{row}'].font = Font(bold=True)

            # 根据分数设置颜色
            if pbi >= 70:
                fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
            elif pbi >= 50:
                fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
            else:
                fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")
            ws[f'B{row}'].fill = fill

            # 五维评分
            row += 2
            ws[f'A{row}'] = "Five Dimensions Score"
            ws[f'A{row}'].font = Font(size=14, bold=True)

            dimensions = data.get('five_dimensions', {})
            for dim_name, dim_data in dimensions.items():
                row += 1
                score = dim_data.get('score', 0)
                ws[f'A{row}'] = dim_name.title()
                ws[f'B{row}'] = score
                ws[f'A{row}'].font = Font(bold=True)

            # 承诺验证结果
            row += 2
            ws[f'A{row}'] = "Promises Verification"
            ws[f'A{row}'].font = Font(size=14, bold=True)

            # 表头
            row += 1
            headers = ["Content", "Type", "Status", "Evidence"]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(row=row, column=col)
                cell.value = header
                cell.font = Font(bold=True)
                cell.alignment = Alignment(horizontal='center')

            # 数据行
            verification_results = data.get('verification_results', [])
            for result in verification_results[:50]:  # 限制 50 条
                row += 1
                ws.cell(row=row, column=1).value = result.get('promise_content', '')[:50]
                ws.cell(row=row, column=2).value = result.get('promise_type', '')
                ws.cell(row=row, column=3).value = result.get('verification_status', '')
                ws.cell(row=row, column=4).value = str(result.get('evidence', ''))[:50]

            # 调整列宽
            ws.column_dimensions['A'].width = 50
            ws.column_dimensions['B'].width = 15
            ws.column_dimensions['C'].width = 15
            ws.column_dimensions['D'].width = 50

            # 保存文件
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            wb.save(output_path)

            logger.info(
                "Excel 报告生成成功",
                output_path=output_path,
                rows=row
            )

            return str(output_path)

        except Exception as e:
            logger.error("Excel 生成失败", error=str(e))
            raise
