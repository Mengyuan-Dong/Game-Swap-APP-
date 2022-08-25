import mysql.connector

# constants for MySQL server configuration
USERNAME = "team038"
PASSWORD = "gatech"
HOST = "127.0.0.1"
DATABASE = "cs6400_sp22_team038"


mydb = mysql.connector.connect(
    user = "team038",
    password = "gatech",
    host = "127.0.0.1",
    database = "cs6400_sp22_team038")

# configure the connection between python and MySQL
# def setup_mysql_connection(username=USERNAME, password=PASSWORD, host=HOST, database_name=DATABASE):
# def setup_mysql_connection(username=USERNAME, password=PASSWORD, host=HOST, database_name=DATABASE):
#     mydb = mysql.connector.connect(
#     user=USERNAME, password=PASSWORD, host=HOST, database=DATABASE)
#     return mydb

# cursor = cnx.cursor()
# cursor.execute("SELECT first_name, last_name FROM User")
# myresult = cursor.fetchall()

# for x in myresult:
#   print(x)


def log_in_check(input_1, input_2):
    # mydb = setup_mysql_connection()
    cursor = mydb.cursor()
    sql_query_str = "SELECT u.email, u.password From User u LEFT JOIN Phone p on u.email = p.email WHERE u.email = '" + input_1 + "' OR p.phone_number = '" + input_1 + "';"
    cursor.execute(sql_query_str)
    user_info = []
    for r in cursor:
        user_info.append(r)
    return user_info

def get_welcome_message(email_or_phone):
    # mydb = setup_mysql_connection()
    userinfo_cursor = mydb.cursor()
    sql_query_str1 = "SELECT u.email, u.first_name, u.last_name From User u LEFT JOIN Phone p on u.email = p.email WHERE u.email = '" + email_or_phone + "' OR p.phone_number = '" + email_or_phone + "';"
    userinfo_cursor.execute(sql_query_str1)
    userinfo = []
    for r in userinfo_cursor:
        userinfo.append(r)
    return userinfo

def get_num_unaccepted_swap(email):
    # mydb = setup_mysql_connection()
    user_unas_cursor = mydb.cursor()
    sql_query_str2 = "SELECT COUNT(*) AS unaccepted_swap FROM (User u JOIN Item i ON u.email=i.email JOIN SwappingDeal s ON i.item_number = s.desired_item_number) WHERE u.email = '" + email + "' AND s.status IS NULL;"
    user_unas_cursor.execute(sql_query_str2)
    userinfo = []
    for r in user_unas_cursor:
        userinfo.append(r)
    return userinfo

def get_num_unrated_swap(email):
    # mydb = setup_mysql_connection()
    user_unrs_cursor = mydb.cursor()
    sql_query_str3 ="SELECT COUNT(*) AS unrated_swap \
    FROM User u JOIN Item i ON u.email=i.email JOIN SwappingDeal s ON (i.item_number = s. desired_item_number AND s.proposed_rating IS NULL) OR (i.item_number = s. proposed_item_number AND s.desired_rating IS NULL)\
    WHERE u.email = '" +  email  + "' AND s.status IS TRUE;"
    user_unrs_cursor.execute(sql_query_str3)
    userinfo = []
    for r in user_unrs_cursor:
        userinfo.append(r)
    return userinfo

def get_user_rating(email):
    # mydb = setup_mysql_connection()
    userrating_cursor = mydb.cursor()
    sql_query_str = "SELECT  ROUND(AVG(rating),2) AS rating \
    FROM ( \
	(SELECT s.proposed_rating as rating \
	FROM User u JOIN Item i on u.email = i.email JOIN SwappingDeal s on i.item_number = s.proposed_item_number \
	WHERE u.email = '" + email + "')\
	UNION \
	(SELECT s.desired_rating as rating \
	FROM User u JOIN Item i on u.email = i.email JOIN SwappingDeal s on i.item_number = s.desired_item_number \
	WHERE u.email = '" + email + "' ) \
    ) as user_rating;"
    userrating_cursor.execute(sql_query_str)
    userrating = []
    for r in userrating_cursor:
        userrating.append(r)
    return userrating

def get_user_item(email):
    # mydb = setup_mysql_connection()
    #add left join
    user_item_cursor = mydb.cursor()
    sql_query_str = "WITH Table_item_type AS ( \
(SELECT 'Video Game' As type, item_number FROM VideoGame) \
UNION \
(SELECT 'Puzzle' as type, item_number FROM Puzzle) \
UNION \
(SELECT 'Board Game' as type, item_number FROM BoardGame) \
UNION \
(SELECT 'Computer Game' as type, item_number FROM \
ComputerGame) \
UNION \
(SELECT 'Card Game' as type, item_number FROM CardGame)) \
SELECT * FROM (SELECT i.item_number, t.type, i.title, i.condition \
FROM Item i LEFT JOIN Table_item_type t ON i.item_number = t.item_number \
WHERE i.item_number IN (SELECT i.item_number \
FROM User u JOIN Item i on u.email = i.email WHERE u.email = '" + email + "')) AS t1 WHERE \
t1.item_number NOT IN (SELECT item_number FROM Item i JOIN SwappingDeal s on i.item_number = s.desired_item_number OR i.item_number = s.proposed_item_number \
WHERE s.status IS NOT FALSE);"
    user_item_cursor.execute(sql_query_str)
    r=user_item_cursor.fetchall()
    return r

def get_item_title(item_number):
    # mydb = setup_mysql_connection()
    cursor = mydb.cursor()
    sql_query_str = "SELECT title FROM Item WHERE item_number =item_number;"
    cursor.execute(sql_query_str)
    r=cursor.fetchall()
  
    return r

def get_5d(email):
    # mydb = setup_mysql_connection()
    cursor = mydb.cursor()
    sql_query_str = "SELECT COUNT(*) AS get_5d FROM (User u JOIN Item i ON u.email=i.email JOIN SwappingDeal s ON i.item_number = s.desired_item_number) WHERE u.email = '" + email + "' AND s.status IS NULL AND CURDATE()-DATE(s.proposed_date)>5; "
    cursor.execute(sql_query_str)
    r=cursor.fetchall()
    if r[0][0]==0:
        r=0
    else:
        r=1
    return r
