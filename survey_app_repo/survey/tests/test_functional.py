'''functional tests for survey app'''
from urllib.parse import urlparse
from time import sleep

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from django.urls import reverse

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, ElementClickInterceptedException
from selenium.webdriver.common.keys import Keys


from . import factory
from ..models import Question, QuestionTypes

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
        survey_with_question = factory.create_survey_with_questions()
        self.browser.get(self.live_server_url+survey_with_question.get_absolute_url())
        self.browser.find_element_by_id('btn_takesurvey').click()

        expected_url = reverse('survey:take_survey', args=[survey_with_question.pk, 1])
        self.assertEqual(urlparse(self.browser.current_url).path, expected_url)

    def test_take_survey_button_disabled_when_no_questions(self):
        '''Test Take Survey buttion is disabled if survey don't have questions'''
        self.browser.get(self.live_server_url+self.survey.get_absolute_url())
        
        # raises error if button is not disabled
        btn = self.browser.find_element_by_css_selector('#btn_takesurvey.disabled')
        with self.assertRaises(ElementClickInterceptedException):
            btn.click()

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

    def load_question_at(self, index):
        url = reverse('survey:take_survey', args=[self.survey.pk, index])
        self.browser.get(self.live_server_url+url)
        btn_next = self.browser.find_element_by_id('btn-next')
        btn_previous = self.browser.find_element_by_id('btn-previous')
        return btn_next, btn_previous

    def test_next_and_previous_buttons_shown_correctly(self):
        # for 1st question
        btn_next, btn_previous = self.load_question_at(1)
        with self.assertRaises(ElementClickInterceptedException):
            btn_previous.click()
        btn_next.click() # btn_next is clickable

        # for 2nd question
        btn_next, btn_previous = self.load_question_at(2)
        btn_next.click()
        btn_next, btn_previous = self.load_question_at(2)
        btn_previous.click()

        #for last question
        index = self.survey.questions.count()
        btn_next, btn_previous = self.load_question_at(index)
        with self.assertRaises(ElementClickInterceptedException):
            btn_next.click()
        btn_previous.click() # btn_previous is clickable
        
    def test_next_and_previous_button_works(self):
        btn_next, btn_previous = self.load_question_at(1)
        btn_next.click()
        expected_url = reverse('survey:take_survey', args=[self.survey.pk, 2])
        self.assertEqual(urlparse(self.browser.current_url).path, expected_url)

        btn_next, btn_previous = self.load_question_at(2)
        btn_next.click()
        expected_url = reverse('survey:take_survey', args=[self.survey.pk, 3])
        self.assertEqual(urlparse(self.browser.current_url).path, expected_url)

        btn_next, btn_previous = self.load_question_at(2)
        btn_previous.click()
        expected_url = reverse('survey:take_survey', args=[self.survey.pk, 1])
        self.assertEqual(urlparse(self.browser.current_url).path, expected_url)


class QuestionTypeTestCase(FunctionalTestCase):
    question_type = None
    def setUp(self):
        self.survey = factory.create_survey_with_questions()
        print(self.question_type)
        index, self.question = factory.get_question_and_index_of_type(self.survey, self.question_type.name)
        self.url = reverse('survey:take_survey', args=[self.survey.pk, index])
        super().setUp()


class TestDescQuestionType(QuestionTypeTestCase):
    '''Test case for Text question type'''
    question_type = QuestionTypes.DESC
    def test_ui_for_description_type_question(self):
        self.browser.get(self.live_server_url+self.url)
        self.assertEqual(self.browser.find_element_by_id('description').text, self.question.description)

class TestTextQuestionType(QuestionTypeTestCase):
    '''Test case for Text question type'''
    question_type = QuestionTypes.TEXT
    def test_ui_of_text_question_type(self):
        '''Test ui components of text question type'''
        self.browser.get(self.live_server_url + self.url)
        self.browser.find_element_by_css_selector("input#id_response")
        
