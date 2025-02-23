import random


def generate_questions(num_questions=10):
    """
    num_questions 개수만큼 구구단 문제를 생성하여 리스트로 반환.
    반환 형식: [(문제문자열, 정답, [보기1, 보기2, 보기3, 보기4]), ...]
    """
    questions = []
    for _ in range(num_questions):
        # 구구단 범위 1~9 (원하는 범위 확장 가능)
        x = random.randint(2, 9)
        y = random.randint(1, 9)
        answer = x * y

        # 보기용 오답 생성 (중복되지 않게)
        choices = set([answer])
        while len(choices) < 4:
            wrong = random.randint(2, 81)  # 9*9 = 81, 범위 내 랜덤
            choices.add(wrong)
        choices = list(choices)
        random.shuffle(choices)

        question_str = f"{x} x {y} = ?"
        questions.append((question_str, answer, choices))

    return questions


def check_answer(user_answer, correct_answer):
    """사용자가 고른 답이 정답과 일치하는지 True/False 반환"""
    return user_answer == correct_answer
