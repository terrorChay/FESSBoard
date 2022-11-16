# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Companies(models.Model):
    company_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=255)
    company_type = models.CharField(max_length=32)
    company_sphere = models.CharField(max_length=12)
    company_website = models.TextField()

    class Meta:
        managed = False
        db_table = 'companies'


class EventManagers(models.Model):
    event = models.ForeignKey('Events', models.DO_NOTHING)
    student = models.ForeignKey('Students', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'event_managers'


class EventParticipants(models.Model):
    event = models.ForeignKey('Events', models.DO_NOTHING)
    student = models.ForeignKey('Students', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'event_participants'


class Events(models.Model):
    event_id = models.AutoField(primary_key=True)
    event_name = models.CharField(max_length=255)
    event_start_date = models.DateField()
    event_end_date = models.DateField()
    event_description = models.TextField()
    is_frozen = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'events'


class Groups(models.Model):
    group_id = models.AutoField(primary_key=True)
    curator = models.ForeignKey('Students', models.DO_NOTHING, db_column='curator')

    class Meta:
        managed = False
        db_table = 'groups'


class ProjectGroups(models.Model):
    project = models.ForeignKey('Projects', models.DO_NOTHING)
    group = models.ForeignKey(Groups, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'project_groups'


class ProjectManagers(models.Model):
    project = models.ForeignKey('Projects', models.DO_NOTHING)
    student = models.ForeignKey('Students', models.DO_NOTHING)
    is_coordinator = models.IntegerField()
    is_moderator = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'project_managers'


class Projects(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=255)
    project_description = models.TextField()
    is_frozen = models.IntegerField()
    project_start_date = models.DateField()
    project_end_date = models.DateField()
    project_grade = models.CharField(max_length=3)
    project_field = models.CharField(max_length=17)
    project_company = models.ForeignKey(Companies, models.DO_NOTHING, db_column='project_company')

    class Meta:
        managed = False
        db_table = 'projects'


class Students(models.Model):
    student_id = models.AutoField(primary_key=True)
    student_surname = models.CharField(max_length=255)
    student_name = models.CharField(max_length=255)
    student_midname = models.CharField(max_length=255)
    bachelor_start_year = models.TextField(blank=True, null=True)  # This field type is a guess.
    master_start_year = models.TextField(blank=True, null=True)  # This field type is a guess.
    student_status = models.CharField(max_length=20)
    bachelors_university = models.ForeignKey('Universities', models.DO_NOTHING, db_column='bachelors_university', blank=True, null=True)
    masters_university = models.ForeignKey('Universities', models.DO_NOTHING, related_name='mast_uni', db_column='masters_university', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'students'


class StudentsInGroups(models.Model):
    group = models.ForeignKey(Groups, models.DO_NOTHING)
    student = models.ForeignKey(Students, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'students_in_groups'


class Teachers(models.Model):
    teacher_id = models.AutoField(primary_key=True)
    teacher_surname = models.CharField(max_length=255)
    teacher_name = models.CharField(max_length=255)
    teacher_midname = models.CharField(max_length=255)
    teacher_university = models.ForeignKey('Universities', models.DO_NOTHING, db_column='teacher_university', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'teachers'


class TeachersInEvents(models.Model):
    teacher = models.ForeignKey(Teachers, models.DO_NOTHING)
    event = models.ForeignKey(Events, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'teachers_in_events'


class TeachersInProjects(models.Model):
    teacher = models.ForeignKey(Teachers, models.DO_NOTHING)
    project = models.ForeignKey(Projects, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'teachers_in_projects'


class Universities(models.Model):
    university_id = models.AutoField(primary_key=True)
    university_name = models.CharField(max_length=255)
    university_logo = models.TextField()

    class Meta:
        managed = False
        db_table = 'universities'


# Create your models here.
class Companies_test(models.Model):
    class CompanyTypes(models.TextChoices):
        big_commercial_company = 'Крупная коммерческая организация'
        governmental_company = 'Государственная организация'
        small_and_medium_company = 'Малый и средний бизнес'

    class CompanySpheres(models.TextChoices):
        education = 'Образование'
        production = 'Производство'
        retail = 'Ритейл'

    company_id = models.BigIntegerField(primary_key=True)
    company_name = models.CharField(max_length=100)
    company_type = models.CharField(max_length=100, choices=CompanyTypes.choices)
    company_sphere = models.CharField(max_length=100, choices=CompanySpheres.choices)
    company_website = models.CharField(max_length=100)


