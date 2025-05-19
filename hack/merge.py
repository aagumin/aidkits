import json
import os

# Читаем JSON файл
with open('ssh___git_sberworks_ru_7998_amazme_platform-docs_gitoutput.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Создаем директорию для результатов, если её еще нет
output_dir = 'output_by_title'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Группируем данные по title
grouped_data = {}
for item in data:
    if 'title' in item:
        title = item['title']
        # Используем title как ключ для группировки
        if title not in grouped_data:
            grouped_data[title] = []
        grouped_data[title].append(item)

# Сохраняем каждую группу в отдельный файл
for title, items in grouped_data.items():
    # Создаем безопасное имя файла (заменяем недопустимые символы)
    safe_filename = title.replace('/', '_').replace('\\', '_')
    if not safe_filename.endswith('.json'):
        safe_filename += '.json'

    output_path = os.path.join(output_dir, safe_filename)

    with open(output_path, 'w', encoding='utf-8') as out_file:
        json.dump(items, out_file, ensure_ascii=False, indent=4)

    print(f"Сохранен файл: {output_path} ({len(items)} записей)")

print(f"\nВсего создано {len(grouped_data)} файлов.")




