services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      SECRET_KEY: "change-this-secret-before-production"
      DATABASE_URL: "sqlite:////app/data/blog.db"
      REDIS_HOST: "redis"
      REDIS_PORT: "6379"
      REDIS_DB: "0"
      ADMIN_USERNAME: "admin"
      ADMIN_EMAIL: "admin@blog.com"
      ADMIN_PASSWORD: "123"
    volumes:
      - ./data:/app/data
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
