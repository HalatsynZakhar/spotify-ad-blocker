#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Пример использования Spotify Ad Blocker

Этот файл демонстрирует различные способы использования блокировщика рекламы.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from spotify_ad_blocker import SpotifyAdBlocker
except ImportError:
    print("❌ Ошибка: Не удалось импортировать SpotifyAdBlocker")
    print("Убедитесь, что файл spotify_ad_blocker.py находится в той же папке")
    sys.exit(1)

def example_basic_usage():
    """
    Базовый пример использования блокировщика
    """
    print("🎵 Запуск базового блокировщика рекламы Spotify...")
    
    # Создаем экземпляр блокировщика
    blocker = SpotifyAdBlocker()
    
    try:
        # Запускаем блокировщик
        blocker.run()
    except KeyboardInterrupt:
        print("\n⏹️ Блокировщик остановлен пользователем")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        # Очистка ресурсов
        blocker.cleanup()
        print("🧹 Очистка завершена")

def example_with_custom_settings():
    """
    Пример с пользовательскими настройками
    """
    print("🎵 Запуск блокировщика с пользовательскими настройками...")
    
    # Пользовательские настройки
    custom_settings = {
        'check_interval': 0.5,  # Проверка каждые 0.5 секунды
        'enable_cache_cleanup': True,  # Включить очистку кэша
        'cache_cleanup_interval': 300,  # Очистка кэша каждые 5 минут
        'enable_hosts_blocking': True,  # Включить блокировку через hosts
        'enable_audio_muting': True,  # Включить отключение звука
        'verbose_logging': True,  # Подробное логирование
    }
    
    blocker = SpotifyAdBlocker(**custom_settings)
    
    try:
        blocker.run()
    except KeyboardInterrupt:
        print("\n⏹️ Блокировщик остановлен")
    finally:
        blocker.cleanup()

def example_monitoring_only():
    """
    Пример только мониторинга без блокировки
    """
    print("👁️ Запуск режима только мониторинга...")
    
    blocker = SpotifyAdBlocker(
        enable_audio_muting=False,
        enable_hosts_blocking=False,
        enable_cache_cleanup=False,
        verbose_logging=True
    )
    
    try:
        blocker.run()
    except KeyboardInterrupt:
        print("\n⏹️ Мониторинг остановлен")
    finally:
        blocker.cleanup()

def check_spotify_status():
    """
    Проверка статуса Spotify
    """
    print("🔍 Проверка статуса Spotify...")
    
    blocker = SpotifyAdBlocker()
    
    # Проверяем, запущен ли Spotify
    if blocker.is_spotify_running():
        print("✅ Spotify запущен")
        
        # Получаем информацию о текущем треке
        current_track = blocker.get_current_track_info()
        if current_track:
            print(f"🎵 Текущий трек: {current_track}")
        else:
            print("⏸️ Воспроизведение остановлено или реклама")
            
        # Проверяем, воспроизводится ли реклама
        if blocker.is_ad_playing():
            print("📢 Обнаружена реклама!")
        else:
            print("🎶 Воспроизводится музыка")
    else:
        print("❌ Spotify не запущен")
        print("💡 Запустите Spotify и попробуйте снова")

def install_dependencies():
    """
    Автоматическая установка зависимостей
    """
    print("📦 Установка зависимостей...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ Файл requirements.txt не найден")
        return False
    
    try:
        # Установка зависимостей
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ Зависимости успешно установлены")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки зависимостей: {e}")
        return False

def setup_environment():
    """
    Настройка окружения для работы блокировщика
    """
    print("🔧 Настройка окружения...")
    
    # Проверяем Python версию
    if sys.version_info < (3, 6):
        print("❌ Требуется Python 3.6 или выше")
        print(f"Текущая версия: {sys.version}")
        return False
    
    print(f"✅ Python версия: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Проверяем наличие Spotify
    blocker = SpotifyAdBlocker()
    if blocker.find_spotify_executable():
        print("✅ Spotify найден")
    else:
        print("⚠️ Spotify не найден или не запущен")
        print("💡 Убедитесь, что Spotify установлен и запущен")
    
    # Создаем конфигурационную папку
    config_dir = blocker.get_config_dir()
    config_dir.mkdir(exist_ok=True)
    print(f"✅ Конфигурационная папка: {config_dir}")
    
    return True

def interactive_menu():
    """
    Интерактивное меню для выбора действий
    """
    while True:
        print("\n" + "="*50)
        print("🎵 Spotify Ad Blocker - Меню")
        print("="*50)
        print("1. 🚀 Запустить базовый блокировщик")
        print("2. ⚙️ Запустить с пользовательскими настройками")
        print("3. 👁️ Режим только мониторинга")
        print("4. 🔍 Проверить статус Spotify")
        print("5. 📦 Установить зависимости")
        print("6. 🔧 Настроить окружение")
        print("7. 📋 Показать информацию о системе")
        print("8. 🧹 Очистить кэш Spotify")
        print("9. ❌ Выход")
        print("="*50)
        
        try:
            choice = input("Выберите действие (1-9): ").strip()
            
            if choice == '1':
                example_basic_usage()
            elif choice == '2':
                example_with_custom_settings()
            elif choice == '3':
                example_monitoring_only()
            elif choice == '4':
                check_spotify_status()
            elif choice == '5':
                install_dependencies()
            elif choice == '6':
                setup_environment()
            elif choice == '7':
                show_system_info()
            elif choice == '8':
                clean_spotify_cache()
            elif choice == '9':
                print("👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
                
        except KeyboardInterrupt:
            print("\n👋 До свидания!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        input("\nНажмите Enter для продолжения...")

def show_system_info():
    """
    Показать информацию о системе
    """
    print("\n💻 Информация о системе:")
    print(f"Операционная система: {os.name}")
    print(f"Платформа: {sys.platform}")
    print(f"Python версия: {sys.version}")
    print(f"Рабочая директория: {os.getcwd()}")
    
    # Проверяем установленные пакеты
    try:
        import psutil
        print(f"✅ psutil версия: {psutil.__version__}")
    except ImportError:
        print("❌ psutil не установлен")
    
    try:
        import requests
        print(f"✅ requests версия: {requests.__version__}")
    except ImportError:
        print("❌ requests не установлен")
    
    try:
        import win32api
        print("✅ pywin32 установлен")
    except ImportError:
        print("❌ pywin32 не установлен")

def clean_spotify_cache():
    """
    Очистка кэша Spotify
    """
    print("🧹 Очистка кэша Spotify...")
    
    blocker = SpotifyAdBlocker()
    
    try:
        blocker.clear_spotify_cache()
        print("✅ Кэш Spotify очищен")
    except Exception as e:
        print(f"❌ Ошибка очистки кэша: {e}")

def main():
    """
    Главная функция
    """
    print("🎵 Добро пожаловать в Spotify Ad Blocker!")
    print("Выберите режим запуска:")
    print("1. Интерактивное меню")
    print("2. Быстрый запуск (базовый блокировщик)")
    
    try:
        choice = input("Ваш выбор (1-2): ").strip()
        
        if choice == '1':
            interactive_menu()
        elif choice == '2':
            example_basic_usage()
        else:
            print("Запуск базового блокировщика по умолчанию...")
            example_basic_usage()
            
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    main()