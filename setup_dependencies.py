#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт автоматической установки и настройки зависимостей для Spotify Ad Blocker

Этот скрипт:
1. Проверяет наличие всех необходимых зависимостей
2. Автоматически устанавливает отсутствующие пакеты
3. Проверяет совместимость системы
4. Создает конфигурационные файлы
5. Запускает диагностику системы
"""

import sys
import subprocess
import importlib
import ctypes
import os
import json
from pathlib import Path
from typing import List, Dict, Tuple

# Список необходимых зависимостей
REQUIRED_PACKAGES = {
    'psutil': '5.9.0',
    'requests': '2.28.0', 
    'pycaw': '20220416',
    'pywin32': '305'
}

# Опциональные пакеты для улучшенной функциональности
OPTIONAL_PACKAGES = {
    'tqdm': '4.64.0',  # Прогресс-бары
    'colorama': '0.4.6',  # Цветной вывод
    'psutil': '5.9.0'  # Мониторинг системы
}

class Colors:
    """ANSI цвета для консольного вывода"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

class DependencyManager:
    """Менеджер зависимостей для Spotify Ad Blocker"""
    
    def __init__(self):
        self.missing_packages = []
        self.failed_packages = []
        self.installed_packages = []
        
    def check_admin_rights(self) -> bool:
        """Проверка прав администратора"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def check_python_version(self) -> bool:
        """Проверка версии Python"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 7):
            print(f"{Colors.RED}❌ Требуется Python 3.7 или выше. Текущая версия: {version.major}.{version.minor}{Colors.END}")
            return False
        
        print(f"{Colors.GREEN}✅ Python {version.major}.{version.minor}.{version.micro} - OK{Colors.END}")
        return True
    
    def check_package(self, package_name: str) -> bool:
        """Проверка наличия пакета"""
        try:
            importlib.import_module(package_name)
            return True
        except ImportError:
            return False
    
    def get_package_version(self, package_name: str) -> str:
        """Получение версии установленного пакета"""
        try:
            module = importlib.import_module(package_name)
            return getattr(module, '__version__', 'unknown')
        except:
            return 'not installed'
    
    def install_package(self, package_name: str, version: str = None) -> bool:
        """Установка пакета через pip"""
        try:
            package_spec = f"{package_name}>={version}" if version else package_name
            
            print(f"{Colors.BLUE}📦 Устанавливаю {package_spec}...{Colors.END}")
            
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', package_spec, '--upgrade'
            ], capture_output=True, text=True, check=True)
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ {package_name} успешно установлен{Colors.END}")
                self.installed_packages.append(package_name)
                return True
            else:
                print(f"{Colors.RED}❌ Ошибка установки {package_name}: {result.stderr}{Colors.END}")
                self.failed_packages.append(package_name)
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"{Colors.RED}❌ Ошибка установки {package_name}: {e.stderr}{Colors.END}")
            self.failed_packages.append(package_name)
            return False
        except Exception as e:
            print(f"{Colors.RED}❌ Неожиданная ошибка при установке {package_name}: {e}{Colors.END}")
            self.failed_packages.append(package_name)
            return False
    
    def check_all_dependencies(self) -> Dict[str, bool]:
        """Проверка всех зависимостей"""
        print(f"\n{Colors.BOLD}🔍 Проверка зависимостей...{Colors.END}")
        
        results = {}
        
        for package, min_version in REQUIRED_PACKAGES.items():
            is_installed = self.check_package(package)
            current_version = self.get_package_version(package)
            
            if is_installed:
                print(f"{Colors.GREEN}✅ {package} ({current_version}){Colors.END}")
                results[package] = True
            else:
                print(f"{Colors.RED}❌ {package} - не установлен{Colors.END}")
                results[package] = False
                self.missing_packages.append(package)
        
        return results
    
    def install_missing_dependencies(self) -> bool:
        """Установка отсутствующих зависимостей"""
        if not self.missing_packages:
            print(f"{Colors.GREEN}✅ Все зависимости уже установлены{Colors.END}")
            return True
        
        print(f"\n{Colors.BOLD}📦 Установка отсутствующих зависимостей...{Colors.END}")
        
        success = True
        for package in self.missing_packages:
            version = REQUIRED_PACKAGES.get(package)
            if not self.install_package(package, version):
                success = False
        
        return success
    
    def install_optional_packages(self) -> None:
        """Установка опциональных пакетов"""
        print(f"\n{Colors.BOLD}🎨 Установка дополнительных пакетов для улучшенной функциональности...{Colors.END}")
        
        for package, version in OPTIONAL_PACKAGES.items():
            if not self.check_package(package):
                print(f"{Colors.CYAN}Устанавливаю опциональный пакет {package}...{Colors.END}")
                self.install_package(package, version)
    
    def create_config_file(self) -> None:
        """Создание конфигурационного файла"""
        config = {
            "check_interval": 0.5,
            "confirmation_threshold": 3,
            "window_switch_protection_time": 2.0,
            "log_level": "INFO",
            "use_pycaw": self.check_package('pycaw'),
            "auto_start_with_spotify": False,
            "minimize_to_tray": False,
            "ad_detection_methods": {
                "window_title": True,
                "audio_session": True,
                "network_monitoring": False
            },
            "performance": {
                "adaptive_checking": True,
                "cache_window_info": True,
                "max_memory_mb": 100
            }
        }
        
        config_path = Path('config.json')
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print(f"{Colors.GREEN}✅ Конфигурационный файл создан: {config_path}{Colors.END}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️ Не удалось создать конфигурационный файл: {e}{Colors.END}")
    
    def run_system_diagnostics(self) -> None:
        """Запуск диагностики системы"""
        print(f"\n{Colors.BOLD}🔧 Диагностика системы...{Colors.END}")
        
        # Проверка операционной системы
        if sys.platform != 'win32':
            print(f"{Colors.RED}❌ Этот блокировщик предназначен только для Windows{Colors.END}")
            return
        
        print(f"{Colors.GREEN}✅ Операционная система: Windows{Colors.END}")
        
        # Проверка прав администратора
        if self.check_admin_rights():
            print(f"{Colors.GREEN}✅ Права администратора: Есть{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️ Права администратора: Отсутствуют (рекомендуется запуск от имени администратора){Colors.END}")
        
        # Проверка Spotify
        try:
            import psutil
            spotify_running = any('spotify' in p.name().lower() for p in psutil.process_iter(['name']))
            if spotify_running:
                print(f"{Colors.GREEN}✅ Spotify: Запущен{Colors.END}")
            else:
                print(f"{Colors.YELLOW}⚠️ Spotify: Не запущен{Colors.END}")
        except:
            print(f"{Colors.YELLOW}⚠️ Не удалось проверить статус Spotify{Colors.END}")
        
        # Проверка аудио системы
        if self.check_package('pycaw'):
            print(f"{Colors.GREEN}✅ Аудио управление: pycaw доступен (быстрое отключение звука){Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️ Аудио управление: Будет использоваться PowerShell (медленнее){Colors.END}")
    
    def create_launcher_script(self) -> None:
        """Создание скрипта запуска"""
        launcher_content = '''@echo off
echo Запуск Spotify Ad Blocker...
echo.

REM Проверка прав администратора
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Запущено с правами администратора
) else (
    echo [WARNING] Рекомендуется запуск от имени администратора
    echo.
)

REM Запуск блокировщика
python spotify_ad_blocker.py

echo.
echo Нажмите любую клавишу для выхода...
pause >nul
'''
        
        try:
            with open('start_ad_blocker.bat', 'w', encoding='cp1251') as f:
                f.write(launcher_content)
            print(f"{Colors.GREEN}✅ Создан скрипт запуска: start_ad_blocker.bat{Colors.END}")
        except Exception as e:
            print(f"{Colors.YELLOW}⚠️ Не удалось создать скрипт запуска: {e}{Colors.END}")
    
    def print_summary(self) -> None:
        """Вывод итогового отчета"""
        print(f"\n{Colors.BOLD}📋 ИТОГОВЫЙ ОТЧЕТ{Colors.END}")
        print("=" * 50)
        
        if self.installed_packages:
            print(f"{Colors.GREEN}✅ Установленные пакеты: {', '.join(self.installed_packages)}{Colors.END}")
        
        if self.failed_packages:
            print(f"{Colors.RED}❌ Не удалось установить: {', '.join(self.failed_packages)}{Colors.END}")
        
        if not self.missing_packages and not self.failed_packages:
            print(f"{Colors.GREEN}🎉 Все зависимости успешно установлены!{Colors.END}")
            print(f"{Colors.CYAN}Теперь вы можете запустить блокировщик командой:{Colors.END}")
            print(f"{Colors.WHITE}python spotify_ad_blocker.py{Colors.END}")
            print(f"{Colors.CYAN}Или используйте созданный скрипт:{Colors.END}")
            print(f"{Colors.WHITE}start_ad_blocker.bat{Colors.END}")
        else:
            print(f"{Colors.YELLOW}⚠️ Некоторые зависимости не установлены. Блокировщик может работать с ограниченной функциональностью.{Colors.END}")
        
        print("\n" + "=" * 50)

