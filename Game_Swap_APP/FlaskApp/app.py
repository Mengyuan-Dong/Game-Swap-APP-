from flask import Flask, request, render_template, redirect, url_for, session, flash
from flaskext.mysql import MySQL
from datetime import datetime
import mysql.connector
import sql_query
from sql_query import *
from logging import FileHandler,WARNING
import json
from tkinter.messagebox import RETRY
from xml.dom.expatbuilder import Rejecter
from logging.config import dictConfig
from re import search

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})


app = Flask(__name__)
#random session secrect key
# when close the browser, the session value is deleted
app.secret_key="secrect_key"

@app.route('/')
def main():
    session.pop('_flashes', None)
    return render_template('login.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    session.pop('_flashes', None)
    email_or_phone=request.form['email_or_phone']
    password=request.form['password']
    user_db = log_in_check(email_or_phone, password)
    if len(user_db) == 0:
        return render_template('login.html', info = "email or phone number does not exist")
    else:
        if user_db[0][1]!= password:
            return render_template('login.html', info = "incorrect password")
        else: 
            # store user email in the session variable
            session ["email"]=user_db[0][0]
            return redirect(url_for("main_menu"))
            # return redirect(url_for("main_menu", email_or_phone=email_or_phone))
            # return main_menu(email_or_phone)

# redirect will only work if the argument of main_menu(email_or_phone) is also in /<>
# @app.route('/<usr>')
# def user(usr):
#     return f"<h1>{usr}</h1>"

# @app.route('/main_menu/<email_or_phone>', methods=['POST', 'GET'])
# def main_menu(email_or_phone):
# because we use session, no need to pass the argument from login() to main_menu()
@app.route('/main_menu', methods=['POST', 'GET'])
def main_menu():
    if "email" in session:
        email=session["email"]
        user_info= get_welcome_message(email)
        user_rating= get_user_rating(email)
        if  len(user_rating)==0:
            user_rating[0][0]="None"
        num_unaccepted_swap=get_num_unaccepted_swap(email)
        num_unrated_swap=get_num_unrated_swap(email)
        more_than_5d=get_5d(email)
        return render_template('main_menu.html', first=user_info[0][1], last=user_info[0][2], my_rating=user_rating[0][0], Unaccepted_swaps=num_unaccepted_swap[0][0],Unrated_swaps = num_unrated_swap[0][0],more_than_5d=more_than_5d )
    else:
        return redirect(url_for("logout")) 

@app.route('/propose_swap', methods=['POST', 'GET'])
def propose_swap():
    session.pop('_flashes', None)
    if "email" in session:
        email=session["email"]
        desired_item =session ["item_number_val"]
        # print ("desired_item" +desired_item)
        # session.pop('item_number_val', None)
        item_title = session ["title_val"]
        # session.pop('title_val', None)
        distance = session ["distance_val"]
        # session.pop('distance_val', None)
        # did not use form because it did not work. Maybe it is because there is another request.method=="POST"?
        # desired_item=request.form["desired_item"]
        # distance=request.form["distance"]
        # email=session["email"]
        user_item= get_user_item(email)
        # item_title = request.form["title"]
        # print (item_title)
        # if distance is None:
        #     distance=0
        if len(user_item)==0:
            return render_template('propose_confirm.html', swap="You have no items available for swap. You can return to the main menu.")
        else: 
            # need to change distance from None to 0 
            if  distance > 100:
                flash("The other user is " + str(distance) + " miles away!" ,"info")     
            if request.method=="POST":
                proposed_item=request.form['select']
                # if the user did not select any item and press the confirm button, show error message
                # check if the exact item-item swap has been rejected before
                check_SD=check_rejected_swap(desired_item,proposed_item)
                if check_SD[0][0] == 0:
                    formatted_date = datetime.now().strftime('%Y-%m-%d')
                    insert_propose(proposed_item, desired_item,formatted_date)
                    return render_template('propose_confirm.html', swap="You have confirmed the trade for  "+ str(item_title)+" with your item# "+str(proposed_item)+" .You can return to the main menu.")
                else:
                    return render_template('propose.html', distance= distance, len=len(user_item),r=user_item, info= item_title, swap="The exact item-for-item swap has been rejected before. Please choose a different item.")
            else:
                return render_template('propose.html', distance= distance, len=len(user_item),r=user_item, info= item_title)
    else:
        return redirect(url_for("logout")) 

@app.route('/logout')
def logout():
    # session.destroy()
    session.pop('_flashes', None)
    if "email" in session:
        email=session["email"]
    session.pop("email", None)
    return render_template('login.html', info = "You have logged out. Please log back in to continue.")


# hyc
@app.route("/search",methods=['GET','POST'])
def search():
    email=session["email"]
    # email='yating.lin10@gmail.com'
    def checkIfAny(keyword, title):
        if keyword.lower() in title.lower():
            return (1)
        return (0)
    
    if request.method=="POST":
        searchby=request.form['search']
        if searchby=="1":
            highlight=[]
            r=search_keyword(request.form['search_keyword'],email)
            for i in range(len(r)):
                highlight.append(checkIfAny(request.form['search_keyword'],r[i][1]))
            key=request.form['search_keyword']
            if len(r) ==0:
                return render_template('search.html', info = "No results found. Please start a new search!")
            return render_template('result.html', len=len(r),r=r,highlight=highlight,searchby=searchby,key=key)
        
        if searchby=='2':
            r=search_my_postal_code(email)
            if len(r) ==0:
                return render_template('search.html', info = "There is no item listed in your postal code")
            else:
                my_postal_code=r[0][11]
            return render_template('result.html', len=len(r),r=r,email=email,my_postal_code=my_postal_code)
        
        if searchby=="3":
            r=search_bymiles(request.form['search_miles'],email)
            miles=request.form['search_miles']
            if len(r) ==0:
                return render_template('search.html', info = "No results found. Please start a new search!")
            return render_template('result.html', len=len(r),r=r,miles=miles)
        
        if searchby=='4':
            r=search_by_postal_code(request.form['search_postalcode'],email)
            postal_code=request.form['search_postalcode']
            if len(r) ==0:
                return render_template('search.html', info = "There is no item found in the input postal code")
            return render_template('result.html', len=len(r),r=r,postal_code=postal_code)
    return render_template('search.html')

#hyc
@app.route("/list_item",methods=['GET','POST'])
def list_item():
    email=session["email"]
    unaccepted=get_num_unaccepted_swap(email)
    unrated=get_num_unrated_swap(email)
    una=unaccepted[0][0]
    unr=unrated[0][0]

    if una>5:
        return render_template('cannot_list.html',una=una)
    if unr>2:
        return render_template('cannot_list.html',unr=unr)
    if request.method=='POST':
        itemname=request.form['selectid']
        itemtitle=request.form['title']
        itemcondition=request.form['condition']
        itemdescription=request.form['description']
        r=insert_item(email,itemtitle,itemcondition,itemdescription)

        #puzzle:
        if itemname=='1':
            itempiececount=request.form['piececount']
            insert_puzzle(email,itempiececount)
            
        #video
        elif itemname=='2':
            videoplatform=request.form['platform']
            videomedia=request.form['media']
            insert_video(email,videoplatform,videomedia)
        #computer
        elif itemname=='5':
            computerplatform=request.form['computerplatform']
            insert_computer(email,computerplatform)
        # return redirect(url_for("main_menu"))

        #boardgame
        elif itemname=='3':
            insert_boardgame(email)

           #cardgame
        elif itemname=='4':
            insert_cardgame(email)
            
        return render_template('list_success_info.html',r=r)
    
    return render_template('list_item.html') 

# Yating - View Item Details (Project Description Pg 9)
@app.route("/view_item",methods=['GET','POST'])
def view_item_details():
    #Testing (getting from other web pages)
    user_email=session["email"]

    if request.method=='POST':
        input_item=request.form['detail']
    #get values for the table
        item_info = view_item(input_item, user_email)
        item_number_val = str(item_info[0][0])
        item_owner_val = item_info[0][1]
        title_val = item_info[0][2]
        game_type_val = item_info[0][9]
        name_val = item_info[0][5]
        piece_count_val = item_info[0][7]
        platform_val = item_info[0][8]
        media_val = item_info[0][6]
        condition_val = item_info[0][3]
        nickname_val = item_info[0][19]
        location_val = item_info[0][20]
        rating_val = item_info[0][22]
        distance_val = item_info[0][21]
        description_val = item_info[0][4]
        unaccepted_val = item_info[0][23]
        unrated_val = item_info[0][24]
        available_val = item_info[0][25]
        if distance_val is None:
            distance_val=0
        session ["item_number_val"]= item_number_val
        # print ("item_number_val" +item_number_val)
        session ["title_val"]=title_val
        session ["distance_val"]=distance_val
        
        return render_template('view_item.html', user_email=user_email, item_number=item_number_val, item_owner=item_owner_val, title=title_val,
                           game_type=game_type_val, platform=platform_val, media= media_val, name=name_val, piece_count=piece_count_val,
                           condition=condition_val, nickname=nickname_val, location=location_val, rating=rating_val, distance=distance_val,
                           description=description_val, unaccepted_swaps=unaccepted_val, unrated_swaps=unrated_val, available=available_val)

# Yating - Swap History (Project Description Pg 12)
@app.route("/swap_history",methods=['GET','POST'])
def swap_history():
    user_email = session["email"]
    if request.method == 'POST':
        deal_id = request.form['deal_id']
        role = request.form['my_role']
        rate_value = request.form['rate']
        #easier to find which deal is updated in database
        # print(deal_id)
        if role == "Proposer":
            update_desired_rating(user_email, rate_value, deal_id)
        else:
            update_proposed_rating(user_email, rate_value, deal_id)
    r = acc_rej_tbl(user_email)
    s = swap_history_tbl(user_email)
    if len(r) ==0 and len (s)==0:
        return render_template('swap_history.html', len=len(r), r=r, len_s=len(s), s=s)
    return render_template('swap_history.html', len=len(r), r=r, len_s=len(s), s=s)



# AL
@app.route("/registration", methods=['GET','POST'])
def register():
    if request.method == "GET":
        return render_template('registration.html')
    #read the posted values from the UI
    email = request.form['inputemail']
    password = request.form['inputpassword']
    firstname = request.form['inputfirstname']
    lastname = request.form['inputlastname']
    nickname = request.form['inputnickname']
    city = request.form['inputcity']
    state = request.form['inputstate']
    postalcode = request.form['inputpostalcode']
    phonenumber = request.form['inputphonenumber']
    phonetype = request.form['inputphonetype']
    isshareable = request.form.get('inputisshareable')

    #validate the received values
    a = email_in_use(email)
    b = phone_number_in_use(phonenumber, email)
    c = check_citystatepostal(postalcode,city,state)
   
    app.logger.info('email_in_use: %d', a)
    app.logger.info('phone_number_in_use: %d', b)
    app.logger.info('check_citystatepostal: %d', c)

    if email and password and firstname and lastname and nickname and city and state and postalcode  and phonetype:
        if  a != 0:
            return render_template('registration.html', info = "This email is already registered. Please use another one")
        elif b != 0:
            return render_template('registration.html', info = "This phone number is already used by other users. Please use another one.")
        elif c == 0:
            return render_template('registration.html', info = "Postal code doesn't match the city and state.")
        else:
            create_user_account(email, password, firstname, lastname, nickname,postalcode,phonenumber, phonetype, isshareable)
            # store user email in the session variable
            session ["email"] = email
            return redirect(url_for("main_menu"))
    else:
        field_error

def field_error():
    app.logger.warn('field_error')


@app.route("/update_user_info", methods=['GET','POST'])
def update_user_info():
    email = session["email"]
    registered_userinfo = get_registered_user_info(email)
    d = check_unaccepted_swaps(email)
    e = check_unrated_swaps(email)
    if request.method == "GET":
        if (d > 0) or (e > 0):
            return render_template('update_user_info_uns.html', info = "You have unapproved swaps or unrated swaps. Please solve before updating user information.")
        else: 
            return render_template('update_user_info.html',email=registered_userinfo[0][0], firstname=registered_userinfo[0][1],lastname=registered_userinfo[0][2],nickname=registered_userinfo[0][3],password=registered_userinfo[0][4],city=registered_userinfo[0][5],state=registered_userinfo[0][6],postalcode=registered_userinfo[0][7],phonenumber=registered_userinfo[0][8],phonetype=registered_userinfo[0][9])
    else: 
        #read the posted values from the UI
        password = request.form['inputpassword']
        firstname = request.form['inputfirstname']
        lastname = request.form['inputlastname']
        nickname = request.form['inputnickname']
        city = request.form['inputcity']
        state = request.form['inputstate']
        postalcode = request.form['inputpostalcode']
        phonenumber = request.form['inputphonenumber']
        phonetype = request.form['inputphonetype']
        isshareable = request.form.get('inputisshareable')

        #validate the received values
        b = phone_number_in_use(phonenumber, email)
        c = check_citystatepostal(postalcode,city,state)
        if password and firstname and lastname and nickname and city and state and postalcode and phonetype:
            if  b != 0:
                # print ("phone in use")
                return render_template('update_user_info.html', email=registered_userinfo[0][0], firstname=registered_userinfo[0][1],lastname=registered_userinfo[0][2],nickname=registered_userinfo[0][3],password=registered_userinfo[0][4],city=registered_userinfo[0][5],state=registered_userinfo[0][6],postalcode=registered_userinfo[0][7],phonenumber=registered_userinfo[0][8],phonetype=registered_userinfo[0][9],info = "This phone number is already used by other user. Please use another one")
            elif c == 0:
                return render_template('update_user_info.html', email=registered_userinfo[0][0], firstname=registered_userinfo[0][1],lastname=registered_userinfo[0][2],nickname=registered_userinfo[0][3],password=registered_userinfo[0][4],city=registered_userinfo[0][5],state=registered_userinfo[0][6],postalcode=registered_userinfo[0][7],phonenumber=registered_userinfo[0][8],phonetype=registered_userinfo[0][9],info = "Postal code doesn't match the city and state.")
            else:
                update_user_account(password, firstname, lastname, nickname,postalcode,phonenumber, phonetype, isshareable, email)
                registered_userinfo = get_registered_user_info(email)
                return render_template('update_user_info.html', email=registered_userinfo[0][0], firstname=registered_userinfo[0][1],lastname=registered_userinfo[0][2],nickname=registered_userinfo[0][3],password=registered_userinfo[0][4],city=registered_userinfo[0][5],state=registered_userinfo[0][6],postalcode=registered_userinfo[0][7],phonenumber=registered_userinfo[0][8],phonetype=registered_userinfo[0][9], info = "User information is successfully updated.")
        else:
            field_error


@app.route("/accept_reject_swaps", methods=['GET','POST'])
def accept_reject_swaps():
    email = session["email"]
    r=get_accept_reject_table_info(email)
    return render_template('accept_reject_swaps.html',len=len(r),r=r)

@app.route("/accept_request", methods=['POST'])
def accept_request():   
    dealID = request.form['dealID']
    email = session["email"]
    accept_reject_date = datetime.now().strftime('%Y-%m-%d')
    # print ("dealID "+dealID+" is accepted")
    accept_swap(accept_reject_date,dealID)
    # neither redirect or render template will refresh the page
    return redirect(url_for("accept_reject_swaps"))

@app.route("/reject_request", methods=['POST'])
def reject_request():
    dealID = request.form['dealID']
    email = session["email"]
    accept_reject_date = datetime.now().strftime('%Y-%m-%d')
    reject_swap(accept_reject_date,dealID)
    r=get_accept_reject_table_info(email)
    # print ("dealID "+dealID+" is rejected")
    # neither redirect or render template will refresh the page
    return render_template('accept_reject_swaps.html',len=len(r),r=r)

#yy    
@app.route('/my_item',methods = ['GET','POST'])
def my_item():
    # email = 'yating.lin9@gmail.com'
    email = session['email']
    count_result = item_counts(email)
    detail_result = my_item_detail(email)
    # session["item_number"] = 
    return render_template('my_item.html', count_result = count_result, detail = detail_result)
#yy
@app.route('/swap_detail',methods = ['GET','POST'])
def swap_detail():
    email = session['email']
    # dealID = session['dealID']
    # email = 'yating.lin7@gmail.com'
    if request.method=='POST':
        dealID=request.form['dealID']
        session['dealID'] = dealID
        swap_detail = get_swap_detail(email,dealID)
        user_detail = get_user_details(email,dealID)
        proposed_item = get_proposed_item(dealID)
        desired_item= get_desired_item(dealID)
        # if request.form['rated_dealID_rating'] is not None: 
        #     # dealID=request.form['rated_dealID']
        #     rate = request.form['rated_dealID_rating']
        #     if swap_detail[0][3] == "Proposer":
        #         update_counterparty_rate(rate,dealID)
        #         swap_detail = get_swap_detail(email,dealID)
        #         render_template('swap_detail.html', swap_detail = swap_detail)
        #     else:
        #         update_proposer_rate(rate,dealID)
        #         swap_detail = get_swap_detail(email,dealID)
        #         render_template('swap_detail.html', swap_detail = swap_detail)
    # print (dealID)
    # print (proposed_item)
    # print (desired_item)
    return render_template('swap_detail.html', swap_detail = swap_detail, user_detail= user_detail,proposed_item = proposed_item, desired_item  = desired_item)

@app.route('/swap_detail_rate',methods = ['GET','POST'])
def swap_detail_rated():
    email = session['email']
    dealID = session['dealID']
    swap_detail = get_swap_detail(email,dealID)
    user_detail = get_user_details(email,dealID)
    proposed_item = get_proposed_item(dealID)
    desired_item= get_desired_item(dealID)
    
    if request.method=='POST':
        rate =  request.form['rated_dealID_rating']
        if swap_detail[0][3] == "Proposer":
            update_counterparty_rate(rate,dealID)
            swap_detail = get_swap_detail(email,dealID)
            return render_template('swap_detail.html', swap_detail = swap_detail, user_detail= user_detail,proposed_item = proposed_item, desired_item  = desired_item)

        else:
            update_proposer_rate(rate,dealID)
            # print (swap_detail[0][3])

            swap_detail = get_swap_detail(email,dealID)
            return render_template('swap_detail.html', swap_detail = swap_detail, user_detail= user_detail,proposed_item = proposed_item, desired_item  = desired_item)
# yy
@app.route('/rate_swap',methods = ['GET','POST'])
def rate_swap():
    # email = "yating.lin10@gmail.com"
    email = session['email']
    rate_detail = get_rate_swap(email)
    if request.method == 'POST':
        dealID=request.form['rated_dealID']
        rate = request.form['rated_dealID_rating']
        if len(rate_detail) > 0:
            if rate_detail[0][2] == "Proposer":
                update_counterparty_rate(rate,dealID)
                rate_detail = get_rate_swap(email)
                render_template('rate_swap.html', rate_detail = rate_detail)
            else:
                update_proposer_rate(rate,dealID)
                rate_detail = get_rate_swap(email)
                render_template('rate_swap.html', rate_detail = rate_detail)
    return render_template('rate_swap.html', rate_detail = rate_detail)



if __name__ == "__main__":
    app.run()
