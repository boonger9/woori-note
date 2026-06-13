"""
generate_index.py
대구우리교회 말씀 동반자 — index.html 자동 생성기
파일명 규칙: YYYY-MM-DD-{type}.html
예배 타입:  sun / sun-eve / wed / dawn / sat / special
            new / bible / baptism / catechism / disciple / etc
"""

import os
import re

# ================================================
# 예배 종류 메타 정보
# ================================================
SERVICE_META = {
    "sun":       {"label": "주일낮예배",    "icon": "☀️",  "cat": "주일예배"},
    "sun-eve":   {"label": "주일오후예배",   "icon": "🌇",  "cat": "주일예배"},
    "wed":       {"label": "수요기도회",    "icon": "🕯️",  "cat": "기도회"},
    "dawn":      {"label": "새벽기도회",    "icon": "🌅",  "cat": "기도회"},
    "sat":       {"label": "토요기도회",    "icon": "🙏",  "cat": "기도회"},
    "special":   {"label": "특별예배",      "icon": "✨",  "cat": "특별/기타"},
    "new":       {"label": "새가족교육",    "icon": "🌱",  "cat": "교육"},
    "bible":     {"label": "성경공부",      "icon": "📖",  "cat": "교육"},
    "baptism":   {"label": "세례/입교교육", "icon": "💧",  "cat": "교육"},
    "catechism": {"label": "학습교육",      "icon": "📝",  "cat": "교육"},
    "disciple":  {"label": "제자양육",      "icon": "🔥",  "cat": "교육"},
    "etc":       {"label": "기타",          "icon": "⛪",  "cat": "특별/기타"},
}

# 카테고리 표시 순서
CAT_ORDER = ["주일예배", "기도회", "교육", "특별/기타"]

# 타입 키를 파일명 접미사에서 추출하기 위한 패턴 (긴 것 먼저)
TYPE_KEYS = sorted(SERVICE_META.keys(), key=len, reverse=True)

# 파일명 정규식: YYYY-MM-DD-{type}.html
FILE_PATTERN = re.compile(
    r'^(\d{4})-(\d{2})-(\d{2})-(' + '|'.join(re.escape(k) for k in TYPE_KEYS) + r')\.html$'
)


def scan_files():
    """현재 디렉터리에서 설교노트 HTML 파일을 스캔합니다."""
    files = []
    for fname in os.listdir('.'):
        m = FILE_PATTERN.match(fname)
        if not m:
            continue
        year, month, day, stype = m.groups()
        meta = SERVICE_META.get(stype, SERVICE_META["etc"])

        # 파일 내부에서 설교 제목 추출 (선택적)
        title = ''
        try:
            with open(fname, encoding='utf-8') as f:
                content = f.read()
            # SERMON_KEY 바로 아래 title 메타 추출 시도
            tm = re.search(r'cfg-title[^>]*value="([^"]+)"', content)
            if not tm:
                # <title> 태그에서 추출 시도 (fallback)
                tm = re.search(r'<title>[^|]+\|\s*([^<]+)</title>', content)
            if tm:
                title = tm.group(1).strip()
        except Exception:
            pass

        files.append({
            'file':    fname,
            'date':    f'{year}-{month}-{day}',
            'year':    year,
            'month':   int(month),
            'day':     int(day),
            'stype':   stype,
            'label':   meta['label'],
            'icon':    meta['icon'],
            'cat':     meta['cat'],
            'display': f'{year}년 {int(month)}월 {int(day)}일',
            'title':   title,
        })

    return sorted(files, key=lambda x: (x['date'], x['stype']), reverse=True)


def make_card(b, is_latest):
    """카드 HTML 생성"""
    latest_cls   = ' latest' if is_latest else ''
    latest_badge = '<span class="latest-badge">최신</span>' if is_latest else ''
    meta_parts   = [b['icon'] + ' ' + b['label'], b['title']]
    meta         = ' · '.join(p for p in meta_parts if p)
    return f'''    <a href="{b['file']}" class="bulletin-card{latest_cls}" data-cat="{b['cat']}">
      <div class="card-icon">{b['icon']}</div>
      <div class="card-body">
        <div class="card-date">{b['display']}</div>
        <div class="card-meta">{meta}</div>
      </div>
      {latest_badge}
      <span class="card-arrow">›</span>
    </a>'''


