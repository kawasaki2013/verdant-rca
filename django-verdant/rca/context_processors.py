from rca.models import Advert, YEARS, SCHOOL_CHOICES, ALL_PROGRAMMES, PROGRAMME_CHOICES, EVENT_LOCATION_CHOICES, AREA_CHOICES, EVENT_AUDIENCE_CHOICES, RESEARCH_TYPES_CHOICES, WORK_THEME_CHOICES, WORK_TYPES_CHOICES, STAFF_TYPES_CHOICES
from datetime import date


def global_vars(request):
    return {
        'global_adverts': Advert.objects.filter(show_globally=True),
        'global_schools': SCHOOL_CHOICES,
        'global_all_programmes': ALL_PROGRAMMES,
        'global_programmes': dict(PROGRAMME_CHOICES)[str(date.today().year)],
        'global_locations': EVENT_LOCATION_CHOICES,
        'global_areas': AREA_CHOICES,
        'global_years': YEARS,
        'global_audiences': EVENT_AUDIENCE_CHOICES,
        'global_research_types': RESEARCH_TYPES_CHOICES,
        'global_work_themes': WORK_THEME_CHOICES,
        'global_work_types': WORK_TYPES_CHOICES,
        'global_staff_types': STAFF_TYPES_CHOICES,
        'global_events_index_url': '/events/',
        'global_news_index_url': '/news/',
        'global_default_twitter_handle': "RCAevents",
    }
