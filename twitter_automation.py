# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re, random

class TwitterAutomation(unittest.TestCase):
    """
    An automated creation of a twitter account using an email pulled from fakemailgenerator
    
    Requires US IP address to avoid phone verification
    TODO: Create metascript of this that humanizes account creation
    TODO: Find out whether armyspy is the only version of the email that works
    """
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "http://www.fakemailgenerator.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_twitter_automation(self):
        #setup driver and uname/pw
        driver = self.driver
        randomName = random.choice(open('names.txt').readlines()).lstrip()
        randomPW = ''.join([random.choice
                            (string.ascii_letters + string.digits) for n in 
                            xrange(0, random.randint(8,15))])

        #save new uname/pw combo in password
        with open('twitter_creds', 'w') as out:
            out.write(randomName + ":" + randomPW + '\n')

        #Initial setup of alias email
        driver.get(self.base_url + "/")
        driver.find_element_by_xpath("//form[@id='emailForm']/fieldset/div[2]").click()
        driver.find_element_by_css_selector("span.center.jcf-unselectable").click()
        driver.find_element_by_css_selector("li.jcfcalc.item-selected > a > span").click()
        Select(driver.find_element_by_id("fDomain")).select_by_visible_text("@armyspy.com")
        fakemail_window = driver.current_window_handle
        

        #Make new twitter window, navigate to it, then wait for it to load
        body = driver.find_element_by_tag_name("body")
        body.send_keys(Keys.CONTROL + 't')
        driver.switch_to.window("New Tab")
        driver.get("www.twitter.com")
        #this might not work
        WebDriverWait(driver, 10).until(EC.title_contains("Twitter"))

        #Getting twitter
        driver.find_element_by_name("user[name]").clear()
        driver.find_element_by_name("user[name]").send_keys(randomName)
        driver.find_element_by_name("user[email]").clear()
        driver.find_element_by_name("user[email]").send_keys(Keys.CONTROL, 'v')
        driver.find_element_by_name("user[user_password]").clear()
        driver.find_element_by_name("user[user_password]").send_keys(randomPW)
        driver.find_element_by_xpath("(//button[@type='submit'])[3]").click()
        driver.find_element_by_css_selector("button.btn-link").click()
        driver.find_element_by_name("user[remember_me_on_signup]").click()
        driver.find_element_by_name("submit_button").click()
        driver.find_element_by_link_text("Let's go!").click()
        driver.find_element_by_css_selector("button.btn.primary-btn").click()
        driver.find_element_by_xpath("(//button[@type='button'])[3]").click()
        driver.find_element_by_link_text("Skip this step").click()
        twitter_window = driver.current_window_handle
        
        #Return to faux email and confirm our twitter account
        driver.switch_to.window(fakemail_window)
        driver.find_element_by_css_selector("a > span").click()
        
        #Spawn new window, navigate to our flask app and allow our new bot to authenticate
        driver.switch_to.window(twitter_window)
        driver.find_element_by_id("allow").click()
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException, e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
