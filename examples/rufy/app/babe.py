from __future__ import print_function # In python 2.7
import sys
import facebook
import requests
import json
import threading
from pprint import *

from flask import *
app = Flask(__name__, template_folder='.')

def print_me(string):
	print(string, file=sys.stderr)

mytoken="EAACEdEose0cBAPMUhoHaJkPd3wLikqOmT0vFgQ4XysYdCce84bqM1QJ6JtvWvj5FKbZAElVJRii0X8epH7glWZAPcK2ZCWi0bInesXVPnHT4Hncogt1jJcnHnXKEZAVWFiAuZBoh3Hvj5WNId4DlpETciCASCoa3YBP6R2sKQsQZDZD"
graph = facebook.GraphAPI(mytoken)
app_id=1335682093131967
def get_results_from_api():
	graph = facebook.GraphAPI(mytoken)
	pages = graph.get_object('me/accounts')

def get_views(token, id):
	graph = facebook.GraphAPI(token)
	post = graph.get_connections(id, 'insights/post_impressions')
	return post['data'][0]['values'][0]['value']

def write_post(id,text, published):
	graph = facebook.GraphAPI(id)
	graph.put_object(parent_object='me', connection_name = 'feed', message = text, published=published)

def get_posts_from_graph_object(obj):
	posts = obj['data']
	next_page = "None"
	if "paging" in obj:
		next_page = obj['paging']['next']
	return posts,next_page


@app.route('/')
def babe():
	#return redirect(url_for('show_pages'))
	#return render_template('login.html', app_id=app_id, name="testing")

	pages=get_accounts()
	#print (pages, file=sys.stderr)
	return render_template('disp.html',pages=pages)

	return '<html><body><h1>Hello World</h1></body></html>'
	#print "hello_world2fl"
	access_token = 'EAACEdEose0cBAKwcCvhAZCsNSDBH9mu3hoWZAZBMeMrIiZCW342I6Niw44eL5LrzNfdoFKyZC8ZBQgCMUm9ZCj00bvVZC6OeH0fnsXZCuZCTJr6LUld3rHOAWJViib0AaZC1L87jTlTW2ZB2KZCEL4YjfRGkqrtIZC73gK5UQYQL4qZAHJUNgZDZD'
	# Look at Bill Gates's profile for this example by using his Facebook id.
	access_token="EAACEdEose0cBAAqAPg5AEGxIvwkFtptqd9xwndDevUU8BDfgDVXNhpCcaVJqBctILdIrz23ZA50IxHYoBEBYqxG2t0Pb8rPKi6Uq6gL3R5oCYlfrnQ5kVtIpDeUhtECvbe3CevbTQcEpOuPt0ZBI9r59SeB1GqCZB69HFkciYmJXqTknd9J"
	graph = facebook.GraphAPI(access_token)
	pages = graph.get_object('me')
	#graph.put_object(parent_object='me', connection_name='feed',
	#                 message='Hello, world')
	#pages=graph.get
	posts = graph.get_connections(pages['id'], 'feed')
	pprint (posts)

def get_accounts():
	graph = facebook.GraphAPI(mytoken)
	pages = graph.get_object('me/accounts')
	#pprint (pages['data'])
	pages_info=[]
	for page in pages['data']:
		pages_info.append(   (  page['name'], page['access_token'] )  )

	return pages_info

@app.route('/show', methods=['POST', 'GET'])
def show_pages():
	page_id=request.args['page_id']

	if str(request.args['r_type'])=="Create":
		return render_template("write.html",page_id=page_id)

	if request.args['referrer']=="home":
		graph = facebook.GraphAPI(page_id)
		pages = graph.get_object('me')
		res = graph.get_connections(pages['id'], 'feed', limit=5)
	else:
		res = requests.request("GET",request.args['next']).json()

	posts,next_page = get_posts_from_graph_object(res)

	"""
	views_list = []
	thread_list = []
	thread=Thread(target=get_views,args=(page_id,i['id']) )
	thread.start()
	"""

	posts_info=[]
	for i in posts:
		if "message" in i:
			views=get_views(page_id,i['id'])
			posts_info.append(  (i['message'], views ) )
	return render_template('show_posts.html', posts_info=(posts_info,next_page,page_id))

@app.route('/show_more', methods=['POST', 'GET'])
def show_more_posts():
	return "deprecated"
	res = requests.request("GET",request.args['next']).json()
	page_id=request.args['page_id']
	posts,next_page = get_posts_from_graph_object(res)
	posts_info=[]
	print_me(posts)
	for i in posts:
		if "message" in i:
			views=get_views(page_id,i['id'])
			posts_info.append(  (i['message'], views ) )
	return render_template('show_posts.html', posts_info=(posts_info,next_page,page_id))





@app.route('/write', methods=['POST', 'GET'])
def write_page():
	page_id = request.args['page_id']
	text = request.args['text']
	if request.args['p_type']=='Published':
		published = "1"
	else:
		published = "0"
	#write_post(page_id, text, published)

	for i in range(30):
		write_post(page_id, "Post num "+str(i), published)
	return str( text	)




	#return	render_template("show_posts.html",)

#def show_posts():

