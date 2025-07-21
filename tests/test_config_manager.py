import os
import tempfile
import yaml
import pytest
from ocr_receipt.config import ConfigManager

def test_yaml_loading(tmp_path):
    config_data = {'foo': 'bar', 'nested': {'value': 42}}
    config_file = tmp_path / 'config.yaml'
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config_data, f)
    cm = ConfigManager(str(config_file))
    assert cm.get('foo') == 'bar'
    assert cm.get('nested.value') == 42

def test_env_override(monkeypatch, tmp_path):
    config_data = {'foo': 'bar'}
    config_file = tmp_path / 'config.yaml'
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config_data, f)
    monkeypatch.setenv('FOO', 'env_bar')
    cm = ConfigManager(str(config_file))
    assert cm.get('foo') == 'env_bar'

def test_runtime_update_and_save(tmp_path):
    config_data = {'foo': 'bar'}
    config_file = tmp_path / 'config.yaml'
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config_data, f)
    cm = ConfigManager(str(config_file))
    cm.set('foo', 'baz')
    assert cm.get('foo') == 'baz'
    cm.save()
    with open(config_file, 'r', encoding='utf-8') as f:
        saved = yaml.safe_load(f)
    assert saved['foo'] == 'baz' 