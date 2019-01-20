import random
import time
from pprint import pprint

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome, ChromeOptions, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def init_chrome_options():
    chrome_options = ChromeOptions()
    chrome_options.headless = False
    # 连接mitmproxy
    chrome_options.add_argument('--proxy-server=http://127.0.0.1:8080')
    return chrome_options


def init_chrome_webdriver(chrome_options=None):
    chrome_driver = Chrome(executable_path="chromedriver.exe", options=chrome_options)
    chrome_driver.maximize_window()
    return chrome_driver


def load_user_info():
    # 用户名 密码 用空格分割
    with open("username_password_info.txt", "r", encoding='utf-8') as info_f:
        username, pwd = info_f.readline().split(" ")
    return username, pwd


def modifying_navigator(driver_for_js: Chrome):
    # driver.execute_script("""function(){
    #     Object.defineProperties(navigator,{
    #         webdriver:{
    #             get:() = false
    #         }
    #     })}""")
    set_webdriver_false = '''
               Object.defineProperties(navigator,{
                 webdriver:{value:undefined,  configurable: false,
        writable: true,
        enumerable: true}
               })
            '''
    driver_for_js.execute_script(set_webdriver_false)
    add_do_not_track_ = '''
               Object.defineProperties(navigator,{
                 doNotTrack:{value:"1",  configurable: false,
        writable: true,
        enumerable: true}
               })
            '''
    driver_for_js.execute_script(add_do_not_track_)
    modifying_languages = '''
            Object.defineProperties(navigator, {
                  languages: {value:["zh-CN", "zh", "en-US", "en", "zh-TW"],  configurable: false,
        writable: true,
        enumerable: true}
                })
            '''
    driver_for_js.execute_script(modifying_languages)
    modifying_plugins = '''
            Object.defineProperties(navigator, {
                    plugins: {value:[1, 2, 3, 4, 5,6,7,8],  configurable: false,
        writable: true,
        enumerable: true}
                 })
            '''
    driver_for_js.execute_script(modifying_plugins)


def generate_human_behaviour(context_driver):
    action_chain = ActionChains(context_driver)
    # 鼠标移动
    for mouse_move_count in range(10):
        x_offset = random.randint(15, 25)
        y_offset = random.randint(12, 14)
        action_chain.move_by_offset(x_offset, y_offset)
        action_chain.pause(0.2)
        # x_offset = -x_offset
        # y_offset = -y_offset
        # action_chain.move_by_offset(x_offset, y_offset)
        action_chain.pause(0.2)
    action_chain.pause(0.2)
    action_chain.release()
    # 执行动作链
    action_chain.perform()


if __name__ == "__main__":
    # 初始化
    options = init_chrome_options()
    driver = init_chrome_webdriver(options)
    driver.delete_all_cookies()
    cookies = None
    # 打开页面
    driver.get("https://login.taobao.com/member/login.jhtml")
    # driver.get("http://h5s.club/featureTest/")
    while not cookies:
        generate_human_behaviour(driver)

        # 切换到用户名密码登录
        WebDriverWait(driver, 6, 0.5).until(expected_conditions.element_to_be_clickable((By.ID, "J_Quick2Static")))
        driver.execute_script("""
        document.getElementById("J_Quick2Static").click()
        """)

        # show_input_box_button = driver.find_element_by_id("J_Quick2Static")
        # show_input_box_button.click()
        generate_human_behaviour(driver)
        user_name, password = load_user_info()
        # 输入用户名
        WebDriverWait(driver, 6, 0.5).until(
            expected_conditions.visibility_of_element_located((By.CLASS_NAME, "J_UserName")))
        user_name_input_box = driver.find_element_by_class_name('J_UserName')
        for i, char in enumerate(user_name):
            time.sleep(random.random() * 0.5 * (i % 3 + 1))
            user_name_input_box.send_keys(char)
        generate_human_behaviour(driver)

        # 输入密码
        WebDriverWait(driver, 6, 0.5).until(
            expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, "#TPL_password_1")))
        password_input_box = driver.find_element_by_css_selector("#TPL_password_1")
        for i, char in enumerate(user_name):
            time.sleep(random.random() * 0.5 * (i % 3 + 1))
            password_input_box.send_keys(char)
        generate_human_behaviour(driver)

        can_submit = False
        try:
            # 处理滑动验证码
            WebDriverWait(driver, 6, 0.5).until(
                expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "#nocaptcha")))
        except TimeoutException as e:
            print("未出现滑动验证码")
            # todo 页面上没找到这个元素不一定就是没有验证码(可能是改名了或者加载慢)
            can_submit = True
        else:
            try:
                WebDriverWait(driver, 6, 0.5).until(
                    expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "#nc_1_n1z")))
            except TimeoutException as e:
                print("未找到滑块位置")
                can_submit = False
            else:
                slide_captcha = driver.find_element_by_css_selector("#nc_1_n1z")
                pprint("滑块初始位置:" + str(slide_captcha.location))
                actions = ActionChains(driver)
                actions.move_to_element(slide_captcha)
                actions.pause(random.random() * 2)
                actions.click_and_hold(slide_captcha)
                for x in range(27):
                    actions.move_by_offset(10, 0)
                    actions.pause(random.random() * 0.01)
                actions.release(slide_captcha)
                actions.perform()
                generate_human_behaviour(driver)

                # todo 检测是否成功滑动,如果不成功再次滑动
                can_submit = True

        if can_submit:
            # 提交用户名和密码
            WebDriverWait(driver, 6, 0.5).until(
                expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "#J_SubmitStatic")))
            submit_button = driver.find_element_by_css_selector("#J_SubmitStatic")
            submit_button.click()
            generate_human_behaviour(driver)
            # todo 检测是否登录成功
            cookies = driver.get_cookies()
            pprint(cookies)
