#!/usr/bin/env python3
"""
OpenSpec 适配器 - 从系分设计文档解析领域模型并映射到数据库表
"""

import re
import json
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum


class DomainObjectType(Enum):
    """领域对象类型"""
    AGGREGATE_ROOT = "聚合根"
    ENTITY = "实体"
    VALUE_OBJECT = "值对象"
    DOMAIN_EVENT = "领域事件"


@dataclass
class DomainField:
    """领域字段"""
    name: str
    type: str
    description: Optional[str] = None
    is_required: bool = True
    is_collection: bool = False
    reference_to: Optional[str] = None  # 关联对象


@dataclass
class DomainObject:
    """领域对象"""
    name: str
    object_type: DomainObjectType
    description: Optional[str] = None
    fields: List[DomainField] = field(default_factory=list)
    parent: Optional[str] = None  # 父聚合


@dataclass
class DomainEvent:
    """领域事件"""
    name: str
    description: Optional[str] = None
    fields: List[DomainField] = field(default_factory=list)
    source_aggregate: Optional[str] = None


@dataclass
class TableMapping:
    """表映射结果"""
    domain_name: str
    table_name: str
    fields: List[Dict[str, Any]]
    description: Optional[str] = None
    indexes: List[Dict[str, Any]] = field(default_factory=list)


