import codecs

import pandas as pd
from utils import project_variables


def extract_limitation_data(df: pd.DataFrame):
    data = pd.DataFrame(data=df.iloc[:, 16])
    new_data = pd.DataFrame()
    for entry in data.iterrows():
        limit_text = entry[1].values[0]
        try:
            limit_parts = limit_text.split('،')
            limits = ''
            for part in limit_parts:
                if 'دانشکده' in part:
                    if 'غیرمجاز' in part:
                        temp = part.strip(' ').strip('غیرمجاز برای دانشکده').strip(' ')
                        flag = 'False'
                    else:
                        temp = part.strip(' ').strip('دانشکده').strip(' ')
                        flag = 'True'
                    if 'واح' in temp or 'آموزش' in temp or 'واحـ' in temp or 'فنی' in temp:
                        continue
                    if 'ار' in temp:
                        temp = 'مهندسی معماری'
                    if 'برق' in temp:
                        temp = 'مهندسی برق'
                    if 'راه' in temp:
                        temp = 'مهندسی راه آهن'
                    elif 'فیزی' in temp:
                        temp = 'فیزیک'
                    elif 'مکانی' in temp:
                        temp = 'مهندسی مکانیک'
                    elif 'عمر' in temp:
                        temp = 'مهندسی عمران'
                    elif 'ض' in temp:
                        temp = 'ریاضی و علوم کامپیوتر'
                    elif 'مدیریت' in temp:
                        temp = 'مدیریت، اقتصاد و مهندسی پیشرفت'
                    elif 'شیمی' in temp:
                        temp = 'مهندسی شیمی، نفت و گاز'
                    elif 'مواد' in temp:
                        temp = 'مهندسی مواد و متالورژی'
                    elif 'صنایع' in temp:
                        temp = 'مهندسی صنایع'
                    if temp not in limits:
                        limits += temp + '-' + flag + ','
        except AttributeError:
            limits = ''
        new_data = pd.concat([new_data, pd.DataFrame(data={project_variables.ALLOWED_DEPARTMENTS: [limits]})],
                             ignore_index=True)
    new_data.reset_index()
    df[project_variables.ALLOWED_DEPARTMENTS] = new_data.values
    return df
