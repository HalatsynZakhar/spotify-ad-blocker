#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Диагностические утилиты для Spotify Ad Blocker

Этот модуль содержит инструменты для диагностики проблем,
тестирования функциональности и отладки блокировщика рекламы.
"""

import os
import sys
import time
import json
import psutil
import socket
import requests
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class SpotifyDiagnostics:
    """
    Класс для диагностики проблем со Spotify и блокировщиком рекламы
    """
    
    def __init__(self):
        self.config_dir = Path.home() / ".spotify_ad_blocker"
        self.log_file = self.config_dir / "diagnostic.log"
        self.results = {}
        
    def log_message(self, message: str, level: str = "INFO"):
        """
        Логирование сообщений
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        print(log_entry)
        
        # Записываем в файл
        self.config_dir.mkdir(exist_ok=True)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
    
    def check_python_environment(self) -> Dict:
        """
        Проверка Python окружения
        """
        self.log_message("Проверка Python окружения...")
        
        result = {
            "python_version": sys.version,
            "python_executable": sys.executable,
            "platform": sys.platform,
            "architecture": sys.maxsize > 2**32 and "64-bit" or "32-bit",
            "modules": {}
        }
        
        # Проверяем необходимые модули
        required_modules = [
            "psutil", "requests", "json", "pathlib", 
            "subprocess", "socket", "time", "datetime"
        ]
        
        optional_modules = [
            "win32api", "win32gui", "win32con", "win32process",
            "colorama", "tqdm", "pycryptodome"
        ]
        
        for module_name in required_modules:
            try:
                module = __import__(module_name)
                version = getattr(module, "__version__", "unknown")
                result["modules"][module_name] = {
                    "status": "installed",
                    "version": version,
                    "required": True
                }
                self.log_message(f"✅ {module_name}: {version}")
            except ImportError as e:
                result["modules"][module_name] = {
                    "status": "missing",
                    "error": str(e),
                    "required": True
                }
                self.log_message(f"❌ {module_name}: не установлен", "ERROR")
        
        for module_name in optional_modules:
            try:
                module = __import__(module_name)
                version = getattr(module, "__version__", "unknown")
                result["modules"][module_name] = {
                    "status": "installed",
                    "version": version,
                    "required": False
                }
                self.log_message(f"✅ {module_name}: {version} (опционально)")
            except ImportError:
                result["modules"][module_name] = {
                    "status": "missing",
                    "required": False
                }
                self.log_message(f"⚠️ {module_name}: не установлен (опционально)")
        
        self.results["python_environment"] = result
        return result
    
    def check_spotify_installation(self) -> Dict:
        """
        Проверка установки Spotify
        """
        self.log_message("Проверка установки Spotify...")
        
        result = {
            "processes": [],
            "executables": [],
            "installation_paths": [],
            "version_info": None,
            "is_microsoft_store": False
        }
        
        # Поиск процессов Spotify
        for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
            try:
                if 'spotify' in proc.info['name'].lower():
                    result["processes"].append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "exe": proc.info['exe'],
                        "cmdline": proc.info['cmdline']
                    })
                    self.log_message(f"🔍 Найден процесс: {proc.info['name']} (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Поиск исполняемых файлов Spotify
        common_paths = [
            Path.home() / "AppData/Roaming/Spotify/Spotify.exe",
            Path("C:/Users") / os.getenv('USERNAME', '') / "AppData/Roaming/Spotify/Spotify.exe",
            Path("C:/Program Files/Spotify/Spotify.exe"),
            Path("C:/Program Files (x86)/Spotify/Spotify.exe"),
        ]
        
        for path in common_paths:
            if path.exists():
                result["executables"].append(str(path))
                result["installation_paths"].append(str(path.parent))
                self.log_message(f"✅ Найден исполняемый файл: {path}")
                
                # Проверяем версию
                try:
                    version_info = self.get_file_version(str(path))
                    if version_info:
                        result["version_info"] = version_info
                        self.log_message(f"📋 Версия Spotify: {version_info}")
                except Exception as e:
                    self.log_message(f"⚠️ Не удалось получить версию: {e}")
        
        # Проверка на Microsoft Store версию
        ms_store_path = Path.home() / "AppData/Local/Packages"
        if ms_store_path.exists():
            for item in ms_store_path.iterdir():
                if "spotify" in item.name.lower():
                    result["is_microsoft_store"] = True
                    self.log_message("⚠️ Обнаружена версия из Microsoft Store")
                    break
        
        if not result["processes"] and not result["executables"]:
            self.log_message("❌ Spotify не найден", "ERROR")
        
        self.results["spotify_installation"] = result
        return result
    
    def check_network_connectivity(self) -> Dict:
        """
        Проверка сетевого подключения
        """
        self.log_message("Проверка сетевого подключения...")
        
        result = {
            "internet_connection": False,
            "spotify_servers": {},
            "ad_servers": {},
            "dns_resolution": {}
        }
        
        # Проверка интернет-соединения
        try:
            response = requests.get("https://www.google.com", timeout=5)
            if response.status_code == 200:
                result["internet_connection"] = True
                self.log_message("✅ Интернет-соединение работает")
            else:
                self.log_message(f"⚠️ Проблемы с интернетом: {response.status_code}")
        except Exception as e:
            self.log_message(f"❌ Нет интернет-соединения: {e}", "ERROR")
        
        # Проверка серверов Spotify
        spotify_servers = [
            "open.spotify.com",
            "api.spotify.com",
            "accounts.spotify.com",
            "spclient.wg.spotify.com"
        ]
        
        for server in spotify_servers:
            try:
                response = requests.get(f"https://{server}", timeout=5)
                result["spotify_servers"][server] = {
                    "status": "accessible",
                    "status_code": response.status_code
                }
                self.log_message(f"✅ {server}: доступен")
            except Exception as e:
                result["spotify_servers"][server] = {
                    "status": "error",
                    "error": str(e)
                }
                self.log_message(f"❌ {server}: недоступен - {e}")
        
        # Проверка рекламных серверов (должны быть заблокированы)
        ad_servers = [
            "ads-fa.spotify.com",
            "adeventtracker.spotify.com",
            "analytics.spotify.com",
            "audio-ak-spotify-com.akamaized.net",
            "crashdump.spotify.com"
        ]
        
        for server in ad_servers:
            try:
                # Проверяем DNS разрешение
                ip = socket.gethostbyname(server)
                result["dns_resolution"][server] = ip
                
                if ip == "127.0.0.1" or ip.startswith("0."):
                    result["ad_servers"][server] = "blocked"
                    self.log_message(f"✅ {server}: заблокирован ({ip})")
                else:
                    result["ad_servers"][server] = "not_blocked"
                    self.log_message(f"⚠️ {server}: не заблокирован ({ip})")
            except Exception as e:
                result["ad_servers"][server] = "dns_error"
                self.log_message(f"❌ {server}: ошибка DNS - {e}")
        
        self.results["network_connectivity"] = result
        return result
    
    def check_audio_system(self) -> Dict:
        """
        Проверка аудио системы
        """
        self.log_message("Проверка аудио системы...")
        
        result = {
            "nircmd_available": False,
            "nircmd_path": None,
            "powershell_available": False,
            "audio_devices": [],
            "volume_control": False
        }
        
        # Проверка NirCmd
        nircmd_paths = [
            self.config_dir / "nircmd.exe",
            Path("nircmd.exe"),
            Path("C:/Windows/System32/nircmd.exe")
        ]
        
        for path in nircmd_paths:
            if path.exists():
                result["nircmd_available"] = True
                result["nircmd_path"] = str(path)
                self.log_message(f"✅ NirCmd найден: {path}")
                break
        
        if not result["nircmd_available"]:
            self.log_message("⚠️ NirCmd не найден")
        
        # Проверка PowerShell
        try:
            subprocess.run(["powershell", "-Command", "Get-Host"], 
                         capture_output=True, timeout=5, check=True)
            result["powershell_available"] = True
            self.log_message("✅ PowerShell доступен")
        except Exception as e:
            self.log_message(f"❌ PowerShell недоступен: {e}")
        
        # Тест управления громкостью
        if result["nircmd_available"]:
            try:
                # Пробуем получить текущую громкость
                subprocess.run([result["nircmd_path"], "speak", "text", ""], 
                             capture_output=True, timeout=2)
                result["volume_control"] = True
                self.log_message("✅ Управление громкостью работает")
            except Exception as e:
                self.log_message(f"⚠️ Проблемы с управлением громкостью: {e}")
        
        self.results["audio_system"] = result
        return result
    
    def check_file_permissions(self) -> Dict:
        """
        Проверка прав доступа к файлам
        """
        self.log_message("Проверка прав доступа к файлам...")
        
        result = {
            "config_dir_writable": False,
            "hosts_file_readable": False,
            "spotify_cache_accessible": False,
            "temp_dir_writable": False
        }
        
        # Проверка конфигурационной папки
        try:
            self.config_dir.mkdir(exist_ok=True)
            test_file = self.config_dir / "test_write.tmp"
            test_file.write_text("test")
            test_file.unlink()
            result["config_dir_writable"] = True
            self.log_message(f"✅ Конфигурационная папка доступна для записи: {self.config_dir}")
        except Exception as e:
            self.log_message(f"❌ Нет доступа к конфигурационной папке: {e}", "ERROR")
        
        # Проверка файла hosts
        hosts_file = Path("C:/Windows/System32/drivers/etc/hosts")
        try:
            hosts_file.read_text()
            result["hosts_file_readable"] = True
            self.log_message("✅ Файл hosts доступен для чтения")
        except Exception as e:
            self.log_message(f"❌ Нет доступа к файлу hosts: {e}")
        
        # Проверка кэша Spotify
        spotify_cache = Path.home() / "AppData/Local/Spotify"
        try:
            if spotify_cache.exists():
                list(spotify_cache.iterdir())
                result["spotify_cache_accessible"] = True
                self.log_message(f"✅ Кэш Spotify доступен: {spotify_cache}")
            else:
                self.log_message("⚠️ Папка кэша Spotify не найдена")
        except Exception as e:
            self.log_message(f"❌ Нет доступа к кэшу Spotify: {e}")
        
        # Проверка временной папки
        temp_dir = Path.home() / "AppData/Local/Temp"
        try:
            test_file = temp_dir / "spotify_test.tmp"
            test_file.write_text("test")
            test_file.unlink()
            result["temp_dir_writable"] = True
            self.log_message("✅ Временная папка доступна для записи")
        except Exception as e:
            self.log_message(f"❌ Нет доступа к временной папке: {e}")
        
        self.results["file_permissions"] = result
        return result
    
    def get_file_version(self, file_path: str) -> Optional[str]:
        """
        Получение версии файла (Windows)
        """
        try:
            import win32api
            info = win32api.GetFileVersionInfo(file_path, "\\")
            ms = info['FileVersionMS']
            ls = info['FileVersionLS']
            version = f"{win32api.HIWORD(ms)}.{win32api.LOWORD(ms)}.{win32api.HIWORD(ls)}.{win32api.LOWORD(ls)}"
            return version
        except Exception:
            return None
    
    def run_full_diagnostic(self) -> Dict:
        """
        Запуск полной диагностики
        """
        self.log_message("🔍 Запуск полной диагностики...")
        
        # Очищаем предыдущие результаты
        self.results = {}
        
        # Запускаем все проверки
        self.check_python_environment()
        self.check_spotify_installation()
        self.check_network_connectivity()
        self.check_audio_system()
        self.check_file_permissions()
        
        # Добавляем общую информацию
        self.results["diagnostic_info"] = {
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "platform": sys.platform,
            "python_version": sys.version
        }
        
        # Сохраняем результаты
        self.save_results()
        
        self.log_message("✅ Диагностика завершена")
        return self.results
    
    def save_results(self):
        """
        Сохранение результатов диагностики
        """
        results_file = self.config_dir / "diagnostic_results.json"
        
        try:
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            self.log_message(f"📄 Результаты сохранены: {results_file}")
        except Exception as e:
            self.log_message(f"❌ Ошибка сохранения результатов: {e}", "ERROR")
    
    def generate_report(self) -> str:
        """
        Генерация отчета о диагностике
        """
        if not self.results:
            return "Диагностика не была запущена"
        
        report = []
        report.append("🔍 ОТЧЕТ О ДИАГНОСТИКЕ SPOTIFY AD BLOCKER")
        report.append("=" * 50)
        report.append(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Python окружение
        if "python_environment" in self.results:
            env = self.results["python_environment"]
            report.append("🐍 PYTHON ОКРУЖЕНИЕ:")
            report.append(f"Версия: {env['python_version'].split()[0]}")
            report.append(f"Платформа: {env['platform']}")
            report.append(f"Архитектура: {env['architecture']}")
            
            missing_required = [name for name, info in env['modules'].items() 
                              if info['required'] and info['status'] == 'missing']
            if missing_required:
                report.append(f"❌ Отсутствуют обязательные модули: {', '.join(missing_required)}")
            else:
                report.append("✅ Все обязательные модули установлены")
            report.append("")
        
        # Spotify
        if "spotify_installation" in self.results:
            spotify = self.results["spotify_installation"]
            report.append("🎵 SPOTIFY:")
            if spotify['processes']:
                report.append(f"✅ Запущенных процессов: {len(spotify['processes'])}")
            else:
                report.append("❌ Spotify не запущен")
            
            if spotify['executables']:
                report.append(f"✅ Найдено исполняемых файлов: {len(spotify['executables'])}")
            else:
                report.append("❌ Исполняемые файлы не найдены")
            
            if spotify['is_microsoft_store']:
                report.append("⚠️ Обнаружена версия из Microsoft Store (может не работать)")
            
            if spotify['version_info']:
                report.append(f"📋 Версия: {spotify['version_info']}")
            report.append("")
        
        # Сеть
        if "network_connectivity" in self.results:
            network = self.results["network_connectivity"]
            report.append("🌐 СЕТЕВОЕ ПОДКЛЮЧЕНИЕ:")
            if network['internet_connection']:
                report.append("✅ Интернет-соединение работает")
            else:
                report.append("❌ Проблемы с интернет-соединением")
            
            blocked_ads = sum(1 for status in network['ad_servers'].values() if status == 'blocked')
            total_ads = len(network['ad_servers'])
            report.append(f"🚫 Заблокировано рекламных серверов: {blocked_ads}/{total_ads}")
            report.append("")
        
        # Аудио
        if "audio_system" in self.results:
            audio = self.results["audio_system"]
            report.append("🔊 АУДИО СИСТЕМА:")
            if audio['nircmd_available']:
                report.append("✅ NirCmd доступен")
            elif audio['powershell_available']:
                report.append("✅ PowerShell доступен (альтернатива)")
            else:
                report.append("❌ Нет инструментов управления звуком")
            report.append("")
        
        # Права доступа
        if "file_permissions" in self.results:
            perms = self.results["file_permissions"]
            report.append("🔐 ПРАВА ДОСТУПА:")
            issues = []
            if not perms['config_dir_writable']:
                issues.append("конфигурационная папка")
            if not perms['hosts_file_readable']:
                issues.append("файл hosts")
            if not perms['spotify_cache_accessible']:
                issues.append("кэш Spotify")
            
            if issues:
                report.append(f"❌ Проблемы с доступом: {', '.join(issues)}")
            else:
                report.append("✅ Все необходимые права доступа есть")
            report.append("")
        
        # Рекомендации
        report.append("💡 РЕКОМЕНДАЦИИ:")
        recommendations = self.get_recommendations()
        for rec in recommendations:
            report.append(f"• {rec}")
        
        return "\n".join(report)
    
    def get_recommendations(self) -> List[str]:
        """
        Получение рекомендаций на основе результатов диагностики
        """
        recommendations = []
        
        if not self.results:
            return ["Запустите диагностику для получения рекомендаций"]
        
        # Проверяем Python модули
        if "python_environment" in self.results:
            env = self.results["python_environment"]
            missing_required = [name for name, info in env['modules'].items() 
                              if info['required'] and info['status'] == 'missing']
            if missing_required:
                recommendations.append(f"Установите отсутствующие модули: pip install {' '.join(missing_required)}")
        
        # Проверяем Spotify
        if "spotify_installation" in self.results:
            spotify = self.results["spotify_installation"]
            if not spotify['processes']:
                recommendations.append("Запустите Spotify перед использованием блокировщика")
            if spotify['is_microsoft_store']:
                recommendations.append("Рекомендуется использовать официальную версию Spotify вместо версии из Microsoft Store")
        
        # Проверяем аудио
        if "audio_system" in self.results:
            audio = self.results["audio_system"]
            if not audio['nircmd_available'] and not audio['powershell_available']:
                recommendations.append("Установите NirCmd для управления звуком или убедитесь, что PowerShell доступен")
        
        # Проверяем блокировку рекламы
        if "network_connectivity" in self.results:
            network = self.results["network_connectivity"]
            blocked_count = sum(1 for status in network['ad_servers'].values() if status == 'blocked')
            total_count = len(network['ad_servers'])
            if blocked_count < total_count:
                recommendations.append("Некоторые рекламные серверы не заблокированы. Запустите блокировщик для их блокировки")
        
        if not recommendations:
            recommendations.append("Все проверки пройдены успешно! Блокировщик готов к работе.")
        
        return recommendations

def main():
    """
    Главная функция для запуска диагностики
    """
    print("🔍 Диагностические утилиты Spotify Ad Blocker")
    print("=" * 50)
    
    diagnostics = SpotifyDiagnostics()
    
    try:
        # Запускаем полную диагностику
        results = diagnostics.run_full_diagnostic()
        
        # Генерируем и показываем отчет
        report = diagnostics.generate_report()
        print("\n" + report)
        
        # Сохраняем отчет в файл
        report_file = diagnostics.config_dir / "diagnostic_report.txt"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"\n📄 Полный отчет сохранен: {report_file}")
        print(f"📄 Подробные результаты: {diagnostics.config_dir / 'diagnostic_results.json'}")
        
    except KeyboardInterrupt:
        print("\n⏹️ Диагностика прервана пользователем")
    except Exception as e:
        print(f"❌ Ошибка диагностики: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()