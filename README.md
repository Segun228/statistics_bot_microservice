
# 📊 StatBot AI - Платформа для статистического анализа и A/B тестирования

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-4.2-green)
![Aiogram](https://img.shields.io/badge/Aiogram-3.21-blue)
![Microservices](https://img.shields.io/badge/Architecture-Microservices-orange)

**StatBot AI** - это мощная платформа для статистического анализа данных через Telegram бота. Загружайте датасеты, проводите A/B тесты, строите модели машинного обучения и визуализируйте результаты в реальном времени! 🚀

## 🌟 Основные возможности

### 📈 **Статистический анализ**
- A/B тестирование (15+ методов)
- Проверка распределений (нормальность, однородность)
- Доверительные интервалы и мощность тестов
- Визуализация результатов

### 🤖 **Машинное обучение**
- Классификация и регрессия
- Предобработка данных
- Кросс-валидация и метрики качества
- Автоматический подбор гиперпараметров

### 📊 **Визуализация и мониторинг**
- Графики распределений
- Real-time дашборды в Grafana
- Экспорт результатов в PDF/CSV
- Интерактивные отчеты

### ⚡ **Производительность**
- Микросервисная архитектура
- Асинхронная обработка
- Кэширование в Redis
- Потоковая обработка через Kafka

## 🏗️ Архитектура системы

```
Telegram Bot (Aiogram) → Django Backend → Kafka → Analytics Service → ClickHouse → Grafana
        ↑                      ↑              ↑           ↑              ↑          ↑
    Пользовательский     Основная бизнес-   Очередь    Аналитика в    Хранилище  Визуализация
       интерфейс           логика API       сообщений  реальном времени данных    метрик
```

## 📁 Структура проекта

```
statbot-ai/
├── 🤖 bot/                    # Telegram бот на Aiogram
├── 🚀 backend/               # Django REST API
├── 📊 analytics/             # Микросервис аналитики
├── 📈 grafana_backup/        # Дашборды и конфиги Grafana
└── 🐳 docker-compose.yaml    # Оркестрация контейнеров
```

## 🛠️ Технологический стек

### **Backend & API**
- **Python 3.12** - основной язык
- **Django 4.2** - веб-фреймворк
- **Django REST Framework** - REST API
- **DRF Spectacular** - OpenAPI документация

### **Базы данных & Кэш**
- **PostgreSQL** - основная БД
- **Redis** - кэширование и сессии
- **ClickHouse** - аналитическое хранилище

### **Очереди & Аналитика**
- **Kafka** - потоковая обработка
- **Grafana** - визуализация метрик
- **Prometheus** - сбор метрик

### **Статистика & ML**
- **Pandas, NumPy, SciPy** - анализ данных
- **Scikit-learn** - машинное обучение
- **Matplotlib, Seaborn** - визуализация

### **Инфраструктура**
- **Docker** - контейнеризация
- **Aiogram** - Telegram бот
- **Gunicorn** - WSGI сервер

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/statbot-ai.git
cd statbot-ai
```

### 2. Настройка окружения
```bash
cp .env.example .env
# Отредактируйте .env файл с вашими настройками
```

### 3. Запуск через Docker
```bash
docker-compose up -d
```

### 4. Инициализация базы данных
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

### 5. Доступ к сервисам
- **Telegram Bot**: Найдите `@YourStatBot` в Telegram
- **API Documentation**: http://localhost:8000/api/schema/
- **Grafana**: http://localhost:3000 (admin/admin)
- **Kafka UI**: http://localhost:8080

## 📡 API Endpoints

### 🔐 **Аутентификация**
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/auth/user/` | Создание пользователя |
| `GET` | `/auth/user/{telegram_id}/` | Получение данных пользователя |

### 📊 **Датасеты**
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `GET` | `/api/datasets/` | Список датасетов |
| `POST` | `/api/datasets/` | Загрузка датасета |
| `GET` | `/api/datasets/{id}/` | Получение датасета |

### 📊 **A/B Тестирование**
| Метод | Эндпоинт | Тест | Описание |
|-------|----------|------|----------|
| `POST` | `/ab-tests/t-test/{dataset_id}/` | t-тест | Сравнение средних |
| `POST` | `/ab-tests/z-test/{dataset_id}/` | Z-тест | Тест пропорций |
| `POST` | `/ab-tests/bootstrap/{dataset_id}/` | Bootstrap | Непараметрический тест |
| `POST` | `/ab-tests/anova/{dataset_id}/` | ANOVA | Дисперсионный анализ |
| `POST` | `/ab-tests/chi-square-2sample/{dataset_id}/` | Chi-square | Тест независимости |
| `POST` | `/ab-tests/cuped/{dataset_id}/` | CUPED | Уменьшение дисперсии |
| `POST` | `/ab-tests/mde/{dataset_id}/` | MDE | Расчет минимального эффекта |

### 📈 **Распределения**
| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| `POST` | `/distributions/plot/{id}/` | Построение графика |
| `POST` | `/distributions/quantile/{id}/` | Расчет квантилей |
| `POST` | `/distributions/probability/{id}/` | Вероятности |

## 🤖 Работа с Telegram ботом

### Основные команды:
```bash
/start - Начало работы
/help - Помощь и инструкции
/datasets - Управление датасетами
/tests - A/B тестирование
/analysis - Статистический анализ
/models - Машинное обучение
```

### Пример workflow:
1. **Загрузка данных**: Отправьте CSV файл боту
2. **Предпросмотр**: Бот покажет структуру данных
3. **Выбор анализа**: Выберите тип теста из меню
4. **Результаты**: Получите детальный отчет с графиками

## 📊 Примеры использования

### A/B тестирование конверсии
```python
# Через API
POST /ab-tests/z-test/123/
{
    "control_column": "conversion_A",
    "test_column": "conversion_B",
    "alpha": 0.05
}

# Ответ
{
    "p_value": 0.032,
    "confidence_interval": [0.01, 0.05],
    "effect_size": 0.03,
    "is_significant": true
}
```

### Анализ распределения
```python
POST /distributions/plot/123/
{
    "distribution_type": "normal",
    "parameters": {"mean": 0, "std": 1}
}
```

## ⚙️ Конфигурация

### Основные настройки (.env)
```env
# Database
DATABASE_URL=postgresql://user:pass@db:5432/statbot
REDIS_URL=redis://redis:6379/0

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_WEBHOOK_URL=https://yourdomain.com

# Kafka
KAFKA_BOOTSTRAP_SERVERS=kafka:9092
KAFKA_TOPIC_ANALYTICS=analytics_events

# Monitoring
GRAFANA_URL=http://grafana:3000
```

## 📈 Мониторинг и метрики

Система предоставляет метрики в реальном времени:

### **Бизнес-метрики**
- Количество запущенных A/B тестов
- Успешность тестов (p-value распределение)
- Время выполнения анализов

### **Технические метрики**
- Загрузка CPU/Memory по сервисам
- Latency API endpoints
- Kafka lag и throughput

### **Дашборды Grafana**
- **A/B Tests Overview**: Общая статистика тестов
- **System Health**: Мониторинг инфраструктуры
- **User Analytics**: Активность пользователей

## 🔧 Разработка

### Установка для разработки
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```


### Ограничения
- Максимальный размер файла: 100MB
- Максимальное количество строк: 1M
- Поддерживаемые форматы: CSV, Excel, JSON

## 🤝 Contributing

Мы приветствуем вклад в проект! 

1. Форкните репозиторий
2. Создайте feature branch: `git checkout -b feature/amazing-feature`
3. Закоммитьте изменения: `git commit -m 'Add amazing feature'`
4. Запушьте ветку: `git push origin feature/amazing-feature`
5. Откройте Pull Request


## 👥 Команда

- **Segun228** - Lead Developer & Data Scientist
- **Segun228** - Contributor


---

**⭐ Если вам нравится проект, поставьте звезду на GitHub!**
