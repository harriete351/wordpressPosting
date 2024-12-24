import requests
import os
import ssl
import certifi
import logging
import base64
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# SSL 설정
ssl._create_default_https_context = ssl._create_unverified_context

# OpenAI API 키 설정 (환경 변수 사용)
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise EnvironmentError("API key is missing. Please provide a valid API key in the .env file.")

# 워드프레스 설정 (REST API 사용, 환경 변수 사용)
wordpress_url = os.getenv("WORDPRESS_URL")
wordpress_username = os.getenv("WORDPRESS_USERNAME")
application_password = os.getenv("WORDPRESS_APP_PASSWORD")

if not wordpress_url or not wordpress_username or not application_password:
    raise EnvironmentError("WordPress credentials are missing. Please ensure the URL, username, and password are provided in the .env file.")

# 로그 설정
logging.basicConfig(
    filename="blog_posting.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_and_print(message):
    print(message)
    logging.info(message)

# 공통 헤더 설정
def get_headers():
    try:
        auth_string = f"{wordpress_username}:{application_password}"
        auth_base64 = base64.b64encode(auth_string.encode()).decode()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_base64}"
        }
        validate_headers(headers)
        return headers
    except Exception as e:
        raise ValueError(f"Error creating headers: {str(e)}")

def validate_headers(headers):
    if not headers.get("Authorization"):
        raise ValueError("Authorization header is missing. Please ensure proper credentials are provided.")
    log_and_print("Headers validated successfully.")

def send_system_prompt(system_prompt_file, user_prompt):
    try:
        log_and_print("Reading system prompt from file...")
        # Setting file path relative to the script location
        script_dir = os.path.dirname(os.path.abspath(__file__))
        system_prompt_file_path = os.path.join(script_dir, system_prompt_file)

        if not os.path.exists(system_prompt_file_path):
            raise FileNotFoundError(f"System prompt file not found: {system_prompt_file_path}")

        with open(system_prompt_file_path, "r", encoding="utf-8") as file:
            system_prompt = file.read()

        log_and_print("Calling OpenAI API with system and user prompts...")
        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }, json=payload)

        if response.status_code == 200:
            log_and_print("Response received from OpenAI API.")
            data = response.json()
            content = data["choices"][0]["message"]["content"].strip('"')

            # Remove redundant HTML structure
            content = content.replace("<html>", "").replace("</html>", "")
            content = content.replace("<body>", "").replace("</body>", "")

            return content.strip()
        else:
            error_message = f"Error: {response.status_code} - {response.text}"
            log_and_print(error_message)
            return error_message
    except Exception as e:
        error_message = f"Exception occurred: {str(e)}"
        log_and_print(error_message)
        return error_message

def save_to_file(filename, content):
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))  # 현재 실행 파일의 경로
        file_path = os.path.join(script_dir, filename)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        log_and_print(f"Content saved to {file_path}")
    except Exception as e:
        error_message = f"Error saving to file: {str(e)}"
        log_and_print(error_message)

def post_to_wordpress(title, content):
    try:
        # Remove duplicate title from content
        headers = get_headers()
        data = {
            "title": title,
            "content": content,  # Directly using HTML content
            "status": "draft"  # 'publish', 'draft', etc.
        }
        response = requests.post(f"{wordpress_url}/wp-json/wp/v2/posts", headers=headers, json=data)
        if response.status_code == 201:
            post_link = response.json().get("link")
            log_and_print(f"Post titled '{title}' published successfully: {post_link}.")
        else:
            error_message = f"Failed to publish post: {response.status_code} - {response.text}"
            if response.status_code == 401:
                error_message += "\nPlease verify the application password or re-generate it."
            log_and_print(error_message)
    except Exception as e:
        error_message = f"Error posting to WordPress: {str(e)}"
        log_and_print(error_message)

# 사용자 입력 받기
keyword = input("Enter a primary keyword: ")

# 1. 키워드로 제목 목차 생성
system_prompt_title_file = "system_prompt_title.txt"
user_prompt_title = f"keyword와 관련된 한글 제목을 생성해줘 '{keyword}'. 이 제목은 검색자에게 매력적이고 SEO에 적합해야해."
blog_title = send_system_prompt(system_prompt_title_file, user_prompt_title)
log_and_print("\nGenerated Blog Title:")
log_and_print(blog_title)

# 2. 제목으로 포스팅 작성
system_prompt_post_file = "system_prompt_post.txt"

# 1단계: 도입부 작성
user_prompt_post_step1 = f"제목을 바탕으로 3~4문장의 도입부를 작성해줘. 도입부 내용은 문제 제기, 해결 방향 제안, 본문 요약 순서로 구성하고 '도입부'라는 단어는 포함하지 말아줘. 참고 데이터: 제목은 '{blog_title}'입니다."

step1_result = send_system_prompt(system_prompt_post_file, user_prompt_post_step1)
log_and_print("\nStep 1 Result:")
log_and_print(step1_result)

# 2단계: 본문의 첫 번째 절반 작성
user_prompt_post_step2 = f"Based on the title '{blog_title}', write the first half of the blog post strictly in HTML. Ensure logical continuation and structure in line with the title."

step2_result = send_system_prompt(system_prompt_post_file, user_prompt_post_step2)
log_and_print("\nStep 2 Result:")
log_and_print(step2_result)

# 3단계: 본문의 나머지 절반 작성 및 최종 마무리
user_prompt_post_step3 = f"Continue and complete the blog post based on the title '{blog_title}' and the first half written in Step 2. Focus on practical tips, a FAQ section, and a strong conclusion. Ensure the structure is consistent and logical."

step3_result = send_system_prompt(system_prompt_post_file, user_prompt_post_step3)
log_and_print("\nStep 3 Result:")
log_and_print(step3_result)

# 긴 응답 처리
final_post = f"<html><body>{step1_result}\n\n{step2_result}\n\n{step3_result}</body></html>"
if len(final_post) > 500:
    save_to_file("blog_post.txt", final_post)
    log_and_print("\nResponse is too long. Saved to 'blog_post.txt'.")
else:
    log_and_print("\nGenerated Blog Post:")
    log_and_print(final_post)

# 워드프레스에 포스팅
post_to_wordpress(blog_title, final_post)