def main():
    """Главная функция установки"""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                 SPOTIFY AD BLOCKER SETUP                    ║")
    print("║              Автоматическая установка зависимостей          ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    manager = DependencyManager()
    
    # Проверка версии Python
    if not manager.check_python_version():
        sys.exit(1)
    
    # Проверка зависимостей
    dependencies_status = manager.check_all_dependencies()
    
    # Установка отсутствующих зависимостей
    if manager.missing_packages:
        print(f"\n{Colors.YELLOW}⚠️ Обнаружены отсутствующие зависимости. Начинаю установку...{Colors.END}")
        
        if not manager.install_missing_dependencies():
            print(f"{Colors.RED}❌ Не удалось установить некоторые зависимости{Colors.END}")
    
    # Установка опциональных пакетов
    try:
        manager.install_optional_packages()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Установка прервана пользователем{Colors.END}")
    
    # Создание конфигурационных файлов
    manager.create_config_file()
    manager.create_launcher_script()
    
    # Диагностика системы
    manager.run_system_diagnostics()
    
    # Итоговый отчет
    manager.print_summary()
    
    print(f"\n{Colors.GREEN}🚀 Установка завершена! Удачного использования!{Colors.END}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️ Установка прервана пользователем{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Критическая ошибка: {e}{Colors.END}")
        sys.exit(1)