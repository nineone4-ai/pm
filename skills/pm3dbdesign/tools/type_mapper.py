#!/usr/bin/env python3
"""
PM3.0 字段类型映射工具
将需求文档中的类型映射为 MySQL 类型
"""

import re
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class MySQLType:
    """MySQL 类型定义"""
    data_type: str      # 数据类型（VARCHAR, DECIMAL等）
    length: str         # 长度/精度
    nullable: bool      # 是否可为空
    default_value: Optional[str]  # 默认值
    comment: str        # 注释


class TypeMapper:
    """类型映射器"""

    # 需求类型到 MySQL 类型的映射
    TYPE_MAPPING = {
        '文本': 'VARCHAR',
        '数值': 'DECIMAL',
        '日期型': 'DATE',
        '时间型': 'DATETIME',
        '布尔值': 'TINYINT',
        '布尔': 'TINYINT',
    }

    # 默认长度配置
    DEFAULT_LENGTHS = {
        'VARCHAR': '255',
        'DECIMAL': '18,2',
        'TINYINT': '1',
        'DATE': '',
        'DATETIME': '',
        'TEXT': '',
        'BIGINT': '',
        'INT': '',
    }

    # 审计字段定义
    AUDIT_FIELDS = {
        'id': MySQLType('VARCHAR', '32', False, None, '主键ID'),
        'create_by': MySQLType('VARCHAR', '64', True, None, '创建人ID'),
        'update_by': MySQLType('VARCHAR', '64', True, None, '更新人ID'),
        'create_time': MySQLType('DATETIME', '', False, 'CURRENT_TIMESTAMP', '创建时间'),
        'update_time': MySQLType('DATETIME', '', True, 'CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP', '更新时间'),
        'is_del': MySQLType('TINYINT', '1', False, '0', '软删除标记：0-未删除，1-已删除'),
        'remark': MySQLType('VARCHAR', '1000', True, None, '备注'),
    }

    def map_type(self, req_type: str, req_length: Optional[str],
                 required: bool, comment: str) -> MySQLType:
        """
        将需求类型映射为 MySQL 类型

        Args:
            req_type: 需求文档中的类型（文本/数值/日期型/时间型/布尔值）
            req_length: 长度（如"16字符"、"128汉字"、"精度2位"）
            required: 是否必填
            comment: 备注

        Returns:
            MySQLType 对象
        """
        # 标准化类型名称
        req_type = req_type.strip() if req_type else '文本'

        # 获取基础 MySQL 类型
        mysql_base = self.TYPE_MAPPING.get(req_type, 'VARCHAR')

        # 解析长度
        length = self._parse_length(req_type, req_length, comment)

        # 确定是否可为空
        nullable = not required

        # 提取默认值
        default_value = self._extract_default(comment)

        # 构建完整注释
        full_comment = self._build_comment(req_type, comment)

        return MySQLType(
            data_type=mysql_base,
            length=length,
            nullable=nullable,
            default_value=default_value,
            comment=full_comment
        )

    def _parse_length(self, req_type: str, req_length: Optional[str],
                      comment: str) -> str:
        """解析长度"""
        if not req_length:
            return self.DEFAULT_LENGTHS.get(self.TYPE_MAPPING.get(req_type, 'VARCHAR'), '255')

        req_length = req_length.strip()

        # 文本类型
        if req_type == '文本':
            # 匹配 "N字符" 或 "N汉字"
            match = re.match(r'(\d+)\s*字符', req_length)
            if match:
                return match.group(1)

            match = re.match(r'(\d+)\s*汉字', req_length)
            if match:
                # 一个汉字 = 3字节（UTF-8）
                return str(int(match.group(1)) * 3)

            # 纯数字
            if req_length.isdigit():
                return req_length

        # 数值类型
        if req_type == '数值':
            # 匹配 "精度N位"
            match = re.search(r'精度\s*(\d+)\s*位', req_length + ' ' + comment)
            if match:
                precision = match.group(1)
                return f'18,{precision}'

            # 匹配整数
            if '整数' in comment or '整型' in comment:
                return ''  # 使用 INT 不指定长度

            return '18,2'  # 默认精度

        return self.DEFAULT_LENGTHS.get(self.TYPE_MAPPING.get(req_type, 'VARCHAR'), '255')

    def _extract_default(self, comment: str) -> Optional[str]:
        """从注释中提取默认值"""
        patterns = [
            r'默认[:：]?\s*([^，。；]+)',
            r'默认值[:：]?\s*([^，。；]+)',
            r'默认显示为\s*([^，。；]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, comment)
            if match:
                default = match.group(1).strip()
                # 转换默认值
                if default in ['0', '0.00', "''", 'CURRENT_TIMESTAMP']:
                    return default
                if default == '空' or default == 'null' or default == 'NULL':
                    return 'NULL'
                # 数值型默认值
                if re.match(r'^\d+(\.\d+)?$', default):
                    return default
                # 字符串默认值
                return f"'{default}'"

        return None

    def _build_comment(self, req_type: str, original_comment: str) -> str:
        """构建字段注释"""
        # 移除默认值说明，保留核心注释
        comment = re.sub(r'默认[:：].*?[，。；]', '', original_comment)
        comment = comment.strip()

        # 保留关键信息
        important_keywords = ['单位', '精度', '格式', '取值', '关联', '引用']
        lines = []

        for line in comment.split('\n'):
            line = line.strip()
            if any(kw in line for kw in important_keywords):
                lines.append(line)

        if lines:
            return ' '.join(lines)

        return comment or req_type

    def get_audit_fields(self) -> dict:
        """获取审计字段定义"""
        return self.AUDIT_FIELDS.copy()

    def is_audit_field(self, field_name: str) -> bool:
        """检查是否为审计字段"""
        return field_name.lower() in ['id', 'create_by', 'update_by',
                                       'create_time', 'update_time',
                                       'is_del', 'remark']

    def map_enum_to_tinyint(self, enum_values: list) -> Tuple[str, str]:
        """
        将枚举值映射为 TINYINT

        Args:
            enum_values: 枚举值列表

        Returns:
            (类型定义, 枚举映射注释)
        """
        if not enum_values:
            return 'TINYINT(1)', ''

        # 生成枚举映射注释
        enum_map = []
        for i, val in enumerate(enum_values):
            enum_map.append(f'{i}-{val}')

        # TINYINT 范围 -128~127，对于小枚举足够
        if len(enum_values) <= 127:
            return 'TINYINT', '，'.join(enum_map)

        return 'INT', '，'.join(enum_map)

    def convert_status_field(self, field_name: str, enum_values: list) -> MySQLType:
        """
        转换状态字段为数值型

        Args:
            field_name: 字段名
            enum_values: 枚举值列表

        Returns:
            MySQLType
        """
        type_def, enum_comment = self.map_enum_to_tinyint(enum_values)

        return MySQLType(
            data_type=type_def.replace('(1)', ''),
            length='1' if 'TINYINT' in type_def else '',
            nullable=False,
            default_value='0',
            comment=f'{field_name}：{enum_comment}'
        )

    def get_mysql_type_string(self, mysql_type: MySQLType) -> str:
        """生成 MySQL 类型字符串"""
        type_str = mysql_type.data_type

        if mysql_type.length:
            type_str += f"({mysql_type.length})"

        # NULL/NOT NULL
        if mysql_type.nullable:
            type_str += " DEFAULT NULL"
        else:
            type_str += " NOT NULL"

        # 默认值
        if mysql_type.default_value:
            if 'CURRENT_TIMESTAMP' in mysql_type.default_value:
                type_str += f" DEFAULT {mysql_type.default_value}"
            elif mysql_type.default_value == 'NULL':
                type_str = type_str.replace("NOT NULL", "DEFAULT NULL")
            else:
                type_str += f" DEFAULT {mysql_type.default_value}"

        return type_str

    def generate_column_def(self, field_name: str, mysql_type: MySQLType) -> str:
        """生成列定义 SQL"""
        type_str = self.get_mysql_type_string(mysql_type)
        return f"  `{field_name}` {type_str} COMMENT '{mysql_type.comment}',"


# 常用字段类型推荐
COMMON_FIELD_TYPES = {
    'id': ('VARCHAR', '32', '主键ID'),
    'code': ('VARCHAR', '50', '编码'),
    'name': ('VARCHAR', '100', '名称'),
    'title': ('VARCHAR', '200', '标题'),
    'status': ('TINYINT', '1', '状态'),
    'type': ('TINYINT', '1', '类型'),
    'sort': ('INT', '', '排序'),
    'remark': ('VARCHAR', '1000', '备注'),
    'content': ('TEXT', '', '内容'),
    'create_by': ('VARCHAR', '64', '创建人'),
    'update_by': ('VARCHAR', '64', '更新人'),
    'create_time': ('DATETIME', '', '创建时间'),
    'update_time': ('DATETIME', '', '更新时间'),
    'is_del': ('TINYINT', '1', '软删除标记'),
}


if __name__ == '__main__':
    # 测试代码
    mapper = TypeMapper()

    test_cases = [
        ('文本', '16字符', True, '主键'),
        ('文本', '128汉字', True, '项目名称'),
        ('数值', '', True, '精度2位小数，单位：MW'),
        ('日期型', '', True, '获取日期'),
        ('时间型', '', False, '创建时间'),
        ('布尔值', '', False, '是否长期有效'),
    ]

    for req_type, req_length, required, comment in test_cases:
        mysql_type = mapper.map_type(req_type, req_length, required, comment)
        print(f"{req_type}({req_length}) -> {mapper.get_mysql_type_string(mysql_type)}")
