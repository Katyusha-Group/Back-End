from jdatetime import jalali


def get_persian_date(date):
    jd = jalali.GregorianToJalali(date.year, date.month, date.day)
    return str(jd.jyear) + '-' + str(jd.jmonth) + '-' + str(jd.jday)
