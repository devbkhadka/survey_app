'''functional tests for survey app'''
from urllib.parse import urlparse
from time import sleep
from functools import wraps

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.conf import settings
from django.urls import reverse

from selenium import webdriver
from selenium.common.exceptions import WebDriverException, ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait



from . import factory
from ..models import Question, QuestionTypes


def wrap_in_wait(func, retires=5):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return wait(func, *args, retires=retires, **kwargs)
    return wrapper

def wait(func, *args, retires=10, exceptions=[AssertionError, NoSuchElementException], **kwargs):
    for i in range(retires):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print('retry', i)
            if type(e) not in exceptions:
                raise e

            if i == retires-1:
                raise e

            sleep(0.5 + i*.2)

def wait_until_document_ready(browser):
    WebDriverWait(browser, 20) \
    .until(lambda d: d.execute_script('return document.readyState == "complete"'))
            


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
        title_elements = wait(self.browser.find_elements_by_css_selector, '.surveys .card-title')
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

    def test_previous_button_disabled_for_1st_question(self):
        # for 1st question
        _, btn_previous = self.load_question_at(1)
        with self.assertRaises(ElementClickInterceptedException):
            btn_previous.click()

    def test_previous_button_works(self):
        btn_next, btn_previous = self.load_question_at(2)
        btn_next.click()
        
        btn_previous = wait(self.browser.find_element_by_id, 'btn-previous')
        sleep(1)
        btn_previous.click()
        expected_url = reverse('survey:take_survey', args=[self.survey.pk, 2])
        sleep(3)
        self.assertEqual(urlparse(self.browser.current_url).path, expected_url)

        
    def test_next_button_works(self):
        # for 1st question
        btn_next, _ = self.load_question_at(1)
        btn_next.click()
        expected_url = reverse('survey:take_survey', args=[self.survey.pk, 2])
        self.assertEqual(urlparse(self.browser.current_url).path, expected_url)

        # for questions betweeen 1st and last
        btn_next, _ = self.load_question_at(2)
        btn_next.click()
        expected_url = reverse('survey:take_survey', args=[self.survey.pk, 3])
        self.assertEqual(urlparse(self.browser.current_url).path, expected_url)

        # for last question
        last_index = self.survey.questions.count()
        btn_next, _ = self.load_question_at(last_index)

        expected_url = reverse('survey:finish_survey', args=[self.survey.pk])
        next_url = urlparse(btn_next.get_attribute('href')).path
        btn_next.click()
        self.assertEqual(next_url, expected_url)


    def test_survey_response_id_cookie_set(self):
        url = reverse('survey:take_survey', args=[self.survey.pk, 1])
        self.browser.get(self.live_server_url+url)
        value = self.browser.get_cookie(f'survey_response_id_{self.survey.pk}')['value']
        self.assertTrue(value.isnumeric())



class QuestionTypeTestCase(FunctionalTestCase):
    question_type = None
    def setUp(self):
        self.survey = factory.create_survey_with_questions()
        self.question, index = factory.get_question_and_index_of_type(self.survey, self.question_type.name)
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
        self.browser.find_element_by_css_selector('input#id_response')

        form = self.browser.find_element_by_id('question_form')
        self.assertEqual(urlparse(form.get_attribute('action')).path, self.url)
        self.assertEqual(form.get_attribute('method'), 'post')

    def test_question_form_is_loaded_with_existing_answer(self):
        '''Test question form pre-loads'''
        self.browser.get(self.live_server_url + self.url)
        inp = self.browser.find_element_by_css_selector("input#id_response")
        inp.send_keys("This is my answer")

        self.browser.find_element_by_id('btn-next').click()

        wait_until_document_ready(self.browser)
        btn_previous = self.browser.find_element_by_id('btn-previous')
        btn_previous.click()
        wait_until_document_ready(self.browser)
        inp = self.browser.find_element_by_css_selector("input#id_response")
        self.assertEqual(inp.get_attribute('value'), "This is my answer")

        


class TestFinishSurveyView(FunctionalTestCase):
    '''Functional test for FinishSurvey view'''

    def setUp(self):
        super().setUp()
        self.survey, self.survey_response = factory.create_survey_with_text_question_and_answer()
        self.cookie_key = f'survey_response_id_{self.survey.pk}'
        self.browser.get(self.live_server_url)
        self.browser.add_cookie({'name': self.cookie_key, 'value': str(self.survey_response.pk)})
        url = reverse('survey:finish_survey', args=[self.survey.pk])
        self.browser.get(self.live_server_url+url)

    def test_review_button_works(self):
        '''Test review button starts the survey again for review'''
       
        self.browser.find_element_by_id("btn-review").click()

        self.assertEqual(urlparse(self.browser.current_url).path,
                         reverse('survey:take_survey', args=[self.survey.pk, 1]))
                         

    def test_complete_button_marks_survey_response_complete(self):
        '''Test pressing Finish button updates survey_response's complted_date'''
        
        btn_finish = self.browser.find_element_by_id("btn-finish")

        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_css_selector('div#done')

        btn_finish.click()
        wait(self.assertEqual, urlparse(self.browser.current_url).path, reverse('survey:thank_you'))

        self.assertEqual(urlparse(self.browser.current_url).path, reverse('survey:thank_you'))
