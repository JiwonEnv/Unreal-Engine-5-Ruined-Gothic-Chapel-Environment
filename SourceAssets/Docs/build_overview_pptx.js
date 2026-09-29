const pptxgen = require("pptxgenjs");
const path = require("path");

const ROOT = "E:/2026_MBC/UE5_GothicChapel";
const IMG_EXT = path.join(ROOT, "SourceAssets/Blockout/Blockout_Exterior.png");
const IMG_INT = path.join(ROOT, "SourceAssets/Blockout/Blockout_Interior.png");
const OUT = process.env.OUT_PPTX || path.join(ROOT, "SourceAssets/Docs/GothicChapel_Project_Overview_v2.pptx");

// Palette: weathered slate + limestone, stained-glass teal, candle amber
const C = {
  slate: "24262A", slate2: "33363C", stone: "F4F1EC", stoneDk: "E4DED4",
  ink: "2A2A2A", muted: "6B6862", teal: "2F6F73", amber: "C08A3E", white: "FFFFFF",
  ruin: "8C5A4A", partial: "B89B6A", line: "D6D0C6", paleTeal: "DCE8E8",
};
const F = "Malgun Gothic";
const FH = "Cambria";

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625
pres.title = "UE5 Ruined Gothic Chapel — 프로젝트 개요";
pres.author = "Jiwon Lee";

const T = (slide, text, o) => slide.addText(text, { fontFace: F, isTextBox: true, ...o });
const title = (s, t, sub, dark = false) => {
  T(s, t, { x: 0.5, y: 0.35, w: 9, h: 0.6, fontSize: 28, bold: true, color: dark ? C.white : C.ink, margin: 0 });
  if (sub) T(s, sub, { x: 0.5, y: 0.95, w: 9, h: 0.35, fontSize: 12, color: dark ? "B8B4AC" : C.muted, margin: 0 });
};
let pageNo = 0;
const num = (s, dark = false) =>
  T(s, String(++pageNo).padStart(2, "0"), { x: 9.0, y: 5.2, w: 0.6, h: 0.3, fontSize: 9, color: dark ? "8A867F" : "A9A49B", align: "right", margin: 0 });
const shadow = () => ({ type: "outer", color: "000000", blur: 6, offset: 1.5, angle: 90, opacity: 0.12 });
const card = (s, x, y, w, h, fill = C.white, sh = true) =>
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, fill: { color: fill }, line: { type: "none" }, rectRadius: 0.08, ...(sh ? { shadow: shadow() } : {}) });
const bullets = (lines, extra = {}) => lines.map((t, i) => ({ text: t, options: { bullet: { indent: 14 }, breakLine: i < lines.length - 1, ...extra } }));
const badge = (s, x, y, n, fill = C.teal, color = C.white, d = 0.32) => {
  s.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { type: "none" } });
  T(s, String(n), { x, y, w: d, h: d, fontSize: 11, bold: true, color, align: "center", valign: "middle", margin: 0 });
};
const newSlide = (bg = C.stone) => { const s = pres.addSlide(); s.background = { color: bg }; return s; };


// Case template: 시도 → 발견한 문제 → 해결·계획
const caseSlide = (no, head, sub, status, cols, note, heads) => {
  const s = newSlide();
  T(s, "CASE " + String(no).padStart(2, "0"), { x: 0.5, y: 0.3, w: 2, h: 0.3, fontSize: 11, bold: true, color: C.amber, charSpacing: 1.5, margin: 0 });
  T(s, head, { x: 0.5, y: 0.6, w: 7.4, h: 0.6, fontSize: 26, bold: true, color: C.ink, margin: 0 });
  T(s, sub, { x: 0.5, y: 1.18, w: 8, h: 0.32, fontSize: 12, color: C.muted, margin: 0 });
  const done = status.startsWith("해결");
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.1, y: 0.65, w: 1.4, h: 0.4, fill: { color: done ? C.teal : C.white }, line: done ? { type: "none" } : { color: C.amber, width: 1.25 }, rectRadius: 0.2 });
  T(s, status, { x: 8.1, y: 0.65, w: 1.4, h: 0.4, fontSize: 11, bold: true, color: done ? C.white : C.amber, align: "center", valign: "middle", margin: 0 });
  const hh = heads || ["시도", "발견한 문제", "해결 · 계획"];
  const labels = [[hh[0], C.teal], [hh[1], C.ruin], [hh[2], C.amber]];
  cols.forEach((lines, i) => {
    const x = 0.5 + i * 3.05, dark = i === 2;
    card(s, x, 1.75, 2.8, 3.1, dark ? C.slate : C.white);
    T(s, labels[i][0], { x: x + 0.25, y: 1.92, w: 2.3, h: 0.35, fontSize: 14, bold: true, color: labels[i][1], margin: 0 });
    T(s, bullets(lines), { x: x + 0.25, y: 2.4, w: 2.35, h: 2.45, fontSize: 11.5, color: dark ? C.white : C.ink, paraSpaceAfter: 6, margin: 0, valign: "top" });
    if (i < 2) s.addShape(pres.shapes.LINE, { x: x + 2.82, y: 3.35, w: 0.21, h: 0, line: { color: C.muted, width: 1.25, endArrowType: "triangle" } });
  });
  if (note) T(s, note, { x: 0.5, y: 5.05, w: 8.4, h: 0.3, fontSize: 9.5, color: C.muted, margin: 0 });
  num(s);
};

