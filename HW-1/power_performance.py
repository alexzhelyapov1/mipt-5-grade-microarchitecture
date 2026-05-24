import numpy as np
import matplotlib.pyplot as plt

perf = np.linspace(0.01, 1.8, 1000)

f_e = perf / 1.0
f_p = perf / 2.0

u_e = np.maximum(1.0, f_e + 0.2)
u_p = np.maximum(1.0, f_p + 0.2)

power_e = 1.0 * (u_e**2) * f_e
power_p = 4.0 * (u_p**2) * f_p

optimal_power = np.minimum(power_e, power_p)

plt.figure(figsize=(10, 6), facecolor='white')

plt.plot(perf, power_e, color='#4A90E2', linewidth=2, linestyle='-.', label='E-ядро (базовая кривая)')
plt.plot(perf, power_p, color='#E94E77', linewidth=2, linestyle='-.', label='P-ядро (базовая кривая)')

plt.plot(perf, optimal_power, color='purple', linewidth=3.5, label='Оптимальная стратегия (Огибающая)')

intersect_perf = np.sqrt(2) - 0.2
intersect_power = 2 * intersect_perf
plt.scatter(intersect_perf, intersect_power, color='gold', s=100, zorder=5, edgecolor='black')
plt.annotate(f'Точка переключения\nPerf = {intersect_perf:.3f}', 
             xy=(intersect_perf, intersect_power), 
             xytext=(intersect_perf - 0.5, intersect_power + 3),
             arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.5),
             fontsize=11, fontweight='bold')

plt.title('Power(Performance) с учетом ограничения частоты $f_{max}=1.8$', fontsize=14, pad=15)
plt.xlabel('Performance (относительные величины)', fontsize=12)
plt.ylabel('Power (относительные величины)', fontsize=12)
plt.xlim(0, 1.8)
plt.ylim(0, 15)
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(loc='upper left', fontsize=11, framealpha=0.9)

plt.tight_layout()
plt.savefig('power_performance_plot.png', dpi=300)
print("Готово! График построен правильно.")
