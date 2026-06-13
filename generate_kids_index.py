"""
generate_kids_index.py
대구우리교회 주일학교 — 입구(kids/index.html) + 학생용 방(kids/student/index.html) + 교사용 방(kids/teacher/index.html)
구조:
  kids/index.html              ← 방 선택 (학생용/교사용)
  kids/student/YYYY-MM-DD.html ← 학생 노트 (암호 3230)
  kids/teacher/YYYY-MM-DD.html ← 교사 노트 (암호 4341)
레거시: kids/YYYY-MM-DD-kids.html (이전 단일 학생노트) → 학생 방 목록에 '(이전)'으로 함께 표시
"""
import os, re

KIDS_DIR = "kids"
NOTE_PAT = re.compile(r'^(\d{4})-(\d{2})-(\d{2})\.html$')
LEGACY_PAT = re.compile(r'^(\d{4})-(\d{2})-(\d{2})-kids\.html$')

def title_of(path):
    try:
        with open(path, encoding='utf-8') as f:
            c = f.read()
        m = re.search(r'<title>[^|]+\|\s*([^<]+)</title>', c)
        if m:
            return m.group(1).strip()
    except Exception:
        pass
    return ''

def scan_room(role):
    items = []
    d = os.path.join(KIDS_DIR, role)
    if os.path.isdir(d):
        for fn in os.listdir(d):
            m = NOTE_PAT.match(fn)
            if not m:
                continue
            y, mo, da = m.groups()
            items.append({'file': fn, 'date': f'{y}-{mo}-{da}', 'legacy': False,
                          'display': f'{y}년 {int(mo)}월 {int(da)}일', 'title': title_of(os.path.join(d, fn))})
    if role == 'student':
        for fn in os.listdir(KIDS_DIR):
            m = LEGACY_PAT.match(fn)
            if not m:
                continue
            y, mo, da = m.groups()
            items.append({'file': f'../{fn}', 'date': f'{y}-{mo}-{da}', 'legacy': True,
                          'display': f'{y}년 {int(mo)}월 {int(da)}일', 'title': title_of(os.path.join(KIDS_DIR, fn))})
    return sorted(items, key=lambda x: x['date'], reverse=True)

BASE_CSS = """
:root{--navy:#2D4A7A;--navy2:#3a5a92;--gold:#C8A000;--gold2:#d4af50;--cream:#faf7f2;--border:#e8e0d0;--tl:#888;}
*{box-sizing:border-box;margin:0;padding:0;}
html,body{overflow-x:hidden;-webkit-text-size-adjust:100%;}
body{font-family:'Noto Sans KR',sans-serif;background:var(--cream);color:var(--navy);min-height:100vh;}
.hdr{background:linear-gradient(160deg,var(--navy),var(--navy2));color:#fff;text-align:center;padding:env(safe-area-inset-top) 20px 0;}
.hdr-inner{padding:30px 20px 26px;position:relative;overflow:hidden;}
.kid{font-size:30px;margin-bottom:8px;display:block;}
.name{font-family:'Noto Serif KR',serif;font-size:22px;font-weight:700;letter-spacing:1.5px;}
.sub{font-size:13px;color:var(--gold2);letter-spacing:1px;margin-top:5px;}
.divx{width:36px;height:1px;background:var(--gold);margin:13px auto;}
.desc{font-size:14px;color:rgba(255,255,255,.78);line-height:1.7;}
.main{padding:20px 16px calc(env(safe-area-inset-bottom) + 40px);max-width:520px;margin:0 auto;}
.year-label{font-family:'Noto Serif KR',serif;font-size:14px;color:var(--tl);font-weight:600;margin:20px 0 8px 4px;display:flex;align-items:center;gap:8px;}
.year-label::after{content:'';flex:1;height:1px;background:var(--border);}
.month-label{font-size:13px;color:var(--gold);font-weight:600;margin:14px 0 6px 4px;}
a.card{display:flex;align-items:center;gap:14px;background:#fff;border-radius:14px;padding:16px 18px;margin-bottom:10px;text-decoration:none;color:inherit;box-shadow:0 1px 6px rgba(26,44,78,.07);border:1.5px solid transparent;}
a.card:active{border-color:var(--gold);}
a.card.latest{border-color:var(--gold);background:linear-gradient(135deg,#fffdf7,#fff);}
.card-icon{width:46px;height:46px;background:var(--navy);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:24px;flex-shrink:0;}
a.card.latest .card-icon{background:linear-gradient(135deg,var(--gold),var(--gold2));}
.card-body{flex:1;min-width:0;}
.card-date{font-family:'Noto Serif KR',serif;font-size:16px;font-weight:600;margin-bottom:3px;}
.card-meta{font-size:13px;color:var(--tl);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.latest-badge{background:var(--gold);color:#fff;font-size:11px;font-weight:700;padding:3px 9px;border-radius:20px;flex-shrink:0;}
.card-arrow{color:var(--border);font-size:18px;flex-shrink:0;}
.empty{text-align:center;padding:50px 20px;color:var(--tl);font-size:15px;line-height:2;}
.ftr{text-align:center;padding:26px 16px;border-top:1px solid var(--border);margin-top:20px;}
.ftr-name{font-family:'Noto Serif KR',serif;font-size:15px;letter-spacing:1.5px;margin-bottom:4px;}
.ftr-slogan{font-size:12px;color:var(--tl);font-style:italic;}
.back{display:inline-block;margin-top:14px;font-size:13px;color:var(--gold2);text-decoration:none;}
"""

