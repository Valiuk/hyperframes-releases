"""Тематичні рамки для phone_slot_spin: усі сітки 3..7 x 3..7.
Геометрія — як у системі сіток: центр (432, 740) у Game, зона 760x600, клітинка <= 190,
шар рамки в Game має масштаб 64.2% x 70.8%, центр сітки в координатах рамки (665.5, 714.914).
"""
import sys, os, json
import numpy as np, cv2

FX, FY = 0.642, 0.708
FCX, FCY = 665.5, 714.914
WG, HG, PMAX = 760.0, 600.0, 190.0
SS = 3            # суперсемплінг
B = 20            # товщина обідка, px Game
M = 16            # поле під тінь
DIV = 6           # ширина роздільника

def pitch(C, R): return min(WG / C, HG / R, PMAX)

def lerp_stops(t, stops):
    t = np.clip(t, 0, 1); n = len(stops) - 1
    x = t * n; i = np.minimum(x.astype(int), n - 1); f = (x - i)[..., None]
    st = np.array(stops, np.float32)
    return st[i] * (1 - f) + st[i + 1] * f

def rrect_mask(h, w, x0, y0, x1, y1, r):
    m = np.zeros((h, w), np.uint8)
    r = int(r)
    cv2.rectangle(m, (int(x0 + r), int(y0)), (int(x1 - r), int(y1)), 255, -1)
    cv2.rectangle(m, (int(x0), int(y0 + r)), (int(x1), int(y1 - r)), 255, -1)
    for cx, cy in [(x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)]:
        cv2.circle(m, (int(cx), int(cy)), r, 255, -1, lineType=cv2.LINE_AA)
    return m

def over(dst, rgb, a):
    a = a[..., None].astype(np.float32)
    dst[..., :3] = rgb * a + dst[..., :3] * (1 - a)
    dst[..., 3:4] = a + dst[..., 3:4] * (1 - a)

def gem(img, cx, cy, r, col):
    # працюємо лише на фрагменті навколо самоцвіта
    H_, W_ = img.shape[:2]
    x0, y0 = max(0, int(cx - r - 3)), max(0, int(cy - r - 3))
    x1, y1 = min(W_, int(cx + r + 4)), min(H_, int(cy + r + 4))
    sub = img[y0:y1, x0:x1]
    _gem(sub, cx - x0, cy - y0, r, col)

def _gem(img, cx, cy, r, col):
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    a = np.clip(r + 0.5 - d, 0, 1)
    rim = np.clip(r + 0.5 - d, 0, 1) - np.clip(r * 0.78 + 0.5 - d, 0, 1)
    shade = np.clip(1 - (yy - (cy - r)) / (2 * r), 0, 1)[..., None]
    base = np.array(col, np.float32) * (0.55 + 0.6 * shade)
    over(img, np.clip(base, 0, 255), a)
    over(img, np.broadcast_to(np.array([255, 225, 140], np.float32), img[..., :3].shape), rim * 0.9)
    hl = np.clip(r * 0.32 - np.sqrt((xx - cx + r * 0.3) ** 2 + (yy - cy + r * 0.35) ** 2), 0, 1)
    over(img, np.broadcast_to(np.array([255, 255, 255], np.float32), img[..., :3].shape), hl * 0.9)

def build(theme, C, R):
    p = pitch(C, R); W, H = C * p, R * p
    Gw, Gh = W + 2 * (B + M), H + 2 * (B + M)
    w, h = int(round(Gw * SS)), int(round(Gh * SS))
    img = np.zeros((h, w, 4), np.float32)
    o = M * SS                                   # верхній лівий кут обідка
    ox0, oy0, ox1, oy1 = o, o, w - o, h - o
    ix0, iy0, ix1, iy1 = o + B * SS, o + B * SS, w - o - B * SS, h - o - B * SS

    # тінь
    sh = rrect_mask(h, w, ox0, oy0 + 4 * SS, ox1, oy1 + 4 * SS, 18 * SS).astype(np.float32) / 255
    sh = cv2.GaussianBlur(sh, (0, 0), 7 * SS) * 0.65
    over(img, np.zeros((h, w, 3), np.float32), sh)

    # вікно (під барабанами)
    win = rrect_mask(h, w, ix0, iy0, ix1, iy1, 6 * SS).astype(np.float32) / 255
    yy = np.mgrid[0:h, 0:w][0].astype(np.float32)
    tv = np.clip((yy - iy0) / max(1, iy1 - iy0), 0, 1)
    wc = lerp_stops(tv, theme['win'])
    over(img, wc[..., :3], win * wc[..., 3] / 255)
    # внутрішня тінь біля краю вікна
    dwin = cv2.distanceTransform((win > 0.5).astype(np.uint8), cv2.DIST_L2, 5)
    ins = np.clip(1 - dwin / (14 * SS), 0, 1) ** 2 * 0.55 * win
    over(img, np.zeros((h, w, 3), np.float32), ins)

    # роздільники
    metal = theme['metal']
    for k in range(1, C):
        x = ix0 + k * (ix1 - ix0) / C
        x0, x1 = x - DIV * SS / 2, x + DIV * SS / 2
        cols = np.arange(int(x0) - 2, int(x1) + 3)
        a = np.clip(np.minimum(cols + 1 - x0, x1 - cols), 0, 1)
        t = np.clip((cols - x0) / (x1 - x0), 0, 1)
        c = lerp_stops(t, [metal[-1], metal[0], metal[1], metal[2], metal[-2]])
        seg = img[iy0:iy1, cols[0]:cols[-1] + 1]
        over(seg, np.broadcast_to(c[None], seg[..., :3].shape).copy(), np.broadcast_to(a[None], seg.shape[:2]).copy())

    # обідок
    outer = rrect_mask(h, w, ox0, oy0, ox1, oy1, 18 * SS)
    ring = (outer.astype(np.float32) / 255) * (1 - (rrect_mask(h, w, ix0, iy0, ix1, iy1, 6 * SS).astype(np.float32) / 255))
    d_out = cv2.distanceTransform((outer > 127).astype(np.uint8), cv2.DIST_L2, 5)
    t = np.clip(d_out / (B * SS), 0, 1)
    mc = lerp_stops(t, metal)
    light = 1.12 - 0.3 * np.clip((yy - oy0) / max(1, oy1 - oy0), 0, 1)
    mc = np.clip(mc * light[..., None], 0, 255)
    over(img, mc, ring)
    band = ((t > 0.42) & (t < 0.6)).astype(np.float32) * ring
    band = cv2.GaussianBlur(band, (0, 0), 0.6 * SS)
    over(img, np.broadcast_to(np.array(theme['accent'], np.float32), mc.shape).copy(), band * 0.95)
    edge = np.clip(1 - np.abs(d_out - 1.2 * SS) / (1.2 * SS), 0, 1) * (outer > 127)
    over(img, np.broadcast_to(np.array(theme['edge'], np.float32), mc.shape).copy(), edge * 0.8)

    # самоцвіти: кути + верх/низ роздільників
    r = 6.5 * SS; bc = B * SS / 2
    for cx, cy in [(ox0 + bc + 2 * SS, oy0 + bc + 2 * SS), (ox1 - bc - 2 * SS, oy0 + bc + 2 * SS),
                   (ox0 + bc + 2 * SS, oy1 - bc - 2 * SS), (ox1 - bc - 2 * SS, oy1 - bc - 2 * SS)]:
        gem(img, cx, cy, r, theme['gem'])
    for k in range(1, C):
        x = ix0 + k * (ix1 - ix0) / C
        gem(img, x, oy0 + bc, r * 0.7, theme['gem']); gem(img, x, oy1 - bc, r * 0.7, theme['gem'])

    # у координати рамки (анізотропно) і 75% для PNG
    fw, fh = Gw / FX, Gh / FY
    pw, ph = int(round(fw * 0.75)), int(round(fh * 0.75))
    out = cv2.resize(img, (pw, ph), interpolation=cv2.INTER_AREA)
    meta = [int(round(FCX - fw / 2)), int(round(FCY - fh / 2)), int(round(fw)), int(round(fh)), pw, ph]
    return out, meta

