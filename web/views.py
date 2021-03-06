from web import app, db, models
from flask import render_template, request
import elasticsearch
from sqlalchemy.sql import text
from operator import itemgetter
import json
import pprint


@app.route('/')
def index():
    cursor = db.engine.execute('select * from region_table')
    # cursor=mysql.connect().cursor()
    # cursor.execute("select * from region_table")
    rows = cursor.fetchall()

    for row in rows:
        row = "%s" % row
        print row
    return render_template('index.html', rows=rows)


@app.route('/search')
def search():
    es = elasticsearch.Elasticsearch()
    query = request.args.get('q', '')
    q_region_id = int(request.args.get('region', ''))
    body = """
{
  "query": {
    "bool": {
      "should": [
        {
          "match": {
            "name": {
                "query": "%s",
                "analyzer": "simple",
                "fuzziness": "auto"
            }
          }
        },
        {
          "match": {
            "categories.shortName": {
                "query": "%s",
                "analyzer": "english",
                "fuzziness": "auto"
          }
            }
        },
        {
            "match": {
                "tips.text": {
                    "query":"%s",
                    "analyzer": "english"                }
            }
        }
      ]
    }
  }
}
""" % (query, query, query)
    # elasticsearch should return all venue_ids
    # relevance from elasticsearch is ignored
    # ranking is by origin on below codes
    returned_query = es.search(index='4sreviews', doc_type='venues',
                               body=body, fields=['_id'])
    results = returned_query['hits']['hits']
    venue_ids = [result['_id'] for result in results]

    # now return all user_id for all the venue who has tips on the venue
    # select distinct(user_id) from tips where venue_id IN
    # ('4ac518caf964a520bda520e3','4ac518d6f964a52031a820e3');
    qry = "select distinct(user_id) from tips where venue_id IN :venue_ids"
    params = {'venue_ids': venue_ids}
    cursor = db.engine.execute(text(qry), params)
    user_ids = [row[0] for row in cursor.fetchall()]

    # SELECT user_id,value,COUNT(*) as count FROM 4sreviews.intermediate where user_id=419 GROUP By value ORDER BY count desc;

    qry = "SELECT value as count FROM 4sreviews.intermediate where user_id=:user_id GROUP By value ORDER BY count desc LIMIT 1"

    user_region = []

    # params = {'user_id': '419'}
    # cursor = db.engine.execute(text(qry), params)
    # region_id = cursor.fetchall()
    # if not region_id:
    #     region_id = 0
    # print region_id

    for u in user_ids:
        params = {'user_id': u}
        cursor = db.engine.execute(text(qry), params)
        result = cursor.fetchall()
        if not result:
            region_id = 0
        else:
            region_id = result[0][0]
            if region_id == q_region_id:
                flag = 5
            else:
                flag = 1

        user_region.append((u, region_id, flag))

    # get the tips
    qry = "SELECT tip_id, user_id, venue_id, text, ph2 FROM tips WHERE venue_id IN :venue_ids"
    # qry = "SELECT tip_id, user_id, venue_id, text, ph2 FROM tips WHERE venue_id=:venue_id"
    params = {'venue_ids': venue_ids}
    # params = {'venue_id': venue_ids[0]}
    cursor = db.engine.execute(text(qry), params)
    tips = cursor.fetchall()

    entries = []
    for tip in tips:
        entry = {}
        entry['tip_id'] = tip[0]
        entry['user_id'] = tip[1]
        entry['venue_id'] = tip[2]
        entry['text'] = tip[3]
        entry['ph2'] = tip[4]

        idx = [i for i, v in
               enumerate(user_region) if v[0] == entry['user_id']][0]
        entry['flag'] = user_region[idx][2]
        entry['ph2'] = flag*entry['ph2']
        entries.append(entry)

    final = []

    for venue_id in venue_ids:
        semi = {}
        semi['venue_id'] = venue_id
        # semi['ph'] = 0
        ph = 0
        # semi['flag_count'] = 0
        flag_count = 1
        semi['relevant_tips'] = []
        for entry in entries:
            if venue_id == entry['venue_id']:
                ph = ph + entry['ph2']
                flag_count = flag_count + entry['flag']

                if entry['flag'] == 5:
                    tip = models.Tip.query.get(entry['tip_id'])
                    # semi['relevant_tips'].append((entry['user_id'],
                    #                               entry['tip_id'],
                    #                               entry['text']))
                    semi['relevant_tips'].append(tip.as_dict())

        semi['final_ph'] = ph / flag_count
        final.append(semi)

    sorted_final = sorted(final, key=itemgetter('final_ph'), reverse=True)
    # sorted_ids = [row['venue_id'] for row in sorted_final]
    # sorted_venues = models.Venue.query.filter(models.Venue.
    #                                           venue_id.in_(sorted_ids)).all()

    sorted_venues = []

    for row in sorted_final:
        venue = models.Venue.query.filter_by(venue_id=row['venue_id']).first()
        venue = venue.as_dict()
        venue['tips'] = row['relevant_tips']
        venue['final_ph'] = row['final_ph']
        sorted_venues.append(venue)

    # get region
    region = models.Region.query.get(q_region_id)

    for v in sorted_venues:
        print '%s - %f' % (v['venue_id'], v['final_ph'])

    return render_template('search.html', query=query,
                           region=json.dumps(region.as_dict()),
                           venues=json.dumps(sorted_venues))


