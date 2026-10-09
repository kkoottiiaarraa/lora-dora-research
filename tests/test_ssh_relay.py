import unittest
from scripts.setup_ssh_relay import render_unit


class SshRelayTests(unittest.TestCase):
    def test_listener_uses_only_tailnet_address_and_service_has_no_credentials(self):
        unit = render_unit("100.105.205.79", "198.51.100.42")
        self.assertIn("bind=100.105.205.79", unit)
        self.assertIn("User=nobody", unit)
        self.assertIn("TCP4:198.51.100.42:22,connect-timeout=10", unit)
        self.assertNotIn("0.0.0.0", unit)
        self.assertNotIn("Password", unit)

    def test_non_tailnet_listener_rejected(self):
        for address in ("0.0.0.0", "127.0.0.1", "203.0.113.12", "100.1.2.3", "::1"):
            with self.subTest(address=address), self.assertRaises(ValueError):
                render_unit(address, "198.51.100.42")

    def test_invalid_port_and_unit_injection_rejected(self):
        for port in (0, 22, 65536, "2222\nUser=root"):
            with self.subTest(port=port), self.assertRaises(ValueError):
                render_unit("100.105.205.79", "198.51.100.42", listen_port=port)
        with self.assertRaises(ValueError):
            render_unit("100.105.205.79", "198.51.100.42\nUser=root")


if __name__ == "__main__":
    unittest.main()
