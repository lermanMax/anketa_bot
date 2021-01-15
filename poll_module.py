'''
Структура словаря

{имя вопроса : {ответ_1: 'следующий вопрос'}} 
'''
question_dict = {
    'start':{
        'default':'loyalty'},
    'loyalty':{
        'default':'manager'},
    'manager':{
        'default':'delivery'},
    'delivery':{
        'default':'cooking'},
    'cooking':{
        'default':'dietetics'},
    'dietetics':{
        'default':'end'},
    'admin_options':{
        'default': 'admin'},
    'admin':{
        'Получить таблицу ответов': 'all_answers',
        'Получить аналитику': 'analysis'},

    }


def get_text_from(path):
    with open(path,'r') as file:
        one_string = ''
        for line in file.readlines():
            one_string += line
    return one_string
            
    

def get_next_question(question_name = 'default', 
                      answer = 'default', 
                      files_dir = 'text_of_questions/'):
    
    question_name = question_dict[question_name][answer]
    question_text = get_text_from(files_dir + question_name +'.txt')
    if question_name in ['start', 'loyalty', 'manager', 'delivery', 'cooking', 'dietetics']: 
        answers = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    elif question_name in ['end', 'all_answers', 'no_information', 'analysis']: 
        answers = []
    else:
        answers = [answer for answer in question_dict[question_name]]
    
    
    return question_name, question_text, answers