// ---------- 1. Title ----------
{
  const s = newSlide(C.slate);
  s.addImage({ path: IMG_EXT, x: 4.2, y: 0, w: 5.8, h: 5.625, sizing: { type: "cover", w: 5.8, h: 5.625 } });
  s.addShape(pres.shapes.RECTANGLE, { x: 4.2, y: 0, w: 5.8, h: 5.625, fill: { color: C.slate, transparency: 70 }, line: { type: "none" } });
  T(s, "UE 5.6  ·  ENVIRONMENT ART", { x: 0.5, y: 1.2, w: 3.6, h: 0.3, fontSize: 10, color: C.amber, bold: true, charSpacing: 1.5, margin: 0 });
  T(s, "Ruined Gothic\nChapel", { x: 0.5, y: 1.6, w: 3.8, h: 1.5, fontFace: FH, fontSize: 40, bold: true, color: C.white, margin: 0, lineSpacingMultiple: 0.9 });
  T(s, "서쪽부터 무너져 내린 13–14세기 영국계 고딕 석조 예배당", { x: 0.5, y: 3.2, w: 3.5, h: 0.7, fontSize: 13, color: "D9D4CB", margin: 0 });
  T(s, "3D Environment Artist Portfolio  |  이지원", { x: 0.5, y: 4.8, w: 3.6, h: 0.3, fontSize: 10, color: "8A867F", margin: 0 });
  pageNo++;
}

// ---------- 2. Overview: purpose + stats ----------
{
  const s = newSlide();
  title(s, "프로젝트 개요", "Unreal을 처음부터 학습하며, 3인칭 플레이 기준으로 검증하는 환경 아트 포트폴리오");
  const stats = [["6 × 12m", "내부 규모"], ["3 Bay", "측랑 없는 단일 본당"], ["4 × 6m", "1 Bay 규격"], ["UE 5.6.1", "Lumen · Nanite"]];
  stats.forEach(([v, l], i) => {
    const x = 0.5 + i * 2.3;
    card(s, x, 1.55, 2.05, 1.3);
    T(s, v, { x, y: 1.68, w: 2.05, h: 0.7, fontFace: FH, fontSize: 28, bold: true, color: C.teal, align: "center", margin: 0 });
    T(s, l, { x, y: 2.38, w: 2.05, h: 0.35, fontSize: 12, color: C.muted, align: "center", margin: 0 });
  });
  const rows = [
    ["설정", "외딴 언덕 위, 전쟁 또는 재난으로 서쪽부터 무너진 뒤 오랜 세월 방치된 소규모 석조 예배당"],
    ["검증", "렌더 장면에 그치지 않고 3인칭 캐릭터로 스케일·이동 동선·시선 유도를 확인"],
    ["증명", "Hero Asset · 모듈러 키트 · PBR · 파손/방치 흔적 · Bay 생성 시스템 · Lumen · 최적화"],
    ["출력", "최종 이미지 3–5장 · 생성 시스템 작동 영상 · 모델링/재질/기술 Breakdown"],
  ];
  rows.forEach(([k, v], i) => {
    const y = 3.15 + i * 0.5;
    T(s, k, { x: 0.5, y, w: 1.0, h: 0.42, fontSize: 13, bold: true, color: C.teal, margin: 0, valign: "middle" });
    T(s, v, { x: 1.5, y, w: 8.0, h: 0.42, fontSize: 13, color: C.ink, margin: 0, valign: "middle" });
  });
  num(s);
}


// ---------- Intent ----------
{
  const s = newSlide();
  title(s, "제작 의도", "무엇을 증명하고 싶은가 — 세 가지 기준으로 모든 판단을 내린다");
  const its = [
    ["건물이 주인공", "소품을 늘려 이야기하지 않는다. 남은 건축 구조·재질의 노후화·붕괴 양상 자체가 공간의 서사를 전달하도록 설계한다.", "소품은 제단·건축 실루엣보다 먼저 읽히지 않게"],
    ["플레이 가능한 공간", "렌더 한 장을 위한 세트가 아니라, 3인칭 캐릭터로 걸었을 때 스케일·동선·시선 유도가 성립하는 게임 배경을 만든다.", "180cm 캐릭터 · 0.5m Grid · 입구→제단 동선"],
    ["학습과 제작 병행", "Unreal을 처음부터 학습하며 필요한 STEP을 바로 적용한다. 이전 Unity 건물 생성 시스템의 설계 원리를 Unreal 방식으로 재설계한다.", "모듈러 · Hero · PBR · 생성 시스템 · Lumen"],
  ];
  its.forEach(([h, d, k], i) => {
    const x = 0.5 + i * 3.05;
    card(s, x, 1.55, 2.85, 3.5);
    badge(s, x + 0.25, 1.8, i + 1, C.teal, C.white, 0.4);
    T(s, h, { x: x + 0.25, y: 2.35, w: 2.4, h: 0.4, fontSize: 16, bold: true, color: C.ink, margin: 0 });
    T(s, d, { x: x + 0.25, y: 2.85, w: 2.4, h: 1.45, fontSize: 11.5, color: C.muted, margin: 0, valign: "top" });
    s.addShape(pres.shapes.LINE, { x: x + 0.25, y: 4.35, w: 2.35, h: 0, line: { color: C.line, width: 0.75 } });
    T(s, k, { x: x + 0.25, y: 4.42, w: 2.4, h: 0.5, fontSize: 10, bold: true, color: C.teal, margin: 0, valign: "top" });
  });
  num(s);
}

