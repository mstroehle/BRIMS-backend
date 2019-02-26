import graphene
import graphql_jwt

from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.contrib.auth import get_user_model

from .models import PatientModel, SpecimenModel, AliquotModel

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()

class PatientType(DjangoObjectType):
    class Meta:
        model = PatientModel


class SpecimenType(DjangoObjectType):
    type = graphene.String()
    patientid = graphene.Int()

    class Meta:
        model = SpecimenModel
        description = " Specimens collected for a patient "

    # return actual type as string rather then type as an object
    # example: "Dried Blood Spot" instead of type{ type: "Dried Blood Spot"}
    def resolve_type(self, info):
        return '{}'.format(self.type.type)

    # override type field to return a string rather than an object
    def resolve_patientid(self, info):
        return '{}'.format(self.patient.id)


class AliquotType(DjangoObjectType):
    visit = graphene.String()
    type = graphene.String()
    specimenid = graphene.Int()
    class Meta:
        model = AliquotModel

    def resolve_specimenid(self, info):
        return '{}'.format(self.specimen.id)

    def resolve_visit(self, info):
        return '{}'.format(self.visit.label)

    def resolve_type(self, info):
        return '{}'.format(self.type.type)


class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)

    def mutate(self, info, username, password, email):
        user = get_user_model()(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()

        return CreateUser(user=user)


class CreatePatientMutation(graphene.Mutation):
    id = graphene.Int()
    pid = graphene.String()
    external_id = graphene.String()
    synced = graphene.Boolean()

    class Arguments:
        pid = graphene.String()
        external_id = graphene.String()
        synced = graphene.Boolean()

    def mutate(self, info, pid, **kwargs):
        external_id = kwargs.get('external_id', None)
        synced = kwargs.get('synced', False)

        patient_input = PatientModel(
            pid=pid,
            external_id=external_id,
            synced=synced)
        patient_input.save()

        return CreatePatientMutation(
            id=patient_input.id,
            pid=patient_input.pid,
            external_id=patient_input.external_id,
            synced=patient_input.synced,
        )

class CreatePatientAPIMutation(graphene.Mutation):
    id = graphene.Int()
    pid = graphene.String()
    external_id = graphene.String()

    class Arguments:
        pid = graphene.String()
        external_id = graphene.String(required=False)

    def mutate(self, info, pid, external_id=""):
        patient_input = PatientModel(pid=pid, external_id=external_id)
        patient_input.save()
        return CreatePatientMutation(
            id=patient_input.id,
            pid=patient_input.pid,
            external_id=patient_input.external_id,
        )



class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    create_patient = CreatePatientMutation.Field()
    create_patient_api = CreatePatientAPIMutation.Field()
    create_user = CreateUser.Field()


class Query(graphene.ObjectType):
    # name here is what ends up in query
    # (underscores end up camelCase for graphql spec)
    me = graphene.Field(UserType)
    users = graphene.List(UserType)
    all_patients = graphene.List(PatientType)
    all_specimen = graphene.List(SpecimenType, patient=graphene.Int())
    all_aliquot = graphene.List(AliquotType, specimen=graphene.Int())
    patient = graphene.Field(PatientType,
                             id=graphene.Int(),
                             pid=graphene.String(),
                             external_id=graphene.String())

    def resolve_users(self, info):
        return get_user_model().objects.all()

    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception('Not logged in!')

        return user

    def resolve_all_patients(self, info, **kwargs):
        return PatientModel.objects.all()

    def resolve_all_specimen(self, info, **kwargs):
        patient = kwargs.get('patient')
        if patient is not None:
            return SpecimenModel.objects.all().filter(patient=patient)
        return SpecimenModel.objects.all()

    def resolve_all_aliquot(self, info, **kwargs):
        specimen = kwargs.get('specimen')
        if specimen is not None:
            return AliquotModel.objects.all().filter(specimen=specimen)
        return AliquotModel.objects.all()


    def resolve_patient(self, info, **kwargs):
        id = kwargs.get('id')
        pid = kwargs.get('pid')
        external_id = kwargs.get('external_id')

        if id is not None:
            return PatientModel.objects.get(pk=id)

        if pid is not None:
            return PatientModel.objects.get(pid=pid)

        if external_id is not None:
            return PatientModel.objects.get(external_id=external_id)

        return None


schema = graphene.Schema(query=Query, mutation=Mutation)
