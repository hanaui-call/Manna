import logging

from django_server.const import SpaceStateEnum, ManClassEnum
from django_server.graphene.utils import get_global_id_from_object
from django_server.test.test_base import BaseTestCase
from django_server.models import Space, Building

logger = logging.getLogger(__name__)


class SpaceTestCase(BaseTestCase):
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

        data = self.execute(gql, variables, user=self.user)['createBuilding']['building']
        self.assertEqual(variables['name'], data['name'])
        self.assertEqual(variables['address'], data['address'])
        self.assertEqual(variables['detailedAddress'], data['detailedAddress'])
        self.assertEqual(variables['phone'], data['phone'])
        self.assertEqual(1, Building.objects.all().count())
        self.assertEqual(self.user.name, data['madeUser']['name'])

    def test_update_building(self):
        building = self.create_building(name="빌딩1", address="주소1", user=self.user)

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

        data = self.execute(gql, variables, user=self.user)['updateBuilding']['building']
        self.assertEqual(variables['name'], data['name'])
        self.assertEqual(variables['address'], data['address'])
        self.assertEqual(variables['detailedAddress'], data['detailedAddress'])
        self.assertEqual(variables['phone'], data['phone'])

    def test_delete_building(self):
        building = self.create_building(name="빌딩1", address="주소1", user=self.user)

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

        ok = self.execute(gql, variables, user=self.user)['deleteBuilding']['ok']
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
        building = self.create_building(name=building_name, user=self.user)

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

        data = self.execute(gql, variables, user=self.user)['createSpace']['space']
        self.assertEqual(variables['name'], data['name'])
        self.assertEqual(variables['state'], data['state'])
        self.assertEqual(variables['requiredManClass'], data['requiredManClass'])
        self.assertEqual(building_name, data['building']['name'])
        self.assertEqual(1, Space.objects.all().count())

    def test_update_space(self):
        space = self.create_space(user=self.user)

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

        data = self.execute(gql, variables, user=self.user)['updateSpace']['space']
        self.assertEqual(variables['name'], data['name'])
        self.assertEqual(variables['requiredManClass'], data['requiredManClass'])
        self.assertEqual(variables['state'], data['state'])

    def test_delete_space(self):
        space = self.create_space(user=self.user)

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

        ok = self.execute(gql, variables, user=self.user)['deleteSpace']['ok']
        self.assertTrue(ok)

        self.assertEqual(0, Space.objects.all().count())

    def test_query_space(self):
        building = self.create_building(name="빌딩1", address="주소1", user=self.user)
        self.create_space(name="공간1", user=self.user, building=building)
        self.create_space(name="공간2", user=self.user, building=building)

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

    def test_query_zoom(self):
        self.create_zoom("Zoom1", 'zoom1@hanaui.net', 'hanaui', '123 456 7890', '1Nt', 'https://us04web.zoom.us/j/1')
        self.create_zoom("Zoom2", 'zoom2@hanaui.net', 'hanaui', '123 456 7899', '2Nt', 'https://us04web.zoom.us/j/2')

        gql = """
        query AllZooms{
            allZooms {
                edges {
                    node {
                        id
                        name
                        accountId
                        meetingRoomId
                        url
                    }
                }
            }
        }
        """

        edges = self.execute(gql)['allZooms']['edges']
        data1 = edges[0]['node']
        data2 = edges[1]['node']

        self.assertEqual(2, len(edges))
        self.assertEqual('Zoom1', data1['name'])
        self.assertEqual('Zoom2', data2['name'])
        self.assertEqual('zoom1@hanaui.net', data1['accountId'])
        self.assertEqual('https://us04web.zoom.us/j/2', data2['url'])