// ---------- 3. Concept & game references ----------
{
  const s = newSlide();
  title(s, "콘셉트 & 게임 레퍼런스", "형태는 직접 차용하지 않고, 레퍼런스마다 적용할 기준을 하나씩 정함");
  card(s, 0.5, 1.5, 3.0, 3.6, C.slate, false);
  T(s, "ONE-LINE CONCEPT", { x: 0.75, y: 1.7, w: 2.5, h: 0.3, fontSize: 10, bold: true, color: C.amber, charSpacing: 1, margin: 0 });
  T(s, "오랜 세월 풍화되고 서쪽부터 무너진 13–14세기 영국계 고딕 석조 예배당.\n\n남은 구조와 재질의 시간감이 동쪽 제단으로 시선을 이끈다.",
    { x: 0.75, y: 2.1, w: 2.55, h: 2.8, fontSize: 13, color: C.white, margin: 0, valign: "top" });
  const refs = [
    ["Demon’s Souls Remake", "성탁 형태 메인 — 두꺼운 석조 매스·단차·블라인드 아케이드"],
    ["Elden Ring", "동쪽 제단 Bay 배치 — Hero 창 중심축과 좌우 통로 여백"],
    ["Dark Souls III", "붕괴 이후 제단 주변 연출 — 촛대·천은 최소 수량"],
    ["Dragon Age: Inquisition", "성소로 읽히는 소품 위계 — 배너·조각상은 1개 이하"],
    ["Baldur’s Gate 3", "서쪽 붕괴와 방치 재질 — 식생은 균열·누수선 주변만"],
    ["Lies of P", "PBR·라이팅 보조 — 젖은 석재와 Roughness 대비"],
  ];
  const hdr = { bold: true, color: C.white, fill: { color: C.teal }, fontSize: 11 };
  const rows = [[{ text: "게임", options: hdr }, { text: "이번 씬 적용 기준", options: hdr }]]
    .concat(refs.map(([g, a], i) => [
      { text: g, options: { bold: true, color: C.ink, fontSize: 11, fill: { color: i % 2 ? "FAF8F5" : C.white } } },
      { text: a, options: { color: C.ink, fontSize: 11, fill: { color: i % 2 ? "FAF8F5" : C.white } } },
    ]));
  s.addTable(rows, { x: 3.8, y: 1.5, w: 5.7, colW: [1.85, 3.85], rowH: 0.5, fontFace: F, border: { type: "solid", pt: 0.5, color: C.line }, valign: "middle", margin: [2, 6, 2, 6] });
  num(s);
}

// ---------- 4. Spatial layout ----------
{
  const s = newSlide();
  title(s, "공간 구성", "붕괴는 서쪽에서 동쪽으로 — 방향성과 구조적 원인을 가진 파손");
  const bays = [
    ["WEST · 제1 Bay", "심한 붕괴", "출입구와 지붕을 중심으로 무너진 영역. 지붕·볼트 소실", C.ruin],
    ["CENTER · 제2 Bay", "부분 파손", "보존 영역과 붕괴 영역을 연결하는 전이 구간", C.partial],
    ["EAST · 제3 Bay", "보존", "제단을 포함한 대부분 보존 영역, 시각적 도착점", C.teal],
  ];
  bays.forEach(([tag, state, desc, col], i) => {
    const x = 0.5 + i * 3.05;
    s.addShape(pres.shapes.RECTANGLE, { x, y: 1.55, w: 2.85, h: 1.85, fill: { color: col }, line: { type: "none" } });
    T(s, tag, { x: x + 0.2, y: 1.7, w: 2.5, h: 0.3, fontSize: 10, bold: true, color: C.white, charSpacing: 1, margin: 0 });
    T(s, state, { x: x + 0.2, y: 2.05, w: 2.5, h: 0.55, fontSize: 22, bold: true, color: C.white, margin: 0 });
    T(s, desc, { x: x + 0.2, y: 2.7, w: 2.45, h: 0.6, fontSize: 12, color: C.white, margin: 0, valign: "top" });
  });
  s.addShape(pres.shapes.LINE, { x: 0.5, y: 3.7, w: 8.95, h: 0, line: { color: C.muted, width: 1.25, endArrowType: "triangle" } });
  T(s, "서쪽 출입구", { x: 0.5, y: 3.75, w: 2, h: 0.3, fontSize: 10, color: C.muted, margin: 0 });
  T(s, "동쪽 제단", { x: 7.5, y: 3.75, w: 1.95, h: 0.3, fontSize: 10, color: C.muted, align: "right", margin: 0 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 4.3, w: 9, h: 0.65, fill: { color: C.slate }, line: { type: "none" }, rectRadius: 0.06 });
  T(s, [
    { text: "핵심 구조 규칙   ", options: { bold: true, color: C.amber } },
    { text: "내부 벽부 기둥 = 리브 볼트 시작점 = 외부 버트레스  (X = 0 · 400 · 800 · 1200cm)", options: { color: C.white } },
  ], { x: 0.7, y: 4.3, w: 8.6, h: 0.65, fontSize: 13, valign: "middle", margin: 0 });
  num(s);
}

// ---------- 5. Design spec (height diagram + openings table) ----------
{
  const s = newSlide();
  title(s, "설계 규격", "모든 모듈이 공유하는 치수 — 0.5m Grid, 180cm 캐릭터 기준");
  // Height diagram
  card(s, 0.5, 1.5, 4.5, 3.6);
  T(s, "높이 기준 (바닥 기준, cm)", { x: 0.75, y: 1.62, w: 4, h: 0.3, fontSize: 11, bold: true, color: C.muted, margin: 0 });
  const baseY = 4.8, scale = 2.55 / 850; // 850cm -> 2.55in
  const bars = [["지붕 마루", 850, C.slate2], ["볼트 정점", 720, C.teal], ["측벽", 550, C.partial], ["캐릭터", 180, C.amber]];
  bars.forEach(([l, v, col], i) => {
    const x = 0.95 + i * 1.0, h = v * scale;
    s.addShape(pres.shapes.RECTANGLE, { x, y: baseY - h, w: 0.6, h, fill: { color: col }, line: { type: "none" } });
    T(s, String(v), { x: x - 0.2, y: baseY - h - 0.3, w: 1.0, h: 0.28, fontFace: FH, fontSize: 13, bold: true, color: C.ink, align: "center", margin: 0 });
    T(s, l, { x: x - 0.2, y: baseY + 0.03, w: 1.0, h: 0.22, fontSize: 9.5, color: C.muted, align: "center", margin: 0 });
  });
  s.addShape(pres.shapes.LINE, { x: 0.75, y: baseY, w: 4.0, h: 0, line: { color: C.muted, width: 1 } });
  // Spec table
  const spec = [
    ["벽 두께", "60cm"], ["리브 시작", "420cm"], ["측창 (랜싯)", "100 × 280cm"],
    ["서쪽 출입구", "160 × 320cm"], ["동쪽 Hero 창", "240 × 400cm"], ["제단 상판 폭", "305cm"], ["외곽 크기", "약 720 × 1,320cm"],
  ];
  const rows = spec.map(([k, v], i) => [
    { text: k, options: { bold: true, color: C.ink, fill: { color: i % 2 ? "FAF8F5" : C.white } } },
    { text: v, options: { color: C.teal, bold: true, fill: { color: i % 2 ? "FAF8F5" : C.white } } },
  ]);
  s.addTable(rows, { x: 5.3, y: 1.5, w: 4.2, colW: [1.9, 2.3], rowH: 0.5, fontFace: F, fontSize: 12.5, border: { type: "solid", pt: 0.5, color: C.line }, valign: "middle", margin: [2, 10, 2, 10] });
  T(s, "창대 높이·제단 깊이 등 노션에 수치가 없는 값은 블록아웃 제안값", { x: 5.3, y: 5.05, w: 4.2, h: 0.25, fontSize: 9, color: C.muted, margin: 0 });
  num(s);
}