@app.route('/venue/<venue_id>')
def venue(venue_id):

    q_region_id = int(request.args.get('region', ''))
    panel = request.args.get('panel', '')
    venue = models.Venue.query.get(venue_id)

    # from all the tips, get users
    qry = "select distinct(user_id) from tips where venue_id = :venue_id"
    params = {'venue_id': venue_id}
    cursor = db.engine.execute(text(qry), params)
    user_ids = [row[0] for row in cursor.fetchall()]

    qry = "SELECT value as count FROM 4sreviews.intermediate where user_id=:user_id GROUP By value ORDER BY count desc LIMIT 1"

    user_region = []

    for u in user_ids:
        params = {'user_id': u}
        cursor = db.engine.execute(text(qry), params)
        result = cursor.fetchall()
        if not result:
            region_id = 0
        else:
            region_id = result[0][0]
            if region_id == q_region_id:
                user_region.append(u)
            else:
                # a workaround to show all tips in the detailed venue
                # not only the relevant one
                user_region.append(u)

    qry = "SELECT tip_id FROM tips WHERE user_id IN :user_ids AND venue_id = :venue_id"
    params = {'user_ids': user_region, 'venue_id': venue_id}
    cursor = db.engine.execute(text(qry), params)
    tip_ids = [row[0] for row in cursor.fetchall()]

    summaries = []

    for tip_id in tip_ids:
        tip = models.Tip.query.get(tip_id)
        user = tip.user

        # get the summary for food
        qry = "SELECT sentence, ph FROM food WHERE tip_id = :tip_id AND label = 1"
        params = {'tip_id': tip_id}
        cursor = db.engine.execute(text(qry), params)
        summary_food = cursor.fetchall()

        if summary_food:
            for s in summary_food:
                summary = {}
                summary['user'] = user.as_dict()
                summary['sentence'] = s[0]
                summary['flag_food'] = 1
                summary['flag_service'] = 0
                summary['ph_food'] = s[1]
                summary['ph_service'] = 0
                summaries.append(summary)

        # get the summary for service
        qry = "SELECT sentence, ph FROM service WHERE tip_id = :tip_id AND label = 1"
        params = {'tip_id': tip_id}
        cursor = db.engine.execute(text(qry), params)
        summary_service = cursor.fetchall()

        if summary_service:
            for s in summary_service:
                summary = {}
                summary['user'] = user.as_dict()
                summary['sentence'] = s[0]
                summary['flag_food'] = 0
                summary['flag_service'] = 1
                summary['ph_food'] = 0
                summary['ph_service'] = s[1]
                summaries.append(summary)
        print "reached here"

    return render_template('venue.html',
                           venue=json.dumps(venue.as_dict()),
                           summary=json.dumps(summaries),
                            panel=panel)


@app.route('/test')
def test():
    return models.Tip.query.first().text
