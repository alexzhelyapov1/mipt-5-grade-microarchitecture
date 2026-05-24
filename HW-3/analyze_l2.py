import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import gmean
import numpy as np

HW3_DIR = "/mnt/storage/mipt/microarch/HW-3"

folders = {
    'LRU': os.path.join(HW3_DIR, 'results_lru'),
    'PLRU': os.path.join(HW3_DIR, 'results_plru'),
    'SRRIP': os.path.join(HW3_DIR, 'results_srrip'),
    'LRU+LIP': os.path.join(HW3_DIR, 'results_lru_lip'),
    'LRU+BIP': os.path.join(HW3_DIR, 'results_lru_bip')
}

def parse_logs(policy_name, folder_path):
    data = []
    if not os.path.exists(folder_path):
        print(f"Предупреждение: Папка {folder_path} не найдена.")
        return data

    for filename in os.listdir(folder_path):
        if filename.endswith(".log"):
            trace_name = filename.replace(".log", "")
            with open(os.path.join(folder_path, filename), 'r') as f:
                content = f.read()
                ipc_match = re.search(r"CPU 0 cumulative IPC:\s+([\d\.]+)", content)
                l2c_match = re.search(r"L2C TOTAL\s+ACCESS:\s+(\d+)\s+HIT:\s+(\d+)\s+MISS:\s+(\d+)", content)

                if ipc_match and l2c_match:
                    ipc = float(ipc_match.group(1))
                    accesses = float(l2c_match.group(1))
                    misses = float(l2c_match.group(3))
                    miss_rate = (misses / accesses * 100) if accesses > 0 else 0.0

                    data.append({
                        'Trace': trace_name,
                        'Policy': policy_name,
                        'IPC': ipc,
                        'L2_Miss_Rate_%': miss_rate
                    })
                else:
                    print(f"Ошибка парсинга лога: {filename} в папке {folder_path}")
    return data

all_results = []
for name, path in folders.items():
    all_results.extend(parse_logs(name, path))

df = pd.DataFrame(all_results)

if df.empty:
    print("Данные не найдены. Дождитесь окончания работы симулятора и проверьте логи.")
    exit()

summary = df.groupby('Policy').agg({
    'IPC': lambda x: gmean(x[x > 0]),
    'L2_Miss_Rate_%': lambda x: gmean(x[x > 0])
}).reset_index()

policy_order = ['LRU', 'PLRU', 'SRRIP', 'LRU+LIP', 'LRU+BIP']
summary['Policy'] = pd.Categorical(summary['Policy'], categories=policy_order, ordered=True)
summary = summary.sort_values('Policy')

print("\n--- Сводная таблица GMEAN ---")
print(summary.to_string(index=False))

csv_path = os.path.join(HW3_DIR, 'l2_gmean_results.csv')
summary.to_csv(csv_path, index=False)

sns.set_theme(style="whitegrid")

plt.figure(figsize=(16, 6))
sns.barplot(data=df, x='Trace', y='L2_Miss_Rate_%', hue='Policy', hue_order=policy_order)
plt.title('Сравнение L2 Miss Rate (%) по трассам (Ниже - лучше)')
plt.ylabel('L2 Miss Rate (%)')
plt.xticks(rotation=45, ha='right')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(HW3_DIR, 'l2_miss_rate_comparison.png'))

plt.figure(figsize=(16, 6))
sns.barplot(data=df, x='Trace', y='IPC', hue='Policy', hue_order=policy_order)
plt.title('Сравнение IPC по трассам (Выше - лучше)')
plt.ylabel('IPC')
plt.xticks(rotation=45, ha='right')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(HW3_DIR, 'ipc_comparison.png'))

fig, ax1 = plt.subplots(figsize=(10, 6))
ax2 = ax1.twinx()

width = 0.35
x = np.arange(len(summary['Policy']))

ax1.bar(x - width/2, summary['IPC'], width, color='skyblue', label='GMEAN IPC')
ax2.bar(x + width/2, summary['L2_Miss_Rate_%'], width, color='salmon', label='GMEAN L2 Miss Rate (%)')

ax1.set_xlabel('Policy')
ax1.set_ylabel('IPC (Выше - лучше)')
ax2.set_ylabel('L2 Miss Rate % (Ниже - лучше)')
ax1.set_title('Итоговое сравнение GMEAN для политик L2')
ax1.set_xticks(x)
ax1.set_xticklabels(summary['Policy'])

lines_1, labels_1 = ax1.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax1.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left', bbox_to_anchor=(0.1, -0.1))

plt.tight_layout()
plt.savefig(os.path.join(HW3_DIR, 'gmean_comparison.png'))

print("\nАнализ завершен! Сохранены файлы:")
print(f" - {csv_path}")
print(f" - {os.path.join(HW3_DIR, 'l2_miss_rate_comparison.png')}")
print(f" - {os.path.join(HW3_DIR, 'ipc_comparison.png')}")
print(f" - {os.path.join(HW3_DIR, 'gmean_comparison.png')}")