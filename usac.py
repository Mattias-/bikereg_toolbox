
import urllib2
import re
import string
import datetime

import bs4

def simple_str(s):
    pattern = re.compile('[\W_]+')
    return pattern.sub('', s.lower())

def findRidersByName(firstname='', lastname=''):
    if firstname or lastname:
        search = '%s,%s' % (lastname, firstname)
    else:
        return []
    url = 'http://www.usacycling.org/results/'
    query = '?compid=%s' % search
    f = urllib2.urlopen(url+query)
    soup = bs4.BeautifulSoup(f)
    div = soup.find('div', class_='rrWatermark')
    table = div.find('table')
    if table.find('td', class_='errormessage'):
        return []
    trs = table.find_all('tr')
    ths = table.find_all('th')
    headers = []
    for th in ths:
        for s in th.stripped_strings:
            headers.append(simple_str(s))
    riders = []
    for tr in trs:
        tds = tr.find_all('td', class_='homearticlebody')
        row = []
        for td in tds:
            for s in td.stripped_strings:
                row.append(s)
        if len(tds) == len(headers):
            rider = dict(zip(headers, row))
            rider['city'], rider['state'] = rider.pop('hometown').split(', ')
            rider['lastname'], rider['firstname'] = rider.pop('name').split(', ')
            rider['url'] = url + '?compid=%s' % rider['usac']
            riders.append(rider)
    return riders


def findRacesByLicence(lic):
    url = 'http://www.usacycling.org/results/'
    query = '?compid=%s' % lic
    f = urllib2.urlopen(url+query)
    soup = bs4.BeautifulSoup(f)
    div = soup.find('div', class_='rrWatermark')
    if div.find('span', class_='errormessage'):
        return []
    table = div.find('table')
    rider_text = table.find('td').get_text()
    m = re.match(r"Race Results for (?P<firstname>\w+) (?P<lastname>.*)"
                 "Racing Age (?P<age>\w+) from (?P<city>.*), (?P<state>\w+)",
                 rider_text)
    try:
        rider = m.groupdict()
        rider['usac'] = lic
    except:
        print 'can not parse rider_text'
        return []

    ths = table.find_all('th')
    headers = []
    for th in ths:
        for s in th.stripped_strings:
            headers.append(simple_str(s))
    tds = table.find_all('td', class_='homearticlebody')
    races = []
    for td in tds[:-1]:
        sp = td.find('span', class_='homearticleheader')
        race = {}
        # Parse date
        m,d,y = sp.contents[0].split()[0].split('/')
        race['date'] = datetime.date(int(y), int(m), int(d))
        race['race_name'] = sp.contents[1].string
        race['href'] = url+sp.contents[1]['href']
        def spanHasTitle(tag):
            return tag.name == 'span' and tag.has_key('title')
        spans = td.find_all(spanHasTitle)
        for span in spans:
            race[simple_str(span['title'])] = span.string
        res_tds = td.parent.next_sibling.find_all('td')
        res = dict(zip(headers, [res_td.string for res_td in res_tds]))
        race.update(res)
        if race.get('points', None) == '-':
            race['points'] = None
        races.append(race)
    return {'rider': rider, 'races': races}

#s = findRacesByLicence('394236')
#print findRidersByName(lastname='Appelgren')
#print s
