import io
import typing

from fpdf import FPDF, XPos, YPos


class Color:
    dark = '#000000'
    light = '#ffffff'
    primary = '#3f51b5'
    secondary = '#52525b'
    muted = '#a1a1aa'


class Resume:
    profile: typing.Any
    pdf: FPDF
    filename: str
    file: io.BytesIO

    color = Color()

    def __init__(self, profile):
        self.profile = profile
        self.pdf = FPDF()
        self.pdf.add_page()
        self.pdf.set_auto_page_break(auto=True, margin=15)
        self.add_all_sections()
        self.file = io.BytesIO(self.pdf.output())
        self.filename = f'{self.profile.owner.username}_resume.pdf'

    def format_date(self, date_obj):
        if not date_obj:
            return 'Present'
        return date_obj.strftime('%b %Y')

    def add_cell(
        self,
        *args,
        new_x: str | XPos = XPos.LMARGIN,
        new_y: str | YPos = YPos.NEXT,
        **kwargs,
    ):
        self.pdf.cell(*args, new_x=new_x, new_y=new_y, **kwargs)

    def add_multi_cell(
        self,
        *args,
        new_x: str | XPos = XPos.LMARGIN,
        new_y: str | YPos = YPos.NEXT,
        **kwargs,
    ):
        self.pdf.multi_cell(*args, new_x=new_x, new_y=new_y, **kwargs)

    def add_section_header(self, title: str):
        self.pdf.ln(2)
        self.pdf.set_font('helvetica', 'B', 18)
        self.pdf.set_text_color(self.color.dark)
        self.add_cell(0, 8, title)
        self.pdf.set_fill_color(self.color.primary)
        self.add_cell(0, 0.5, '', fill=True)  # Primary border
        self.pdf.ln(2)

    def add_entry_title(
        self,
        title: str,
        size=14,
        link=None,
        sub_title=None,
        w: float = 0,
        h: float = 6.0,
    ):
        self.pdf.set_font('helvetica', 'B', size)
        self.pdf.set_text_color(self.color.primary)
        if sub_title:
            self.add_cell(
                w, h, title, link=link, new_x=XPos.END, new_y=YPos.LAST
            )
            self.pdf.set_font('helvetica', '', size)
            self.pdf.set_text_color(self.color.secondary)
            self.add_cell(w, h, sub_title)
        else:
            self.add_cell(w, h, title, link=link)

    def add_entry_dates(self, start, end, location=None):
        self.pdf.set_font('helvetica', '', 10)
        self.pdf.set_text_color(self.color.muted)
        date_str = f'{self.format_date(start)} - {self.format_date(end)}'
        if location:
            date_str += f'  |  {location}'
        self.add_cell(0, 5, date_str)

    def add_entry(
        self,
        title: str,
        sub_title=None,
        title_link=None,
        summary=None,
        start=None,
        end=None,
        location=None,
        keywords=None,
        links=None,
    ):
        self.add_entry_title(title, link=title_link, sub_title=sub_title)
        if start:
            self.add_entry_dates(start, end, location)
        if links:
            self.pdf.set_font('helvetica', '', 10)
            self.pdf.set_text_color(self.color.secondary)
            for link in links:
                self.add_cell(0, 5, link.label or link.href, link=link.href)
        if summary:
            self.pdf.set_font('helvetica', '', 11)
            self.pdf.set_text_color(self.color.dark)
            self.add_multi_cell(0, 5, summary)
        if keywords:
            self.pdf.set_font('helvetica', '', 10)
            self.pdf.set_text_color(self.color.secondary)
            kws = typing.cast(str, keywords).split(',')
            self.add_cell(0, 5, ' '.join([f'#{kw.strip()}' for kw in kws]))
        self.pdf.ln(2)

    def add_header(self):
        self.pdf.set_font('helvetica', 'B', 28)
        self.pdf.set_text_color(self.color.dark)
        self.add_cell(0, 10, self.profile.name)
        if self.profile.title:
            self.add_entry_title(title=self.profile.title, size=18, h=8)
        if self.profile.location:
            self.pdf.set_font('helvetica', '', 10)
            self.pdf.set_text_color(self.color.secondary)
            self.add_cell(0, 5, self.profile.location)
        if self.profile.bio:
            self.pdf.ln(2)
            self.pdf.set_font('helvetica', '', 12)
            self.pdf.set_text_color(self.color.dark)
            self.add_multi_cell(0, 5, self.profile.bio)
        self.pdf.ln(2)

    def add_contact(self):
        profile = self.profile
        self.pdf.set_font('helvetica', '', 10)
        self.pdf.set_text_color(self.color.secondary)
        if profile.email:
            self.add_cell(0, 5, profile.email, f'mailto://{profile.email}')
        if profile.tel:
            self.add_cell(0, 5, profile.tel, f'tel://{profile.tel}')
        for link in profile.links.filter(project__isnull=True):
            self.add_cell(0, 5, link.label or link.href, link.href)
        self.pdf.ln(2)

    def add_education(self):
        educations = self.profile.educations.all()
        if educations.exists():
            self.add_section_header('Education')
            for edu in educations:
                self.add_entry(
                    title=edu.title,
                    summary=edu.summary,
                    start=edu.start_date,
                    end=edu.end_date,
                )

    def add_work_experiences(self):
        work_exps = self.profile.work_experiences.all()
        if work_exps.exists():
            self.add_section_header('Work Experience')
            for work in work_exps:
                self.add_entry(
                    title=work.position,
                    sub_title=f'at {work.company}',
                    summary=work.summary,
                    start=work.start_date,
                    end=work.end_date,
                    location=work.location,
                )

    def add_projects(self):
        projects = self.profile.projects.all()
        if projects.exists():
            self.add_section_header('Projects')
            for proj in projects:
                self.add_entry(
                    title=proj.title,
                    title_link=proj.href,
                    summary=proj.summary,
                    start=proj.start_date,
                    end=proj.end_date,
                    keywords=proj.keywords,
                    links=proj.links.all() if proj.links.exists() else None,
                )

    def add_courses(self):
        courses = self.profile.courses.all()
        if courses.exists():
            self.add_section_header('Courses & Certifications')
            for course in courses:
                self.add_entry(
                    title=course.name,
                    sub_title=f'from {course.academy}',
                    title_link=course.href,
                    start=course.start_date,
                    end=course.end_date,
                )

    def add_skills(self):
        skills = self.profile.skills.all()
        if skills.exists():
            self.add_section_header('Skills')
            for skill in skills:
                self.add_entry(title=skill.name, keywords=skill.keywords)

    def add_all_sections(self):
        self.add_header()
        self.add_contact()
        self.add_education()
        self.add_work_experiences()
        self.add_projects()
        self.add_courses()
        self.add_skills()