// ---------- 6. Asset list ----------
{
  const s = newSlide();
  title(s, "제작 범위 — Asset List", "정상형 모듈과 교체형 파손 모듈이 같은 구조 규격을 공유");
  const items = [
    ["기본 구조 모듈", "평벽, 랜싯 창벽, 서/동 박공벽, 바닥 Bay, 벽부 기둥, 버트레스, 4분할 리브 볼트, 목조 트러스, 슬레이트 지붕"],
    ["변형·파손 모듈", "막힌 벽/창, 파손 벽, 파손 아치·기둥, 붕괴 볼트, 파손 트러스 — 정상형 규격 유지"],
    ["잔해", "석재·슬레이트·목재 파편 3–5종 — 서쪽 붕괴의 원인과 결과 연결"],
    ["Hero Asset", "동쪽 제단, 3연 트레이서리 스테인드글라스, 서쪽 붕괴 출입구·소형 종탑"],
    ["Props", "벤치 A/B, 촛대, 헤진 제단 천 — 원래 예배 공간이었음을 최소 수량으로"],
    ["재질·효과", "석회암·슬레이트·목재·유리 PBR / 균열·누수·이끼 데칼 / 먼지·물방울 VFX"],
  ];
  items.forEach(([h, d], i) => {
    const x = 0.5 + (i % 3) * 3.05, y = 1.55 + Math.floor(i / 3) * 1.85;
    const hero = h === "Hero Asset";
    card(s, x, y, 2.85, 1.65, hero ? C.slate : C.white);
    badge(s, x + 0.2, y + 0.22, i + 1, hero ? C.amber : C.teal);
    T(s, h, { x: x + 0.62, y: y + 0.2, w: 2.1, h: 0.36, fontSize: 14, bold: true, color: hero ? C.white : C.ink, margin: 0, valign: "middle" });
    T(s, d, { x: x + 0.2, y: y + 0.68, w: 2.5, h: 0.9, fontSize: 11, color: hero ? "D9D4CB" : C.muted, margin: 0, valign: "top" });
  });
  num(s);
}

// ---------- 7. Scope in/out ----------
{
  const s = newSlide();
  title(s, "범위 관리", "대성당이 아닌 소규모 예배당 — 만들지 않을 것을 먼저 정한다");
  const box = (x, head, fill, headColor, textColor, lines) => {
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.55, w: 4.35, h: 3.0, fill: { color: fill }, line: { type: "none" }, rectRadius: 0.08 });
    T(s, head, { x: x + 0.3, y: 1.75, w: 3.8, h: 0.4, fontSize: 16, bold: true, color: headColor, margin: 0 });
    T(s, bullets(lines), { x: x + 0.3, y: 2.3, w: 3.8, h: 2.1, fontSize: 13.5, color: textColor, paraSpaceAfter: 8, margin: 0, valign: "top" });
  };
  box(0.5, "Must Have", C.teal, C.white, C.white, [
    "단일 본당 3 Bay 구조 + 교체형 파손 모듈",
    "동쪽 제단 · Hero 창 · 서쪽 붕괴 출입구",
    "필수 잔해, 최소 수량의 예배 소품",
    "핵심 PBR 재질, 데칼, VFX",
  ]);
  box(5.15, "제작하지 않음", C.stoneDk, C.ruin, C.ink, [
    "측랑, 신랑 아케이드, 독립 기둥, 트랜셉트, 앱스",
    "플라잉 버트레스, 팬 볼트, 반복 피너클, 성곽식 흉벽",
    "대성당 규모의 장식, 다수의 부속 공간",
    "공포·의식물 과밀, 건축 실루엣을 가리는 식생",
  ]);
  T(s, "추가 아이디어는 Must Have 완성 후 확장으로 분리한다.", { x: 0.5, y: 4.75, w: 9, h: 0.3, fontSize: 11, italic: true, color: C.muted, margin: 0 });
  num(s);
}


// ---------- CASE 1 ----------
caseSlide(1, "범위 재정의", "처음 기획한 건물이 ‘건물이 주인공’이라는 의도와 맞는지 다시 확인", "해결", [
  ["후기 고딕 예배당의 측랑 반복 구획 3칸으로 기획", "기둥·첨두아치·벽·창·볼트·바닥 각 1종의 반복 모듈 구성"],
  ["측랑은 신랑 아케이드·독립 기둥을 전제로 하는 구조", "최종 참조 이미지와 다른 건물이 되고 소규모 범위가 흐려짐", "문서마다 범위(측랑 / 단일 본당)가 서로 달라짐"],
  ["13–14세기 영국계 고딕 단일 본당 6 × 12m · 3 Bay로 확정", "측랑·아케이드·독립 기둥·트랜셉트·앱스 제외 목록 명시", "모든 제작 문서를 같은 범위로 정리 (2026-09-28)"],
], "근거: 노션 제작 1 · 12-11 — 블록아웃 중 측랑·아케이드·독립 기둥이 생기면 최종 참조와 다른 건물이므로 즉시 수정");

