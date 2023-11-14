from jdatetime import jalali


def get_persian_date(self):
    jd = jalali.GregorianToJalali(self.date.year, self.date.month, self.date.day)
    return str(jd.jyear) + '-' + str(jd.jmonth) + '-' + str(jd.jday)
