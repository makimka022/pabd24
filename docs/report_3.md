# Отчет по семинару № 3
Исследование поведения серверов flask и gunicorn под разными видами нагрузки.  

### Введение
Для тяжелых моделей предиктивной аналитики возможно два варианта деплоя. 
Первый вариант - запускать модели на своем сервере. 
Этот вариант имеет очевидный недостаток. 
Если у вас очень тяжелая модель, то пользователи вашего сервиса должны будут долго ждать ответа.  
Даже самый мощный компьютер имеет предел вычислительной мощности. 
Поэтому если вашим сервисом будут пользоваться несколько пользователей одновременно, придется настраивать собственный вычислительный кластер. 

Второй вариант - использовать специальные сервисы, например:  
- TensorFlow Serving
- AWS SageMaker
- Yandex DataSphere
- Google Vertex AI

В этом случае вычислительная нагрузка снимается с вашего сервера. 
Но за каждый запрос к стороннему сервису нужно платить, как деньги, так и временем на обработку запросов. 

### Метод исследования
В файле `src/utils.py` определены три функции, которые эмулируют три варианта решения задачи `predict` :
- `predict_io_bounded(area)` - соответсвует второму варианту, запрос к стороннему сервису заменяет `time.sleep(1)`. 
Это соответствует задержке в 1 секунду, которая нужна для обмена информацией со сторонним сервисом. 
При этом вычислительная нагрузка на наш сервер не создается, процесс просто спит. 
- `predict_cpu_bounded(area, n)` - соответствует первому варианту, предикту на собственном сервере. 
Параметр `n` позволяет регулировать нагрузку, на самом деле это просто вычисление среднего арифметического линейного массива. 
При достаточно больших `n` сервер будет выдавать ошибку из-за нехватки памяти. 
Необходимо эмпирическим путем определить это значение. 
- `predict_cpu_multithread(area, n)` - тоже соответствует первому варианту, но используется оптимизированный код на numpy. 
Необходимо также эмпирическим путем определить критическое значение `n` и сравнить его с предыдущим. 

Для запуска сервиса доступно два варианта: 
- `python src/predict_app.py` - сервер, предназначенный для разработки. 
- `gunicorn src.predict_app:app` - сервер, предназначенный для непрерывной работы в продакшн. 

Нагрузка создается файлом `test/test_parallel.py`.  

**Задача**: запустить 6 (шесть) возможных вариантов сочетаний серверов и функций под нагрузкой в 10 запросов. 

Результат запуска должен быть сохранен в логи, например с помощью перенаправления вывода:  
`py test/test_parallel.py > log/test_np_flask.txt 2>&1` 
Обратите внимание, файлы должны иметь расширение txt, а значит не игнорятся гитом и должны быть запушены в мастере.  

### Результат и обсуждение

