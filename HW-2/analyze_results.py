import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import gmean
import numpy as np

# Получаем абсолютный путь к директории, где лежит сам скрипт (HW-2)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ИСПРАВЛЕНО: пути к папкам теперь правильные
folders = {
    'Bimodal': os.path.join(BASE_DIR, 'results-bimodal'),
    'GAg': os.path.join(BASE_DIR, 'results-gag'),
    'PAp': os.path.join(BASE_DIR, 'results-pap'),
    'GAp': os.path.join(BASE_DIR, 'results-gap')
}

def parse_logs(folder_name, folder_path):
    data = []
    if not os.path.exists(folder_path):
        print(f"Предупреждение: Папка {folder_path} не найдена.")
        return data

    for filename in os.listdir(folder_path):
        if filename.endswith(".log"):
            with open(os.path.join(folder_path, filename), 'r') as f:
                content = f.read()

                ipc_match = re.search(r"CPU 0 cumulative IPC: ([\d\.]+)", content)
                mpki_match = re.search(r"MPKI: ([\d\.]+)", content)
                trace_match = re.search(r"runs .*/(\d+\.\w+)_s", content)

                if ipc_match and mpki_match and trace_match:
                    data.append({
                        'Trace': trace_match.group(1),
                        'Predictor': folder_name,
                        'IPC': float(ipc_match.group(1)),
                        'MPKI': float(mpki_match.group(1))
                    })
    return data

all_results = []
for name, path in folders.items():
    all_results.extend(parse_logs(name, path))

df = pd.DataFrame(all_results)

if df.empty:
    print("Данные не найдены. Проверь пути к папкам и содержимое логов.")
    exit()

summary = df.groupby('Predictor').agg({
    'IPC': lambda x: gmean(x[x > 0]),
    'MPKI': lambda x: gmean(x[x > 0])
}).reset_index()

print("\n--- Сводная таблица GMEAN ---")
print(summary.to_string(index=False))

csv_path = os.path.join(BASE_DIR, 'gmean_results.csv')
summary.to_csv(csv_path, index=False)

sns.set_theme(style="whitegrid")

plt.figure(figsize=(14, 6))
sns.barplot(data=df, x='Trace', y='IPC', hue='Predictor')
plt.title('Сравнение IPC по трассам (mispredict_penalty=12)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, 'ipc_comparison.png'))

plt.figure(figsize=(14, 6))
sns.barplot(data=df, x='Trace', y='MPKI', hue='Predictor')
plt.title('Сравнение MPKI по трассам (ниже - лучше)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, 'mpki_comparison.png'))

fig, ax1 = plt.subplots(figsize=(10, 6))
ax2 = ax1.twinx()

summary.plot(x='Predictor', y='IPC', kind='bar', ax=ax1, position=1, width=0.3, color='skyblue', label='GMEAN IPC')
summary.plot(x='Predictor', y='MPKI', kind='bar', ax=ax2, position=0, width=0.3, color='salmon', label='GMEAN MPKI')

ax1.set_ylabel('IPC')
ax2.set_ylabel('MPKI')
ax1.set_title('Итоговое сравнение (GMEAN)')
ax1.legend(loc='upper left')
ax2.legend(loc='upper right')
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, 'gmean_comparison.png'))

print(f"\nГрафики и CSV успешно сохранены в директорию: {BASE_DIR}")