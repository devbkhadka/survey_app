'''functional tests for survey app'''
from urllib.parse import urlparse
from time import sleep

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from django.urls import reverse

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys


from . import factory


class SurveysFunctionalTest(StaticLiveServerTestCase):
    ''''Collections of all functional tests'''
    def setUp(self):
        self.browser = webdriver.Chrome()
        self.surveys_raw = [
            {
                'title': 'Your favourite candidate',
                'summary': 'Answer questions like who is your favourite candidate and why',
                'published_date': '2019-4-20 00:00+0545',
            },
            {
                'title': 'Your view on inflation',
                'summary': 'What do you feel about value of money, do you have some examples?',
                'published_date': '2019-4-20 00:00+0545',
            },
            {
                'title': 'Top movie of 2019',
                'summary': 'Which movie do you like most in the year 2019',
                'published_date': '2019-4-20 00:00+0545',
            }

        ]

        self.surveys = factory.create_surveys(self.surveys_raw)

    def test_can_see_list_of_surveys(self):
        '''Test page lists surveys in database'''
        self.browser.get(self.live_server_url)
        sleep(5)
        title_elements = self.browser.find_elements_by_css_selector('.surveys .card-title')
        summary_elements = self.browser.find_elements_by_css_selector('.surveys .card-text')

        self.assertEqual([survey['title'].lower() for survey in self.surveys_raw],
                         [elem.text.lower() for elem in title_elements])
        self.assertEqual([survey['summary'].lower() for survey in self.surveys_raw],
                         [elem.text.lower() for elem in summary_elements])


    def test_clicking_list_items_takes_to_survey_page(self):
        '''Test clicking on survey items takes to survey page'''
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id(f'survey_{self.surveys[0].pk}').click()
        self.assertEqual(urlparse(self.browser.current_url).path,
                         reverse("survey:detail", args=[self.surveys[0].pk]))

    def tearDown(self):
        self.browser.quit()
        super().tearDown()

class SurveyFunctionalTest(StaticLiveServerTestCase):
    pass