# check if the exact arrangement of items has been rejected before
def check_rejected_swap(desired_item,proposed_item):
    # mydb = setup_mysql_connection()
    cursor = mydb.cursor()
    sql_query_str = "SELECT COUNT(*) AS rejected_swap FROM SwappingDeal s WHERE s.desired_item_number= "+str(desired_item)+" AND s.proposed_item_number= "+ str(proposed_item) +" ;"
    cursor.execute(sql_query_str)
    r=cursor.fetchall()
    return r

def insert_propose(proposed_item_number,desired_item_number,formatted_date):
    # mydb = setup_mysql_connection()
    cursor = mydb.cursor()
    sql_query_str = "INSERT INTO `SwappingDeal`(`dealID`, `proposed_item_number`, `desired_item_number`, `proposed_date`, `accept_reject_date`, `status`, `desired_rating`, `proposed_rating`) VALUES (NULL,'%s','%s','%s',NULL,NULL,NULL,NULL);"
    cursor.execute(sql_query_str % (proposed_item_number,desired_item_number,formatted_date))
    r=cursor.fetchall()
    mydb.commit()
    return r
    


# AL
def email_in_use(input_1):
    cursor=mydb.cursor()
    sql_str="SELECT count(email) FROM User WHERE email='"+input_1+"'"
    cursor.execute(sql_str)
    result = cursor.fetchone()
    return result[0]


def phone_number_in_use(phonenumber, email):
    cursor=mydb.cursor()
    sql_str="SELECT count(phone_number) FROM Phone WHERE phone_number='"+phonenumber+"' AND email <> '"+email+"'"
    cursor.execute(sql_str)
    result = cursor.fetchone()
    return result[0]

def check_citystatepostal(postal,city,state):
    cursor=mydb.cursor()
    sql_str="SELECT count(*) FROM Address WHERE postal_code='"+postal+"' AND city= '"+city+"' AND state= '"+state+"'"
    cursor.execute(sql_str)
    result = cursor.fetchone()
    return result[0]

def create_user_account(email, password, firstname, lastname, nickname, postal,phonenumber, phonetype, Isshareable):
    try:
        cursor=mydb.cursor()
        cursor.execute(
            "INSERT INTO User (email, password, first_name, last_name, nickname, postal_code) VALUES (%s, %s, %s, %s, %s, %s)",
            (email, password, firstname, lastname, nickname, postal))
        cursor.execute(
            "INSERT INTO Phone (phone_number, phone_type, Is_shareable, email) VALUES (%s, %s, %s, %s)",
            (phonenumber, phonetype, Isshareable, email))
        mydb.commit()
    except:
        traceback.print_exc()
        # print("An error has occured")

def get_registered_user_info(email):
    cursor=mydb.cursor()
    sql_str = "SELECT u.email, u.first_name, u.last_name, u.nickname, u.password, a.city, a.state, a.postal_code, p.phone_number, p.phone_type From User u LEFT JOIN Phone p on u.email = p.email JOIN Address a on u.postal_code = a.postal_code WHERE u.email = '" + email + "' ;"
    cursor.execute(sql_str)
    registered_userinfo = []
    for r in cursor:
        registered_userinfo.append(r)
    return registered_userinfo

def check_unaccepted_swaps(email):
    cursor=mydb.cursor()
    sql_str="SELECT COUNT(*) AS unaccepted_swap FROM (User u JOIN Item i ON u.email=i.email JOIN SwappingDeal s ON i.item_number = s.desired_item_number) WHERE u.email = '"+email+"' AND status IS NULL;"
    cursor.execute(sql_str)
    result = cursor.fetchone()
    return result[0]
    
def check_unrated_swaps(email):
    cursor=mydb.cursor()
    # sql_str="SELECT COUNT(*) AS unrated_swap FROM (User u JOIN Item i ON u.email=i.email JOIN SwappingDeal s ON (i.item_number = s. desired_item_number AND s.desired_rating IS NULL) OR (i.item_number = s. proposed_item_number AND s.proposed_rating IS NULL)) WHERE u.email = '"+email+"';"
    sql_str="SELECT COUNT(*) AS unrated_swap \
    FROM (User u JOIN Item i ON u.email=i.email JOIN SwappingDeal s ON (i.item_number = s. desired_item_number AND s.proposed_rating IS NULL) OR (i.item_number = s. proposed_item_number AND s.desired_rating IS NULL))\
    WHERE u.email = '" +  email  + "' AND s.status IS TRUE;"
    cursor.execute(sql_str)
    result = cursor.fetchone()
    return result[0]

def update_user_account(password, firstname, lastname, nickname, postal, phonenumber, phonetype, Isshareable, email):
    try:
        cursor=mydb.cursor()
        cursor.execute("""
            UPDATE User 
            SET password=%s, first_name=%s, last_name=%s, nickname=%s, postal_code=%s 
            WHERE email=%s;
            """, (password, firstname, lastname, nickname, postal, email))
        cursor.execute("""
            UPDATE Phone 
            SET phone_number=%s, phone_type=%s, Is_shareable=%s
            WHERE email=%s;
        """, (phonenumber, phonetype, Isshareable, email))       
        mydb.commit()
    except:
        traceback.print_exc()
        # print("An error has occured")


