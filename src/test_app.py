import json
import os
import unittest

from flask_sqlalchemy import SQLAlchemy
import httpx

from app import create_app
from models import (User, Paper, PaperTag, ResultAbstTranslation,
                    ResultAbstSummary, ResultPaperSummary, db, setup_db)
from dotenv import load_dotenv

load_dotenv()

DATABASE_PATH = f'postgresql://{os.environ["DATABASE_USER"]}' + \
                f':{os.environ["DATABASE_PASSWORD"]}' + \
                f'@{os.environ["DATABASE_ENDPOINT"]}:5432' + \
                f'/{os.environ["TEST_DATABASE_NAME"]}'

def set_user(self):
    # user attributes
    self.id = "tarogithub"
    self.name = "Taro"
    self.email = "0000000@gmail.com"

    # create new user
    user = User(
        id=self.id,
        name=self.name,
        email=self.email
    )

    # create new paper
    self.pmid = "12345678"
    self.title = "Title"
    self.last_author = "Last Author"
    self.publication_date = "2022-01-01"
    self.url = "https://pubmed.ncbi.nlm.nih.gov/12345678"
    self.abstract = "Abstract"
    paper = Paper(
        pmid=self.pmid,
        title=self.title,
        last_author=self.last_author,
        publication_date=self.publication_date,
        url=self.url,
        abstract=self.abstract
    )
    paper.user = user

    # create new paper tag
    self.tag = "Tag"
    paper_tag = PaperTag(
        tag=self.tag
    )
    paper_tag.paper = paper

    # create new result abst translation
    self.translated_abstract = "Translation"
    self.language_abst_translation = "Japanese"
    result_abst_translation = ResultAbstTranslation(
        translated_abstract=self.translated_abstract,
        language=self.language_abst_translation
    )
    result_abst_translation.paper = paper

    # create new result abst summary
    self.abst_summary = "Summary"
    self.language_abst_summary = "Japanese"
    result_abst_summary = ResultAbstSummary(
        abst_summary=self.abst_summary,
        language=self.language_abst_summary
    )
    result_abst_summary.user = user

    # create new result paper summary
    self.paper_summary = "Summary"
    self.length = "short"
    self.language_paper_summary = "Japanese"
    result_paper_summary = ResultPaperSummary(
        paper_summary=self.paper_summary,
        length=self.length,
        language=self.language_paper_summary
    )
    result_paper_summary.user = user

    # insert all
    user.insert()

def set_variables(self):
    # user attributes
    self.new_id = "tanakagithub"
    self.new_name = "Tanaka"
    self.new_email = "11111111@gmail.com"

    # paper attributes
    self.new_pmid = "32293474"
    self.new_title = "New Title"
    self.new_last_author = "New Last Author"
    self.new_publication_date = "2023-01-01"
    self.new_url = "https://pubmed.ncbi.nlm.nih.gov/32293474"
    self.new_abstract = "New Abstract"

    # paper tag attributes
    self.new_tag = "New Tag"

    # result abst translation attributes
    self.new_translated_abstract = "New Translation"
    self.new_language_abst_translation = "Japanese"
    
    # result abst summary attributes
    self.new_abst_summary = "New Summary"
    self.new_search_words = ["chemotaxis", "bacteria"]
    self.new_language_abst_summary = "Japanese"

    # result paper summary attributes
    self.new_paper_summary = "New Summary"
    self.new_length = "long"
    self.new_language_paper_summary = "English"


# ----------------------------------------------------------------------------#
# Test Class
# ----------------------------------------------------------------------------#
class TestApp(unittest.TestCase):
    def setUp(self):
        # Executed before each test
        self.database_path = DATABASE_PATH
        self.app = create_app(self.database_path)
        self.client = self.app.test_client
        # setup_db(self.app, self.database_path)

        with self.app.app_context():
            db.drop_all()
            db.create_all()
        #     self.db = SQLAlchemy()
        #     self.db.init_app(self.app)
            set_user(self)
        
        # variables for new instance
        set_variables(self)
    
    def tearDown(self):
        # Executed after each test
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_register_user(self):
        # create data
        data = {
            "user_id": self.new_id,
            "name": self.new_name,
            "email": self.new_email
        }
        with self.app.app_context():
            # check status code
            response = self.client().post('/api/users', data=json.dumps(data),\
                                          content_type='application/json')
            self.assertEqual(response.status_code, 200)
    
    def test_get_user(self):
        with self.app.app_context():
            # check status code
            response = self.client().get(f'/api/users/{self.id}')
            self.assertEqual(response.status_code, 200)
    
    def test_get_user_papars(self):
        with self.app.app_context():
            # check status code
            response = self.client().get(f'/api/users/{self.id}/papers')
            self.assertEqual(response.status_code, 200)
    
    def test_get_user_results_paper_summary(self):
        with self.app.app_context():
            # check status code
            response = self.client().get(f'/api/users/{self.id}/results-paper-summary')
            self.assertEqual(response.status_code, 200)
    
    def test_register_result_abst_summary(self):
        # create data
        data = {
            "search_words": self.new_search_words,
            "language": self.new_language_abst_summary
        }
        with self.app.app_context():
            # check status code
            response = self.client().post(f'/api/users/{self.id}/results-abst-summary', data=json.dumps(data),\
                                          content_type='application/json')
            self.assertEqual(response.status_code, 200)
        
    def test_get_user_results_abst_summary(self):
        with self.app.app_context():
            # check status code
            response = self.client().get(f'/api/users/{self.id}/results-abst-summary')
            self.assertEqual(response.status_code, 200)
    
    def test_register_paper(self):
        # create data
        data = {
            "pmid": self.new_pmid
        }
        with self.app.app_context():
            # check status code
            response = self.client().post(f'/api/users/{self.id}/papers', data=json.dumps(data),\
                                          content_type='application/json')
            self.assertEqual(response.status_code, 200)
    
    def test_get_paper(self):
        with self.app.app_context():
            # check status code
            response = self.client().get(f'/api/papers/1')
            self.assertEqual(response.status_code, 200)
    
    def test_edit_paper_tags(self):
        # create data
        data = {
            "tags": self.new_tag
        }
        with self.app.app_context():
            # check status code
            response = self.client().patch(f'/api/papers/1/tags', data=json.dumps(data),\
                                          content_type='application/json')
            self.assertEqual(response.status_code, 200)
    
    def test_delete_paper(self):
        with self.app.app_context():
            # check status code
            response = self.client().delete(f'/api/papers/1')
            self.assertEqual(response.status_code, 200)
    
    def test_register_result_abst_translation(self):
        # create data
        data = {
            "language": self.new_language_abst_translation
        }
        with self.app.app_context():
            # check status code
            response = self.client().post(f'/api/papers/1/results-abst-translation', data=json.dumps(data),\
                                          content_type='application/json')
            self.assertEqual(response.status_code, 200)
    
    def test_delete_result_paper_summary(self):
        with self.app.app_context():
            # check status code
            response = self.client().delete(f'/api/results-paper-summary/1')
            self.assertEqual(response.status_code, 200)
    
    def test_delete_result_abst_summary(self):
        with self.app.app_context():
            # check status code
            response = self.client().delete(f'/api/results-abst-summary/1')
            self.assertEqual(response.status_code, 200)

if __name__ == "__main__":
    unittest.main()
