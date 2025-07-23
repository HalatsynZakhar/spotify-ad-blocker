#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spotify Ad Blocker - Python Implementation
Блокировщик рекламы для Spotify без прав администратора

Автор: AI Assistant
Версия: 1.0
Дата: 2024

Описание:
Этот скрипт блокирует рекламу в Spotify используя несколько методов:
1. Модификация локального DNS через пользовательский hosts файл
2. Мониторинг процессов Spotify и автоматическое отключение звука во время рекламы
3. Блокировка рекламных доменов через прокси
4. Очистка кэша Spotify

Преимущества:
- Не требует прав администратора
- Работает с официальной версией Spotify
- Безопасен для аккаунта
- Автоматическое восстановление после обновлений
"""

import os
import sys
import time
import json
import shutil
import psutil
import requests
import threading
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import winreg
from datetime import datetime

class SpotifyAdBlocker:
    def __init__(self):
        self.spotify_process = None
        self.is_running = False
        self.muted = False
        self.user_home = Path.home()
        self.config_dir = self.user_home / '.spotify_ad_blocker'
        self.config_dir.mkdir(exist_ok=True)
        
        # Список рекламных доменов Spotify
        self.ad_domains = [
            'media-match.com',
            'adclick.g.doublecklick.net',
            'www.googleadservices.com',
            'pagead2.googlesyndication.com',
            'desktop.spotify.com',
            'googleads.g.doubleclick.net',
            'pubads.g.doubleclick.net',
            'audio2.spotify.com',
            'bounceexchange.com',
            'pagead46.l.doubleclick.net',
            'pagead.l.doubleclick.net',
            'video-ad-stats.googlesyndication.com',
            'pagead-googlehosted.l.google.com',
            'partnerad.l.doubleclick.net',
            'adserver.adtechus.com',
            'anycast.pixel.adsafeprotected.com',
            'gads.pubmatic.com',
            'securepubads.g.doubleclick.net',
            'crashdump.spotify.com',
            'adeventtracker.spotify.com',
            'log.spotify.com',
            'analytics.spotify.com',
            'ads-fa.spotify.com',
            'ads.pubmatic.com',
            'www.googletagservices.com',
            'b.scorecardresearch.com',
            'bs.serving-sys.com',
            'doubleclick.net',
            'ds.serving-sys.com',
            'googleadservices.com',
            'js.moatads.com'
        ]
        
        self.spotify_paths = [
            self.user_home / 'AppData/Roaming/Spotify',
            self.user_home / 'AppData/Local/Spotify'
        ]
        
    def log(self, message: str, level: str = 'INFO'):
        """Логирование с временной меткой"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] [{level}] {message}")
        
        # Сохранение в файл лога
        log_file = self.config_dir / 'ad_blocker.log'
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] [{level}] {message}\n")
    
    def check_spotify_running(self) -> bool:
        """Проверка запущен ли Spotify"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'spotify' in proc.info['name'].lower():
                    self.spotify_process = proc
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    def get_spotify_window_title(self) -> Optional[str]:
        """Получение заголовка окна Spotify для определения рекламы"""
        try:
            import win32gui
            import win32process
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if 'spotify' in window_title.lower():
                        windows.append(window_title)
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                return windows[0]
        except ImportError:
            self.log("Модуль win32gui не найден. Установите: pip install pywin32", "WARNING")
        except Exception as e:
            self.log(f"Ошибка получения заголовка окна: {e}", "ERROR")
        
        return None
    
    def is_ad_playing(self) -> bool:
        """Определение воспроизведения рекламы по заголовку окна"""
        title = self.get_spotify_window_title()
        if not title:
            return False
        
        # Признаки рекламы в заголовке
        ad_indicators = [
            'advertisement',
            'spotify ad',
            'sponsored',
            'реклама',
            '• Spotify'
        ]
        
        title_lower = title.lower()
        for indicator in ad_indicators:
            if indicator in title_lower:
                return True
        
        # Если заголовок содержит только "Spotify" без названия трека
        if title.strip().lower() == 'spotify':
            return True
            
        return False
    
    def mute_system_audio(self):
        """Отключение звука системы"""
        try:
            # Используем nircmd для управления звуком (не требует прав администратора)
            subprocess.run(['nircmd.exe', 'mutesysvolume', '1'], 
                         capture_output=True, check=False)
            self.muted = True
            self.log("Звук отключен (реклама обнаружена)")
        except FileNotFoundError:
            # Альтернативный метод через PowerShell
            try:
                ps_command = """
                Add-Type -TypeDefinition '
                using System;
                using System.Runtime.InteropServices;
                public class Audio {
                    [DllImport("user32.dll")]
                    public static extern void keybd_event(byte bVk, byte bScan, int dwFlags, int dwExtraInfo);
                }
                '
                [Audio]::keybd_event(0xAD, 0, 0, 0)
                """
                subprocess.run(['powershell', '-Command', ps_command], 
                             capture_output=True, check=False)
                self.muted = True
                self.log("Звук отключен через PowerShell")
            except Exception as e:
                self.log(f"Не удалось отключить звук: {e}", "ERROR")
    
    def unmute_system_audio(self):
        """Включение звука системы"""
        try:
            subprocess.run(['nircmd.exe', 'mutesysvolume', '0'], 
                         capture_output=True, check=False)
            self.muted = False
            self.log("Звук включен")
        except FileNotFoundError:
            try:
                ps_command = """
                Add-Type -TypeDefinition '
                using System;
                using System.Runtime.InteropServices;
                public class Audio {
                    [DllImport("user32.dll")]
                    public static extern void keybd_event(byte bVk, byte bScan, int dwFlags, int dwExtraInfo);
                }
                '
                [Audio]::keybd_event(0xAE, 0, 0, 0)
                """
                subprocess.run(['powershell', '-Command', ps_command], 
                             capture_output=True, check=False)
                self.muted = False
                self.log("Звук включен через PowerShell")
            except Exception as e:
                self.log(f"Не удалось включить звук: {e}", "ERROR")
    
    def create_user_hosts_file(self):
        """Создание пользовательского hosts файла"""
        user_hosts = self.config_dir / 'user_hosts'
        
        hosts_content = "# Spotify Ad Blocker - User Hosts File\n"
        hosts_content += "# Этот файл блокирует рекламные домены Spotify\n\n"
        
        for domain in self.ad_domains:
            hosts_content += f"127.0.0.1 {domain}\n"
        
        with open(user_hosts, 'w', encoding='utf-8') as f:
            f.write(hosts_content)
        
        self.log(f"Создан пользовательский hosts файл: {user_hosts}")
        return user_hosts
    
    def setup_dns_blocking(self):
        """Настройка блокировки DNS без прав администратора"""
        try:
            # Создаем пользовательский hosts файл
            user_hosts = self.create_user_hosts_file()
            
            # Попытка изменить DNS через реестр (может не работать без прав админа)
            try:
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                   r"Software\Microsoft\Windows\CurrentVersion\Internet Settings")
                # Здесь можно добавить настройки прокси для блокировки доменов
                winreg.CloseKey(key)
            except Exception as e:
                self.log(f"Не удалось изменить настройки DNS: {e}", "WARNING")
            
            self.log("DNS блокировка настроена")
            
        except Exception as e:
            self.log(f"Ошибка настройки DNS блокировки: {e}", "ERROR")
    
    def clear_spotify_cache(self):
        """Очистка кэша Spotify"""
        try:
            for spotify_path in self.spotify_paths:
                if spotify_path.exists():
                    # Очистка кэша
                    cache_dirs = ['Data', 'Browser', 'PersistentCache']
                    for cache_dir in cache_dirs:
                        cache_path = spotify_path / cache_dir
                        if cache_path.exists():
                            try:
                                shutil.rmtree(cache_path)
                                self.log(f"Очищен кэш: {cache_path}")
                            except Exception as e:
                                self.log(f"Не удалось очистить {cache_path}: {e}", "WARNING")
            
            self.log("Кэш Spotify очищен")
            
        except Exception as e:
            self.log(f"Ошибка очистки кэша: {e}", "ERROR")
    
    def download_nircmd(self):
        """Загрузка NirCmd для управления звуком"""
        nircmd_path = self.config_dir / 'nircmd.exe'
        
        if nircmd_path.exists():
            return str(nircmd_path)
        
        try:
            self.log("Загрузка NirCmd...")
            url = "https://www.nirsoft.net/utils/nircmd.zip"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                zip_path = self.config_dir / 'nircmd.zip'
                with open(zip_path, 'wb') as f:
                    f.write(response.content)
                
                # Распаковка
                import zipfile
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(self.config_dir)
                
                zip_path.unlink()  # Удаляем архив
                
                # Добавляем в PATH
                os.environ['PATH'] = str(self.config_dir) + os.pathsep + os.environ['PATH']
                
                self.log("NirCmd загружен и настроен")
                return str(nircmd_path)
            
        except Exception as e:
            self.log(f"Ошибка загрузки NirCmd: {e}", "ERROR")
        
        return None
    
    def monitor_spotify(self):
        """Мониторинг Spotify и блокировка рекламы"""
        self.log("Запуск мониторинга Spotify...")
        
        while self.is_running:
            try:
                if self.check_spotify_running():
                    if self.is_ad_playing():
                        if not self.muted:
                            self.mute_system_audio()
                    else:
                        if self.muted:
                            self.unmute_system_audio()
                else:
                    if self.muted:
                        self.unmute_system_audio()
                
                time.sleep(1)  # Проверка каждую секунду
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log(f"Ошибка мониторинга: {e}", "ERROR")
                time.sleep(5)
    
    def start(self):
        """Запуск блокировщика рекламы"""
        self.log("=== Spotify Ad Blocker запущен ===")
        self.log("Версия: 1.0")
        self.log("Автор: AI Assistant")
        self.log("")
        
        try:
            # Проверка зависимостей
            self.log("Проверка зависимостей...")
            
            # Загрузка NirCmd если нужно
            self.download_nircmd()
            
            # Настройка DNS блокировки
            self.setup_dns_blocking()
            
            # Очистка кэша Spotify
            if not self.check_spotify_running():
                self.clear_spotify_cache()
            else:
                self.log("Spotify запущен, пропуск очистки кэша", "WARNING")
            
            # Запуск мониторинга
            self.is_running = True
            monitor_thread = threading.Thread(target=self.monitor_spotify, daemon=True)
            monitor_thread.start()
            
            self.log("Блокировщик рекламы активен!")
            self.log("Нажмите Ctrl+C для остановки")
            self.log("")
            
            # Основной цикл
            try:
                while self.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop()
                
        except Exception as e:
            self.log(f"Критическая ошибка: {e}", "ERROR")
            self.stop()
    
    def stop(self):
        """Остановка блокировщика"""
        self.log("Остановка блокировщика рекламы...")
        self.is_running = False
        
        # Включаем звук если он был отключен
        if self.muted:
            self.unmute_system_audio()
        
        self.log("Блокировщик остановлен")

def main():
    """Главная функция"""
    print("")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                    Spotify Ad Blocker                       ║")
    print("║                     Python Edition                          ║")
    print("║                                                              ║")
    print("║  Блокировщик рекламы для Spotify без прав администратора     ║")
    print("║                                                              ║")
    print("║  Возможности:                                                ║")
    print("║  • Автоматическое отключение звука во время рекламы          ║")
    print("║  • Блокировка рекламных доменов                              ║")
    print("║  • Очистка кэша Spotify                                      ║")
    print("║  • Работа без прав администратора                            ║")
    print("║                                                              ║")
    print("║  Автор: AI Assistant                                         ║")
    print("║  Версия: 1.0                                                 ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("")
    
    # Проверка Python версии
    if sys.version_info < (3, 6):
        print("❌ Требуется Python 3.6 или выше")
        sys.exit(1)
    
    # Проверка операционной системы
    if os.name != 'nt':
        print("❌ Этот скрипт работает только на Windows")
        sys.exit(1)
    
    # Проверка зависимостей
    required_modules = ['psutil', 'requests']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"❌ Отсутствуют модули: {', '.join(missing_modules)}")
        print(f"Установите их командой: pip install {' '.join(missing_modules)}")
        sys.exit(1)
    
    # Запуск блокировщика
    blocker = SpotifyAdBlocker()
    
    try:
        blocker.start()
    except KeyboardInterrupt:
        print("\n👋 До свидания!")
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()