def get_accept_reject_table_info(email):
    cursor=mydb.cursor(buffered=True)
    sql_str ="""WITH rating 
                AS (SELECT  email, ROUND(AVG(rating),2) AS rating 
                    FROM ( 
                (SELECT u.email, s.proposed_rating AS rating 
                    FROM User u 
                    JOIN Item i on u.email = i.email 
                    JOIN SwappingDeal s on i.item_number = s.proposed_item_number
                    )
                    UNION 
                    (SELECT u.email, s.desired_rating as rating 
                    FROM User u 
                    JOIN Item i on u.email = i.email 
                    JOIN SwappingDeal s on i.item_number = s.desired_item_number
                )) as user_rating
                GROUP BY email)
                
                SELECT proposed_date AS `Date`, i.title AS desired_item, u2.nickname AS proposer, r.rating,
                ROUND(3959 *ACOS(cos(radians(a.latitude)) *
                            cos(radians(a2.latitude)) 
                        * cos(radians(a.longitude) - radians(a2.longitude))
                        + sin( radians(a.latitude) ) * sin(radians(a2.latitude))),1) AS Distance
                ,i2.title AS proposed_item, u2.email AS proposer_email, u2.first_name AS proposer_firstname, p2.phone_number AS proposer_phonenumber, p2.is_shareable, s.dealID, u.email AS counterparty_email, i.item_number AS desired_item_number, i2.item_number AS proposed_item_number  
                FROM swappingdeal s 
                JOIN Item i ON s.desired_item_number = i.item_number 
                JOIN Item i2 ON s.proposed_item_number = i2.item_number 
                JOIN User u ON i.email = u.email 
                JOIN User u2 ON i2.email = u2.email  
                LEFT JOIN rating r ON i2.email=r.email
                JOIN Address a ON u.postal_code=a.postal_code -- Join to get counterparty's longitude and latitude
                JOIN Address a2 ON u2.postal_code=a2.postal_code -- Join to get proposer's longitude and latitude
                LEFT JOIN Phone p2 ON u2.email=p2.email
                WHERE i.email = '%s' and `status` is null;"""
    cursor.execute(sql_str % (email))
    result = cursor.fetchall()
    #print ("hello")
    #print(result)
    return result


def accept_swap(accept_reject_date,dealID):
    try:
        cursor=mydb.cursor()
        cursor.execute("""
            UPDATE SwappingDeal
            SET accept_reject_date=%s, status = TRUE
            WHERE dealID = %s;
            """, (accept_reject_date,dealID))     
        mydb.commit()
    except:
        traceback.print_exc()
        # print("An error has occured")    

def reject_swap(accept_reject_date,dealID):
    try:
        cursor=mydb.cursor()
        cursor.execute("""
            UPDATE SwappingDeal
            SET accept_reject_date=%s, status = FALSE
            WHERE dealID=%s;
            """, (accept_reject_date,dealID))     
        mydb.commit()
    except:
        traceback.print_exc()
        # print("An error has occured")    


# Yating - Accept/Reject Table (Project Description Pg 12 Top table)
# This should not include pending swaps
def acc_rej_tbl(cur_user):
    acc_rej_cursor = mydb.cursor()
    sql_query_str3 = \
    """WITH my_role_table AS (
    (SELECT 'Proposer' as my_role, s.dealID, s.status
    FROM SwappingDeal s JOIN item i ON i.item_number=s.proposed_item_number
    JOIN user u ON u.email=i.email
    WHERE u.email = '{cur_user}')
    UNION
    (SELECT 'Counterparty' as my_role, s.dealID, s.`status`
    FROM SwappingDeal s JOIN item i ON i.item_number=s.desired_item_number 
    JOIN user u ON u.email=i.email
    WHERE u.email = '{cur_user}')
    )
    SELECT my_role_table.my_role,
    COUNT(*) AS 'Total',
    SUM(CASE WHEN `status`=1 THEN 1 ELSE 0 END) AS 'Accepted', 
    SUM(CASE WHEN `status`=0 THEN 1 ELSE 0 END) AS 'Rejected',
    FORMAT(SUM(CASE WHEN `status`=0 THEN 1 ELSE 0 end) / COUNT(*) * 100, 2) as 'Rejected %'
    FROM my_role_table 
    WHERE `status` IS NOT NULL 
    GROUP BY my_role;
    ;""".format(cur_user=cur_user)
    acc_rej_cursor.execute(sql_query_str3)
    r = acc_rej_cursor.fetchall()
    return r


# Yating - Swap History Table (Project Description Pg 12 2nd table)
def swap_history_tbl(cur_user):
    # cnx = setup_mysql_connection()
    swap_history_cursor = mydb.cursor()
    sql_query_str4 = \
    """WITH my_role_table AS
    ((SELECT 'Proposer' as my_role, s.dealID
    FROM SwappingDeal s JOIN item i ON i.item_number=s.proposed_item_number
    JOIN user u on u.email=i.email
    WHERE u.email = '{cur_user}')
    UNION
    (SELECT 'Counterparty' as my_role, s.dealID
    FROM SwappingDeal s JOIN item i ON i.item_number=s.desired_item_number 
    JOIN user u on u.email=i.email
    WHERE u.email = '{cur_user}'))
    
    SELECT s.dealID,
    s.proposed_date, s.accept_reject_date, 
    CASE WHEN s.`status` =1 THEN 'Accepted' ELSE 'Rejected' END AS swap_status, 
    ro.my_role, 
    ip.title AS proposed_item, 
    id.title AS desired_item, 
    CASE WHEN ro.my_role ='Proposer' THEN ud.nickname ELSE up.nickname END AS other_user,
    CASE WHEN ro.my_role ='Proposer' THEN desired_rating ELSE proposed_rating END AS rating
    FROM my_role_table ro 
    JOIN SwappingDeal s ON ro.dealID=s.dealID
    JOIN Item ip ON s.proposed_item_number=ip.item_number 
    JOIN Item id ON s.desired_item_number=id.item_number 
    JOIN User up ON ip.email = up.email
    JOIN User ud ON id.email = ud.email
    WHERE s.`status` IS NOT NULL
    ORDER BY accept_reject_date DESC, proposed_date;
    ;""".format(cur_user=cur_user)
    swap_history_cursor.execute(sql_query_str4)
    s = swap_history_cursor.fetchall()
    return s


# Yating - If my role is proposer, update desired_rating in `SwappingDeal`Table
def update_desired_rating(cur_user, rate, dealID):
    # cnx = setup_mysql_connection()
    desired_rating_cursor =  mydb.cursor()
    sql_query_str5 = \
    """UPDATE SwappingDeal SET desired_rating = {rate} WHERE (dealID = {dealID});
    ;""".format(cur_user=cur_user, rate=rate, dealID=dealID)
    desired_rating_cursor.execute(sql_query_str5)
    mydb.commit()


# Yating - If my role is counterparty, update proposed_rating in `SwappingDeal`Table
def update_proposed_rating(cur_user, rate, dealID):
    # cnx = setup_mysql_connection()
    proposed_rating_cursor =  mydb.cursor()
    sql_query_str6 = \
    """UPDATE SwappingDeal SET proposed_rating = {rate} WHERE (dealID = {dealID});
    ;""".format(cur_user=cur_user, rate=rate, dealID=dealID)
    proposed_rating_cursor.execute(sql_query_str6)
    mydb.commit()


