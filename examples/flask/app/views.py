from __future__ import print_function # In python 2.7
import sys
from facebook import get_user_from_cookie, GraphAPI
from flask import g, render_template, redirect, request, session, url_for
import facebook
from app import app, db
from models import User
import sys
import requests
from threading import *
import time
# Facebook app details
FB_APP_ID = '1335682093131967'
FB_APP_NAME = 'testing'
FB_APP_SECRET = '7cc4885f7b114f87747bb664d6a3a200'
mytoken=""



def get_accounts():
    """
    Fetches all pages for the given user
    """
    graph = facebook.GraphAPI(mytoken)
    pages = graph.get_object('me/accounts')
    pages_info=[]
    for page in pages['data']:
        pages_info.append(   (  page['name'], page['access_token'] )  )
    return pages_info


def get_results_from_api():
    graph = facebook.GraphAPI(mytoken)
    pages = graph.get_object('me/accounts')

def get_views(token, id, views_dict):
    """
    Fetches number of views from a given post ID
    """
    graph = facebook.GraphAPI(token)
    post = graph.get_connections(id, 'insights/post_impressions')
    views_dict[id] = post['data'][0]['values'][0]['value']


def write_post(id, args):
    """
    Write a post to the page with specified arguments 
    """
    graph = facebook.GraphAPI(id) 
    graph.put_object(parent_object='me', connection_name = 'feed', **args)


def get_posts_from_graph_object(obj):
    """
    Using 'next' field, gets next set of posts
    """
    posts = obj['data']
    next_page = "None"
    if "paging" in obj:
        next_page = obj['paging']['next']
    return posts,next_page


@app.route('/show', methods=['POST', 'GET'])
def show_pages():
    """
    Fetches published or unpublished posts and displays them
    """
    page_id=request.args['page_id']

    if str(request.args['r_type'])=="Create":
        return render_template("write.html",page_id=page_id)

    if request.args['referrer']=="home":
        graph = facebook.GraphAPI(page_id)
        pages = graph.get_object('me')
        is_published = request.args['r_type'] == "Show_Published"
        print_me(is_published)
        res = graph.get_connections(pages['id'], 'promotable_posts', is_published=is_published, limit=8)
    else:
        res = requests.request("GET",request.args['next']).json()
    posts,next_page = get_posts_from_graph_object(res)
    views_dict={}
    thread_list = []
    message_dict={} 
    id_list=[]
    for post in posts:
        if "message" in post:
            post_id = post['id']
            message_dict[post_id] = post['message']
            id_list.append(post_id)
            thread=Thread(target=get_views,args=(page_id, post_id, views_dict) )
            thread.start()
            thread_list.append(thread)

    for thread in thread_list:
        thread.join()
    posts_info=[]
    for i in id_list:
        posts_info.append(  (message_dict[i], views_dict[i] ) )
    return render_template('show_posts.html', posts_info=(posts_info,next_page,page_id))



@app.route('/write', methods=['POST', 'GET'])
def write_page():
    """
    Recieves text from HTML form and makes POST api call to create a new page post 
    """
    #1480631468
    page_id = request.args['page_id']
    post_time = request.args['time']
    #bday=2016-11-10
    args={}
    if post_time is not None:
        pattern = '%Y-%m-%d'
        epoch_time=int(time.mktime(time.strptime(post_time, pattern)))
        print_me(epoch_time)
     
        args['scheduled_publish_time']=epoch_time

    args['message'] = request.args['text']
    args['published']= request.args['p_type'] == 'Published'

    """
    demo purposes"
    """
    #args['scheduled_publish_time']="1480631468"
    #args['published']="0"
    write_post(page_id, args)
    return render_template('write_done.html')


@app.route('/pages')
def main_page():
    """
    Main page that displays the pages owned/administered by the user
    """
    pages=get_accounts()
    return render_template('disp.html',pages=pages)



@app.route('/')
def index():
    # If a user was set in the get_current_user function before the request,
    # the user is logged in.
    if g.user:
        return render_template('index.html', app_id=FB_APP_ID,
                               app_name=FB_APP_NAME, user=g.user)
    # Otherwise, a user is not logged in.
    return render_template('login.html', app_id=FB_APP_ID, name=FB_APP_NAME)


@app.route('/logout')
def logout():
    """Log out the user from the application.

    Log out the user from the application by removing them from the
    session.  Note: this does not log the user out of Facebook - this is done
    by the JavaScript SDK.
    """
    session.pop('user', None)
    return redirect(url_for('index'))


@app.before_request
def get_current_user():
    """Set g.user to the currently logged in user.

    Called before each request, get_current_user sets the global g.user
    variable to the currently logged in user.  A currently logged in user is
    determined by seeing if it exists in Flask's session dictionary.

    If it is the first time the user is logging into this application it will
    create the user and insert it into the database.  If the user is not logged
    in, None will be set to g.user.
    """

    # Set the user in the session dictionary as a global g.user and bail out
    # of this function early.
    if session.get('user'):
        global mytoken
        g.user = session.get('user')
        mytoken=g.user['access_token']
        return

    # Attempt to get the short term access token for the current user.
    result = get_user_from_cookie(cookies=request.cookies, app_id=FB_APP_ID,
                                  app_secret=FB_APP_SECRET)

    # If there is no result, we assume the user is not logged in.
    if result:
        # Check to see if this user is already in our database.
        user = User.query.filter(User.id == result['uid']).first()

        if not user:
            # Not an existing user so get info
            graph = GraphAPI(result['access_token'])
            profile = graph.get_object('me')
            if 'link' not in profile:
                profile['link'] = ""

            # Create the user and insert it into the database
            user = User(id=str(profile['id']), name=profile['name'],
                        profile_url=profile['link'],
                        access_token=result['access_token'])
            db.session.add(user)
        elif user.access_token != result['access_token']:
            # If an existing user, update the access token
            user.access_token = result['access_token']

        # Add the user to the current session
        session['user'] = dict(name=user.name, profile_url=user.profile_url,
                               id=user.id, access_token=user.access_token)

    # Commit changes to the database and set the user as a global g.user
    db.session.commit()
    g.user = session.get('user', None)

def print_me(string):
    """
    used of debugging
    """
    print(string, file=sys.stderr)
