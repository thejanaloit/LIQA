# TLS / mTLS

Put Caddy or nginx in front of Control :8788 with your certificate.
Worker talks outbound HTTPS to Control.
Optional mTLS: client cert on Worker, verify on proxy.
Local host 127.0.0.1 may stay HTTP.