# Yating - View Item Details (Project Description Pg 9)
def view_item(item_number, cur_user):
    # cnx = setup_mysql_connection()
    iteminfo_cursor =  mydb.cursor()
    sql_query_str2 = \
    """WITH Table_item_type AS 
    (
    (SELECT 'Video Game' as game_type, item_number FROM VideoGame)
    UNION
    (SELECT 'Puzzle' as game_type, item_number FROM Puzzle)
     UNION
    (SELECT 'Board Game' as game_type, item_number FROM BoardGame)
     UNION
    (SELECT 'Computer Game' as game_type, item_number FROM ComputerGame)
    UNION
    (SELECT 'Card Game' as game_type, item_number FROM CardGame)
    )
    ,unaccepted_swap AS (
    SELECT COUNT(*) AS unaccepted_swap
    FROM (User u JOIN Item i ON u.email=i.email JOIN SwappingDeal s ON i.item_number = s.desired_item_number)
    WHERE u.email = '{cur_user}' AND s.status IS NULL
    ) 
    , unrated_swap AS (
    SELECT COUNT(*) AS unrated_swap
    FROM User u JOIN Item i ON u.email=i.email 
    JOIN SwappingDeal s ON (i.item_number = s.desired_item_number AND s.proposed_rating IS NULL) OR (i.item_number = s.proposed_item_number AND s.desired_rating IS NULL)
    WHERE u.email = '{cur_user}' AND s.status IS TRUE
    )
    , cur_user_loc AS (
    SELECT u.email AS cur_user 
    	, u.postal_code AS cur_postal_code
    	, a.longitude AS cur_longitude
        , a.latitude AS cur_latitude
    FROM User u
    LEFT JOIN Address a ON u.postal_code = a.postal_code
    WHERE u.email = '{cur_user}' 
    )
    , avg_rating AS (
    SELECT email,ROUND(AVG(rating),2) AS rating
    FROM (
    	(SELECT u.email, s.proposed_rating as rating
    	FROM User u LEFT JOIN Item i on u.email = i.email LEFT JOIN SwappingDeal s ON i.item_number = s.proposed_item_number)
    	UNION 
    	(SELECT u.email, s.desired_rating as rating
    	FROM User u LEFT JOIN Item i on u.email = i.email LEFT JOIN SwappingDeal s on i.item_number = s.desired_item_number)
        ) as t1
        GROUP BY 1
    )
    , in_deal AS (
    SELECT Item_number, 0 as available_for_swap
    FROM Item i JOIN SwappingDeal s ON i.item_number = s.desired_item_number OR i.item_number = s.proposed_item_number 
    WHERE `status` IS NOT FALSE 
    )
    SELECT i.*
	    , v.name
        , v.media
        , p.piece_count
        , c.platform
    	, t.game_type
        , u.nickname
        , u.postal_code
        , a.longitude
        , a.latitude
        , a.city
        , a.state
        , '{cur_user}' AS cur_user
        , cloc.cur_longitude
        , cloc.cur_latitude
        , CASE WHEN i.email<>cur_user THEN u.nickname ELSE Null END AS offered_by
        , CASE WHEN i.email<>cur_user THEN CONCAT(a.city, ', ', a.state, ' ', u.postal_code) ELSE Null END AS offered_by_loc
        , CASE WHEN i.email<>cur_user THEN ROUND(3959 *ACOS( cos( radians(a.latitude) ) *
                  cos( radians(cloc.cur_latitude) ) 
            * cos( radians( a.longitude) - radians(cloc.cur_longitude) )
            + sin( radians(a.latitude) ) * sin(radians(cloc.cur_latitude))),1) ELSE Null END AS distance
    	, CASE WHEN i.email<>cur_user THEN avgr.rating ELSE Null END AS rating
    	, unaccepted_swap
        , unrated_swap
        , CASE WHEN available_for_swap = 0 THEN 0 ELSE 1 END AS available_for_swap
    From Item i
    LEFT JOIN VideoGame v ON i.item_number = v.item_number
    LEFT JOIN Puzzle p ON i.item_number = p.item_number
    LEFT JOIN ComputerGame c ON i.item_number = c.item_number
    LEFT JOIN Table_item_type t ON i.item_number = t.item_number
    LEFT JOIN User u ON i.email = u.email
    LEFT JOIN Address a ON u.postal_code = a.postal_code
    LEFT JOIN cur_user_loc cloc ON cur_user = cloc.cur_user
    LEFT JOIN avg_rating avgr ON i.email = avgr.email
    JOIN unaccepted_swap
    JOIN unrated_swap 
    LEFT JOIN in_deal i2 ON i.item_number = i2.item_number
    WHERE i.item_number = {item_number}
    ;""".format(cur_user=cur_user, item_number=item_number)
    iteminfo_cursor.execute(sql_query_str2)
    iteminfo = []
    for r in iteminfo_cursor:
        iteminfo.append(r)
    return iteminfo

    
