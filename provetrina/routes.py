from rest_framework.routers import SimpleRouter

from . import views

base = 'provetrina'

router = SimpleRouter()

router.register(rf'{base}/profiles', views.ProfileViewSet, 'profile')
router.register(rf'{base}/projects', views.ProjectViewSet, 'project')
router.register(rf'{base}/courses', views.CourseViewSet, 'course')
router.register(rf'{base}/skills', views.SkillViewSet, 'skill')
router.register(rf'{base}/links', views.LinkViewSet, 'link')
router.register(rf'{base}/works', views.WorkExperienceViewSet, 'work')
router.register(rf'{base}/educations', views.EducationViewSet, 'education')
