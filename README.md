# Веб-приложение для прогнозирования цен недвижимости на данных ЦИАН

Учебный проект для демонстрации основных этапов жизненного цикла проекта предиктивной аналитики.  

## Installation 

Клонируйте репозиторий, создайте виртуальное окружение, активируйте и установите зависимости:  

```sh
git clone https://github.com/makimka022/pabd24
cd pabd24
python3 -m venv venv

source venv/bin/activate  # mac or linux
.\venv\Scripts\activate   # windows

pip install -r requirements.txt
```

## Usage

### 1. Сбор данных о ценах на недвижимость 
```sh
python src/parse_cian.py 
```  
Параметры для парсинга можно изменить в скрипте.   

### 2. Выгрузка данных в хранилище S3 
Для доступа к хранилищу скопируйте файл `.env` в корень проекта.  

```sh
python src/upload_to_s3.py -i data/raw/file.csv 
```  
i - аргумент, который мы используем в функции. В этом примере мы указываем путь к файлу нашей функции.

### 3. Загрузка данных из S3 на локальную машину  
```sh
python src/download_from_s3.py 
``` 
Скрипт для загрузки данных с S3 в локальный репозиторий.

### 4. Предварительная обработка данных  
```sh
python src/preprocess_data.py 
``` 
Данный скрипт осуществляет препроцессинг данных для обучения парной линейной регрессии.

### 5. Обучение модели 
```sh
python src/train_model.py 
```   
В качестве входных данных для парной линейной регрессии используется площадь квартиры `area`.   
Модель возвращает цену недвижимости `price`.

Протестировать модель можно с помощью скрипта
```sh
python src/test_model.py 
``` 

Логи обучения и валидации модели появятся в папке `log`.

### 6. Запуск приложения flask 

Для запуска приложения на dev-сервер используй 
```sh
python src/predict_app.py 
``` 
Юнит-тест для проверки работоспособности проводить с помощью
```sh
python test/test_api.py 
``` 
или 
```sh
python test/test_parallel.py 
``` 
если хотим проверить нагрузку при нескольких параллельных запросах.

#### Запуск приложения на prod (gunicorn)
```bash
gunicorn -b 0.0.0.0 src.predict_app:app --daemon 
```
Адрес задеплоенного приложения http://192.144.14.8:8000/predict

### 7. Использование сервиса через веб интерфейс 

Для использования сервиса используйте файл `web/index.html`.

### 8. Запуск через docker

Для запуска приложения используйте docker:

```bash
docker run -p 8000:8000 makimka022/pabd24:latest
```
