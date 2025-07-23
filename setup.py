#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Установочный скрипт для Spotify Ad Blocker

Этот скрипт автоматически настраивает окружение и устанавливает
все необходимые компоненты для работы блокировщика рекламы.
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
from pathlib import Path

class SpotifyAdBlockerSetup:
    """
    Класс для автоматической установки и настройки блокировщика
    """
    
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.config_dir = Path.home() / ".spotify_ad_blocker"
        self.requirements_file = self.project_dir / "requirements.txt"
        
    def print_step(self, message: str, step: int = None):
        """
        Вывод информации о текущем шаге
        """
        if step:
            print(f"\n[Шаг {step}] {message}")
        else:
            print(f"✅ {message}")
    
    def print_error(self, message: str):
        """
        Вывод ошибки
        """
        print(f"❌ Ошибка: {message}")
    
    def print_warning(self, message: str):
        """
        Вывод предупреждения
        """
        print(f"⚠️ Предупреждение: {message}")
    
    def check_python_version(self) -> bool:
        """
        Проверка версии Python
        """
        self.print_step("Проверка версии Python...", 1)
        
        if sys.version_info < (3, 6):
            self.print_error(f"Требуется Python 3.6 или выше. Текущая версия: {sys.version}")
            return False
        
        self.print_step(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} - OK")
        return True
    
    def install_dependencies(self) -> bool:
        """
        Установка зависимостей Python
        """
        self.print_step("Установка зависимостей Python...", 2)
        
        if not self.requirements_file.exists():
            self.print_error(f"Файл requirements.txt не найден: {self.requirements_file}")
            return False
        
        try:
            # Обновляем pip
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Устанавливаем зависимости
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)
            ])
            
            self.print_step("Зависимости успешно установлены")
            return True
            
        except subprocess.CalledProcessError as e:
            self.print_error(f"Не удалось установить зависимости: {e}")
            return False
    
    def create_config_directory(self) -> bool:
        """
        Создание конфигурационной папки
        """
        self.print_step("Создание конфигурационной папки...", 3)
        
        try:
            self.config_dir.mkdir(exist_ok=True)
            self.print_step(f"Конфигурационная папка создана: {self.config_dir}")
            return True
        except Exception as e:
            self.print_error(f"Не удалось создать конфигурационную папку: {e}")
            return False
    
    def download_nircmd(self) -> bool:
        """
        Загрузка утилиты NirCmd
        """
        self.print_step("Загрузка утилиты NirCmd...", 4)
        
        nircmd_path = self.config_dir / "nircmd.exe"
        
        if nircmd_path.exists():
            self.print_step("NirCmd уже установлен")
            return True
        
        try:
            # URL для загрузки NirCmd
            nircmd_url = "https://www.nirsoft.net/utils/nircmd.zip"
            zip_path = self.config_dir / "nircmd.zip"
            
            # Загружаем архив
            print("Загрузка NirCmd...")
            urllib.request.urlretrieve(nircmd_url, zip_path)
            
            # Извлекаем файлы
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Ищем nircmd.exe в архиве
                for file_info in zip_ref.filelist:
                    if file_info.filename.endswith('nircmd.exe'):
                        # Извлекаем только nircmd.exe
                        with zip_ref.open(file_info) as source:
                            with open(nircmd_path, 'wb') as target:
                                target.write(source.read())
                        break
            
            # Удаляем архив
            zip_path.unlink()
            
            if nircmd_path.exists():
                self.print_step("NirCmd успешно установлен")
                return True
            else:
                self.print_error("Не удалось извлечь nircmd.exe из архива")
                return False
                
        except Exception as e:
            self.print_error(f"Не удалось загрузить NirCmd: {e}")
            self.print_warning("NirCmd не обязателен, блокировщик может работать через PowerShell")
            return True  # Не критичная ошибка
    
    def create_user_hosts_file(self) -> bool:
        """
        Создание пользовательского hosts файла
        """
        self.print_step("Создание пользовательского hosts файла...", 5)
        
        hosts_file = self.config_dir / "user_hosts"
        
        if hosts_file.exists():
            self.print_step("Пользовательский hosts файл уже существует")
            return True
        
        # Список рекламных доменов Spotify
        ad_domains = [
            "# Spotify Ad Blocker - Рекламные домены",
            "# Создано автоматически установочным скриптом",
            "",
            "127.0.0.1 ads-fa.spotify.com",
            "127.0.0.1 adeventtracker.spotify.com",
            "127.0.0.1 analytics.spotify.com",
            "127.0.0.1 audio-ak-spotify-com.akamaized.net",
            "127.0.0.1 crashdump.spotify.com",
            "127.0.0.1 log.spotify.com",
            "127.0.0.1 longtail-dir.spotify.com",
            "127.0.0.1 spclient.wg.spotify.com",
            "127.0.0.1 audio-ak-spotify-com.akamaized.net",
            "127.0.0.1 heads-ak-spotify-com.akamaized.net",
            "127.0.0.1 audio4-ak-spotify-com.akamaized.net",
            "127.0.0.1 audio-akp-spotify-com.akamaized.net",
            "127.0.0.1 audio4-akp-spotify-com.akamaized.net",
            "127.0.0.1 heads4-ak-spotify-com.akamaized.net",
            "127.0.0.1 audio-ak.spotify.com.edgesuite.net",
            "127.0.0.1 audio4-ak.spotify.com.edgesuite.net",
            "127.0.0.1 heads-ak.spotify.com.edgesuite.net",
            "127.0.0.1 heads4-ak.spotify.com.edgesuite.net",
            "127.0.0.1 gew1.ap.spotify.com",
            "127.0.0.1 gew4.ap.spotify.com",
            "127.0.0.1 audio-sp-sto.spotify.com",
            "127.0.0.1 audio4-sp-sto.spotify.com",
            "127.0.0.1 heads-sp-sto.spotify.com",
            "127.0.0.1 heads4-sp-sto.spotify.com",
            "127.0.0.1 audio-sp-fra.spotify.com",
            "127.0.0.1 audio4-sp-fra.spotify.com",
            "127.0.0.1 heads-sp-fra.spotify.com",
            "127.0.0.1 heads4-sp-fra.spotify.com",
            "127.0.0.1 audio-sp-lon.spotify.com",
            "127.0.0.1 audio4-sp-lon.spotify.com",
            "127.0.0.1 heads-sp-lon.spotify.com",
            "127.0.0.1 heads4-sp-lon.spotify.com",
            "127.0.0.1 audio-sp-mia.spotify.com",
            "127.0.0.1 audio4-sp-mia.spotify.com",
            "127.0.0.1 heads-sp-mia.spotify.com",
            "127.0.0.1 heads4-sp-mia.spotify.com",
            "127.0.0.1 audio-sp-sjc.spotify.com",
            "127.0.0.1 audio4-sp-sjc.spotify.com",
            "127.0.0.1 heads-sp-sjc.spotify.com",
            "127.0.0.1 heads4-sp-sjc.spotify.com",
            "127.0.0.1 audio-sp-sea.spotify.com",
            "127.0.0.1 audio4-sp-sea.spotify.com",
            "127.0.0.1 heads-sp-sea.spotify.com",
            "127.0.0.1 heads4-sp-sea.spotify.com",
            "127.0.0.1 audio-sp-ash.spotify.com",
            "127.0.0.1 audio4-sp-ash.spotify.com",
            "127.0.0.1 heads-sp-ash.spotify.com",
            "127.0.0.1 heads4-sp-ash.spotify.com",
            "127.0.0.1 audio-sp-dfw.spotify.com",
            "127.0.0.1 audio4-sp-dfw.spotify.com",
            "127.0.0.1 heads-sp-dfw.spotify.com",
            "127.0.0.1 heads4-sp-dfw.spotify.com",
            "",
            "# Дополнительные рекламные домены",
            "127.0.0.1 googleads.g.doubleclick.net",
            "127.0.0.1 securepubads.g.doubleclick.net",
            "127.0.0.1 www.googletagservices.com",
            "127.0.0.1 gads.pubmatic.com",
            "127.0.0.1 ads.pubmatic.com",
            "127.0.0.1 tpc.googlesyndication.com",
            "127.0.0.1 pagead2.googlesyndication.com",
            "127.0.0.1 partner.googleadservices.com",
            "127.0.0.1 www.google-analytics.com",
            "127.0.0.1 ssl.google-analytics.com",
            "",
            "# Конец списка рекламных доменов"
        ]
        
        try:
            with open(hosts_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(ad_domains))
            
            self.print_step(f"Пользовательский hosts файл создан: {hosts_file}")
            return True
            
        except Exception as e:
            self.print_error(f"Не удалось создать hosts файл: {e}")
            return False
    
    def check_spotify_installation(self) -> bool:
        """
        Проверка установки Spotify
        """
        self.print_step("Проверка установки Spotify...", 6)
        
        # Проверяем наличие процессов Spotify
        try:
            import psutil
            spotify_processes = []
            for proc in psutil.process_iter(['name']):
                if 'spotify' in proc.info['name'].lower():
                    spotify_processes.append(proc.info['name'])
            
            if spotify_processes:
                self.print_step(f"Spotify запущен: {', '.join(set(spotify_processes))}")
                return True
        except ImportError:
            pass
        
        # Проверяем наличие исполняемых файлов
        common_paths = [
            Path.home() / "AppData/Roaming/Spotify/Spotify.exe",
            Path("C:/Program Files/Spotify/Spotify.exe"),
            Path("C:/Program Files (x86)/Spotify/Spotify.exe"),
        ]
        
        for path in common_paths:
            if path.exists():
                self.print_step(f"Spotify найден: {path}")
                return True
        
        # Проверяем версию из Microsoft Store
        ms_store_path = Path.home() / "AppData/Local/Packages"
        if ms_store_path.exists():
            for item in ms_store_path.iterdir():
                if "spotify" in item.name.lower():
                    self.print_warning("Обнаружена версия Spotify из Microsoft Store")
                    self.print_warning("Рекомендуется использовать официальную версию с spotify.com")
                    return True
        
        self.print_warning("Spotify не найден или не запущен")
        self.print_warning("Убедитесь, что Spotify установлен и запущен перед использованием блокировщика")
        return True  # Не критичная ошибка
    
    def create_desktop_shortcut(self) -> bool:
        """
        Создание ярлыка на рабочем столе
        """
        self.print_step("Создание ярлыка на рабочем столе...", 7)
        
        try:
            desktop = Path.home() / "Desktop"
            if not desktop.exists():
                desktop = Path.home() / "Рабочий стол"
            
            if not desktop.exists():
                self.print_warning("Папка рабочего стола не найдена")
                return True
            
            # Создаем batch файл для запуска
            shortcut_path = desktop / "Spotify Ad Blocker.bat"
            main_script = self.project_dir / "spotify_ad_blocker.py"
            
            batch_content = f'''@echo off
cd /d "{self.project_dir}"
python "{main_script}"
pause'''
            
            with open(shortcut_path, 'w', encoding='utf-8') as f:
                f.write(batch_content)
            
            self.print_step(f"Ярлык создан: {shortcut_path}")
            return True
            
        except Exception as e:
            self.print_error(f"Не удалось создать ярлык: {e}")
            return True  # Не критичная ошибка
    
    def run_setup(self) -> bool:
        """
        Запуск полной установки
        """
        print("🎵 Установка Spotify Ad Blocker")
        print("=" * 40)
        
        success = True
        
        # Выполняем все шаги установки
        steps = [
            self.check_python_version,
            self.install_dependencies,
            self.create_config_directory,
            self.download_nircmd,
            self.create_user_hosts_file,
            self.check_spotify_installation,
            self.create_desktop_shortcut
        ]
        
        for step in steps:
            if not step():
                success = False
                break
        
        print("\n" + "=" * 40)
        
        if success:
            self.print_step("🎉 Установка завершена успешно!")
            print("\n💡 Что дальше:")
            print("1. Запустите Spotify")
            print("2. Запустите блокировщик: python spotify_ad_blocker.py")
            print("3. Или используйте ярлык на рабочем столе")
            print("4. Для диагностики проблем: python diagnostic_tools.py")
            print("\n📖 Подробная документация в файле README.md")
        else:
            self.print_error("Установка завершена с ошибками")
            print("\n💡 Попробуйте:")
            print("1. Запустить установку от имени администратора")
            print("2. Проверить подключение к интернету")
            print("3. Установить зависимости вручную: pip install -r requirements.txt")
        
        return success

def main():
    """
    Главная функция установки
    """
    try:
        setup = SpotifyAdBlockerSetup()
        setup.run_setup()
    except KeyboardInterrupt:
        print("\n⏹️ Установка прервана пользователем")
    except Exception as e:
        print(f"❌ Критическая ошибка установки: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()