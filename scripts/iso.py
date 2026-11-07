"""메인 슬라이드용 아이소메트릭 일러스트를 SVG로 그립니다.

사업분야마다 장면을 따로 짭니다. 블록(상자)을 격자 좌표로 쌓고, 면마다 밝기를 달리해 입체로 보이게 합니다.
"""
import math

C, S = math.cos(math.radians(30)), math.sin(math.radians(30))


class Scene:
    def __init__(self, ox=230, oy=120, unit=22):
        self.ox, self.oy, self.u = ox, oy, unit
        self.items = []  # (깊이, svg)

    def p(self, x, y, z):
        return (self.ox + (x - y) * C * self.u, self.oy + (x + y) * S * self.u - z * self.u)

    def pts(self, *xyz):
        return " ".join(f"{a:.1f},{b:.1f}" for a, b in (self.p(*q) for q in xyz))

    def box(self, x, y, z, w, d, h, top, left, right, stroke="none", depth=None):
        dp = depth if depth is not None else x + y + z * 0.01
        svg = (f'<polygon points="{self.pts((x, y + d, z), (x + w, y + d, z), (x + w, y + d, z + h), (x, y + d, z + h))}" fill="{left}" stroke="{stroke}"/>'
               f'<polygon points="{self.pts((x + w, y, z), (x + w, y + d, z), (x + w, y + d, z + h), (x + w, y, z + h))}" fill="{right}" stroke="{stroke}"/>'
               f'<polygon points="{self.pts((x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h))}" fill="{top}" stroke="{stroke}"/>')
        self.items.append((dp, svg))

    def raw(self, svg, depth):
        self.items.append((depth, svg))

    def render(self, label, w=460, h=330, extra_defs=""):
        body = "".join(s for _, s in sorted(self.items, key=lambda t: t[0]))
        return (f'<svg viewBox="0 0 {w} {h}" role="img" aria-label="{label}"><defs>{extra_defs}</defs>'
                f'{body}</svg>')


def base(sc, n=8, top="#FFFFFF", left="#C9DBF5", right="#AFC8EE"):
    sc.box(0, 0, -0.6, n, n, 0.6, top, left, right, depth=-100)