def save(path, img):
    a = np.clip(img[..., 3:4], 0, 1)
    rgb = np.clip(img[..., :3], 0, 255)
    bgra = np.concatenate([rgb[..., ::-1], a * 255], 2).astype(np.uint8)
    cv2.imwrite(path, bgra, [cv2.IMWRITE_PNG_COMPRESSION, 6])

GOLD = [(255, 246, 190), (240, 196, 86), (168, 108, 24), (110, 62, 8), (214, 160, 58), (255, 232, 150)]
THEMES = {
 'BH': dict(metal=GOLD, accent=(40, 190, 70), edge=(60, 30, 0), gem=(30, 200, 70),
            win=[(6, 52, 22, 235), (3, 30, 12, 240)]),
 'BR': dict(metal=GOLD, accent=(40, 110, 210), edge=(70, 35, 5), gem=(40, 110, 220),
            win=[(70, 40, 12, 230), (40, 20, 4, 240)]),
 'FG': dict(metal=GOLD, accent=(210, 40, 110), edge=(70, 30, 5), gem=(220, 50, 130),
            win=[(40, 14, 52, 230), (22, 6, 30, 240)]),
 'FT': dict(metal=GOLD, accent=(220, 30, 30), edge=(80, 10, 0), gem=(225, 30, 40),
            win=[(110, 14, 14, 230), (60, 4, 6, 240)]),
 'MF': dict(metal=GOLD, accent=(200, 20, 30), edge=(70, 10, 0), gem=(30, 160, 120),
            win=[(70, 8, 14, 230), (36, 2, 8, 240)]),
 'SC': dict(metal=GOLD, accent=(220, 20, 40), edge=(80, 10, 0), gem=(230, 30, 60),
            win=[(90, 30, 8, 235), (50, 14, 2, 240)]),
 'DB': dict(metal=[(255, 255, 255), (255, 214, 232), (238, 130, 184), (200, 80, 140), (250, 180, 215), (255, 240, 248)],
            accent=(70, 200, 150), edge=(170, 50, 110), gem=(80, 210, 160),
            win=[(255, 248, 252, 235), (250, 228, 240, 240)]),
 'SE': dict(metal=GOLD, accent=(30, 90, 210), edge=(70, 35, 5), gem=(30, 110, 230),
            win=[(18, 24, 60, 230), (8, 10, 32, 240)]),
}

if __name__ == '__main__':
    root = sys.argv[1]; ids = sys.argv[2].split(',') if len(sys.argv) > 2 else list(THEMES)
    dirs = {d.split('_')[0]: d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))}
    allmeta = json.load(open(os.path.join(root, '_meta_frames.json'))) if os.path.exists(os.path.join(root, '_meta_frames.json')) else {}
    for sid in ids:
        fd = os.path.join(root, dirs[sid], 'FrameGrids'); os.makedirs(fd, exist_ok=True); meta = {}
        for C in range(3, 8):
            for R in range(3, 8):
                img, m = build(THEMES[sid], C, R)
                save(os.path.join(fd, 'g%dx%d.png' % (C, R)), img); meta['%dx%d' % (C, R)] = m
        allmeta[sid] = meta
        json.dump(allmeta, open(os.path.join(root, '_meta_frames.json'), 'w'))
        print(sid, 'ok', flush=True)
