import tornado.ioloop
import tornado.web
import asyncio
import sys
import os
import importlib
from importlib.util import find_spec
import traceback

CUSTOM_MODULE_NAME = "custom_inference_spec"

class AsyncPredictionHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.response_msg = "Async Handler: "
        try:
            if find_spec(CUSTOM_MODULE_NAME):
                custom_inference_module = importlib.import_module(CUSTOM_MODULE_NAME)
                self.customInference = custom_inference_module.CustomInferenceOrchestrator()
                self.response_msg += ", real inference loaded"
            else :
                self.customInference = None
                self.response_msg += ", Custom Inference Spec Not Loaded"
        except Exception as e:
            print({"error": str(e)})

    async def post(self):
        data = self.request.body
        data_str = data.decode("utf-8")
        try:
            if self.customInference is not None :
                response = await self.customInference.handle(data_str)
                self.response_msg += ", custom inference response recorded"
            else :
                response = "Custom Inference Spec Not Present"
                self.response_msg += ", Custom Inference Spec Not Present"
            self.write({"generated_text": response, "metadata": self.response_msg})
        except Exception as e:
            self.set_status(400)
            print(traceback.format_exc())
            self.write({"error": str(e)})

    async def get(self):
        try:
            if self.customInference is not None :
                response = await self.customInference.handle("Where is Seattle?")
                self.response_msg += ", custom inference response recorded"
            else :
                response = "Custom Inference Spec Not Present"
                self.response_msg += ", Custom Inference Spec Not Present"
            self.write({"generated_text": response, "metadata": self.response_msg})
        except Exception as e:
            self.set_status(400)
            print(traceback.format_exc())
            self.write({"error": str(e)})

class PingHandler(tornado.web.RequestHandler):
    def initialize(self):
        return

    def get(self):
        self.set_status(200)
        self.write("")

    def post(self):
        self.set_status(200)
        self.write("")

def make_app():
    sys.path.append(os.path.abspath('/opt/ml/model/code'))

    return tornado.web.Application([
        (r"/invocations", AsyncPredictionHandler),
        (r"/ping", PingHandler),
    ])

port = 8080

async def main():
    app = make_app()
    app.listen(port)
    print(f"Starting server on http://localhost:{port}")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
    print(f"Started server on http://localhost:{port}")