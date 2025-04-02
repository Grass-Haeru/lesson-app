import os
from flask import Flask, request, jsonify, render_template
from datetime import datetime
import openai
import random
import base64
from io import BytesIO
from PIL import Image

app = Flask(__name__)

tag=1

# ChatGPT APIキーの設定
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not client:
    raise ValueError("OPENAI_API_KEY が設定されていません。環境変数にAPIキーを設定してください。")

# ログファイルの作成
current_date = datetime.now().strftime("%Y%m%d")
current_dir = os.path.dirname(os.path.abspath(__file__))
new_dir_log = os.path.join(current_dir, f"chatlog")
new_dir_date = os.path.join(new_dir_log, f"{current_date}_chatlog")

os.makedirs(new_dir_log, exist_ok=True)
os.makedirs(new_dir_date, exist_ok=True)

new_dir_images = os.path.join(new_dir_date, "image")
os.makedirs(new_dir_images, exist_ok=True)

current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
file_path = os.path.join(new_dir_date, f"{current_time}.txt")
CHAT_LOG_FILE = file_path

print(f"チャットログディレクトリと画像ログディレクトリが作成されました: {file_path},{new_dir_images}")


# 過去ログを保持する変数
conversation_history = []

# ホームページのルート
@app.route('/')
def index():
    return render_template('index.html')  # templates/index.htmlを表示

# 画像をbase64でエンコードする関数
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_student_name(text):
    if text.startswith("太郎"):
        return 1
    elif text.startswith("花子"):
        return 2
    elif text.startswith("次郎"):
        return 3
    elif text.startswith("美咲"):
        return 4
    return None  # 名前が見つからない場合

# 先生からの質問を受け取り、ChatGPTが生徒として返答するAPI
@app.route('/chat', methods=['POST'])
def chat():
    try:
        global conversation_history
        data = request.form

        question = data.get('question', '')
        num_students = data.get('num_students', 3)
        target = data.get('target','')
        view = data.get('view','')
        grade = data.get('grade','')
        Taro_correct = data.get('Taro_correct','40')
        Taro_wrong = data.get('Taro_wrong','30')
        Taro_idk = data.get('Taro_idk','30')
        Hanako_correct = data.get('Hanako_correct','40')
        Hanako_wrong = data.get('Hanako_wrong','30')
        Hanako_idk = data.get('Hanako_idk','30')
        Jiro_correct = data.get('Jiro_correct','40')
        Jiro_wrong = data.get('Jiro_wrong','30')
        Jiro_idk = data.get('Jiro_idk','30')
        Misaki_correct = data.get('Misaki_correct','40')
        Misaki_wrong = data.get('Misaki_wrong','30')
        Misaki_idk = data.get('Misaki_idk','30')
        subject = data.get('subject','')
        # nomination = int(data.get('nomination',''))

        image_file=data.get('image') #画像があれば追加。なければNone型を代入
        image_base64=None

        if not image_file:
            print("errer for image")

        # 質問が空の場合の処理
        if not question:
            return jsonify({'error': '質問が空です'}), 400

        # 質問を会話履歴に追加
        conversation_history.append({"role": "user", "content": question})

         # 画像が送信されている場合、Base64をデコードしてファイルに保存
        if image_file:
            image_data=base64.b64decode(image_file)
            image=Image.open(BytesIO(image_data))
            img_filename = os.path.join(new_dir_images, f"image_{current_time}.png")
            image.save(img_filename)
            print(f"Image saved as {img_filename}")
            image_base64=encode_image(img_filename)

        # ChatGPTに複数の生徒として質問を送信
        chatgpt_responses = ask_multiple_students(conversation_history,num_students,target,view,grade,Taro_correct,Taro_wrong,Taro_idk,Hanako_correct,Hanako_wrong,Hanako_idk,Jiro_correct,Jiro_wrong,Jiro_idk,Misaki_correct,Misaki_wrong,Misaki_idk,subject,image_base64)

        # 生徒の返答を会話履歴に追加
        for response in chatgpt_responses:
            conversation_history.append({"role": "assistant", "content": response['message']})

        # チャットのやり取りを保存
        save_chat_log(question, chatgpt_responses)
        
        # レスポンスとして生徒の名前とメッセージを配列で返す
        response_data = {'answers': chatgpt_responses}
        print(f"Sending response: {response_data}")  # デバッグ用にレスポンスを出力
        return jsonify(response_data)
    except Exception as e:
        print(f"Error in chat endpoint: {e}")
        return jsonify({'error': f'サーバーエラーが発生しました: {str(e)}'}), 500

