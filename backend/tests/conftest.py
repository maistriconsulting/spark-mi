import os

os.environ.setdefault("DB_HOST", "127.0.0.1")
os.environ.setdefault("DB_NAME", "spark_test")
os.environ.setdefault("DB_USER", "spark_test")
os.environ.setdefault("DB_PASSWORD", "spark_test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-that-is-long-enough-for-unit-tests")
