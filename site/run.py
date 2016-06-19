from flask import Flask, render_template
import os
import json
from collections import defaultdict
import sys
from flask_frozen import Freezer

reload(sys)
sys.setdefaultencoding('utf-8')

app = Flask(__name__)
app.config['FREEZER_DESTINATION'] = "../gh_pages"
app.config['FREEZER_BASE_URL']="http://sztanko.github.io/solsticestreets/"
freezer = Freezer(app)

def load_all_cities():
    files = os.listdir("json/")
    a = [json.load(file('json/'+f)) for f in os.listdir("json/")]
    print "print loading all files from dir"

def loadCityList():
    headers = 'group,geonameid,top,left,bottom,right,slug,name'.split(',')
    cities = [dict(zip(headers, c.strip().split('\t'))) for c in file('cities.txt').readlines()[1:]]
    cities_by_continent = defaultdict(list)
    for c in cities:
        cities_by_continent[c['group']].append(c)
    for cc in cities_by_continent.values():
        cc.sort(key = lambda c: c['name'])
    continents = cities_by_continent.keys()
    continents.sort()
    return cities, cities_by_continent, continents

@app.route('/')
def get_list():
    c, cbc, continents = loadCityList()
    return render_template('index.html', c=c, cbc=cbc, continents=continents)
@app.route('/cities/<cityName>.html')
def get_city(cityName):
    cities, cbg, c = loadCityList()
    city = filter(lambda c: c['slug']==cityName, cities)[0]
    summer = json.load(file('json/summersolstice/'+cityName+'.geojson'))
    winter = json.load(file('json/wintersolstice/'+cityName+'.geojson'))
    stats = json.load(file('json/wintersolstice/'+cityName+'.stats.json'))
    stats['summer_sun_azimuth'] = json.load(file('json/summersolstice/'+cityName+'.stats.json'))['sun_azimuth']
    streetIndex = list(set([f['properties']['name'] for f in summer['features'] + winter['features']]))
    return render_template('city.html', city=city,  streetIndex=streetIndex, 
            stats=stats, summer = summer, winter = winter)

@freezer.register_generator
def cityGen():
    cities, cities_by_continent, continents = loadCityList()
    #print cities['']
    for city in cities:
        print city
        yield '/cities/%s.html' %(city['slug'])

@freezer.register_generator
def indexGen():
    yield '/'

#app.run(debug=True)
freezer.freeze()
