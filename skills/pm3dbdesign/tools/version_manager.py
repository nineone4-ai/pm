#!/usr/bin/env python3
"""
版本管理器 - 数据库设计文档版本对比和变更检测
"""

import re
import json
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any, Set, Tuple
from enum import Enum
from datetime import datetime
import hashlib


class ChangeType(Enum):
    """变更类型"""
    ADDED = "新增"      # 新增表/字段
    MODIFIED = "修改"   # 修改字段属性
    DELETED = "删除"    # 删除表/字段
    UNCHANGED = "未变"  # 无变化


@dataclass
class Column:
    """字段定义"""
    name: str
    data_type: str
    length: Optional[str] = None
    nullable: bool = True
    default_value: Optional[str] = None
    comment: Optional[str] = None
    is_primary_key: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Column':
        return cls(**data)

    def __hash__(self):
        return hash((self.name, self.data_type, self.length))

    def __eq__(self, other):
        if not isinstance(other, Column):
            return False
        return (self.name == other.name and
                self.data_type == other.data_type and
                self.length == other.length and
                self.nullable == other.nullable and
                self.default_value == other.default_value and
                self.comment == other.comment)


@dataclass
class Table:
    """表定义"""
    name: str
    comment: Optional[str] = None
    columns: List[Column] = None

    def __post_init__(self):
        if self.columns is None:
            self.columns = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'comment': self.comment,
            'columns': [c.to_dict() for c in self.columns]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Table':
        columns = [Column.from_dict(c) for c in data.get('columns', [])]
        return cls(
            name=data['name'],
            comment=data.get('comment'),
            columns=columns
        )

    def get_column(self, name: str) -> Optional[Column]:
        """获取指定字段"""
        for col in self.columns:
            if col.name == name:
                return col
        return None


@dataclass
class TableChange:
    """表级别变更"""
    change_type: ChangeType
    table_name: str
    details: str
    columns_added: List[Column] = None
    columns_deleted: List[Column] = None
    columns_modified: List[Tuple[Column, Column]] = None  # (旧, 新)

    def __post_init__(self):
        if self.columns_added is None:
            self.columns_added = []
        if self.columns_deleted is None:
            self.columns_deleted = []
        if self.columns_modified is None:
            self.columns_modified = []


@dataclass
class VersionInfo:
    """版本信息"""
    version: str
    timestamp: str
    file_hash: str
    table_count: int
    column_count: int


