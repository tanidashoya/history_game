#GETとPOSTの処理を明確に分ける（POSTはif文、GETはif文を使わずに下部に記述）

from flask import Flask,render_template,url_for,request,session,redirect
from random import choice
from quiz_dict_list_data import quiz_dict_list

app = Flask(__name__)

app.secret_key = "shoya_secret"
correct_count = 0   #正答数カウント用リスト
result = []  #結果保管用リスト

class Quiz:
    def __init__(self, num, quiz, choices, answer):
        self.num = num
        self.quiz = quiz
        self.choices = choices
        self.answer = answer

#メソッドが何でも実行されたときに実行
@app.before_request
def before():
    if request.method == "GET" and "round" not in session:
        session.clear()

# 最初に表示されるページ
@app.route("/",methods=["GET","POST"])
def index():
    global correct_count
    global result   
    
    #sessionにroundがなくて、methodがGET(ページアクセス（見るだけ）)のときに実行
    if "round" not in session and request.method == "GET":
        session["round"] = 0        #一定回数POSTを受けたら抜けられるように回数を記録しておく用のsession

    #methodがデータ送信（何かを渡す・登録する）のときに実行
    if request.method == "POST":
        user_input = request.form.get("user_input")  #ユーザーの選択した値を受け取る
        quiz_dic = {"quiz": session["quiz"],"choices": session["choices"],"answer": session["answer"]}
        result.append([quiz_dic, user_input, session["round"]+1])  #result = [クイズの内容、ユーザーの選択肢、問題数]
        if user_input == quiz_dic["answer"]:
            correct_count += 1
        session["round"] += 1       #一回目のポストでsession["round"] = 1になる
        return redirect(url_for("index"))     #新しくいれたコード

        
    if session["round"] >= 20:
        return redirect("/finish")
    
   
    rd_quiz = choice(quiz_dict_list)  #同じブラウザ内（クッキー内）では同じ問題が出ないようにしたい
    quiz_inst = Quiz(rd_quiz["番号"], rd_quiz["問題"], rd_quiz["選択肢"], rd_quiz["正解"])   #quizインスタンスを作成 
     #sessionに直接インスタンスは渡せないのでそれぞれ属性ごとに渡す
    session["quiz"] = quiz_inst.quiz
    session["choices"] = quiz_inst.choices
    session["answer"] = quiz_inst.answer
    
    
    round_count = session["round"] + 1        
    #quizインズタンスをHTML側に渡して問題文を表示することはできないのでsessionの値を渡す
    return render_template("index.html", quiz = session["quiz"], choices = session["choices"], answer = session["answer"], round_count = round_count)

#採点結果URL
@app.route("/finish",methods=["GET","POST"])
def finish():
    global result  #問題や解答の辞書、ユーザーの入力、問題番号が入ったリスト：[ [{},user_input,1], [{},user_input,2], ・・・]
    global correct_count
    
    return render_template("finish.html", result = result, correct_count = correct_count)


#誤答解説用URL
@app.route("/explanation",methods=["GET","POST"])
def explanation():
    global result
    
    return render_template("explanation.html")




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    

"""rd_quiz = choice(quiz_dict_list) おなじセッション内？では同じ問題が選ばれないようにしたい"""