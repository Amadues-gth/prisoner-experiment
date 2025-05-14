from flask import Flask, request, jsonify, render_template
from openai import OpenAI
import openai

app = Flask(__name__)

# 设置你的 OpenAI API 密钥（使用环境变量方式）
openai.api_key = os.environ.get("OPENAI_API_KEY") 

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/gpt_response", methods=["POST"])
def gpt_response():
    data = request.get_json()
    round_number = data.get("round")
    player_choice = data.get("playerChoice")
    inertia = data.get("inertia", 0.6)
    history = data.get("history", [])

    history_text = "\n".join(
        [f"第{h['round']}轮：玩家选择{h['player']}，GPT选择{h['gpt']}" for h in history]
    )

    prompt = f"""你是一个参与囚徒困境实验的AI。你要根据玩家过往的行为与策略惯性（当前值为 {inertia}），做出“合作”或“背叛”的选择，并简要解释。

当前回合：第{round_number}轮  
对手本轮选择：{player_choice}  
历史记录：
{history_text if history_text else '（无）'}

请以以下格式回复：
选择：合作 或 背叛  
解释：……"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一个参与囚徒困境实验的AI助手，理性且逻辑清晰。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )

        reply = response.choices[0].message["content"]

        if "选择：" in reply and "解释：" in reply:
            choice_line = reply.split("选择：")[1].splitlines()[0].strip()
            explanation = reply.split("解释：")[1].strip()
        else:
            choice_line = "合作"
            explanation = "我根据策略惯性选择合作。"

        return jsonify({"gptChoice": choice_line, "explanation": explanation})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # 默认5000，用于本地运行
    app.run(host='0.0.0.0', port=port)

