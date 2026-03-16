# Service 模板

## 1. Service 接口

```java
package com.sungrow.pm.{module}.service;

import cn.iiot.myth.starter.orm.service.IBaseService;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.sungrow.pm.{module}.dto.{Business}AddParam;
import com.sungrow.pm.{module}.dto.{Business}DTO;
import com.sungrow.pm.{module}.dto.{Business}EditParam;
import com.sungrow.pm.{module}.dto.{Business}QueryParam;
import com.sungrow.pm.{module}.entity.{Business};

/**
 * <p>
 * {业务描述}服务接口
 * </p>
 *
 * @author {author}
 * @since {date}
 */
public interface I{Business}Service extends IBaseService<{Business}> {
    
    /**
     * 分页查询
     * @param param 查询参数
     * @return 分页结果
     */
    IPage<{Business}DTO> pageList({Business}QueryParam param);
    
    /**
     * 新增
     * @param param 新增参数
     * @return 是否成功
     */
    boolean save({Business}AddParam param);
    
    /**
     * 修改
     * @param param 修改参数
     * @return 是否成功
     */
    boolean update({Business}EditParam param);
    
    /**
     * 详情
     * @param id 主键ID
     * @return 详情DTO
     */
    {Business}DTO getDetail(String id);
    
    /**
     * 删除
     * @param id 主键ID
     * @return 是否成功
     */
    boolean delete(String id);
}
```

## 2. Service 实现

```java
package com.sungrow.pm.{module}.service.impl;

import cn.hutool.core.util.ObjectUtil;
import cn.hutool.core.util.StrUtil;
import cn.iiot.myth.starter.auth.util.AuthUtils;
import cn.iiot.myth.starter.orm.service.impl.BaseServiceImpl;
import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.core.metadata.IPage;
import com.baomidou.mybatisplus.core.toolkit.IdWorker;
import com.baomidou.mybatisplus.core.toolkit.StringUtils;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.sungrow.pm.{module}.constants.Constants;
import com.sungrow.pm.{module}.dto.{Business}AddParam;
import com.sungrow.pm.{module}.dto.{Business}DTO;
import com.sungrow.pm.{module}.dto.{Business}EditParam;
import com.sungrow.pm.{module}.dto.{Business}QueryParam;
import com.sungrow.pm.{module}.entity.{Business};
import com.sungrow.pm.{module}.exception.BusinessErrorEnum;
import com.sungrow.pm.{module}.exception.BusinessException;
import com.sungrow.pm.{module}.mapper.{Business}Mapper;
import com.sungrow.pm.{module}.service.I{Business}Service;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.BeanUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Date;
import java.util.List;

/**
 * <p>
 * {业务描述}服务实现
 * </p>
 *
 * @author {author}
 * @since {date}
 */
@Slf4j
@Service
public class {Business}ServiceImpl extends BaseServiceImpl<{Business}Mapper, {Business}> 
        implements I{Business}Service {

    @Autowired
    private {Business}Mapper {business}Mapper;

    /**
     * 分页查询
     */
    @Override
    public IPage<{Business}DTO> pageList({Business}QueryParam param) {
        // 1. 构建分页对象
        Page<{Business}DTO> page = new Page<>(param.getPageNo(), param.getPageSize());

        // 2. 构建查询条件
        LambdaQueryWrapper<{Business}> wrapper = new LambdaQueryWrapper<>();
        wrapper.like(StringUtils.isNotBlank(param.getName()), 
            {Business}::getName, param.getName());
        wrapper.eq(param.getStatus() != null, 
            {Business}::getStatus, param.getStatus());
        wrapper.orderByDesc({Business}::getCreateTime);

        // 3. 执行查询
        Page<{Business}> resultPage = this.page(page, wrapper);
        
        // 4. 转换为 DTO
        List<{Business}DTO> dtoList = resultPage.getRecords().stream()
            .map(this::convertToDTO)
            .collect(java.util.stream.Collectors.toList());
        
        Page<{Business}DTO> dtoPage = new Page<>(
            resultPage.getCurrent(), resultPage.getSize(), resultPage.getTotal());
        dtoPage.setRecords(dtoList);
        
        return dtoPage;
    }

    /**
     * 新增
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean save({Business}AddParam param) {
        try {
            // 1. 参数校验
            validateParam(param);
            
            // 2. 构建实体
            {Business} entity = new {Business}();
            BeanUtils.copyProperties(param, entity);
            entity.setId(IdWorker.getIdStr());
            entity.setCreateTime(new Date());
            entity.setCreateBy(AuthUtils.getUser().getUid());
            entity.setDeleteFlag(0);
            
            // 3. 保存
            return this.save(entity);
        } catch (Exception ex) {
            log.error("新增{业务名}异常：{}", Constants.EXCEPTION_MESSAGE, ex);
            throw new BusinessException(BusinessErrorEnum.SAVE_ERROR);
        }
    }

    /**
     * 修改
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean update({Business}EditParam param) {
        try {
            // 1. 查询原数据
            {Business} entity = this.getById(param.getId());
            if (ObjectUtil.isNull(entity)) {
                throw new BusinessException(BusinessErrorEnum.DATA_NOT_FOUND);
            }
            
            // 2. 更新字段
            entity.setName(param.getName());
            // ... 其他字段
            
            entity.setUpdateTime(new Date());
            entity.setUpdateBy(AuthUtils.getUser().getUid());
            
            // 3. 更新
            return this.updateById(entity);
        } catch (Exception ex) {
            log.error("修改{业务名}异常：{}", Constants.EXCEPTION_MESSAGE, ex);
            throw new BusinessException(BusinessErrorEnum.UPDATE_ERROR);
        }
    }

    /**
     * 详情
     */
    @Override
    public {Business}DTO getDetail(String id) {
        {Business} entity = this.getById(id);
        if (ObjectUtil.isNull(entity)) {
            throw new BusinessException(BusinessErrorEnum.DATA_NOT_FOUND);
        }
        return convertToDTO(entity);
    }

    /**
     * 删除
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean delete(String id) {
        {Business} entity = new {Business}();
        entity.setId(id);
        entity.setDeleteFlag(1);
        return this.updateById(entity);
    }

    /**
     * 参数校验
     */
    private void validateParam({Business}AddParam param) {
        if (StrUtil.isBlank(param.getName())) {
            throw new BusinessException(BusinessErrorEnum.PARAM_IS_NULL);
        }
    }

    /**
     * 实体转 DTO
     */
    private {Business}DTO convertToDTO({Business} entity) {
        {Business}DTO dto = new {Business}DTO();
        BeanUtils.copyProperties(entity, dto);
        return dto;
    }
}
```

## 关键模式

### 事务管理
```java
@Transactional(rollbackFor = Exception.class)
```

### 异常处理
```java
try {
    // 业务逻辑
} catch (Exception ex) {
    log.error("操作异常：{}", Constants.EXCEPTION_MESSAGE, ex);
    throw new BusinessException(BusinessErrorEnum.SAVE_ERROR);
}
```

### 分页查询
```java
Page<DTO> page = new Page<>(param.getPageNo(), param.getPageSize());
Page<Entity> resultPage = this.page(page, wrapper);
```

### 实体转换
```java
BeanUtils.copyProperties(source, target);
```
