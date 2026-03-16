#!/usr/bin/env python3
"""
PM3.0 统一表冲突检测工具
检测需求实体是否与系统统一表冲突
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ConflictType(Enum):
    """冲突类型"""
    IDM = "身份认证表"
    PERMISSION = "权限角色表"
    MAM = "主数据表(mam)"
    MDM = "主数据表(mdm)"
    ATTACHMENT = "附件表"
    WORKFLOW = "审批流表"


@dataclass
class ConflictReport:
    """冲突报告"""
    entity_name: str            # 实体名称
    conflict_table: str         # 冲突的表名
    conflict_type: ConflictType # 冲突类型
    suggestion: str             # 建议处理方式


class ConflictChecker:
    """冲突检测器"""

    # 禁止新建的系统表清单
    PROHIBITED_TABLES = {
        # idm 表 - 身份认证
        'idm_oauth_client': ConflictType.IDM,
        'idm_oauth_client_user': ConflictType.IDM,
        'idm_org': ConflictType.IDM,
        'idm_position': ConflictType.IDM,
        'idm_tenant': ConflictType.IDM,
        'idm_tenant_user': ConflictType.IDM,
        'idm_user': ConflictType.IDM,
        'idm_user_org': ConflictType.IDM,

        # permission 表 - 权限角色
        'permission_role': ConflictType.PERMISSION,
        'permission_role_apply_record': ConflictType.PERMISSION,
        'permission_role_approver': ConflictType.PERMISSION,
        'permission_role_assign': ConflictType.PERMISSION,
        'permission_role_btn_ref': ConflictType.PERMISSION,
        'permission_role_data_range': ConflictType.PERMISSION,
        'permission_role_field': ConflictType.PERMISSION,
        'permission_role_field_ref': ConflictType.PERMISSION,
        'permission_role_group': ConflictType.PERMISSION,
        'permission_role_operation': ConflictType.PERMISSION,
        'permission_role_org_parse': ConflictType.PERMISSION,
        'permission_role_relation': ConflictType.PERMISSION,
        'permission_role_resource': ConflictType.PERMISSION,
        'permission_role_row_ref': ConflictType.PERMISSION,
        'permission_role_user_data_range': ConflictType.PERMISSION,
        'permission_group_role': ConflictType.PERMISSION,

        # mam 表 - 主数据
        'mam_area': ConflictType.MAM,
        'mam_person': ConflictType.MAM,

        # mdm 表 - 主数据
        'mdm_centralized': ConflictType.MDM,
        'mdm_city': ConflictType.MDM,
        'mdm_company': ConflictType.MDM,
        'mdm_country': ConflictType.MDM,
        'mdm_currency': ConflictType.MDM,
        'mdm_dept': ConflictType.MDM,
        'mdm_dept_view': ConflictType.MDM,
        'mdm_dept_view_prd': ConflictType.MDM,
        'mdm_dept_view_prd_new': ConflictType.MDM,
        'mdm_equity_transfer_view': ConflictType.MDM,
        'mdm_language': ConflictType.MDM,
        'mdm_language_view': ConflictType.MDM,
        'mdm_material_category': ConflictType.MDM,
        'mdm_position': ConflictType.MDM,
        'mdm_profit_center': ConflictType.MDM,
        'mdm_profit_center_prd': ConflictType.MDM,
        'mdm_project': ConflictType.MDM,
        'mdm_project_view': ConflictType.MDM,
        'mdm_province': ConflictType.MDM,
        'mdm_reg_cer_type': ConflictType.MDM,
        'mdm_request_og': ConflictType.MDM,
        'mdm_sap': ConflictType.MDM,
        'mdm_subsidiary': ConflictType.MDM,
        'mdm_supply_category': ConflictType.MDM,
        'mdm_unit': ConflictType.MDM,
    }

    # 特殊实体关键词映射
    ENTITY_KEYWORDS = {
        # 用户相关
        '用户': ['idm_user'],
        '人员': ['idm_user', 'mam_person'],
        '账号': ['idm_user'],
        '登录': ['idm_user'],

        # 组织相关
        '组织': ['idm_org', 'mdm_dept'],
        '部门': ['mdm_dept'],
        '公司': ['mdm_company'],
        '机构': ['idm_org'],

        # 角色权限
        '角色': ['permission_role'],
        '权限': ['permission_role'],
        '岗位': ['idm_position', 'mdm_position'],

        # 地域
        '区域': ['mam_area'],
        '城市': ['mdm_city'],
        '省份': ['mdm_province'],
        '国家': ['mdm_country'],

        # 项目
        '项目': ['mdm_project'],

        # 附件
        '附件': ['pm_attachment'],
    }

    def check_entity(self, entity_name: str) -> Optional[ConflictReport]:
        """
        检查单个实体是否冲突

        Args:
            entity_name: 实体名称

        Returns:
            ConflictReport 或 None
        """
        entity_lower = entity_name.lower().replace(' ', '_')

        # 直接匹配
        if entity_lower in self.PROHIBITED_TABLES:
            conflict_type = self.PROHIBITED_TABLES[entity_lower]
            return ConflictReport(
                entity_name=entity_name,
                conflict_table=entity_lower,
                conflict_type=conflict_type,
                suggestion=self._get_suggestion(conflict_type, entity_lower)
            )

        # 前缀匹配
        for prefix in ['idm_', 'permission_', 'mam_', 'mdm_']:
            if entity_lower.startswith(prefix):
                table_name = entity_lower
                conflict_type = self._get_conflict_type_by_prefix(prefix)
                return ConflictReport(
                    entity_name=entity_name,
                    conflict_table=table_name,
                    conflict_type=conflict_type,
                    suggestion=self._get_suggestion(conflict_type, table_name)
                )

        # 关键词匹配
        for keyword, tables in self.ENTITY_KEYWORDS.items():
            if keyword in entity_name:
                # 返回第一个匹配的系统表
                table_name = tables[0]
                if table_name in self.PROHIBITED_TABLES or table_name == 'pm_attachment':
                    conflict_type = self.PROHIBITED_TABLES.get(table_name, ConflictType.ATTACHMENT)
                    return ConflictReport(
                        entity_name=entity_name,
                        conflict_table=table_name,
                        conflict_type=conflict_type,
                        suggestion=self._get_suggestion(conflict_type, table_name)
                    )

        return None

    def check_entities(self, entity_names: List[str]) -> List[ConflictReport]:
        """
        批量检查实体

        Args:
            entity_names: 实体名称列表

        Returns:
            冲突报告列表
        """
        conflicts = []
        checked = set()  # 避免重复报告

        for entity_name in entity_names:
            report = self.check_entity(entity_name)
            if report and report.conflict_table not in checked:
                conflicts.append(report)
                checked.add(report.conflict_table)

        return conflicts

    def _get_conflict_type_by_prefix(self, prefix: str) -> ConflictType:
        """根据前缀获取冲突类型"""
        prefix_map = {
            'idm_': ConflictType.IDM,
            'permission_': ConflictType.PERMISSION,
            'mam_': ConflictType.MAM,
            'mdm_': ConflictType.MDM,
        }
        return prefix_map.get(prefix, ConflictType.MDM)

    def _get_suggestion(self, conflict_type: ConflictType, table_name: str) -> str:
        """获取建议处理方式"""
        suggestions = {
            ConflictType.IDM: f"复用 {table_name} 表，通过逻辑外键关联（如 user_id 字段）",
            ConflictType.PERMISSION: f"复用 {table_name} 表，不新建角色权限相关表",
            ConflictType.MAM: f"复用 {table_name} 表，通过逻辑外键关联",
            ConflictType.MDM: f"复用 {table_name} 表，通过 mdm_xxx_id 字段关联",
            ConflictType.ATTACHMENT: "复用 pm_attachment 统一附件表，使用 business_type 区分业务",
            ConflictType.WORKFLOW: "复用 Activity 工作流引擎，通过 business_key 关联业务表",
        }
        return suggestions.get(conflict_type, f"复用 {table_name} 表")

    def generate_report(self, conflicts: List[ConflictReport]) -> str:
        """
        生成冲突检测报告

        Args:
            conflicts: 冲突报告列表

        Returns:
            Markdown 格式的报告
        """
        if not conflicts:
            return """
