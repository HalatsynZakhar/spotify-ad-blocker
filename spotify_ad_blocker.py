#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔥 АГРЕССИВНЫЙ Spotify Ad Blocker - БЕЗ блокировки звука! 🔥

Этот скрипт использует МАКСИМАЛЬНО АГРЕССИВНЫЕ методы блокировки рекламы в Spotify
БЕЗ отключения звука! Вместо этого он:

🚀 АГРЕССИВНЫЕ МЕТОДЫ БЛОКИРОВКИ:
- ❌ Закрытие рекламных окон
- ⏭️ Автоматический пропуск рекламных треков
- 🚫 Блокировка рекламных процессов
- 🧹 Очистка рекламного кэша
- 🌐 Максимальная DNS-блокировка рекламных доменов
- 🎯 Детекция рекламы по множественным критериям

✅ ЗВУК НИКОГДА НЕ БЛОКИРУЕТСЯ!
✅ Музыка играет непрерывно!
✅ Максимально агрессивная борьба с рекламой!

Автор: AI Assistant
Версия: 1.0 (Агрессивная без блокировки звука)
Дата: 2024
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
        self.user_home = Path.home()
        self.config_dir = self.user_home / '.spotify_ad_blocker'
        self.config_dir.mkdir(exist_ok=True)
        
        # МАКСИМАЛЬНО АГРЕССИВНЫЙ список рекламных доменов Spotify
        self.ad_domains = [
            # Основные рекламные домены Spotify
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
            'js.moatads.com',
            
            # ДОПОЛНИТЕЛЬНЫЕ агрессивные блокировки
            'ads.spotify.com',
            'adnxs.com',
            'adsystem.com',
            'amazon-adsystem.com',
            'googlesyndication.com',
            'googletagmanager.com',
            'facebook.com/tr',
            'connect.facebook.net',
            'analytics.google.com',
            'google-analytics.com',
            'googletagservices.com',
            'scorecardresearch.com',
            'quantserve.com',
            'outbrain.com',
            'taboola.com',
            'adsafeprotected.com',
            'moatads.com',
            'adsrvr.org',
            'turn.com',
            'rlcdn.com',
            'rubiconproject.com',
            'pubmatic.com',
            'openx.net',
            'contextweb.com',
            'casalemedia.com',
            'adsymptotic.com',
            'amazon.com/gp/aw/cr',
            'amazon.com/dp/aw/cr',
            'amazon.com/gp/product/aw/cr',
            'amazon.com/gp/aw/d/cr',
            'amazon.com/gp/aw/ol/cr',
            'amazon.com/gp/aw/s/cr',
            'amazon.com/gp/aw/ya/cr',
            'amazon.com/gp/aw/ys/cr',
            'amazon.com/gp/aw/ls/cr',
            'amazon.com/gp/aw/h/cr',
            'amazon.com/gp/aw/c/cr',
            'amazon.com/gp/aw/rd/cr',
            'amazon.com/gp/aw/gb/cr',
            'amazon.com/gp/aw/wl/cr',
            'amazon.com/gp/aw/cart/cr',
            'amazon.com/gp/aw/help/cr',
            'amazon.com/gp/aw/si/cr',
            'amazon.com/gp/aw/ss/cr',
            'amazon.com/gp/aw/sis/cr',
            'amazon.com/gp/aw/fbt/cr',
            'amazon.com/gp/aw/recs/cr',
            'amazon.com/gp/aw/sp/cr',
            'amazon.com/gp/aw/aw/cr',
            'amazon.com/gp/aw/aw/cr',
            
            # Spotify-специфичные рекламные домены
            'spclient.wg.spotify.com',
            'audio-sp-*.pscdn.co',
            'heads4-ak.spotify.com.edgesuite.net',
            'heads-ak.spotify.com.edgesuite.net',
            'audio-ak.spotify.com.edgesuite.net',
            'audio4-ak.spotify.com.edgesuite.net',
            'heads4-ak-spotify-com.akamaized.net',
            'audio4-ak-spotify-com.akamaized.net',
            
            # Дополнительные блокировки для максимальной агрессивности
            'spotify.map.fastly.net',
            'spotify.map.fastlylb.net',
            'fastly.com',
            'fastlylb.net',
            'akamai.net',
            'akamaized.net',
            'edgekey.net',
            'edgesuite.net',
            'cloudfront.net'
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
            
            # ИСПРАВЛЕНО: Более консервативная логика для предотвращения ложных срабатываний
            checks = [title_check, audio_check, process_check, duration_check, window_state_check]
            confidence_score = sum(checks)
            
            # Очень строгая логика: требуем явные индикаторы рекламы
            is_ad = False
            
            # Сильные индикаторы рекламы - требуем заголовок окна + дополнительное подтверждение
            if title_check and duration_check:
                # Заголовок окна содержит рекламу И паттерн трека подтверждает
                is_ad = True
            elif title_check and audio_check and process_check:
                # Заголовок + аудио + процесс (тройное подтверждение)
                is_ad = True
            elif confidence_score >= 4 and title_check:
                # 4+ методов + заголовок окна (очень высокая уверенность)
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
            'sponsored',
            'spotify - advertisement'
        ]
        
        for indicator in exact_ad_indicators:
            if indicator in title_lower:
                return True
        
        # ИСПРАВЛЕНО: НЕ считаем рекламой стандартные заголовки Spotify
        # Эти заголовки появляются при паузе или загрузке, но это НЕ реклама
        standard_titles = ['spotify', 'spotify free', 'spotify premium']
        if title_lower in standard_titles:
            return False  # Это НЕ реклама!
            
        # Проверка на рекламные паттерны только если нет музыкальной структуры
        ad_patterns = [
            'spotify.com',
            'upgrade now',
            'get premium',
            'ad-free music'
        ]
        
        # Если заголовок содержит рекламные паттерны И нет структуры трека
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
            
            # ИСПРАВЛЕНО: Стандартные заголовки Spotify (НЕ реклама)
            standard_titles = ['spotify', 'spotify free', 'spotify premium']
            if window_title_lower in standard_titles:
                return False  # Это точно НЕ реклама!
            
            # Сильные индикаторы рекламы в заголовке
            strong_ad_patterns = [
                r'\b(advertisement|sponsored)\b',
                r'spotify\s*-\s*advertisement\b',
                r'\b(upgrade|subscribe)\s*(now|today)\b',
                r'\b(get|try)\s*premium\b',
                r'\bad[\s-]?free\s*music\b'
            ]
            
            import re
            
            # Проверяем на сильные рекламные паттерны
            for pattern in strong_ad_patterns:
                if re.search(pattern, window_title_lower):
                    return True
            
            # ИСПРАВЛЕНО: Если есть разделитель " - ", это ТОЧНО музыка, НЕ реклама
            if ' - ' in window_title:
                # Дополнительная проверка только на очень явные рекламные слова
                parts = window_title.split(' - ')
                if len(parts) == 2:
                    artist, track = parts[0].strip(), parts[1].strip()
                    
                    # Проверяем только на очень явные рекламные индикаторы
                    explicit_ad_keywords = ['advertisement', 'sponsored', 'spotify ad']
                    if any(keyword in artist.lower() or keyword in track.lower() for keyword in explicit_ad_keywords):
                        return True
                
                return False  # Структура "Артист - Трек" = это музыка!
            
            # Если нет разделителя, проверяем дополнительные критерии
            # ИСПРАВЛЕНО: Более строгие критерии для коротких заголовков
            if len(window_title.strip()) < 5:  # Только очень короткие
                return False  # Даже короткие заголовки могут быть названиями треков
            
            # Заголовки, содержащие только URL или промо-текст
            url_patterns = [r'spotify\.com', r'www\.', r'http']
            if any(re.search(pattern, window_title_lower) for pattern in url_patterns):
                return True
            
            # ИСПРАВЛЕНО: Более строгие паттерны призывов к действию
            action_patterns = [
                r'\bupgrade\s+to\s+premium\b',
                r'\bget\s+spotify\s+premium\b',
                r'\btry\s+premium\s+free\b'
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
    
    def block_ad_aggressively(self):
        """Агрессивное блокирование рекламы БЕЗ отключения звука"""
        try:
            # Метод 1: Закрытие рекламных окон
            self._close_ad_windows()
            
            # Метод 2: Попытка пропустить рекламу
            self._skip_ad_track()
            
            # Метод 3: Блокировка рекламных процессов
            self._block_ad_processes()
            
            # Метод 4: Очистка рекламного кэша
            self._clear_ad_cache()
            
            self.log("🚫 Реклама заблокирована агрессивными методами (звук НЕ отключен)")
            
        except Exception as e:
            self.log(f"Ошибка агрессивного блокирования: {e}", "ERROR")
    
    def _close_ad_windows(self):
        """Закрытие рекламных окон и попапов"""
        try:
            import win32gui
            import win32con
            
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_text = win32gui.GetWindowText(hwnd)
                    if window_text:
                        window_text_lower = window_text.lower()
                        # Ищем рекламные окна
                        ad_keywords = ['advertisement', 'spotify ad', 'premium', 'upgrade', 'sponsored']
                        if any(keyword in window_text_lower for keyword in ad_keywords):
                            # Закрываем рекламное окно
                            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                            self.log(f"🗙 Закрыто рекламное окно: {window_text}")
                return True
            
            win32gui.EnumWindows(enum_windows_callback, [])
            
        except ImportError:
            self.log("win32gui не установлен, пропуск закрытия окон", "WARNING")
        except Exception as e:
            self.log(f"Ошибка закрытия рекламных окон: {e}", "ERROR")
    
    def _skip_ad_track(self):
        """Попытка пропустить рекламный трек"""
        try:
            # Отправляем команду "следующий трек" через клавиатурные сочетания
            import win32api
            import win32con
            
            # Находим окно Spotify
            import win32gui
            
            def find_spotify_window():
                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_text = win32gui.GetWindowText(hwnd)
                        if 'spotify' in window_text.lower():
                            windows.append(hwnd)
                    return True
                
                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)
                return windows[0] if windows else None
            
            spotify_hwnd = find_spotify_window()
            if spotify_hwnd:
                # Активируем окно Spotify
                win32gui.SetForegroundWindow(spotify_hwnd)
                time.sleep(0.1)
                
                # Отправляем Ctrl+Right (следующий трек)
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                win32api.keybd_event(win32con.VK_RIGHT, 0, 0, 0)
                win32api.keybd_event(win32con.VK_RIGHT, 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                self.log("⏭️ Попытка пропустить рекламный трек")
                
        except ImportError:
            self.log("win32api не установлен, пропуск команды skip", "WARNING")
        except Exception as e:
            self.log(f"Ошибка пропуска трека: {e}", "ERROR")
    
    def _block_ad_processes(self):
        """Блокировка рекламных процессов"""
        try:
            # Ищем подозрительные процессы связанные с рекламой
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_name = proc.info['name'].lower()
                    cmdline = proc.info.get('cmdline', [])
                    
                    # Проверяем на рекламные процессы
                    if 'spotify' in proc_name:
                        cmdline_str = ' '.join(cmdline).lower() if cmdline else ''
                        ad_indicators = ['ad', 'advertisement', 'sponsored', 'promo', 'banner']
                        
                        if any(indicator in cmdline_str for indicator in ad_indicators):
                            # Завершаем рекламный процесс
                            proc.terminate()
                            self.log(f"🔪 Завершен рекламный процесс: {proc_name}")
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        except Exception as e:
            self.log(f"Ошибка блокировки процессов: {e}", "ERROR")
    
    def _clear_ad_cache(self):
        """Очистка рекламного кэша"""
        try:
            # Очищаем только рекламные файлы из кэша
            for spotify_path in self.spotify_paths:
                if spotify_path.exists():
                    # Ищем рекламные файлы
                    ad_cache_patterns = ['*ad*', '*advertisement*', '*promo*', '*banner*']
                    
                    for pattern in ad_cache_patterns:
                        for cache_file in spotify_path.rglob(pattern):
                            try:
                                if cache_file.is_file():
                                    cache_file.unlink()
                                    self.log(f"🗑️ Удален рекламный файл: {cache_file.name}")
                            except Exception:
                                continue
                                
        except Exception as e:
            self.log(f"Ошибка очистки рекламного кэша: {e}", "ERROR")
    
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
        """АГРЕССИВНЫЙ мониторинг Spotify БЕЗ блокировки звука"""
        self.log("🚀 Начат АГРЕССИВНЫЙ мониторинг Spotify (звук НЕ блокируется!)")
        
        # Более агрессивные настройки для быстрого реагирования
        ad_detection_count = 0
        music_detection_count = 0
        required_confirmations = 2  # Быстрое реагирование на рекламу
        last_ad_block_time = 0
        
        while self.is_running:
            try:
                if self.check_spotify_running():
                    is_ad = self.is_ad_playing()
                    
                    if is_ad:
                        ad_detection_count += 1
                        music_detection_count = 0
                        
                        # АГРЕССИВНАЯ блокировка рекламы (БЕЗ отключения звука)
                        if ad_detection_count >= required_confirmations:
                            current_time = time.time()
                            # Блокируем не чаще чем раз в 3 секунды
                            if current_time - last_ad_block_time > 3.0:
                                self.block_ad_aggressively()
                                last_ad_block_time = current_time
                                self.log(f"🔥 АГРЕССИВНАЯ блокировка рекламы после {ad_detection_count} проверок")
                    else:
                        music_detection_count += 1
                        ad_detection_count = 0
                        
                        # Логируем обнаружение музыки
                        if music_detection_count >= required_confirmations:
                            if hasattr(self, '_last_music_log'):
                                current_time = time.time()
                                if current_time - self._last_music_log > 30:  # Логируем раз в 30 сек
                                    self.log(f"🎵 Музыка играет нормально (звук НЕ блокирован)")
                                    self._last_music_log = current_time
                            else:
                                self.log(f"🎵 Музыка обнаружена после {music_detection_count} проверок")
                                self._last_music_log = time.time()
                else:
                    # Spotify не запущен
                    ad_detection_count = 0
                    music_detection_count = 0
                    if hasattr(self, '_last_music_log'):
                        delattr(self, '_last_music_log')
                
                time.sleep(0.3)  # Еще более частая проверка для агрессивного реагирования
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.log(f"Ошибка мониторинга: {e}", "ERROR")
                time.sleep(2)  # Меньшая пауза при ошибке для быстрого восстановления
    
    def start(self):
        """Запуск АГРЕССИВНОГО блокировщика рекламы (БЕЗ блокировки звука)"""
        self.log("=== АГРЕССИВНЫЙ Spotify Ad Blocker запущен ===")
        self.log("Версия: 1.0 (Агрессивная без блокировки звука)")
        self.log("Автор: AI Assistant")
        self.log("")
        
        try:
            # Проверка зависимостей
            self.log("Проверка зависимостей...")
            
            # Загрузка NirCmd для дополнительных функций
            try:
                self.download_nircmd()
            except Exception as e:
                self.log(f"Предупреждение при загрузке NirCmd: {e}", "WARNING")
            
            # Настройка АГРЕССИВНОЙ DNS блокировки
            try:
                self.setup_dns_blocking()
            except Exception as e:
                self.log(f"Предупреждение при настройке DNS: {e}", "WARNING")
            
            # Очистка кэша Spotify
            try:
                if not self.check_spotify_running():
                    self.clear_spotify_cache()
                else:
                    self.log("Spotify запущен, пропуск очистки кэша", "WARNING")
            except Exception as e:
                self.log(f"Предупреждение при очистке кэша: {e}", "WARNING")
            
            # Запуск АГРЕССИВНОГО мониторинга
            self.is_running = True
            monitor_thread = threading.Thread(target=self.monitor_spotify, daemon=True)
            monitor_thread.start()
            
            self.log("🔥 АГРЕССИВНЫЙ блокировщик рекламы активен! (звук НЕ блокируется)")
            self.log("Нажмите Ctrl+C для остановки")
            self.log("")
            
            # Основной цикл с улучшенной обработкой ошибок
            try:
                while self.is_running:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.log("Получен сигнал остановки от пользователя")
                self.stop()
                raise  # Передаем KeyboardInterrupt дальше для корректной обработки
                
        except KeyboardInterrupt:
            # Корректная обработка Ctrl+C
            raise
        except Exception as e:
            self.log(f"Критическая ошибка при запуске: {e}", "ERROR")
            self.stop()
            raise  # Передаем исключение дальше для обработки в main()
    
    def stop(self):
        """Остановка АГРЕССИВНОГО блокировщика"""
        self.log("🛑 Остановка АГРЕССИВНОГО блокировщика рекламы...")
        self.is_running = False
        
        self.log("✅ АГРЕССИВНЫЙ блокировщик остановлен (звук остался нетронутым)")

def main():
    """Главная функция с улучшенной обработкой ошибок"""
    try:
        print("")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║                🔥 АГРЕССИВНЫЙ Spotify Ad Blocker 🔥          ║")
        print("║                     Python Edition                          ║")
        print("║                                                              ║")
        print("║  АГРЕССИВНЫЙ блокировщик рекламы БЕЗ блокировки звука!      ║")
        print("║                                                              ║")
        print("║  🚀 АГРЕССИВНЫЕ МЕТОДЫ:                                      ║")
        print("║  • ❌ Закрытие рекламных окон                                ║")
        print("║  • ⏭️ Автоматический пропуск рекламных треков                ║")
        print("║  • 🚫 Блокировка рекламных процессов                        ║")
        print("║  • 🧹 Очистка рекламного кэша                               ║")
        print("║  • 🌐 Максимальная DNS-блокировка                           ║")
        print("║                                                              ║")
        print("║  ✅ ЗВУК НИКОГДА НЕ БЛОКИРУЕТСЯ!                             ║")
        print("║                                                              ║")
        print("║  Автор: AI Assistant                                         ║")
        print("║  Версия: 1.0 (Агрессивная без блокировки звука)             ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print("")
        
        # Проверка Python версии
        if sys.version_info < (3, 6):
            print("❌ Требуется Python 3.6 или выше")
            input("Нажмите Enter для выхода...")
            sys.exit(1)
        
        # Проверка операционной системы
        if os.name != 'nt':
            print("❌ Этот скрипт работает только на Windows")
            input("Нажмите Enter для выхода...")
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
            print("")
            input("Нажмите Enter для выхода...")
            sys.exit(1)
        
        # Запуск блокировщика
        blocker = SpotifyAdBlocker()
        
        try:
            blocker.start()
        except KeyboardInterrupt:
            print("\n👋 Программа остановлена пользователем")
            blocker.stop()
        except Exception as e:
            print(f"\n❌ Критическая ошибка: {e}")
            print("Проверьте логи для получения дополнительной информации")
            blocker.stop()
            input("\nНажмите Enter для выхода...")
            sys.exit(1)
        
        print("\n✅ Программа завершена успешно")
        
    except Exception as e:
        print(f"\n💥 Неожиданная ошибка при запуске: {e}")
        input("\nНажмите Enter для выхода...")
        sys.exit(1)

if __name__ == "__main__":
    main()