# ChatGPTに生徒役として質問を送信する関数（学力レベル別）
def ask_chatgpt_as_student(conversation_history,num_students,target,view,grade,Taro_correct,Taro_wrong,Taro_idk,Hanako_correct,Hanako_wrong,Hanako_idk,Jiro_correct,Jiro_wrong,Jiro_idk,Misaki_correct,Misaki_wrong,Misaki_idk,subject,image_base64):
    try:
        global tag
        system_message=f"私は{grade}の4人の生徒を演じます。\n{subject}の先生として発言するユーザーに対して、20文字以内で発言します。\nユーザーからの質問に対して、答えるのに最もふさわしい生徒として回答してください。\nどんな場合でもあなたが演じる生徒の発言の前に名前を「太郎：」のように表記してください。"
        Taro_data=f"出席番号1番、太郎は先生から言われた問題に対して、{Taro_correct}%の確率で正しい答えを言い、{Taro_wrong}%の確率で間違った答えを言い、{Taro_idk}%の確率で分からないと答えます。"
        Hanako_data=f"出席番号2番、花子は先生から言われた問題に対して、{Hanako_correct}%の確率で正しい答えを言い、{Hanako_wrong}%の確率で間違った答えを言い、{Hanako_idk}%の確率で分からないと答えます。"
        Jiro_data=f"出席番号3番、次郎は先生から言われた問題に対して、{Jiro_correct}%の確率で正しい答えを言い、{Jiro_wrong}%の確率で間違った答えを言い、{Jiro_idk}%の確率で分からないと答えます。"
        Misaki_data=f"出席番号4番、美咲は先生から言われた問題に対して、{Misaki_correct}%の確率で正しい答えを言い、{Misaki_wrong}%の確率で間違った答えを言い、{Misaki_idk}%の確率で分からないと言葉に詰まってしまいます。"
        
        if(tag==1):
            print(f"Sending to ChatGPT:\n{system_message}\n{Taro_data}\n{Hanako_data}\n{Jiro_data}\n{Misaki_data}")
            tag=0

        if image_base64: #画像ファイルが存在する場合
            # OpenAI API呼び出し

            print('Talking with image now.')
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=conversation_history+[
                    {"role": "system", "content": system_message },
                    {"role":"system","content": f"{view}"},
                    {"role": "user", "name": "Taro", "content":Taro_data},
                    {"role": "user", "name": "Hanako", "content":Hanako_data},
                    {"role": "user", "name": "Jiro", "content":Jiro_data},
                    {"role": "user", "name": "Misaki", "content":Misaki_data},
                    {"role": "user", "content": [
                        {"type": "text", "text": "質問に対して、以下の画像を見て、生徒の誰かとして意見を述べてください。\n誰が話すかは質問の内容から判断してください。\n画像の解釈とともに、あなたが演じる生徒の発言の前に名前を「太郎：」のように表記してください。\n画像に不十分な点が合ってもその旨は一切回答してはいけません。必ず生徒として回答してください。"},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                    ]}
                ]# 過去の会話履歴を追加
            )
        else: #画像ファイルが存在しない場合
            # OpenAI API呼び出し

            print('Talking without image now.')
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=conversation_history+[
                    {"role": "system", "content": system_message },
                    {"role":"system","content": f"{view}"},
                    {"role": "user", "name": "Taro", "content":Taro_data},
                    {"role": "user", "name": "Hanako", "content":Hanako_data},
                    {"role": "user", "name": "Jiro", "content":Jiro_data},
                    {"role": "user", "name": "Misaki", "content":Misaki_data},
                ]# 過去の会話履歴を追加
            )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error during OpenAI API call: {e}")
        return f"エラーが発生しました: {str(e)}"

# 複数の生徒に対して質問を送信する関数
def ask_multiple_students(conversation_history,num_students,target,view,grade,Taro_correct,Taro_wrong,Taro_idk,Hanako_correct,Hanako_wrong,Hanako_idk,Jiro_correct,Jiro_wrong,Jiro_idk,Misaki_correct,Misaki_wrong,Misaki_idk,subject,image_base64):
    responses = []
    student_num = [1, 2, 3, 4]  # 生徒の名前をリストに設定 太郎:1, 花子:2, 次郎:3, 美咲:4
    response = ask_chatgpt_as_student(conversation_history,num_students,target,view,grade,Taro_correct,Taro_wrong,Taro_idk,Hanako_correct,Hanako_wrong,Hanako_idk,Jiro_correct,Jiro_wrong,Jiro_idk,Misaki_correct,Misaki_wrong,Misaki_idk,subject,image_base64)
    name=get_student_name(response)
    responses.append({
        "name": name,  # 名前をリストから選択
        "message": response
    })

    return responses

# チャットのやり取りをファイルに保存する関数
def save_chat_log(question, responses):
    with open(CHAT_LOG_FILE, 'a', encoding='utf-8') as file:
        file.write(f"先生: {question}\n{datetime.now().strftime('%H%M%S')}\n")
        for response in responses:
            file.write(f"{response['name']}: {response['message']}\n")
        file.write("-" * 20 + "\n")  # 区切りのラインS

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)