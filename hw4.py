import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.size'] = 14

# 定義 x 範圍
x = np.linspace(-2, 2, 1000)
# 計算 a
a = (1 - x**2)**2 + (1.2 * x)**2
y1 = 1 / np.sqrt(a)

# 畫圖
plt.figure(figsize=(8, 6))
plt.plot(x, y1, label=r'$1/\sqrt{(1-x^2)^2+(1.2x)^2}$')
plt.axhline(1.01, color='r', linestyle='--', label=r'$y=1.01$')
plt.axhline(0.99, color='g', linestyle='--', label=r'$y=0.99$')

# 找交點 (y1=1.01 和 y1=0.99)
def find_roots(y_target):
	# 找 y1 - y_target = 0 的 x
	# 先找符號改變的區間
	roots = []
	for i in range(len(x)-1):
		if (y1[i] - y_target) * (y1[i+1] - y_target) < 0:
			root = fsolve(lambda xx: 1/np.sqrt((1-xx**2)**2 + (1.2*xx)**2) - y_target, x[i])[0]
			# 避免重複
			if not any(np.isclose(root, r, atol=1e-4) for r in roots):
				roots.append(root)
	return roots

roots_101 = find_roots(1.01)
roots_099 = find_roots(0.99)


# 標記交點
for r in roots_101:
	plt.plot(r, 1.01, 'ro')
for r in roots_099:
	plt.plot(r, 0.99, 'go')

# --- 區間上色 ---
# 只考慮 x>0 的交點
roots_101_pos = sorted([r for r in roots_101 if r > 0])
roots_099_pos = sorted([r for r in roots_099 if r > 0])

# 第一區間：0 < x < 第一個交點 (y=1.01)
if roots_101_pos:
	x_fill1 = x[(x > 0) & (x < roots_101_pos[0])]
	plt.fill_between(x_fill1, 0, 1/np.sqrt((1-x_fill1**2)**2 + (1.2*x_fill1)**2), color='orange', alpha=0.3)

# 第二區間：第一象限的第二個交點（y=1.01）和第三個交點（y=0.99）之間
roots_all = roots_101_pos + roots_099_pos
roots_all = sorted(roots_all)
if len(roots_all) >= 3:
	x2_left = roots_all[1]
	x2_right = roots_all[2]
	x_fill2 = x[(x > x2_left) & (x < x2_right)]
	if len(x_fill2) > 0:
		plt.fill_between(x_fill2, 0, 1/np.sqrt((1-x_fill2**2)**2 + (1.2*x_fill2)**2), color='cyan', alpha=0.3)

plt.legend()
plt.ylabel(r'$w_n^2\frac{u_0}{\ddot{u}_{go}}$', fontname='Times New Roman')
plt.xlabel(r'$f/f_n$', fontname='Times New Roman')
plt.xticks(fontname='Times New Roman')
plt.yticks(fontname='Times New Roman')
plt.grid(True)
plt.savefig('output.png')
plt.show()

plt.xlim(0, 1)
plt.ylim(0.95, 1.05)
plt.savefig('output_limited.png')
plt.show()