GATE_CSS = """
#gate{position:fixed;inset:0;background:linear-gradient(160deg,var(--navy),var(--navy2));display:flex;align-items:center;justify-content:center;z-index:9999;padding:24px;}
#gate .box{background:#fff;border-radius:18px;padding:30px 26px;max-width:340px;width:100%;text-align:center;}
#gate h3{color:var(--navy);font-size:18px;margin-bottom:6px;}
#gate p{font-size:13px;color:#888;margin-bottom:18px;}
#gate input{width:100%;border:1.5px solid #d8e0ec;border-radius:10px;font-size:18px;text-align:center;letter-spacing:6px;padding:12px;margin-bottom:12px;font-family:inherit;}
#gate button{width:100%;background:var(--navy);color:#fff;border:none;border-radius:10px;padding:12px;font-size:15px;font-weight:700;font-family:inherit;cursor:pointer;}
#gate .err{color:#c0392b;font-size:13px;height:18px;margin-top:8px;}
"""

def card(b, latest):
    lc = ' latest' if latest else ''
    badge = '<span class="latest-badge">최신</span>' if latest else ''
    meta = ' · '.join(p for p in ([b['title']] + (['(이전 노트)'] if b['legacy'] else [])) if p) or '주일학교 노트'
    return f'''    <a href="{b['file']}" class="card{lc}">
      <div class="card-icon">🧒</div>
      <div class="card-body"><div class="card-date">{b['display']}</div><div class="card-meta">{meta}</div></div>
      {badge}<span class="card-arrow">›</span>
    </a>'''

def note_list_html(items):
    if not items:
        return '  <div class="empty">아직 등록된 노트가 없습니다.</div>'
    grouped = {}
    for b in items:
        y = b['date'][:4]; mo = int(b['date'][5:7])
        grouped.setdefault(y, {}).setdefault(mo, []).append(b)
    out, idx = '', 0
    for y in sorted(grouped, reverse=True):
        out += f'  <div class="year-label">{y}년</div>\n'
        for mo in sorted(grouped[y], reverse=True):
            out += f'  <div class="month-label">{mo}월</div>\n'
            for b in grouped[y][mo]:
                out += card(b, idx == 0) + '\n'; idx += 1
    return out

def write_room(role, pw, icon, room_name):
    items = scan_room(role)
    sections = note_list_html(items)
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<title>대구우리교회 주일학교 | {room_name}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@600;700&family=Noto+Sans+KR:wght@400;500;600&display=swap" rel="stylesheet">
<style>{BASE_CSS}{GATE_CSS}</style>
</head>
<body>
<div id="gate"><div class="box">
  <h3>{icon} {room_name}</h3>
  <p>암호를 입력해 주세요</p>
  <input id="gate-pw" type="password" inputmode="numeric" maxlength="8" placeholder="••••">
  <button onclick="tryGate()">들어가기</button>
  <div class="err" id="gate-err"></div>
