#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрое исправление проблемы с pycaw для Spotify Ad Blocker

Этот скрипт:
1. Проверяет наличие pycaw
2. Устанавливает его при отсутствии
3. Проверяет корректность установки
4. Предлагает перезапустить блокировщик
"""

import sys
import subprocess
import importlib
from pathlib import Path

def check_pycaw() -> bool:
    """Проверка наличия pycaw"""
    try:
        import pycaw
        print("✅ pycaw уже установлен")
        return True
    except ImportError:
        print("❌ pycaw не найден")
        return False

def install_pycaw() -> bool:
    """Установка pycaw"""
    print("📦 Устанавливаю pycaw...")
    
    try:
        # Попробуем установить через pip
        result = subprocess.run([
            sys.executable, '-m', 'pip', 'install', 'pycaw', '--upgrade'
        ], capture_output=True, text=True, check=True)
        
        if result.returncode == 0:
            print("✅ pycaw успешно установлен")
            return True
        else:
            print(f"❌ Ошибка установки: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка установки pycaw: {e.stderr}")
        
        # Попробуем альтернативный способ
        print("🔄 Пробую альтернативный способ установки...")
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', 'pycaw', '--user', '--upgrade'
            ], capture_output=True, text=True, check=True)
            
            if result.returncode == 0:
                print("✅ pycaw установлен через --user")
                return True
        except:
            pass
        
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def test_pycaw_functionality() -> bool:
    """Тестирование функциональности pycaw"""
    print("🧪 Тестирую функциональность pycaw...")
    
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL
        
        # Попробуем получить аудио устройства
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        
        # Получим текущий уровень громкости (не изменяем его)
        current_volume = volume.GetMasterVolumeLevel()
        
        print(f"✅ pycaw работает корректно (текущая громкость: {current_volume:.2f} dB)")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования pycaw: {e}")
        return False

def check_spotify_blocker() -> bool:
    """Проверка наличия основного файла блокировщика"""
    blocker_path = Path('spotify_ad_blocker.py')
    if blocker_path.exists():
        print(f"✅ Найден файл блокировщика: {blocker_path}")
        return True
    else:
        print(f"❌ Файл блокировщика не найден: {blocker_path}")
        return False

def offer_restart_blocker() -> None:
    """Предложение перезапустить блокировщик"""
    if not check_spotify_blocker():
        return
    
    print("\n🚀 pycaw готов к использованию!")
    print("Теперь блокировщик будет использовать быстрое отключение звука.")
    
    response = input("\nХотите запустить блокировщик сейчас? (y/n): ").lower().strip()
    
    if response in ['y', 'yes', 'да', 'д']:
        print("🎵 Запускаю Spotify Ad Blocker...")
        try:
            subprocess.Popen([sys.executable, 'spotify_ad_blocker.py'])
            print("✅ Блокировщик запущен в отдельном процессе")
        except Exception as e:
            print(f"❌ Ошибка запуска: {e}")
            print("Запустите блокировщик вручную: python spotify_ad_blocker.py")
    else:
        print("Запустите блокировщик вручную когда будете готовы:")
        print("python spotify_ad_blocker.py")

def main():
    """Главная функция"""
    print("🔧 Исправление проблемы с pycaw для Spotify Ad Blocker")
    print("=" * 60)
    
    # Проверяем текущее состояние
    if check_pycaw():
        # pycaw уже установлен, проверим его работоспособность
        if test_pycaw_functionality():
            print("\n🎉 pycaw работает корректно! Никаких действий не требуется.")
            print("Ваш блокировщик должен использовать быстрое отключение звука.")
        else:
            print("\n⚠️ pycaw установлен, но не работает корректно.")
            print("Попробуем переустановить...")
            if install_pycaw() and test_pycaw_functionality():
                offer_restart_blocker()
            else:
                print("❌ Не удалось исправить pycaw. Блокировщик будет использовать PowerShell.")
    else:
        # pycaw не установлен
        print("\n📦 Устанавливаю pycaw для улучшения производительности...")
        
        if install_pycaw():
            # Проверяем установку
            if check_pycaw() and test_pycaw_functionality():
                offer_restart_blocker()
            else:
                print("❌ pycaw установлен, но не работает. Возможны проблемы с системой.")
        else:
            print("❌ Не удалось установить pycaw.")
            print("\nВозможные решения:")
            print("1. Запустите скрипт от имени администратора")
            print("2. Обновите pip: python -m pip install --upgrade pip")
            print("3. Установите вручную: pip install pycaw")
            print("\nБлокировщик будет работать через PowerShell (медленнее).")
    
    print("\n" + "=" * 60)
    print("Готово! Нажмите Enter для выхода...")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        print("Нажмите Enter для выхода...")
        input()