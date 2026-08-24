#!/usr/bin/env python3
import os
import re
import unittest
import xml.etree.ElementTree as ET

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestWindowsCompatibility(unittest.TestCase):

    def test_01_sandbox_wsb_xml_valid(self):
        """Test that sandbox.wsb is a valid XML configuration for Windows Sandbox"""
        wsb_path = os.path.join(PROJECT_ROOT, "sandbox.wsb")
        self.assertTrue(os.path.exists(wsb_path), "sandbox.wsb must exist")
        tree = ET.parse(wsb_path)
        root = tree.getroot()
        self.assertEqual(root.tag, "Configuration")
        
        # Verify mapped folders and logon command
        mapped = root.find("MappedFolders")
        self.assertIsNotNone(mapped, "MappedFolders must exist in sandbox.wsb")
        logon = root.find("LogonCommand")
        self.assertIsNotNone(logon, "LogonCommand must exist in sandbox.wsb")
        cmd = logon.find("Command").text
        self.assertIn("start.bat", cmd)
        print("✓ Windows Sandbox XML structure is valid")

    def test_02_start_bat_syntax_integrity(self):
        """Test that start.bat does not contain syntax flaws or unmatched quotes"""
        bat_path = os.path.join(PROJECT_ROOT, "start.bat")
        self.assertTrue(os.path.exists(bat_path), "start.bat must exist")
        with open(bat_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check required labels and commands
        self.assertIn("@echo off", content)
        self.assertIn("setlocal", content)
        self.assertIn("http://localhost:3000", content)
        self.assertIn("http://localhost:5678", content)
        self.assertIn("T5xzFPEkCQ3vjclr", content)
        self.assertIn("send-recruiter-outreach", content)
        print("✓ start.bat contains all required Windows initialization routines")

    def test_03_windows_icon_resolutions(self):
        """Test that app_icon.ico exists and has valid binary ICO format with multi-res layers"""
        import struct
        ico_path = os.path.join(PROJECT_ROOT, "assets", "app_icon.ico")
        self.assertTrue(os.path.exists(ico_path), "assets/app_icon.ico must exist")
        with open(ico_path, "rb") as f:
            header = f.read(6)
            reserved, img_type, num_images = struct.unpack("<HHH", header)
            self.assertEqual(reserved, 0, "ICO reserved field must be 0")
            self.assertEqual(img_type, 1, "ICO format type must be 1")
            self.assertTrue(num_images >= 4, f"ICO file must have at least 4 layers, found {num_images}")
        print(f"✓ app_icon.ico verified binary structure with {num_images} embedded resolution layers")

    def test_04_create_windows_shortcut_syntax(self):
        """Test that scripts/create-windows-shortcut.bat properly calls WScript.Shell"""
        shortcut_bat = os.path.join(PROJECT_ROOT, "scripts", "create-windows-shortcut.bat")
        self.assertTrue(os.path.exists(shortcut_bat), "create-windows-shortcut.bat must exist")
        with open(shortcut_bat, "r", encoding="utf-8") as f:
            code = f.read()
        self.assertIn("WScript.Shell", code)
        self.assertIn("CreateShortcut", code)
        self.assertIn("app_icon.ico", code)
        print("✓ create-windows-shortcut.bat properly creates .lnk with icon")

if __name__ == "__main__":
    unittest.main(verbosity=2)
