from django.test import TestCase
from django.test import Client
from django.core.urlresolvers import reverse
import simplejson as json

class TextAnalyzerTest(TestCase):
    
    def test_extract_named_entities(self):
        """
        Tests an example of named entities extraction.
        """
        client = Client()
        response = client.get("/text_analyzer/extract_named_entities/?text=I+love+Twitter")
        response_json = response.content
        named_entities = json.loads(response_json)
        print named_entities
        self.assertEqual(1, len(named_entities), "Expected 1 and only 1 named entity to be extracted from the text")
        self.assertEqual("Twitter", named_entities[0]["name"], "Expected the extracted named entity to be Twitter")
        
    def test_extract_essence(self):
        """
        Tests an example of named entities extraction.
        """
        client = Client()
        response = client.get("/text_analyzer/extract_essence/?text=Some text from twitter by @somebody").content
        self.assertEqual("Some text from twitter", response)
        response = client.get("/text_analyzer/extract_essence/?text=Some text from twitter via @somebody").content
        self.assertEqual("Some text from twitter", response)
        response = client.get("/text_analyzer/extract_essence/?text=RT @somebody: Some text from twitter").content
        self.assertEqual("Some text from twitter", response)
        
