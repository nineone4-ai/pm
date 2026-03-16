# 异常处理模板

## 1. BusinessErrorEnum（错误码枚举）

```java
package com.sungrow.pm.{module}.exception;

import cn.iiot.myth.framework.common.api.IResultCode;
import lombok.AllArgsConstructor;
import lombok.Getter;

/**
 * <p>
 * 业务错误码枚举
 * </p>
 *
 * @author {author}
 * @since {date}
 */
@Getter
@AllArgsConstructor
public enum BusinessErrorEnum implements IResultCode {
    
    SUCCESS("200", "操作成功"),
    
    SYSTEM_ERROR("500", "系统异常，请联系管理员"),
    PARAM_IS_NULL("400", "参数不能为空"),
    DATA_NOT_FOUND("404", "数据不存在"),
    DATA_ALREADY_EXISTS("409", "数据已存在"),
    
    SAVE_ERROR("1001", "保存失败"),
    UPDATE_ERROR("1002", "更新失败"),
    DELETE_ERROR("1003", "删除失败"),
    
    PERMISSION_DENIED("403", "没有操作权限");
    
    private final String code;
    private final String message;
}
```

## 2. BusinessException（业务异常）

```java
package com.sungrow.pm.{module}.exception;

import cn.iiot.myth.framework.common.api.IResultCode;
import lombok.Getter;

/**
 * <p>
 * 业务异常
 * </p>
 *
 * @author {author}
 * @since {date}
 */
@Getter
public class BusinessException extends RuntimeException {
    
    private final int code;
    private final String message;
    
    public BusinessException(IResultCode errorCode) {
        super(errorCode.getMessage());
        this.code = Integer.parseInt(errorCode.getCode());
        this.message = errorCode.getMessage();
    }
    
    public BusinessException(int code, String message) {
        super(message);
        this.code = code;
        this.message = message;
    }
    
    public BusinessException(String message) {
        super(message);
        this.code = 500;
        this.message = message;
    }
}
```

## 3. GlobalExceptionHandler（全局异常处理器）

```java
package com.sungrow.pm.{module}.exception;

import cn.iiot.myth.framework.common.api.RestResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.validation.BindException;
import org.springframework.validation.FieldError;
import org.springframework.web.HttpRequestMethodNotSupportedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.util.List;
import java.util.stream.Collectors;

/**
 * <p>
 * 全局异常处理器
 * </p>
 *
 * @author {author}
 * @since {date}
 */
@Slf4j
@RestControllerAdvice
public class GlobalExceptionHandler {

    /**
     * 处理业务异常
     */
    @ExceptionHandler(BusinessException.class)
    public RestResponse<Void> handleBusinessException(BusinessException e) {
        log.error("业务异常：", e);
        return RestResponse.failed(e.getCode(), e.getMessage());
    }

    /**
     * 处理参数校验异常（@Valid）
     */
    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public RestResponse<Void> handleMethodArgumentNotValidException(MethodArgumentNotValidException e) {
        List<FieldError> fieldErrors = e.getBindingResult().getFieldErrors();
        String message = fieldErrors.stream()
            .map(error -> error.getField() + ": " + error.getDefaultMessage())
            .collect(Collectors.joining("; "));
        log.error("参数校验异常：{}", message);
        return RestResponse.failed(400, message);
    }

    /**
     * 处理绑定异常
     */
    @ExceptionHandler(BindException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public RestResponse<Void> handleBindException(BindException e) {
        List<FieldError> fieldErrors = e.getBindingResult().getFieldErrors();
        String message = fieldErrors.stream()
            .map(error -> error.getField() + ": " + error.getDefaultMessage())
            .collect(Collectors.joining("; "));
        log.error("绑定异常：{}", message);
        return RestResponse.failed(400, message);
    }

    /**
     * 处理请求方法不支持异常
     */
    @ExceptionHandler(HttpRequestMethodNotSupportedException.class)
    @ResponseStatus(HttpStatus.METHOD_NOT_ALLOWED)
    public RestResponse<Void> handleHttpRequestMethodNotSupportedException(HttpRequestMethodNotSupportedException e) {
        log.error("请求方法不支持：", e);
        return RestResponse.failed(405, "不支持的请求方法");
    }

    /**
     * 处理其他异常
     */
    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public RestResponse<Void> handleException(Exception e) {
        log.error("系统异常：", e);
        return RestResponse.failed(500, "系统异常，请联系管理员");
    }
}
```

## 错误码规范

| 错误码范围 | 用途 |
|-----------|------|
| 200 | 成功 |
| 400 | 参数错误 |
| 403 | 无权限 |
| 404 | 数据不存在 |
| 405 | 请求方法不支持 |
| 409 | 数据冲突 |
| 500 | 系统异常 |
| 1001-1099 | 业务操作错误 |

## 使用示例

```java
// 抛出业务异常
if (ObjectUtil.isNull(entity)) {
    throw new BusinessException(BusinessErrorEnum.DATA_NOT_FOUND);
}

// 抛出带自定义消息的异常
if (StrUtil.isBlank(name)) {
    throw new BusinessException(400, "名称不能为空");
}
```
