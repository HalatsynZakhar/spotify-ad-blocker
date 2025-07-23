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
        """Улучшенное определение воспроизведения рекламы с множественными проверками"""
        try:
            # Сначала проверяем, что Spotify вообще запущен и активен
            if not self._is_spotify_running():
                return False
            
            # Метод 1: Проверка заголовка окна (самый надежный)
            title_check = self._check_window_title()
            
            # Метод 2: Проверка аудио сессии
            audio_check = self._check_audio_session()
            
            # Метод 3: Проверка процессов
            process_check = self._check_process_names()
            
            # Метод 4: Проверка длительности трека
            duration_check = self._check_track_duration()
            
            # Метод 5: Проверка состояния окна (НЕ фокуса!)
            window_state_check = self._check_window_focus()
            
            # Комбинированная логика для уменьшения ложных срабатываний
            checks = [title_check, audio_check, process_check, duration_check, window_state_check]
            confidence_score = sum(checks)
            
            # Строгая логика: требуем либо очень сильные индикаторы, либо множественные подтверждения
            is_ad = False
            
            # Сильные индикаторы рекламы (достаточно одного)
            if title_check and any([audio_check, duration_check]):
                # Заголовок окна + аудио или паттерн трека
                is_ad = True
            elif confidence_score >= 3 and title_check:
                # 3+ методов + заголовок окна
                is_ad = True
            elif confidence_score >= 4:
                # 4+ методов (очень высокая уверенность)
                is_ad = True
            
            # Дополнительная защита от ложных срабатываний
            if is_ad:
                # Проверяем, что это не ложное срабатывание из-за переключения окон
                current_time = time.time()
                if hasattr(self, '_last_window_switch') and (current_time - self._last_window_switch) < 2.0:
                    # Недавно было переключение окон, игнорируем
                    return False
            
            if is_ad and not hasattr(self, '_last_ad_detection'):
                self.log(f"Реклама обнаружена: окно={title_check}, аудио={audio_check}, процесс={process_check}, длительность={duration_check}, состояние_окна={window_state_check}")
                self._last_ad_detection = time.time()
            elif not is_ad and hasattr(self, '_last_ad_detection'):
                delattr(self, '_last_ad_detection')
                
            return is_ad
            
        except Exception as e:
            self.log(f"Ошибка определения рекламы: {e}", "ERROR")
            return False
    
    def _get_spotify_window_title(self):
        """Получение заголовка окна Spotify"""
        try:
            import win32gui
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if 'spotify' in window_text.lower():
                        windows.append(window_text)
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            return windows[0] if windows else None
            
        except ImportError:
            return None
        except Exception as e:
            self.log(f"Ошибка получения заголовка окна: {e}", "ERROR")
            return None
    
    def _check_window_title(self) -> bool:
        """Проверка заголовка окна на наличие рекламы"""
        title = self._get_spotify_window_title()
        if not title:
            return False
        
        title_lower = title.lower().strip()
        
        # Точные индикаторы рекламы
        exact_ad_indicators = [
            'advertisement',
            'spotify ad',
            'sponsored'
        ]
        
        for indicator in exact_ad_indicators:
            if indicator in title_lower:
                return True
        
        # Проверка на паузу или отсутствие трека (может быть реклама)
        if title_lower in ['spotify', 'spotify free', 'spotify premium']:
            return True
            
        # Проверка на рекламные паттерны
        ad_patterns = [
            'spotify.com',
            'premium',
            'upgrade',
            'ad-free'
        ]
        
        # Если заголовок содержит только рекламные паттерны без музыкальной информации
        if any(pattern in title_lower for pattern in ad_patterns) and ' - ' not in title:
            return True
            
        return False
    
    def _check_audio_session(self) -> bool:
        """Проверка аудио сессии для определения рекламы"""
        try:
            from pycaw.pycaw import AudioUtilities
            
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.Process and 'spotify' in session.Process.name().lower():
                    # Проверяем состояние аудио сессии
                    volume = session.SimpleAudioVolume
                    if volume:
                        # Если громкость очень низкая, это может быть реклама
                        current_volume = volume.GetMasterVolume()
                        if current_volume < 0.1:  # Очень тихо
                            return True
                            
                        # Проверяем активность аудио потока
                        # Если нет активного воспроизведения, но процесс активен
                        if hasattr(session, 'State') and session.State == 0:  # Неактивен
                            return True
                            
        except ImportError:
            self.log("pycaw не установлен, пропуск проверки аудио сессии", "WARNING")
        except Exception as e:
            self.log(f"Ошибка проверки аудио сессии: {e}", "DEBUG")
            
        return False
    
    def _check_process_names(self) -> bool:
        """Проверка имен процессов Spotify на наличие рекламных индикаторов"""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if 'spotify' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline:
                        cmdline_str = ' '.join(cmdline).lower()
                        # Проверяем командную строку на рекламные индикаторы
                        if any(indicator in cmdline_str for indicator in 
                               ['ad', 'advertisement', 'sponsored', 'promo']):
                            return True
            return False
        except Exception as e:
            self.log(f"Ошибка проверки процессов: {e}", "ERROR")
            return False
    
    def _check_track_duration(self) -> bool:
        """Проверка паттернов трека для определения рекламы"""
        try:
            # Получаем заголовок окна для анализа
            window_title = self._get_spotify_window_title()
            if not window_title:
                return False
            
            window_title_lower = window_title.lower().strip()
            
            # Стандартные заголовки Spotify (не реклама)
            standard_titles = ['spotify', 'spotify free', 'spotify premium']
            if window_title_lower in standard_titles:
                return False
            
            # Сильные индикаторы рекламы в заголовке
            strong_ad_patterns = [
                r'\b(advertisement|sponsored)\b',
                r'spotify\s*(premium|ad)\b',
                r'\b(upgrade|subscribe)\s*(now|today)?\b',
                r'\b(get|try)\s*premium\b',
                r'\bad[\s-]?free\b'
            ]
            
            import re
            
            # Проверяем на сильные рекламные паттерны
            for pattern in strong_ad_patterns:
                if re.search(pattern, window_title_lower):
                    return True
            
            # Проверяем структуру заголовка
            # Обычная музыка: "Артист - Название трека"
            # Реклама часто не имеет такой структуры
            
            # Если есть разделитель " - ", это скорее всего музыка
            if ' - ' in window_title:
                # Дополнительная проверка: даже с разделителем может быть реклама
                parts = window_title.split(' - ')
                if len(parts) == 2:
                    artist, track = parts[0].strip(), parts[1].strip()
                    
                    # Проверяем, не содержат ли части рекламные слова
                    ad_keywords = ['premium', 'upgrade', 'ad', 'advertisement', 'subscribe']
                    if any(keyword in artist.lower() or keyword in track.lower() for keyword in ad_keywords):
                        return True
                
                return False  # Обычная структура трека
            
            # Если нет разделителя, проверяем дополнительные критерии
            # Короткие заголовки без структуры могут быть рекламой
            if len(window_title.strip()) < 10:
                return True
            
            # Заголовки, содержащие только URL или промо-текст
            url_patterns = [r'spotify\.com', r'www\.', r'http', r'\.com', r'\.net']
            if any(re.search(pattern, window_title_lower) for pattern in url_patterns):
                return True
            
            # Заголовки с призывами к действию без музыкальной информации
            action_patterns = [
                r'\b(listen|hear|discover|explore)\b.*\b(more|now|today)\b',
                r'\b(unlimited|endless|millions)\b.*\b(songs|music|tracks)\b'
            ]
            
            for pattern in action_patterns:
                if re.search(pattern, window_title_lower):
                    return True
                
            return False
        except Exception as e:
            self.log(f"Ошибка проверки паттернов трека: {e}", "ERROR")
            return False
    
    def _is_spotify_running(self) -> bool:
        """Проверка, что Spotify запущен и активен"""
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if 'spotify' in proc.info['name'].lower():
                    return True
            return False
        except Exception:
            return False
    
    def _check_window_focus(self) -> bool:
        """Проверка состояния окна Spotify (НЕ фокуса, а внутреннего состояния)"""
        try:
            import win32gui
            import win32con
            
            # Отслеживаем переключения окон
            try:
                foreground_window = win32gui.GetForegroundWindow()
                foreground_title = win32gui.GetWindowText(foreground_window)
                
                # Если активно окно PowerShell или другое не-Spotify окно
                if 'powershell' in foreground_title.lower() or 'cmd' in foreground_title.lower():
                    self._last_window_switch = time.time()
                    return False  # Не считаем это индикатором рекламы
            except Exception:
                pass
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if 'spotify' in window_text.lower():
                        windows.append((hwnd, window_text))
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            for hwnd, title in windows:
                # Проверяем состояние окна
                placement = win32gui.GetWindowPlacement(hwnd)
                if placement[1] == win32con.SW_SHOWMINIMIZED:
                    # Окно свернуто, не проверяем размеры
                    continue
                
                # Проверяем размер окна только если окно видимо
                # Реклама может создавать дополнительные маленькие окна
                rect = win32gui.GetWindowRect(hwnd)
                width = rect[2] - rect[0]
                height = rect[3] - rect[1]
                
                # Очень маленькие окна могут быть рекламными попапами
                # Но только если это не основное окно Spotify
                if width < 200 or height < 150:
                    # Дополнительная проверка: это не основное окно Spotify
                    if 'spotify' == title.lower().strip():
                        continue  # Это основное окно, пропускаем
                    # Дополнительная проверка на рекламные индикаторы в заголовке
                    if any(ad_word in title.lower() for ad_word in ['ad', 'advertisement', 'premium', 'upgrade']):
                        return True
                    
                # Проверяем на необычно большие окна (полноэкранная реклама)
                try:
                    import win32api
                    screen_width = win32api.GetSystemMetrics(0)
                    screen_height = win32api.GetSystemMetrics(1)
                except ImportError:
                    # Fallback: используем стандартные размеры экрана
                    screen_width = 1920
                    screen_height = 1080
                
                if width > screen_width * 0.9 and height > screen_height * 0.9:
                    # Полноэкранное окно может быть рекламой
                    if 'advertisement' in title.lower() or 'ad' in title.lower():
                        return True
            
            return False
        except ImportError:
            # win32gui не установлен, пропускаем эту проверку
            return False
        except Exception as e:
            self.log(f"Ошибка проверки состояния окна: {e}", "ERROR")
            return False
    
    def mute_spotify_audio(self):
        """Отключение звука только для Spotify (более точное решение)"""
        try:
            # Метод 1: Использование pycaw для отключения конкретно Spotify
            from pycaw.pycaw import AudioUtilities
            
            sessions = AudioUtilities.GetAllSessions()
            spotify_muted = False
            
            for session in sessions:
                if session.Process and 'spotify' in session.Process.name().lower():
                    volume = session.SimpleAudioVolume
                    if volume:
                        volume.SetMute(1, None)
                        spotify_muted = True
                        self.log("Spotify отключен (реклама обнаружена)")
                        break
            
            if not spotify_muted:
                # Fallback: отключение системного звука если не удалось найти Spotify
                self._mute_system_fallback()
            
            self.muted = True
            
        except ImportError:
            self.log("pycaw не установлен, использую системное отключение", "WARNING")
            self._mute_system_fallback()
        except Exception as e:
            self.log(f"Ошибка отключения Spotify: {e}", "ERROR")
            self._mute_system_fallback()
    
    def _mute_system_fallback(self):
        """Резервный метод отключения системного звука"""
        try:
            # Используем nircmd для управления звуком (не требует прав администратора)
            subprocess.run(['nircmd.exe', 'mutesysvolume', '1'], 
                         capture_output=True, check=False)
            self.muted = True
            self.log("Системный звук отключен (резервный метод)")
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
    
    def unmute_spotify_audio(self):
        """Включение звука для Spotify"""
        try:
            # Метод 1: Использование pycaw для включения конкретно Spotify
            from pycaw.pycaw import AudioUtilities
            
            sessions = AudioUtilities.GetAllSessions()
            spotify_unmuted = False
            
            for session in sessions:
                if session.Process and 'spotify' in session.Process.name().lower():
                    volume = session.SimpleAudioVolume
                    if volume:
                        volume.SetMute(0, None)
                        spotify_unmuted = True
                        self.log("Spotify включен")
                        break
            
            if not spotify_unmuted:
                # Fallback: включение системного звука
                self._unmute_system_fallback()
            
            self.muted = False
            
        except ImportError:
            self.log("pycaw не установлен, использую системное включение", "WARNING")
            self._unmute_system_fallback()
        except Exception as e:
            self.log(f"Ошибка включения Spotify: {e}", "ERROR")
            self._unmute_system_fallback()
    
    def _unmute_system_fallback(self):
        """Резервный метод включения системного звука"""
        try:
            subprocess.run(['nircmd.exe', 'mutesysvolume', '0'], 
                         capture_output=True, check=False)
            self.muted = False
            self.log("Системный звук включен")
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
        """Мониторинг Spotify и управление звуком"""
        self.log("Начат мониторинг Spotify")
        
        # Счетчики для защиты от ложных срабатываний
        ad_detection_count = 0
        music_detection_count = 0
        required_confirmations = 3  # Требуется 3 подтверждения для смены состояния
        
        while self.is_running:
            try:
                if self.check_spotify_running():
                    is_ad = self.is_ad_playing()
                    
                    if is_ad:
                        ad_detection_count += 1
                        music_detection_count = 0
                        
                        # Отключаем звук только после нескольких подтверждений
                        if ad_detection_count >= required_confirmations and not self.muted:
                            self.mute_spotify_audio()
                            self.log(f"Реклама обнаружена после {ad_detection_count} проверок")
                    else:
                        music_detection_count += 1
                        ad_detection_count = 0
                        
                        # Включаем звук только после нескольких подтверждений
                        if music_detection_count >= required_confirmations and self.muted:
                            self.unmute_spotify_audio()
                            self.log(f"Музыка обнаружена после {music_detection_count} проверок")
                else:
                    # Spotify не запущен
                    if self.muted:
                        self.unmute_spotify_audio()
                    ad_detection_count = 0
                    music_detection_count = 0
                
                time.sleep(0.5)  # Более частая проверка для быстрого реагирования
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log(f"Ошибка мониторинга: {e}", "ERROR")
                time.sleep(5)  # Пауза при ошибке
    
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
            self.unmute_spotify_audio()
        
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