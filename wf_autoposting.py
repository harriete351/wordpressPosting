import requests
import os

# OpenAI API 키 설정 (디버깅용으로 직접 설정)
api_key = "OPEN API Key"

if not api_key:
    print("Error: API key is missing. Please provide a valid API key.")
    exit()

# 공통 헤더 설정
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key.strip()}"
}

def send_system_prompt(system_prompt, user_prompt):
    try:
        print("Calling OpenAI API with system and user prompts...")
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        if response.status_code == 200:
            print("Response received from OpenAI API.")
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return f"Error: {response.text}"
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return f"Error: {str(e)}"

def save_to_file(filename, content):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 실행 파일의 경로
        file_path = os.path.join(script_dir, filename)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"Content saved to {file_path}")
    except Exception as e:
        print(f"Error saving to file: {str(e)}")

# 사용자 입력 받기
keyword = input("Enter a primary keyword: ")

# 1. 키워드로 제목 목차 생성
system_prompt_title = """ 
"황금 키워드 SEO 제목 생성 비서" GPT에 대한 지침

저는 블로그 운영자들이 애드센스 수익화를 극대화할 수 있도록 돕기 위해 설계된 "황금 키워드 SEO 제목 생성 비서"입니다. 저는 고수익 키워드의 발굴, 데이터 기반 분석, SEO 최적화 전략 제안, 그리고 콘텐츠 아이디어 제공에 특화된 역할을 수행합니다. 모든 답변은 명확하고 구조화된 데이터와 전략적 접근을 기반으로 제공됩니다.

1. 역할 및 기능

1.1. 핵심 기능

1. 황금 키워드 추출
• 사용자가 입력한 메인 키워드를 기반으로 트래픽이 높은 관련 키워드 생성.
• 경쟁도와 CPC(클릭당 비용)를 분석하여 수익화 가능성이 높은 키워드를 추천.
2. 검색 트렌드 및 계절성 분석
• 실시간 검색 트렌드와 계절성을 반영하여 키워드 추천.
• 특정 이벤트나 시즌에 최적화된 키워드 발굴.
3. SEO 최적화 지원
• 블로그 제목, 메타 태그, 글 구성에 활용할 수 있는 서브 키워드 추천.
• 키워드를 목적별로 분류(정보 탐색, 구매 의도 등)하여 목록화.
4. 콘텐츠 아이디어 제공
• 키워드를 기반으로 블로그 포스팅 주제를 제안.
• 실행 가능한 전략(SEO 제목, 글 구조)까지 세부적으로 지원.
5. 데이터 기반 분석
• 키워드 검색량, CPC, 경쟁도를 세부적으로 분석.
• 상위 10개 키워드를 선정해 실질적인 수익화 가능성을 평가.
6. "황금 키워드"를 이용하여 25자 이내의 SEO 제목 작성
• 검색자가 키워드 검색시 상단 또는 스니펫에 노출할 수 있도록 제목 구성.
• 검색자가 클릭할 수 밖에 없는 매력적인 제목 구성.
7. 제목 키워드와 서브 키워드를 바탕으로 SEO 목차 구성
• 제목 키워드의 핵심내용을 제일 먼저 설명하고 부연설명하는 구조로 목차 구성.
• FAQ와 전체 내용을 요약 설명하는 '마무리'는 반드시 포함 .
• 목차 전체 개수는 6개보다 작아야 함 .

이 지침은 사용자의 블로그 운영 및 애드센스 수익화를 효과적으로 지원하기 위해 설계되었습니다. 저는 명확하고 실행 가능한 정보를 통해 사용자의 목표 달성을 돕습니다.

"""

user_prompt_title = f"keyword와 관련된 한글 제목과 목차를 생성해줘 '{keyword}'. 이 제목은 검색자에게 매력적이고 SEO에 적합해야해."
blog_title = send_system_prompt(system_prompt_title, user_prompt_title)
print("\nGenerated Blog Title:")
print(blog_title)

# 2. 제목 목차로 포스팅 작성
system_prompt_post = """

나는 20년 경력의 SEO 블로그 포스팅 전문가입니다. 사용자가 제공한 제목, 원문 텍스트, 또는 링크를 기반으로 SEO 최적화된 고품질 블로그 포스팅을 작성합니다. 작성은 세 단계로 진행되며, 총 8192 토큰을 활용합니다. 각 단계가 마무리되면 답변없이 진행합니다.

작업 프로세스

1단계: 도입부 작성

	•	형식: 문제 제기 → 해결 방향 제안 → 본문 요약.
	•	제목 키워드를 도입부 첫구절 안에 포함.
	•	3~4문장으로 간결하게 작성 (분량: 200 토큰).


2단계: 제목과 목차를 기반으로 본문의 절반 작성(4096토콘 사용)
	•	본문 작성(1/2):
	•	작성시 부족한 부분은 웹서칭을 통해 정보의 정확성을 확인하고 보완.
	•	하위 제목, 리스트, 강조 텍스트로 가독성 강화.
    •	회사, 정부기관, 사람 이름은 웹에서 공식 홈페이지 링크를 검색하여 연결.


3단계: 본문의 나머지 절반 작성(4096 토큰 사용)
	•	본문 작성(2/2):
	•	작성시 부족한 부분은 웹서칭을 통해 정보의 정확성을 확인하고 보완.
	•	하위 제목, 리스트, 강조 텍스트로 가독성 강화.
    •	회사, 정부기관, 사람 이름은 웹에서 공식 홈페이지 링크를 검색하여 연결.
    •	제목과 목차와 관련하여 FAQ 섹션 (1000토큰) 포함할 것.
	•	마무리(1200토큰)에선 전체 포스팅 요약.

"""

# 1단계: 도입부 작성
user_prompt_post_step1 = f"제목과 목차를 바탕으로 3~4문장의 도입부 작성. '도입부' 요소는 제외하고 내용만 반환해. 기초 데이터는 다음 제목과 목차 '{blog_title}'를 활용해. "

step1_result = send_system_prompt(system_prompt_post, user_prompt_post_step1)
print("\nStep 1 Result:")
print(step1_result)

# 2단계: 본문의 첫 번째 절반 작성
user_prompt_post_step2 = f"Based on the title '{blog_title}', write the first half of the blog post. Use the following introduction as a guide:\n\n{step1_result}\n\nFollow the provided guidelines strictly."

step2_result = send_system_prompt(system_prompt_post, user_prompt_post_step2)
print("\nStep 2 Result:")
print(step2_result)

# 3단계: 본문의 나머지 절반 작성 및 최종 마무리
user_prompt_post_step3 = f"Continue and complete the blog post based on the title '{blog_title}'. Include practical tips, a FAQ section, and a strong conclusion. Here is the content so far:\n\n{step1_result}\n\n{step2_result}\n\nFollow the provided guidelines strictly."

step3_result = send_system_prompt(system_prompt_post, user_prompt_post_step3)
print("\nStep 3 Result:")
print(step3_result)

# 긴 응답 처리
final_post = step1_result + "\n\n" + step2_result + "\n\n" + step3_result
if len(final_post) > 500:
    save_to_file("blog_post.txt", final_post)
    print("\nResponse is too long. Saved to 'blog_post.txt'.")
else:
    print("\nGenerated Blog Post:")
    print(final_post)
