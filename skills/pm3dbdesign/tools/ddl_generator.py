#!/usr/bin/env python3
"""
DDL 生成器 - 根据数据库设计生成可执行的 SQL 文件
支持 MySQL 和 Oracle 数据库方言
"""

from dataclasses import dataclass
from typing import List, Optional, Dict
from enum import Enum
import re


class DatabaseDialect(Enum):
    MYSQL = "mysql"
    ORACLE = "oracle"


@dataclass
class Column:
    """表字段定义"""
    name: str
    data_type: str
    length: Optional[int] = None
    precision: Optional[int] = None
    scale: Optional[int] = None
    nullable: bool = True
    default_value: Optional[str] = None
    comment: Optional[str] = None
    is_primary_key: bool = False
    is_auto_increment: bool = False
    is_unique: bool = False


@dataclass
class Index:
    """索引定义"""
    name: str
    columns: List[str]
    is_unique: bool = False
    index_type: str = "BTREE"  # BTREE, HASH, etc.


@dataclass
class Table:
    """表定义"""
    name: str
    comment: Optional[str] = None
    columns: List[Column] = None
    primary_key: Optional[List[str]] = None
    indexes: List[Index] = None
    foreign_keys: List[Dict] = None

    def __post_init__(self):
        if self.columns is None:
            self.columns = []
        if self.indexes is None:
            self.indexes = []
        if self.foreign_keys is None:
            self.foreign_keys = []


