# Information Retrieval Group 10

## Requirements

### MySQL server

Run mysql instance on your local machine. Then import `data.sql` to the mysql.

### Elasticsearch

Download elasticsearch from [here](https://www.elastic.co/downloads/elasticsearch). Install on your local machine. Run it. Open on browser http://localhost:9200 to check if the instance is running.

### Python 2.7 and pip

Installed all required python package `pip install -r requirements.txt`

### Indexed data to elasticsearch

Open `config.py`. Change the url on the `SQLALCHEMY_DATABASE_URI` according to the mySQL configuration on your local machine. Format:

`SQLALCHEMY_DATABASE_URI = mysql+pymysql://<username>:<password>@127.0.0.1/4sreviews`

For example, mySQL with root as username and no password

`SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@127.0.0.1/4sreviews'`

Now run the import_elasticsearch.py
`python import_elasticsearch.py`

## Run

Run the web server `python run.py`

Go to http://localhost:5000 on the browser





