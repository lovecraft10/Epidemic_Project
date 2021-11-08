from flask import Flask
from flask import render_template
import utils
from flask import jsonify
from jieba.analyse import extract_tags

app = Flask(__name__)



@app.route('/time')
def gettime():
    return utils.get_time()

@app.route('/c1')
def get_c1_data():
    data = utils.get_c1_data()
    return jsonify({'confirm':data[0], 'suspect':data[1], 'heal':data[2], 'dead':data[3]})

@app.route('/')
def hello_word():
    return render_template('main.html')

@app.route('/c2')
def get_c2_data():
    res = []
    for tup in utils.get_c2_data():
        res.append({"name":tup[0],"value":int(tup[1])})
    return jsonify({"data":res})

@app.route("/l1")
def get_l1_data():
    data = utils.get_l1_data()
    day,confirm,suspect,heal,dead = [],[],[],[],[]
    for a,b,c,d,e in data[:]:
        day.append(a.strftime("%m-%d")) #a是datatime类型
        confirm.append(b)
        suspect.append(c)
        heal.append(d)
        dead.append(e)
    return jsonify({"day":day,"confirm": confirm, "suspect": suspect, "heal": heal, "dead": dead})

@app.route("/l2")
def get_l2_data():
    data = utils.get_l2_data()
    day, confirm_add, suspect_add = [], [], []
    for a, b, c in data[7:]:
        day.append(a.strftime("%m-%d"))  # a是datatime类型
        confirm_add.append(b)
        suspect_add.append(c)
    return jsonify({"day": day, "confirm_add": confirm_add, "suspect_add": suspect_add})

@app.route("/r1")
def get_r1_data():
    progress = utils.get_r1_data()
    return progress


@app.route("/r2")
def get_r2_data():
    tf_dic = {}
    data = utils.get_r2_data()
    c = []
    d = []
    for i in data:
        content = i[0]
        words = extract_tags(content) #2.withWeight设置为True时可以显示词的权重 3.topK设置显示的词的个数
        d.extend(words)
    for word in d:
        # 遍历words 据k取v 存在则 +1  不存在则 =1
        tf_dic[word] = tf_dic.get(word, 0) + 1
    a = sorted(tf_dic.items(), key=lambda x: x[1], reverse=True)
    for i in a:
        c.append({"name": i[0], "value": i[1]})
    return jsonify({"kws": c})



if __name__ == '__main__':
    app.run(debug = True)
