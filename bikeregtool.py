from flask import Flask

import bikereg

app = Flask(__name__)

@app.route("/<race_id>/<category>")
def printhtml(race_id, category):
    br_riders = bikereg.findPreRegOfRace(race_id, category)
    #br_riders = bikereg.findPreRegOfRace('18723', 'Category 4')
    r = bikereg.findUsacRidersOfPreReg(br_riders)
    print r
    res = []
    for rider in r:
        ri = rider['rider']
        row = '<a href="%s">%s</a>' % (ri['url'],
                                       ri['firstname']+' '+ri['lastname'])
        res.append(row)
    return "<br>".join(res)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
