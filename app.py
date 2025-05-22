from flask import Flask, render_template, request
import openai
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

app = Flask(__name__)

# Together.ai API 설정
openai.api_key = os.getenv("TOGETHER_API_KEY")
openai.api_base = "https://api.together.xyz/v1"

@app.route("/", methods=["GET", "POST"])
def index():
    result = {"start": "", "end": ""}

    if request.method == "POST":
        situation = request.form.get("situation")
        topic = request.form.get("topic")

        # 프롬프트 구성
        prompt = (
            f"상황: {situation}\n"
            f"주제: {topic}\n\n"
            "이 상황에서 대화를 시작할 때 어울리는 자연스러운 멘트 하나와, "
            "대화를 마무리할 때 어울리는 멘트 하나를 추천해줘. "
            "각각 '시작:'과 '마무리:'로 시작해줘."
        )

        try:
            response = openai.ChatCompletion.create(
                model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            content = response['choices'][0]['message']['content'].strip()
            print("🔍 모델 응답 확인:\n", content)

            # 응답 파싱 (줄바꿈 대응 포함)
            lines = content.split("\n")
            for i, line in enumerate(lines):
                line = line.strip()
                if "시작:" in line:
                    if ":" in line and line.split("시작:", 1)[-1].strip():
                        result["start"] = line.split("시작:", 1)[-1].strip().strip('"')
                    elif i + 1 < len(lines):
                        result["start"] = lines[i + 1].strip().strip('"')
                elif "마무리:" in line:
                    if ":" in line and line.split("마무리:", 1)[-1].strip():
                        result["end"] = line.split("마무리:", 1)[-1].strip().strip('"')
                    elif i + 1 < len(lines):
                        result["end"] = lines[i + 1].strip().strip('"')

            # 결과 비어 있을 경우 예외 메시지 출력
            if not result["start"]:
                result["start"] = "[시작 멘트를 찾지 못했습니다.]"
            if not result["end"]:
                result["end"] = "[마무리 멘트를 찾지 못했습니다.]"

            print("🔍 시작 멘트:", result["start"])
            print("🔍 마무리 멘트:", result["end"])

        except Exception as e:
            result = {"start": "", "end": f"오류 발생: {e}"}

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)