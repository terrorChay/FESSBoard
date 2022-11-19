from django.db import models


class Companies(models.Model):
    company_id = models.AutoField(primary_key=True)
    company_name = models.CharField(max_length=255)
    company_type = models.ForeignKey('CompanyTypes', models.DO_NOTHING, db_column='company_type')
    company_sphere = models.ForeignKey('CompanySpheres', models.DO_NOTHING, db_column='company_sphere')
    company_website = models.TextField()

    class Meta:
        managed = False
        db_table = 'companies'

    def __str__(self):
        return ""

class CompanySpheres(models.Model):
    company_sphere_id = models.AutoField(primary_key=True)
    company_sphere = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'company_spheres'

    def __str__(self):
        return "%s" % self.company_sphere


class CompanyTypes(models.Model):
    company_type_id = models.AutoField(primary_key=True)
    company_type = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'company_types'

    def __str__(self):
        return "%s" % self.company_type


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


class FieldSpheres(models.Model):
    sphere_id = models.AutoField(primary_key=True)
    sphere = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'field_spheres'


class Groups(models.Model):
    group_id = models.AutoField(primary_key=True)
    curator = models.ForeignKey('Students', models.DO_NOTHING, db_column='curator')

    class Meta:
        managed = False
        db_table = 'groups'


class ProjectFields(models.Model):
    field_id = models.AutoField(primary_key=True)
    field = models.CharField(max_length=255)
    sphere = models.ForeignKey(FieldSpheres, models.DO_NOTHING, db_column='sphere')

    class Meta:
        managed = False
        db_table = 'project_fields'


class ProjectGrades(models.Model):
    grade_id = models.AutoField(primary_key=True)
    grade = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'project_grades'


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
    project_grade = models.ForeignKey(ProjectGrades, models.DO_NOTHING, db_column='project_grade')
    project_field = models.ForeignKey(ProjectFields, models.DO_NOTHING, db_column='project_field')
    project_company = models.ForeignKey(Companies, models.DO_NOTHING, db_column='project_company')

    class Meta:
        managed = False
        db_table = 'projects'


class Regions(models.Model):
    region_id = models.AutoField(primary_key=True)
    region = models.CharField(max_length=255)
    is_foreign = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'regions'


class StudentStatuses(models.Model):
    student_status_id = models.AutoField(primary_key=True)
    student_status = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'student_statuses'

    def __str__(self):
        return "%s" % self.student_status


class Students(models.Model):
    student_id = models.AutoField(primary_key=True)
    student_surname = models.CharField(max_length=255)
    student_name = models.CharField(max_length=255)
    student_midname = models.CharField(max_length=255)
    bachelor_start_year = models.CharField(max_length=255, blank=True, default=None, null=True)  # This field type is a guess.
    master_start_year = models.CharField(max_length=255, blank=True)  # This field type is a guess.
    student_status = models.ForeignKey(StudentStatuses, models.DO_NOTHING, db_column='student_status')
    bachelors_university = models.ForeignKey('Universities', models.DO_NOTHING, db_column='bachelors_university',
                                             blank=True, null=True)
    masters_university = models.ForeignKey('Universities', models.DO_NOTHING, related_name='masters_uni', db_column='masters_university',
                                           blank=True, null=True)

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
    teacher_university = models.ForeignKey('Universities', models.DO_NOTHING, db_column='teacher_university',
                                           blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'teachers'

    def __str__(self):
        return "%s" % self.teacher_name + self.teacher_surname + self.teacher_midname


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
    university_region = models.ForeignKey(Regions, models.DO_NOTHING, db_column='university_region')

    class Meta:
        managed = False
        db_table = 'universities'

    def __str__(self):
        return "%s" % self.university_name