// ---------- CASE 2 ----------
caseSlide(2, "반복 모듈 제작 비용 — AI 도입", "AI를 무조건 쓰지 않고, 같은 조건으로 비교해 도움이 되는 구간만 판단", "진행 중", [
  ["반복 구조(벽·창·버트레스·볼트)를 전부 수작업하면 시간이 크게 듦", "Tripo · Meshy · VARCO 3D에 같은 이미지 입력, 100점 기준 비교", "1차 랜싯 창벽 → 2차 버트레스"],
  ["Tripo: 무료 플랜 내보내기 차단 → 와이어·UV 검증 불가", "Meshy: 약 198만 Tri, 낮은 면 수 리메시는 몰딩 손상", "VARCO: 측면·상단이 불규칙해 접합 모듈로 부적합", "파손형을 따로 생성하면 크기·접합면이 달라질 위험"],
  ["역할 분리: Tripo 정상형 초안 · Meshy 하이폴·베이크 소스 · VARCO 풍화 참고", "파손형은 확정된 정상형을 복제해 내부에만 파손 적용", "규격·접합·토폴로지·UV는 제작자가 판단", "다음: Blender 기술 검사 후 최종 선정"],
], "근거: 노션 제작 2.1 — 점수와 순위는 화면 비교 기준 잠정값");

// ---------- 8. AI modeling comparison ----------
{
  const s = newSlide();
  title(s, "AI 3D 모델링 도구 비교", "같은 입력 이미지·같은 100점 기준으로 비교 — AI는 초안, 규격·토폴로지는 제작자가 판단");
  card(s, 0.5, 1.5, 4.6, 3.6);
  s.addChart(pres.charts.BAR, [{ name: "1·2차 종합 잠정 점수", labels: ["VARCO 3D", "Meshy", "Tripo"], values: [58, 76, 80] }], {
    x: 0.65, y: 1.6, w: 4.3, h: 3.4, barDir: "bar", chartColors: [C.teal],
    showTitle: true, title: "1·2차 종합 잠정 점수 (100점)", titleFontFace: F, titleFontSize: 12, titleColor: C.ink,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontSize: 12, dataLabelColor: C.ink, dataLabelFontBold: true,
    valAxisMinVal: 0, valAxisMaxVal: 100, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    catAxisLabelColor: C.ink, catAxisLabelFontSize: 12, catAxisLabelFontFace: F, catAxisLineShow: false, showLegend: false, barGapWidthPct: 60,
  });
  const roles = [
    ["Tripo", "잠정 1순위", "정상형 구조 모듈 초안 — 후면 접합면이 가장 평평, 43K Triangle", C.teal],
    ["Meshy", "2순위", "하이폴·베이크 소스 — 약 1분·20크레딧, 디테일 풍부(약 198만 Tri)", C.partial],
    ["VARCO 3D", "3순위", "풍화·파손 Variant 참고 — 불규칙한 석재 표현이 강함", C.ruin],
  ];
  roles.forEach(([n, r, d, col], i) => {
    const y = 1.5 + i * 1.22;
    card(s, 5.4, y, 4.1, 1.05);
    s.addShape(pres.shapes.OVAL, { x: 5.6, y: y + 0.22, w: 0.2, h: 0.2, fill: { color: col }, line: { type: "none" } });
    T(s, [{ text: n + "  ", options: { bold: true, color: C.ink } }, { text: r, options: { color: col, bold: true, fontSize: 11 } }],
      { x: 5.95, y: y + 0.12, w: 3.4, h: 0.4, fontSize: 14, margin: 0, valign: "middle" });
    T(s, d, { x: 5.95, y: y + 0.52, w: 3.4, h: 0.45, fontSize: 10.5, color: C.muted, margin: 0, valign: "top" });
  });
  T(s, "화면 비교 기준 잠정 결과 · Blender 기술 검사 후 최종 선정", { x: 0.5, y: 5.15, w: 6, h: 0.25, fontSize: 9, color: C.muted, margin: 0 });
  num(s);
}


// ---------- CASE 3 ----------
caseSlide(3, "모듈 배치 비용 — Bay 생성 시스템", "모듈을 하나씩 옮기지 않고, Bay 조합표만 바꿔 예배당을 다시 조립", "설계 완료", [
  ["이전 Unity 건물 생성 시스템의 설계 원리를 Unreal Blueprint로 재설계", "Construction Script로 벽·버트레스·볼트·지붕 반복 배치"],
  ["한 Bay 안에서도 벽·버트레스·지붕의 파손 정도가 서로 다름", "그래서 손상 상태 하나로 Bay 전체를 바꾸는 방식 대신 모듈별로 고르는 조합표로 설계", "AI 원본은 길이·Pivot·접합면이 제각각이라 공통 규격이 먼저 필요"],
  ["F_ChapelBayConfig: Bay별로 벽·버트레스·볼트·지붕·낙석을 각각 선택", "모든 모듈을 400cm Bay · 공통 Pivot · 평평한 접합면으로 리터칭", "Hero·소품은 자동 조립 후 직접 배치"],
], "근거: 노션 제작 2.2 · 제작 10", ["시도", "고려한 점", "설계 · 계획"]);

