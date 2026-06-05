"""
generate_kids_index.py
대구우리교회 주일학교 설교노트 아카이브 — kids/index.html 자동 생성기
파일명 규칙: kids/YYYY-MM-DD-kids.html
"""
import os, re

KIDS_DIR = "kids"
FILE_PATTERN = re.compile(r'^(\d{4})-(\d{2})-(\d{2})-kids\.html$')

def scan():
    items = []
    if not os.path.isdir(KIDS_DIR):
        return items
    for fname in os.listdir(KIDS_DIR):
        m = FILE_PATTERN.match(fname)
        if not m:
            continue
        y, mo, d = m.groups()
        title = ''
        try:
            with open(os.path.join(KIDS_DIR, fname), encoding='utf-8') as f:
                c = f.read()
            tm = re.search(r'<title>[^|]+\|\s*([^<]+)</title>', c)
            if tm:
                title = tm.group(1).strip()
        except Exception:
            pass
        items.append({
            'file': fname, 'date': f'{y}-{mo}-{d}',
            'year': y, 'month': int(mo), 'day': int(d),
            'display': f'{y}년 {int(mo)}월 {int(d)}일',
            'title': title,
        })
    return sorted(items, key=lambda x: x['date'], reverse=True)

def card(b, latest):
    lc = ' latest' if latest else ''
    badge = '<span class="latest-badge">최신</span>' if latest else ''
    meta = ' · '.join(p for p in ['🧒 초등부', b['title']] if p)
    return f'''    <a href="{b['file']}" class="card{lc}">
      <div class="card-icon">🧒</div>
      <div class="card-body">
        <div class="card-date">{b['display']}</div>
        <div class="card-meta">{meta}</div>
      </div>
      {badge}<span class="card-arrow">›</span>
    </a>'''

def generate():
    items = scan()
    grouped = {}
    for b in items:
        grouped.setdefault(b['year'], {}).setdefault(b['month'], []).append(b)
    sections, idx = '', 0
    for y in sorted(grouped, reverse=True):
        sections += f'  <div class="year-label">{y}년</div>\n'
        for mo in sorted(grouped[y], reverse=True):
            sections += f'  <div class="month-label">{mo}월</div>\n'
            for b in grouped[y][mo]:
                sections += card(b, idx == 0) + '\n'
                idx += 1
    if not sections.strip():
        sections = '  <div class="empty">아직 등록된 주일학교 노트가 없습니다.</div>'

    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<title>대구우리교회 주일학교 | 설교노트 모아보기</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@600;700&family=Noto+Sans+KR:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root{{--navy:#2D4A7A;--navy2:#3a5a92;--gold:#C8A000;--gold2:#d4af50;--cream:#faf7f2;--border:#e8e0d0;--tl:#888;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
html,body{{overflow-x:hidden;-webkit-text-size-adjust:100%;}}
body{{font-family:'Noto Sans KR',sans-serif;background:var(--cream);color:var(--navy);min-height:100vh;}}
.hdr{{background:linear-gradient(160deg,var(--navy),var(--navy2));color:#fff;text-align:center;padding:env(safe-area-inset-top) 20px 0;}}
.hdr-inner{{padding:30px 20px 26px;position:relative;overflow:hidden;}}
.hdr-inner::before{{content:'';position:absolute;top:-50px;right:-50px;width:200px;height:200px;border-radius:50%;background:rgba(200,160,0,.12);}}
.kid{{font-size:30px;margin-bottom:8px;display:block;position:relative;z-index:1;}}
.name{{font-family:'Noto Serif KR',serif;font-size:23px;font-weight:700;letter-spacing:2px;position:relative;z-index:1;}}
.sub{{font-size:13px;color:var(--gold2);letter-spacing:1px;margin-top:5px;position:relative;z-index:1;}}
.div{{width:36px;height:1px;background:var(--gold);margin:13px auto;position:relative;z-index:1;}}
.desc{{font-size:14px;color:rgba(255,255,255,.78);line-height:1.7;position:relative;z-index:1;}}
.main{{padding:20px 16px calc(env(safe-area-inset-bottom) + 40px);max-width:520px;margin:0 auto;}}
.year-label{{font-family:'Noto Serif KR',serif;font-size:14px;color:var(--tl);font-weight:600;letter-spacing:1px;margin:24px 0 8px 4px;display:flex;align-items:center;gap:8px;}}
.year-label::after{{content:'';flex:1;height:1px;background:var(--border);}}
.year-label:first-child{{margin-top:0;}}
.month-label{{font-size:13px;color:var(--gold);font-weight:600;margin:14px 0 6px 4px;letter-spacing:.5px;}}
a.card{{display:flex;align-items:center;gap:14px;background:#fff;border-radius:14px;padding:16px 18px;margin-bottom:9px;text-decoration:none;color:inherit;box-shadow:0 1px 6px rgba(26,44,78,.07);border:1.5px solid transparent;transition:all .2s;}}
a.card:active{{border-color:var(--gold);}}
a.card.latest{{border-color:var(--gold);background:linear-gradient(135deg,#fffdf7,#fff);}}
.card-icon{{width:44px;height:44px;background:var(--navy);border-radius:11px;display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;}}
a.card.latest .card-icon{{background:linear-gradient(135deg,var(--gold),var(--gold2));}}
.card-body{{flex:1;min-width:0;}}
.card-date{{font-family:'Noto Serif KR',serif;font-size:16px;font-weight:600;margin-bottom:3px;}}
.card-meta{{font-size:13px;color:var(--tl);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}}
.latest-badge{{background:var(--gold);color:#fff;font-size:11px;font-weight:700;padding:3px 9px;border-radius:20px;flex-shrink:0;}}
.card-arrow{{color:var(--border);font-size:18px;flex-shrink:0;}}
.empty{{text-align:center;padding:60px 20px;color:var(--tl);font-size:16px;line-height:2;}}
.ftr{{text-align:center;padding:26px 16px;border-top:1px solid var(--border);margin-top:20px;}}
.ftr-name{{font-family:'Noto Serif KR',serif;font-size:15px;letter-spacing:1.5px;margin-bottom:4px;}}
.ftr-slogan{{font-size:12px;color:var(--tl);font-style:italic;}}
.back{{display:inline-block;margin-top:14px;font-size:13px;color:var(--gold2);text-decoration:none;position:relative;z-index:1;}}
</style>
</head>
<body>
<header class="hdr">
  <div class="hdr-inner">
    <span class="kid">🧒</span>
    <div class="name">대구우리교회 주일학교</div>
    <div class="sub">초등부 설교노트</div>
    <div class="div"></div>
    <div class="desc">주일학교 말씀 노트 모아보기<br>원하는 날짜를 선택하세요</div>
    <a class="back" href="../index.html">← 어른 말씀 동반자 목록으로</a>
  </div>
</header>
<main class="main">
{sections}
</main>
<footer class="ftr">
  <div class="ftr-name">대구우리교회 주일학교</div>
  <div class="ftr-slogan">바른신학 · 바른교회 · 바른생활</div>
</footer>
</body>
</html>'''
    os.makedirs(KIDS_DIR, exist_ok=True)
    with open(os.path.join(KIDS_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'✅ kids/index.html 생성 완료: {len(items)}개')
    for b in items:
        print(f'   {b["date"]} {b["title"] or "(제목 없음)"}')

if __name__ == '__main__':
    generate()
