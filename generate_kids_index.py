"""
generate_kids_index.py — 대구우리교회 주일학교 인덱스 생성기
  kids/index.html              ← 입구 (학생용 방 / 교사용 방)
  kids/student/index.html      ← 학생 방 (개인 로그인: 이름 + 고유 4자리 번호)
  kids/teacher/index.html      ← 교사 방 (암호 4341)
  kids/{student|teacher}/YYYY-MM-DD.html ← 주차 노트
레거시: kids/YYYY-MM-DD-kids.html → 학생 방 목록에 '(이전)' 표시
"""
import os, re

KIDS_DIR = "kids"
NOTE_PAT = re.compile(r'^(\d{4})-(\d{2})-(\d{2})\.html$')
LEGACY_PAT = re.compile(r'^(\d{4})-(\d{2})-(\d{2})-kids\.html$')

FIREBASE_JS = """const FIREBASE_CONFIG={apiKey:"AIzaSyCFIs7e7z8t2nzsgHSwcX72COjzBNTJz_s",authDomain:"daegu-woorinote.firebaseapp.com",projectId:"daegu-woorinote",storageBucket:"daegu-woorinote.firebasestorage.app",messagingSenderId:"1047053636423",appId:"1:1047053636423:web:9dfcad4b55678879403262"};
let DB=null,fbReady=false;try{firebase.initializeApp(FIREBASE_CONFIG);DB=firebase.firestore();fbReady=true;}catch(e){console.warn(e);}"""

def title_of(path):
    try:
        c = open(path, encoding='utf-8').read()
        m = re.search(r'<title>[^|]+\|\s*([^<]+)</title>', c)
        if m: return m.group(1).strip()
    except Exception: pass
    return ''

def scan_room(role):
    items, d = [], os.path.join(KIDS_DIR, role)
    if os.path.isdir(d):
        for fn in os.listdir(d):
            m = NOTE_PAT.match(fn)
            if not m: continue
            y, mo, da = m.groups()
            items.append({'file': fn, 'date': f'{y}-{mo}-{da}', 'legacy': False,
                          'display': f'{y}년 {int(mo)}월 {int(da)}일', 'title': title_of(os.path.join(d, fn))})
    if role == 'student':
        for fn in os.listdir(KIDS_DIR):
            m = LEGACY_PAT.match(fn)
            if not m: continue
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
.hdr-inner{padding:30px 20px 26px;}
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
#gate{position:fixed;inset:0;background:linear-gradient(160deg,var(--navy),var(--navy2));display:flex;align-items:center;justify-content:center;z-index:9999;padding:24px;}
#gate .box{background:#fff;border-radius:18px;padding:30px 26px;max-width:340px;width:100%;text-align:center;}
#gate h3{color:var(--navy);font-size:18px;margin-bottom:4px;}
#gate .hint{font-size:12px;color:#888;margin-bottom:16px;line-height:1.6;}
#gate input{width:100%;border:1.5px solid #d8e0ec;border-radius:10px;font-size:17px;text-align:center;padding:12px;margin-bottom:10px;font-family:inherit;}
#gate button{width:100%;background:var(--navy);color:#fff;border:none;border-radius:10px;padding:12px;font-size:15px;font-weight:700;font-family:inherit;cursor:pointer;}
#gate .err{color:#c0392b;font-size:13px;min-height:18px;margin-top:8px;}
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
        grouped.setdefault(b['date'][:4], {}).setdefault(int(b['date'][5:7]), []).append(b)
    out, idx = '', 0
    for y in sorted(grouped, reverse=True):
        out += f'  <div class="year-label">{y}년</div>\n'
        for mo in sorted(grouped[y], reverse=True):
            out += f'  <div class="month-label">{mo}월</div>\n'
            for b in grouped[y][mo]:
                out += card(b, idx == 0) + '\n'; idx += 1
    return out

def shell(title, gate_html, body, extra_head='', script=''):
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@600;700&family=Noto+Sans+KR:wght@400;500;600&display=swap" rel="stylesheet">
{extra_head}
<style>{BASE_CSS}</style>
</head>
<body>
{gate_html}
{body}
<footer class="ftr"><div class="ftr-name">대구우리교회 주일학교</div><div class="ftr-slogan">바른신학 · 바른교회 · 바른생활</div></footer>
<script>{script}</script>
</body>
</html>'''

def write_student_room():
    items = scan_room('student')
    body = f'''<header class="hdr"><div class="hdr-inner">
  <span class="kid">🧒</span><div class="name">학생용 방</div>
  <div class="sub">대구우리교회 주일학교 · 초등부</div><div class="divx"></div>
  <div class="desc">원하는 날짜를 선택하세요</div>
  <a class="back" href="../index.html">← 주일학교 입구로</a>
</div></header>
<main class="main">
{note_list_html(items)}
</main>'''
    gate = '''<div id="gate"><div class="box">
  <h3>🧒 학생용 방</h3>
  <div class="hint">내 이름과 나만의 4자리 번호로 들어가요.<br>처음이면 번호를 새로 정하고, 다음부터 같은 번호로 들어오면 돼요.</div>
  <input id="g-name" type="text" placeholder="이름" autocomplete="off">
  <input id="g-num" type="password" inputmode="numeric" maxlength="4" placeholder="번호 4자리" style="letter-spacing:8px">
  <button onclick="doLogin()">들어가기</button>
  <div class="err" id="g-err"></div>
</div></div>'''
    head = '''<script src="https://www.gstatic.com/firebasejs/9.23.0/firebase-app-compat.js"></script>
<script src="https://www.gstatic.com/firebasejs/9.23.0/firebase-firestore-compat.js"></script>'''
    script = FIREBASE_JS + '''
