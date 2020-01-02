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

class FunctionalTestCase(StaticLiveServerTestCase):
    def setUp(self):
        self.browser = webdriver.Chrome()
        super().setUp()

    def tearDown(self):
        self.browser.quit()
        super().tearDown()
    
class SurveysFunctionalTest(FunctionalTestCase):
    ''''Collections of all functional tests'''
    def setUp(self):
        self.surveys = factory.create_surveys()
        super().setUp()

    def test_can_see_list_of_surveys(self):
        '''Test page lists surveys in database'''
        self.browser.get(self.live_server_url)
        sleep(5)
        title_elements = self.browser.find_elements_by_css_selector('.surveys .card-title')
        summary_elements = self.browser.find_elements_by_css_selector('.surveys .card-text')

        self.assertEqual([survey.title.lower() for survey in self.surveys],
                         [elem.text.lower() for elem in title_elements])
        self.assertEqual([survey.summary.lower() for survey in self.surveys],
                         [elem.text.lower() for elem in summary_elements])


    def test_clicking_list_items_takes_to_survey_page(self):
        '''Test clicking on survey items takes to survey page'''
        self.browser.get(self.live_server_url)
        self.browser.find_element_by_id(f'survey_{self.surveys[0].pk}').click()
        self.assertEqual(urlparse(self.browser.current_url).path,
                         reverse("survey:detail", args=[self.surveys[0].pk]))

    

class SurveyFunctionalTest(FunctionalTestCase):
    '''Functional tests for survey detail view'''

    def setUp(self):
        self.survey = factory.create_surveys()[0]
        super().setUp()

    def test_view_shows_correct_survey(self):
        '''Test detail view showing correct survey'''
        self.browser.get(self.live_server_url+self.survey.get_absolute_url())
        survey_title = self.browser.find_element_by_id('survey-title').text
        self.assertEqual(survey_title.lower(), self.survey.title.lower())

        survey_summary = self.browser.find_element_by_id('survey-summary').text
        self.assertEqual(survey_summary, self.survey.summary)

    def test_can_go_to_takesurvey_page(self):
        '''Test can go to takesurvey page of by clicking button'''
        self.browser.get(self.live_server_url+self.survey.get_absolute_url())
        self.browser.find_element_by_id('btn_takesurvey').click()

        expected_url = reverse('survey:take_survey', args=[self.survey.pk])
        self.assertEqual(urlparse(self.browser.current_url).path, expected_url)

class TakeSurveyFunctionalTest(FunctionalTestCase):
    '''Test case for TakeSurvey view'''
    
    def setUp(self):
        self.survey = factory.create_survey_with_questions()
        super().setUp()

    def test_invoking_url_shows_ui_of_1st_question(self):
        '''Test hitting url of TakeSurvey page will show 1st question of specified survey'''
        url = reverse('survey:take_survey', args=[self.survey.pk, 1])
        self.browser.get(self.live_server_url+url)

        self.assertEqual(self.browser.find_element_by_id('survey-title').text.lower(),
                         self.survey.title.lower())

        self.assertEqual(self.browser.find_element_by_id('question-title').text.lower(),
                         self.survey.questions.first().question.lower())
