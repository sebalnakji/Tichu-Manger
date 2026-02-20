"""
Hangul Converter
한글을 영문 키보드 입력으로 변환하는 유틸리티
"""


def convert_hangul_to_english(text: str) -> str:
    """
    한글을 영문 자판 입력으로 변환
    예: "징징이" → "wldwlddl"

    Args:
        text: 변환할 텍스트 (한글 포함 가능)

    Returns:
        str: 영문 자판으로 변환된 텍스트 (대소문자 구분)
    """
    # 초성 리스트
    CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    # 중성 리스트
    JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ',
                     'ㅣ']

    # 종성 리스트
    JONGSUNG_LIST = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ',
                     'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    # 한글 자모 → 영문 키보드 매핑
    KOREAN_TO_ENGLISH = {
        # 자음
        'ㄱ': 'r', 'ㄲ': 'R',
        'ㄴ': 's',
        'ㄷ': 'e', 'ㄸ': 'E',
        'ㄹ': 'f',
        'ㅁ': 'a',
        'ㅂ': 'q', 'ㅃ': 'Q',
        'ㅅ': 't', 'ㅆ': 'T',
        'ㅇ': 'd',
        'ㅈ': 'w', 'ㅉ': 'W',
        'ㅊ': 'c',
        'ㅋ': 'z',
        'ㅌ': 'x',
        'ㅍ': 'v',
        'ㅎ': 'g',
        # 모음
        'ㅏ': 'k',
        'ㅐ': 'o',
        'ㅑ': 'i',
        'ㅒ': 'O',
        'ㅓ': 'j',
        'ㅔ': 'p',
        'ㅕ': 'u',
        'ㅖ': 'P',
        'ㅗ': 'h',
        'ㅘ': 'hk',
        'ㅙ': 'ho',
        'ㅚ': 'hl',
        'ㅛ': 'y',
        'ㅜ': 'n',
        'ㅝ': 'nj',
        'ㅞ': 'np',
        'ㅟ': 'nl',
        'ㅠ': 'b',
        'ㅡ': 'm',
        'ㅢ': 'ml',
        'ㅣ': 'l',
        # 복합 자음 (종성)
        'ㄳ': 'rt',
        'ㄵ': 'sw',
        'ㄶ': 'sg',
        'ㄺ': 'fr',
        'ㄻ': 'fa',
        'ㄼ': 'fq',
        'ㄽ': 'ft',
        'ㄾ': 'fx',
        'ㄿ': 'fv',
        'ㅀ': 'fg',
        'ㅄ': 'qt',
    }

    result = []

    for char in text:
        # 한글 음절인 경우 (가-힣)
        if '가' <= char <= '힣':
            # 유니코드 값 계산
            code = ord(char) - ord('가')

            # 초성, 중성, 종성 분리
            chosung_index = code // (21 * 28)
            jungsung_index = (code % (21 * 28)) // 28
            jongsung_index = code % 28

            chosung = CHOSUNG_LIST[chosung_index]
            jungsung = JUNGSUNG_LIST[jungsung_index]
            jongsung = JONGSUNG_LIST[jongsung_index]

            # 영문 키보드로 변환
            result.append(KOREAN_TO_ENGLISH.get(chosung, chosung))
            result.append(KOREAN_TO_ENGLISH.get(jungsung, jungsung))
            if jongsung:
                result.append(KOREAN_TO_ENGLISH.get(jongsung, jongsung))

        # 한글 자모인 경우 (ㄱ-ㅎ, ㅏ-ㅣ)
        elif 'ㄱ' <= char <= 'ㅎ' or 'ㅏ' <= char <= 'ㅣ':
            result.append(KOREAN_TO_ENGLISH.get(char, char))

        # 영문, 숫자, 특수문자는 그대로
        else:
            result.append(char)

    return ''.join(result)