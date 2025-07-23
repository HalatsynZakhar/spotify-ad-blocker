# Рекомендации по улучшению качества и поддерживаемости кода

## 🚨 Критические исправления (выполнены)

### ✅ Исправлена ошибка GetSystemMetrics
- **Проблема:** `win32gui.GetSystemMetrics` не существует
- **Решение:** Заменено на `win32api.GetSystemMetrics` с fallback
- **Статус:** Исправлено

## 📦 Управление зависимостями

### 1. Обновить requirements.txt
```txt
psutil>=5.9.0
requests>=2.28.0
pycaw>=20220416
pywin32>=305
```

### 2. Добавить проверку зависимостей
```python
def check_dependencies():
    """Проверка наличия всех необходимых зависимостей"""
    missing_deps = []
    
    try:
        import pycaw
    except ImportError:
        missing_deps.append('pycaw')
    
    try:
        import win32gui, win32api
    except ImportError:
        missing_deps.append('pywin32')
    
    if missing_deps:
        print(f"Отсутствуют зависимости: {', '.join(missing_deps)}")
        print("Установите: pip install " + ' '.join(missing_deps))
        return False
    return True
```

## 🏗️ Архитектурные улучшения

### 1. Разделение ответственности
```python
class SpotifyDetector:
    """Отвечает только за определение состояния Spotify"""
    pass

class AudioController:
    """Отвечает только за управление звуком"""
    pass

class AdBlocker:
    """Основной класс, координирующий работу"""
    pass
```

### 2. Конфигурационный файл
```python
# config.py
class Config:
    CHECK_INTERVAL = 0.5
    CONFIRMATION_THRESHOLD = 3
    WINDOW_SWITCH_PROTECTION_TIME = 2.0
    LOG_LEVEL = "INFO"
    
    AD_DOMAINS = [
        "spclient.wg.spotify.com",
        "audio-sp-*.pscdn.co",
        # ...
    ]
```

## 🔧 Улучшения кода

### 1. Добавить типизацию
```python
from typing import Optional, List, Tuple, Dict
from dataclasses import dataclass

@dataclass
class DetectionResult:
    is_ad: bool
    confidence: float
    methods_triggered: List[str]
    timestamp: float
```

### 2. Улучшить обработку ошибок
```python
class SpotifyAdBlockerError(Exception):
    """Базовый класс для ошибок блокировщика"""
    pass

class DependencyError(SpotifyAdBlockerError):
    """Ошибка отсутствующих зависимостей"""
    pass

class AudioControlError(SpotifyAdBlockerError):
    """Ошибка управления звуком"""
    pass
```

### 3. Добавить контекстные менеджеры
```python
from contextlib import contextmanager

@contextmanager
def audio_session_manager():
    """Безопасное управление аудио сессией"""
    session = None
    try:
        session = get_audio_session()
        yield session
    except Exception as e:
        logger.error(f"Ошибка аудио сессии: {e}")
    finally:
        if session:
            session.cleanup()
```

## 📊 Мониторинг и метрики

### 1. Добавить метрики производительности
```python
class PerformanceMetrics:
    def __init__(self):
        self.detection_times = []
        self.false_positives = 0
        self.true_positives = 0
        self.start_time = time.time()
    
    def log_detection(self, detection_time: float, is_correct: bool):
        self.detection_times.append(detection_time)
        if is_correct:
            self.true_positives += 1
        else:
            self.false_positives += 1
    
    def get_accuracy(self) -> float:
        total = self.true_positives + self.false_positives
        return self.true_positives / total if total > 0 else 0.0
```

### 2. Улучшить логирование
```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_level: str = "INFO"):
    """Настройка продвинутого логирования"""
    logger = logging.getLogger('spotify_ad_blocker')
    logger.setLevel(getattr(logging, log_level))
    
    # Ротация логов
    handler = RotatingFileHandler(
        'spotify_ad_blocker.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
```

## 🧪 Тестирование

### 1. Добавить unit тесты
```python
import unittest
from unittest.mock import Mock, patch

class TestSpotifyAdBlocker(unittest.TestCase):
    def setUp(self):
        self.blocker = SpotifyAdBlocker()
    
    def test_window_title_detection(self):
        # Тест определения рекламы по заголовку
        pass
    
    def test_false_positive_protection(self):
        # Тест защиты от ложных срабатываний
        pass
```

### 2. Добавить интеграционные тесты
```python
class TestIntegration(unittest.TestCase):
    def test_full_ad_blocking_cycle(self):
        # Тест полного цикла блокировки рекламы
        pass
```

## 🔒 Безопасность

### 1. Валидация входных данных
```python
def validate_window_title(title: str) -> bool:
    """Валидация заголовка окна"""
    if not isinstance(title, str):
        return False
    if len(title) > 1000:  # Защита от слишком длинных строк
        return False
    return True
```

### 2. Ограничение ресурсов
```python
class ResourceLimiter:
    def __init__(self, max_memory_mb: int = 100):
        self.max_memory = max_memory_mb * 1024 * 1024
    
    def check_memory_usage(self):
        import psutil
        process = psutil.Process()
        if process.memory_info().rss > self.max_memory:
            raise MemoryError("Превышен лимит памяти")
```

## 📈 Производительность

### 1. Кэширование результатов
```python
from functools import lru_cache
from time import time

class CachedDetector:
    def __init__(self, cache_ttl: float = 1.0):
        self.cache_ttl = cache_ttl
        self._cache = {}
    
    def get_cached_result(self, key: str):
        if key in self._cache:
            result, timestamp = self._cache[key]
            if time() - timestamp < self.cache_ttl:
                return result
        return None
```

### 2. Асинхронная обработка
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncAdBlocker:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
    
    async def check_ad_async(self):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self.executor, self.check_ad_sync
        )
```

## 📚 Документация

### 1. Добавить docstrings
```python
def is_ad_playing(self) -> bool:
    """Определяет, воспроизводится ли реклама в Spotify.
    
    Returns:
        bool: True если обнаружена реклама, False в противном случае
    
    Raises:
        SpotifyAdBlockerError: При критических ошибках определения
    
    Example:
        >>> blocker = SpotifyAdBlocker()
        >>> if blocker.is_ad_playing():
        ...     print("Реклама обнаружена!")
    """
```

### 2. Создать API документацию
```python
# Использовать sphinx для генерации документации
# pip install sphinx
# sphinx-quickstart docs
```

## 🚀 Развертывание

### 1. Создать setup.py
```python
from setuptools import setup, find_packages

setup(
    name="spotify-ad-blocker",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "psutil>=5.9.0",
        "requests>=2.28.0",
        "pycaw>=20220416",
        "pywin32>=305",
    ],
    entry_points={
        "console_scripts": [
            "spotify-ad-blocker=spotify_ad_blocker:main",
        ],
    },
)
```

### 2. Добавить CI/CD
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: python -m pytest
```

## 📋 Приоритетный план внедрения

### Фаза 1 (Критично)
1. ✅ Исправить ошибку GetSystemMetrics
2. Обновить requirements.txt с версиями
3. Добавить проверку зависимостей при запуске

### Фаза 2 (Важно)
1. Разделить код на отдельные классы
2. Добавить конфигурационный файл
3. Улучшить обработку ошибок

### Фаза 3 (Желательно)
1. Добавить unit тесты
2. Улучшить логирование
3. Добавить метрики производительности

### Фаза 4 (Долгосрочно)
1. Асинхронная обработка
2. Полная документация
3. CI/CD pipeline

Эти улучшения сделают код более надежным, поддерживаемым и готовым к продакшену.