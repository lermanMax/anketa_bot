from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from db_module import DB_module



# Data base
DB = DB_module(DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_PORT)

translate = {'manager': 'менеджер', 
             'delivery': 'доставка', 
             'cooking': 'кулинария', 
             'dietetics': 'диеталогия'}
translate_month = {
             1: 'январь',
             2: 'февраль',
             3: 'март',
             4: 'апрель',
             5: 'май',
             6: 'июнь',
             7: 'июль',
             8: 'август',
             9: 'сентябрь',
             10: 'октябрь',
             11: 'ноябрь',
             12: 'декабрь'}

def get_analysis(list_of_answers):
    text = 'Отчет:\n'
    dict_of_votes = {} #словарь с оценками
    for answer in list_of_answers:
        year = answer['answering_date'].timetuple()[0]
        month = answer['answering_date'].timetuple()[1]
        if not year in dict_of_votes:
            dict_of_votes[year] = {}
        if not month in dict_of_votes[year]:
            dict_of_votes[year][month] = {'loyalty':[],
                                          'n_promoters':0,
                                          'n_critics':0,
                                          'manager':[], 
                                          'delivery':[], 
                                          'cooking':[], 
                                          'dietetics':[]}
        
        dict_of_votes[year][month]['loyalty'].append(answer['loyalty'])
        if answer['loyalty'] > 8: dict_of_votes[year][month]['n_promoters']+=1
        elif answer['loyalty'] < 7: dict_of_votes[year][month]['n_critics']+=1
        
        for name in ['manager', 'delivery', 'cooking', 'dietetics']:
            vote = answer[name]
            if vote: dict_of_votes[year][month][name].append(vote)
                

    list_of_years = list(dict_of_votes.keys())
    list_of_years.sort()        
    for year in list_of_years:
        text += '\nГод - ' + str(year) + '\n'
        
        list_of_month = list(dict_of_votes[year].keys())
        list_of_month.sort() 
        for month in list_of_month:
            text += '\nМесяц - ' + translate_month[month] + '\n'
            
            n_answers = len(dict_of_votes[year][month]['loyalty'])
            n_promoters = dict_of_votes[year][month]['n_promoters']
            n_critics = dict_of_votes[year][month]['n_critics']
            persent_promoters = int(n_promoters/n_answers * 100)
            persent_critics = int(n_critics/n_answers * 100)
            NPS = persent_promoters - persent_critics
            
            text += 'Количество ответов: ' + str(n_answers) + '\n'
            text += '% промоутеров: ' + str(persent_promoters) + '%\n'
            text += '% критиков: ' + str(persent_critics) + '%\n'
            text += '➡ NPS: ' + str(NPS) + '%\n'
            
            text += 'Средние оценки по показателям:\n'     
            for name in translate:
                
                len_ = len(dict_of_votes[year][month][name])
                sum_ = sum(dict_of_votes[year][month][name])
                if len_ != 0: average_rating = round(sum_/len_, 2)
                else: average_rating = 'нет оценок'
                
                text += '▪'+translate[name]+': ' + str(average_rating) + '\n'
    
    return text

