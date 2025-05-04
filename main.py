import re
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright, expect, TimeoutError

# Load environment variables from .env file (if it exists)
load_dotenv()

def run(playwright: Playwright) -> None:
    # Get credentials from environment variables - format: "email password"
    google_pw = os.environ.get("GOOGLE_PW", "")
    credentials = google_pw.split(' ', 1) if google_pw else []
    
    email = credentials[0] if len(credentials) > 0 else None
    password = credentials[1] if len(credentials) > 1 else None
    
    app_url = os.environ.get("APP_URL", "https://idx.google.com/app-43646734")
    cookies_path = Path("google_cookies.json")
    
    # Check if credentials are available
    if not email or not password:
        print("错误: 缺少凭据。请设置 GOOGLE_PW 环境变量，格式为 '账号 密码'。")
        print("例如:")
        print("  export GOOGLE_PW='your.email@gmail.com your_password'")
        return
    
    browser = playwright.firefox.launch(headless=True)
    context = browser.new_context()
    
    # 尝试加载已保存的 cookies
    cookies_loaded = False
    if cookies_path.exists():
        try:
            print("尝试使用已保存的 cookies 登录...")
            with open(cookies_path, 'r') as f:
                cookies = json.load(f)
                context.add_cookies(cookies)
            cookies_loaded = True
        except Exception as e:
            print(f"加载 cookies 失败: {e}")
            cookies_loaded = False
    
    page = context.new_page()
    
    try:
        # 先访问目标页面，查看是否已登录
        print(f"访问目标页面: {app_url}")
        page.goto(app_url)
        time.sleep(10)  # 等待10秒
        # 等待页面完全加载
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_load_state("networkidle")
        
        login_required = True
        
        # 检查是否需要登录 (通过页面URL判断)
        current_url = page.url
        if cookies_loaded:
            try:
                # 检测登录状态：如果URL包含idx.google.com但不包含signin，则已登录成功
                if "idx.google.com" in current_url and "signin" not in current_url:
                    print("已经通过cookies登录成功!")
                    login_required = False
                    
                    # 即使通过cookie登录成功，也保存最新的cookies
                    print("保存最新的cookies...")
                    cookies = context.cookies()
                    with open(cookies_path, 'w') as f:
                        json.dump(cookies, f)
                else:
                    print("Cookie登录失败，将尝试密码登录...")
            except Exception:
                print("无法判断登录状态，将尝试密码登录...")
        
        # 如果需要登录
        if login_required:
            print("开始密码登录流程...")
            
            # 确保在登录页面
            if "signin" not in page.url:
                page.goto(app_url)
                
                page.wait_for_load_state("domcontentloaded")
                page.wait_for_load_state("networkidle")
            
            # 输入邮箱
            print("输入邮箱...")
            page.get_by_label("Email or phone").fill(email)
            page.get_by_role("button", name="Next").click()
            
            # 等待密码输入框出现
            page.wait_for_selector('input[type="password"]', state="visible")
            
            # 输入密码
            print("输入密码...")
            page.get_by_label("Enter your password").fill(password)
            page.get_by_role("button", name="Next").click()
            
            # 等待登录完成并跳转
            print("等待登录完成...")
            page.wait_for_load_state("networkidle")
            
            # 使用与cookie登录相同的判断标准验证登录是否成功
            current_url = page.url
            if "idx.google.com" in current_url and "signin" not in current_url:
                print("密码登录成功!")
                
                # 保存cookies以便下次使用
                print("保存cookies以供下次使用...")
                cookies = context.cookies()
                with open(cookies_path, 'w') as f:
                    json.dump(cookies, f)
            else:
                print("登录失败：未能跳转到目标页面")
                return
        
        # 无论是已登录还是刚登录，都跳转到目标URL
        print(f"导航到目标页面: {app_url}")
        page.goto(app_url)
        
        # 等待页面完全加载，包括所有资源和AJAX请求
        print("等待页面完全加载...")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_load_state("networkidle")
        page.wait_for_load_state("load")
        
        # 最终验证是否成功访问目标URL
        current_url = page.url
        print("验证当前是否在目标URL...")
        
        # 使用统一的判断标准来验证最终访问是否成功
        if "idx.google.com" in current_url and "signin" not in current_url:
            # 最后再次保存cookies，确保获取最新状态
            print("保存最终的cookies状态...")
            cookies = context.cookies()
            with open(cookies_path, 'w') as f:
                json.dump(cookies, f)
                
            print("成功访问目标页面！")
            print("等待30秒后关闭...")
            time.sleep(30)  # 等待30秒
            print("自动化流程完成!")
        else:
            print(f"警告: 当前页面URL ({current_url}) 与目标URL不符")
            print(f"登录可能失败或被重定向到其他页面")
        
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        page.close()
        context.close()
        browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
