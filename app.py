#GETとPOSTの処理を明確に分ける（POSTはif文、GETはif文を使わずに下部に記述）

from flask import Flask,render_template,url_for,request,session,redirect
from random import choice
from quiz_dict_list_data import quiz_dict_list
import openai
import os

app = Flask(__name__)
app.secret_key = "shoya_secret"
openai.api_key = os.environ.get("OPENAI_API_KEY")

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

    #sessionにroundがなくて、methodがGET(ページアクセス（見るだけ）)のときに実行
    if "round" not in session and request.method == "GET":
        session["round"] = 0        #一定回数POSTを受けたら抜けられるように回数を記録しておく用のsession
        session["correct_count"] = 0   #正答数カウント用リスト
        session["result"] = []  #結果保管用リスト
        session["incorrect_result"] = [] #誤答した結果の辞書を格納するリスト

    #methodがデータ送信（何かを渡す・登録する）のときに実行
    if request.method == "POST":
        user_input = request.form.get("user_input")  #ユーザーの選択した値を受け取る
        quiz_dic = {"quiz": session["quiz"],"choices": session["choices"],"answer": session["answer"]}
        result = session.get("result",[])
        result.append([quiz_dic, user_input, session["round"]+1])  #result = [クイズの内容、ユーザーの選択肢、問題数]
        session["result"] = result #sessuinに再代入
        if user_input == quiz_dic["answer"]:
            session["correct_count"] += 1
        if user_input != quiz_dic["answer"]:
            incorrect_result = session.get("incorrect_result",[])
            incorrect_result.append([quiz_dic, user_input, session["round"]+1])
            session["incorrect_result"] = incorrect_result
        session["round"] += 1       #一回目のポストでsession["round"] = 1になる
        return redirect(url_for("index"))     #新しくいれたコード

        
    if session["round"] >= 15:
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
    #sessionをクリアするために一時変数に避難
    rendered = render_template("finish.html", result=session.get("result",[]), correct_count=session.get("correct_count"))
    
    incorrect_result = session["incorrect_result"]
    last_round = session["round"]
   
    session.clear()
    
    if incorrect_result:  #incorrect_resultに値が存在している場合のみsessionに戻す　　　新追加
        # 避難したsessionを再代入およびHTMLに渡す
        session["round"] = last_round
        session["incorrect_result"] = incorrect_result
    return rendered


#誤答解説用URL
@app.route("/explanation",methods=["GET","POST"])
def explanation():
    #session["incorrect_result"] = [クイズの内容(辞書型)、ユーザーの選択肢、問題数]
    #クイズの内容{"quiz": session["quiz"],"choices": session["choices"],"answer": session["answer"]}
    incorrect_result = session.get("incorrect_result", [])
    session.clear()
    #chatgptapiにクイズの内容を渡して答えの解答を出力させる
    for res in incorrect_result:
        quiz = res[0]["quiz"]
        choices = res[0]["choices"]
        answer = res[0]["answer"]
        user_answer = res[1]
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
            {
                "role": "system",
                "content": (
                    "あなたは一流の世界史の先生です。"
                    f"{quiz}の内容の問題に{choices}の選択肢がユーザーに与えられており、問題の正解は{answer}でユーザーは{user_answer}と答えて間違えています。"
                    "ユーザーの誤答を考慮しながら、クイズの内容より問題の解説を行ってください。"
                    "解説和分かりやすく、簡潔に行ってください"
                    )
            },
            {
                "role": "user",
                "content": (
                    "あなたは渡されたクイズの内容、選択肢、正解、ユーザーの解答（誤答）から問題の解説を分かりやすく丁寧に簡潔に行ってください"
                    "最初の相槌や最後の挨拶などはいりません。また、クイズ内容や選択肢の復唱もいりません"
                    "クイズの解説を述べることに神経を集中させてください"
                    "また前後の歴史的経緯も簡潔に述べてください"
                    "始まりと締めのあいさつ文は必要ありません"
                )
            }
        ],
            temperature=1.0,
            presence_penalty=1.0,
            frequency_penalty=1.0,
            max_tokens=1800
            
            )
        res.append(response.choices[0].message.content)
        
    return render_template("explanation.html",incorrect_result = incorrect_result)

@app.route("/start",methods=["GET","POST"])
def start():
    session.clear()
    return redirect(url_for("index"))
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    

"""rd_quiz = choice(quiz_dict_list) おなじセッション内？では同じ問題が選ばれないようにしたい"""
"""gloval変数を使っていると複数ユーザーがアクセスする際に高確率でバグが発生する
→sessionに保存することで解決"""""

"""問題数を増やす中級・上級問題も作成する(出題ページを分ける)"""
"""記述問題もつくる？"""
"""chatgptのapiキーとsessionのキーをVPSの環境変数に設定できるようにする"""
