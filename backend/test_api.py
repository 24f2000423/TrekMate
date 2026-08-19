import unittest
from app import create_app
from database import db
from models import User, Trek, Booking, Notification, ExportJob
from tasks import send_daily_reminders, generate_monthly_activity_report, export_user_bookings_csv

class TMATestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_01_health_check(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'healthy')
        print("[PASS] Health check endpoint OK")

    def test_02_admin_login(self):
        res = self.client.post('/api/auth/login', json={
            'identifier': 'admin@trekma.com',
            'password': 'Admin@123'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('access_token', data)
        self.assertEqual(data['user']['role'], 'admin')
        print("[PASS] Superuser Admin login OK")

    def test_03_staff_login(self):
        res = self.client.post('/api/auth/login', json={
            'identifier': 'alex@trekma.com',
            'password': 'Staff@123'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('access_token', data)
        self.assertEqual(data['user']['role'], 'staff')
        print("[PASS] Trek Staff login OK")

    def test_04_user_registration_and_login(self):
        username = f"new_trekker_{abs(hash('test_user_reg')) % 100000}"
        email = f"{username}@example.com"
        # Delete if exists
        User.query.filter((User.username == username) | (User.email == email)).delete()
        db.session.commit()

        res = self.client.post('/api/auth/register', json={
            'name': 'New Trekker',
            'username': username,
            'email': email,
            'password': 'Password@123',
            'contact_no': '+91 91122 33445'
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertIn('access_token', data)
        self.assertEqual(data['user']['role'], 'user')
        print("[PASS] Trekker self-registration OK")

    def test_05_trek_search_and_caching(self):
        # 1st call
        res1 = self.client.get('/api/treks?difficulty=Moderate')
        self.assertEqual(res1.status_code, 200)
        data1 = res1.get_json()
        self.assertIsInstance(data1['treks'], list)

        # 2nd call (verifies cache retrieval)
        res2 = self.client.get('/api/treks?difficulty=Moderate')
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertTrue(data2.get('cached', False))
        print("[PASS] Trek search, filter, and Redis caching OK")

    def test_06_booking_flow_and_slot_management(self):
        # Login as trekker
        login_res = self.client.post('/api/auth/login', json={
            'identifier': 'john@example.com',
            'password': 'User@123'
        })
        token = login_res.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        # Find open trek with available slots
        trek = Trek.query.filter(Trek.status == 'Open', Trek.available_slots >= 2).first()
        self.assertIsNotNone(trek)
        initial_slots = trek.available_slots

        # Ensure no active booking exists for this specific test trek
        user = User.query.filter_by(email='john@example.com').first()
        Booking.query.filter_by(user_id=user.id, trek_id=trek.id, status='Booked').delete()
        db.session.commit()

        # Book 2 slots
        book_res = self.client.post('/api/bookings', json={
            'trek_id': trek.id,
            'seats': 2,
            'special_notes': 'Test booking'
        }, headers=headers)
        self.assertEqual(book_res.status_code, 201)
        booking_data = book_res.get_json()['booking']
        booking_id = booking_data['id']

        # Verify slot decrement
        trek_after = Trek.query.get(trek.id)
        self.assertEqual(trek_after.available_slots, initial_slots - 2)

        # Duplicate booking prevention
        dup_res = self.client.post('/api/bookings', json={
            'trek_id': trek.id,
            'seats': 1
        }, headers=headers)
        self.assertEqual(dup_res.status_code, 400)

        # Cancel booking and verify slot recovery
        cancel_res = self.client.post(f'/api/bookings/{booking_id}/cancel', headers=headers)
        self.assertEqual(cancel_res.status_code, 200)

        trek_final = Trek.query.get(trek.id)
        self.assertEqual(trek_final.available_slots, initial_slots)
        print("[PASS] Booking flow, slot decrement, duplicate check, and cancellation refund OK")

    def test_07_admin_analytics_and_moderation(self):
        # Admin login
        login_res = self.client.post('/api/auth/login', json={
            'identifier': 'admin@trekma.com',
            'password': 'Admin@123'
        })
        token = login_res.get_json()['access_token']
        headers = {'Authorization': f'Bearer {token}'}

        # Stats
        stats_res = self.client.get('/api/admin/stats', headers=headers)
        self.assertEqual(stats_res.status_code, 200)
        metrics = stats_res.get_json()['metrics']
        self.assertIn('total_treks', metrics)
        self.assertIn('total_users', metrics)

        # Moderation
        user_res = self.client.get('/api/admin/users', headers=headers)
        self.assertEqual(user_res.status_code, 200)
        users = user_res.get_json()['users']
        self.assertTrue(len(users) > 0)
        print("[PASS] Admin analytics and user moderation endpoints OK")

    def test_08_celery_tasks(self):
        # Test daily reminder task
        rem_res = send_daily_reminders()
        self.assertEqual(rem_res['status'], 'SUCCESS')

        # Test monthly activity report task (PDF and HTML)
        rep_res = generate_monthly_activity_report(8, 2026)
        self.assertEqual(rep_res['status'], 'SUCCESS')
        self.assertTrue(rep_res['html_file'].endswith('.html'))
        self.assertTrue(rep_res['pdf_file'].endswith('.pdf'))

        # Test CSV export task
        exp_res = export_user_bookings_csv(user_id=1, task_id='test_unit_export_1')
        self.assertEqual(exp_res['status'], 'SUCCESS')
        self.assertTrue(exp_res['file_name'].endswith('.csv'))
        print("[PASS] Celery tasks (Daily reminders, Monthly PDF/HTML report, Async CSV Export) OK")

if __name__ == '__main__':
    unittest.main()