def search_keyword(a,b):
#     mycursor=mydb.curso
# r()
    mycursor=mydb.cursor()
    sql_str="""with Table_item_type AS ( 
(SELECT 'Video Game'as type, item_number FROM VideoGame) UNION 
(SELECT 'Puzzle' as type, item_number FROM Puzzle) 
UNION 
(SELECT 'Board Game' as type, item_number FROM BoardGame) UNION 
(SELECT 'Computer Game' as type, item_number FROM ComputerGame) 
UNION 
(SELECT 'Card Game' as type, item_number FROM CardGame) )  
,match_keyword AS (SELECT i.title, i.description, i.item_number from Item i WHERE i.title like '%"""+"%s" % a +"%' OR i.description like '%"+"%s" % a +"""%'
AND i.item_number NOT IN (SELECT item_number FROM Item i JOIN SwappingDeal s on i.item_number = s.desired_item_number OR i.item_number = s.proposed_item_number WHERE status IS NOT FALSE) 
AND i.item_number NOT IN (SELECT item_number FROM User u JOIN Item i on u.email = i.email WHERE u.email = '{b}'))
, cur_user_loc AS (
SELECT u.email AS cur_user 
	, u.postal_code AS cur_postal_code
	, a.longitude AS cur_longitude
    , a.latitude AS cur_latitude
FROM User u
LEFT JOIN Address a ON u.postal_code = a.postal_code
WHERE u.email = '{b}'
)
SELECT mk.item_number
, mk.title
, i.condition
, mk.description
, t.type
, '{b}' AS cur_user
, a.longitude
, a.latitude
, cloc.cur_longitude
, cloc.cur_latitude
,ROUND(3959 *ACOS( cos( radians(a.latitude) ) *
              cos( radians(cloc.cur_latitude) ) 
        * cos( radians( a.longitude) - radians(cloc.cur_longitude) )
        + sin( radians(a.latitude) ) * sin(radians(cloc.cur_latitude))),1)AS distance
FROM User u 
JOIN Item i on u.email = i.email 
JOIN Table_item_type t ON i.item_number = t.item_number 
JOIN match_keyword mk ON i.item_number = mk.item_number
JOIN Address a ON u.postal_code = a.postal_code
JOIN cur_user_loc cloc ON cur_user = cloc.cur_user WHERE i.email<>cur_user
ORDER BY distance;
""".format(b=b)
    mycursor.execute(sql_str)
    r=mycursor.fetchall()
    return (r)


def search_bymiles(a,b):
    mycursor=mydb.cursor()
    sql_str="""with Table_item_type AS ( 
(SELECT 'Video Game'as type, item_number FROM VideoGame) UNION 
(SELECT 'Puzzle' as type, item_number FROM Puzzle) 
UNION 
(SELECT 'Board Game' as type, item_number FROM BoardGame) UNION 
(SELECT 'Computer Game' as type, item_number FROM ComputerGame) 
UNION 
(SELECT 'Card Game' as type, item_number FROM CardGame) )
, cur_user_loc AS (
SELECT u.email AS cur_user 
	, u.postal_code AS cur_postal_code
	, a.longitude AS cur_longitude
    , a.latitude AS cur_latitude
FROM User u
LEFT JOIN Address a ON u.postal_code = a.postal_code
WHERE u.email = '{b}' 
)
SELECT i.item_number
, i.title
, i.condition
, i.description
, t.type
, '{b}' AS cur_user
, a.longitude
, a.latitude
, cloc.cur_longitude
, cloc.cur_latitude
 , ROUND(3959 *ACOS( cos( radians(a.latitude) ) *
              cos( radians(cloc.cur_latitude) ) 
        * cos( radians( a.longitude) - radians(cloc.cur_longitude) )
        + sin( radians(a.latitude) ) * sin(radians(cloc.cur_latitude))),1) AS distance
FROM User u 
JOIN Item i on u.email = i.email 
JOIN Table_item_type t ON i.item_number = t.item_number 
JOIN Address a ON u.postal_code = a.postal_code
JOIN cur_user_loc cloc ON cur_user = cloc.cur_user
where i.email<>cur_user
AND i.item_number NOT IN (SELECT item_number FROM Item i JOIN SwappingDeal s on i.item_number = s.desired_item_number OR i.item_number = s.proposed_item_number WHERE status IS NOT FALSE) 
having distance<{a}
ORDER BY distance;""".format(b=b,a=a)
    mycursor.execute(sql_str)
    r=mycursor.fetchall()
    return(r)


def search_by_postal_code(a,b):
    mycursor=mydb.cursor()
    sql_str="""with Table_item_type AS ( 
(SELECT 'Video Game'as type, item_number FROM VideoGame) UNION 
(SELECT 'Puzzle' as type, item_number FROM Puzzle) 
UNION 
(SELECT 'Board Game' as type, item_number FROM BoardGame) UNION 
(SELECT 'Computer Game' as type, item_number FROM ComputerGame) 
UNION 
(SELECT 'Card Game' as type, item_number FROM CardGame) )
, cur_user_loc AS (
SELECT u.email AS cur_user 
	, u.postal_code AS cur_postal_code
	, a.longitude AS cur_longitude
    , a.latitude AS cur_latitude
FROM User u
LEFT JOIN Address a ON u.postal_code = a.postal_code
WHERE u.email = '{b}' 
)
SELECT i.item_number
, i.title
, i.condition
, i.description
, t.type
, '{b}' AS cur_user
,a.postal_code
, a.longitude
, a.latitude
, cloc.cur_longitude
, cloc.cur_latitude
 , ROUND(3959 *ACOS( cos( radians(a.latitude) ) *
              cos( radians(cloc.cur_latitude) ) 
        * cos( radians( a.longitude) - radians(cloc.cur_longitude) )
        + sin( radians(a.latitude) ) * sin(radians(cloc.cur_latitude))),2)AS distance
FROM User u 
JOIN Item i on u.email = i.email 
JOIN Table_item_type t ON i.item_number = t.item_number 
JOIN Address a ON u.postal_code = a.postal_code
JOIN cur_user_loc cloc ON cur_user = cloc.cur_user
where a.postal_code='{a}' and i.email<>cur_user
AND i.item_number NOT IN (SELECT item_number FROM Item i JOIN SwappingDeal s on i.item_number = s.desired_item_number OR i.item_number = s.proposed_item_number WHERE status IS NOT FALSE) 
ORDER BY distance;;""".format(b=b,a=a)
    mycursor.execute(sql_str)
    r=mycursor.fetchall()
    return(r)
        
