# Запуск с default конф файлом
python log_analyzer.py

# Запуск с указанием конфиг файла        
python log_analyzer.py --config=config.cfg
# Запуск с указанием вывода лога в файл
python log_analyzer.py --logfile=/var/log/logfile.log

# Тесты        
python -m unittest discover -p test_log_analyzer.py