// ---------- 9. Bay generator ----------
{
  const s = newSlide();
  title(s, "Bay 기반 모듈 생성 시스템", "Bay 수와 Bay별 모듈 조합을 입력하면 규격 모듈로 예배당을 자동 조립");
  const steps = [["AI 초기 메시", "형태·석재 원본"], ["Blender", "400cm 규격·Pivot"], ["DA_Module Set", "모듈 라이브러리"], ["F_BayConfig", "Bay별 조합표"], ["BP_Generator", "Construction Script"]];
  steps.forEach(([h, d], i) => {
    const x = 0.5 + i * 1.86, last = i === steps.length - 1;
    card(s, x, 1.5, 1.6, 1.0, last ? C.slate : C.white);
    T(s, h, { x, y: 1.6, w: 1.6, h: 0.4, fontSize: 12, bold: true, color: last ? C.amber : C.teal, align: "center", margin: 0, valign: "middle" });
    T(s, d, { x, y: 2.0, w: 1.6, h: 0.35, fontSize: 10, color: last ? "D9D4CB" : C.muted, align: "center", margin: 0 });
    if (!last) s.addShape(pres.shapes.LINE, { x: x + 1.62, y: 2.0, w: 0.22, h: 0, line: { color: C.muted, width: 1.25, endArrowType: "triangle" } });
  });
  const hdr = { bold: true, color: C.white, fill: { color: C.slate }, fontSize: 11 };
  const cfg = [
    ["Bay 1", "창벽 붕괴형", "붕괴형", "열린 지붕·파손 볼트", "Large", C.ruin],
    ["Bay 2", "창벽 부분 파손", "부분 파손", "부분 파손 지붕", "Small", C.partial],
    ["Bay 3", "정상 창벽", "정상형", "정상 지붕·볼트", "None", C.teal],
  ];
  const rows = [["Bay", "벽체", "버트레스", "볼트·지붕", "낙석"].map(t => ({ text: t, options: hdr }))]
    .concat(cfg.map(r => r.slice(0, 5).map((t, j) => ({ text: t, options: j === 0 ? { bold: true, color: C.white, fill: { color: r[5] } } : { color: C.ink, fill: { color: C.white } } }))));
  s.addTable(rows, { x: 0.5, y: 2.85, w: 9, colW: [1.1, 2.1, 1.6, 2.6, 1.6], rowH: 0.42, fontFace: F, fontSize: 12, border: { type: "solid", pt: 0.5, color: C.line }, valign: "middle", align: "center" });
  T(s, [
    { text: "핵심 분리  ", options: { bold: true, color: C.teal } },
    { text: "모듈은 Blender에서 한 번 제작 · 조합은 Bay 조합표 · 배치는 Blueprint", options: { color: C.ink } },
  ], { x: 0.5, y: 4.65, w: 9, h: 0.45, fontSize: 12, margin: 0, valign: "middle" });
  num(s);
}

// ---------- 10. Blockout result ----------
{
  const s = newSlide();
  s.addImage({ path: IMG_INT, x: 0, y: 0, w: 5.4, h: 5.625, sizing: { type: "cover", w: 5.4, h: 5.625 } });
  T(s, "블록아웃 완료", { x: 5.8, y: 0.45, w: 3.8, h: 0.6, fontSize: 28, bold: true, color: C.ink, margin: 0 });
  T(s, "GothicChapel_Main · 2026-09-28", { x: 5.8, y: 1.05, w: 3.8, h: 0.3, fontSize: 11, color: C.muted, margin: 0 });
  const st = [["181", "생성 액터"], ["36", "전용 메시"], ["9", "단색 재질"], ["6 / 6", "충돌 경로 통과"]];
  st.forEach(([v, l], i) => {
    const x = 5.8 + (i % 2) * 1.95, y = 1.6 + Math.floor(i / 2) * 1.15;
    T(s, v, { x, y, w: 1.8, h: 0.6, fontFace: FH, fontSize: 30, bold: true, color: C.teal, margin: 0 });
    T(s, l, { x, y: y + 0.6, w: 1.8, h: 0.3, fontSize: 11, color: C.muted, margin: 0 });
  });
  T(s, bullets([
    "서쪽 진입 시 제단·Hero 창 중심축 정렬 확인",
    "입구 3경로·내부 3경로 캡슐 충돌 검사 통과",
    "남은 일: 3인칭 PIE 이동 테스트",
  ]), { x: 5.8, y: 4.0, w: 3.9, h: 1.1, fontSize: 11, color: C.ink, paraSpaceAfter: 4, margin: 0, valign: "top" });
  num(s);
}


// ---------- CASE 4: blockout issues ----------
{
  const s = newSlide();
  T(s, "CASE 04", { x: 0.5, y: 0.3, w: 2, h: 0.3, fontSize: 11, bold: true, color: C.amber, charSpacing: 1.5, margin: 0 });
  T(s, "블록아웃 검수에서 발견한 문제", { x: 0.5, y: 0.6, w: 7.4, h: 0.6, fontSize: 26, bold: true, color: C.ink, margin: 0 });
  T(s, "실제 에디터 바운드와 충돌 쿼리로 확인하고, 설계 문서의 공백은 제안값으로 명시", { x: 0.5, y: 1.18, w: 8, h: 0.32, fontSize: 12, color: C.muted, margin: 0 });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.1, y: 0.65, w: 1.4, h: 0.4, fill: { color: C.teal }, line: { type: "none" }, rectRadius: 0.2 });
  T(s, "해결", { x: 8.1, y: 0.65, w: 1.4, h: 0.4, fontSize: 11, bold: true, color: C.white, align: "center", valign: "middle", margin: 0 });
  const hdr = (t, f) => ({ text: t, options: { bold: true, color: C.white, fill: { color: f }, fontSize: 11.5 } });
  const data = [
    ["박공벽·일부 소품 방향 오류", "회전축 설정 오류", "실제 액터 바운드로 방향·치수를 확인하고 수정"],
    ["OBJ 임포트 스무딩·탄젠트 경고", "블록아웃 메시의 법선 정보", "법선·탄젠트 재계산, MikkTSpace 해제 (최종 UV는 별도 제작)"],
    ["지붕 경사면 3.8m 자료값 불일치", "폭 6m · 마루/처마 높이차 3m와 동시에 성립 불가", "전체 폭·높이를 우선, 반폭 375 · 상승 300cm 임시 매스"],
    ["노션에 없는 수치", "창대 높이·제단 깊이·소품 위치 미정", "블록아웃 제안값 적용(측창 창대 160 · 동쪽 220), README에 표기"],
  ];
  const rows = [[hdr("발견한 문제", C.ruin), hdr("원인", C.slate2), hdr("해결", C.teal)]]
    .concat(data.map((r, i) => r.map((t, j) => ({ text: t, options: { color: C.ink, bold: j === 0, fill: { color: i % 2 ? "FAF8F5" : C.white } } }))));
  s.addTable(rows, { x: 0.5, y: 1.7, w: 9, colW: [2.6, 2.8, 3.6], rowH: 0.52, fontFace: F, fontSize: 11, border: { type: "solid", pt: 0.5, color: C.line }, valign: "middle", margin: [2, 8, 2, 8] });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 4.55, w: 9, h: 0.55, fill: { color: C.white }, line: { color: C.amber, width: 1.25 }, rectRadius: 0.06 });
  T(s, [
    { text: "남은 검증  ", options: { bold: true, color: C.amber } },
    { text: "캡슐 충돌 검사(입구 3 · 내부 3경로)는 통과했지만 에디터 쿼리일 뿐 — 3인칭 PIE 플레이 테스트로 확인 예정", options: { color: C.ink } },
  ], { x: 0.7, y: 4.55, w: 8.6, h: 0.55, fontSize: 11.5, valign: "middle", margin: 0 });
  num(s);
}

