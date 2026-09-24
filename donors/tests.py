from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core import mail
from donors.models import Donor, BloodRequest, MatchLog


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class SignupToMatchIntegrationTest(TestCase):
    """
    Full integration test: user signup -> donor registration -> blood request
    submission -> match creation -> notification email sent.
    """

    def setUp(self):
        # Create a donor user - Profile is auto-created via post_save signal
        self.donor_user = User.objects.create_user(username='test_donor', password='testpass123')
        self.donor_user.profile.is_donor = True
        self.donor_user.profile.save()

        self.donor = Donor.objects.create(
            user=self.donor_user,
            name='Test Donor',
            email='testdonor@example.com',
            blood_group='O+',
            phone_number='9999999999',
            location='Vadodara',
            availability_status=True,
            is_verified=True,
        )

        # Create a requester user - Profile is auto-created via post_save signal
        self.requester_user = User.objects.create_user(username='test_requester', password='testpass123')
        self.requester_user.profile.is_requester = True
        self.requester_user.profile.save()

    def test_signup_creates_profile(self):
        """A newly created user should be linkable to a Profile with correct roles."""
        self.assertTrue(self.donor_user.profile.is_donor)
        self.assertTrue(self.requester_user.profile.is_requester)

    def test_donor_registration_links_to_user(self):
        """Donor record should be correctly linked to its owning User account."""
        self.assertEqual(self.donor.user, self.donor_user)

    def test_blood_request_creates_matchlog_and_sends_email(self):
        """
        Submitting a blood request that matches an existing donor should:
        1. Create a MatchLog entry with status 'Pending'
        2. Send a match-notification email to the donor
        """
        self.client.login(username='test_requester', password='testpass123')

        response = self.client.post('/donors/request/', {
            'requester_name': 'Test Requester',
            'requester_email': 'testrequester@example.com',
            'blood_group_needed': 'O+',
            'urgency': 'High',
            'hospital_location': 'Vadodara',
        })

        self.assertEqual(response.status_code, 200)

        blood_request = BloodRequest.objects.filter(requester_name='Test Requester').first()
        self.assertIsNotNone(blood_request)

        match_log = MatchLog.objects.filter(donor=self.donor, blood_request=blood_request).first()
        self.assertIsNotNone(match_log)
        self.assertEqual(match_log.status, 'Pending')

        # Confirm a notification email was sent (locmem backend captures it in mail.outbox)
        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn('Matched', mail.outbox[-1].subject)
        self.assertEqual(mail.outbox[-1].to, [self.donor.email])

    def test_donor_dashboard_shows_pending_match(self):
        """After a match is created, the donor should see it as Pending in their dashboard."""
        blood_request = BloodRequest.objects.create(
            requester_name='Dashboard Test',
            requester_email='dashtest@example.com',
            blood_group_needed='O+',
            urgency='Medium',
            hospital_location='Vadodara',
        )
        MatchLog.objects.create(donor=self.donor, blood_request=blood_request, status='Pending')

        self.client.login(username='test_donor', password='testpass123')
        response = self.client.get('/donors/dashboard/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vadodara')

    def test_donor_can_accept_match(self):
        """Donor accepting a match should update its status and timestamp."""
        blood_request = BloodRequest.objects.create(
            requester_name='Accept Test',
            requester_email='accepttest@example.com',
            blood_group_needed='O+',
            urgency='Low',
            hospital_location='Vadodara',
        )
        match_log = MatchLog.objects.create(donor=self.donor, blood_request=blood_request, status='Pending')

        self.client.login(username='test_donor', password='testpass123')
        response = self.client.post(f'/donors/respond/{match_log.id}/', {'response': 'Accepted'})

        match_log.refresh_from_db()
        self.assertEqual(match_log.status, 'Accepted')
        self.assertIsNotNone(match_log.responded_at)

    def test_admin_verify_donor_sends_email(self):
        """Verifying a donor should mark is_verified True and send a notification email."""
        admin_user = User.objects.create_user(username='test_admin', password='testpass123')
        admin_user.profile.is_admin = True
        admin_user.profile.save()

        unverified_donor = Donor.objects.create(
            name='Unverified Donor',
            email='unverified@example.com',
            blood_group='A+',
            phone_number='8888888888',
            location='Nadiad',
            is_verified=False,
        )

        self.client.login(username='test_admin', password='testpass123')
        response = self.client.get(f'/donors/verify/{unverified_donor.id}/')

        unverified_donor.refresh_from_db()
        self.assertTrue(unverified_donor.is_verified)
        self.assertEqual(response.status_code, 302)  # redirect after verify

        self.assertGreaterEqual(len(mail.outbox), 1)
        self.assertIn('Verified Donor', mail.outbox[-1].subject)

    def test_donor_with_no_email_does_not_crash_verification(self):
        """
        Verifying a donor with a blank email should not crash the admin action.
        The email attempt should fail gracefully and log the failure, not raise an exception.
        """
        admin_user = User.objects.create_user(username='test_admin_2', password='testpass123')
        admin_user.profile.is_admin = True
        admin_user.profile.save()

        donor_no_email = Donor.objects.create(
            name='No Email Donor',
            email='',
            blood_group='B+',
            phone_number='7777777777',
            location='Nadiad',
            is_verified=False,
        )

        self.client.login(username='test_admin_2', password='testpass123')
        response = self.client.get(f'/donors/verify/{donor_no_email.id}/')

        donor_no_email.refresh_from_db()
        self.assertTrue(donor_no_email.is_verified)
        self.assertEqual(response.status_code, 302)

    def test_duplicate_blood_request_does_not_duplicate_matchlog(self):
        """
        If the same requester submits two separate blood requests for the same
        blood group and location, each request should get its own MatchLog entries
        (not merged or blocked), and no duplicate MatchLog should exist for the
        same donor+request pair even if matching logic runs twice.
        """
        self.client.login(username='test_requester', password='testpass123')

        first_response = self.client.post('/donors/request/', {
            'requester_name': 'Duplicate Test',
            'requester_email': 'dup1@example.com',
            'blood_group_needed': 'O+',
            'urgency': 'High',
            'hospital_location': 'Vadodara',
        })
        second_response = self.client.post('/donors/request/', {
            'requester_name': 'Duplicate Test',
            'requester_email': 'dup2@example.com',
            'blood_group_needed': 'O+',
            'urgency': 'High',
            'hospital_location': 'Vadodara',
        })

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)

        requests = BloodRequest.objects.filter(requester_name='Duplicate Test')
        self.assertEqual(requests.count(), 2)

        for req in requests:
            match_count = MatchLog.objects.filter(donor=self.donor, blood_request=req).count()
            self.assertEqual(match_count, 1)


    def test_donor_with_donation_history_ranks_above_donor_with_none(self):
        """
        ML ranking integration (FR-14): a donor with a real, frequent
        DonationHistory should rank above a donor with no history at all,
        confirming the trained model is actually being applied to reorder
        matched donors, not just returning them unchanged.
        """
        import datetime
        from donors.models import DonationHistory

        frequent_donor = Donor.objects.create(
            name='Frequent Donor',
            email='frequent@example.com',
            blood_group='O+',
            phone_number='9000000001',
            location='Vadodara',
            availability_status=True,
            is_verified=True,
        )
        for i in range(8):
            DonationHistory.objects.create(
                donor=frequent_donor,
                donation_date=datetime.date.today() - datetime.timedelta(days=30 * i),
                is_confirmed=True,
            )

        no_history_donor = Donor.objects.create(
            name='No History Donor',
            email='nohistory@example.com',
            blood_group='O+',
            phone_number='9000000002',
            location='Vadodara',
            availability_status=True,
            is_verified=True,
        )

        self.client.login(username='test_requester', password='testpass123')
        response = self.client.post('/donors/request/', {
            'requester_name': 'Ranking Test',
            'requester_email': 'rankingtest@example.com',
            'blood_group_needed': 'O+',
            'urgency': 'High',
            'hospital_location': 'Vadodara',
        })

        self.assertEqual(response.status_code, 200)
        returned_donors = response.context['matches']
        self.assertGreaterEqual(len(returned_donors), 2)

        names_in_order = [d.name for d in returned_donors]
        self.assertLess(
            names_in_order.index('Frequent Donor'),
            names_in_order.index('No History Donor')
        )