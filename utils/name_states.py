def response_for_state(answer: str):
    answer = int(answer)
    if 0 <= answer <= 3:
        return 'Всё не так уж и плохо'
    elif 4 <= answer <= 6:
        return 'Держись, воин. Думай о хорошем'
    elif 7 <= answer <= 8:
        return 'Ууу, запахло жареным, где мой огнетушитель'
    else:
        return 'Пожарная служба уже выехала на помощь'