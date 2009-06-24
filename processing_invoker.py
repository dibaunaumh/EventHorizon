import httplib, urllib
import time
import sys
#from django.contrib.sites.models import Site


def log(message):
    print "[%s] %s" % (time.strftime("%I:%M:%S %p"), message)


def invoke(domain="localhost:8000", verbose=False):
    """Invokes the cells processing service, using an HTTP call"""
    try:
        params_map = {}
        params = urllib.urlencode(params_map)
        headers = {"Content-type": "text/plain", "Accept": "text/html"}
        #site = Site.objects.get(id=1)
        #domain = site.domain
        log("Invoking cells processing at %s..." % domain)
        conn = httplib.HTTPConnection(domain)
        conn.request("GET", "/cells/process/1", params, headers)
        response = conn.getresponse()
        if response.status == 200:
            log("Processing completed successfully.")
        else:
            log("Error in processing (HTTP status code %d)" % response.status)
        data = response.read()
        if verbose:
            print data
        conn.close()
    except:
        log("Failed to invoke cells processing")
        for ei in sys.exc_info():
            log(ei)


if __name__ == "__main__":
    # todo read options from command-line (e.g., domain, interval & verbose)
    log("Processing invoker started")
    while (True):
        invoke()
        time.sleep(10)
