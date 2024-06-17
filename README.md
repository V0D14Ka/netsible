# Система управления конфигурациями сетевого оборудования

## Содержание

- [Установка](#установка)
- [Разовое использование](#использование)
- [Использование задач](#использование_задач)
- [Примеры](#примеры)

## Установка CLI<a name="установка"></a>

```bash
git clone https://github.com/V0D14Ka/netsible.git
cd netsible
pip3 install .
```

## Разовое использование <a name="использование"></a>

Проверим корректность установки:
```bash
netsible -v
```
Этот шаг важен, поскольку во время первого запуска создается директория **~/.netsible.** <br>
Теперь необходимо создать файл **hosts** в созданной автоматически на прошлом шаге директории **~/.netsible/**. 
Вы так же можете использовать свою директорию для конфигурационных файлов:

Заполните **hosts** как показано в **hosts_example** и запустите программу.

```bash
netsible <target> -m <method> 
```
Или
```bash
netsible <target> -m <method> -i <path_to_custom_dir>
```
Где:
 - ``target`` - имя хоста для выполнения команды.
 - ``method`` - метод/команда для выполнения на хосте.
 - ``path_to_custom_dir`` - путь до пользовательской директории с конфигурационными файлами netsible.

## Использование задач <a name="использование_задач"></a>

Создайте файл в директории **~/.netsible** в формате **.yaml** с задачами, как показано в
**task_example.yaml**. 

Чтобы запустить выполнение задач используйте следующую команду: 

```bash
netsible-task -t <task_file.yaml> 
```

Чтобы использовать пользовательскую директорию используйте следующую команду:
```bash
netsible-task -t <task_file.yaml> -p <path_to_custom_dir>
```

Где:
 - ``task_file.yaml`` - файл с описанием задач и хостов.
 - ``path_to_custom_dir`` - путь до пользовательской директории с конфигурационными файлами netsible.

## Примеры <a name="примеры"></a>
### netsible 
- **ping**<br>
  *input:*
  ```bash
  netsible <target> -m ping
  ```
  *output:*
  ```
  SUCCESS: 1718620994.87460:
  Ping successful. Round-trip time: 0.0010001659393310547 ms
  ```

- **uptime** <br>
  *input:*
  ```bash
  netsible <target> -m uptime
  ```
  *output:*
  ```
  SUCCESS: 1718620988.32537: 

  10:43:09 up 16 days,  1:55,  1 user,  load average: 0,94, 0,87, 0,84
  ```

### netsible-task
- **some tasks SUCCESS** <br>
  Запуск корректно настроенного файла с задачами.<br>
  *input:*
  ```bash
  netsible-task -t <task_file.yaml>
  ```
  *output:*
  ```
  LOG: 110428 1718621745.63506: C:\Users\Admin\.netsible\bib.yaml is valid YAML.
  LOG: 110428 1718621745.63649: Running task 'Aboba' using module 'updateint' with params {'int': 'None', 'cmd': 'nameserver 10.1.250.12'}
  LOG: 110428 1718621745.63649: Running task 'Abiba' using module 'updateint' with params {'int': 'None', 'cmd': 'nameserver 10.1.250.10'}
  
  SUCCESS
  ```
- **some tasks ERROR** <br>
  Запуск файла с ошибкой module. <br>
  *input:*
  ```bash
  netsible-task -t <task_file.yaml>
  ```
  *output:*
  ```
  LOG: 106264 1718621886.35859: C:\Users\Admin\.netsible\bib.yaml is valid YAML.
  ERROR: 106264 1718621886.36011: Module 'updadteint' is not in the list of available modules.
  ```
  
  Запуск файла с ошибкой param. <br>
  *input:*
  ```bash
  netsible-task -t <task_file.yaml>
  ```
  *output:*
  ```
  LOG: 112416 1718622072.60345: C:\Users\Admin\.netsible\bib.yaml is valid YAML.
  ERROR: 112416 1718622072.60445: Incorrect param - 'intd' in module - 'updateint'.
  ```