class VersionManager:
    """版本管理器"""

    def __init__(self):
        self.changes: List[TableChange] = []

    def compare_versions(self, old_tables: Dict[str, Table], new_tables: Dict[str, Table]) -> List[TableChange]:
        """
        对比两个版本的表结构
        """
        changes = []

        old_table_names = set(old_tables.keys())
        new_table_names = set(new_tables.keys())

        # 1. 检测删除的表
        deleted_tables = old_table_names - new_table_names
        for table_name in deleted_tables:
            change = TableChange(
                change_type=ChangeType.DELETED,
                table_name=table_name,
                details=f"删除表 {table_name}",
                columns_deleted=old_tables[table_name].columns
            )
            changes.append(change)

        # 2. 检测新增的表
        added_tables = new_table_names - old_table_names
        for table_name in added_tables:
            change = TableChange(
                change_type=ChangeType.ADDED,
                table_name=table_name,
                details=f"新增表 {table_name}",
                columns_added=new_tables[table_name].columns
            )
            changes.append(change)

        # 3. 检测修改的表
        common_tables = old_table_names & new_table_names
        for table_name in common_tables:
            old_table = old_tables[table_name]
            new_table = new_tables[table_name]

            table_change = self._compare_table_columns(old_table, new_table)
            if table_change:
                changes.append(table_change)

        # 按变更类型排序：删除 > 修改 > 新增
        priority = {ChangeType.DELETED: 0, ChangeType.MODIFIED: 1, ChangeType.ADDED: 2}
        changes.sort(key=lambda x: priority.get(x.change_type, 3))

        self.changes = changes
        return changes

    def _compare_table_columns(self, old_table: Table, new_table: Table) -> Optional[TableChange]:
        """对比单个表的字段变更"""
        old_columns = {c.name: c for c in old_table.columns}
        new_columns = {c.name: c for c in new_table.columns}

        old_col_names = set(old_columns.keys())
        new_col_names = set(new_columns.keys())

        columns_added = []
        columns_deleted = []
        columns_modified = []

        # 检测新增字段
        for col_name in new_col_names - old_col_names:
            columns_added.append(new_columns[col_name])

        # 检测删除字段
        for col_name in old_col_names - new_col_names:
            columns_deleted.append(old_columns[col_name])

        # 检测修改字段
        for col_name in old_col_names & new_col_names:
            old_col = old_columns[col_name]
            new_col = new_columns[col_name]

            if old_col != new_col:
                columns_modified.append((old_col, new_col))

        # 如果有任何变更，返回 TableChange
        if columns_added or columns_deleted or columns_modified:
            details = []
            if columns_added:
                details.append(f"新增 {len(columns_added)} 个字段")
            if columns_deleted:
                details.append(f"删除 {len(columns_deleted)} 个字段")
            if columns_modified:
                details.append(f"修改 {len(columns_modified)} 个字段")

            return TableChange(
                change_type=ChangeType.MODIFIED,
                table_name=old_table.name,
                details="，".join(details),
                columns_added=columns_added,
                columns_deleted=columns_deleted,
                columns_modified=columns_modified
            )

        return None

    def generate_diff_report(self) -> str:
        """生成变更对比报告"""
        if not self.changes:
            return "## 版本对比报告\n\n未发现任何变更。"

        lines = ["## 版本对比报告", ""]

        # 统计信息
        added_count = sum(1 for c in self.changes if c.change_type == ChangeType.ADDED)
        modified_count = sum(1 for c in self.changes if c.change_type == ChangeType.MODIFIED)
        deleted_count = sum(1 for c in self.changes if c.change_type == ChangeType.DELETED)

        lines.append("### 📊 变更统计")
        lines.append(f"- 🟢 新增表: {added_count} 个")
        lines.append(f"- 🟡 修改表: {modified_count} 个")
        lines.append(f"- 🔴 删除表: {deleted_count} 个")
        lines.append("")

        # 详细变更
        lines.append("### 📝 详细变更")
        lines.append("")

        for change in self.changes:
            lines.extend(self._format_table_change(change))

        return "\n".join(lines)

    def _format_table_change(self, change: TableChange) -> List[str]:
        """格式化单个表的变更"""
        lines = []

        icon = {
            ChangeType.ADDED: "🟢",
            ChangeType.MODIFIED: "🟡",
            ChangeType.DELETED: "🔴",
        }.get(change.change_type, "⚪")

        lines.append(f"#### {icon} {change.table_name}")
        lines.append(f"**变更类型**: {change.change_type.value}")
        lines.append(f"**说明**: {change.details}")
        lines.append("")

        # 新增字段
        if change.columns_added:
            lines.append("**新增字段**:")
            for col in change.columns_added:
                nullable = "可空" if col.nullable else "非空"
                lines.append(f"- `+` `{col.name}` {col.data_type}({col.length or ''}) - {col.comment or '无注释'} ({nullable})")
            lines.append("")

        # 删除字段
        if change.columns_deleted:
            lines.append("**删除字段**:")
            for col in change.columns_deleted:
                lines.append(f"- `-` `{col.name}` {col.data_type} - {col.comment or '无注释'}")
            lines.append("")

        # 修改字段
        if change.columns_modified:
            lines.append("**修改字段**:")
            for old_col, new_col in change.columns_modified:
                diff_parts = []
                if old_col.data_type != new_col.data_type:
                    diff_parts.append(f"类型: `{old_col.data_type}` → `{new_col.data_type}`")
                if old_col.length != new_col.length:
                    diff_parts.append(f"长度: `{old_col.length}` → `{new_col.length}`")
                if old_col.nullable != new_col.nullable:
                    diff_parts.append(f"可空性: `{old_col.nullable}` → `{new_col.nullable}`")
                if old_col.default_value != new_col.default_value:
                    diff_parts.append(f"默认值: `{old_col.default_value}` → `{new_col.default_value}`")
                if old_col.comment != new_col.comment:
                    diff_parts.append(f"注释变化")

                diff_str = ", ".join(diff_parts) if diff_parts else "属性微调"
                lines.append(f"- `~` `{new_col.name}`: {diff_str}")
            lines.append("")

        return lines

    def generate_ddl_migration(self, dialect: str = "mysql") -> str:
        """生成 DDL 迁移脚本"""
        lines = ["-- 数据库结构变更迁移脚本", f"-- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", f"-- 数据库方言: {dialect}", ""]

        for change in self.changes:
            if change.change_type == ChangeType.ADDED:
                # 新增表已在 ddl.sql 中，跳过
                pass

            elif change.change_type == ChangeType.DELETED:
                lines.append(f"-- 删除表: {change.table_name}")
                lines.append(f"DROP TABLE IF EXISTS `{change.table_name}`;")
                lines.append("")

            elif change.change_type == ChangeType.MODIFIED:
                lines.append(f"-- 修改表: {change.table_name}")

                # 新增字段
                for col in change.columns_added:
                    col_def = self._generate_column_def(col, dialect)
                    lines.append(f"ALTER TABLE `{change.table_name}` ADD COLUMN `{col.name}` {col_def};")

                # 删除字段
                for col in change.columns_deleted:
                    lines.append(f"ALTER TABLE `{change.table_name}` DROP COLUMN `{col.name}`;")

                # 修改字段
                for old_col, new_col in change.columns_modified:
                    if dialect == "mysql":
                        col_def = self._generate_column_def(new_col, dialect)
                        lines.append(f"ALTER TABLE `{change.table_name}` MODIFY COLUMN `{new_col.name}` {col_def};")
                    else:
                        # Oracle 需要特殊处理
                        lines.append(f"-- Oracle: 需要重建字段 {new_col.name}")

                lines.append("")

        return "\n".join(lines)

    def _generate_column_def(self, col: Column, dialect: str) -> str:
        """生成字段定义"""
        type_str = col.data_type
        if col.length:
            type_str += f"({col.length})"

        null_str = "NULL" if col.nullable else "NOT NULL"

        default_str = ""
        if col.default_value:
            default_str = f" DEFAULT {col.default_value}"

        comment_str = ""
        if dialect == "mysql" and col.comment:
            comment_str = f" COMMENT '{col.comment}'"

        return f"{type_str} {null_str}{default_str}{comment_str}"

    @classmethod
    def parse_tables_from_markdown(cls, markdown_content: str) -> Dict[str, Table]:
        """从 Markdown 文档解析表结构"""
        tables = {}

        # 匹配表名和字段
        table_pattern = r'###\s*表名[:：]?\s*(\w+)\s*\n.*?\|\s*字段名\s*\|\s*类型\s*\|\s*长度\s*\|\s*必填\s*\|\s*默认值\s*\|\s*说明\s*\|(.*?)\n\s*\n'

        for match in re.finditer(table_pattern, markdown_content, re.DOTALL | re.IGNORECASE):
            table_name = match.group(1)
            table_content = match.group(2)

            table = Table(name=table_name)

            for line in table_content.strip().split('\n'):
                line = line.strip()
                if '|' not in line or '---' in line:
                    continue

                parts = [p.strip() for p in line.split('|')]
                parts = [p for p in parts if p]

                if len(parts) < 2:
                    continue

                col = Column(
                    name=parts[0],
                    data_type=parts[1],
                    length=parts[2] if len(parts) > 2 and parts[2] else None,
                    nullable=not (len(parts) > 3 and parts[3] == '是'),
                    default_value=parts[4] if len(parts) > 4 and parts[4] != '-' else None,
                    comment=parts[5] if len(parts) > 5 else None,
                    is_primary_key=(parts[0] == 'id')
                )
                table.columns.append(col)

            if table.columns:
                tables[table_name] = table

        return tables

    @classmethod
    def generate_version_info(cls, content: str) -> VersionInfo:
        """生成版本信息"""
        tables = cls.parse_tables_from_markdown(content)

        # 计算文件哈希
        file_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:8]

        column_count = sum(len(t.columns) for t in tables.values())

        return VersionInfo(
            version=f"v{datetime.now().strftime('%Y%m%d')}-{file_hash}",
            timestamp=datetime.now().isoformat(),
            file_hash=file_hash,
            table_count=len(tables),
            column_count=column_count
        )


def compare_design_files(old_file: str, new_file: str, output_format: str = "markdown") -> Tuple[str, str]:
    """
    对比两个数据库设计文件

    Returns:
        (diff_report, ddl_migration) 元组
    """
    with open(old_file, 'r', encoding='utf-8') as f:
        old_content = f.read()

    with open(new_file, 'r', encoding='utf-8') as f:
        new_content = f.read()

    # 解析表结构
    old_tables = VersionManager.parse_tables_from_markdown(old_content)
    new_tables = VersionManager.parse_tables_from_markdown(new_content)

    # 对比版本
    manager = VersionManager()
    manager.compare_versions(old_tables, new_tables)

    # 生成报告
    diff_report = manager.generate_diff_report()
    ddl_migration = manager.generate_ddl_migration()

    return diff_report, ddl_migration


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("用法: python version_manager.py <旧版本文件> <新版本文件>")
        sys.exit(1)

    old_file = sys.argv[1]
    new_file = sys.argv[2]

    try:
        diff_report, ddl_migration = compare_design_files(old_file, new_file)
        print(diff_report)
        print("\n---\n")
        print("## DDL 迁移脚本\n")
        print("```sql")
        print(ddl_migration)
        print("```")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