def search_my_postal_code(b):
    mycursor=mydb.cursor()
    sql_str="""with Table_item_type AS ( 
(SELECT 'Video Game'as type, item_number FROM VideoGame) UNION 
(SELECT 'Puzzle' as type, item_number FROM Puzzle) 
UNION 
(SELECT 'Board Game' as type, item_number FROM BoardGame) UNION 
(SELECT 'Computer Game' as type, item_number FROM ComputerGame) 
UNION 
(SELECT 'Card Game' as type, item_number FROM CardGame) )
, cur_user_loc AS (
SELECT u.email AS cur_user 
	, u.postal_code AS cur_postal_code
	, a.longitude AS cur_longitude
    , a.latitude AS cur_latitude
FROM User u
LEFT JOIN Address a ON u.postal_code = a.postal_code
WHERE u.email = '{b}' 
)
SELECT i.item_number
, i.title
, i.condition
, i.description
, t.type
, '{b}' AS cur_user
, a.longitude
, a.latitude
, cloc.cur_longitude
, cloc.cur_latitude
 , ROUND(3959 *ACOS( cos( radians(a.latitude) ) *
              cos( radians(cloc.cur_latitude) ) 
        * cos( radians( a.longitude) - radians(cloc.cur_longitude) )
        + sin( radians(a.latitude) ) * sin(radians(cloc.cur_latitude))),1) AS distance
,a.postal_code
FROM User u 
JOIN Item i on u.email = i.email 
JOIN Table_item_type t ON i.item_number = t.item_number 
JOIN Address a ON u.postal_code = a.postal_code
JOIN cur_user_loc cloc ON cur_user = cloc.cur_user
WHERE a.postal_code=cloc.cur_postal_code
AND i.item_number NOT IN (SELECT item_number FROM Item i JOIN SwappingDeal s on i.item_number = s.desired_item_number OR i.item_number = s.proposed_item_number WHERE status IS NOT FALSE) 
AND i.email<>cur_user
ORDER BY distance;""".format(b=b)
    mycursor.execute(sql_str)
    r=mycursor.fetchall()
    return(r)


def insert_item(b,itemtitle,itemcondition,itemdescription):
    mycursor=mydb.cursor()
    sql_str="""INSERT INTO Item (item_number,email, title, `condition`, description ) 
VALUES (NULL, '%s', '%s', '%s', "%s");"""
    mycursor.execute(sql_str % (b,itemtitle,itemcondition,itemdescription))
    mydb.commit()
    sql_str_get_itemnumber="""Select max(item_number) from Item where email='%s'"""
    mycursor.execute(sql_str_get_itemnumber % (b))
    item_num=mycursor.fetchall()
    item=item_num[0][0]
    return item

def insert_puzzle(email,itempiececount):
    mycursor=mydb.cursor()
    sql_str_get_itemnumber="""Select max(item_number) from Item where email='%s'"""
    mycursor.execute(sql_str_get_itemnumber % (email))
    item_num=mycursor.fetchall()
    item=item_num[0][0]
    # print(item)
    sql_str_puzzle="""INSERT INTO Puzzle(item_number, piece_count) 
VALUES (%s, %s);"""
    mycursor.execute(sql_str_puzzle % (item,itempiececount))
    mydb.commit()

def insert_video(email,videoplatform,videomedia):
    mycursor=mydb.cursor()
    sql_str_get_itemnumber="""Select max(item_number) from Item where email='%s'"""
    mycursor.execute(sql_str_get_itemnumber % (email))
    item_num=mycursor.fetchall()
    sql_str_video="""INSERT INTO VideoGame (item_number, name, media)
VALUES (%s, '%s', '%s');"""
    mycursor.execute(sql_str_video % (item_num[0][0],videoplatform,videomedia))
    mydb.commit()

def insert_computer(email,computerplatform):
    mycursor=mydb.cursor()
    sql_str_get_itemnumber="""Select max(item_number) from Item where email='%s'"""
    mycursor.execute(sql_str_get_itemnumber % (email))
    item_num=mycursor.fetchall()
    sql_str_computer="""INSERT INTO ComputerGame (item_number, platform)
VALUES (%s, '%s');"""
    mycursor.execute(sql_str_computer % (item_num[0][0],computerplatform))
    mydb.commit()

def insert_cardgame(email):
    mycursor=mydb.cursor()
    sql_str_get_itemnumber="""Select max(item_number) from Item where email='%s'"""
    mycursor.execute(sql_str_get_itemnumber % (email))
    item_num=mycursor.fetchall()
    sql_str_card="""INSERT INTO CardGame (item_number)
VALUES (%s);"""
    mycursor.execute(sql_str_card % (item_num[0][0]))
    mydb.commit()

def insert_boardgame(email):
    mycursor=mydb.cursor()
    sql_str_get_itemnumber="""Select max(item_number) from Item where email='%s'"""
    mycursor.execute(sql_str_get_itemnumber % (email))
    item_num=mycursor.fetchall()
    sql_str_board="""INSERT INTO BoardGame (item_number)
VALUES (%s);"""
    mycursor.execute(sql_str_board % (item_num[0][0]))
    mydb.commit()

#yy
def item_counts(email):
    #email = 
    cursor =mydb.cursor()
    sql_query_str = """(SELECT COUNT(*) as number, 'BoardGame' as type
                    FROM BoardGame b JOIN Item i on b.item_number = i.item_number
                    WHERE email= '{email}' 
                    AND i.item_number NOT IN (
	                SELECT i.item_number FROM 
                    User u JOIN Item i ON u.email=i.email JOIN BoardGame b ON i.item_number = b.item_number JOIN SwappingDeal s ON b.item_number = s.desired_item_number OR b.item_number = s.proposed_item_number
                    WHERE status IS NOT FALSE))
                    UNION
                    (SELECT COUNT(*) as number, 'CardGame' as type
                    FROM CardGame c1 JOIN Item i on c1.item_number = i.item_number
                    WHERE email= '{email}' 
                    AND i.item_number NOT IN (
	                SELECT i.item_number FROM 
                    User u JOIN Item i ON u.email=i.email JOIN CardGame c1 ON i.item_number = c1.item_number JOIN SwappingDeal s ON c1.item_number = s.desired_item_number OR c1.item_number = s.proposed_item_number
                    WHERE status IS NOT FALSE))
                    UNION
                    (SELECT COUNT(*) as number, 'ComputerGame' as type
                    FROM ComputerGame c JOIN Item i on c.item_number = i.item_number
                    WHERE email= '{email}' 
                    AND i.item_number NOT IN (
	                SELECT i.item_number FROM 
                    User u JOIN Item i ON u.email=i.email JOIN ComputerGame c ON i.item_number = c.item_number JOIN SwappingDeal s ON c.item_number = s.desired_item_number OR c.item_number = s.proposed_item_number
                    WHERE status IS NOT FALSE))
                    UNION
                    (SELECT COUNT(*) as number, 'Puzzle' as type
                    FROM Puzzle p JOIN Item i on p.item_number = i.item_number
                    WHERE email= '{email}' 
                    AND i.item_number NOT IN (
	                SELECT i.item_number FROM 
                    User u JOIN Item i ON u.email=i.email JOIN Puzzle p ON i.item_number = p.item_number JOIN SwappingDeal s ON p.item_number = s.desired_item_number OR p.item_number = s.proposed_item_number
                    WHERE status IS NOT FALSE))
                    UNION
                    (SELECT COUNT(*) as number, 'VideoGame' as type
                    FROM VideoGame v JOIN Item i on v.item_number = i.item_number
                    WHERE email= '{email}'
                    AND i.item_number NOT IN (
	                SELECT i.item_number FROM 
                    User u JOIN Item i ON u.email=i.email JOIN VideoGame v ON i.item_number = v.item_number JOIN SwappingDeal s ON v.item_number = s.desired_item_number OR v.item_number = s.proposed_item_number
                    WHERE status IS NOT FALSE))
                    UNION
                    (SELECT COUNT(*) as number, 'Total' as type
                    FROM Item
                    WHERE email= '{email}'
                    AND item_number NOT IN (
	                SELECT i.item_number FROM 
                    User u JOIN Item i ON u.email=i.email JOIN SwappingDeal s ON i.item_number = s.desired_item_number OR i.item_number = s.proposed_item_number
                    WHERE status IS NOT FALSE));""".format(email = email)
    cursor.execute(sql_query_str)
    count_result =[]
    for i in cursor:
        count_result.append(i[0])
    return(count_result)
