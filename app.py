""" 
박사 일정 리드 앱
- 학위논문 + 학술논문 시점별 완성을 돕는 자기주도 관리 도구
- 일반 To-do 앱과 달리, 박사 진행의 맥락(단계·마일스톤)을 알고 있음
"""

import streamlit as st
import json
import os
from datetime import date, datetime

# ============================================================
# 1. 박사 맥락 (한 번만 박아두는 정보)
# ============================================================
DISSERTATION = {
    "title": "AI융합교육 환경에서 생체정보 AI 필터링이 개인정보보호와 AI윤리의식에 미치는 효과",
    "graduation": "2027-08-31",
    "defense": "2027-04-30",
    "dependent_vars": ["개인정보보호", "AI윤리의식"],
}

# 마일스톤 + 각 마일스톤 아래 할 일 묶음 (초안)
DEFAULT_MILESTONES = [
    {"id": "M1", "name": "분석 단계 착수", "period": "2026.6~7",
     "deadline": "2026-07-31", "phase": "분석", "tasks": [
        "교수님과 큰 방향 합의 (제목·종속변인·일정)",
        "메타분석 문헌 찾기 (RISS/DBpia)",
        "AI 윤리 교육 항목 정리 (A1~A8 다듬기)",
        "보리치 설문 문항 초안 만들기",
        "선행연구 정리 (2장 재료)",
     ]},
    {"id": "M2", "name": "여름방학 · 설계+개발 집중", "period": "2026.7~8",
     "deadline": "2026-08-31", "phase": "설계+개발", "tasks": [
        "보리치/Locus 요구도 조사 실시",
        "요인분석·AHP 설계요소 도출",
        "채팅+마스킹 합친 도구 만들기",
        "로컬AI 프롬프트 튜닝 정교화",
        "원본 자동 삭제 기능 추가",
        "홍채 정밀 마스킹 (MediaPipe)",
     ]},
    {"id": "M3", "name": "소논문 1 투고", "period": "2026 가을",
     "deadline": "2026-10-31", "phase": "소논문", "tasks": [
        "소논문 1 주제 확정 (교수님과)",
        "소논문 1 초안 쓰기",
        "교수님 피드백 받고 수정",
        "KCI 학술지 선정 + 투고",
     ]},
    {"id": "M4", "name": "2학기 · 검토 + 1·2장 집필", "period": "2026.9~12",
     "deadline": "2026-12-31", "phase": "검토+집필", "tasks": [
        "전문가 타당성 검토 (CVI)",
        "IRB 승인 준비·신청",
        "도구 개선 (검토 반영)",
        "박사논문 1장(서론) 쓰기",
        "박사논문 2장(이론적 배경) 쓰기",
     ]},
    {"id": "M5", "name": "겨울방학 · 적용 준비 + 3장", "period": "2027.1~2",
     "deadline": "2027-02-28", "phase": "준비+집필", "tasks": [
        "효과 측정도구 확정 (척도 선정)",
        "현장 적용 계획 수립",
        "도구 최종 점검",
        "박사논문 3장(연구방법) 쓰기",
     ]},
    {"id": "M6", "name": "소논문 2 투고", "period": "2027 봄",
     "deadline": "2027-03-31", "phase": "소논문", "tasks": [
        "소논문 2 주제 확정 (설계·개발편)",
        "소논문 2 초안 쓰기",
        "교수님 피드백·수정",
        "KCI 투고",
     ]},
    {"id": "M7", "name": "1학기 · 현장 적용", "period": "2027.3~6",
     "deadline": "2027-06-30", "phase": "적용", "tasks": [
        "1차시 적용 + 데이터 수집",
        "중간 결과 분석",
        "적용 마무리 + 사후 검사",
        "박사논문 4장(결과) 쓰기 시작",
     ]},
    {"id": "M8", "name": "심사", "period": "2027.4",
     "deadline": "2027-04-30", "phase": "심사", "tasks": [
        "심사 발표자료 준비",
        "박사논문 초고 정리",
        "심사",
     ]},
    {"id": "M9", "name": "최종본 완성", "period": "2027.6~7",
     "deadline": "2027-07-31", "phase": "마무리", "tasks": [
        "심사 의견 반영",
        "4장 결과 채우기",
        "5장 논의·결론 쓰기",
        "전체 다듬기",
     ]},
    {"id": "M10", "name": "🎓 졸업", "period": "2027.8",
     "deadline": "2027-08-31", "phase": "졸업", "tasks": []},
]

# ============================================================
# 2. 데이터 저장 (컴퓨터에 작은 파일로 남기기)
# ============================================================
DATA_FILE = "phd_data.json"

