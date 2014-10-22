# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

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
        driver = self.driver

        #Initial setup of alias email
        #TODO: Figure out how to navigate to a new email each time

        driver.get(self.base_url + "/#/superrito.com/gwhan3028/")
        driver.find_element_by_xpath("//form[@id='emailForm']/fieldset/div[2]").click()
        main_window = driver.current_window_handle
        driver.find_element_by_css_selector("span.center.jcf-unselectable").click()
        
        #Create twitter tab, change to it, and create a new account with our alias email
        #TODO: Get and pass values from alias email, randomize password and username

        driver.find_element_by_css_selector("li.jcfcalc.item-selected > a > span").click()
        Select(driver.find_element_by_id("fDomain")).select_by_visible_text("@armyspy.com")
        driver.find_element_by_name("user[name]").clear()
        driver.find_element_by_name("user[name]").send_keys("Greg Davis")
        driver.find_element_by_name("user[email]").clear()
        driver.find_element_by_name("user[email]").send_keys("GWhan3028@armyspy.com")
        driver.find_element_by_name("user[user_password]").clear()
        driver.find_element_by_name("user[user_password]").send_keys("johnjohnanjohnan")
        driver.find_element_by_xpath("(//button[@type='submit'])[3]").click()
        driver.find_element_by_css_selector("button.btn-link").click()
        driver.find_element_by_name("user[remember_me_on_signup]").click()
        driver.find_element_by_name("submit_button").click()
        driver.find_element_by_link_text("Let's go!").click()
        driver.find_element_by_css_selector("button.btn.primary-btn").click()
        driver.find_element_by_xpath("(//button[@type='button'])[3]").click()
        driver.find_element_by_link_text("Skip this step").click()
        
        #Return to faux email and confirm our twitter account
        driver.find_element_by_css_selector("a > span").click()
        
        #Spawn new window, navigate to our flask app and allow our new bot to authenticate
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