# ---------------------------------------------------------------- 01 정책 기획: 도시 블록과 깃발
def policy():
    sc = Scene()
    base(sc)
    sc.box(0.4, 0.4, 0, 7.2, 7.2, 0.05, "#E8F0FC", "#E8F0FC", "#E8F0FC", depth=-90)
    # 도로
    sc.box(0.4, 3.6, 0.05, 7.2, 0.8, 0.02, "#D3E1F7", "#D3E1F7", "#D3E1F7", depth=-80)
    sc.box(3.6, 0.4, 0.05, 0.8, 7.2, 0.02, "#D3E1F7", "#D3E1F7", "#D3E1F7", depth=-80)
    blues = [("#5B9BF0", "#2F6FD0", "#1F57B0"), ("#8BB8F5", "#5C8FDB", "#4878C4"), ("#C8DCFA", "#9DBCEB", "#86A8DD")]
    blocks = [(0.8, 0.8, 1.2, 1.2, 2.6, 0), (2.2, 0.9, 1.0, 1.1, 1.5, 1), (0.9, 2.3, 1.0, 1.0, 1.0, 2),
              (4.8, 0.8, 1.4, 1.2, 1.2, 2), (6.4, 0.9, 0.8, 1.0, 2.0, 1), (5.0, 2.3, 1.1, 1.0, 3.4, 0),
              (0.8, 4.8, 1.2, 1.4, 1.8, 1), (2.3, 5.0, 1.0, 1.0, 0.9, 2), (0.9, 6.5, 1.0, 0.8, 1.3, 2),
              (4.9, 4.9, 1.2, 1.2, 2.2, 1), (6.4, 5.0, 0.9, 1.0, 1.0, 2), (5.0, 6.5, 1.0, 0.8, 0.8, 2)]
    for x, y, w, d, h, c in blocks:
        t, l, r = blues[c]
        sc.box(x, y, 0.07, w, d, h, t, l, r)
    # 나무
    for x, y in [(2.6, 2.6), (2.9, 6.6), (6.8, 6.8), (6.9, 3.0)]:
        sc.box(x, y, 0.07, 0.12, 0.12, 0.4, "#7A5C3E", "#7A5C3E", "#6B4F33")
        cx, cy = sc.p(x + 0.06, y + 0.06, 0.75)
        sc.raw(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{0.38 * sc.u:.1f}" fill="#5FC27A"/>', x + y + 0.5)
    # 깃발 (가장 높은 건물 위)
    fx, fy = sc.p(5.55, 2.8, 3.47)
    sc.raw(f'<line x1="{fx:.1f}" y1="{fy:.1f}" x2="{fx:.1f}" y2="{fy - 46:.1f}" stroke="#274071" stroke-width="2"/>'
           f'<path d="M{fx:.1f} {fy - 46:.1f} l26 7 l-26 8z" fill="#FF8A3D"/>', 99)
    # 떠 있는 문서 카드
    sc.raw('<g transform="translate(350 32) rotate(6)"><rect width="78" height="96" rx="8" fill="#fff" stroke="#BCD2F3"/>'
           '<rect x="10" y="12" width="40" height="6" rx="3" fill="#126BDA"/><rect x="10" y="28" width="58" height="4" rx="2" fill="#D6E3F7"/>'
           '<rect x="10" y="38" width="50" height="4" rx="2" fill="#D6E3F7"/><rect x="10" y="48" width="56" height="4" rx="2" fill="#D6E3F7"/>'
           '<path d="M12 72 l8 8 l16 -18" fill="none" stroke="#2EB872" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></g>', 100)
    return sc.render("도시 블록 위에 깃발이 꽂힌 정책 기획 일러스트")


# ---------------------------------------------------------------- 02 R&D 기획: 계단형 로드맵과 설계판
def rnd():
    sc = Scene()
    base(sc)
    steps = [("#E3EDFB", "#B8CEEE", "#A0BCE6"), ("#C3D9F8", "#8DB0E6", "#779DD9"), ("#8DB8F3", "#5E8FDB", "#4B7CCB"), ("#4C8DEB", "#2766C4", "#1C54A8")]
    for i, (t, l, r) in enumerate(steps):
        sc.box(1 + i * 1.5, 4.6, 0, 1.5, 2.2, 0.7 + i * 0.75, t, l, r)
    # 계단 위 마일스톤 표시
    for i in range(4):
        x, y = sc.p(1.75 + i * 1.5, 5.7, 0.7 + i * 0.75)
        sc.raw(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="#fff" stroke="#126BDA" stroke-width="2"/>'
               f'<text x="{x:.1f}" y="{y + 3.5:.1f}" font-size="9" text-anchor="middle" fill="#126BDA" font-weight="700">{i + 1}</text>', 50 + i)
    # 설계 보드 (세로 판)
    sc.box(1.2, 1.0, 0, 3.6, 0.25, 3.0, "#F4F8FE", "#FFFFFF", "#DDE8F8", stroke="#BCD2F3")
    x0, y0 = sc.p(1.45, 1.0, 2.7)
    sc.raw(f'<g transform="translate({x0:.1f} {y0:.1f}) skewY(30)">'
           '<rect width="62" height="5" rx="2.5" fill="#126BDA"/>'
           '<g fill="none" stroke="#7FA7E3" stroke-width="1.5"><rect x="0" y="14" width="18" height="12" rx="2"/><rect x="26" y="14" width="18" height="12" rx="2"/>'
           '<rect x="52" y="14" width="18" height="12" rx="2"/><path d="M9 26 v10 h52 v-10 M35 26 v10"/></g>'
           '<rect x="0" y="44" width="70" height="3" rx="1.5" fill="#D6E3F7"/><rect x="0" y="52" width="50" height="3" rx="1.5" fill="#D6E3F7"/></g>', 30)
    # 사람(기획자) 두 명
    for x, y, col in [(5.6, 2.2, "#274071"), (6.6, 3.0, "#FF8A3D")]:
        sc.box(x, y, 0, 0.45, 0.35, 0.9, col, col, col)
        hx, hy = sc.p(x + 0.22, y + 0.17, 1.2)
        sc.raw(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="6.5" fill="#F6C9A8"/>', x + y + 1)
    # 목표 깃발 (최상단 계단)
    fx, fy = sc.p(6.0, 5.2, 3.05)
    sc.raw(f'<line x1="{fx:.1f}" y1="{fy:.1f}" x2="{fx:.1f}" y2="{fy - 40:.1f}" stroke="#274071" stroke-width="2"/>'
           f'<path d="M{fx:.1f} {fy - 40:.1f} l22 6 l-22 7z" fill="#2EB872"/>', 99)
    return sc.render("계단형 로드맵과 설계판이 있는 R&D 기획 일러스트")


# ---------------------------------------------------------------- 03 조사분석: 막대 차트와 돋보기
def analysis():
    sc = Scene()
    base(sc)
    # 격자 판
    for i in range(1, 8):
        a, b = sc.pts((i, 0.3, 0.01), (i, 7.7, 0.01)).split(" ")
        sc.raw(f'<line x1="{a.split(",")[0]}" y1="{a.split(",")[1]}" x2="{b.split(",")[0]}" y2="{b.split(",")[1]}" stroke="#E1EBF9"/>', -50)
        a, b = sc.pts((0.3, i, 0.01), (7.7, i, 0.01)).split(" ")
        sc.raw(f'<line x1="{a.split(",")[0]}" y1="{a.split(",")[1]}" x2="{b.split(",")[0]}" y2="{b.split(",")[1]}" stroke="#E1EBF9"/>', -50)
    heights = [1.3, 2.2, 1.7, 3.1, 4.1]
    cols = [("#C8DCFA", "#9DBCEB", "#86A8DD"), ("#9FC3F7", "#6D9CE2", "#5888D3"), ("#C8DCFA", "#9DBCEB", "#86A8DD"),
            ("#6FA5F2", "#3F7ED8", "#2F6AC0"), ("#2F7BE6", "#1A5FC0", "#134EA3")]
    for i, (h, (t, l, r)) in enumerate(zip(heights, cols)):
        sc.box(1.0 + i * 1.25, 4.2, 0, 0.85, 0.85, h, t, l, r)
    # 추세선
    pts = [sc.p(1.43 + i * 1.25, 4.62, h + 0.35) for i, h in enumerate(heights)]
    d = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    sc.raw(f'<path d="{d}" fill="none" stroke="#FF8A3D" stroke-width="2.5" stroke-linejoin="round"/>'
           + "".join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#fff" stroke="#FF8A3D" stroke-width="2"/>' for x, y in pts), 90)
    # 원형 차트 타일
    cx, cy = sc.p(6.3, 6.6, 0.02)
    sc.raw(f'<g transform="translate({cx:.1f} {cy:.1f}) scale(1 .58)"><circle r="30" fill="#E8F0FC"/>'
           '<path d="M0 0 L0 -30 A30 30 0 0 1 28.5 9.3Z" fill="#126BDA"/><path d="M0 0 L28.5 9.3 A30 30 0 0 1 -12 27.5Z" fill="#7DDB8A"/></g>', 60)
    # 돋보기
    mx, my = sc.p(6.2, 1.6, 1.6)
    sc.raw(f'<g transform="translate({mx:.1f} {my:.1f})"><line x1="16" y1="16" x2="36" y2="36" stroke="#274071" stroke-width="7" stroke-linecap="round"/>'
           '<circle r="24" fill="#E8F4FF" fill-opacity=".85" stroke="#274071" stroke-width="5"/>'
           '<path d="M-12 6 l7 -9 l7 5 l9 -12" fill="none" stroke="#126BDA" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></g>', 100)
    return sc.render("막대 차트와 돋보기가 놓인 조사분석 일러스트")


# ---------------------------------------------------------------- 04 연구개발: 온실과 재배 존
def research():
    sc = Scene()
    base(sc, top="#F4FBF1", left="#CDE6C4", right="#B4D9A8")
    # 밭 고랑
    for i in range(5):
        sc.box(0.5, 0.5 + i * 0.75, 0, 2.6, 0.45, 0.18, "#8BCF7E", "#5FA956", "#4E9447")
    # 온실 (몸체 + 박공지붕)
    gx, gy, gw, gd, gh = 3.8, 0.8, 3.6, 4.4, 1.3
    sc.box(gx, gy, 0, gw, gd, gh, "#EAF6FF", "#CFE8F8", "#B9DCF2", stroke="#8EC3E6")
    ridge = gh + 1.0
    roof_l = sc.pts((gx, gy + gd, gh), (gx + gw, gy + gd, gh), (gx + gw, gy + gd / 2, ridge), (gx, gy + gd / 2, ridge))
    roof_r = sc.pts((gx + gw, gy, gh), (gx + gw, gy + gd, gh), (gx + gw, gy + gd / 2, ridge))
    sc.raw(f'<polygon points="{roof_r}" fill="#DDF0FB" stroke="#8EC3E6"/><polygon points="{roof_l}" fill="#F3FAFF" fill-opacity=".9" stroke="#8EC3E6"/>', gx + gy + 50)
    # 유리 프레임 선
    for k in range(1, 4):
        a, b = sc.p(gx + gw * k / 4, gy + gd, 0), sc.p(gx + gw * k / 4, gy + gd, gh)
        sc.raw(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="#8EC3E6"/>', gx + gy + 49)
    # 온실 앞 재배 존 A/B/C
    for i, (t, l, r, lab) in enumerate([("#7DDB8A", "#4FB565", "#3F9E55", "A"), ("#FF9D7A", "#E2704C", "#C95E3D", "B"), ("#C9B8F5", "#9C86DD", "#8670C9", "C")]):
        sc.box(gx + 0.3 + i * 1.1, gy + gd + 0.5, 0, 0.9, 1.2, 0.55, t, l, r)
        x, y = sc.p(gx + 0.75 + i * 1.1, gy + gd + 1.1, 0.55)
        sc.raw(f'<text x="{x:.1f}" y="{y + 3:.1f}" font-size="9" font-weight="700" text-anchor="middle" fill="#fff">{lab}</text>', 80 + i)
    # 드론 (데이터 수집)
    dx, dy = sc.p(1.6, 1.4, 3.6)
    sc.raw(f'<g transform="translate({dx:.1f} {dy:.1f})"><rect x="-12" y="-4" width="24" height="8" rx="4" fill="#274071"/>'
           '<line x1="-20" y1="-8" x2="20" y2="-8" stroke="#274071" stroke-width="2"/><ellipse cx="-20" cy="-9" rx="9" ry="2" fill="#9DBCEB"/>'
           '<ellipse cx="20" cy="-9" rx="9" ry="2" fill="#9DBCEB"/><path d="M0 6 L-14 40 L14 40Z" fill="#7DDB8A" opacity=".18"/></g>', 100)
    # 구름
    sc.raw('<g fill="#fff" opacity=".95"><ellipse cx="392" cy="40" rx="22" ry="11"/><ellipse cx="410" cy="34" rx="16" ry="12"/><ellipse cx="376" cy="44" rx="12" ry="8"/></g>', 101)
    return sc.render("온실과 재배 존, 드론이 있는 스마트팜 연구개발 일러스트")


SCENES = {"policy": policy, "rnd": rnd, "analysis": analysis, "research": research}