</div></div>
<header class="hdr"><div class="hdr-inner">
  <span class="kid">{icon}</span>
  <div class="name">{room_name}</div>
  <div class="sub">대구우리교회 주일학교 · 초등부</div>
  <div class="divx"></div>
  <div class="desc">원하는 날짜를 선택하세요</div>
  <a class="back" href="../index.html">← 주일학교 입구로</a>
</div></header>
<main class="main">
{sections}
</main>
<footer class="ftr"><div class="ftr-name">대구우리교회 주일학교</div><div class="ftr-slogan">바른신학 · 바른교회 · 바른생활</div></footer>
<script>
const PW="{pw}", ROLE="{role}";
function tryGate(){{
  if(document.getElementById('gate-pw').value.trim()===PW){{ sessionStorage.setItem('kids_role',ROLE); document.getElementById('gate').style.display='none'; }}
  else {{ document.getElementById('gate-err').textContent='암호가 맞지 않습니다.'; }}
}}
document.getElementById('gate-pw').addEventListener('keydown',e=>{{ if(e.key==='Enter') tryGate(); }});
if(sessionStorage.getItem('kids_role')===ROLE){{ document.getElementById('gate').style.display='none'; }}
</script>
</body>
</html>'''
    os.makedirs(os.path.join(KIDS_DIR, role), exist_ok=True)
    with open(os.path.join(KIDS_DIR, role, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'  kids/{role}/index.html — {len(items)} note(s)')

def write_landing():
    html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<title>대구우리교회 주일학교 | 입구</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@600;700&family=Noto+Sans+KR:wght@400;500;600&display=swap" rel="stylesheet">
<style>{BASE_CSS}
.room{{display:flex;align-items:center;gap:16px;background:#fff;border-radius:16px;padding:22px 20px;margin-bottom:14px;text-decoration:none;color:inherit;box-shadow:0 1px 8px rgba(26,44,78,.08);border:1.5px solid transparent;}}
.room:active{{border-color:var(--gold);}}
.room .ic{{width:54px;height:54px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-size:28px;flex-shrink:0;background:linear-gradient(135deg,var(--navy),var(--navy2));}}
.room.t .ic{{background:linear-gradient(135deg,var(--gold),var(--gold2));}}
.room .tt{{font-size:17px;font-weight:700;}}
.room .ds{{font-size:13px;color:var(--tl);margin-top:3px;}}
.room .ar{{margin-left:auto;color:var(--border);font-size:20px;}}
.lockmsg{{text-align:center;font-size:12px;color:var(--tl);margin-top:6px;}}
</style>
</head>
<body>
<header class="hdr"><div class="hdr-inner">
  <span class="kid">🧒</span>
  <div class="name">대구우리교회 주일학교</div>
  <div class="sub">초등부</div>
  <div class="divx"></div>
  <div class="desc">들어갈 방을 선택하세요</div>
  <a class="back" href="../index.html">← 어른 말씀 동반자로</a>
</div></header>
<main class="main">
  <a class="room s" href="student/"><div class="ic">🧒</div><div><div class="tt">학생용 방</div><div class="ds">노트 읽기 · 활동지 직접 쓰기 · 기도제목/질문 보내기</div></div><span class="ar">›</span></a>
  <a class="room t" href="teacher/"><div class="ic">🧑‍🏫</div><div><div class="tt">교사용 방</div><div class="ds">교사 가이드·정답 · 제출된 활동지 확인 · 소통 답장</div></div><span class="ar">›</span></a>
  <div class="lockmsg">🔒 각 방은 암호로 보호됩니다</div>
</main>
<footer class="ftr"><div class="ftr-name">대구우리교회 주일학교</div><div class="ftr-slogan">바른신학 · 바른교회 · 바른생활</div></footer>
</body>
</html>'''
    with open(os.path.join(KIDS_DIR, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print('  kids/index.html (landing)')

def generate():
    write_landing()
    write_room('student', '3230', '🧒', '학생용 방')
    write_room('teacher', '4341', '🧑\u200d🏫', '교사용 방')
    print('OK: 주일학교 인덱스 생성 완료')

if __name__ == '__main__':
    generate()
