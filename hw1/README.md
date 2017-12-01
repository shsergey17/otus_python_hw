# Запуск с default конф файлом
python log_analyzer.py

# Запуск с указанием конфиг файла        
python log_analyzer.py --config=config.cfg

# Тесты        
python -m unittest discover -p test_log_analyzer.py
