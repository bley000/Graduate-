import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString, Point
import numpy as np

# -------------------------------
# 1. 樓板與柱子設定
# -------------------------------
floor_boundary = Polygon([(0, 0), (18.69, 0), (18.69, 11.51), (0, 11.51)])
columns = {
    'A': (0, 3.1), 'B': (3.11, 3.1), 'C': (6.17, 3.1), 'D': (9.32, 3.1), 'E': (12.47, 3.1), 'F': (15.6, 3.1), 'G': (18.69, 3.1),
    'H': (0, 10.8), 'I': (3.08, 10.8), 'J': (6.17, 10.8), 'K': (9.32, 10.8), 'L': (12.47, 10.8), 'M': (15.37, 10.8), 'N': (18.57, 10.8)
} 
ray_angles = [45, 135, 225, 315]  # 射線角度（度）


# 畫樓板邊界
x, y = floor_boundary.exterior.xy
min_x, max_x = min(x), max(x)
min_y, max_y = min(y), max(y)
width = max_x - min_x
height = max_y - min_y
fig_w = 12
fig_h = fig_w * (height / width)
plt.figure(figsize=(fig_w, fig_h))
plt.plot(x, y, 'k-', linewidth=2, label='Floor Boundary')

# 畫柱子與射線，並儲存所有射線資訊
all_rays = []  # (柱名, 起點, 角度, LineString)
for name, (cx, cy) in columns.items():
    plt.plot(cx, cy, 'ro')
    plt.text(cx, cy, name, fontsize=12, ha='center', va='center', color='white', bbox=dict(facecolor='red', edgecolor='none', boxstyle='circle,pad=0.2'))
    for angle in ray_angles:
        rad = np.deg2rad(angle)
        ray_length = 20
        dx = np.cos(rad) * ray_length
        dy = np.sin(rad) * ray_length
        ray = LineString([(cx, cy), (cx + dx, cy + dy)])
        intersection = ray.intersection(floor_boundary.boundary)
        if intersection.is_empty:
            continue
        if intersection.geom_type == 'MultiPoint':
            points = list(intersection.geoms)
            points.sort(key=lambda p: Point(cx, cy).distance(p))
            end_point = points[0]
        else:
            end_point = intersection
        # 先暫存射線資訊，稍後決定終點
        all_rays.append({
            'col': name,
            'start': (cx, cy),
            'angle': angle,
            'line': LineString([(cx, cy), (end_point.x, end_point.y)]),
            'end_default': (end_point.x, end_point.y)
        })

# 計算所有射線的交點，並記錄每條射線最近的交點
ray_stops = [None] * len(all_rays)
for i in range(len(all_rays)):
    ray1 = all_rays[i]
    min_dist = None
    min_point = None
    for j in range(len(all_rays)):
        if i == j:
            continue
        ray2 = all_rays[j]
        if ray1['col'] == ray2['col']:
            continue
        inter = ray1['line'].intersection(ray2['line'])
        if inter.is_empty or not isinstance(inter, Point):
            continue
        if not floor_boundary.contains(inter):
            continue
        dist = Point(ray1['start']).distance(inter)
        if min_dist is None or dist < min_dist:
            min_dist = dist
            min_point = inter
    if min_point is not None:
        ray_stops[i] = (min_point.x, min_point.y)
    else:
        ray_stops[i] = all_rays[i]['end_default']

# 畫射線（到交點或邊界）
for i, ray in enumerate(all_rays):
    sx, sy = ray['start']
    ex, ey = ray_stops[i]
    plt.plot([sx, ex], [sy, ey], 'b--', linewidth=1)
    # 更新射線的實際終點
    all_rays[i]['line'] = LineString([(sx, sy), (ex, ey)])

# 找所有不同柱子的射線交點，並畫外平分線（遇到樓板邊界就停止）
for i in range(len(all_rays)):
    for j in range(i+1, len(all_rays)):
        ray1 = all_rays[i]
        ray2 = all_rays[j]
        if ray1['col'] == ray2['col']:
            continue  # 同柱不處理
        inter = ray1['line'].intersection(ray2['line'])
        if inter.is_empty or not isinstance(inter, Point):
            continue
        # 檢查交點是否在樓板內部
        if not floor_boundary.contains(inter):
            continue
        # 外角平分線方向
        a1 = ray1['angle'] % 360
        a2 = ray2['angle'] % 360
        v1 = np.array([np.cos(np.deg2rad(a1)), np.sin(np.deg2rad(a1))])
        v2 = np.array([np.cos(np.deg2rad(a2)), np.sin(np.deg2rad(a2))])
        bisect_vec = (+v1 + v2)
        if np.linalg.norm(bisect_vec) < 1e-8:
            bisect_vec = np.array([-v1[1], v1[0]])
        bisect_vec = bisect_vec / np.linalg.norm(bisect_vec)
        # 先設一個較長長度
        bisect_length = 10
        bx_far = inter.x + bisect_vec[0] * bisect_length
        by_far = inter.y + bisect_vec[1] * bisect_length
        bisect_line = LineString([(inter.x, inter.y), (bx_far, by_far)])
        # 1. 與樓板邊界交點
        bisect_inter = bisect_line.intersection(floor_boundary.boundary)
        bisect_targets = []
        if not bisect_inter.is_empty:
            if bisect_inter.geom_type == 'MultiPoint':
                bisect_targets += list(bisect_inter)
            elif bisect_inter.geom_type == 'Point':
                bisect_targets.append(bisect_inter)
        # 2. 與其他交點的交點
        # 先收集所有交點（排除自己）
        all_cross_points = []
        for m in range(len(all_rays)):
            for n in range(m+1, len(all_rays)):
                if (m == i and n == j) or (m == j and n == i):
                    continue
                rayA = all_rays[m]
                rayB = all_rays[n]
                if rayA['col'] == rayB['col']:
                    continue
                cross = rayA['line'].intersection(rayB['line'])
                if cross.is_empty or not isinstance(cross, Point):
                    continue
                if not floor_boundary.contains(cross):
                    continue
                all_cross_points.append(cross)
        # 計算外角平分線與這些交點的交點（其實就是檢查外角平分線是否會經過這些點）
        for pt in all_cross_points:
            # 向量投影法判斷pt是否在外角平分線上且方向正確
            vec_to_pt = np.array([pt.x - inter.x, pt.y - inter.y])
            proj = np.dot(vec_to_pt, bisect_vec)
            if proj > 1e-8:  # 在外角平分線正方向上
                # 並且在直線上（允許微小誤差）
                perp_dist = np.linalg.norm(vec_to_pt - proj * bisect_vec)
                if perp_dist < 1e-6:
                    bisect_targets.append(pt)
        # 取離交點最近的作為終點
        if bisect_targets:
            bisect_targets.sort(key=lambda p: Point(inter.x, inter.y).distance(p))
            bx, by = bisect_targets[0].x, bisect_targets[0].y
        else:
            bx, by = bx_far, by_far
        plt.plot([inter.x, bx], [inter.y, by], 'g-', linewidth=2, alpha=0.7)

plt.axis('equal')
plt.xlim(min(x) - 1, max(x) + 1)
plt.ylim(min(y) - 1, max(y) + 1)
plt.xlabel('X')
plt.ylabel('Y')
plt.title('Floor, Columns, and Rays')
plt.legend()
plt.tight_layout()
plt.savefig('column_rays.png')
plt.show()
