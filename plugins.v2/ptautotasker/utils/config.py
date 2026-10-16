class Config:
    # PT 站点普遍套 Cloudflare + DB 查询，慢站响应常超过 10s 导致
    # "HTTPSConnectionPool(...): Read timed out"，再次放宽到 30 秒。
    REQUEST_TIMEOUT = 30  # Default timeout for requests in seconds
