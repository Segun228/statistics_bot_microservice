# Statistics Bot Platform 📊

Многофункциональная платформа для статистического анализа, A/B тестирования и машинного обучения с Telegram-ботом и веб-интерфейсом.

## 🏆 Технологический стек

### 🔧 Основные технологии
![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/-Django-092E20?style=flat-square&logo=django&logoColor=white)
![Django REST](https://img.shields.io/badge/-Django_REST-FF1709?style=flat-square&logo=django&logoColor=white)
![Aiogram](https://img.shields.io/badge/-Aiogram-0088CC?style=flat-square&logo=telegram&logoColor=white)

### 🗄️ Базы данных
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)
![ClickHouse](https://img.shields.io/badge/-ClickHouse-FFCC02?style=flat-square&logo=clickhouse&logoColor=black)
![Redis](https://img.shields.io/badge/-Redis-DC382D?style=flat-square&logo=redis&logoColor=white)

### 🚀 Брокеры сообщений
![Apache Kafka](https://img.shields.io/badge/-Apache_Kafka-231F20?style=flat-square&logo=apachekafka&logoColor=white)
![Zookeeper](https://img.shields.io/badge/-Zookeeper-FFFFFF?style=flat-square&logo=apachezookeeper&logoColor=black)

### 📊 Мониторинг и аналитика
![Grafana](https://img.shields.io/badge/-Grafana-F46800?style=flat-square&logo=grafana&logoColor=white)
![Prometheus](https://img.shields.io/badge/-Prometheus-E6522C?style=flat-square&logo=prometheus&logoColor=white)
![Apache Superset](https://img.shields.io/badge/-Apache_Superset-1E90FF?style=flat-square&logo=apache&logoColor=white)

### 🐳 Контейнеризация и оркестрация
![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Docker Compose](https://img.shields.io/badge/-Docker_Compose-2496ED?style=flat-square&logo=docker&logoColor=white)

### 📈 Машинное обучение
![Scikit-learn](https://img.shields.io/badge/-Scikit--Learn-F7931E?style=flat-square&logo=scikitlearn&logoColor=white)
![XGBoost](https://img.shields.io/badge/-XGBoost-3776AB?style=flat-square&logo=xgboost&logoColor=white)
![CatBoost](https://img.shields.io/badge/-CatBoost-00C4CC?style=flat-square)
![LightGBM](https://img.shields.io/badge/-LightGBM-792EE5?style=flat-square)

### 📊 Статистика и анализ данных
![Pandas](https://img.shields.io/badge/-Pandas-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/-NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![SciPy](https://img.shields.io/badge/-SciPy-8CAAE6?style=flat-square&logo=scipy&logoColor=white)
![StatsModels](https://img.shields.io/badge/-StatsModels-8CAAE6?style=flat-square)

## 🎯 Ключевые возможности

### 📊 A/B Тестирование
![T-test](https://img.shields.io/badge/-T_test-4ECDC4?style=flat-square)
![Z-test](https://img.shields.io/badge/-Z_test-45B7D1?style=flat-square)
![ANOVA](https://img.shields.io/badge/-ANOVA-FF6B6B?style=flat-square)
![Chi-square](https://img.shields.io/badge/-Chi_square-FFA500?style=flat-square)
![Bootstrap](https://img.shields.io/badge/-Bootstrap-7965D1?style=flat-square)
![CUPED](https://img.shields.io/badge/-CUPED-67C7C7?style=flat-square)

### 📈 Распределения вероятностей
![Normal Distribution](https://img.shields.io/badge/-Normal-28a745?style=flat-square)
![Binomial Distribution](https://img.shields.io/badge/-Binomial-007bff?style=flat-square)
![Poisson Distribution](https://img.shields.io/badge/-Poisson-6f42c1?style=flat-square)
![Exponential Distribution](https://img.shields.io/badge/-Exponential-e83e8c?style=flat-square)

### 🤖 Машинное обучение
![Regression](https://img.shields.io/badge/-Regression-20c997?style=flat-square)
![Classification](https://img.shields.io/badge/-Classification-fd7e14?style=flat-square)
![Clustering](https://img.shields.io/badge/-Clustering-e83e8c?style=flat-square)
![Gradient Boosting](https://img.shields.io/badge/-Gradient_Boosting-6f42c1?style=flat-square)


## 📋 Содержание

- [Обзор](#обзор)
- [Архитектура](#архитектура)
- [Функциональности](#функциональности)
- [Установка и запуск](#установка-и-запуск)
- [API Документация](#api-документация)
- [Мониторинг](#мониторинг)
- [Разработка](#разработка)

## 🎯 Обзор

Statistics Bot Platform - это комплексное решение для статистического анализа данных, проведения A/B тестов и построения ML моделей. Платформа предоставляет:

- **Telegram бот** для интерактивной работы
- **REST API** для програмmatic доступа
- **Веб-интерфейсы** для визуализации и администрирования
- **Распределенную архитектуру** с использованием микросервисов
- **Мониторинг и аналитику** в реальном времени

## 🏗 Архитектура

Платформа построена на микросервисной архитектуре с использованием следующих компонентов:

### Основные сервисы

| Сервис | Назначение | Порт |
|--------|------------|------|
| `backend` | Django REST API | 8000 |
| `bot` | Telegram бот | 8080 |
| `analytics` | Аналитика и ClickHouse | 8001 |
| `logs` | Централизованное логирование | 8002 |

### Базы данных и брокеры

| Сервис | Назначение | Порт |
|--------|------------|------|
| `postgres` | Основная БД | 5432 |
| `clickhouse` | Аналитическая БД | 8123, 9000 |
| `redis` | Кэширование | 6379 |
| `kafka` | Брокер сообщений | 9092, 29092 |

### Мониторинг и визуализация

| Сервис | Назначение | Порт |
|--------|------------|------|
| `grafana` | Дашборды | 3000 |
| `prometheus` | Сбор метрик | 9090 |
| `superset` | BI аналитика | 8088 |
| `pgadmin` | Администрирование БД | 5050 |

## 🚀 Функциональности

### 📊 A/B Тестирование
- **T-тест** - сравнение средних значений
- **Z-тест** - для больших выборок
- **U-тест (Манна-Уитни)** - непараметрический тест
- **ANOVA** - дисперсионный анализ
- **Хи-квадрат** - тест на независимость
- **Тест Крамера** - анализ номинальных данных
- **Bootstrap** - ресэмплинг
- **Тест Колмогорова-Смирнова** - сравнение распределений
- **Тест Шапиро-Уилка** - проверка нормальности
- **Тест Лиллиефорса** - нормальность с оценкой параметров
- **Тест Андерсона-Дарлинга** - проверка распределений
- **CUPED** - повышение чувствительности тестов
- **CUPAC** - ковариатная адаптация
- **Расчет MDE** - минимального детектируемого эффекта
- **Расчет размера выборки**

### 📈 Распределения вероятностей
- **Нормальное** - `normal`
- **Биномиальное** - `binomial` 
- **Пуассона** - `poisson`
- **Равномерное** - `uniform`
- **Экспоненциальное** - `exponential`
- **Бета** - `beta`
- **Гамма** - `gamma`
- **Лог-нормальное** - `lognormal`
- **Хи-квадрат** - `chi2`
- **Стьюдента** - `t`
- **Фишера** - `f`
- **Геометрическое** - `geometric`
- **Гипергеометрическое** - `hypergeom`
- **Отрицательно биномиальное** - `negative_binomial`

**Операции с распределениями:**
- Расчет вероятностей
- Квантили и процентили
- Генерация выборок
- Построение графиков
- Доверительные интервалы

### 🤖 Машинное обучение
**Задачи:**
- Регрессия
- Классификация  
- Кластеризация

**Алгоритмы:**
- Линейная регрессия
- Полиномиальная регрессия
- KNN регрессия
- Градиентный бустинг
- Логистическая регрессия
- SVM классификация
- KNN классификация
- Случайный лес
- K-means кластеризация
- DBSCAN кластеризация

**Функциональности ML:**
- Создание и обучение моделей
- Предсказания
- Переобучение моделей
- Управление фичами

### 👥 Пользовательская система
- Аутентификация через Telegram
- Ролевая модель (админы/пользователи)
- CRUD операции с логированием
- Активные сессии пользователей

## ⚙️ Установка и запуск

### Предварительные требования

- Docker & Docker Compose
- Python 3.12 (для разработки)
- Telegram бот токен

### Быстрый запуск

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd statistics_bot
```

2. **Настройка окружения**
```bash
cp .env.example .env
# Отредактируйте .env файл, указав свои настройки
```

3. **Запуск сервисов**
```bash
docker-compose up -d
```

4. **Инициализация Superset** (опционально)
```bash
docker-compose --profile init up superset-init
```

### ❗️Конфигурация окружения 

Основные переменные в `.env`:

```env
# ========================
# PROJECT CONFIG
# ========================
PROJECT_NAME=stats_platform
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=<django secret key>

# ========================
# NEON DATABASE
# ========================
DATABASE_URL=<neon database url>

# ========================
# CLICKHOUSE DATABASE
# ========================
CLICKHOUSE_HOST=clickhouse
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=default
CLICKHOUSE_DB=default

# ========================
# POSTGRES DATABASE
# ========================

POSTGRES_DB=stats_platform
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_FIRSTNAME=admin
POSTGRES_LASTNAME=admin

# ========================
# REDIS
# ========================
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379/0

# ========================
# KAFKA CONFIG
# ========================
KAFKA_BOOTSTRAP_SERVERS=kafka_stats:9092
KAFKA_BROKER_URL=kafka_stats:9092
KAFKA_BROKER_DOCKER=kafka_stats:9092
BOOTSTRAP_SERVERS=kafka_stats:9092

# Kafka Topics
KAFKA_BOT_TOPIC=bot_logs_topic
KAFKA_BACKEND_TOPIC=backend_logs_topic
KAFKA_TOPIC=backend_logs_topic

# Kafka Producers
PRODUCER_CLIENT_ID_DJANGO_BACKEND=django_backend_producer
PRODUCER_CLIENT_ID_DJANGO_BOT=django_bot_producer

# Kafka Consumer
BATCH_SIZE=2
KAFKA_GROUP_ID=stats_platform

# ========================
# TELEGRAM BOT
# ========================
# Production Bot
BOT_TOKEN=<your bot token>


# Bot Configuration
BASE_URL=http://backend:8000/
BASE_URL_DEV=http://127.0.0.1:8000/

# ========================
# CLOUD STORAGE (Supabase)
# ========================
CLOUD_URL=https://<supabase_project_hash>.supabase.co/storage/v1/object/public/statistics-bot-bucket/

CLOUD_UPLOAD_URL=https://<supabase_project_hash>.supabase.co/storage/v1/object/statistics-bot-bucket/

CLOUD_API_KEY=<your api key>

# ========================
# GRAFANA
# ========================
GF_SECURITY_ADMIN_USER=admin
GF_SECURITY_ADMIN_PASSWORD=admin

# ========================
# ADMINISTRATION
# ========================
ADMIN_1=<main admin id>
ADMINS=<admin id separated by _>

# ========================
# FEATURE FLAGS
# ========================
LOGS=True
CACHE=False
MPLCONFIGDIR=/tmp/mplconfig


# ========================
# CLICKHOUSE EXPORTER
# ========================
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=default
CLICKHOUSE_URL=http://clickhouse:8123


# ========================
# REDDIS EXPORTER
# ========================
REDIS_ADDR=redis://redis:6379


# ========================
# SUPERSET CONFIG
# ========================
SUPERSET_SECRET_KEY=your-super-secret-key-change-this-in-production
SUPERSET_USERNAME=admin
SUPERSET_PASSWORD=admin
SUPERSET_EMAIL=admin@stats.com
SUPERSET_PORT=8088


# Feature flags
SUPERSET_FEATURE_EMBEDDED_SUPERSET=<True or False>
```


# Statistics Bot Platform 📊 - API Documentation

## 📋 Содержание API

- [A/B Testing](#ab-testing)
- [Datasets Management](#datasets-management) 
- [Distributions](#distributions)
- [Machine Learning](#machine-learning)
- [Users & Authentication](#users--authentication)
- [System](#system)

## 🔬 A/B Testing

| Method | Endpoint | Parameters | Description | Response |
|--------|----------|------------|-------------|----------|
| **POST** | `/ab-tests/t-test/{dataset_id}/` | `dataset_id` (integer, path) | T-тест для сравнения средних значений | 200 - JSON Response |
| **POST** | `/ab-tests/z-test/{dataset_id}/` | `dataset_id` (integer, path) | Z-тест для больших выборок | 200 - JSON Response |
| **POST** | `/ab-tests/u-test/{dataset_id}/` | `dataset_id` (integer, path) | U-тест Манна-Уитни | 200 - JSON Response |
| **POST** | `/ab-tests/welch-test/{dataset_id}/` | `dataset_id` (integer, path) | T-тест Уэлча для неравных дисперсий | 200 - JSON Response |
| **POST** | `/ab-tests/anova/{dataset_id}/` | `dataset_id` (integer, path) | Дисперсионный анализ ANOVA | 200 - JSON Response |
| **POST** | `/ab-tests/chi-square-2sample/{dataset_id}/` | `dataset_id` (integer, path) | Хи-квадрат тест для двух выборок | 200 - JSON Response |
| **POST** | `/ab-tests/cramer-test/{dataset_id}/` | `dataset_id` (integer, path) | Тест Крамера для номинальных данных | 200 - JSON Response |
| **POST** | `/ab-tests/ks-test-2sample/{dataset_id}/` | `dataset_id` (integer, path) | Тест Колмогорова-Смирнова | 200 - JSON Response |
| **POST** | `/ab-tests/bootstrap/{dataset_id}/` | `dataset_id` (integer, path) | Bootstrap ресэмплинг | 200 - JSON Response |
| **POST** | `/ab-tests/anderson-darling-test/{dataset_id}/` | `dataset_id` (integer, path) | Тест Андерсона-Дарлинга | 200 - JSON Response |
| **POST** | `/ab-tests/anderson-darling-2sample-test/{dataset_id}/` | `dataset_id` (integer, path) | Тест Андерсона-Дарлинга для двух выборок | 200 - JSON Response |
| **POST** | `/ab-tests/shapiro-wilk-test/{dataset_id}/` | `dataset_id` (integer, path) | Тест Шапиро-Уилка на нормальность | 200 - JSON Response |
| **POST** | `/ab-tests/lilliefors-test/{dataset_id}/` | `dataset_id` (integer, path) | Тест Лиллиефорса на нормальность | 200 - JSON Response |
| **POST** | `/ab-tests/cuped/{dataset_id}/` | `dataset_id` (integer, path) | CUPED для повышения чувствительности | 200 - JSON Response |
| **POST** | `/ab-tests/cupac/{dataset_id}/` | `dataset_id` (integer, path) | CUPAC ковариатная адаптация | 200 - JSON Response |
| **POST** | `/ab-tests/mde/{dataset_id}/` | `dataset_id` (integer, path) | Расчет минимального детектируемого эффекта | 200 - JSON Response |
| **POST** | `/ab-tests/sample-size/{dataset_id}/` | `dataset_id` (integer, path) | Расчет размера выборки | 200 - JSON Response |

## 📁 Datasets Management

| Method | Endpoint | Parameters | Description | Request Body | Response |
|--------|----------|------------|-------------|--------------|----------|
| **GET** | `/api/datasets/` | - | Получить список датасетов | - | 200 - Array of `Dataset` |
| **POST** | `/api/datasets/` | - | Создать новый датасет | `Dataset` (JSON/form-data) | 200 - `Dataset` |
| **GET** | `/api/datasets/{dataset_id}/` | `dataset_id` (integer, path) | Получить датасет по ID | - | 200 - `Dataset` |
| **PUT** | `/api/datasets/{dataset_id}/` | `dataset_id` (integer, path) | Полностью обновить датасет | `Dataset` (JSON/form-data) | 200 - `Dataset` |
| **PATCH** | `/api/datasets/{dataset_id}/` | `dataset_id` (integer, path) | Частично обновить датасет | `PatchedDataset` (JSON/form-data) | 200 - `Dataset` |
| **DELETE** | `/api/datasets/{dataset_id}/` | `dataset_id` (integer, path) | Удалить датасет | - | 204 - No content |

### Dataset Schema
```typescript
{
  id: integer (readonly),
  columns: string[] (nullable),
  url: string (uri, nullable, maxLength: 1000),
  name: string (maxLength: 100),
  alpha: number (double),
  beta: number (double),
  test: string (maxLength: 100),
  control: string (maxLength: 100),
  length: integer
}
```

## 📊 Distributions

### CRUD Operations

| Method | Endpoint | Parameters | Description | Request Body | Response |
|--------|----------|------------|-------------|--------------|----------|
| **GET** | `/api/distributions/` | - | Получить список распределений | - | 200 - Array of `Distribution` |
| **POST** | `/api/distributions/` | - | Создать новое распределение | `Distribution` (JSON/form-data) | 200 - `Distribution` |
| **GET** | `/api/distributions/{distribution_id}/` | `distribution_id` (integer, path) | Получить распределение по ID | - | 200 - `Distribution` |
| **PUT** | `/api/distributions/{distribution_id}/` | `distribution_id` (integer, path) | Полностью обновить распределение | `Distribution` (JSON/form-data) | 200 - `Distribution` |
| **PATCH** | `/api/distributions/{distribution_id}/` | `distribution_id` (integer, path) | Частично обновить распределение | `PatchedDistribution` (JSON/form-data) | 200 - `Distribution` |
| **DELETE** | `/api/distributions/{distribution_id}/` | `distribution_id` (integer, path) | Удалить распределение | - | 204 - No content |

### Distribution Operations

| Method | Endpoint | Parameters | Description | Response |
|--------|----------|------------|-------------|----------|
| **POST** | `/distributions/probability/{id}/` | `id` (integer, path) | Расчет вероятности для распределения | 200 - JSON Response |
| **POST** | `/distributions/quantile/{id}/` | `id` (integer, path) | Расчет квантилей распределения | 200 - JSON Response |
| **POST** | `/distributions/percentile/{id}/` | `id` (integer, path) | Расчет процентилей распределения | 200 - JSON Response |
| **POST** | `/distributions/interval/{id}/` | `id` (integer, path) | Расчет доверительного интервала | 200 - JSON Response |
| **POST** | `/distributions/sample/{id}/` | `id` (integer, path) | Генерация выборки из распределения | 200 - JSON Response |
| **POST** | `/distributions/plot/{id}/` | `id` (integer, path) | Построение графика распределения | 200 - JSON Response |

### Distribution Schema
```typescript
{
  id: integer (readonly),
  user: integer (readonly),
  name: string (maxLength: 100),
  description: string (nullable, maxLength: 1000),
  distribution_type: DistributionTypeEnum,
  distribution_parameters: object,
  created_at: string (date-time, readonly),
  updated_at: string (date-time, readonly)
}
```

### Distribution Types
```
normal, binomial, poisson, uniform, exponential, beta, gamma, 
lognormal, chi2, t, f, geometric, hypergeom, negative_binomial
```

## 🤖 Machine Learning

### Model Management

| Method | Endpoint | Parameters | Description | Request Body | Response |
|--------|----------|------------|-------------|--------------|----------|
| **GET** | `/ml-algorithms/model-create/` | - | Получить список ML моделей | - | 200 - Array of `ML_Model` |
| **POST** | `/ml-algorithms/model-create/` | - | Создать новую ML модель | `ML_Model` (JSON/form-data) | 200 - `ML_Model` |
| **POST** | `/ml-algorithms/get_models/` | - | Получить доступные модели | `ML_Model` (JSON/form-data) | 200 - `ML_Model` |
| **GET** | `/ml-algorithms/model/` | - | Получить текущую модель | - | 200 - `ML_Model` |
| **GET** | `/ml-algorithms/model/{model_id}/` | `model_id` (integer, path) | Получить модель по ID | - | 200 - `ML_Model` |
| **PUT** | `/ml-algorithms/model/{model_id}/` | `model_id` (integer, path) | Полностью обновить модель | `ML_Model` (JSON/form-data) | 200 - `ML_Model` |
| **PATCH** | `/ml-algorithms/model/{model_id}/` | `model_id` (integer, path) | Частично обновить модель | `PatchedML_Model` (JSON/form-data) | 200 - `ML_Model` |
| **DELETE** | `/ml-algorithms/model/{model_id}/` | `model_id` (integer, path) | Удалить модель | - | 204 - No content |

### Model Operations

| Method | Endpoint | Parameters | Description | Request Body | Response |
|--------|----------|------------|-------------|--------------|----------|
| **POST** | `/ml-algorithms/model-fit/{model_id}/` | `model_id` (integer, path) | Обучение ML модели | `ML_Model` (JSON/form-data) | 200 - `ML_Model` |
| **POST** | `/ml-algorithms/model-predict/{model_id}/` | `model_id` (integer, path) | Предсказание ML модели | `ML_Model` (JSON/form-data) | 200 - `ML_Model` |
| **GET** | `/ml-algorithms/model-refit/{model_id}/` | `model_id` (integer, path) | Переобучение модели | - | 200 - `ML_Model` |
| **PUT** | `/ml-algorithms/model-refit/{model_id}/` | `model_id` (integer, path) | Обновление и переобучение | `ML_Model` (JSON/form-data) | 200 - `ML_Model` |
| **PATCH** | `/ml-algorithms/model-refit/{model_id}/` | `model_id` (integer, path) | Частичное обновление и переобучение | `PatchedML_Model` (JSON/form-data) | 200 - `ML_Model` |
| **DELETE** | `/ml-algorithms/model-refit/{model_id}/` | `model_id` (integer, path) | Удаление переобученной модели | - | 204 - No content |

### ML Model Schema
```typescript
{
  id: integer (readonly),
  user: integer (readonly),
  name: string (maxLength: 100),
  description: string (maxLength: 100),
  task: TaskEnum,
  task_display: string (readonly),
  type: TypeEnum,
  type_display: string (readonly),
  features: string[] (nullable),
  target: string (maxLength: 200),
  get_url: string (uri, nullable, maxLength: 1000),
  post_url: string (uri, nullable, maxLength: 1000),
  created_at: string (date-time, readonly),
  updated_at: string (date-time, readonly)
}
```

### Task Types
```
regression, classification, clusterization
```

### Algorithm Types
```
linear_regression, polinomial_regression, knn_regression, 
gradient_boosting_regression, logistic_regression, 
support_vector_machine_classification, knn_classification, 
random_forest_classification, gradient_boosting_classification, 
kmeans_clusterization, density_clusterization
```

## 👥 Users & Authentication

| Method | Endpoint | Parameters | Description | Request Body | Response |
|--------|----------|------------|-------------|--------------|----------|
| **GET** | `/auth/user/` | - | Получить список пользователей | - | 200 - Array of `User` |
| **POST** | `/auth/user/` | - | Создать нового пользователя | `User` (JSON/form-data) | 201 - `User` |
| **GET** | `/auth/user/{telegram_id}/` | `telegram_id` (string, path) | Получить пользователя по Telegram ID | - | 200 - `User` |
| **PUT** | `/auth/user/{telegram_id}/` | `telegram_id` (string, path) | Полностью обновить пользователя | `User` (JSON/form-data) | 200 - `User` |
| **PATCH** | `/auth/user/{telegram_id}/` | `telegram_id` (string, path) | Частично обновить пользователя | `PatchedUser` (JSON/form-data) | 200 - `User` |
| **DELETE** | `/auth/user/{telegram_id}/` | `telegram_id` (string, path) | Удалить пользователя | - | 204 - No content |
| **GET** | `/auth/user/active/` | - | Получить активных пользователей | - | 200 - Array of `User` |

### User Schema
```typescript
{
  id: integer (readonly),
  telegram_id: string (maxLength: 100),
  created_at: string (date-time, readonly),
  is_admin: boolean (readonly),
  updated_at: string (date-time, readonly),
  is_alive: boolean
}
```

## 🖥️ System

| Method | Endpoint | Parameters | Description | Response |
|--------|----------|------------|-------------|----------|
| **GET** | `/api/schema/` | `format`: json/yaml<br>`lang`: language code | Получить OpenAPI схему | 200 - OpenAPI specification |

## 🎯 Примеры использования

### Создание датасета
```bash
curl -X POST "http://localhost:8000/api/datasets/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my_dataset",
    "columns": ["col1", "col2", "col3"],
    "alpha": 0.05,
    "beta": 0.2,
    "test": "variant_a",
    "control": "control",
    "length": 1000
  }'
```

### Запуск T-теста
```bash
curl -X POST "http://localhost:8000/ab-tests/t-test/1/"
```

### Создание распределения
```bash
curl -X POST "http://localhost:8000/api/distributions/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Normal Distribution",
    "distribution_type": "normal",
    "distribution_parameters": {"mean": 0, "std": 1}
  }'
```

### Создание ML модели
```bash
curl -X POST "http://localhost:8000/ml-algorithms/model-create/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Regression Model",
    "task": "regression",
    "type": "linear_regression",
    "target": "price",
    "features": ["feature1", "feature2"]
  }'
```

## 🔐 Аутентификация

Большинство endpoints требуют аутентификации через Telegram. Используйте заголовок:
```
Authorization: Bearer <telegram_token>
```

## 📊 Статус коды

- `200` - Успешный запрос
- `201` - Успешное создание
- `204` - Успешное удаление (нет содержимого)
- `400` - Неверный запрос
- `401` - Не авторизован
- `403` - Запрещено
- `404` - Не найдено
- `500` - Внутренняя ошибка сервера


## 📊 Мониторинг

### Доступные интерфейсы

После запуска доступны следующие веб-интерфейсы:

- **Grafana Dashboards**: http://localhost:3000
  - Логин: `admin`, Пароль: `admin`
- **Prometheus**: http://localhost:9090
- **Superset BI**: http://localhost:8088
- **pgAdmin**: http://localhost:5050
- **Kafdrop**: http://localhost:9001

### Метрики и экспортеры

- **Node Exporter**: Системные метрики - порт 9100
- **cAdvisor**: Метрики контейнеров - порт 8081
- **PostgreSQL Exporter**: Метрики БД - порт 9187
- **Redis Exporter**: Метрики Redis - порт 9121
- **Kafka Exporter**: Метрики Kafka - порт 9308
- **ClickHouse Exporter**: Метрики ClickHouse - порт 9116

# 🔧 Разработка

## 🏗 Реальная архитектура проекта

```
statistics_bot/
├── 📊 analytics/                    # Сервис аналитики (FastAPI + ClickHouse)
│   ├── Dockerfile
│   ├── app/
│   │   ├── clickhouse_client.py     # Клиент ClickHouse
│   │   ├── init_clickhouse.py       # Инициализация ClickHouse
│   │   ├── kafka_consumer.py        # Консьюмер Kafka для аналитики
│   │   └── main.py                  # Точка входа FastAPI
│   └── requirements.txt
│
├── 🐍 backend/                      # Основной Django бекенд
│   ├── Dockerfile
│   ├── 📊 ab_tests/                 # Модуль A/B тестирования
│   │   ├── handlers/                # Обработчики статистических тестов
│   │   │   ├── handlers.py          # Основные обработчики тестов
│   │   │   └── test.ipynb           # Jupyter ноутбук для тестирования
│   │   ├── exception_handler.py     # Обработка исключений
│   │   ├── models.py               # Модели A/B тестов
│   │   ├── serializers.py          # Сериализаторы DRF
│   │   ├── urls.py                 # Маршруты A/B тестов
│   │   └── views.py                # Представления A/B тестов
│   │
│   ├── 📈 api/                     # Основное API приложение
│   │   ├── migrations/             # Миграции базы данных
│   │   │   ├── 0001_initial.py
│   │   │   ├── 0002_alter_dataset_columns.py
│   │   │   ├── 0003_dataset_alfa_dataset_beta.py
│   │   │   ├── 0004_rename_alfa_dataset_alpha.py
│   │   │   ├── 0005_dataset_control_dataset_test.py
│   │   │   └── 0006_dataset_length.py
│   │   ├── models.py              # Модели Dataset
│   │   ├── permissions.py         # Права доступа
│   │   ├── serializers.py         # Сериализаторы
│   │   ├── urls.py               # Маршруты API
│   │   └── views.py              # Представления API
│   │
│   ├── 📊 datasets/               # Приложение датасетов
│   │   ├── models.py             # Модели датасетов
│   │   ├── serializers.py        # Сериализаторы
│   │   ├── urls.py              # Маршруты датасетов
│   │   └── views.py             # Представления датасетов
│   │
│   ├── 📊 distributions/         # Модуль распределений вероятностей
│   │   ├── handlers.py          # Обработчики распределений
│   │   ├── models.py           # Модели распределений
│   │   ├── serializers.py      # Сериализаторы
│   │   ├── urls.py            # Маршруты распределений
│   │   └── views.py           # Представления распределений
│   │
│   ├── 🔄 kafka_broker/         # Интеграция с Kafka
│   │   ├── utils.py            # Утилиты Kafka
│   │   ├── models.py          # Модели Kafka
│   │   └── views.py          # Представления Kafka
│   │
│   ├── 🤖 ml_algorithms/       # Модуль машинного обучения
│   │   ├── model_handlers/    # Обработчики ML моделей
│   │   │   ├── base.py       # Базовый класс обработчика
│   │   │   ├── regression.py # Регрессионные модели
│   │   │   ├── classification.py # Классификация
│   │   │   ├── clusterization.py # Кластеризация
│   │   │   ├── factory.py    # Фабрика моделей
│   │   │   ├── sklearn/      # Scikit-learn интеграция
│   │   │   └── main.ipynb    # Jupyter ноутбук ML
│   │   ├── migrations/       # Миграции ML моделей
│   │   │   ├── 0001_initial.py
│   │   │   └── 0002_alter_ml_model_features.py
│   │   ├── models.py        # Модели ML
│   │   ├── serializers.py   # Сериализаторы ML
│   │   ├── urls.py         # Маршруты ML
│   │   └── views.py        # Представления ML
│   │
│   ├── 🗄️ redis_cache/      # Кэширование Redis
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── views.py
│   │
│   ├── 📨 signals/          # Django сигналы
│   │   ├── signals.py       # Определения сигналов
│   │   ├── models.py
│   │   └── views.py
│   │
│   ├── 👥 users/           # Модуль пользователей
│   │   ├── migrations/     # Миграции пользователей
│   │   │   └── 0001_initial.py
│   │   ├── models.py      # Модели User
│   │   ├── serializers.py # Сериализаторы
│   │   ├── urls.py       # Маршруты пользователей
│   │   └── views.py      # Представления
│   │
│   ├── ⚙️ backend/        # Настройки Django проекта
│   │   ├── settings.py   # Основные настройки
│   │   ├── urls.py      # Корневые маршруты
│   │   ├── asgi.py      # ASGI конфигурация
│   │   ├── wsgi.py      # WSGI конфигурация
│   │   └── authentication.py # Аутентификация
│   │
│   ├── manage.py         # Django management
│   ├── gunicorn.conf.py # Gunicorn конфигурация
│   └── requirements.txt  # Зависимости Python
│
├── 🤖 bot/              # Telegram бот (Aiogram)
│   ├── Dockerfile
│   ├── app/
│   │   ├── 🎯 handlers/     # Обработчики сообщений
│   │   │   ├── admin_handlers.py    # Админ команды
│   │   │   ├── user_handlers.py     # Пользовательские команды
│   │   │   ├── dataset_handlers.py  # Работа с датасетами
│   │   │   ├── distribution_handlers.py # Распределения
│   │   │   ├── ml_handlers.py       # Машинное обучение
│   │   │   ├── catcher.py          # Перехватчик ошибок
│   │   │   └── router.py           # Маршрутизатор
│   │   │
│   │   ├── ⌨️ keyboards/    # Клавиатуры бота
│   │   │   ├── answer_admin.py     # Reply клавиатуры админа
│   │   │   ├── answer_user.py      # Reply клавиатуры пользователя
│   │   │   ├── inline_admin.py     # Inline кнопки админа
│   │   │   ├── inline_dataset.py   # Inline кнопки датасетов
│   │   │   ├── inline_ml.py        # Inline кнопки ML
│   │   │   └── inline_user.py      # Inline кнопки пользователя
│   │   │
│   │   ├── 🏗 middlewares/  # Промежуточное ПО
│   │   │   ├── antiflood.py       # Защита от флуда
│   │   │   └── metrics.py         # Метрики производительности
│   │   │
│   │   ├── 📡 requests/     # HTTP запросы к API
│   │   │   ├── dataset/     # Запросы датасетов
│   │   │   ├── distribution/ # Запросы распределений
│   │   │   ├── get/         # GET запросы
│   │   │   ├── post/        # POST запросы
│   │   │   ├── put/         # PUT запросы
│   │   │   ├── delete/      # DELETE запросы
│   │   │   ├── ml_models/   # Запросы ML моделей
│   │   │   ├── user/        # Запросы пользователей
│   │   │   └── helpers/     # Вспомогательные функции
│   │   │
│   │   ├── 🗂️ database/     # Работа с БД (если есть)
│   │   ├── 🔔 states/       # Состояния FSM
│   │   │   └── states.py    # Определения состояний
│   │   │
│   │   ├── 📊 kafka/        # Интеграция с Kafka
│   │   │   └── utils.py     # Утилиты Kafka
│   │   │
│   │   └── 🛠️ filters/      # Фильтры бота
│   │       └── IsAdmin.py   # Фильтр проверки админа
│   │
│   ├── main.py             # Основной файл бота (polling)
│   ├── main_wh.py          # Webhook версия бота
│   └── requirements.txt    # Зависимости бота
│
├── 📊 logs/               # Сервис логирования
│   ├── Dockerfile
│   ├── app/
│   │   ├── init_postgres.py    # Инициализация PostgreSQL для логов
│   │   ├── kafka_consumer.py   # Консьюмер Kafka для логов
│   │   ├── postgres_client.py  # Клиент PostgreSQL
│   │   └── main.py            # Точка входа
│   └── requirements.txt
│
├── 📈 dashboards/         # Grafana дашборды
│   ├── Docker Container-1761997579326.json
│   ├── Kubernetes cluster-1761997608049.json
│   ├── Node Exporter Full-1761997619412.json
│   └── PostgreSQL Database-1761997627875.json
│
├── 🐳 docker-compose.yaml # Docker Compose конфигурация
├── 📊 prometheus/         # Prometheus конфигурация
│   └── prometheus.yml
│
├── 📊 superset/          # Apache Superset
│   └── Dockerfile
│
└── 📝 Документация и настройки
    ├── README.md
    ├── requirements.txt    # Общие зависимости
    └── .env               # Переменные окружения
```

## 🔄 Взаимодействие компонентов

### Поток данных:
1. **Пользователь** → **Telegram Bot** → **Django Backend API**
2. **Backend** → **PostgreSQL** (основные данные)
3. **Backend** → **Kafka** (события и логи)
4. **Kafka** → **Analytics Service** → **ClickHouse** (аналитика)
5. **Kafka** → **Logs Service** → **PostgreSQL** (логи)
6. **Все сервисы** → **Prometheus** (метрики)
7. **Prometheus** → **Grafana** (визуализация)

### Основные технологии каждого компонента:

| Компонент | Технологии | Назначение |
|-----------|------------|------------|
| **Backend** | Django + DRF + PostgreSQL | Основная бизнес-логика, API |
| **Bot** | Aiogram + Requests | Telegram интерфейс, клиент API |
| **Analytics** | FastAPI + ClickHouse | Аналитика, быстрые запросы |
| **Logs** | FastAPI + PostgreSQL | Централизованное логирование |
| **Monitoring** | Prometheus + Grafana | Мониторинг и метрики |
| **BI** | Apache Superset | Бизнес-аналитика |
| **Message Broker** | Kafka + Zookeeper | Асинхронная коммуникация |
| **Cache** | Redis | Кэширование данных |

### Локальная разработка

1. **Установка зависимостей**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Запуск без Docker**
```bash
# Backend
cd backend
python manage.py runserver

# Bot
cd ../bot
python main.py
```

3. **Миграции базы данных**
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

### Тестирование

```bash
# Запуск тестов
python manage.py test

# С код покрытием
coverage run manage.py test
coverage report
```

## 🐛 Поиск и устранение неисправностей

### Распространенные проблемы

1. **Kafka не запускается**
   - Проверьте, что Zookeeper запущен первым
   - Убедитесь в достаточности ресурсов памяти

2. **Проблемы с подключением к БД**
   - Проверьте переменные окружения в .env
   - Убедитесь, что PostgreSQL контейнер здоров

3. **Бот не отвечает**
   - Проверьте BOT_TOKEN в .env
   - Убедитесь, что backend сервис доступен

### Логи

Логи доступны через:
```bash
# Просмотр логов конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f bot

# Все логи
docker-compose logs -f
```

## 📄 Лицензия

[Указать лицензию]

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте feature ветку (`git checkout -b feature/amazing-feature`)
3. Закоммитьте изменения (`git commit -m 'Add amazing feature'`)
4. Запушьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📞 Поддержка

Для вопросов и поддержки:
- Создайте Issue в репозитории
- Напишите в Telegram бот
- Обратитесь к администраторам платформы

---

**Statistics Bot Platform** - мощный инструмент для статистического анализа и машинного обучения с удобным Telegram интерфейсом и расширенными возможностями мониторинга.