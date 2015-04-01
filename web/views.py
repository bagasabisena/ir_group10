from web import app, db, models
from flask import render_template, request
import elasticsearch
from flaskext.mysql import MySQL


@app.route('/')
def index():
    cursor = db.engine.execute('select * from region_table')
    #cursor=mysql.connect().cursor()
    #cursor.execute("select * from region_table")
    rows = cursor.fetchall()

    for row in rows:
        row="%s" %row
        print row
    return render_template('index.html',rows=rows)


@app.route('/search')
def search():
    es = elasticsearch.Elasticsearch()
    query = request.args.get('q', '')
    region_id = request.args.get('region', '')
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
                    "analyzer": "english",
                    "fuzziness": "auto"
                }
            }
        }
      ]
    }
  }
}
""" % (query, query, query)
    returned_query = es.search(index='4sreviews', doc_type='venues',
                               body=body)
    results = returned_query['hits']['hits']
    return render_template('search.html', query=query, results=results)


@app.route('/venue/<venue_id>')
def venue(venue_id):
    es = elasticsearch.Elasticsearch()
    venue = es.get(index='4sreviews', doc_type='venues', id=venue_id)
    return render_template('venue.html', venue=venue)


@app.route('/test')
def test():
    return models.Tip.query.first().text
