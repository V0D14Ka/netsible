#!/bin/bash

DIR="/etc/netsible"

if [ ! -d "$DIR" ]; then
  echo "Создание директории $DIR..."
  sudo mkdir -p "$DIR"
else
  echo "Директория $DIR уже существует."
fi

HOSTS_FILE="$DIR/hosts"
if [ ! -f "$HOSTS_FILE" ]; then
  echo "Создание файла hosts..."
  sudo touch "$HOSTS_FILE"
else
  echo "Файл hosts уже существует."
fi

CONFIG_FILE="$DIR/config"
if [ ! -f "$CONFIG_FILE" ]; then
  echo "Создание файла config..."
  sudo touch "$CONFIG_FILE"
else
  echo "Файл config уже существует."
fi

echo "Скрипт завершен."