#yy
def my_item_detail(email):
    # add left join
    cursor =mydb.cursor()
    sql_query_str1 = """WITH Table_item_type AS 
                        ((SELECT 'Video Game' as game_type, item_number FROM VideoGame)
                        UNION
                        (SELECT 'Puzzle' as game_type, item_number FROM Puzzle)
                        UNION
                        (SELECT 'Board Game' as game_type, item_number FROM BoardGame)
                        UNION
                        (SELECT 'Computer Game' as game_type, item_number FROM ComputerGame)
                        UNION
                        (SELECT 'Card Game' as game_type, item_number FROM CardGame))
                        SELECT * FROM
                        (SELECT i.item_number, t.game_type, i.title, i.condition, i.description
                        FROM Item i JOIN Table_item_type t ON t.item_number=i.item_number
                        WHERE email= '{email}' ORDER BY Item_number DESC) AS t1
                        WHERE item_number NOT IN(SELECT item_number FROM User u JOIN Item i ON u.email=i.email JOIN SwappingDeal s ON i.item_number = s.desired_item_number OR i.item_number = s.proposed_item_number
													WHERE s.status IS NOT FALSE)
                        ORDER BY Item_number;""".format(email = email)
    cursor.execute(sql_query_str1)
    result_table = []
    for i in cursor:
        result_table.append(i)
  
    return result_table


#yy
def get_item_detail(item_number):
    cursor =mydb.cursor()
    sql_query_str = """SELECT i.item_number, i.title,t.game_type ,i.condition
FROM Item i JOIN ((SELECT 'Video Game' as game_type, item_number FROM VideoGame)
UNION
(SELECT 'Puzzle' as game_type, item_number FROM Puzzle)
 UNION
(SELECT 'Board Game' as game_type, item_number FROM BoardGame)
 UNION
(SELECT 'Computer Game' as game_type, item_number FROM ComputerGame)
UNION
(SELECT 'Card Game' as game_type, item_number FROM CardGame)
) as t ON i.item_number = t.item_number
WHERE i.item_number = '{item_number}';""".format(item_number = item_number)
    cursor.execute(sql_query_str)
    result_table = []
    for i in cursor:
        result_table.append(i)
    return result_table
#yy
def get_swap_detail(email,dealID):
    cursor =mydb.cursor()
    sql_query_str = """SELECT proposed_date,accept_reject_date, CASE WHEN `status`= 1  THEN 'Accepted' ELSE 'Rejected' END AS swap_status, my_role, rating
FROM ((SELECT s.proposed_date, s.accept_reject_date, s.status, 'Proposer' as my_role, desired_rating AS rating
FROM SwappingDeal s JOIN item i ON i.item_number=s.proposed_item_number
JOIN user u on u.email=i.email
WHERE u.email='{email}' AND dealID= '{dealID}')
UNION
(SELECT s.proposed_date, s.accept_reject_date, s.status, 'Counterparty' as my_role, proposed_rating AS rating
FROM SwappingDeal s JOIN item i ON i.item_number=s.desired_item_number 
JOIN user u on u.email=i.email
WHERE u.email='{email}' AND dealID= '{dealID}')) as sd;""".format(email = email,dealID = dealID)
    cursor.execute(sql_query_str)
    result_table = []
    for i in cursor:
        result_table.append(i)
    return result_table
#yy
def get_user_details(email,dealID):
    cursor =mydb.cursor()
    sql_query_str = """WITH proposer AS(SELECT u.nickname, u.first_name,u.email, p.phone_number,p.phone_type ,a. longitude,a.latitude FROM SwappingDeal s JOIN Item  i  ON s.proposed_item_number = i.item_number  JOIN User u ON u.email = i.email JOIN Address a ON u.postal_code = a.postal_code LEFT JOIN  phone  p ON u.email =p.email and  p.is_shareable is TRUE WHERE s.dealID  = {dealID}),
		  counterparty AS (SELECT u.nickname, u.first_name,u.email, p.phone_number,p.phone_type,a.longitude,a.latitude FROM  SwappingDeal  s  JOIN  Item i ON s.desired_item_number = i.item_number JOIN User u  ON u.email = i.email JOIN Address a ON u.postal_code = a.postal_code  LEFT JOIN  Phone p ON u.email = p.email and is_shareable  is TRUE WHERE  s.dealID  = {dealID}),
          distance AS (SELECT  ROUND(3959 *ACOS( cos( radians(a.latitude) ) *cos( radians(b.latitude) ) 
        * cos( radians( a.longitude) - radians(b.longitude ) )+ sin( radians(a.latitude) ) * sin(radians(b.latitude))),1)AS distance
				FROM proposer a, counterparty b)
SELECT a.nickname,  d.distance, a.first_name, a.email, a.phone_number,a.phone_type
FROM (SELECT *
FROM proposer 
UNION 
SELECT * 
FROM counterparty) as a, distance d
HAVING email <> '{email}';""".format(email = email,dealID = dealID)
    cursor.execute(sql_query_str)
    def phone_format(n):                                                                                                                                  
        return format(int(n[:-1]), ",").replace(",", "-") + n[-1] 
    cursor_result = []
    result_table = []
    for i in cursor:
        cursor_result.append(i)
    for i in range(len(cursor_result)):
        tmp = []
        for cell in cursor_result[i]:
          tmp.append(cell)
        result_table.append(tmp)
    # print (result_table[0][4])
    if result_table[0][4] is not None:
        # print (result_table[0][5])
        result_table[0][4] = phone_format(result_table[0][4]) + '(' + result_table[0][5] + ')'
        
    return result_table
