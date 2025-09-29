#!/usr/bin/env python3
"""
Tests for PythonAnywhere Git Pipeline
"""

import unittest
import tempfile
import os
import yaml
from unittest.mock import Mock, patch, MagicMock
from main import PythonAnywhereGitPipeline, PAWCredentials, load_credentials_from_yaml


class TestPAWCredentials(unittest.TestCase):
    """Test PAWCredentials class"""
    
    def test_credentials_with_http_host(self):
        """Test credentials with http host"""
        creds = PAWCredentials("user", "token", "https://example.com")
        self.assertEqual(creds.host, "https://example.com")
    
    def test_credentials_without_http_host(self):
        """Test credentials without http prefix"""
        creds = PAWCredentials("user", "token", "example.com")
        self.assertEqual(creds.host, "https://example.com")


class TestYAMLLoading(unittest.TestCase):
    """Test YAML configuration loading"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_config = {
            'pythonanywhere': {
                'username': 'testuser',
                'token': 'testtoken',
                'host': 'testhost.com'
            }
        }
    
    def test_load_valid_yaml(self):
        """Test loading valid YAML configuration"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.test_config, f)
            f.flush()
            
            try:
                creds = load_credentials_from_yaml(f.name)
                self.assertEqual(creds.username, 'testuser')
                self.assertEqual(creds.token, 'testtoken')
                self.assertEqual(creds.host, 'https://testhost.com')
            finally:
                os.unlink(f.name)
    
    def test_load_missing_fields(self):
        """Test loading YAML with missing required fields"""
        incomplete_config = {
            'pythonanywhere': {
                'username': 'testuser'
                # Missing token and host
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(incomplete_config, f)
            f.flush()
            
            try:
                with self.assertRaises(Exception) as context:
                    load_credentials_from_yaml(f.name)
                self.assertIn("Missing required fields", str(context.exception))
            finally:
                os.unlink(f.name)
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent YAML file"""
        with self.assertRaises(Exception):
            load_credentials_from_yaml('nonexistent.yaml')


class TestPythonAnywhereGitPipeline(unittest.TestCase):
    """Test PythonAnywhereGitPipeline class"""
    
    def setUp(self):
        """Set up test environment"""
        self.credentials = PAWCredentials("testuser", "testtoken", "testhost.com")
        self.pipeline = PythonAnywhereGitPipeline(self.credentials)
    
    def test_initialization(self):
        """Test pipeline initialization"""
        self.assertEqual(self.pipeline.credentials.username, "testuser")
        self.assertEqual(self.pipeline.api_base, "https://testhost.com/api/v0/user/testuser")
        self.assertIn("Token testtoken", self.pipeline.session.headers['Authorization'])
    
    @patch('requests.Session.get')
    def test_connection_success(self, mock_get):
        """Test successful connection test"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        result = self.pipeline.test_connection()
        self.assertTrue(result)
    
    @patch('requests.Session.get')
    def test_connection_failure(self, mock_get):
        """Test failed connection test"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        result = self.pipeline.test_connection()
        self.assertFalse(result)
    
    @patch('requests.Session.get')
    def test_connection_exception(self, mock_get):
        """Test connection test with exception"""
        mock_get.side_effect = Exception("Network error")
        
        result = self.pipeline.test_connection()
        self.assertFalse(result)
    
    @patch.object(PythonAnywhereGitPipeline, '_execute_console_commands')
    def test_git_pull(self, mock_execute):
        """Test git pull execution"""
        mock_execute.return_value = {'success': True, 'results': []}
        
        result = self.pipeline.execute_git_pull("/home/user/project", "main")
        
        self.assertTrue(result['success'])
        mock_execute.assert_called_once()
        
        # Check that the correct commands were passed
        called_commands = mock_execute.call_args[0][0]
        self.assertIn("cd /home/user/project", called_commands)
        self.assertIn("git pull origin main", called_commands)
    
    @patch.object(PythonAnywhereGitPipeline, '_execute_console_commands')
    def test_git_clone(self, mock_execute):
        """Test git clone execution"""
        mock_execute.return_value = {'success': True, 'results': []}
        
        result = self.pipeline.execute_git_clone(
            "https://github.com/user/repo.git",
            "/home/user/newproject", 
            "main"
        )
        
        self.assertTrue(result['success'])
        mock_execute.assert_called_once()
        
        # Check that the correct commands were passed
        called_commands = mock_execute.call_args[0][0]
        self.assertIn("git clone -b main https://github.com/user/repo.git /home/user/newproject", called_commands)


class TestConsoleOperations(unittest.TestCase):
    """Test console operations with mocked API calls"""
    
    def setUp(self):
        """Set up test environment"""
        self.credentials = PAWCredentials("testuser", "testtoken", "testhost.com")
        self.pipeline = PythonAnywhereGitPipeline(self.credentials)
    
    @patch('requests.Session.delete')
    @patch('requests.Session.get')
    @patch('requests.Session.post')
    def test_execute_console_commands_success(self, mock_post, mock_get, mock_delete):
        """Test successful console command execution"""
        # Mock console creation
        mock_create_response = Mock()
        mock_create_response.status_code = 201
        mock_create_response.json.return_value = {'id': 123}
        
        # Mock command sending
        mock_send_response = Mock()
        mock_send_response.status_code = 200
        
        # Mock output retrieval
        mock_output_response = Mock()
        mock_output_response.status_code = 200
        mock_output_response.json.return_value = {'output': 'Command executed successfully'}
        
        # Mock console ready check
        mock_ready_response = Mock()
        mock_ready_response.status_code = 200
        
        # Mock console deletion
        mock_delete_response = Mock()
        mock_delete_response.status_code = 204
        
        # Configure mock responses
        mock_post.side_effect = [mock_create_response, mock_send_response]
        mock_get.side_effect = [mock_ready_response, mock_output_response]
        mock_delete.return_value = mock_delete_response
        
        result = self.pipeline._execute_console_commands(["echo 'test'"])
        
        self.assertTrue(result['success'])
        self.assertEqual(result['console_id'], 123)
        self.assertEqual(len(result['results']), 1)
        self.assertEqual(result['results'][0]['output'], 'Command executed successfully')


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
