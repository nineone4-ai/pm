#!/usr/bin/env python3
"""
智能索引推荐器 - 基于字段名、备注和规则自动推荐索引
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Set, Tuple
from enum import Enum


class IndexType(Enum):
    """索引类型"""
    PRIMARY = "PRIMARY"      # 主键
    UNIQUE = "UNIQUE"        # 唯一索引
    INDEX = "INDEX"          # 普通索引
    FULLTEXT = "FULLTEXT"    # 全文索引
    COMPOSITE = "COMPOSITE"  # 复合索引


@dataclass
class IndexRecommendation:
    """索引推荐结果"""
    table_name: str
    index_name: str
    columns: List[str]
    index_type: IndexType
    reason: str
    priority: int  # 1-5，1为最高优先级
    confidence: float  # 0.0-1.0，置信度


@dataclass
class Column:
    """字段信息"""
    name: str
    data_type: str
    comment: Optional[str] = None
    is_primary_key: bool = False
    is_foreign_key: bool = False


class IndexRecommender:
    """智能索引推荐器"""

    # 高频查询字段关键词（在备注中匹配）
    QUERY_KEYWORDS = {
        # 高优先级 - 业务查询核心字段
        "高优先级": [
            "编码", "code", "编号", "no", "手机号", "phone", "邮箱", "email",
            "身份证号", "idcard", "名称", "name", "状态", "status",
            "类型", "type", "类别", "category", "等级", "level",
        ],
        # 中优先级 - 常用查询条件
        "中优先级": [
            "查询", "搜索", "检索", "lookup", "search",
            "时间", "日期", "date", "time", "创建时间", "更新时间",
            "用户", "user", "用户ID", "user_id",
            "组织", "部门", "org", "dept", "organization",
            "业务日期", "交易日期", "生效日期", "过期时间",
        ],
        # 低优先级 - 辅助查询
        "低优先级": [
            "标签", "tag", "关键字", "keyword", "关键词",
            "地区", "区域", "地址", "address", "省", "市", "区",
            "来源", "source", "渠道", "channel",
        ],
    }

    # 字段名模式匹配（自动识别高频查询字段）
    FIELD_PATTERNS = {
        # 编码类 - 高优先级
        "code": (r".*_code$|.*_no$|.*_num$|code_.*|number$", 1, 0.95),
        "phone": (r".*phone.*|.*mobile.*|.*tel.*", 1, 0.95),
        "email": (r".*email.*|.*mail.*", 1, 0.95),
        "idcard": (r".*id.*card.*|.*identity.*|身份证号.*", 1, 0.95),
        "name": (r".*_name$|^name$|名称$|名$", 1, 0.90),
        "status": (r".*_status$|^status$|状态$", 1, 0.90),
        "type": (r".*_type$|^type$|.*_kind$|类型$|类别$", 1, 0.90),

        # 时间类 - 中优先级
        "date": (r".*_date$|^date$|.*_time$|日期|时间$", 2, 0.85),
        "create_time": (r"create_time|created_at|创建时间", 2, 0.85),
        "update_time": (r"update_time|updated_at|更新时间", 2, 0.80),

        # 外键关联类 - 中优先级
        "foreign_key": (r".*_id$", 2, 0.75),

        # 业务字段 - 中低优先级
        "user": (r"user_id|creator|updator|创建人|更新人", 2, 0.80),
        "org": (r"org_id|dept_id|部门|组织|机构", 2, 0.75),
        "category": (r"category|分类|类目", 2, 0.75),
        "level": (r"level|等级|级别|grade", 2, 0.75),

        # 地理位置 - 低优先级
        "location": (r"province|city|district|region|area|省|市|区|地址", 3, 0.70),
        "source": (r"source|渠道|来源", 3, 0.65),
    }

    # 复合索引推荐规则
    COMPOSITE_INDEX_RULES = [
        # (字段组合模式, 索引类型, 原因, 优先级)
        ("(tenant_id|org_id|dept_id)", "(user_id|create_by)", "组织+用户查询", 2),
        ("(tenant_id|org_id|dept_id)", "(status|state)", "组织+状态查询", 2),
        ("(user_id|create_by)", "(create_time|created_at)", "用户+时间查询", 2),
        ("(status|state)", "(create_time|created_at)", "状态+时间查询", 2),
        ("(type|category|kind)", "(status|state)", "类型+状态查询", 3),
        ("(province|city)", "(status|state)", "地区+状态查询", 3),
    ]

    def __init__(self):
        self.recommendations: List[IndexRecommendation] = []

    def analyze_table(self, table_name: str, columns: List[Column]) -> List[IndexRecommendation]:
        """
        分析单个表的索引需求
        """
        recommendations = []

        # 1. 检查主键
        pk_columns = [c for c in columns if c.is_primary_key]
        if pk_columns:
            rec = IndexRecommendation(
                table_name=table_name,
                index_name=f"pk_{table_name}",
                columns=[c.name for c in pk_columns],
                index_type=IndexType.PRIMARY,
                reason="主键，唯一标识每条记录",
                priority=1,
                confidence=1.0
            )
            recommendations.append(rec)

        # 2. 基于字段名模式推荐索引
        for col in columns:
            if col.is_primary_key:
                continue

            rec = self._analyze_column_patterns(table_name, col)
            if rec:
                recommendations.append(rec)

        # 3. 基于字段备注推荐索引
        for col in columns:
            if col.is_primary_key:
                continue

            rec = self._analyze_column_comment(table_name, col)
            if rec and not self._has_recommendation(recommendations, table_name, col.name):
                recommendations.append(rec)

        # 4. 推荐复合索引
        composite_recs = self._analyze_composite_indexes(table_name, columns)
        recommendations.extend(composite_recs)

        # 5. 外键自动添加索引
        for col in columns:
            if col.is_foreign_key and not self._has_recommendation(recommendations, table_name, col.name):
                rec = IndexRecommendation(
                    table_name=table_name,
                    index_name=f"idx_{table_name}_{col.name}",
                    columns=[col.name],
                    index_type=IndexType.INDEX,
                    reason=f"外键字段，加速关联查询",
                    priority=2,
                    confidence=0.90
                )
                recommendations.append(rec)

        # 去重并排序
        recommendations = self._deduplicate_recommendations(recommendations)
        recommendations.sort(key=lambda x: (x.priority, -x.confidence))

        return recommendations

    def _analyze_column_patterns(self, table_name: str, col: Column) -> Optional[IndexRecommendation]:
        """基于字段名模式分析"""
        col_lower = col.name.lower()

        for pattern_name, (pattern, priority, confidence) in self.FIELD_PATTERNS.items():
            if re.match(pattern, col_lower, re.IGNORECASE):
                # 判断是否适合唯一索引
                index_type = IndexType.UNIQUE if pattern_name in ["code", "phone", "email", "idcard"] else IndexType.INDEX

                # 检查是否已存在主键
                if index_type == IndexType.UNIQUE and col.name == "id":
                    continue

                reason_map = {
                    "code": "业务编码，高频查询",
                    "phone": "手机号，高频查询且需唯一",
                    "email": "邮箱，高频查询且需唯一",
                    "idcard": "身份证号，高频查询且需唯一",
                    "name": "名称字段，常用查询条件",
                    "status": "状态字段，高频筛选条件",
                    "type": "类型字段，高频筛选条件",
                    "date": "日期时间，常用范围查询",
                    "create_time": "创建时间，常用排序和范围查询",
                    "update_time": "更新时间，常用排序和范围查询",
                    "foreign_key": "外键字段，加速关联查询",
                    "user": "用户关联，常用查询条件",
                    "org": "组织关联，常用查询条件",
                    "category": "分类字段，常用筛选",
                    "level": "等级字段，常用筛选",
                    "location": "地理位置，常用查询",
                    "source": "来源渠道，常用筛选",
                }

                index_name = f"{'uk' if index_type == IndexType.UNIQUE else 'idx'}_{table_name}_{col.name}"

                return IndexRecommendation(
                    table_name=table_name,
                    index_name=index_name,
                    columns=[col.name],
                    index_type=index_type,
                    reason=reason_map.get(pattern_name, f"{col.name} 字段，常用查询条件"),
                    priority=priority,
                    confidence=confidence
                )

        return None

    def _analyze_column_comment(self, table_name: str, col: Column) -> Optional[IndexRecommendation]:
        """基于字段备注分析"""
        if not col.comment:
            return None

        comment_lower = col.comment.lower()

        # 检查高优先级关键词
        for keyword in self.QUERY_KEYWORDS["高优先级"]:
            if keyword.lower() in comment_lower:
                # 判断是否适合唯一索引
                index_type = IndexType.UNIQUE if any(k in comment_lower for k in ["编码", "code", "编号", "no", "手机号", "邮箱"]) else IndexType.INDEX

                return IndexRecommendation(
                    table_name=table_name,
                    index_name=f"{'uk' if index_type == IndexType.UNIQUE else 'idx'}_{table_name}_{col.name}",
                    columns=[col.name],
                    index_type=index_type,
                    reason=f"字段备注包含'{keyword}'，高频查询字段",
                    priority=1,
                    confidence=0.90
                )

        # 检查中优先级关键词
        for keyword in self.QUERY_KEYWORDS["中优先级"]:
            if keyword.lower() in comment_lower:
                return IndexRecommendation(
                    table_name=table_name,
                    index_name=f"idx_{table_name}_{col.name}",
                    columns=[col.name],
                    index_type=IndexType.INDEX,
                    reason=f"字段备注包含'{keyword}'，常用查询字段",
                    priority=2,
                    confidence=0.80
                )

        # 检查低优先级关键词
        for keyword in self.QUERY_KEYWORDS["低优先级"]:
            if keyword.lower() in comment_lower:
                return IndexRecommendation(
                    table_name=table_name,
                    index_name=f"idx_{table_name}_{col.name}",
                    columns=[col.name],
                    index_type=IndexType.INDEX,
                    reason=f"字段备注包含'{keyword}'，辅助查询字段",
                    priority=3,
                    confidence=0.70
                )

        return None

    def _analyze_composite_indexes(self, table_name: str, columns: List[Column]) -> List[IndexRecommendation]:
        """分析复合索引需求"""
        recommendations = []
        column_names = {c.name.lower(): c for c in columns}

        for pattern1, pattern2, reason, priority in self.COMPOSITE_INDEX_RULES:
            matched_cols = []

            # 查找匹配的字段组合
            for col_name in column_names:
                if re.match(pattern1, col_name, re.IGNORECASE):
                    for col_name2 in column_names:
                        if re.match(pattern2, col_name2, re.IGNORECASE) and col_name != col_name2:
                            matched_cols.append((column_names[col_name].name, column_names[col_name2].name))

            for col1, col2 in matched_cols:
                # 检查是否已存在单列索引，避免重复
                rec = IndexRecommendation(
                    table_name=table_name,
                    index_name=f"idx_{table_name}_{col1}_{col2}",
                    columns=[col1, col2],
                    index_type=IndexType.COMPOSITE,
                    reason=f"复合索引：{reason}，优化联合查询",
                    priority=priority,
                    confidence=0.75
                )
                recommendations.append(rec)

        return recommendations

    def _has_recommendation(self, recommendations: List[IndexRecommendation], table_name: str, column_name: str) -> bool:
        """检查是否已有该字段的索引推荐"""
        for rec in recommendations:
            if rec.table_name == table_name and column_name in rec.columns:
                return True
        return False

    def _deduplicate_recommendations(self, recommendations: List[IndexRecommendation]) -> List[IndexRecommendation]:
        """去重，优先保留高优先级/高置信度的推荐"""
        seen = {}

        for rec in recommendations:
            key = (rec.table_name, tuple(rec.columns))
            if key not in seen:
                seen[key] = rec
            else:
                # 保留优先级更高的
                existing = seen[key]
                if rec.priority < existing.priority or (rec.priority == existing.priority and rec.confidence > existing.confidence):
                    seen[key] = rec

        return list(seen.values())

    def generate_report(self, recommendations: List[IndexRecommendation]) -> str:
        """生成索引推荐报告"""
        if not recommendations:
            return "未找到需要推荐的索引。"

        lines = ["## 智能索引推荐报告", ""]

        # 按优先级分组
        priority_names = {1: "🔴 高优先级", 2: "🟡 中优先级", 3: "🟢 低优先级", 4: "🔵 可选", 5: "⚪ 参考"}

        by_priority = {}
        for rec in recommendations:
            by_priority.setdefault(rec.priority, []).append(rec)

        for priority in sorted(by_priority.keys()):
            recs = by_priority[priority]
            lines.append(f"### {priority_names.get(priority, '其他')} ({len(recs)}个)")
            lines.append("")

            for rec in recs:
                index_type_icon = {
                    IndexType.PRIMARY: "🔑",
                    IndexType.UNIQUE: "✨",
                    IndexType.INDEX: "📇",
                    IndexType.FULLTEXT: "📄",
                    IndexType.COMPOSITE: "🔗",
                }.get(rec.index_type, "📇")

                lines.append(f"**{index_type_icon} {rec.index_name}**")
                lines.append(f"- 表名: `{rec.table_name}`")
                lines.append(f"- 字段: `{', '.join(rec.columns)}`")
                lines.append(f"- 类型: {rec.index_type.value}")
                lines.append(f"- 原因: {rec.reason}")
                lines.append(f"- 置信度: {rec.confidence:.0%}")
                lines.append("")

        # 生成 SQL 语句
        lines.append("---")
        lines.append("")
        lines.append("## 推荐索引 SQL 语句")
        lines.append("")

        for rec in recommendations:
            sql = self._generate_index_sql(rec)
            if sql:
                lines.append(f"```sql")
                lines.append(f"-- {rec.reason}")
                lines.append(sql)
                lines.append(f"```")
                lines.append("")

        return "\n".join(lines)

    def _generate_index_sql(self, rec: IndexRecommendation) -> Optional[str]:
        """生成创建索引的 SQL 语句"""
        if rec.index_type == IndexType.PRIMARY:
            return None  # 主键在 CREATE TABLE 中已创建

        cols = ", ".join([f"`{c}`" for c in rec.columns])

        if rec.index_type == IndexType.UNIQUE:
            return f"CREATE UNIQUE INDEX `{rec.index_name}` ON `{rec.table_name}` ({cols});"
        else:
            return f"CREATE INDEX `{rec.index_name}` ON `{rec.table_name}` ({cols});"

    @classmethod
    def parse_columns_from_markdown(cls, markdown_content: str) -> Dict[str, List[Column]]:
        """
        从 Markdown 文档解析表结构
        """
        tables = {}

        # 匹配表名和字段
        table_pattern = r'###\s*表名[:：]?\s*(\w+)\s*\n.*?\|\s*字段名\s*\|\s*类型\s*\|\s*长度\s*\|\s*必填\s*\|\s*默认值\s*\|\s*说明\s*\|(.*?)\n\s*\n'

        for match in re.finditer(table_pattern, markdown_content, re.DOTALL | re.IGNORECASE):
            table_name = match.group(1)
            table_content = match.group(2)

            columns = []
            for line in table_content.strip().split('\n'):
                line = line.strip()
                if '|' not in line or '---' in line:
                    continue

                parts = [p.strip() for p in line.split('|')]
                parts = [p for p in parts if p]

                if len(parts) < 2:
                    continue

                col_name = parts[0]
                col_type = parts[1]
                col_comment = parts[-1] if len(parts) > 2 else None

                col = Column(
                    name=col_name,
                    data_type=col_type,
                    comment=col_comment,
                    is_primary_key=(col_name == 'id'),
                    is_foreign_key=col_name.endswith('_id') and col_name != 'id'
                )
                columns.append(col)

            if columns:
                tables[table_name] = columns

        return tables


def analyze_indexes(design_file: str) -> str:
    """
    分析数据库设计文档并生成索引推荐报告
    """
    with open(design_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 解析表结构
    tables = IndexRecommender.parse_columns_from_markdown(content)

    if not tables:
        return "未从设计文档中解析到表结构。"

    # 分析索引
    recommender = IndexRecommender()
    all_recommendations = []

    for table_name, columns in tables.items():
        recs = recommender.analyze_table(table_name, columns)
        all_recommendations.extend(recs)

    # 生成报告
    return recommender.generate_report(all_recommendations)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python index_recommender.py <设计文档路径>")
        sys.exit(1)

    design_file = sys.argv[1]
    report = analyze_indexes(design_file)
    print(report)
