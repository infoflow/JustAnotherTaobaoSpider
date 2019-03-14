import json
import logging
import random
import sys
import time

from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import Chrome, ChromeOptions, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

log = logging.getLogger("logger")


class TaobaoCookiesGenerator(object):

    @staticmethod
    def init_chrome_options(proxy_url, headless):
        """
        初始化chrome的配置
        :return: ChromeOptions()的实例
        """
        chrome_options = ChromeOptions()
        chrome_options.headless = headless
        if sys.platform == "linux":
            chrome_options.binary_location = '/usr/bin/google-chrome'
        # mitmproxy 代理地址
        chrome_options.add_argument('--proxy-server=' + proxy_url)
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--blink-settings=imagesEnabled=False')
        return chrome_options

    @staticmethod
    def init_chrome_webdriver(chrome_options=None):
        """
        初始化webdriver
        :param chrome_options: chrome配置
        :return: webdriver 实例
        """
        if sys.platform == "linux":
            driver_path = "chromedriver"
        else:
            driver_path = "chromedriver.exe"
        chrome_driver = Chrome(executable_path=driver_path, options=chrome_options)
        chrome_driver.maximize_window()
        return chrome_driver

    def __init__(self, mitmproxy_url, headless=True):
        # 初始化chrome 和 webdriver
        options = self.init_chrome_options(mitmproxy_url, headless)
        self.driver = self.init_chrome_webdriver(options)
        self.driver.delete_all_cookies()

    def get_cookies(self, name, password):
        cookies = None
        log.debug("打开登录页面")
        self.driver.get("https://login.taobao.com/member/login.jhtml")
        # self.driver.get("http://h5s.club/featureTest/")
        self.driver.save_screenshot("1_open_the_page.png")
        retry_count = 0
        while not cookies and retry_count < 3:

            retry_count += 1
            try:
                WebDriverWait(self.driver, 10, 0.1).until(
                    expected_conditions.visibility_of_element_located((By.ID, "J_LoginBox"))
                )
            except TimeoutException as e:
                log.debug("未出现切换扫码登录和用户名密码登录的按钮")
                return
            try:
                self.driver.find_element_by_css_selector("login-box no-longlogin module-static")
            except NoSuchElementException as e:
                log.debug("当前页码为扫码登录,正在切换到用户名密码登录")
                self.driver.execute_script("""
                document.getElementById("J_Quick2Static").click()
                """)
                self.driver.save_screenshot("2_switch_to_input_username_and_password.png")
            else:
                log.debug("当前页面为用户名密码登录")

            log.debug("输入用户名")
            WebDriverWait(self.driver, 10, 0.1).until(
                expected_conditions.visibility_of_element_located((By.CLASS_NAME, "J_UserName")))
            user_name_input_box = self.driver.find_element_by_class_name('J_UserName')
            user_name_input_box.clear()
            for i, char in enumerate(name):
                time.sleep(random.random() * 0.1 * (i % 3 + 1))
                user_name_input_box.send_keys(char)

            log.debug("输入密码")
            WebDriverWait(self.driver, 10, 0.1).until(
                expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, "#TPL_password_1")))
            password_input_box = self.driver.find_element_by_css_selector("#TPL_password_1")
            password_input_box.clear()
            for i, char in enumerate(password):
                time.sleep(random.random() * 0.1 * (i % 3 + 1))
                password_input_box.send_keys(char)

            try:
                self.driver.save_screenshot("process_captcha.png")
                WebDriverWait(self.driver, 6, 0.1).until(
                    expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "#nocaptcha")))
            except TimeoutException as e:
                log.debug("未出现滑动验证码")
                can_submit = True
            else:
                log.debug("出现滑动验证码,正在处理...")
                try:
                    WebDriverWait(self.driver, 60, 0.1).until(
                        expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "#nc_1_n1z")))
                except TimeoutException as e:
                    log.debug("未找到滑块位置")
                    can_submit = False
                else:
                    slide_captcha = self.driver.find_element_by_css_selector("#nc_1_n1z")
                    log.debug("滑块初始位置:" + str(slide_captcha.location))
                    actions = ActionChains(self.driver)
                    actions.move_to_element(slide_captcha)
                    actions.pause(random.random() * 2)
                    actions.click_and_hold(slide_captcha)
                    for x in range(27):
                        actions.move_by_offset(10, 0)
                        actions.pause(random.random() * 0.01)
                    actions.release(slide_captcha)
                    actions.perform()
                    # todo 检测是否成功滑动
                    can_submit = True

            self.driver.save_screenshot("after_process_captcha.png")
            if can_submit:
                log.debug("提交用户名和密码")
                WebDriverWait(self.driver, 6, 0.1).until(
                    expected_conditions.element_to_be_clickable((By.CSS_SELECTOR, "#J_SubmitStatic")))
                submit_button = self.driver.find_element_by_css_selector("#J_SubmitStatic")
                submit_button.click()
                log.debug("检测是否进入登录状态")
                try:
                    WebDriverWait(self.driver, 6, 0.1).until(
                        expected_conditions.visibility_of_element_located((By.CSS_SELECTOR, ".s-name > a > em"))
                    )
                except TimeoutException as e:
                    log.debug("未检测到用户的昵称,登录失败")
                    return
                else:
                    nickname = self.driver.find_element_by_css_selector(".s-name > a > em").text
                    log.debug(f"{name},{password}登录成功,昵称为{nickname}")
                    log.debug("获取登录之后的cookies为:")
                    cookies = json.dumps(self.driver.get_cookies(), ensure_ascii=False)
                    log.debug(cookies)
                    self.driver.save_screenshot("after_login.png")
                    return cookies

    def close(self):
        self.driver.close()