def generate():
    bulletins = scan_files()

    # ── 연도 → 월 → 카테고리 → 파일 그룹핑 ──
    # 구조: grouped[year][month][cat] = [bulletin, ...]
    grouped = {}
    for b in bulletins:
        y  = b['year']
        mo = b['month']
        c  = b['cat']
        grouped.setdefault(y, {}).setdefault(mo, {}).setdefault(c, []).append(b)

    sections    = ''
    card_index  = 0

    for year in sorted(grouped.keys(), reverse=True):
        sections += f'  <div class="year-label">{year}년</div>\n'
        for month in sorted(grouped[year].keys(), reverse=True):
            sections += f'  <div class="month-label">{month}월</div>\n'
            for cat in CAT_ORDER:
                if cat not in grouped[year][month]:
                    continue
                items = grouped[year][month][cat]
                sections += f'  <div class="cat-label" data-cat="{cat}">{cat}</div>\n'
                for b in items:
                    sections += make_card(b, card_index == 0) + '\n'
                    card_index += 1

    if not sections.strip():
        sections = '  <div class="empty">아직 등록된 말씀 동반자가 없습니다.</div>'

    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<title>대구우리교회 | 말씀 동반자 목록</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@400;600;700&family=Noto+Sans+KR:wght@300;400;500;600&display=swap" rel="stylesheet">