> [!SUCCESS]
> ## 统一表冲突检测报告
>
> 未检测到与系统统一表的冲突，所有实体均可新建。
"""

        lines = [
            "> [!WARNING]",
            "> ## 统一表冲突检测报告",
            ">",
            "> 以下实体与系统统一表冲突，建议复用已有表结构：",
            ">",
            "> | 实体名称 | 冲突表名 | 冲突类型 | 建议处理方式 |",
            "> |---------|---------|---------|-------------|",
        ]

        for c in conflicts:
            lines.append(f"> | {c.entity_name} | {c.conflict_table} | {c.conflict_type.value} | {c.suggestion} |")

        lines.append(">")
        lines.append("> **设计约束**：")
        lines.append("> 1. 身份认证：通过 idm_user.id 关联用户，通过 idm_org.id 关联组织")
        lines.append("> 2. 权限角色：复用 permission_role 等权限表，通过 role_id/user_id 关联")
        lines.append("> 3. 主数据引用：通过 mdm_xxx_id 字段关联已有主数据表")
        lines.append("> 4. 附件管理：统一使用 pm_attachment，通过 business_type 区分业务类型")

        return '\n'.join(lines)

    def is_attachment_entity(self, entity_name: str) -> bool:
        """检查是否为附件实体"""
        return '附件' in entity_name or 'attachment' in entity_name.lower()

    def is_workflow_entity(self, entity_name: str) -> bool:
        """检查是否为审批流实体"""
        keywords = ['审批', '流程', '节点', 'workflow', 'approval']
        return any(kw in entity_name for kw in keywords)

    def get_recommended_table_name(self, entity_name: str,
                                    module_prefix: str) -> Tuple[str, bool]:
        """
        获取推荐的表名

        Args:
            entity_name: 实体名称
            module_prefix: 模块前缀

        Returns:
            (表名, 是否复用已有表)
        """
        # 检查冲突
        conflict = self.check_entity(entity_name)

        if conflict:
            return conflict.conflict_table, True

        # 生成新表名
        table_name = f"pm_{module_prefix}_{entity_name.lower().replace(' ', '_')}"
        return table_name, False


def check_before_design(entities: List[Dict]) -> Dict:
    """
    设计前检查入口

    Args:
        entities: 实体列表，每个实体包含 entity_name

    Returns:
        {
            'conflicts': List[ConflictReport],
            'can_create': List[str],  # 可以新建的实体
            'must_reuse': List[str],  # 必须复用的实体
        }
    """
    checker = ConflictChecker()

    entity_names = [e.get('entity_name', '') for e in entities]
    conflicts = checker.check_entities(entity_names)

    conflict_names = {c.entity_name for c in conflicts}
    can_create = [name for name in entity_names if name not in conflict_names]
    must_reuse = list(conflict_names)

    return {
        'conflicts': conflicts,
        'can_create': can_create,
        'must_reuse': must_reuse,
        'report': checker.generate_report(conflicts),
    }


if __name__ == '__main__':
    # 测试代码
    checker = ConflictChecker()

    test_entities = [
        '线索',
        '用户',  # 应该冲突 idm_user
        '部门',  # 应该冲突 mdm_dept
        '角色',  # 应该冲突 permission_role
        '附件',  # 应该建议复用 pm_attachment
        '开发权',
    ]

    conflicts = checker.check_entities(test_entities)
    print(checker.generate_report(conflicts))
