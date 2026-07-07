# 外部系统适配层规范

`app/integration/` 只放外部系统客户端、认证、传输对象和协议适配代码。

## 目录约定

每接入 1 个外部系统，创建 1 个独立子目录：

```text
app/integration/<provider>/
  __init__.py
  client.py
  dto.py
  auth.py
```

如需令牌缓存、分模块客户端或重试策略，可在同一子目录内继续拆分：

```text
token_cache.py
upload_client.py
query_client.py
```

## 边界规则

- `service` 可以调用 `integration`。
- `repository` 禁止调用 `integration`。
- `integration` 禁止写业务判断，只负责协议、认证、请求、响应解析和错误映射。
- 外部响应必须先转换为内部 DTO，再交给 `service`。
- 禁止在适配层硬编码密钥、令牌、私有地址。
- 外部超时、认证失败、响应格式异常必须转换为项目业务异常或明确的适配层异常。
