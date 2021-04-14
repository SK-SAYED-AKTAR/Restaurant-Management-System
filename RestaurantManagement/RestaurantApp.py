from flask import Flask, render_template, request, jsonify, json
import mysql.connector as connector

def getConnection():
    conn = connector.connect(
                    host="localhost",
                    port=3306,
                    username="root",
                    password="",
                    database="restaurant"
    )
    return conn

app = Flask(__name__)

#Fetch All Category From Database
def getAllTheCategory():
    con = getConnection()
    cur = con.cursor(buffered=True)
    query = "SELECT * FROM food_category ORDER BY sl"
    cur.execute(query)

    return cur


def getAllTheFoods():
    con = getConnection()
    cur1 = con.cursor()
    query = "SELECT food_name, food_cat FROM food_category, food_items WHERE food_category.sl = food_items.food_cat"
    cur1.execute(query)
    food = []
    f_food = []
    for a in cur1:
        food.append(a[0])
        f_food.append(a[1])

    values = []

    for food_name, num in zip(food, f_food):
        values.append(str(num)+"."+food_name)
    return values

#Find the food Id
def getTheFoodId(food_name):
    food_id = 0
    query = "SELECT sl from food_category WHERE food_category = '{}'".format(food_name)
    # print(query)
    con = getConnection()
    cursor = con.cursor()
    cursor.execute(query)
    for i in cursor:
        food_id = i[0]

    return food_id


@app.route('/')
def home():
    return render_template("index.html")

@app.route("/admin/")
def about():
    return render_template("adminAuthentication.html")


@app.route("/order/", methods=['POST', 'GET'])
def order():

    con = getConnection()
    cur = con.cursor()
    cur.execute("SELECT sl, food_category FROM food_category ORDER BY sl")

    food_categories = []
    food_categories_sl = []

    final_foods = []
    for i in cur:
        food_categories.append(i[1])
        food_categories_sl.append(i[0])

    for j, k in zip(food_categories_sl, food_categories):
        final_foods.append(str(j)+"."+str(k))
    conn = getConnection()
    cursor = conn.cursor()
    sql2 = "SELECT food_cat, food_name FROM food_items ORDER BY sl"
    food_items_are = []
    food_items_final = []
    food_cat_id = []
    cursor.execute(sql2)
    for i in cursor:
        print(i)
        food_cat_id.append(i[0])
        food_items_are.append(i[1])

    for i, j in zip(food_cat_id, food_items_are):
        food_items_final.append(str(i)+"."+str(j))

    conn = getConnection()
    cursor = conn.cursor()
    sql3 = "SELECT extra_name, product_name FROM food_extra ORDER BY sl"
    cursor.execute(sql3)
    extra_name = []
    for i in cursor:
        print(i)
        extra_name.append(str(i[1])+"."+str(i[0]))

    if request.method == "POST":
        return render_template("order.html", food_categories=final_foods,
                               food_items=food_items_final,
                               extra_name=extra_name, order=True)
    return render_template("order.html", food_categories=final_foods,
                                        food_items = food_items_final,
                                        extra_name = extra_name, order=False)


@app.route("/check/", methods=['POST'])
def check():
    values = request.args.get("extra")
    try:
        values = values.split(",")
    except:
        print("In except...")
    item = request.form["fooditems"]
    con = getConnection()
    cur = con.cursor()
    query = "SELECT sl FROM food_items WHERE food_name = '{}'".format(item)
    print("For get the id: "+query)
    cur.execute(query)
    for i in cur:
        id = i[0]

    for k in values:
        sql = "INSERT INTO food_extra(extra_name, product_name) VALUES('{}', {})".format(k, id)
        print(sql)
        con = getConnection()
        cur = con.cursor()
        cur.execute(sql)
        con.commit()
    return "<h1> Hi {} </h1> {{ item }}".format(values)


@app.route("/additems/", methods=['POST', 'GET'])
def addItems():

    if request.method == "POST":
        name = request.form['name']
        passwrd = request.form['password']
        if name == "admin" and passwrd == "root":
            items = []
            foods = []
            f_food = []
            food_name = []
            product = getAllTheCategory()
            foods_item = getAllTheFoods()
            for i in product:
                print(i)
                items.append(i[1])
                foods.append(i[0])

            for j in foods_item:
                f_food.append(j[2])
                food_name.append(j[1])

            print(f_food, food_name)
            return render_template("additems.html", items=list((i for i in zip(foods, items))), food_are=list((j for j in zip(f_food, food_name))))
        else:
            return """
                    <center>
                        <h1>You Have Entered Wrong Credential</h1>
                        <p style="font-size: 20px";>Username: admin and Password: root, use it.</p>
                    </center>
            """
    else:
        #return render_template("adminAuthentication.html")
        items = []
        foods = []

        product = getAllTheCategory()

        foods_are = getAllTheFoods()


        for i in product:
            items.append(i[1])
            foods.append(i[0])
        return render_template("additems.html", items=list((i for i in zip(foods, items))), food_are=foods_are)


#Add food category
@app.route("/add_category/", methods=["POST", "GET"])
def add_category():
    if request.method == "POST":
        category = request.form["cat"]
        trim = str(category.strip())

        if trim == "":
            return render_template("add_category.html", trim=True)

        duplicate = False
        result = False
        if category:
            try:
                query = "INSERT INTO food_category(food_category) VALUES('{}')".format(category)
                print(query)
                con=getConnection()
                cursor = con.cursor()
                cursor.execute(query)
                con.commit()
                duplicate = False
                result = True
            except:
                result = False
                duplicate = True
            return render_template("add_category.html", duplicate=duplicate, result=result)
    else:
        return render_template("add_category.html")

#Add food items
@app.route("/add_food/", methods=["POST", "GET"])
def add_food():
    duplicate = False
    food_category = request.args.get('cat')
    index = 0
    finalIndex = 0
    for i in food_category:
        if i.isalpha():
            finalIndex = index
            break
        else:
            index = index + 1
    food_category = food_category[finalIndex:len(food_category)]
    food_id = getTheFoodId(food_category)
    if request.method == "POST":
        food_name = request.form['food_name']

        try:
            print("Try")
            query = "INSERT INTO food_items(food_name, food_cat) VALUES('{}', {})".format(food_name, food_id)
            print(query)
            con = getConnection()
            cursor = con.cursor()
            cursor.execute(query)
            con.commit()
        except:
            duplicate = True
        finally:
            return render_template("add_food.html")
    else:
        return render_template("add_food.html", food_category=food_category)

if __name__ == "__main__":
    app.run(debug=True, port=2020)