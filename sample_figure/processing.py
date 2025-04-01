import os
import base64
import openai

# OpenAIクライアントを作成
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 画像をbase64でエンコードする関数
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# ChatGPTに画像の解説を求める関数
def get_image_description(image_base64):
    prompt = "以下の画像の内容を解説してください。"

    # ChatGPTにリクエスト（修正後）
    response = client.chat.completions.create(
        model="gpt-4o",  # 使用するモデルを指定
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": "この三角形の面積を求めてください。"},
            {"role": "user", "content": [
                {"type": "text", "text": "この三角形の面積を求めてください。"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
            ]}
        ]
    )

    return response.choices[0].message.content.strip()

# メイン処理
def main():
    # 画像が入っているディレクトリを指定
    image_directory = './'  # 画像ファイルがあるディレクトリ
    for filename in os.listdir(image_directory):
        if filename.endswith("sample1.png"):  # PNG画像のみを対象
            image_path = os.path.join(image_directory, filename)

            # 画像をbase64エンコード
            image_base64 = encode_image(image_path)

            # 画像解説を取得
            description = get_image_description(image_base64)

            print(f"画像 {filename} の解説:\n{description}\n")

if __name__ == "__main__":
    main()
