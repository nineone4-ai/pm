#!/usr/bin/env python3
"""
ER 图生成器 - 基于数据库设计生成 Mermaid ER 图
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Set
from enum import Enum


class Cardinality(Enum):
    """关系基数"""
    ONE_TO_ONE = "||--||"      # 一对一
    ONE_TO_MANY = "||--o{"      # 一对多
    MANY_TO_ONE = "}o--||"      # 多对一
    MANY_TO_MANY = "}o--o{"      # 多对多


@dataclass
class Column:
    """字段定义"""
    name: str
    data_type: str
    is_primary_key: bool = False
    is_foreign_key: bool = False
    comment: Optional[str] = None


@dataclass
class Relationship:
    """表关系定义"""
    source_table: str
    source_column: str
    target_table: str
    target_column: str
    cardinality: Cardinality
    description: Optional[str] = None


@dataclass
class Table:
    """表定义"""
    name: str
    comment: Optional[str] = None
    columns: List[Column] = field(default_factory=list)


class ERGenerator:
    """ER 图生成器"""

    def __init__(self):
        self.tables: Dict[str, Table] = {}
        self.relationships: List[Relationship] = []

    def add_table(self, table: Table):
        """添加表"""
        self.tables[table.name] = table

    def add_relationship(self, relationship: Relationship):
        """添加关系"""
        self.relationships.append(relationship)

    def generate_mermaid(self, title: Optional[str] = None) -> str:
        """生成 Mermaid ER 图"""
        lines = ["erDiagram"]

        if title:
            lines.append(f'    %% {title}')

        # 添加表定义
        for table_name, table in self.tables.items():
            lines.append(self._generate_table_definition(table))

        # 添加关系
        if self.relationships:
            lines.append("")
            for rel in self.relationships:
                lines.append(self._generate_relationship(rel))

        return "\n".join(lines)

    def _generate_table_definition(self, table: Table) -> str:
        """生成表定义"""
        lines = [f'    {table.name} {{']

        for col in table.columns:
            # 确定字段类型标识
            type_indicator = self._get_type_indicator(col.data_type)

            # 构建字段定义
            field_def = f'        {type_indicator} {col.name}'

            # 添加注释
            if col.comment:
                field_def += f' "{col.comment}"'

            # 标记主键和外键
            if col.is_primary_key:
                field_def += " PK"
            if col.is_foreign_key:
                field_def += " FK"

            lines.append(field_def)

        lines.append("    }")
        return "\n".join(lines)

    def _get_type_indicator(self, data_type: str) -> str:
        """获取类型标识符"""
        type_lower = data_type.lower()

        if any(t in type_lower for t in ['bigint', 'int', 'integer', 'smallint']):
            return "int"
        elif any(t in type_lower for t in ['decimal', 'numeric', 'float', 'double']):
            return "float"
        elif any(t in type_lower for t in ['varchar', 'char', 'text', 'string']):
            return "string"
        elif any(t in type_lower for t in ['datetime', 'timestamp', 'date', 'time']):
            return "datetime"
        elif 'bool' in type_lower or 'tinyint(1)' in type_lower:
            return "boolean"
        elif 'blob' in type_lower or 'binary' in type_lower:
            return "blob"
        else:
            return "string"

    def _generate_relationship(self, rel: Relationship) -> str:
        """生成关系定义"""
        cardinality_str = rel.cardinality.value
        rel_str = f'    {rel.source_table} {cardinality_str} {rel.target_table} : "{rel.description or ""}"'
        return rel_str

    @classmethod
    def parse_from_markdown(cls, markdown_content: str) -> 'ERGenerator':
        """
        从数据库设计 Markdown 文档解析 ER 结构
        """
        generator = cls()

        # 解析表结构
        tables = cls._parse_tables(markdown_content)
        for table in tables:
            generator.add_table(table)

        # 解析外键关系
        relationships = cls._parse_relationships(markdown_content, generator.tables)
        for rel in relationships:
            generator.add_relationship(rel)

        # 自动推断关系（基于字段名模式）
        inferred_relationships = cls._infer_relationships(generator.tables)
        for rel in inferred_relationships:
            # 避免重复添加
            if not generator._has_relationship(rel):
                generator.add_relationship(rel)

        return generator

    @classmethod
    def _parse_tables(cls, content: str) -> List[Table]:
        """解析 Markdown 中的表定义"""
        tables = []

        # 匹配表名（支持多种格式）
        # 格式1: ### 表名: xxx 或 ### 表名：xxx
        # 格式2: ### 表名 xxx
        table_patterns = [
            r'###\s*表名[:：]?\s*(\w+).*?\n.*?\|\s*字段名\s*\|\s*类型\s*\|\s*长度\s*\|\s*必填\s*\|\s*默认值\s*\|\s*说明\s*\|(.*?)\n\s*\n',
            r'####\s*(\w+).*?表.*?\n.*?\|\s*字段名\s*\|\s*类型\s*\|(.*?)\n\s*\n',
        ]

        for pattern in table_patterns:
            for match in re.finditer(pattern, content, re.DOTALL | re.IGNORECASE):
                table_name = match.group(1).strip()
                table_content = match.group(2)

                table = Table(name=table_name)

                # 解析字段行
                for line in table_content.strip().split('\n'):
                    line = line.strip()
                    if '|' not in line or '---' in line:
                        continue

                    parts = [p.strip() for p in line.split('|')]
                    # 过滤空字符串
                    parts = [p for p in parts if p]

                    if len(parts) < 2:
                        continue

                    col_name = parts[0]
                    col_type = parts[1] if len(parts) > 1 else "String"
                    col_comment = parts[-1] if len(parts) > 2 else None

                    col = Column(
                        name=col_name,
                        data_type=col_type,
                        is_primary_key=(col_name == 'id'),
                        is_foreign_key=col_name.endswith('_id') and col_name != 'id',
                        comment=col_comment
                    )

                    table.columns.append(col)

                if table.columns:
                    tables.append(table)

        return tables

    @classmethod
    def _parse_relationships(cls, content: str, tables: Dict[str, Table]) -> List[Relationship]:
        """解析显式定义的关系"""
        relationships = []

        # 匹配关系定义（例如在文档中明确说明的外键关系）
        # 格式: 表A.字段 -> 表B.字段 或 表A.字段 关联 表B.字段
        rel_patterns = [
            r'(\w+)\.(\w+)\s*[-=]+>\s*(\w+)\.(\w+)',
            r'(\w+)\.(\w+)\s*关联\s*(\w+)\.(\w+)',
            r'外键[:：]?\s*(\w+)\s*[,，]?\s*\(?\s*(\w+)\s*\)?\s*引用\s*(\w+)\s*[,，]?\s*\(?\s*(\w+)\s*\)?',
            r'FOREIGN\s+KEY.*?\((\w+)\).*?REFERENCES\s+(\w+)\s*\((\w+)\)',
        ]

        for pattern in rel_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE | re.DOTALL):
                groups = match.groups()
                if len(groups) >= 4:
                    # 尝试推断顺序
                    if len(groups) == 4:
                        src_table, src_col, tgt_table, tgt_col = groups
                    else:
                        continue

                    rel = Relationship(
                        source_table=src_table,
                        source_column=src_col,
                        target_table=tgt_table,
                        target_column=tgt_col,
                        cardinality=Cardinality.MANY_TO_ONE  # 默认多对一
                    )
                    relationships.append(rel)

        return relationships

    @classmethod
    def _infer_relationships(cls, tables: Dict[str, Table]) -> List[Relationship]:
        """基于字段名模式推断关系"""
        relationships = []

        # 获取所有表名（转换为小写用于匹配）
        table_names = {name.lower(): name for name in tables.keys()}

        for table_name, table in tables.items():
            for col in table.columns:
                if not col.is_foreign_key:
                    continue

                # 尝试从字段名推断关联表
                # 例如: user_id -> users 表, order_id -> orders 表
                col_lower = col.name.lower()

                # 去掉 _id 后缀
                if col_lower.endswith('_id'):
                    potential_table = col_lower[:-3]

                    # 尝试多种复数形式
                    potential_names = [
                        potential_table,  # user
                        potential_table + 's',  # users
                        potential_table + 'es',  # boxes
                        potential_table.rstrip('s') if potential_table.endswith('s') else potential_table,  # 处理已经是复数的情况
                        potential_table.replace('_', ''),  # userprofile
                    ]

                    for name in potential_names:
                        if name in table_names:
                            target_table = table_names[name]

                            rel = Relationship(
                                source_table=table_name,
                                source_column=col.name,
                                target_table=target_table,
                                target_column='id',
                                cardinality=Cardinality.MANY_TO_ONE,
                                description=f"{col.comment or col.name}"
                            )
                            relationships.append(rel)
                            break

        return relationships

    def _has_relationship(self, rel: Relationship) -> bool:
        """检查是否已存在相同关系"""
        for existing in self.relationships:
            if (existing.source_table == rel.source_table and
                existing.source_column == rel.source_column and
                existing.target_table == rel.target_table and
                existing.target_column == rel.target_column):
                return True
        return False

    def generate_summary(self) -> str:
        """生成 ER 图统计信息"""
        lines = ["## ER 图统计", ""]
        lines.append(f"- 表数量: {len(self.tables)}")
        lines.append(f"- 关系数量: {len(self.relationships)}")
        lines.append("")

        # 表列表
        lines.append("### 表列表")
        for table_name in sorted(self.tables.keys()):
            table = self.tables[table_name]
            pk_count = sum(1 for c in table.columns if c.is_primary_key)
            fk_count = sum(1 for c in table.columns if c.is_foreign_key)
            lines.append(f"- **{table_name}**: {len(table.columns)} 个字段 (PK: {pk_count}, FK: {fk_count})")

        # 关系列表
        if self.relationships:
            lines.append("")
            lines.append("### 关系列表")
            for rel in self.relationships:
                card_desc = {
                    Cardinality.ONE_TO_ONE: "一对一",
                    Cardinality.ONE_TO_MANY: "一对多",
                    Cardinality.MANY_TO_ONE: "多对一",
                    Cardinality.MANY_TO_MANY: "多对多",
                }.get(rel.cardinality, "未知")
                lines.append(f"- {rel.source_table}.{rel.source_column} -> {rel.target_table}.{rel.target_column} ({card_desc})")

        return "\n".join(lines)


def generate_er_from_design(design_file: str, output_format: str = "mermaid") -> Tuple[str, str]:
    """
    从数据库设计文档生成 ER 图

    Args:
        design_file: 数据库设计 Markdown 文件路径
        output_format: 输出格式 (mermaid)

    Returns:
        (er_diagram, summary) 元组
    """
    with open(design_file, 'r', encoding='utf-8') as f:
        content = f.read()

    generator = ERGenerator.parse_from_markdown(content)

    # 提取文档标题
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else "数据库 ER 图"

    er_diagram = generator.generate_mermaid(title)
    summary = generator.generate_summary()

    return er_diagram, summary


def generate_er_with_ddl(ddl_content: str) -> str:
    """
    从 DDL SQL 生成 ER 图
    """
    generator = ERGenerator()

    # 解析 CREATE TABLE 语句
    table_pattern = r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?`?(\w+)`?\s*\((.+?)\)\s*(?:ENGINE|;|$)'

    for match in re.finditer(table_pattern, ddl_content, re.DOTALL | re.IGNORECASE):
        table_name = match.group(1)
        columns_str = match.group(2)

        table = Table(name=table_name)

        # 解析字段
        for col_match in re.finditer(r'`?(\w+)`?\s+(\w+(?:\([^)]+\))?)', columns_str):
            col_name = col_match.group(1)
            col_type = col_match.group(2)

            col = Column(
                name=col_name,
                data_type=col_type,
                is_primary_key=bool(re.search(r'PRIMARY\s+KEY.*?\b' + re.escape(col_name) + r'\b', columns_str, re.I)),
                is_foreign_key=col_name.endswith('_id') and col_name != 'id'
            )
            table.columns.append(col)

        generator.add_table(table)

    # 解析外键约束
    fk_pattern = r'FOREIGN\s+KEY\s*\(?`?(\w+)`?\)?\s*REFERENCES\s*`?(\w+)`?\s*\(?`?(\w+)`?\)?'
    for match in re.finditer(fk_pattern, ddl_content, re.IGNORECASE):
        source_col = match.group(1)
        target_table = match.group(2)
        target_col = match.group(3)

        # 找到包含这个外键的表
        for table_name, table in generator.tables.items():
            if any(c.name == source_col for c in table.columns):
                rel = Relationship(
                    source_table=table_name,
                    source_column=source_col,
                    target_table=target_table,
                    target_column=target_col,
                    cardinality=Cardinality.MANY_TO_ONE
                )
                generator.add_relationship(rel)
                break

    return generator.generate_mermaid()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python er_generator.py <设计文档路径>")
        sys.exit(1)

    design_file = sys.argv[1]

    try:
        er_diagram, summary = generate_er_from_design(design_file)
        print(summary)
        print("\n## Mermaid ER 图\n")
        print("```mermaid")
        print(er_diagram)
        print("```")
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