function rosterRef(num){return DB.collection('sermons').doc('kids-roster').collection('students').doc(num);}
function gerr(t){document.getElementById('g-err').textContent=t||'';}
async function doLogin(){
  const name=document.getElementById('g-name').value.trim();
  const num=document.getElementById('g-num').value.trim();
  if(!name){gerr('이름을 적어 주세요.');return;}
  if(!/^\\d{4}$/.test(num)){gerr('번호 4자리를 정확히 입력해 주세요.');return;}
  if(!fbReady){gerr('서버 연결을 확인해 주세요.');return;}
  gerr('확인 중...');
  try{
    const snap=await rosterRef(num).get();
    if(snap.exists){
      if((snap.data().name||'').trim()!==name){gerr('이 번호는 다른 친구가 쓰고 있어요. 다른 번호를 정해 주세요.');return;}
    }else{
      await rosterRef(num).set({name:name,createdAt:firebase.firestore.FieldValue.serverTimestamp()});
    }
    sessionStorage.setItem('kids_role','student');sessionStorage.setItem('kids_num',num);sessionStorage.setItem('kids_name',name);
    try{localStorage.setItem('kids_num',num);localStorage.setItem('kids_name',name);}catch(e){}
    document.getElementById('gate').style.display='none';
  }catch(e){gerr('처리 중 오류가 발생했어요.');console.error(e);}
}
(function(){
  if(sessionStorage.getItem('kids_role')==='student'&&sessionStorage.getItem('kids_num')){document.getElementById('gate').style.display='none';return;}
  const n=localStorage.getItem('kids_name'),m=localStorage.getItem('kids_num');
  if(n)document.getElementById('g-name').value=n; if(m)document.getElementById('g-num').value=m;
})();
document.getElementById('g-num').addEventListener('keydown',e=>{if(e.key==='Enter')doLogin();});'''
    html = shell('대구우리교회 주일학교 | 학생용 방', gate, body, head, script)
    os.makedirs(os.path.join(KIDS_DIR, 'student'), exist_ok=True)
    open(os.path.join(KIDS_DIR, 'student', 'index.html'), 'w', encoding='utf-8').write(html)
    print(f'  kids/student/index.html — {len(items)} note(s) [개인 로그인]')

def write_teacher_room():
    items = scan_room('teacher')
    body = f'''<header class="hdr"><div class="hdr-inner">
  <span class="kid">🧑\u200d🏫</span><div class="name">교사용 방</div>
  <div class="sub">대구우리교회 주일학교 · 초등부</div><div class="divx"></div>
  <div class="desc">원하는 날짜를 선택하세요</div>
  <a class="back" href="../index.html">← 주일학교 입구로</a>
</div></header>
<main class="main">
{note_list_html(items)}
</main>'''
    gate = '''<div id="gate"><div class="box">
  <h3>🧑‍🏫 교사용 방</h3>
  <div class="hint">교사 암호를 입력해 주세요</div>
  <input id="g-pw" type="password" inputmode="numeric" maxlength="8" placeholder="암호" style="letter-spacing:6px">
  <button onclick="tryGate()">들어가기</button>
  <div class="err" id="g-err"></div>
</div></div>'''
    script = '''const PW="4341";
function tryGate(){
  if(document.getElementById('g-pw').value.trim()===PW){sessionStorage.setItem('kids_role','teacher');document.getElementById('gate').style.display='none';}
  else{document.getElementById('g-err').textContent='암호가 맞지 않습니다.';}
}
document.getElementById('g-pw').addEventListener('keydown',e=>{if(e.key==='Enter')tryGate();});
if(sessionStorage.getItem('kids_role')==='teacher'){document.getElementById('gate').style.display='none';}'''
    html = shell('대구우리교회 주일학교 | 교사용 방', gate, body, '', script)
    os.makedirs(os.path.join(KIDS_DIR, 'teacher'), exist_ok=True)
    open(os.path.join(KIDS_DIR, 'teacher', 'index.html'), 'w', encoding='utf-8').write(html)
    print(f'  kids/teacher/index.html — {len(items)} note(s) [암호 4341]')

def write_landing():
    body = '''<header class="hdr"><div class="hdr-inner">
  <span class="kid">🧒</span><div class="name">대구우리교회 주일학교</div>
  <div class="sub">초등부</div><div class="divx"></div>
  <div class="desc">들어갈 방을 선택하세요</div>
  <a class="back" href="../index.html">← 어른 말씀 동반자로</a>
</div></header>
<main class="main">
  <a class="card" href="student/"><div class="card-icon">🧒</div><div class="card-body"><div class="card-date">학생용 방</div><div class="card-meta">노트 · 활동지 직접 쓰기 · 기도제목/질문</div></div><span class="card-arrow">›</span></a>
  <a class="card" href="teacher/"><div class="card-icon" style="background:linear-gradient(135deg,var(--gold),var(--gold2))">🧑‍🏫</div><div class="card-body"><div class="card-date">교사용 방</div><div class="card-meta">가이드·정답 · 제출 활동지 · 소통 답장</div></div><span class="card-arrow">›</span></a>
  <div style="text-align:center;font-size:12px;color:var(--tl);margin-top:8px">🔒 각 방은 로그인/암호로 보호됩니다</div>
</main>'''
    html = shell('대구우리교회 주일학교 | 입구', '', body)
    open(os.path.join(KIDS_DIR, 'index.html'), 'w', encoding='utf-8').write(html)
    print('  kids/index.html (입구)')

def generate():
    write_landing(); write_student_room(); write_teacher_room()
    print('OK: 주일학교 인덱스 생성 완료')

if __name__ == '__main__':
    generate()
