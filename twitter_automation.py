# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re, random, string

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
        randomName = random.choice(open('names.txt').
                                   readlines()).lstrip().rstrip(' \n')
        randomPW = ''.join([random.choice
                            (string.ascii_letters + string.digits) for n in 
                            xrange(0, random.randint(8,15))])

        #Initial setup of alias email
        driver.get(self.base_url + "/")
        fake_email = driver.find_element_by_id("cxtEmail").text
        email_name, email_domain = str(fake_email).split('@')

        #save new credentials combo in a file
        with open('twitter_creds', 'a') as out:
            out.write(randomName + ":" + randomPW + '\n' + 
                      self.base_url + "/#/" + email_domain 
                      + "/" + email_name + "/" + '\n')

        #Go to twitter and sign up for an account
        driver.get("www.twitter.com")
        driver.find_element_by_name("user[name]").clear()
        driver.find_element_by_name("user[name]").send_keys(randomName)
        driver.find_element_by_name("user[email]").clear()
        driver.find_element_by_name("user[email]").send_keys(fake_email)
        driver.find_element_by_name("user[user_password]").clear()
        driver.find_element_by_name("user[user_password]").send_keys(randomPW)
        driver.find_element_by_xpath("(//button[@type='submit'])[3]").click()
        time.sleep(3)
        driver.find_element_by_css_selector("button.btn-link").click()
        driver.find_element_by_name("submit_button").click()
        driver.find_element_by_link_text("Let's go!").click()
        driver.find_element_by_link_text("Continue").click()
        driver.find_element_by_partial_link_text("Follow").click()
        driver.find_element_by_link_text("Skip this step").click()
        
        #Return to faux email and confirm our twitter account        
        driver.get(self.base_url + "/#/" + email_domain + 
                   "/" + email_name + "/")
        driver.find_element_by_css_selector("a > span").click()
        
        #Spawn new window, navigate to our flask app and allow our 
        #new bot to authenticate
        driver.get("54.173.95.142/twitter")
        timer.sleep(2)
        driver.find_element_by_id("username_or_email").clear()
        driver.find_element_by_id("username_or_email").send_keys(randomName)
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys(randomPW)
        time.sleep(2)
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