// ---------- 11. Art direction & PBR ----------
{
  const s = newSlide();
  title(s, "아트 디렉션 & PBR 기준");
  const col = (x, head, color, lines) => {
    card(s, x, 1.25, 4.35, 3.85);
    T(s, head, { x: x + 0.3, y: 1.45, w: 3.8, h: 0.4, fontSize: 16, bold: true, color, margin: 0 });
    T(s, bullets(lines), { x: x + 0.3, y: 2.0, w: 3.8, h: 2.9, fontSize: 13, color: C.ink, paraSpaceAfter: 8, margin: 0, valign: "top" });
  };
  col(0.5, "시간감과 파손 원칙", C.teal, [
    "석회암 벽·랜싯 창·리브 볼트·트러스·슬레이트 지붕이 주된 읽힘을 만든다",
    "파손은 랜덤 장식이 아니라 구조가 실제로 무너진 결과",
    "젖은 석재·누수·이끼·먼지·마모를 재질 레이어로 사용",
    "소품은 건축·제단 실루엣보다 앞서지 않게",
  ]);
  col(5.15, "PBR·텍스처 기준", C.amber, [
    "Base Color에 조명·그림자를 그리지 않는다",
    "석회암 Metalness = 0, 젖은 면은 Roughness로 구분",
    "Base Color · Normal · ORM 출력 규칙 통일",
    "반복 모듈은 공통 Texel Density, Hero만 고유 해상도",
    "Tiling · Trim · Unique Texture 역할 분리",
  ]);
  num(s);
}

// ---------- 12. Hero & props ----------
{
  const s = newSlide();
  title(s, "Hero Asset & 소품", "소품은 채우기가 아니라 ‘무엇이 무너졌고 얼마나 오래 방치되었는가’를 보여주는 묶음");
  const hero = [
    ["동쪽 제단", "서쪽 진입 시 읽히는 계단형 정면 실루엣. 상판 305cm → 중앙 본체 → 필라스터 → 아치 리세스"],
    ["3연 트레이서리 창", "제단의 중심축 · 배경 광원 · 색 포인트"],
    ["서쪽 출입구·종탑", "첫 화면에서 폐허 사건과 진입 방향 제시"],
  ];
  T(s, "HERO ASSET", { x: 0.5, y: 1.45, w: 4.4, h: 0.3, fontSize: 10, bold: true, color: C.amber, charSpacing: 1, margin: 0 });
  hero.forEach(([h, d], i) => {
    const y = 1.85 + i * 1.08;
    card(s, 0.5, y, 4.4, 0.92, C.slate, false);
    T(s, h, { x: 0.75, y: y + 0.1, w: 4.0, h: 0.32, fontSize: 13, bold: true, color: C.white, margin: 0 });
    T(s, d, { x: 0.75, y: y + 0.42, w: 4.0, h: 0.45, fontSize: 10.5, color: "D9D4CB", margin: 0, valign: "top" });
  });
  T(s, "PROPS 배치 규칙", { x: 5.2, y: 1.45, w: 4.3, h: 0.3, fontSize: 10, bold: true, color: C.teal, charSpacing: 1, margin: 0 });
  card(s, 5.2, 1.85, 4.3, 3.08);
  T(s, bullets([
    "통로 중앙은 비우고 측벽·제단 단 주변에 배치",
    "소품은 보존된 중앙~동쪽 Bay에 배치",
    "벤치는 방향·간격·파손을 달리해 반복감 제거",
    "촛대·천은 낮게, 시선을 제단 쪽으로",
    "예배당 → 붕괴 → 방치로 읽히게",
  ]), { x: 5.45, y: 2.05, w: 3.85, h: 2.75, fontSize: 12, color: C.ink, paraSpaceAfter: 9, margin: 0, valign: "top" });
  num(s);
}