<style>
:root{{--navy:#1a2c4e;--navy2:#2a4070;--gold:#b8952a;--gold2:#d4af50;--cream:#faf7f2;--border:#e8e0d0;--tl:#888;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
html,body{{overflow-x:hidden;-webkit-text-size-adjust:100%;}}
body{{font-family:'Noto Sans KR',sans-serif;background:var(--cream);color:var(--navy);min-height:100vh;-webkit-font-smoothing:antialiased;}}
.hdr{{background:linear-gradient(160deg,var(--navy) 0%,var(--navy2) 100%);color:#fff;text-align:center;padding:env(safe-area-inset-top) 20px 0;}}
.hdr-inner{{padding:32px 20px 28px;position:relative;overflow:hidden;}}
.hdr-inner::before{{content:'';position:absolute;top:-50px;right:-50px;width:200px;height:200px;border-radius:50%;background:rgba(184,149,42,.1);}}
.cross{{font-size:28px;margin-bottom:10px;display:block;position:relative;z-index:1;}}
.church-name{{font-family:'Noto Serif KR',serif;font-size:26px;font-weight:700;letter-spacing:3px;position:relative;z-index:1;}}
.church-sub{{font-size:13px;color:var(--gold2);letter-spacing:1px;margin-top:5px;position:relative;z-index:1;}}
.hdr-div{{width:36px;height:1px;background:var(--gold);margin:14px auto;position:relative;z-index:1;}}
.hdr-desc{{font-size:15px;color:rgba(255,255,255,.75);line-height:1.7;position:relative;z-index:1;}}
.f-btn.f-kids{{border-color:var(--gold);color:#9a7b18;font-weight:700;}}
.f-btn.f-kids.on,.f-btn.f-kids:active{{background:var(--gold);color:#fff;border-color:var(--gold);}}
/* 필터 탭 */
.filter-bar{{background:#fff;border-bottom:2px solid var(--border);padding:10px 16px;display:flex;gap:8px;overflow-x:auto;-webkit-overflow-scrolling:touch;scrollbar-width:none;position:sticky;top:0;z-index:100;}}
.filter-bar::-webkit-scrollbar{{display:none;}}
.f-btn{{flex-shrink:0;padding:6px 14px;border-radius:20px;font-size:13px;font-family:inherit;border:1.5px solid var(--border);background:#fff;color:var(--navy);cursor:pointer;transition:all 0.2s;white-space:nowrap;}}
.f-btn.on{{background:var(--navy);color:#fff;border-color:var(--navy);font-weight:700;}}
.main{{padding:20px 16px calc(env(safe-area-inset-bottom) + 40px);max-width:520px;margin:0 auto;}}
.year-label{{font-family:'Noto Serif KR',serif;font-size:14px;color:var(--tl);font-weight:600;letter-spacing:1px;margin:24px 0 8px 4px;display:flex;align-items:center;gap:8px;}}
.year-label::after{{content:'';flex:1;height:1px;background:var(--border);}}
.year-label:first-child{{margin-top:0;}}
.month-label{{font-size:13px;color:var(--gold);font-weight:600;margin:14px 0 4px 4px;letter-spacing:.5px;}}
.cat-label{{font-size:11px;color:var(--tl);font-weight:600;margin:10px 0 5px 4px;letter-spacing:.5px;text-transform:uppercase;}}
a.bulletin-card{{display:flex;align-items:center;gap:14px;background:#fff;border-radius:14px;padding:16px 18px;margin-bottom:9px;text-decoration:none;color:inherit;box-shadow:0 1px 6px rgba(26,44,78,.07);border:1.5px solid transparent;-webkit-tap-highlight-color:rgba(26,44,78,.08);touch-action:manipulation;transition:all 0.2s;}}
a.bulletin-card:active{{border-color:var(--gold);box-shadow:0 2px 12px rgba(184,149,42,.2);}}
a.bulletin-card.latest{{border-color:var(--gold);background:linear-gradient(135deg,#fffdf7,#fff);}}
.card-icon{{width:44px;height:44px;background:var(--navy);border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0;}}
a.bulletin-card.latest .card-icon{{background:linear-gradient(135deg,var(--gold),var(--gold2));}}
.card-body{{flex:1;min-width:0;}}
.card-date{{font-family:'Noto Serif KR',serif;font-size:16px;font-weight:600;color:var(--navy);margin-bottom:3px;}}
.card-meta{{font-size:13px;color:var(--tl);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.latest-badge{{background:var(--gold);color:#fff;font-size:11px;font-weight:700;padding:3px 9px;border-radius:20px;letter-spacing:.5px;flex-shrink:0;}}
.card-arrow{{color:var(--border);font-size:18px;flex-shrink:0;}}
a.bulletin-card.latest .card-arrow{{color:var(--gold2);}}
.empty{{text-align:center;padding:60px 20px;color:var(--tl);font-size:16px;line-height:2;}}
.hidden-card{{display:none;}}
.ftr{{text-align:center;padding:28px 16px;border-top:1px solid var(--border);margin-top:20px;}}
.ftr-name{{font-family:'Noto Serif KR',serif;font-size:15px;color:var(--navy);letter-spacing:1.5px;margin-bottom:4px;}}
.ftr-slogan{{font-size:12px;color:var(--tl);font-style:italic;}}
</style>
</head>
<body>
<header class="hdr">
  <div class="hdr-inner">
    <span class="cross">✝</span>
    <div class="church-name">대구우리교회</div>
    <div class="church-sub">대한예수교장로회 합신 · 경북노회</div>
    <div class="hdr-div"></div>
    <div class="hdr-desc">말씀 동반자 모아보기<br>원하는 날짜를 선택하세요</div>
  </div>
</header>
<!-- 필터 탭 -->
<div class="filter-bar">
  <button class="f-btn on" onclick="filterCat('all',this)">전체</button>
  <button class="f-btn" onclick="filterCat('주일예배',this)">☀️ 주일예배</button>
  <button class="f-btn" onclick="filterCat('기도회',this)">🕯️ 기도회</button>
  <button class="f-btn" onclick="filterCat('교육',this)">📖 교육</button>
  <button class="f-btn" onclick="filterCat('특별/기타',this)">✨ 특별/기타</button>
  <a class="f-btn f-kids" href="kids/">🧒 주일학교</a>
</div>
<main class="main" id="main-list">
{sections}
</main>
<footer class="ftr">
  <div class="ftr-name">대구우리교회</div>
  <div class="ftr-slogan">바른신학 · 바른교회 · 바른생활</div>
</footer>
<script>
function filterCat(cat, btn) {{
  document.querySelectorAll('.f-btn').forEach(b => b.classList.remove('on'));
  btn.classList.add('on');
  const cards = document.querySelectorAll('a.bulletin-card');
  const catLabels = document.querySelectorAll('.cat-label');
  if (cat === 'all') {{
    cards.forEach(c => c.style.display = '');
    catLabels.forEach(l => l.style.display = '');
  }} else {{
    // 카드: data-cat 속성으로 필터
    cards.forEach(c => {{
      c.style.display = c.dataset.cat === cat ? '' : 'none';
    }});
    catLabels.forEach(l => {{
      l.style.display = l.dataset.cat === cat ? '' : 'none';
    }});
  }}
}}
</script>
</body>
</html>'''

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'✅ index.html 생성 완료: {len(bulletins)}개 말씀 동반자')
    for b in bulletins:
        print(f'   {b["date"]} [{b["label"]}] {b["title"] or "(제목 없음)"}')


if __name__ == '__main__':
    generate()