1) При запуске `predict_io_bounded` на `dev-сервере flask` получен [результат](https://github.com/makimka022/pabd24/tree/master/log/test_dev_task_1.txt). 
Все запросы обрабатываются одновременно, в среднем за 1.05 секунды. При такой нагрузке (10 запросов с задержкой)  данный сервер имет стабильную и даже эффективную работу, но при возрастании нагрузки может быть сбой, потому что вся нагрузка поступает одновременно и никак не распределяется, что нормально для сервера разработки, где работет 1 клиент, но не подходит для промышленной среды, где одновременно может поступать огромное количество запросов.

2) При запуске `predict_io_bounded` на `prod-сервере gunicorn` получен [результат](https://github.com/makimka022/pabd24/tree/master/log/test_prod_task_1.txt).
В отличие от запросов на dev-сервере, здесь существует приоритизация запросов, исходя из нагрузки (образуется очередь запросов) - последний запрос обрабатывается 9 секунд. Такой сценарий работы действительно предпочтителен для промышленного сервера, потому что мы можем быть почти наверняка уверены в его большей стабильности и более грамотной работе с ресурсами.

3) При запуске `predict_cpu_bounded` (расчет среднего из n первых целых чисел) на `dev-сервере flask` здесь и в дальнейших тестах были выбраны следующие переменные n in [1M, 5M, 25M]. Видно, что такое низкопроизводительное решение (стандартными функциями Python) сильно нагружает как процессор, так и память. В результате [тест c 25M чисел](https://github.com/makimka022/pabd24/tree/master/log/test_dev_task_2_25M.txt) даже не прошел тест, упав с ошибкой, израсходовав все предоставленные виртуальной машиной вычислительные мощности. [Тест с 1М чисел](https://github.com/makimka022/pabd24/tree/master/log/test_dev_task_2_1M.txt) и [тест с 5М чисел](https://github.com/makimka022/pabd24/tree/master/log/test_dev_task_2_5M.txt) были успешно пройдены. Нагрузка опять же распределяется точечным образом на один процесс, однако все 10 запросов теперь не занимают одинаковое количество времени. Так же видно, что среднее время выполнение команд увеличилось в 5 раз при росте n в 5 раз, то есть пропорционально сложности задачи.

4) При запуске `predict_cpu_bounded` на `prod-сервере gunicorn` в отличие от dev-сервера удается запустить [тест с 25М чисел](https://github.com/makimka022/pabd24/tree/master/log/test_prod_task_2_25M.txt), что неудивительно, так как запросы опять же идут в порядке многопоточности, что не дает сразу ударную нагрузку на CPU и RAM, а подает ее более грамотно, учитывая имеющие мощности. Этот же эффект дает преимущество prod-серверу во времени прохождения тестов [с 1М чисел](https://github.com/makimka022/pabd24/tree/master/log/test_prod_task_2_1M.txt) и [с 5М чисел](https://github.com/makimka022/pabd24/tree/master/log/test_prod_task_2_5M.txt), так как не все 10 пользователей ждут по максимально-возможному времени, а только последний. При этом было найдено число, после которого сервер упал с ошибкой. Оно оказалось в 4 раза больше, чем в случае `dev-сервера flask`, а именно [100M](https://github.com/makimka022/pabd24/tree/master/log/test_prod_task_2_100M.txt), что опять же демонстрирует более грамотную работу с ресурсами на промышленном сервере и его возможность справится с кратно превосходящими нагрузками.

5) При запуске `predict_cpu_multithread` на `dev-сервере flask` все вычисления ([на 1 М](https://github.com/makimka022/pabd24/tree/master/log/test_dev_task_3_1M.txt), [на 5 М](https://github.com/makimka022/pabd24/tree/master/log/test_dev_task_3_5M.txt) и [на 25М](https://github.com/makimka022/pabd24/tree/master/log/test_dev_task_3_25M.txt)) значительно ускоряются (в 10-20 раз) из-за использования библиотки numpy при вычислении среднего, которая использует более продвинутые и высокопроизводительные решения. Это же и позволяет серверу прирасти в стабильности, потому что теперь ничего не падает из-за перегрузки ВМ. Эмпирически было найдено значение, после которого сервер перестал отвечать - [200M](https://github.com/makimka022/pabd24/tree/master/log/test_dev_task_3_200M.txt).

6) При запуске `predict_cpu_multithread` на `prod-сервере gunicorn` на [первом тесте с 1М](https://github.com/makimka022/pabd24/tree/master/log/test_prod_task_3_1M.txt) не видно различий с dev-сервером по скорости обработки запросов (так как обработка запросов происходит настолько быстро, что "очередь не успевает образоваться"). Но не следующих тестах ([5M](https://github.com/makimka022/pabd24/tree/master/log/test_prod_task_3_5M.txt), [25M](https://github.com/makimka022/pabd24/tree/master/log/test_prod_task_3_25M.txt)) уже видна разница из-за роста нагрузки, где также, как и в предыдущих тестах, промышленный сервер показывает более грамотную работу в потоками и ресурсами. Сервер опять пережил в 4 раза большую нагрузку, чем `dev-сервер` и упал при нагрузке более [800M](https://github.com/makimka022/pabd24/tree/master/log/test_prod_task_3_800M.txt).

После проведения всех тестов можно сделать следующие выводы:
* `dev-сервер flask` хорошо подходит для разработки, потому что более производителен для работы с 1 клиентом, так как запросы на сервере обрабатываются на одном процессе, но при возрастании нагрузки это приводит к быстрой утилизации имеющихся ресурсов ВМ;
* `prod-сервер gunicorn` хорошо подходит для промышленной среды, потому что более стабилен при работе с высоконагруженным сервисом из-за грамотной работы с ресурсами ВМ, многопоточности, приоритезации запросов (выстраивании "очереди"), что очень важно, когда клиентов, одновременно делающих запросы на сервер, множество;
* было продемонстрировано, что использование более оптимизированных и высокопроизводительных библиотек и кода в принципе может приводить к ускорению общей производительности в несколько десятков раз;
* эмпирически было выявлено, что `prod-сервер gunicorn` может справляться с нагрузкой, в 4 раза превосходящую нагрузку на `dev-сервер flask`.