// ---------- 13. Roadmap (15 steps) ----------
{
  const s = newSlide();
  title(s, "제작 로드맵", "규격 고정 → 플레이 검증 → 에셋 → 조립 → 증명");
  const DONE = "done", WIP = "wip", TODO = "todo";
  const steps = [
    ["콘셉트·범위", "제작 1", DONE], ["설계 규격", "제작 2", DONE], ["블록아웃·동선", "제작 3", WIP], ["1 Bay 프로토타입", "제작 4", TODO], ["Bay 생성기 v0", "제작 2.2·10", TODO],
    ["AI→기본 모듈", "제작 2.1·5", WIP], ["파손 Variation·잔해", "제작 5", TODO], ["Hero 에셋", "제작 6", WIP], ["PBR 기준 확정", "제작 7", TODO], ["텍스처 본 제작", "제작 8", TODO],
    ["머티리얼", "제작 9", TODO], ["조립·세트 드레싱", "제작 10·11", TODO], ["라이팅·VFX", "제작 12", TODO], ["최적화", "제작 13", TODO], ["포트폴리오", "제작 14", TODO],
  ];
  const sty = {
    done: { fill: C.teal, head: C.white, sub: "CFE3E3", badge: C.white, bt: C.teal },
    wip: { fill: C.white, head: C.ink, sub: C.amber, badge: C.amber, bt: C.white },
    todo: { fill: C.stoneDk, head: C.ink, sub: C.muted, badge: "BDB6AA", bt: C.white },
  };
  steps.forEach(([h, p, st], i) => {
    const x = 0.5 + (i % 5) * 1.82, y = 1.45 + Math.floor(i / 5) * 1.12, S = sty[st];
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 1.68, h: 0.98, fill: { color: S.fill }, line: st === WIP ? { color: C.amber, width: 1.5 } : { type: "none" }, rectRadius: 0.07 });
    badge(s, x + 0.12, y + 0.12, i + 1, S.badge, S.bt, 0.3);
    T(s, p, { x: x + 0.5, y: y + 0.12, w: 1.1, h: 0.3, fontSize: 9, color: S.sub, margin: 0, valign: "middle" });
    T(s, h, { x: x + 0.12, y: y + 0.48, w: 1.5, h: 0.42, fontSize: 11.5, bold: true, color: S.head, margin: 0, valign: "middle" });
  });
  const leg = [["완료", C.teal, null], ["진행 중", C.white, C.amber], ["예정", C.stoneDk, null]];
  leg.forEach(([l, f, ln], i) => {
    const x = 0.5 + i * 1.3;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 4.97, w: 0.28, h: 0.2, fill: { color: f }, line: ln ? { color: ln, width: 1.25 } : { type: "none" }, rectRadius: 0.04 });
    T(s, l, { x: x + 0.36, y: 4.94, w: 0.9, h: 0.26, fontSize: 10, color: C.muted, margin: 0, valign: "middle" });
  });
  num(s);
}

// ---------- 14. Why this order ----------
{
  const s = newSlide();
  title(s, "순서를 이렇게 정한 이유", "앞 단계가 흔들리면 뒤 단계를 전부 다시 해야 한다");
  const pts = [
    ["생성기를 앞당긴다", "규격만 있으면 프록시로 만들 수 있다. 먼저 만들면 모듈을 교체할 때마다 3 Bay 전체를 바로 확인한다."],
    ["파손형은 정상형 확정 뒤", "정상형을 복제해 파손을 적용해야 규격·Pivot·접합면이 같은 교체용 Variant가 된다."],
    ["PBR 기준을 먼저 승인", "Tiling·Trim 초안으로 색상·Roughness·Normal 기준을 잡은 뒤 본 제작에 들어간다."],
    ["캡처는 매 단계마다", "라이팅은 블록아웃부터 가볍게 확인하고, 단계별 캡처가 그대로 Breakdown 자료가 된다."],
  ];
  pts.forEach(([h, d], i) => {
    const x = 0.5 + (i % 2) * 4.6, y = 1.55 + Math.floor(i / 2) * 1.75;
    card(s, x, y, 4.4, 1.45);
    badge(s, x + 0.25, y + 0.25, i + 1, C.teal);
    T(s, h, { x: x + 0.7, y: y + 0.22, w: 3.5, h: 0.38, fontSize: 14, bold: true, color: C.ink, margin: 0, valign: "middle" });
    T(s, d, { x: x + 0.25, y: y + 0.72, w: 3.9, h: 0.8, fontSize: 11.5, color: C.muted, margin: 0, valign: "top" });
  });
  num(s);
}

// ---------- 15. Deliverables & next (dark) ----------
{
  const s = newSlide(C.slate);
  title(s, "최종 결과물 & 다음 단계", "대표 이미지·영상·제작 과정이 한 포트폴리오 페이지에서 이어지도록", true);
  card(s, 0.5, 1.5, 4.35, 3.1, C.slate2, false);
  T(s, "최종 결과물", { x: 0.8, y: 1.7, w: 3.8, h: 0.4, fontSize: 15, bold: true, color: C.amber, margin: 0 });
  T(s, bullets([
    "최종 이미지 3–5장",
    "Bay 생성 시스템 작동 영상",
    "기본 모듈 · Hero High/Low/Bake Breakdown",
    "Tiling·Trim·Master Material · Vertex Blend·Decal",
    "최적화 전후 비교",
  ]), { x: 0.8, y: 2.25, w: 3.85, h: 2.7, fontSize: 12.5, color: C.white, paraSpaceAfter: 7, margin: 0, valign: "top" });
  T(s, "NEXT", { x: 5.2, y: 1.7, w: 4.3, h: 0.4, fontSize: 15, bold: true, color: C.amber, margin: 0 });
  const next = ["블록아웃 레벨 3인칭 PIE 이동 테스트", "1 Bay 프로토타입 + Bay 생성기 v0", "AI 모델 Blender 기술 검사 → 최종 선정"];
  next.forEach((t, i) => {
    const y = 2.25 + i * 0.9;
    badge(s, 5.2, y + 0.1, i + 1, C.amber, C.slate, 0.4);
    T(s, t, { x: 5.75, y, w: 3.75, h: 0.6, fontSize: 13, color: C.white, margin: 0, valign: "middle" });
  });
  num(s, true);
}

pres.writeFile({ fileName: OUT }).then(f => console.log("wrote", f));
