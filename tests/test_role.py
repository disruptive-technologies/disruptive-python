# Project imports.
import disruptive as dt
import tests.mock_responses as dtresponses


class TestRole():

    def test_unpack(self, request_mock):
        # Update the response data with project data.
        res = dtresponses.project_user_role
        request_mock.json = res

        # Call the appropriate endpoint.
        p = dt.Role.get_role('project.user')

        # Assert attributes unpacked correctly.
        assert p.role == res['name'].split('/')[-1]
        assert p.display_name == res['displayName']
        assert p.description == res['description']
        assert p.permissions == res['permissions']

    def test_get_role(self, request_mock):
        # Update the response data with role data.
        request_mock.json = dtresponses.project_developer_role

        # Call the appropriate endpoint.
        r = dt.Role.get_role('project.developer')

        # Verify request parameters.
        request_mock.assert_requested(
            method='GET',
            url=dt.base_url+'/roles/project.developer',
        )

        # Assert single request sent.
        request_mock.assert_request_count(1)

        # Assert output is instance of Role.
        assert isinstance(r, dt.Role)

    def test_list_roles(self, request_mock):
        # Update the response data with list of role data.
        request_mock.json = dtresponses.roles

        # Call the appropriate endpoint
        roles = dt.Role.list_roles()

        # Verify request parameters.
        request_mock.assert_requested(
            method='GET',
            url=dt.base_url+'/roles',
        )

        # Assert single request sent.
        request_mock.assert_request_count(1)

        # Assert instances of Role in output list.
        for r in roles:
            assert isinstance(r, dt.Role)
