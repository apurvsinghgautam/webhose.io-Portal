import time
import json
import webhoseio
from flask import *
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})


app = Flask(__name__)


@app.route('/', methods=['GET','POST'])
def index():
	return render_template('index.html')
	

class Webhose():

	data={}
	filt=''
	def __init__(self):
		self.api_key = '<your_api_key>' # Enter your WebhoseIO API key
		webhoseio.config(token=self.api_key)

	def get_posts(self,filtr,query):
		r=webhoseio.query(filtr, {'q':query})
		return r

	
@app.route('/search', methods=['GET','POST'])
def search():
	if request.method == 'POST':
		try:
			web=Webhose()
		except:
			app.logger.warning("Connection delayed by the server")
			app.logger.warning("Retrying in few seconds")
			time.sleep(60)
			
		filtr=request.form['filter']
		query=request.form['search_query']
		try:
			r=web.get_posts(filtr,query)
		except Exception as e:
			app.logger.warning(e)
		app.logger.info('Searching your query {}'.format(query))
		Webhose.filt=filtr
		Webhose.data=r
		posts, requests_left=handle_posts(web.data,filtr)											
		total_page=len(posts)
		mid_page=int(total_page/2)
		if posts:
			return render_template('view_data.html', post=posts[0], r=requests_left, filtr=filtr, page=1, mid_page=mid_page, total_page=total_page)
		else:
			flash('No Data Found','danger')
			return render_template('search.html')
	return render_template('search.html')


@app.route('/view_data/<int:page>')
def view_data(page):
	try:
		web=Webhose()
	except:
		app.logger.warning("Connection delayed by the server")
		app.logger.warning("Retrying in few seconds")
		time.sleep(60)
	data=web.data
	filtr=web.filt
	posts, requests_left=handle_posts(data,filtr)
	total_page=len(posts)
	mid_page=int(total_page/2)
	if page <= 0:
		return render_template('404.html')
	elif page > total_page:
		return render_template('404.html')
	else:
		if posts:
			return render_template('view_data.html', post=posts[page-1], r=requests_left, filtr=filtr, page=page, mid_page=mid_page, total_page=total_page)
		else:
			flash('No Data Found','danger')
			return render_template('search.html')


def handle_posts(data,filtr):
	requests_left=data['requestsLeft']
	if filtr == 'filterWebContent':
		posts=[]
		for post in data['posts']:
			posts.append(post)
		return posts,requests_left
	elif filtr == 'reviewFilter':
		posts=[]
		for post in data['reviews']:
			posts.append(post)
		return posts,requests_left
	elif filtr == 'productFilter':
		posts=[]
		for post in data['products']:
			posts.append(post)
		return posts,requests_left
	elif filtr == 'darkwebFilter':
		posts=[]
		for post in data['DarkwebPosts']:
			posts.append(post)
		return posts,requests_left
	elif filtr == 'broadcastFilter':
		posts=[]
		for post in data['items']:
			posts.append(post)
		return posts,requests_left


if __name__ == '__main__':
	app.secret_key = '<your_secret_key>' # Enter Flask Secret Key
	app.run()