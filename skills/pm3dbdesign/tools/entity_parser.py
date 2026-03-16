#!/usr/bin/env python3
"""
PM3.0 数据实体解析工具
从需求规格说明书中提取数据实体定义
"""

import re
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum


class EntityType(Enum):
    """实体类型"""
    MAIN = "主实体"           # 主数据项
    ATTACHMENT = "附件实体"    # 附件数据项
    APPLY = "申请单实体"       # 申请单数据项
    APPROVAL = "审批单实体"    # 审批单数据项
    RELATION = "关联实体"      # 关联数据项（如线索数据项）


class DataType(Enum):
    """需求文档中的数据类型"""
    TEXT = "文本"
    NUMBER = "数值"
    DATE = "日期型"
    DATETIME = "时间型"
    BOOLEAN = "布尔值"


@dataclass
class FieldDefinition:
    """字段定义"""
    original_name: str          # 原始中文名
    field_name: str             # 转换后的英文名
    data_type: str              # 数据类型
    length: Optional[str]       # 长度
    required: bool              # 是否必填
    comment: str                # 备注
    is_primary_key: bool = False
    is_foreign_key: bool = False
    is_unique: bool = False
    default_value: Optional[str] = None
    enum_values: Optional[List[str]] = None
    references: Optional[str] = None  # 外键引用


@dataclass
class EntityDefinition:
    """实体定义"""
    entity_name: str            # 实体名称（如"线索"）
    entity_type: EntityType     # 实体类型
    data_item_name: str         # 数据项全称（如"线索数据项"）
    module: str                 # 所属模块
    fields: List[FieldDefinition] = field(default_factory=list)
    is_system_table: bool = False  # 是否系统统一表
    system_table_name: Optional[str] = None  # 对应的系统表名


