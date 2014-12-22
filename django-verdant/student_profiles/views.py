
import re
import unicodedata

from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from wagtail.wagtailcore.models import Page
from rca.models import NewStudentPage
from rca.models import NewStudentPageContactsEmail, NewStudentPageContactsPhone, NewStudentPageContactsWebsite
from rca.models import NewStudentPagePreviousDegree, NewStudentPageExhibition, NewStudentPageAward, NewStudentPagePublication, NewStudentPageConference

from .forms import ProfileBasicForm, EmailFormset, PhoneFormset, WebsiteFormset
from .forms import ProfileAcademicDetailsForm, PreviousDegreesFormset, ExhibitionsFormset, AwardsFormset, PublicationsFormset, ConferencesFormset


NEW_STUDENT_PAGE_INDEX = Page.objects.get(id=5)

def slugify(value):
    """
    TODO: documentation
    """
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)


def save_multiple(profile_page, fieldname, formset, form_fieldname, field_model):
    """
    TODO: documentation
    """
    getattr(profile_page, fieldname).all().delete()
    for values in formset.cleaned_data:
        if values and values.get(form_fieldname, '').strip():
            field_model.objects.create(**{
                'page': profile_page,
                form_fieldname: values.get(form_fieldname).strip()
            })




@login_required
def overview(request):
    data = {}

    data['profile_pages'] = NewStudentPage.objects.filter(owner=request.user)

    return render(request, 'student_profiles/overview.html', data)


@login_required
def basic_profile(request, page_id=None):
    data = {}

    if page_id is None:
        profile_page = NewStudentPage(owner=request.user)
        NEW_STUDENT_PAGE_INDEX.add_child(instance=profile_page)
        data['basic_form'] = ProfileBasicForm()
        data['email_formset'] = EmailFormset(prefix='email')
        data['phone_formset'] = PhoneFormset(prefix='phone')
        data['website_formset'] = WebsiteFormset(prefix='website')
    else:
        profile_page = get_object_or_404(NewStudentPage, owner=request.user, id=page_id)
        data['page_id'] = page_id
        data['basic_form'] = ProfileBasicForm(instance=profile_page)
        data['email_formset'] = EmailFormset(
            prefix='email',
            initial=[{'email': x.email} for x in profile_page.emails.all()]
        )
        data['phone_formset'] = PhoneFormset(
            prefix='phone',
            initial=[{'phone': x.phone} for x in profile_page.phones.all()]
        )
        data['website_formset'] = WebsiteFormset(
            prefix='website',
            initial=[{'website': x.website} for x in profile_page.websites.all()]
        )

    if request.method == 'POST':
        data['basic_form'] = basic_form = ProfileBasicForm(request.POST, request.FILES)
        data['email_formset'] = email_formset = EmailFormset(request.POST, prefix='email')
        data['phone_formset'] = phone_formset = PhoneFormset(request.POST, prefix='phone')
        data['website_formset'] = website_formset = WebsiteFormset(request.POST, prefix='website')
        if basic_form.is_valid() and email_formset.is_valid() and phone_formset.is_valid() and website_formset.is_valid():
            bcd = basic_form.cleaned_data
            
            profile_page.first_name = bcd['first_name']
            profile_page.last_name = bcd['last_name']
            
            profile_page.title = u'{} {}'.format(bcd['first_name'], bcd['last_name'])
            profile_page.slug = slugify(profile_page.title)
            
            profile_page.statement = bcd['statement']

            if bcd['profile_image']:
                profile_image = RcaImage.objects.create(
                    image=bcd['profile_image'],
                )
                profile_page.profile_image = profile_image
            
            revision = profile_page.save_revision(
                user=request.user,
                submitted_for_moderation=False,
            )

            # save additional contact data
            def save_contact(fieldname, formset, form_fieldname, field_model):
                getattr(profile_page, fieldname).all().delete()
                for values in formset.cleaned_data:
                    if values and values.get(form_fieldname, '').strip():
                        field_model.objects.create(**{
                            'page': profile_page,
                            form_fieldname: values.get(form_fieldname).strip()
                        })

            save_contact(
                'emails',
                email_formset, 'email',
                NewStudentPageContactsEmail,
            )
            save_contact(
                'phones',
                phone_formset, 'phone',
                NewStudentPageContactsPhone,
            )
            save_contact(
                'websites',
                website_formset, 'website',
                NewStudentPageContactsWebsite,
            )

            return redirect('student-profiles:edit-basic', page_id=profile_page.id)

    return render(request, 'student_profiles/basic.html', data)



@login_required
def academic_details(request, page_id=None):
    data = {}

    profile_page = get_object_or_404(NewStudentPage, owner=request.user, id=page_id)
    data['page_id'] = page_id
    
    data['academic_form'] = ProfileAcademicDetailsForm(instance=profile_page)
    
    def make_formset(title, formset_class, relname, form_attr_name, model_attr_name=None):
        
        model_attr_name = model_attr_name or form_attr_name
        
        data[relname + '_formset'] = formset_class(
            prefix=relname,
            initial=[{form_attr_name: getattr(x, model_attr_name)} for x in getattr(profile_page, relname).all()],
        )
        data[relname + '_formset'].title = title

    make_formset(
        'Previous degrees',
        PreviousDegreesFormset, 'previous_degrees',
        'degree',
    )

    make_formset(
        'Exhibitions',
        ExhibitionsFormset, 'exhibitions',
        'exhibition',
    )

    make_formset(
        'Awards',
        AwardsFormset, 'awards',
        'award',
    )

    make_formset(
        'Publications',
        PublicationsFormset, 'publications',
        'name',
    )

    make_formset(
        'Conferences',
        ConferencesFormset, 'conferences',
        'name',
    )
    
    if request.method == 'POST':
        data['academic_form'] = pf = ProfileAcademicDetailsForm(request.POST)
        data['previous_degrees_formset'] = pdfs = PreviousDegreesFormset(request.POST, prefix='previous_degrees')
        data['exhibitions_formset'] = efs = ExhibitionsFormset(request.POST, prefix='exhibitions')
        data['awards_formset'] = afs = AwardsFormset(request.POST, prefix='awards')
        data['publications_formset'] = pfs = PublicationsFormset(request.POST, prefix='publications')
        data['conferences_formset'] = cfs = ConferencesFormset(request.POST, prefix='conferences')
        
        if pf.is_valid() and pdfs.is_valid() and efs.is_valid() and pfs.is_valid() and cfs.is_valid():
            profile_page.funding = pf.cleaned_data['funding']
            
            revision = profile_page.save_revision(
                user=request.user,
                submitted_for_moderation=False,
            )
            
            save_multiple(
                profile_page, 
                'previous_degrees',
                pdfs, 'degree',
                NewStudentPagePreviousDegree,
            )
            
            save_multiple(
                profile_page, 
                'exhibitions',
                efs, 'exhibition',
                NewStudentPageExhibition,
            )
            
            save_multiple(
                profile_page, 
                'awards',
                afs, 'award',
                NewStudentPageAward,
            )
            
            save_multiple(
                profile_page, 
                'publications',
                pfs, 'name',
                NewStudentPagePublication,
            )
            
            save_multiple(
                profile_page, 
                'conferences',
                cfs, 'name',
                NewStudentPageConference,
            )
            
        
            return redirect('student-profiles:edit-academic', page_id=profile_page.id)
    
    return render(request, 'student_profiles/academic_details.html', data)
