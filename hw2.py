import numpy as np
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from scipy.spatial import Voronoi

# ==============================================
# 🔧 基本設定
# ==============================================
F_total = 300  # 總水平力 (kN)

# 樓板尺寸 (6m x 6m)
floor_boundary = Polygon([(0, 0), (18.69, 0), (18.69, 11.51), (0, 11.51)])

# 柱子座標
columns = {
    'A': (0, 3.1),
    'B': (3.11, 3.1),
    'C': (6.17, 3.1),
    'D': (9.32, 3.1),
    'E': (12.47, 3.1),
    'F': (15.6, 3.1),
    'G': (18.69, 3.1),
    'H': (0, 10.8),
    'I': (3.08, 10.8),
    'J': (6.17, 10.8),
    'K': (9.32, 10.8),
    'L': (12.47, 10.8),
    'M': (15.37, 10.8),
    'N': (18.57, 10.8),
    #'O': (0, 6.95),
    #'P': (9.32, 6.95),
    #'Q': (18.69, 6.95)  
}

# ==============================================
# 📐 建立 Voronoi 分割 (加入外框防止無限延伸)
# ==============================================
points = np.array(list(columns.values()))

minx, miny, maxx, maxy = floor_boundary.bounds
# 加入外框邊界點 (讓 Voronoi 完全包覆樓板區域)
pad_x = (maxx - minx) * 0.1
pad_y = (maxy - miny) * 0.1
extra_points = np.array([
    [minx - pad_x, miny - pad_y],
    [maxx + pad_x, miny - pad_y],
    [maxx + pad_x, maxy + pad_y],
    [minx - pad_x, maxy + pad_y]
])
all_points = np.vstack([points, extra_points])

vor = Voronoi(all_points)

# function：取得每個 Voronoi 區域的 shapely 多邊形
def voronoi_region(region_index, vor, boundary):
    region = vor.regions[region_index]
    if not region or -1 in region:
        return None
    polygon = Polygon([vor.vertices[i] for i in region])
    return polygon.intersection(boundary)

# 建立每根柱子的影響區域（只取前五個真實柱子）
regions = {}
for i, name in enumerate(columns.keys()):
    region_index = vor.point_region[i]
    poly = voronoi_region(region_index, vor, floor_boundary)
    if poly and poly.area > 0:
        regions[name] = poly

# ==============================================
# 📏 計算各柱子面積 & 軸力
# ==============================================
areas = {name: poly.area for name, poly in regions.items()}
total_area = sum(areas.values())
axial_forces = {name: F_total * area / total_area for name, area in areas.items()}

# ==============================================
# 🧾 輸出結果
# ==============================================
print("柱子軸力分配（等力分割法）")
print("-" * 35)
for name in regions:
    print(f"柱子 {name}: 面積 = {areas[name]:.3f} m², 軸力 = {axial_forces[name]:.1f} kN")
print("-" * 35)
print(f"總樓板面積 = {total_area:.3f} m²")

# ==============================================
# 🎨 繪圖
# ==============================================

colors = ['lightblue', 'lightgreen', 'lightpink', 'lightyellow', 'lightgray']

# 根據樓板比例自動調整 figsize
fig_width = 8
fig_height = fig_width * (maxy - miny) / (maxx - minx)
plt.figure(figsize=(fig_width, fig_height))
x_floor, y_floor = floor_boundary.exterior.xy
plt.plot(x_floor, y_floor, 'k-', linewidth=2, label='樓板邊界')

for i, (name, poly) in enumerate(regions.items()):
    x, y = poly.exterior.xy
    plt.fill(x, y, alpha=0.5, fc=colors[i % len(colors)], ec='black')
    plt.text(columns[name][0], columns[name][1], f"{name}\n{axial_forces[name]:.1f} kN",
             ha='center', va='center', fontsize=9, fontweight='bold')

plt.title(f"等力分割法柱子影響區域 ({maxx-minx:.2f}m×{maxy-miny:.2f}m)")
plt.xlim(minx, maxx)
plt.ylim(miny, maxy)
plt.gca().set_aspect('equal', adjustable='box')
plt.savefig("hw2_voronoi.png", dpi=300)
plt.show()