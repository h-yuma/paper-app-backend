import os
import unittest

from flask_sqlalchemy import SQLAlchemy

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
    self.new_pmid = "87654321"
    self.new_title = "New Title"
    self.new_last_author = "New Last Author"
    self.new_publication_date = "2023-01-01"
    self.new_url = "https://pubmed.ncbi.nlm.nih.gov/87654321"
    self.new_abstract = "New Abstract"

    # paper tag attributes
    self.new_tag = "New Tag"

    # result abst translation attributes
    self.new_translated_abstract = "New Translation"
    self.new_language_abst_translation = "English"
    
    # result abst summary attributes
    self.new_abst_summary = "New Summary"
    self.new_language_abst_summary = "English"

    # result paper summary attributes
    self.new_paper_summary = "New Summary"
    self.new_length = "long"
    self.new_language_paper_summary = "English"


# ----------------------------------------------------------------------------#
# Test Class
# ----------------------------------------------------------------------------#
class TestModel(unittest.TestCase):
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
    
    def test_inset_into_users(self):
        # create new user
        new_user = User(
            id=self.new_id,
            name=self.new_name,
            email=self.new_email
        )
        with self.app.app_context():
            new_user.insert()

            # retrieve new entry
            query = db.session.get(User, new_user.id)
            # check the new entry attributes
            self.assertEqual(query.id, self.new_id)
            self.assertEqual(query.name, self.new_name)
            self.assertEqual(query.email, self.new_email)
    
    def test_insert_into_papers(self):
        # create new paper
        new_paper = Paper(
            pmid=self.new_pmid,
            title=self.new_title,
            last_author=self.new_last_author,
            publication_date=self.new_publication_date,
            url=self.new_url,
            abstract=self.new_abstract
        )
        with self.app.app_context():
            user = db.session.get(User, self.id)

            new_paper.user = user

            # insert new paper
            new_paper.insert()

            # retrieve new entry
            query = db.session.get(Paper, new_paper.id)
            # check the new entry attributes
            self.assertEqual(query.pmid, self.new_pmid)
            self.assertEqual(query.title, self.new_title)
            self.assertEqual(query.last_author, self.new_last_author)
            self.assertEqual(query.publication_date.strftime("%Y-%m-%d"), \
                             self.new_publication_date)
            self.assertEqual(query.url, self.new_url)
            self.assertEqual(query.abstract, self.new_abstract)
            self.assertIsNotNone(query.created_at)
    
    def test_insert_into_paper_tags(self):
        # create new paper tag
        new_paper_tag = PaperTag(
            tag=self.new_tag
        )
        with self.app.app_context():
            paper_query = db.select(Paper).where(Paper.pmid == self.pmid)
            paper = db.session.scalars(paper_query).first()
            new_paper_tag.paper = paper

            # insert new paper tag
            new_paper_tag.insert()

            # retrieve new entry
            query = db.session.get(PaperTag, new_paper_tag.id)
            # check the new entry attributes
            self.assertEqual(query.tag, self.new_tag)
            self.assertIsNotNone(query.created_at)
    
    def test_insert_into_result_abst_translation(self):
        # create new result abst translation
        new_result_abst_translation = ResultAbstTranslation(
            translated_abstract=self.new_translated_abstract,
            language=self.new_language_abst_translation
        )
        with self.app.app_context():
            paper_query = db.select(Paper).where(Paper.pmid == self.pmid)
            paper = db.session.scalars(paper_query).first()
            new_result_abst_translation.paper = paper

            # insert new result abst translation
            new_result_abst_translation.insert()

            # retrieve new entry
            query = db.session.get(ResultAbstTranslation, new_result_abst_translation.id)
            # check the new entry attributes
            self.assertEqual(query.translated_abstract, self.new_translated_abstract)
            self.assertEqual(query.language, self.new_language_abst_translation)
            self.assertIsNotNone(query.created_at)
    
    def test_insert_into_result_abst_summary(self):
        # create new result abst summary
        new_result_abst_summary = ResultAbstSummary(
            abst_summary=self.new_abst_summary,
            language=self.new_language_abst_summary
        )
        with self.app.app_context():
            user = db.session.get(User, self.id)
            new_result_abst_summary.user = user

            # insert new result abst summary
            new_result_abst_summary.insert()

            # retrieve new entry
            query = db.session.get(ResultAbstSummary, new_result_abst_summary.id)
            # check the new entry attributes
            self.assertEqual(query.abst_summary, self.new_abst_summary)
            self.assertEqual(query.language, self.new_language_abst_summary)
            self.assertIsNotNone(query.created_at)
    
    def test_insert_into_result_paper_summary(self):
        # create new result paper summary
        new_result_paper_summary = ResultPaperSummary(
            paper_summary=self.new_paper_summary,
            length=self.new_length,
            language=self.new_language_paper_summary
        )
        with self.app.app_context():
            user = db.session.get(User, self.id)
            new_result_paper_summary.user = user

            # insert new result paper summary
            new_result_paper_summary.insert()

            # retrieve new entry
            query = db.session.get(ResultPaperSummary, new_result_paper_summary.id)
            # check the new entry attributes
            self.assertEqual(query.paper_summary, self.new_paper_summary)
            self.assertEqual(query.length, self.new_length)
            self.assertEqual(query.language, self.new_language_paper_summary)
            self.assertIsNotNone(query.created_at)
    





if __name__ == "__main__":
    unittest.main()

        