class DDLGenerator:
    """DDL 生成器基类"""

    # Java/MyBatis 类型到数据库类型的映射
    TYPE_MAPPING = {
        "Long": {"mysql": "BIGINT", "oracle": "NUMBER(19)"},
        "Integer": {"mysql": "INT", "oracle": "NUMBER(10)"},
        "String": {"mysql": "VARCHAR", "oracle": "VARCHAR2"},
        "BigDecimal": {"mysql": "DECIMAL", "oracle": "NUMBER"},
        "LocalDateTime": {"mysql": "DATETIME", "oracle": "TIMESTAMP"},
        "Date": {"mysql": "DATE", "oracle": "DATE"},
        "Boolean": {"mysql": "TINYINT(1)", "oracle": "NUMBER(1)"},
        "Text": {"mysql": "TEXT", "oracle": "CLOB"},
        "Blob": {"mysql": "BLOB", "oracle": "BLOB"},
    }

    # 审计字段标准定义
    AUDIT_COLUMNS = [
        {"name": "id", "type": "Long", "length": None, "nullable": False, "comment": "主键ID", "is_pk": True},
        {"name": "create_by", "type": "Long", "length": None, "nullable": True, "comment": "创建人ID"},
        {"name": "create_time", "type": "LocalDateTime", "length": None, "nullable": True, "comment": "创建时间"},
        {"name": "update_by", "type": "Long", "length": None, "nullable": True, "comment": "更新人ID"},
        {"name": "update_time", "type": "LocalDateTime", "length": None, "nullable": True, "comment": "更新时间"},
        {"name": "is_del", "type": "Integer", "length": None, "nullable": True, "default": "0", "comment": "删除标志(0:未删除,1:已删除)"},
        {"name": "remark", "type": "String", "length": 500, "nullable": True, "comment": "备注"},
    ]

    def __init__(self, dialect: DatabaseDialect):
        self.dialect = dialect

    def generate_ddl(self, table: Table) -> str:
        """生成单个表的完整 DDL"""
        ddl_parts = []

        # 1. DROP TABLE 语句（可选，用于重建）
        ddl_parts.append(self._generate_drop_table(table))

        # 2. CREATE TABLE 语句
        ddl_parts.append(self._generate_create_table(table))

        # 3. 表注释
        if table.comment:
            ddl_parts.append(self._generate_table_comment(table))

        # 4. 列注释
        ddl_parts.append(self._generate_column_comments(table))

        # 5. 索引
        ddl_parts.append(self._generate_indexes(table))

        # 6. 外键
        ddl_parts.append(self._generate_foreign_keys(table))

        return "\n".join(ddl_parts)

    def generate_multiple_tables(self, tables: List[Table]) -> str:
        """生成多个表的 DDL"""
        all_ddl = []

        # 添加文件头注释
        all_ddl.append(self._generate_file_header())

        for table in tables:
            all_ddl.append(self.generate_ddl(table))
            all_ddl.append("\n-- " + "=" * 60 + "\n")

        return "\n".join(all_ddl)

    def _generate_file_header(self) -> str:
        """生成文件头注释"""
        dialect_name = "MySQL" if self.dialect == DatabaseDialect.MYSQL else "Oracle"
        return f"""-- ============================================
-- PM3.0 数据库设计 DDL
-- 数据库类型: {dialect_name}
-- 生成时间: AUTO GENERATED
-- 注意: 本文件由工具自动生成，请勿手动修改
-- ============================================

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

"""

    def _generate_drop_table(self, table: Table) -> str:
        """生成 DROP TABLE 语句"""
        if self.dialect == DatabaseDialect.MYSQL:
            return f"DROP TABLE IF EXISTS `{table.name}`;"
        else:
            return f"DROP TABLE {table.name};"

    def _generate_create_table(self, table: Table) -> str:
        """生成 CREATE TABLE 语句"""
        lines = []

        if self.dialect == DatabaseDialect.MYSQL:
            lines.append(f"CREATE TABLE `{table.name}` (")
        else:
            lines.append(f"CREATE TABLE {table.name} (")

        column_defs = []
        for col in table.columns:
            column_defs.append(self._generate_column_definition(col))

        # 主键定义
        if table.primary_key:
            pk_cols = ", ".join(table.primary_key)
            if self.dialect == DatabaseDialect.MYSQL:
                column_defs.append(f"    PRIMARY KEY ({pk_cols})")
            else:
                column_defs.append(f"    CONSTRAINT pk_{table.name} PRIMARY KEY ({pk_cols})")

        lines.append(",\n".join(column_defs))
        lines.append(")")

        # MySQL 特有的表选项
        if self.dialect == DatabaseDialect.MYSQL:
            lines.append("ENGINE=InnoDB")
            lines.append("DEFAULT CHARSET=utf8mb4")
            lines.append("COLLATE=utf8mb4_unicode_ci")
            if table.comment:
                escaped_comment = table.comment.replace("'", "\\'")
                lines.append(f"COMMENT='{escaped_comment}'")

        return " ".join(lines) + ";"

    def _generate_column_definition(self, col: Column) -> str:
        """生成字段定义"""
        parts = []

        # 字段名
        if self.dialect == DatabaseDialect.MYSQL:
            parts.append(f"    `{col.name}`")
        else:
            parts.append(f"    {col.name}")

        # 数据类型
        data_type = self._map_data_type(col)
        parts.append(data_type)

        # MySQL 的自增
        if col.is_auto_increment and self.dialect == DatabaseDialect.MYSQL:
            parts.append("AUTO_INCREMENT")

        # 是否可空
        if not col.nullable:
            parts.append("NOT NULL")
        else:
            parts.append("NULL")

        # 默认值
        if col.default_value is not None:
            if col.default_value.upper() in ("NULL", "CURRENT_TIMESTAMP"):
                parts.append(f"DEFAULT {col.default_value}")
            else:
                parts.append(f"DEFAULT '{col.default_value}'")

        # MySQL 的列注释
        if col.comment and self.dialect == DatabaseDialect.MYSQL:
            escaped_comment = col.comment.replace("'", "\\'")
            parts.append(f"COMMENT '{escaped_comment}'")

        return " ".join(parts)

    def _map_data_type(self, col: Column) -> str:
        """映射数据类型"""
        java_type = col.data_type

        # 处理带长度的类型，如 VARCHAR(255)
        if "(" in java_type:
            match = re.match(r'(\w+)\((\d+)\)', java_type)
            if match:
                java_type = match.group(1)
                col.length = int(match.group(2))

        if java_type in self.TYPE_MAPPING:
            db_type = self.TYPE_MAPPING[java_type][self.dialect.value]

            # 添加长度/精度
            if java_type == "String" and col.length:
                return f"{db_type}({col.length})"
            elif java_type == "BigDecimal" and col.precision:
                if col.scale:
                    return f"{db_type}({col.precision},{col.scale})"
                return f"{db_type}({col.precision},2)"

            return db_type

        # 未知类型直接返回
        return java_type

    def _generate_table_comment(self, table: Table) -> str:
        """生成表注释语句"""
        if self.dialect == DatabaseDialect.MYSQL:
            # MySQL 的表注释在 CREATE TABLE 中已处理
            return ""
        else:
            escaped_comment = table.comment.replace("'", "''")
            return f"COMMENT ON TABLE {table.name} IS '{escaped_comment}';"

    def _generate_column_comments(self, table: Table) -> str:
        """生成列注释语句"""
        comments = []

        for col in table.columns:
            if not col.comment:
                continue

            escaped_comment = col.comment.replace("'", "''")

            if self.dialect == DatabaseDialect.MYSQL:
                # MySQL 的列注释在 CREATE TABLE 中已处理
                continue
            else:
                comments.append(
                    f"COMMENT ON COLUMN {table.name}.{col.name} IS '{escaped_comment}';"
                )

        return "\n".join(comments)

    def _generate_indexes(self, table: Table) -> str:
        """生成索引语句"""
        indexes = []

        for idx in table.indexes:
            if self.dialect == DatabaseDialect.MYSQL:
                cols = ", ".join([f"`{c}`" for c in idx.columns])
                unique = "UNIQUE " if idx.is_unique else ""
                indexes.append(
                    f"CREATE {unique}INDEX `{idx.name}` ON `{table.name}` ({cols});"
                )
            else:
                cols = ", ".join(idx.columns)
                unique = "UNIQUE " if idx.is_unique else ""
                indexes.append(
                    f"CREATE {unique}INDEX {idx.name} ON {table.name} ({cols});"
                )

        return "\n".join(indexes)

    def _generate_foreign_keys(self, table: Table) -> str:
        """生成外键语句"""
        fks = []

        for fk in table.foreign_keys:
            fk_name = fk.get("name", f"fk_{table.name}_{fk['column']}")
            column = fk["column"]
            ref_table = fk["ref_table"]
            ref_column = fk.get("ref_column", "id")

            if self.dialect == DatabaseDialect.MYSQL:
                fks.append(
                    f"ALTER TABLE `{table.name}` ADD CONSTRAINT `{fk_name}` "
                    f"FOREIGN KEY (`{column}`) REFERENCES `{ref_table}` (`{ref_column}`);"
                )
            else:
                fks.append(
                    f"ALTER TABLE {table.name} ADD CONSTRAINT {fk_name} "
                    f"FOREIGN KEY ({column}) REFERENCES {ref_table} ({ref_column});"
                )

        return "\n".join(fks)

    @classmethod
    def parse_from_markdown(cls, markdown_content: str) -> List[Table]:
        """
        从数据库设计 Markdown 文档解析表结构
        """
        tables = []

        # 简单的 Markdown 表格解析
        # 匹配表名和表结构
        table_pattern = r'###\s+表名[:：]?\s*(\w+)\s*\n.*?\|\s*字段名\s*\|\s*类型\s*\|\s*长度\s*\|\s*必填\s*\|\s*默认值\s*\|\s*说明\s*\|(.*?)\n\n'

        for match in re.finditer(table_pattern, markdown_content, re.DOTALL):
            table_name = match.group(1)
            table_content = match.group(2)

            table = Table(name=table_name)

            # 解析字段行
            for line in table_content.strip().split('\n'):
                if '|' not in line or '---' in line:
                    continue

                parts = [p.strip() for p in line.split('|')]
                if len(parts) < 6:
                    continue

                col = Column(
                    name=parts[1],
                    data_type=parts[2],
                    length=int(parts[3]) if parts[3] and parts[3].isdigit() else None,
                    nullable=parts[4] != '是',
                    default_value=parts[5] if parts[5] != '-' else None,
                    comment=parts[6] if len(parts) > 6 else None
                )

                # 识别主键
                if col.name == 'id':
                    col.is_primary_key = True
                    col.is_auto_increment = True
                    col.nullable = False
                    table.primary_key = ['id']

                table.columns.append(col)

            tables.append(table)

        return tables


def generate_ddl_from_design(design_file: str, dialect: str = "mysql") -> str:
    """
    从数据库设计文档生成 DDL

    Args:
        design_file: 数据库设计 Markdown 文件路径
        dialect: 数据库方言 (mysql/oracle)

    Returns:
        DDL SQL 内容
    """
    with open(design_file, 'r', encoding='utf-8') as f:
        content = f.read()

    db_dialect = DatabaseDialect(dialect.lower())
    generator = DDLGenerator(db_dialect)

    tables = DDLGenerator.parse_from_markdown(content)

    if not tables:
        # 如果没有解析到表，返回提示
        return "-- 未从设计文档中解析到表结构\n"

    return generator.generate_multiple_tables(tables)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python ddl_generator.py <设计文档路径> [mysql|oracle]")
        sys.exit(1)

    design_file = sys.argv[1]
    dialect = sys.argv[2] if len(sys.argv) > 2 else "mysql"

    ddl = generate_ddl_from_design(design_file, dialect)
    print(ddl)
