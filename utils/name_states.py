from random import choice


tags = {
    '1': ('alcoholic', 'cash', 'dj', 'psychedelic'),
    '2': ('FAT', 'computer', 'dark', 'dictator', 'fun', 'samurai', 'shark', 'swimming', 'zombie'),
    '3': ('Wet', 'disappointed', 'mad', 'metal', 'praise', 'strange', 'unicorn'),
    '4': ('hard', 'sad', 'Trippy', 'crying', 'scream', 'ugly', 'victory')
}

def response_for_state(answer: str):
    answer = int(answer)
    
    tag: str
    support_words: str

    if 0 <= answer <= 3:
        tag = choice(tags['1'])
        support_words = 'Всё не так уж и плохо'
    elif 4 <= answer <= 6:
        tag = choice(tags['2'])
        support_words = 'Держись, воин. Думай о хорошем'
    elif 7 <= answer <= 8:
        tag = choice(tags['3'])
        support_words = 'Ууу, запахло жареным'
    else:
        tag = choice(tags['4'])
        support_words = 'Пожарные уже выехали на помощь'
    
    return (tag, support_words)