from services import *

#add try and catch
class ExtractNamedEntitiesTask(Task):
     name = "text_analyzer.extract_named_entities"
     def run(self, request, **kwargs):
         logger = self.get_logger(**kwargs)
         logger.info("Extracting named entities...")
         return extract_named_entities(request)
tasks.register(ExtractNamedEntitiesTask)

#add try and catch
class ExtractEssenceTask(Task):
     name = "text_analyzer.extract_essence"
     def run(self, request, **kwargs):
         logger = self.get_logger(**kwargs)
         logger.info("Extracting essence...")
         return extract_essence(request)
tasks.register(ExtractEssenceTask)