class EntityParser:
    """实体解析器"""

    # 禁止新建的系统表清单
    PROHIBITED_TABLES = {
        # idm 表
        'idm_oauth_client', 'idm_oauth_client_user', 'idm_org',
        'idm_position', 'idm_tenant', 'idm_tenant_user',
        'idm_user', 'idm_user_org',
        # permission 表
        'permission_role', 'permission_role_apply_record', 'permission_role_approver',
        'permission_role_assign', 'permission_role_btn_ref', 'permission_role_data_range',
        'permission_role_field', 'permission_role_field_ref', 'permission_role_group',
        'permission_role_operation', 'permission_role_org_parse', 'permission_role_relation',
        'permission_role_resource', 'permission_role_row_ref', 'permission_role_user_data_range',
        'permission_group_role',
        # mam/mdm 表
        'mam_area', 'mam_person', 'mdm_centralized', 'mdm_city', 'mdm_company',
        'mdm_country', 'mdm_currency', 'mdm_dept', 'mdm_dept_view',
        'mdm_dept_view_prd', 'mdm_dept_view_prd_new', 'mdm_equity_transfer_view',
        'mdm_language', 'mdm_language_view', 'mdm_material_category', 'mdm_position',
        'mdm_profit_center', 'mdm_profit_center_prd', 'mdm_project', 'mdm_project_view',
        'mdm_province', 'mdm_reg_cer_type', 'mdm_request_og', 'mdm_sap',
        'mdm_subsidiary', 'mdm_supply_category', 'mdm_unit',
    }

    # 字段名转换映射
    FIELD_NAME_MAPPING = {
        'id': 'id',
        '编号': '_no',
        '编码': '_code',
        '名称': '_name',
        '状态': '_status',
        '类型': '_type',
        '时间': '_time',
        '日期': '_date',
        '人': '_by',
        '人员': '_by',
        '容量': '_capacity',
        '功率': '_power',
        '地址': '_address',
        '面积': '_area',
        '备注': 'remark',
        '标签': 'tag',
        '原因': '_reason',
    }

    def __init__(self):
        self.entities: List[EntityDefinition] = []

    def parse_document(self, content: str) -> List[EntityDefinition]:
        """
        解析需求规格说明书

        Args:
            content: Markdown文档内容

        Returns:
            实体定义列表
        """
        self.entities = []

        # 分割成模块章节
        module_sections = self._split_into_modules(content)

        for module_name, module_content in module_sections:
            # 在每个模块中提取数据项
            self._extract_data_items(module_name, module_content)

        return self.entities

    def _split_into_modules(self, content: str) -> List[tuple]:
        """将文档按模块分割"""
        modules = []

        # 匹配 4.x. 模块名称 格式
        pattern = r'##\s+4\.(\d+)\.\s+(.+?)(?=##\s+4\.\d+\.|##\s+5\.|$)'
        matches = list(re.finditer(pattern, content, re.DOTALL))

        if not matches:
            # 尝试其他格式
            pattern = r'##\s+(\d+)\.\s*(.+?)(?=##\s+\d+\.|$)'
            matches = list(re.finditer(pattern, content, re.DOTALL))

        for match in matches:
            module_num = match.group(1)
            module_title = match.group(2).strip().split('\n')[0]
            module_content = match.group(0)
            modules.append((module_title, module_content))

        return modules

    def _extract_data_items(self, module_name: str, module_content: str):
        """提取数据项章节"""
        # 匹配 #### XXX数据项 章节
        pattern = r'####\s+(.+?数据项)\s*\n\s*\|(.+?)\|\s*\n\s*\|[-\s\|]+\|\s*\n((?:\|.+?\|\s*\n)+)'

        matches = re.finditer(pattern, module_content, re.MULTILINE)

        for match in matches:
            data_item_name = match.group(1).strip()
            header_row = match.group(2)
            data_rows = match.group(3)

            # 解析实体类型和名称
            entity_type, entity_name = self._classify_entity(data_item_name)

            # 解析字段
            fields = self._parse_fields(data_rows)

            # 创建实体定义
            entity = EntityDefinition(
                entity_name=entity_name,
                entity_type=entity_type,
                data_item_name=data_item_name,
                module=module_name,
                fields=fields
            )

            # 检查是否系统统一表
            self._check_system_table(entity)

            self.entities.append(entity)

    def _classify_entity(self, data_item_name: str) -> tuple:
        """
        分类实体类型

        Returns:
            (EntityType, entity_name)
        """
        # 附件数据项
        match = re.match(r'^(.+?)附件数据项$', data_item_name)
        if match:
            return EntityType.ATTACHMENT, match.group(1)

        # 申请单数据项
        match = re.match(r'^(.+?)申请单数据项$', data_item_name)
        if match:
            return EntityType.APPLY, match.group(1)

        # 审批单数据项
        match = re.match(r'^(.+?)审批单数据项$', data_item_name)
        if match:
            return EntityType.APPROVAL, match.group(1)

        # 关联数据项（XX数据项XXX）
        match = re.match(r'^(.+?)(数据项.+)$', data_item_name)
        if match and match.group(2) != '数据项':
            return EntityType.RELATION, match.group(1) + match.group(2).replace('数据项', '')

        # 主数据项
        match = re.match(r'^(.+?)数据项$', data_item_name)
        if match:
            return EntityType.MAIN, match.group(1)

        return EntityType.MAIN, data_item_name

    def _parse_fields(self, data_rows: str) -> List[FieldDefinition]:
        """解析字段表格"""
        fields = []

        # 分割行
        rows = [r.strip() for r in data_rows.strip().split('\n') if r.strip()]

        for row in rows:
            # 解析表格行
            cells = self._parse_table_row(row)
            if len(cells) < 5:
                continue

            original_name = cells[0].strip()
            data_type = cells[1].strip()
            length = cells[2].strip() if cells[2].strip() else None
            required = cells[3].strip() == '是'
            comment = cells[4].strip() if len(cells) > 4 else ''

            # 转换字段名
            field_name = self._convert_field_name(original_name)

            # 识别特殊属性
            is_pk = '主键' in comment
            is_fk = any(kw in comment for kw in ['引用', '关联', '来源于'])
            is_unique = '唯一' in comment

            # 提取默认值
            default_value = self._extract_default(comment)

            # 提取枚举值
            enum_values = self._extract_enum_values(comment)

            # 提取外键引用
            references = self._extract_references(comment)

            field = FieldDefinition(
                original_name=original_name,
                field_name=field_name,
                data_type=data_type,
                length=length,
                required=required,
                comment=comment,
                is_primary_key=is_pk,
                is_foreign_key=is_fk,
                is_unique=is_unique,
                default_value=default_value,
                enum_values=enum_values,
                references=references
            )

            fields.append(field)

        return fields

    def _parse_table_row(self, row: str) -> List[str]:
        """解析表格行"""
        # 移除行首尾的 |
        row = row.strip()
        if row.startswith('|'):
            row = row[1:]
        if row.endswith('|'):
            row = row[:-1]

        # 分割单元格
        cells = [cell.strip() for cell in row.split('|')]
        return cells

    def _convert_field_name(self, chinese_name: str) -> str:
        """将中文字段名转换为 snake_case 英文名"""
        # 直接返回如果已经是英文
        if re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', chinese_name):
            return chinese_name.lower()

        # 特殊处理 ID 字段
        if chinese_name.endswith('ID'):
            prefix = chinese_name[:-2]
            if prefix:
                return self._convert_field_name(prefix) + '_id'
            return 'id'

        # 处理 "是否XXX" 格式
        if chinese_name.startswith('是否'):
            return 'is_' + self._convert_field_name(chinese_name[2:])

        # 逐词转换
        result = []
        remaining = chinese_name

        # 按优先级匹配
        for cn, en in sorted(self.FIELD_NAME_MAPPING.items(),
                            key=lambda x: len(x[0]), reverse=True):
            if remaining.endswith(cn):
                result.insert(0, en)
                remaining = remaining[:-len(cn)]
                break

        if remaining:
            # 使用拼音或简化处理
            result.insert(0, self._pinyin_convert(remaining))

        field_name = ''.join(result)
        if field_name.startswith('_'):
            field_name = field_name[1:]

        return field_name or 'field'

    def _pinyin_convert(self, chinese: str) -> str:
        """简单的拼音转换（简化版）"""
        # 常见词汇映射
        pinyin_map = {
            '线索': 'clue',
            '开发权': 'dev_right',
            '项目': 'project',
            '立项': 'project_approval',
            '预立项': 'pre_project',
            '指标': 'quota',
            '附件': 'attachment',
            '申请': 'apply',
            '审批': 'approval',
            '用户': 'user',
            '组织': 'org',
            '部门': 'dept',
            '公司': 'company',
            '名称': 'name',
            '标题': 'title',
            '描述': 'desc',
            '内容': 'content',
            '类型': 'type',
            '状态': 'status',
            '创建': 'create',
            '更新': 'update',
            '删除': 'delete',
            '时间': 'time',
            '日期': 'date',
            '编号': 'no',
            '编码': 'code',
            '备注': 'remark',
        }

        for cn, py in pinyin_map.items():
            chinese = chinese.replace(cn, py + '_')

        # 移除末尾的下划线
        chinese = chinese.strip('_')

        return chinese if chinese else 'field'

    def _extract_default(self, comment: str) -> Optional[str]:
        """提取默认值"""
        patterns = [
            r'默认[:：]?\s*([^，。；]+)',
            r'默认值[:：]?\s*([^，。；]+)',
            r'默认显示为\s*([^，。；]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, comment)
            if match:
                return match.group(1).strip()

        return None

    def _extract_enum_values(self, comment: str) -> Optional[List[str]]:
        """提取枚举值"""
        patterns = [
            r'取值[范围]?[:：]?\s*([^。；]+)',
            r'字典取值[范围]?[:：]?\s*([^。；]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, comment)
            if match:
                values_str = match.group(1)
                # 分割取值
                values = re.split(r'[,，、/；;]', values_str)
                return [v.strip() for v in values if v.strip()]

        return None

    def _extract_references(self, comment: str) -> Optional[str]:
        """提取外键引用"""
        patterns = [
            r'引用(.+?)\.(.+?)[，。；\s]',
            r'关联(.+?)\.(.+?)[，。；\s]',
            r'来源于(.+?)\.(.+?)[，。；\s]',
        ]

        for pattern in patterns:
            match = re.search(pattern, comment)
            if match:
                table = match.group(1).strip()
                field = match.group(2).strip()
                return f"{table}.{field}"

        return None

    def _check_system_table(self, entity: EntityDefinition):
        """检查是否系统统一表"""
        # 生成可能的表名
        possible_names = [
            f"idm_{entity.entity_name}",
            f"permission_{entity.entity_name}",
            f"mam_{entity.entity_name}",
            f"mdm_{entity.entity_name}",
            entity.entity_name.lower().replace(' ', '_'),
        ]

        for name in possible_names:
            if name in self.PROHIBITED_TABLES:
                entity.is_system_table = True
                entity.system_table_name = name
                break

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = []
        for entity in self.entities:
            entity_dict = asdict(entity)
            entity_dict['entity_type'] = entity.entity_type.value
            result.append(entity_dict)
        return {'entities': result}

    def to_json(self, indent: int = 2) -> str:
        """转换为JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


# 模块前缀映射
MODULE_PREFIX_MAP = {
    '线索管理': 'clue',
    '开发权管理': 'dev_right',
    '预立项管理': 'pre_project',
    '立项管理': 'project',
    '指标管理': 'quota',
}


def get_module_prefix(module_name: str) -> str:
    """获取模块前缀"""
    for key, prefix in MODULE_PREFIX_MAP.items():
        if key in module_name:
            return prefix
    return 'biz'


if __name__ == '__main__':
    # 测试代码
    test_content = """
## 4.1. 线索管理

### 4.1.8. 数据项

#### 线索数据项

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **数据项名称** | **类型** | **长度** | **必填** | **备注** |
| 线索ID | 文本 | 16字符 | 是 | 主键，自动生成 |
| 项目名称 | 文本 | 128汉字 | 是 | 手动输入 |
| 线索状态 | 文本 | 8汉字 | 是 | 取值：不通过、通过、放弃 |

#### 线索附件数据项

|  |  |  |  |  |
| --- | --- | --- | --- | --- |
| **数据项名称** | **类型** | **长度** | **必填** | **备注** |
| ID | 文本 | 32字符 | 是 | 主键 |
| 线索ID | 文本 | 16字符 | 是 | 引用线索.线索ID |
"""

    parser = EntityParser()
    entities = parser.parse_document(test_content)
    print(parser.to_json())
