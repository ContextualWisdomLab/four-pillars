from __future__ import annotations

STEMS_HANJA = ("甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸")
STEMS_KO = ("갑", "을", "병", "정", "무", "기", "경", "신", "임", "계")
BRANCHES_HANJA = ("子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥")
BRANCHES_KO = ("자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해")
ELEMENTS = ("wood", "fire", "earth", "metal", "water")
ELEMENTS_KO = {
    "wood": "목",
    "fire": "화",
    "earth": "토",
    "metal": "금",
    "water": "수",
}
STEM_ELEMENT = ("wood", "wood", "fire", "fire", "earth", "earth", "metal", "metal", "water", "water")
BRANCH_ELEMENT = ("water", "earth", "wood", "wood", "earth", "fire", "fire", "earth", "metal", "metal", "earth", "water")

# Hidden stems are ordered by traditional weight: main, middle, residual.
HIDDEN_STEMS: dict[int, tuple[int, ...]] = {
    0: (9,),
    1: (5, 9, 7),
    2: (0, 2, 4),
    3: (1,),
    4: (4, 1, 9),
    5: (2, 4, 6),
    6: (3, 5),
    7: (5, 3, 1),
    8: (6, 8, 4),
    9: (7,),
    10: (4, 7, 3),
    11: (8, 0),
}

TEN_GODS_KO = {
    "peer": "비견",
    "rob_wealth": "겁재",
    "eating_god": "식신",
    "hurting_officer": "상관",
    "indirect_wealth": "편재",
    "direct_wealth": "정재",
    "seven_killings": "편관",
    "direct_officer": "정관",
    "indirect_resource": "편인",
    "direct_resource": "정인",
}

GROWTH_STAGES = ("장생", "목욕", "관대", "건록", "제왕", "쇠", "병", "사", "묘", "절", "태", "양")
GROWTH_START_BRANCH = {
    0: 11,  # 甲 at 亥
    1: 6,   # 乙 at 午
    2: 2,   # 丙 at 寅
    3: 9,   # 丁 at 酉
    4: 2,   # 戊 at 寅
    5: 9,   # 己 at 酉
    6: 5,   # 庚 at 巳
    7: 0,   # 辛 at 子
    8: 8,   # 壬 at 申
    9: 3,   # 癸 at 卯
}

# Month-changing solar terms (절), with apparent solar longitude and month branch.
JIE_TERMS: tuple[tuple[str, str, float, int, int, int], ...] = (
    ("소한", "小寒", 285.0, 1, 5, 1),
    ("입춘", "立春", 315.0, 2, 4, 2),
    ("경칩", "驚蟄", 345.0, 3, 6, 3),
    ("청명", "清明", 15.0, 4, 5, 4),
    ("입하", "立夏", 45.0, 5, 6, 5),
    ("망종", "芒種", 75.0, 6, 6, 6),
    ("소서", "小暑", 105.0, 7, 7, 7),
    ("입추", "立秋", 135.0, 8, 8, 8),
    ("백로", "白露", 165.0, 9, 8, 9),
    ("한로", "寒露", 195.0, 10, 8, 10),
    ("입동", "立冬", 225.0, 11, 7, 11),
    ("대설", "大雪", 255.0, 12, 7, 0),
)

BRANCH_CLASHES = frozenset({frozenset(p) for p in ((0, 6), (1, 7), (2, 8), (3, 9), (4, 10), (5, 11))})
BRANCH_COMBINES = frozenset({frozenset(p) for p in ((0, 1), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7))})
BRANCH_HARMS = frozenset({frozenset(p) for p in ((0, 7), (1, 6), (2, 5), (3, 4), (8, 11), (9, 10))})
STEM_COMBINES = frozenset({frozenset(p) for p in ((0, 5), (1, 6), (2, 7), (3, 8), (4, 9))})
STEM_CLASHES = frozenset({frozenset(p) for p in ((0, 6), (1, 7), (2, 8), (3, 9))})

FORBIDDEN_COPY = (
    "시키는 대로 책임지는 사람",
    "평가받는 사람에서 조건을 정하는 사람",
    "사옥 이전도 이동수로 볼 수 있습니까",
    "상세판",
)
VAGUE_COPY = ("이 힘", "그 선택", "현재 상황", "내 몫")
