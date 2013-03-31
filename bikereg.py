import urllib2
import re
import string
import datetime

import bs4

import usac

def simple_str(s):
    pattern = re.compile('[\W_]+')
    return pattern.sub('', s.lower().strip())

def findPreRegOfRace(race_id, race_class):
    url = 'https://www.bikereg.com/NET/Confirmed/%s' % race_id
    f = urllib2.urlopen(url)
    soup = bs4.BeautifulSoup(f)
    div = _getCatElement(soup, race_class)
    race_cat_id = div.find('div', class_='categoryEntries')['racerecid']
    return _getRiders(race_id, race_cat_id)

def _getRiders(race_id, race_cat_id):
    url = 'https://www.bikereg.com/Net/Registration/ConfirmedSingleRace.aspx?'
    query = 'RaceRecID=%s&EventID=%s' % (race_cat_id, race_id)
    f = urllib2.urlopen(url+query)
    soup = bs4.BeautifulSoup(f)

    ths = soup.find_all('th')
    headers = []
    for th in ths:
            res = simple_str(th.get_text())
            if res == 'st':
                res = 'state'
            elif res == 'first':
                res = 'firstname'
            elif res == 'last':
                res = 'lastname'
            headers.append(res)
    riders = []
    for tr in soup.find('tbody').find_all('tr'):
        row = []
        for td in tr.find_all('td'):
            row.append(td.get_text())
        rider = dict(zip(headers,row))
        riders.append(rider)
    return riders


def _getCatElement(soup, race_class):
    cat_divs = soup.find_all('div', class_='categoryHeader')
    for cat_div in cat_divs:
        cat_str = cat_div.find('div', class_='categoryName').get_text()
        if race_class in cat_str and 'Waitlist' not in cat_str:
            return cat_div

def scoreRider(br_rider, usac_rider):
    points = 100
    multiplier = 1
    br_rider_last = simple_str(br_rider['lastname'])
    usac_rider_last = simple_str(usac_rider['lastname'])
    br_rider_first = simple_str(br_rider['firstname'])
    usac_rider_first = simple_str(usac_rider['firstname'])
    if (br_rider_last == usac_rider_last and
        br_rider_first == usac_rider_first):
        multiplier = 1
    elif br_rider_last == usac_rider_last:
        multiplier = 0.70
    elif br_rider_first == usac_rider_first:
        multiplier = 0.75
    else:
        multiplier = 0.5
    points *= multiplier

    br_rider_state = simple_str(br_rider['state'])
    usac_rider_state = simple_str(usac_rider['state'])
    br_rider_city = simple_str(br_rider['city'])
    usac_rider_city = simple_str(usac_rider['city'])
    if (br_rider_state == usac_rider_state and
        br_rider_city == usac_rider_city):
        multiplier = 1
    elif br_rider_state == usac_rider_state:
        multiplier = 0.5
    elif br_rider_city == usac_rider_city:
        multiplier = 0.8
    else:
        multiplier = 0.3

    points *= multiplier
    return points



def findUsacRidersOfPreReg(br_riders):
    matched_riders = []
    for br_rider in br_riders:
        res = usac.findRidersByName(lastname=br_rider['lastname'],
                                    firstname=br_rider['firstname'])
        #print "\n\nRider: %s %s, %s" % (br_rider['firstname'],
        #                                br_rider['lastname'], br_rider)
        weighed_res_riders = []
        total_points = 0
        for usac_rider in res:
            points = scoreRider(br_rider, usac_rider)
            weighed_res_riders.append({'rider':usac_rider, 'points':points})
            total_points += points
            #print '%s for %s' % (points, usac_rider)

        best_match = {'points':-1}
        for d in weighed_res_riders:
            cur = d['points']/total_points
            d['points'] = cur
            if cur > best_match['points']:
                best_match = d
        matched_riders.append(best_match)
    return matched_riders

if __name__ == '__main__':
    import pprint
    br_riders = findPreRegOfRace('18723', 'Category 4')
    r = findUsacRidersOfPreReg(br_riders)
    pprint.pprint(r)