def load_data():
    """저장된 데이터 불러오기. 없으면 초기값."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # 초기 데이터: 마일스톤별 할 일을 "미완료"로 다 풀어놓기
    initial = {"todos": [], "today_tasks": []}
    for m in DEFAULT_MILESTONES:
        for t in m["tasks"]:
            initial["todos"].append({
                "milestone_id": m["id"],
                "milestone_name": m["name"],
                "task": t,
                "done": False,
            })
    return initial

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ============================================================
# 3. 화면 그리기
# ============================================================
st.set_page_config(page_title="박사 일정 리드", layout="wide")
st.title("🎓 박사 일정 리드")
st.caption(f"_{DISSERTATION['title']}_")

data = load_data()
today = date.today()

# --- 상단: 큰 그림 (현재 위치) ---
defense_date = datetime.strptime(DISSERTATION["defense"], "%Y-%m-%d").date()
grad_date = datetime.strptime(DISSERTATION["graduation"], "%Y-%m-%d").date()
days_to_defense = (defense_date - today).days
days_to_grad = (grad_date - today).days

# 현재 마일스톤 찾기 (오늘 날짜가 어느 마일스톤 마감 전에 있는지)
current_milestone = None
for m in DEFAULT_MILESTONES:
    m_deadline = datetime.strptime(m["deadline"], "%Y-%m-%d").date()
    if today <= m_deadline:
        current_milestone = m
        break

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("심사까지", f"{days_to_defense}일")
with col2:
    st.metric("졸업까지", f"{days_to_grad}일")
with col3:
    st.metric("현재 단계", current_milestone["phase"] if current_milestone else "—")

if current_milestone:
    st.info(f"📍 지금 진행 중: **{current_milestone['name']}** ({current_milestone['period']}) — 마감 {current_milestone['deadline']}")

st.divider()

# --- 2단 레이아웃: 왼쪽 오늘 할 일, 오른쪽 큰 그림 ---
left, right = st.columns([1, 1])

# === 왼쪽: 오늘 할 일 ===
with left:
    st.subheader("✅ 오늘 할 일")
    
    # 오늘 할 일 표시·체크
    if data["today_tasks"]:
        for i, t in enumerate(data["today_tasks"]):
            cols = st.columns([0.1, 0.8, 0.1])
            with cols[0]:
                checked = st.checkbox("", value=t["done"], key=f"today_{i}")
                if checked != t["done"]:
                    data["today_tasks"][i]["done"] = checked
                    save_data(data)
                    st.rerun()
            with cols[1]:
                style = "~~" if t["done"] else ""
                st.write(f"{style}{t['task']}{style}")
                st.caption(f"_{t.get('milestone_name', '')}_")
            with cols[2]:
                if st.button("✕", key=f"del_today_{i}"):
                    data["today_tasks"].pop(i)
                    save_data(data)
                    st.rerun()
    else:
        st.caption("오른쪽에서 마일스톤 할 일을 끌어와 오늘의 일을 채우세요.")
    
    st.divider()
    st.markdown("**➕ 직접 추가하기**")
    new_task = st.text_input("새 할 일", key="new_today")
    if st.button("추가", key="add_today"):
        if new_task.strip():
            data["today_tasks"].append({
                "task": new_task.strip(),
                "milestone_name": "(직접 추가)",
                "done": False,
            })
            save_data(data)
            st.rerun()

# === 오른쪽: 마일스톤별 할 일 묶음 ===
with right:
    st.subheader("🗂️ 마일스톤별 할 일 묶음")
    st.caption("아래 '오늘로'를 누르면 왼쪽 오늘 할 일로 옮겨집니다.")
    
    for m in DEFAULT_MILESTONES:
        # 이 마일스톤의 할 일들
        m_todos = [t for t in data["todos"] if t["milestone_id"] == m["id"]]
        if not m_todos and not m["tasks"]:
            continue
        
        # 진척도 계산
        if m_todos:
            done_count = sum(1 for t in m_todos if t["done"])
            total = len(m_todos)
            progress = done_count / total if total > 0 else 0
        else:
            done_count, total, progress = 0, 0, 0
        
        # 마일스톤 헤더
        is_current = (current_milestone and m["id"] == current_milestone["id"])
        marker = "📍 " if is_current else ""
        with st.expander(f"{marker}**{m['id']}. {m['name']}** ({m['period']}) — {done_count}/{total}", expanded=is_current):
            if total > 0:
                st.progress(progress)
            st.caption(f"마감: {m['deadline']}")
            
            for i, t in enumerate(m_todos):
                cols = st.columns([0.1, 0.7, 0.2])
                with cols[0]:
                    checked = st.checkbox("", value=t["done"], key=f"m_{m['id']}_{i}")
                    if checked != t["done"]:
                        # 전체 todos에서 찾아 업데이트
                        for j, full_t in enumerate(data["todos"]):
                            if full_t == t:
                                data["todos"][j]["done"] = checked
                                break
                        save_data(data)
                        st.rerun()
                with cols[1]:
                    style = "~~" if t["done"] else ""
                    st.write(f"{style}{t['task']}{style}")
                with cols[2]:
                    if not t["done"] and st.button("오늘로", key=f"to_today_{m['id']}_{i}"):
                        # 오늘 할 일에 복사 (중복 방지)
                        already = any(tt["task"] == t["task"] for tt in data["today_tasks"])
                        if not already:
                            data["today_tasks"].append({
                                "task": t["task"],
                                "milestone_name": m["name"],
                                "done": False,
                            })
                            save_data(data)
                            st.rerun()

st.divider()
st.caption("💾 모든 변경사항은 phd_data.json에 자동 저장됩니다. 컴퓨터를 꺼도 남아요.")