class OpenSpecAdapter:
    """OpenSpec 适配器"""

    # 类型映射：领域类型 -> Java类型 -> DB类型
    TYPE_MAPPING = {
        # 基础类型
        "String": {"java": "String", "db": "VARCHAR", "length": 255},
        "Integer": {"java": "Integer", "db": "INT"},
        "Long": {"java": "Long", "db": "BIGINT"},
        "Boolean": {"java": "Boolean", "db": "TINYINT", "length": 1},
        "BigDecimal": {"java": "BigDecimal", "db": "DECIMAL", "precision": 18, "scale": 2},
        "LocalDateTime": {"java": "LocalDateTime", "db": "DATETIME"},
        "Date": {"java": "Date", "db": "DATE"},
        "LocalDate": {"java": "LocalDate", "db": "DATE"},
        "LocalTime": {"java": "LocalTime", "db": "TIME"},
        "Text": {"java": "String", "db": "TEXT"},
        "JSON": {"java": "String", "db": "JSON"},
        # 集合类型
        "List": {"java": "List", "db": None},  # 需要特殊处理
        "Set": {"java": "Set", "db": None},
        "Map": {"java": "Map", "db": None},
    }

    def __init__(self):
        self.domain_objects: Dict[str, DomainObject] = {}
        self.domain_events: Dict[str, DomainEvent] = {}
        self.table_mappings: List[TableMapping] = []

    def parse_from_openspec(self, content: str) -> Tuple[Dict[str, DomainObject], Dict[str, DomainEvent]]:
        """
        从 OpenSpec 系分文档解析领域模型
        """
        # 解析聚合根
        self._parse_aggregate_roots(content)

        # 解析实体
        self._parse_entities(content)

        # 解析领域事件
        self._parse_domain_events(content)

        # 解析关联关系
        self._parse_relationships(content)

        return self.domain_objects, self.domain_events

    def _parse_aggregate_roots(self, content: str):
        """解析聚合根"""
        # 匹配聚合根定义（多种格式）
        patterns = [
            r'###\s*聚合根[:：]?\s*(\w+).*?\n.*?属性[:：]?(.*?)(?=###|##|$)',
            r'####\s*(\w+).*?聚合根.*?\n.*?属性[:：]?(.*?)(?=####|###|##|$)',
            r'\*\*聚合根[:：]\s*(\w+)\*\*.*?(?:属性|字段)[:：]?(.*?)(?=\*\*|##|$)',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, content, re.DOTALL | re.IGNORECASE):
                name = match.group(1).strip()
                fields_text = match.group(2)

                obj = DomainObject(
                    name=name,
                    object_type=DomainObjectType.AGGREGATE_ROOT,
                    fields=self._parse_fields(fields_text)
                )
                self.domain_objects[name] = obj

    def _parse_entities(self, content: str):
        """解析实体"""
        patterns = [
            r'###\s*实体[:：]?\s*(\w+).*?\n.*?属性[:：]?(.*?)(?=###|##|$)',
            r'####\s*(\w+).*?实体.*?\n.*?属性[:：]?(.*?)(?=####|###|##|$)',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, content, re.DOTALL | re.IGNORECASE):
                name = match.group(1).strip()
                fields_text = match.group(2)

                # 检查是否已存在（可能是聚合根）
                if name in self.domain_objects:
                    continue

                obj = DomainObject(
                    name=name,
                    object_type=DomainObjectType.ENTITY,
                    fields=self._parse_fields(fields_text)
                )
                self.domain_objects[name] = obj

    def _parse_domain_events(self, content: str):
        """解析领域事件"""
        patterns = [
            r'###\s*领域事件[:：]?\s*(\w+).*?\n.*?属性[:：]?(.*?)(?=###|##|$)',
            r'####\s*(\w+).*?领域事件.*?\n.*?属性[:：]?(.*?)(?=####|###|##|$)',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, content, re.DOTALL | re.IGNORECASE):
                name = match.group(1).strip()
                fields_text = match.group(2)

                event = DomainEvent(
                    name=name,
                    fields=self._parse_fields(fields_text)
                )
                self.domain_events[name] = event

    def _parse_fields(self, text: str) -> List[DomainField]:
        """解析字段定义"""
        fields = []

        # 匹配表格行或列表项
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('---') or line.startswith('| --'):
                continue

            # 表格格式: | name | type | desc |
            if '|' in line:
                parts = [p.strip() for p in line.split('|')]
                parts = [p for p in parts if p]
                if len(parts) >= 2:
                    field = self._create_field(parts[0], parts[1], parts[2] if len(parts) > 2 else None)
                    if field:
                        fields.append(field)

            # 列表格式: - name: type - desc
            elif line.startswith('- ') or line.startswith('* '):
                match = re.match(r'[-*]\s*(\w+)\s*[:：]\s*(\w+)\s*[-:]?\s*(.*)', line)
                if match:
                    field = self._create_field(match.group(1), match.group(2), match.group(3) or None)
                    if field:
                        fields.append(field)

        return fields

    def _create_field(self, name: str, type_str: str, desc: Optional[str]) -> Optional[DomainField]:
        """创建字段对象"""
        # 处理集合类型 List<Type> 或 Type[]
        is_collection = False
        base_type = type_str

        if type_str.startswith('List<') or type_str.startswith('Set<'):
            is_collection = True
            match = re.match(r'\w+<(\w+)>', type_str)
            if match:
                base_type = match.group(1)
        elif type_str.endswith('[]'):
            is_collection = True
            base_type = type_str[:-2]

        return DomainField(
            name=name,
            type=base_type,
            description=desc,
            is_collection=is_collection
        )

    def _parse_relationships(self, content: str):
        """解析对象间关系"""
        # 关联关系：contains, belongs_to, has_many 等
        rel_patterns = [
            r'(\w+)\s+包含\s+(\w+)',
            r'(\w+)\s+has\s+(\w+)',
            r'(\w+)\s+belongs_to\s+(\w+)',
            r'(\w+)\s+关联\s+(\w+)',
        ]

        for pattern in rel_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                source = match.group(1)
                target = match.group(2)

                if source in self.domain_objects:
                    # 添加关联字段
                    field = DomainField(
                        name=f"{target.lower()}_id",
                        type="Long",
                        description=f"关联{target}的ID",
                        reference_to=target
                    )
                    self.domain_objects[source].fields.append(field)

    def generate_table_design(self) -> List[TableMapping]:
        """
        将领域模型映射为数据库表设计
        """
        mappings = []

        # 聚合根生成主表
        for name, obj in self.domain_objects.items():
            if obj.object_type == DomainObjectType.AGGREGATE_ROOT:
                mapping = self._map_aggregate_to_table(obj)
                mappings.append(mapping)

                # 处理聚合内的实体（生成从表）
                for field in obj.fields:
                    if field.is_collection and field.type in self.domain_objects:
                        child_obj = self.domain_objects[field.type]
                        child_mapping = self._map_child_entity_to_table(child_obj, obj.name)
                        mappings.append(child_mapping)

        # 独立实体生成表
        for name, obj in self.domain_objects.items():
            if obj.object_type == DomainObjectType.ENTITY and obj.parent is None:
                # 检查是否已处理
                if not any(m.domain_name == name for m in mappings):
                    mapping = self._map_entity_to_table(obj)
                    mappings.append(mapping)

        self.table_mappings = mappings
        return mappings

    def _map_aggregate_to_table(self, obj: DomainObject) -> TableMapping:
        """映射聚合根到主表"""
        # 表名转换：Order -> orders, User -> users
        table_name = self._to_snake_case(obj.name)
        if not table_name.endswith('s'):
            table_name += 's'

        fields = []
        indexes = []

        # ID 字段
        fields.append({
            "name": "id",
            "type": "Long",
            "db_type": "BIGINT",
            "length": None,
            "nullable": False,
            "comment": "主键ID",
            "is_pk": True
        })

        # 映射属性字段
        for field in obj.fields:
            if field.is_collection:
                # 集合类型不直接存储，通过从表关联
                continue

            db_field = self._map_field_to_db(field)
            if db_field:
                fields.append(db_field)

                # 外键字段添加索引
                if field.reference_to:
                    indexes.append({
                        "name": f"idx_{table_name}_{field.name}",
                        "columns": [field.name],
                        "type": "INDEX"
                    })

        # 添加审计字段
        fields.extend(self._get_audit_fields())

        return TableMapping(
            domain_name=obj.name,
            table_name=table_name,
            fields=fields,
            description=obj.description,
            indexes=indexes
        )

    def _map_child_entity_to_table(self, obj: DomainObject, parent_name: str) -> TableMapping:
        """映射子实体到从表"""
        # 表名：parent_childs
        parent_table = self._to_snake_case(parent_name)
        table_name = f"{parent_table}_{self._to_snake_case(obj.name)}s"

        fields = []

        # ID 字段
        fields.append({
            "name": "id",
            "type": "Long",
            "db_type": "BIGINT",
            "length": None,
            "nullable": False,
            "comment": "主键ID",
            "is_pk": True
        })

        # 父表外键
        parent_id_field = f"{parent_name.lower()}_id"
        fields.append({
            "name": parent_id_field,
            "type": "Long",
            "db_type": "BIGINT",
            "length": None,
            "nullable": False,
            "comment": f"关联{parent_name}的ID",
            "is_fk": True,
            "ref_table": parent_table,
            "ref_column": "id"
        })

        # 映射属性字段
        for field in obj.fields:
            if not field.is_collection:
                db_field = self._map_field_to_db(field)
                if db_field:
                    fields.append(db_field)

        # 添加审计字段
        fields.extend(self._get_audit_fields())

        return TableMapping(
            domain_name=obj.name,
            table_name=table_name,
            fields=fields,
            description=f"{obj.description}（{parent_name}的从表）",
            indexes=[{
                "name": f"idx_{table_name}_{parent_id_field}",
                "columns": [parent_id_field],
                "type": "INDEX"
            }]
        )

    def _map_entity_to_table(self, obj: DomainObject) -> TableMapping:
        """映射独立实体到表"""
        return self._map_aggregate_to_table(obj)

    def _map_field_to_db(self, field: DomainField) -> Optional[Dict[str, Any]]:
        """映射领域字段到数据库字段"""
        type_info = self.TYPE_MAPPING.get(field.type, {"java": "String", "db": "VARCHAR", "length": 255})

        # 如果是领域对象引用，转为外键
        if field.type in self.domain_objects:
            return {
                "name": f"{field.name.lower()}_id",
                "type": "Long",
                "db_type": "BIGINT",
                "length": None,
                "nullable": not field.is_required,
                "comment": field.description or f"关联{field.type}的ID",
                "is_fk": True,
                "ref_table": self._to_snake_case(field.type) + 's',
                "ref_column": "id"
            }

        db_field = {
            "name": self._to_snake_case(field.name),
            "type": type_info["java"],
            "db_type": type_info["db"],
            "length": type_info.get("length"),
            "nullable": not field.is_required,
            "comment": field.description or f"{field.name}"
        }

        # 添加精度信息
        if "precision" in type_info:
            db_field["precision"] = type_info["precision"]
            db_field["scale"] = type_info.get("scale", 0)

        return db_field

    def _get_audit_fields(self) -> List[Dict[str, Any]]:
        """获取审计字段"""
        return [
            {"name": "create_by", "type": "Long", "db_type": "BIGINT", "length": None, "nullable": True, "comment": "创建人ID"},
            {"name": "create_time", "type": "LocalDateTime", "db_type": "DATETIME", "length": None, "nullable": True, "comment": "创建时间"},
            {"name": "update_by", "type": "Long", "db_type": "BIGINT", "length": None, "nullable": True, "comment": "更新人ID"},
            {"name": "update_time", "type": "LocalDateTime", "db_type": "DATETIME", "length": None, "nullable": True, "comment": "更新时间"},
            {"name": "is_del", "type": "Integer", "db_type": "INT", "length": None, "nullable": True, "default": "0", "comment": "删除标志(0:未删除,1:已删除)"},
            {"name": "remark", "type": "String", "db_type": "VARCHAR", "length": 500, "nullable": True, "comment": "备注"},
        ]

    def _to_snake_case(self, name: str) -> str:
        """驼峰命名转下划线命名"""
        # OrderItem -> order_item
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def generate_markdown_report(self) -> str:
        """生成 Markdown 格式的数据库设计报告"""
        lines = ["# 数据库设计文档（从OpenSpec系分生成）", ""]

        lines.append("## 领域模型映射概述")
        lines.append(f"- 聚合根/实体数量：{len([o for o in self.domain_objects.values() if o.object_type in (DomainObjectType.AGGREGATE_ROOT, DomainObjectType.ENTITY)])}")
        lines.append(f"- 领域事件数量：{len(self.domain_events)}")
        lines.append(f"- 生成表数量：{len(self.table_mappings)}")
        lines.append("")

        # 生成表结构
        for mapping in self.table_mappings:
            lines.extend(self._generate_table_section(mapping))

        # 生成领域事件表（可选）
        if self.domain_events:
            lines.append("## 领域事件存储表")
            lines.append("")
            lines.append("如需记录领域事件，建议创建以下表：")
            lines.append("")
            for event_name in self.domain_events.keys():
                lines.append(f"- `{event_name.lower()}_events` - 存储{event_name}事件")
            lines.append("")

        return "\n".join(lines)

    def _generate_table_section(self, mapping: TableMapping) -> List[str]:
        """生成单个表的 Markdown 章节"""
        lines = []

        lines.append(f"### 表名: {mapping.table_name}")
        if mapping.description:
            lines.append(f"**描述**: {mapping.description}")
        lines.append(f"**来源领域对象**: {mapping.domain_name}")
        lines.append("")

        # 字段表
        lines.append("| 字段名 | 类型 | 长度 | 必填 | 默认值 | 说明 |")
        lines.append("|--------|------|------|------|--------|------|")

        for field in mapping.fields:
            length = field.get("length", "")
            nullable = "否" if not field.get("nullable", True) else "是"
            default = field.get("default", "-")
            comment = field.get("comment", "")

            if field.get("is_pk"):
                comment += " [PK]"
            if field.get("is_fk"):
                comment += " [FK]"

            lines.append(f"| {field['name']} | {field['db_type']} | {length} | {nullable} | {default} | {comment} |")

        lines.append("")

        # 索引
        if mapping.indexes:
            lines.append("**索引**:")
            for idx in mapping.indexes:
                lines.append(f"- `{idx['name']}` ({', '.join(idx['columns'])}) - {idx['type']}")
            lines.append("")

        return lines

    def export_to_json(self) -> str:
        """导出为 JSON 格式"""
        data = {
            "domain_objects": [
                {
                    "name": o.name,
                    "type": o.object_type.value,
                    "fields": [{"name": f.name, "type": f.type} for f in o.fields]
                }
                for o in self.domain_objects.values()
            ],
            "tables": [
                {
                    "domain_name": m.domain_name,
                    "table_name": m.table_name,
                    "fields": m.fields
                }
                for m in self.table_mappings
            ]
        }
        return json.dumps(data, ensure_ascii=False, indent=2)


def integrate_openspec(openspec_file: str, output_format: str = "markdown") -> str:
    """
    集成 OpenSpec 系分文档，生成数据库设计

    Args:
        openspec_file: OpenSpec 系分文档路径
        output_format: 输出格式 (markdown/json)

    Returns:
        数据库设计文档
    """
    with open(openspec_file, 'r', encoding='utf-8') as f:
        content = f.read()

    adapter = OpenSpecAdapter()

    # 解析领域模型
    adapter.parse_from_openspec(content)

    # 生成表设计
    adapter.generate_table_design()

    # 输出结果
    if output_format == "json":
        return adapter.export_to_json()
    else:
        return adapter.generate_markdown_report()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python openspec_adapter.py <OpenSpec系分文档路径> [markdown|json]")
        sys.exit(1)

    openspec_file = sys.argv[1]
    output_format = sys.argv[2] if len(sys.argv) > 2 else "markdown"

    try:
        result = integrate_openspec(openspec_file, output_format)
        print(result)
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
