import math, struct, zlib, os

W, H = 512, 512
BG = (168, 210, 185)
FG = (45, 32, 18)

img = bytearray(W * H * 4)

def set_px(x, y, r, g, b, a=255):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 4
        sa = a / 255.0; da = img[i+3] / 255.0
        oa = sa + da * (1 - sa)
        if oa > 0:
            img[i]   = int((r * sa + img[i]   * da * (1-sa)) / oa)
            img[i+1] = int((g * sa + img[i+1] * da * (1-sa)) / oa)
            img[i+2] = int((b * sa + img[i+2] * da * (1-sa)) / oa)
        img[i+3] = int(oa * 255)

def edge_alpha(x, y, cx, cy, r, feather=1.5):
    d = math.sqrt((x - cx)**2 + (y - cy)**2)
    if d >= r + feather: return 0
    if d <= r - feather: return 255
    return int(255 * (r + feather - d) / (2 * feather))

# Background
for y in range(H):
    for x in range(W):
        img[(y*W+x)*4] = BG[0]; img[(y*W+x)*4+1] = BG[1]
        img[(y*W+x)*4+2] = BG[2]; img[(y*W+x)*4+3] = 255

# Flower geometry
FCX, FCY = W // 2, 217
PETAL_DIST = 70
HOLE_R = 56
STEM_W = 14
STEM_TOP = FCY + HOLE_R + 6
STEM_BOT = 442

# Petals — slightly elongated outward for a touch more floral feel
for i in range(6):
    angle = i * math.pi / 3
    pcx = int(FCX + PETAL_DIST * math.sin(angle))
    pcy = int(FCY - PETAL_DIST * math.cos(angle))

    # radial and tangential radii (slightly egg-shaped)
    PETAL_R_OUT = 80   # radius away from center (elongated)
    PETAL_R_SIDE = 68  # radius across

    cos_a = math.sin(angle); sin_a = -math.cos(angle)  # radial direction

    x0 = pcx - PETAL_R_OUT - 2; x1 = pcx + PETAL_R_OUT + 2
    y0 = pcy - PETAL_R_OUT - 2; y1 = pcy + PETAL_R_OUT + 2

    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            dx = x - pcx; dy = y - pcy
            radial = dx * cos_a + dy * sin_a
            tang   = -dx * sin_a + dy * cos_a
            d = math.sqrt((radial / PETAL_R_OUT)**2 + (tang / PETAL_R_SIDE)**2)
            feather = 2.0 / PETAL_R_SIDE
            if d <= 1:
                a = 255
            elif d <= 1 + feather:
                a = int(255 * (1 + feather - d) / feather)
            else:
                a = 0
            if a > 0:
                set_px(x, y, FG[0], FG[1], FG[2], a)

# Stem
for y in range(STEM_TOP, STEM_BOT):
    for x in range(FCX - STEM_W//2, FCX + STEM_W//2 + 1):
        a = edge_alpha(x, y, FCX, y, STEM_W//2 + 0.5)
        set_px(x, y, FG[0], FG[1], FG[2], a)

# Punch center hole
for y in range(FCY - HOLE_R - 2, FCY + HOLE_R + 2):
    for x in range(FCX - HOLE_R - 2, FCX + HOLE_R + 2):
        a = edge_alpha(x, y, FCX, FCY, HOLE_R)
        if a > 0:
            fa = a / 255.0; i = (y * W + x) * 4
            img[i]   = int(img[i]   * (1-fa) + BG[0] * fa)
            img[i+1] = int(img[i+1] * (1-fa) + BG[1] * fa)
            img[i+2] = int(img[i+2] * (1-fa) + BG[2] * fa)

# Rounded square mask
R = W * 0.15
for y in range(H):
    for x in range(W):
        dx = max(0.0, max(R - x, x - (W - 1 - R)))
        dy = max(0.0, max(R - y, y - (H - 1 - R)))
        d = math.sqrt(dx*dx + dy*dy)
        if d > R: img[(y*W+x)*4+3] = 0
        elif d > R - 2: img[(y*W+x)*4+3] = int(img[(y*W+x)*4+3] * (R-d) / 2)

def make_png(pixels, w, h):
    def chunk(tag, data):
        c = struct.pack('>I', len(data)) + tag + data
        return c + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
    raw = bytearray()
    for row in range(h): raw += b'\x00' + pixels[row*w*4:(row+1)*w*4]
    ihdr = chunk(b'IHDR', struct.pack('>II', w, h) + bytes([8,6,0,0,0]))
    idat = chunk(b'IDAT', zlib.compress(bytes(raw), 9))
    iend = chunk(b'IEND', b'')
    return b'\x89PNG\r\n\x1a\n' + ihdr + idat + iend

def downsample(src, sw, dw, dh):
    s = sw // dw; out = bytearray(dw * dh * 4)
    for y in range(dh):
        for x in range(dw):
            r=g=b=a=0
            for dy in range(s):
                for dx in range(s):
                    i=((y*s+dy)*sw+(x*s+dx))*4
                    r+=src[i];g+=src[i+1];b+=src[i+2];a+=src[i+3]
            n=s*s; j=(y*dw+x)*4
            out[j]=r//n;out[j+1]=g//n;out[j+2]=b//n;out[j+3]=a//n
    return out

base = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base, 'icon-512.png'), 'wb') as f:
    f.write(make_png(img, W, H))
print('icon-512.png')
img192 = downsample(img, W, 192, 192)
with open(os.path.join(base, 'icon-192.png'), 'wb') as f:
    f.write(make_png(img192, 192, 192))
print('icon-192.png')
