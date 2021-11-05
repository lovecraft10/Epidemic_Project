from flask import request
from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World'

@app.route('/login')
def hello_world2():
    name = request.values.get("name")
    pwd = request.values.get("pwd")
    return f'name:{name}, pwd:{pwd}'

@app.route('/abc')
def hello_world1():
    id = request.values.get('id')
    return f"""
    <form action="/login"> 
        账号: <input name="name" value="{id}"> <br>
        密码: <input name="pwd">
        <input type="submit"> 
    </form> 
    """

@app.route('/tem')
def hello_world3():
    return render_template('index.html')


@app.route('/ajax', methods=['get', 'post'])
def hello_world4():
    return 'Hello World!!!!!!!!!!!!!!!'

if __name__ == '__main__':
    app.run(debug = True)