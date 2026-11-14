"""Picture of the patch antenna: its parts pulled apart, and the simulated beam."""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

res_dir, out = sys.argv[1], sys.argv[2]
G, L, cut, feed, h = 60.0, 37.52, 3.5, 7.0, 1.524

COPPER = "#d9a521"
BOARD = "#e9e4d4"
INK = "#222222"


def rect(g, z):
    a = g / 2
    return [(-a, -a, z), (a, -a, z), (a, a, z), (-a, a, z)]


def patch_poly(z):
    a = L / 2
    # clipped corners: (-x,+y) and (+x,-y)
    return [(-a, -a, z), (a - cut, -a, z), (a, -a + cut, z), (a, a, z),
            (-a + cut, a, z), (-a, a - cut, z)]


def slab(g, z0, z1):
    a = g / 2
    c = [(-a, -a), (a, -a), (a, a), (-a, a)]
    faces = [[(x, y, z0) for x, y in c], [(x, y, z1) for x, y in c]]
    for i in range(4):
        (x0, y0), (x1, y1) = c[i], c[(i + 1) % 4]
        faces.append([(x0, y0, z0), (x1, y1, z0), (x1, y1, z1), (x0, y0, z1)])
    return faces


def cylinder(ax, x, y, z0, z1, r, color):
    t = np.linspace(0, 2 * np.pi, 30)
    zz = np.array([z0, z1])
    T, Z = np.meshgrid(t, zz)
    ax.plot_surface(x + r * np.cos(T), y + r * np.sin(T), Z, color=color,
                    linewidth=0, shade=True)


fig = plt.figure(figsize=(15, 7.5), facecolor="white")

# ---------------------------------------------------------------- parts
from mpl_toolkits.mplot3d import proj3d
ax = fig.add_subplot(1, 2, 1, projection="3d", computed_zorder=False)
zc0, zc1, zg, zs, zp = -40.0, -26.0, 0.0, 18.0, 40.0   # exploded heights
cylinder(ax, feed, 0, zc0, zc1, 3.2, "#9a9a9a")
ax.plot([feed, feed], [0, 0], [zc1, zg], color="#b03030", linewidth=2.2, zorder=1)
ax.add_collection3d(Poly3DCollection([rect(G, zg)], facecolor=COPPER,
                                     edgecolor=INK, linewidth=0.8, zorder=2))
ax.plot([feed, feed], [0, 0], [zg, zs], color="#b03030", linewidth=2.2, zorder=3)
ax.add_collection3d(Poly3DCollection(slab(G, zs, zs + 4), facecolor=BOARD,
                                     edgecolor=INK, linewidth=0.6, alpha=0.8, zorder=4))
ax.plot([feed, feed], [0, 0], [zs + 4, zp], color="#b03030", linewidth=2.2, zorder=5)
ax.add_collection3d(Poly3DCollection([patch_poly(zp)], facecolor=COPPER,
                                     edgecolor=INK, linewidth=0.8, zorder=6))
ax.scatter([feed], [0], [zp], color="#b03030", s=26, depthshade=False, zorder=7)

ax.set_xlim(-48, 48); ax.set_ylim(-48, 48); ax.set_zlim(-42, 46)
ax.set_box_aspect((1, 1, 0.92))
ax.view_init(elev=22, azim=-58)
ax.set_axis_off()
ax.set_position([0.0, 0.02, 0.40, 0.86])
fig.canvas.draw()


def callout(text, xyz, ty):
    x2, y2, _ = proj3d.proj_transform(*xyz, ax.get_proj())
    ax.annotate(text, xy=(x2, y2), xytext=(1.02, ty), textcoords="axes fraction",
                fontsize=11.5, color=INK, va="center", ha="left", zorder=20,
                arrowprops=dict(arrowstyle="-", color="#666666", linewidth=0.9))