#yy
def get_proposed_item(dealID):
    cursor =mydb.cursor()
    # changd to left join
    sql_query_str ="""SELECT s.proposed_item_number, i.title, t.game_type, i.condition, i.description,v.media, p.piece_count, c.platform
FROM SwappingDeal s JOIN Item i ON s.proposed_item_number =  i.item_number LEFT JOIN 
((SELECT 'Video Game' as game_type, item_number FROM VideoGame)
UNION
(SELECT 'Puzzle' as game_type, item_number FROM Puzzle)
 UNION
(SELECT 'Board Game' as game_type, item_number FROM BoardGame)
 UNION
(SELECT 'Computer Game' as game_type, item_number FROM ComputerGame)
UNION
(SELECT 'Card Game' as game_type, item_number FROM CardGame)) AS t ON i.item_number =t.item_number
LEFT JOIN VideoGame v ON i.item_number = v.item_number
LEFT JOIN Puzzle p ON i.item_number = p.item_number
LEFT JOIN ComputerGame c ON i.item_number = c.item_number
WHERE dealID = '{dealID}';""".format(dealID =dealID)
    cursor.execute(sql_query_str)
    result_table = []
    for i in cursor:
        result_table.append(i)
    # print (result_table)
    return result_table
#yy
def get_desired_item(dealID):
    cursor =mydb.cursor()
    # changd to left join
    sql_query_str ="""SELECT s.desired_item_number, i.title, t.game_type, i.condition, i.description,v.media, p.piece_count, c.platform
FROM SwappingDeal s JOIN Item i ON s.desired_item_number =  i.item_number LEFT JOIN 
((SELECT 'Video Game' as game_type, item_number FROM VideoGame)
UNION
(SELECT 'Puzzle' as game_type, item_number FROM Puzzle)
 UNION
(SELECT 'Board Game' as game_type, item_number FROM BoardGame)
 UNION
(SELECT 'Computer Game' as game_type, item_number FROM ComputerGame)
UNION
(SELECT 'Card Game' as game_type, item_number FROM CardGame)) AS t ON i.item_number =t.item_number 
LEFT JOIN VideoGame v ON i.item_number = v.item_number
LEFT JOIN Puzzle p ON i.item_number = p.item_number
LEFT JOIN ComputerGame c ON i.item_number = c.item_number
WHERE dealID = '{dealID}';""".format(dealID = dealID)
    cursor.execute(sql_query_str)
    result_table = []
    for i in cursor:
        result_table.append(i)
    # print (result_table)
    return result_table

#yy
def get_rate_swap(email):
    cursor =mydb.cursor()
    sql_query_str ="""WITH my_role_table AS
    ((SELECT 'Proposer' as my_role, s.dealID
    FROM SwappingDeal s JOIN item i ON i.item_number=s.proposed_item_number
    JOIN user u on u.email=i.email
    WHERE u.email= "{email}")
    UNION
    (SELECT 'Counterparty' as my_role, s.dealID
    FROM SwappingDeal s JOIN item i ON i.item_number=s.desired_item_number 
    JOIN user u on u.email=i.email
    WHERE u.email= "{email}"))
    ,Other_user_table AS
    (SELECT  u.nickname as other_user, s.dealID
    FROM Item i JOIN SwappingDeal s 
    ON i.item_number=s.desired_item_number OR i.item_number=s.proposed_item_number
    JOIN user u ON u.email=i.email
    WHERE u.email<> "{email}" )
    ,desired_item AS
    (SELECT i.title as desired_item, s.dealID FROM Item i JOIN SwappingDeal s ON i.item_number=s.desired_item_number)
    ,proposed_item AS
    (SELECT i.title as proposed_item,s.dealID FROM Item i JOIN SwappingDeal s ON i.item_number=s.proposed_item_number)
    SELECT s.dealID,s.accept_reject_date AS acceptance_date, my_role_table.my_role as my_role, desired_item.desired_item,proposed_item.proposed_item,Other_user_table.other_user
    FROM (User u JOIN Item i ON u.email=i.email
    JOIN SwappingDeal s ON (i.item_number = s. desired_item_number AND s.proposed_rating IS NULL) OR (i.item_number = s. proposed_item_number AND s.desired_rating IS NULL)
    JOIN my_role_table ON my_role_table.dealID=s.dealID
    JOIN Other_user_table ON Other_user_table.dealID=s.dealID
    JOIN proposed_item ON proposed_item.dealID=s.dealID
    JOIN desired_item ON desired_item.dealID=s.dealID)
    WHERE u.email = "{email}" and s.status is TRUE;""".format(email = email)
    cursor.execute(sql_query_str)
    result_table = []
    for i in cursor:
        result_table.append(i)
    return result_table

def update_proposer_rate(rate,dealID):
    cursor =mydb.cursor()
    sql_query_str = """UPDATE SwappingDeal SET proposed_rating = "{rate}" WHERE dealID = "{dealID}";""".format(rate = rate, dealID = dealID)
    cursor.execute(sql_query_str)
    mydb.commit()
    return

def update_counterparty_rate(rate,dealID):
    cursor =mydb.cursor()
    sql_query_str = """UPDATE SwappingDeal SET desired_rating = "{rate}" WHERE dealID = "{dealID}";""".format(rate = rate, dealID = dealID)
    cursor.execute(sql_query_str)
    mydb.commit()
    return