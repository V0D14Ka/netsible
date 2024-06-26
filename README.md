# Система управления конфигурациями сетевого оборудования

## Содержание

- [Установка](#установка)
- [netsible cli](#использование)
- [Доступные методы](#методы)
- [netsible-task cli](#использование_задач)
- [Доступные модули](#модули)
- [Доступные ОС](#ос)
- [Примеры](#примеры)

## Установка CLI<a name="установка"></a>

```bash
git clone https://github.com/V0D14Ka/netsible.git
cd netsible
pip3 install .
```

## netsible cli <a name="использование"></a>

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

## Доступные методы <a name="методы"></a>
1) **cisco_ios & router_os**
     - **int** - список интерфейсов;
     - **vlan** - список vlan;
     - **route** - список маршрутов;
     - **lldp** - список lldp соседей;
     - **config** - запущенный конфиг.
2) **linux**
     - **int** - список интерфейсов;
     - **uptime** - время работы и средняя загрузка.
## netsible-task cli <a name="использование_задач"></a>

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

## Доступные модули <a name="модули"></a>
1) **updateint** - модуль позволяет конфигурировать интерфейс, список доступный параметров:<br>
    - **interface_name** - название интерфейса;
    - **description** - описание;
    - **ip_address** - адрес, который будет назначен;
    - **subnet_mask** - маска сети;
    - **mtu** - mtu;
    - **speed** - скорость;
    - **duplex** - duplex;
    - **bandwidth** - 
    - **encapsulation** - метод инкапсуляции в L2;
    - **authentication** - 
    - **switchport_mode** - режим интерфейса;
    - **trunk_allowed_vlans** - vlans, допущенные к trunk;
    - **shutdown** - включение/ выключение интерфейса;
    - **write** - сохранение изменений;
2) **ospf** - модуль позволяет настраивать ospf, список доступный параметров:<br>
    - **process** - номер запущенного процесса ospf;
    - **networks** - список сетей для анонсирования;
      - **ip** - адрес сети;
      - **subnet_mask** - маска сети;
      - **area** - зона ospf;
    - **auth** - авторизация соседей;
      - **int** - интерфейс, на котором будет пароль;
      - **pass** - пароль.
3) **bgp** - модуль позволяет настраивать bgp, список доступный параметров:<br>
    - **as**
    - **networks** - список сетей для анонсирования;
      - **ip** - адрес сети;
      - **subnet_mask** - маска сети;
    - **neighbors** - список bgp соседей;
      - **ip** - адрес соседа;
      - **name** - имя соседа;
      - **as** - автономная система соседа;
      - **hext_hop_self** - анонсирование gateway;
      - **route_reflector** 

## Доступные ОС <a name="ос"></a>
1) **сisco_ios**
2) **mikrotik_routeros**
3) **linux**

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
