# 예배당 랜드스케이프 — 2026-09-30

기획 출처: https://app.notion.com/p/3e910d86fdd580b38d3cf6b84133957f

기획의 ‘외딴 언덕 위 소규모 예배당’, ‘비 갠 뒤’, ‘건축 실루엣을 가리지 않는 식생’을 기준으로 지형을 구성했습니다. 기획에 지형의 치수는 없어 아래 수치는 구현 제안값입니다.

- 적용 맵: `/Game/GothicChapel/Levels/Main/GothicChapel_Main`
- 액터: `Landscape_Chapel_Hill`. 실제 Landscape이며 기존 Edit Layer를 유지합니다.
- 크기 252×252m, 505×505 높이 샘플, XY 50cm, Z scale 100. 위치 (-12000,-12600,12)cm.
- 예배당 중앙 (600,0) 주변은 평탄한 기초 접합부, 외곽은 비대칭 완만한 언덕. 총 높이 차 약19.3m.
- 서쪽 진입로는 지형 경사를 따라가며, 약2.2m 중심부에서 넓은 어깨로 부드럽게 연결됩니다.
- 절차적 초지·흙·경사 석회암 색, 지표 미세 노멀, 길·건물 주변의 낮은 Roughness를 적용했습니다. 식생 메시를 배치한 상태는 아닙니다.
- 새 재질: `/Game/GothicChapel/Environment/Landscape/Materials/M_Landscape_ChapelHill`. 기존 M_Landscape_Master / MI_Landscape / MF_LandscapeLayer_A는 보존했습니다.
- 검수 카메라: `LS_Camera_Hill_Overview`, 미리보기 `Landscape_Overview.png`.

## 검증

`verification.json`: 높이 7점의 실제 Landscape 충돌과 원본 값 비교, 입구·실내 6개 캡슐 이동 경로 검사. 진입로 종방향 최대 샘플 경사는 약28도입니다. 전체 PIE 이동 테스트나 FPS 벤치마크는 수행하지 않았습니다.

현재 결과는 지형 형태와 기본 재질 구현입니다. 최종 식생·사진 기반 PBR 텍스처·먼 배경과 최종 라이팅은 후속 아트 작업입니다. 기존 하늘·조명·안개 설정을 유지했습니다.

## 수정 및 복구

- Landscape Sculpt에서 직접 편집할 수 있습니다.
- `Chapel_Hill_505.r16`은 최종 16비트 little-endian 높이맵입니다. 재임포트는 Landscape Manage → Import에서 505×505, Original, 현재 지형 원점에 맞춰 진행합니다. 수동 조형 후 재임포트하면 현재 선택 레이어의 높이가 바뀌므로 먼저 레벨을 백업하세요.
- `Scripts/prepare_landscape.py`는 최초 생성 이력입니다. 완료된 맵에 다시 실행하지 마세요.
- `Scripts/refine_landscape.py`는 최종 높이맵 및 재질 생성 이력입니다. 자동으로 높이맵을 적용하지 않으며 재질 수정 내용을 덮어씁니다.
- `Scripts/verify_landscape.py`는 현재 지형을 검증하고 레벨과 미리보기를 저장합니다.
- 변경 전 현재 에디터 내용을 저장한 백업: `Saved/LandscapeBackups/20260930_111746/GothicChapel_Main.umap`.
- 노션 페이지는 읽기만 했습니다.
