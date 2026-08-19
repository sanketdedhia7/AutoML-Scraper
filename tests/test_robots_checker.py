import pytest
from unittest.mock import patch, MagicMock
from pipeline.robots_checker import RobotsChecker

def test_robots_checker_allows_mock_urls():
    checker = RobotsChecker()
    assert checker.is_allowed("https://example.com/some/article") is True
    assert checker.is_allowed("http://localhost:8000/test") is True

@patch("urllib.robotparser.RobotFileParser.read")
@patch("urllib.robotparser.RobotFileParser.can_fetch")
def test_robots_checker_enforces_rules(mock_can_fetch, mock_read):
    checker = RobotsChecker()
    mock_can_fetch.return_value = False
    
    res = checker.is_allowed("https://disallowed-site.com/secret")
    assert res is False
    assert mock_can_fetch.called