a2 = G / 2
callout("PATCH: copper square, 37.5 mm.\nThis is the part that radiates.", (L / 2, -L / 4, zp), 0.84)
callout("Two clipped corners make the\nsignal spin (circular polarization).", (L / 2 - cut / 2, -L / 2 + cut / 2, zp), 0.70)
callout("BOARD MATERIAL: PTFE, 1.52 mm thick.\nJust holds the copper apart.", (a2, -a2 / 2, zs + 2), 0.54)
callout("GROUND PLANE: solid copper, 60 mm.\nReflects the signal forward.", (a2, -a2 / 2, zg), 0.38)
callout("FEED PIN (red): carries the radio\nsignal up to the patch.", (feed, 0, (zg + zs) / 2), 0.24)
callout("SMA CONNECTOR: the cable from\nthe radio screws on here.", (feed + 3, 0, (zc0 + zc1) / 2), 0.10)
fig.text(0.21, 0.94, "The antenna, layers pulled apart", fontsize=14, color=INK, ha="center")
fig.text(0.21, 0.905, "(really all one board, 1.6 mm thick)", fontsize=11, color="#555555", ha="center")

# ---------------------------------------------------------------- beam
d = np.genfromtxt(f"{res_dir}/pattern_f0.csv", delimiter=",", names=True)
th_c = d["theta_deg"]
c0, c90 = d["cutT_phi0"], d["cutT_phi90"]

th = np.linspace(0, 180, 91)
ph = np.linspace(0, 360, 121)
TH, PH = np.meshgrid(th, ph)
c0p = np.interp(TH, th_c, c0); c0m = np.interp(-TH, th_c, c0)
c9p = np.interp(TH, th_c, c90); c9m = np.interp(-TH, th_c, c90)
cp, sp = np.cos(np.radians(PH)), np.sin(np.radians(PH))
gain = cp**2 * np.where(cp >= 0, c0p, c0m) + sp**2 * np.where(sp >= 0, c9p, c9m)

floor = -20.0
r = np.clip(gain - floor, 0, None) / (gain.max() - floor) * 70.0
X = r * np.sin(np.radians(TH)) * cp
Y = r * np.sin(np.radians(TH)) * sp
Z = r * np.cos(np.radians(TH))

ax2 = fig.add_subplot(1, 2, 2, projection="3d", computed_zorder=False)
norm = plt.Normalize(-15, gain.max())
ax2.add_collection3d(Poly3DCollection(slab(G, -1.5, 0), facecolor=BOARD,
                                      edgecolor=INK, linewidth=0.6, zorder=1))
ax2.add_collection3d(Poly3DCollection([patch_poly(0.3)], facecolor=COPPER,
                                      edgecolor=INK, linewidth=0.8, zorder=2))
ax2.plot_surface(X, Y, Z, facecolors=plt.cm.viridis(norm(gain)), rstride=1,
                 cstride=1, linewidth=0, antialiased=True, alpha=0.38, shade=False,
                 zorder=3)
ax2.plot([0, 0], [0, 0], [0, 82], color=INK, linewidth=0.8, linestyle="--", zorder=4)
ax2.text(0, 0, 86, f"peak {gain.max():.1f} dBi, straight out", fontsize=11,
         color=INK, ha="center")
ax2.set_xlim(-60, 60); ax2.set_ylim(-60, 60); ax2.set_zlim(-35, 85)
ax2.set_box_aspect((1, 1, 1))
ax2.view_init(elev=14, azim=-58)
ax2.set_axis_off()
ax2.set_position([0.62, 0.02, 0.30, 0.86])
ax2.patch.set_alpha(0)
fig.text(0.77, 0.94, "Where it sends the signal (simulated, 2.425 GHz)", fontsize=14, color=INK, ha="center")
fig.text(0.77, 0.905, "bubble size = signal strength in that direction", fontsize=11, color="#555555", ha="center")
sm = plt.cm.ScalarMappable(norm=norm, cmap="viridis")
cb = fig.colorbar(sm, cax=fig.add_axes([0.925, 0.25, 0.012, 0.45]))
cb.set_label("Gain (dBi)", fontsize=11)

fig.savefig(out, dpi=130, facecolor="white")
print("wrote", out)
