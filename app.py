from flask import Flask, render_template, session, redirect, request, url_for, flash
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField
from wtforms.validators import DataRequired
from passlib.hash import sha256_crypt
import Symptoms as sym
from sentiment import nb
app = Flask(__name__)
import pandas as pd
from werkzeug.datastructures import MultiDict


app = Flask(__name__)

mysql = MySQL(app)

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='doctor'
app.config['MYSQL_CURSORCLASS']='DictCursor'


@app.route('/',methods=['POST','GET'])
def hello():
    cur = mysql.connection.cursor()
    selected=0
    result = cur.execute("SELECT * FROM dis_spec")
    dis_spec = cur.fetchall()

    result=None
    if request.method=='POST':
        symp=request.form['sym']
        selected=symp.split(",")
        result=sym.Symptoms.predict(0,symp)
        for d in dis_spec:
            if(d['disease']==result):
                print(d)
                result=d['speciality']
                print(result)

    suggestions=None
    spec = result
    print(spec)
    cur.execute("SELECT * FROM doctors INNER JOIN rank on rank.id=doctors.id where speciality= %s ORDER BY rank.total_liked desc ",[spec])
    suggestions = cur.fetchall()
    symptoms=sym.Symptoms.symptoms(0)
    return render_template("home.html",symptoms=symptoms,selected=selected,result=result,suggestions=suggestions)


class RecDoc(Form):
    
    speciality = SelectField(
        'Choose :',
        choices= [],
        validators=[DataRequired()]
    )

@app.route('/speciality', methods = ['GET','POST'])
def index():

    form=RecDoc(request.form)
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT DISTINCT (speciality) FROM doctors")

    doctors = cur.fetchall()
    form.speciality.choices=[(d['speciality'],d['speciality'])for d in doctors]
    result=None
    if request.method == 'POST' and form.validate():
        spec = form.speciality.data
        print(spec)
        cur.execute("SELECT * FROM doctors INNER JOIN rank on rank.id=doctors.id where speciality= %s ORDER BY rank.total_liked desc LIMIT 3 ",[spec])
        result = cur.fetchall()
    print(result)

    return render_template('speciality.html', doctors=doctors, form=form, result=result)

@app.route('/doctors')
def doctors():
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM doctors")

    doctors = cur.fetchall()

    return render_template('doctors.html', doctors=doctors)


class CommentForm(Form):
    comment=TextAreaField('Comment',[validators.Length(min=1,max=500)], render_kw={'rows': 8})

@app.route('/doctor/<string:id>', methods = ['GET','POST'])
def info(id):
    form= CommentForm(request.form)

    cur = mysql.connection.cursor()

    if request.method == 'POST' and form.validate():
        comment = form.comment.data
        cur.execute("INSERT INTO reviews (id,review) VALUES(%s,%s)",([id],comment))
        flash('Your comment has been successfully submitted','success')
        mysql.connection.commit()

    result = cur.execute("SELECT * FROM doctors where id= %s",[id])

    doctor = cur.fetchone()

    result = cur.execute("SELECT * FROM reviews where id= %s",[id])

    reviews = cur.fetchall()
    cur.close()
    return render_template('info.html', info=doctor, reviews=reviews, form=form)

# The admin panel starts
@app.route('/admin',methods=['POST','GET'])
def admin():
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT DISTINCT (speciality) FROM doctors")
    speciality = cur.fetchall()

    result = cur.execute("SELECT * FROM dis_spec")
    dis_spec = cur.fetchall()

    diseases=sym.Symptoms.diseases(0)

    if request.method=='POST':
        symp=request.form.to_dict()
        for key,val in symp.items():
            print(key)
            print(val)
            available=0
            for d in dis_spec:
                if(d['disease']==key):
                    cur.execute("UPDATE dis_spec set speciality=%s where disease=%s",[val,key])
                    available=1
                    mysql.connection.commit()
                    return redirect("admin")

            if(available==0):
                cur.execute("insert into dis_spec values(%s,%s)",[key,val])
                mysql.connection.commit()
                return redirect("admin")
    
    return render_template("dis_to_spec.html",diseases=diseases,speciality=speciality,dis_spec=dis_spec) 

@app.route('/nb')
def nbreviews():

    cur = mysql.connection.cursor()

    cur.execute(" select rank.id,name,total_liked from rank inner join doctors on rank.id=doctors.id")
    result = cur.fetchall()

    return render_template('nb.html',result=result)

@app.route('/nb/fit')
def fitreviews():
    cur = mysql.connection.cursor()

    result = cur.execute("SELECT * FROM reviews")
    reviews = cur.fetchall()

    result = cur.execute("SELECT * FROM pos")
    pos = cur.fetchall()

    result = cur.execute("SELECT * FROM neg")
    neg = cur.fetchall()

    test=nb.fit(0,pos,neg,reviews)
    res=pd.DataFrame(test)
    res=res[res.liked != 0]

    freq = pd.crosstab(res["id"],columns="liked")

    cur.execute("DELETE FROM RANK")

    for k in zip(freq.index,freq.liked):
        print(str(k[0])+' and '+str(k[1]))
        cur.execute("INSERT INTO RANK(id,total_liked) VALUES(%s,%s)",(k[0],k[1]))

    mysql.connection.commit()

    cur.execute(" select rank.id,name,total_liked from rank inner join doctors on rank.id=doctors.id")
    result = cur.fetchall()

    return render_template('fit.html', result=result)


if __name__=='__main__':
    app.secret_key= 'secret123'
    app.run(debug=True)