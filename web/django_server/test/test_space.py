import logging

from django_server.const import SpaceStateEnum, ManClassEnum
from django_server.graphene.utils import get_global_id_from_object
from django_server.test.test_base import BaseTestCase
from django_server.models import Space, Building

logger = logging.getLogger('__file__')


class SpaceTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        pass

    def setUp(self):
        self.clean_db()

    def test_create_building(self):
        gql = """
        mutation CreateBuilding($name:String!, $address:String!, $detailedAddress:String, $phone:String) {
            createBuilding(name:$name, address:$address, detailedAddress:$detailedAddress, phone:$phone) {
                building {
                    name
                    address
                    detailedAddress
                    phone
                    madeUser {
                        name
                    }
                }
            }
        }
        """
        variables = {
            'name': '슈퍼빌딩',
            'address': '서울 서대문구',
            'detailedAddress': '123층',
            'phone': '010-1234-5678'
        }

        data = self.execute(gql, variables)['createBuilding']['building']
        self.assertEqual(data['name'], variables['name'])
        self.assertEqual(data['address'], variables['address'])
        self.assertEqual(data['detailedAddress'], variables['detailedAddress'])
        self.assertEqual(data['phone'], variables['phone'])
        self.assertEqual(1, Building.objects.all().count())

    def test_update_building(self):
        user = self.create_user()
        building = self.create_building(name="빌딩1", address="주소1", user=user)

        gql = """
        mutation UpdateBuilding($id:ID!, $name:String, $address:String, $detailedAddress:String, $phone:String) {
            updateBuilding(id:$id, name:$name, address:$address, detailedAddress:$detailedAddress, phone:$phone) {
                building {
                    name
                    address
                    detailedAddress
                    phone
                }
            }
        }
        """
        variables = {
            'id': get_global_id_from_object('Building', building.pk),
            'name': '빌딩3',
            'address': '주소3',
            'detailedAddress': '123층',
            'phone': '010-1234-5678'
        }

        data = self.execute(gql, variables)['updateBuilding']['building']
        self.assertEqual(data['name'], variables['name'])
        self.assertEqual(data['address'], variables['address'])
        self.assertEqual(data['detailedAddress'], variables['detailedAddress'])
        self.assertEqual(data['phone'], variables['phone'])

    def test_delete_building(self):
        user = self.create_user()
        building = self.create_building(name="빌딩1", address="주소1", user=user)

        gql = """
        mutation DeleteBuilding($id:ID!) {
            deleteBuilding(id:$id) {
                ok
            }
        }
        """
        variables = {
            'id': get_global_id_from_object('Building', building.pk),
        }

        self.assertEqual(1, Building.objects.all().count())

        ok = self.execute(gql, variables)['deleteBuilding']['ok']
        self.assertTrue(ok)

        self.assertEqual(0, Building.objects.all().count())

    def test_query_building(self):
        user = self.create_user()
        self.create_building(name="빌딩1", address="주소1", user=user)
        self.create_building(name="빌딩2", address="주소2", user=user)

        gql = """
        query AllBuildings {
            allBuildings {
                edges {
                    node {
                        id
                        name
                        address
                    }
                }
            }
        }
        """

        edges = self.execute(gql)['allBuildings']['edges']
        data1 = edges[0]['node']
        data2 = edges[1]['node']

        self.assertEqual(2, len(edges))
        self.assertEqual('빌딩1', data1['name'])
        self.assertEqual('주소1', data1['address'])
        self.assertEqual('빌딩2', data2['name'])
        self.assertEqual('주소2', data2['address'])

    def test_create_space(self):
        building_name = '와우빌딩'
        building = self.create_building(name=building_name)

        gql = """
        mutation CreateSpace($buildingId:ID!, $name:String!, $requiredManClass:ManClassEnum, $state:SpaceStateEnum) {
            createSpace(buildingId:$buildingId, name:$name, requiredManClass:$requiredManClass, state:$state) {
                space {
                    name
                    state
                    requiredManClass
                    building {
                        name
                    }
                }
            }
        }
        """
        variables = {
            'name': '슈퍼빌딩',
            'requiredManClass': ManClassEnum.ADMIN.name,
            'state': SpaceStateEnum.AVAILABLE.name
        }

        with self.assertRaises(Exception):
            self.execute(gql, variables)['createSpace']['space']

        variables['buildingId'] = get_global_id_from_object('Building', building.pk)

        data = self.execute(gql, variables)['createSpace']['space']
        self.assertEqual(data['name'], variables['name'])
        self.assertEqual(data['state'], variables['state'])
        self.assertEqual(data['requiredManClass'], variables['requiredManClass'])
        self.assertEqual(data['building']['name'], building_name)
        self.assertEqual(1, Space.objects.all().count())

    def test_update_space(self):
        space = self.create_space()

        gql = """
        mutation UpdateSpace($id:ID!, $buildingId:ID, $name:String, $requiredManClass:ManClassEnum, $state:SpaceStateEnum) {
            updateSpace(id:$id, buildingId:$buildingId, name:$name, requiredManClass:$requiredManClass, state:$state) {
                space {
                    name
                    state
                    requiredManClass
                }
            }
        }
        """
        variables = {
            'id': get_global_id_from_object('Space', space.pk),
            'name': '그냥빌딩',
            'requiredManClass': ManClassEnum.MEMBER.name,
            'state': SpaceStateEnum.UNAVAILABLE.name
        }

        data = self.execute(gql, variables)['updateSpace']['space']
        self.assertEqual(data['name'], variables['name'])
        self.assertEqual(data['requiredManClass'], variables['requiredManClass'])
        self.assertEqual(data['state'], variables['state'])

    def test_delete_space(self):
        space = self.create_space()

        gql = """
        mutation DeleteSpace($id:ID!) {
            deleteSpace(id:$id) {
                ok
            }
        }
        """
        variables = {
            'id': get_global_id_from_object('Space', space.pk),
        }

        self.assertEqual(1, Space.objects.all().count())

        ok = self.execute(gql, variables)['deleteSpace']['ok']
        self.assertTrue(ok)

        self.assertEqual(0, Space.objects.all().count())

    def test_query_space(self):
        user = self.create_user()
        building = self.create_building(name="빌딩1", address="주소1", user=user)
        self.create_space(name="공간1", user=user, building=building)
        self.create_space(name="공간2", user=user, building=building)

        gql = """
        query AllSpaces {
            allSpaces {
                edges {
                    node {
                        id
                        name
                        state
                    }
                }
            }
        }
        """

        edges = self.execute(gql)['allSpaces']['edges']
        data1 = edges[0]['node']
        data2 = edges[1]['node']

        self.assertEqual(2, len(edges))
        self.assertEqual('공간1', data1['name'])
        self.assertEqual('공간2', data2['name'])
        self.assertEqual(SpaceStateEnum.WATING.name, data2['state'])
