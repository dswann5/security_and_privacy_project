# -*- coding: utf-8 -*-
#selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
#needed for controlling tor
import stem.socket, stem.connection, stem.process
from stem import Signal
#other necessary libraries
import unittest, time, re, random, string, sys

class TwitterAutomation(unittest.TestCase):
    """
    An automated creation of a twitter account using an email pulled from fakemailgenerator
    
    Requires US IP address to avoid phone verification
    TODO: Create metascript of this that humanizes account creation
    """
    def setUp(self):
        #basic setup
        self.base_url = "http://www.fakemailgenerator.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
        
        #create tor privacy profile
        #first, create profile and setup a little bit of privacy so we aren't
        #recognized between runs of our script
        profile = webdriver.FirefoxProfile()
        profile.set_preference("places.history.enabled", False)
        profile.set_preference("privacy.clearonShutdown.passwords", True)
        profile.set_preference("privacy.clearOnShutdown.siteSettings", True)
        profile.set_preference("privacy.sanitize.sanitizeOnShutdown", True)
        profile.set_preference("signon.rememberSignons", False)
        #cookies expire at the end of the session
        profile.set_preference("network.cookie.lifetimePolicy", 2)
        
        #next, setup our socks proxy
        profile.set_preference("network.proxy.type", 1)
        profile.set_preference("network.proxy.socks_version", 5)
        profile.set_preference("network.proxy.socks", '127.0.0.1')
        profile.set_preference("network.proxy.socks_port", 9050)
        profile.set_preference("network.proxy.socks_remote_dns", True)

        #Since we're running headless, we don't need images. 
        #We get a big speed boost from not loading them
        profile.set_preference("permissions.default.image", 2)
	
        #attach to tor control port
        self.tor_controller = stem.socket.ControlPort(port = 9051)
        self.control_password = 'afJh18ahjjjb_'
        stem.connection.authenticate(self.tor_controller, 
                                     password=self.control_password)

        #check everything is fine with tor, if so, set to only try US-based
	#IP addresses
        self.tor_controller.send('GETINFO status/bootstrap-phase')
        response = self.tor_controller.recv()
        if "SUMMARY=\"Done\"" not in str(response):
            self.tor_controller.signal(Signal.NEWNYM)
            raise ValueError("Tor error:" + str(response) + "\n")

	#if everything is fine, setup webdriver
        self.driver = webdriver.Firefox(profile)
        self.driver.implicitly_wait(30)

    
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

        #Go to twitter and sign up for an account
        self.make_twitter(fake_email,randomName,randomPW,email_name)

        #save new credentials combo in a file
        with open('twitter_creds', 'a') as out:
            out.write(randomName + ":" + randomPW + '\n' + 
                      self.base_url + "/#/" + email_domain 
                      + "/" + email_name + "/" + '\n')
        
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

    def make_twitter(self, email, uname, pw, ename):
	driver = self.driver
        driver.get("www.twitter.com")
        driver.find_element_by_name("user[name]").clear()
        driver.find_element_by_name("user[name]").send_keys(uname)
        driver.find_element_by_name("user[email]").clear()
        driver.find_element_by_name("user[email]").send_keys(email)
        driver.find_element_by_name("user[user_password]").clear()
        driver.find_element_by_name("user[user_password]").send_keys(pw)
        driver.find_element_by_xpath("(//button[@type='submit'])[3]").click()
        time.sleep(3)
        driver.find_element_by_id("username").clear()
        driver.find_element_by_id("username").send_keys(ename)
        driver.find_element_by_name("submit_button").click()
        time.sleep(3)
#        try:
	driver.find_element_by_xpath("/html/body/div[2]/div/div/" +
                                     "div[2]/div/div/div/div[1]/div/a").click()
 #       except:
            #assume we are not allowed to make new twitters from this identity
            #create new identity and try again
  #          self.tor_controller.send(Signal.NEWNYM)
   #         print("Account creation failed, trying again with new identity")        
    #        self.make_twitter(email, uname, pw, ename)
     #       sys.exit()

        driver.find_element_by_link_text("Continue").click()
        driver.find_element_by_partial_link_text("Follow").click()
        driver.find_element_by_link_text("Skip this step").click()

    
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
