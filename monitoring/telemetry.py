import os

try:
    from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
    HAVE_PROMETHEUS = True
except ImportError:
    HAVE_PROMETHEUS = False
    
    class DummyMetric:
        def inc(self, amount=1, **kwargs): pass
        def observe(self, amount, **kwargs): pass
        def labels(self, **kwargs): return self
        def set(self, amount, **kwargs): pass

    def Counter(*args, **kwargs): return DummyMetric()
    def Histogram(*args, **kwargs): return DummyMetric()
    def Gauge(*args, **kwargs): return DummyMetric()
    
    make_asgi_app = None

# Define Core Application Metrics
SCRAPER_SUCCESS_TOTAL = Counter(
    'scraper_success_total',
    'Total successful scraper runs',
    ['collector_id']
)

SCRAPER_FAILURE_TOTAL = Counter(
    'scraper_failure_total',
    'Total failed scraper runs',
    ['collector_id']
)

SCRAPER_DURATION_SECONDS = Histogram(
    'scraper_duration_seconds',
    'Scraper execution time in seconds',
    ['collector_id']
)

ARTICLES_EXTRACTED_TOTAL = Counter(
    'articles_extracted_total',
    'Total articles extracted',
    ['collector_id']
)

HEAL_REQUESTS_TOTAL = Counter(
    'heal_requests_total',
    'Total heal requests triggered',
    ['collector_id']
)

metrics_app = make_asgi_app() if HAVE_PROMETHEUS else None
