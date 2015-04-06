from web import models
import json
import elasticsearch


# elasticsearch --config=/usr/local/opt/elasticsearch/config/elasticsearch.yml

INDEX_NAME = '4sreviews'

es = elasticsearch.Elasticsearch()

if es.indices.exists(INDEX_NAME):
    print("deleting '%s' index..." % (INDEX_NAME))
    res = es.indices.delete(index=INDEX_NAME)
    print(" response: '%s'" % (res))

# since we are running locally, use one shard and no replicas
request_body = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    }
}

print("creating '%s' index..." % (INDEX_NAME))
res = es.indices.create(index=INDEX_NAME, body=request_body)
print(" response: '%s'" % (res))

mapping = """
{
    "venues": {
        "properties": {
            "name": {
                "type": "string",
                "analyzer": "simple"
            },
            "categories": {
                "properties": {
                    "shortName": {
                        "type": "string",
                        "analyzer": "english"
                    }
                }
            },
            "tips": {
                "properties": {
                    "text": {
                        "type": "string",
                        "analyzer": "english"
                    }
                }
            }
        }
    }
}
"""

print('change analyzer for field')
res = es.indices.put_mapping(index=INDEX_NAME,
                             doc_type='venues',
                             body=mapping)

print('creating index now...')

for v in models.Venue.query.all():
    v_dict = {}
    v_dict['name'] = v.name
    v_dict['location'] = json.loads(v.location)

    if v.menu:
        v_dict['menu'] = json.loads(v.menu)

    v_dict['stats'] = json.loads(v.stats)
    v_dict['categories'] = json.loads(v.categories)

    tips = v.tips
    tips_dict = [t.as_dict() for t in tips]
    v_dict['tips'] = tips_dict

    es.index(index='4sreviews', doc_type='venues', id=v.venue_id, body=v_dict)

    print('venue %s is inserted' % v.venue_id)
