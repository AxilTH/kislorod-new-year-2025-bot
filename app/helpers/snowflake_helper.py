def get_snowflakes_word(score: int) -> str:
    """Возвращает правильную форму слова 'снежинка' для числа"""
    if score % 10 == 1 and score % 100 != 11:
        return "снежинка"
    elif score % 10 in [2, 3, 4] and score % 100 not in [12, 13, 14]:
        return "снежинки"
    else:
        return "снежинок"