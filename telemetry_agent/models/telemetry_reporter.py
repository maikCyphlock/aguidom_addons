import requests
import logging
import hashlib
import os
import subprocess
from pathlib import Path
from odoo import models, api
from odoo.modules.module import get_module_path

_logger = logging.getLogger(__name__)

class TelemetryReporter(models.AbstractModel):
    _name = 'telemetry.reporter'
    _description = 'Telemetry Reporter'

    def _calculate_module_hash(self, module_path):
        """
        Calculate MD5 hash of all files in a module (excluding .fileignore patterns).
        Returns first 8 characters of hash as version identifier.
        
        Supports .fileignore file with gitignore-like patterns.
        """
        try:
            if not module_path:
                return None
                
            module_dir = Path(module_path)
            if not module_dir.exists():
                return None
            
            # Read .fileignore patterns if exists
            ignore_patterns = ['__pycache__', '*.pyc', '*.pyo', '.git', '.fileignore']
            fileignore_path = module_dir / '.fileignore'
            if fileignore_path.exists():
                try:
                    with open(fileignore_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                ignore_patterns.append(line)
                except (IOError, OSError):
                    pass
            
            # Get all files recursively
            all_files = []
            for item in sorted(module_dir.rglob('*')):
                if item.is_file():
                    # Check if file should be ignored
                    try:
                        relative_path = item.relative_to(module_dir)
                    except ValueError:
                        continue
                        
                    should_ignore = False
                    
                    for pattern in ignore_patterns:
                        # Simple pattern matching
                        if pattern in str(relative_path) or relative_path.match(pattern):
                            should_ignore = True
                            break
                    
                    if not should_ignore:
                        all_files.append(item)
            
            if not all_files:
                return None
            
            # Calculate combined hash
            hash_md5 = hashlib.md5()
            for file_path in all_files:
                try:
                    with open(file_path, 'rb') as f:
                        hash_md5.update(f.read())
                except (IOError, OSError):
                    continue
            
            # Return first 8 chars of hash as version
            return hash_md5.hexdigest()[:8]
        except Exception as e:
            _logger.debug("Could not calculate hash for %s: %s", module_path, e)
            return None

    def _get_git_info(self, module_path):
        """
        Get git branch and latest commit hash for a module.
        Returns dict with 'branch' and 'commit' or None if not a git repo.
        """
        try:
            if not module_path:
                return None
                
            module_dir = Path(module_path)
            if not module_dir.exists():
                return None
            
            # Check if it's a git repository
            git_dir = module_dir
            while git_dir != git_dir.parent:
                if (git_dir / '.git').exists():
                    break
                git_dir = git_dir.parent
            else:
                return None  # No .git found
            
            # Get current branch
            try:
                branch = subprocess.check_output(
                    ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                    cwd=str(git_dir),
                    stderr=subprocess.DEVNULL
                ).decode().strip()
            except (subprocess.CalledProcessError, FileNotFoundError):
                branch = None
            
            # Get latest commit hash
            try:
                commit = subprocess.check_output(
                    ['git', 'rev-parse', '--short', 'HEAD'],
                    cwd=str(git_dir),
                    stderr=subprocess.DEVNULL
                ).decode().strip()
            except (subprocess.CalledProcessError, FileNotFoundError):
                commit = None
            
            if branch or commit:
                return {
                    'branch': branch,
                    'commit': commit
                }
            return None
        except Exception as e:
            _logger.debug("Could not get git info for %s: %s", module_path, e)
            return None

    def _get_module_version_info(self, module):
        """
        Get comprehensive version info for a module.
        Returns dict with manifest_version, content_hash, git_branch, git_commit.
        """
        info = {
            'manifest_version': module.installed_version or None,
            'content_hash': None,
            'git_branch': None,
            'git_commit': None
        }
        
        # Get module path using Odoo utility
        module_path = get_module_path(module.name)
        
        if module_path:
            # Content hash
            content_hash = self._calculate_module_hash(module_path)
            if content_hash:
                info['content_hash'] = content_hash
            
            # Git info
            git_info = self._get_git_info(module_path)
            if git_info:
                info['git_branch'] = git_info.get('branch')
                info['git_commit'] = git_info.get('commit')
        
        return info

    def action_send_report(self):
        """Send telemetry report to HQ with ALL installed modules."""
        client_name = self.env['ir.config_parameter'].sudo().get_param('telemetry.client_name')
        url = self.env['ir.config_parameter'].sudo().get_param('telemetry.hq_url')
        
        if not url:
            _logger.warning("Telemetry HQ URL is not configured.")
            return
        
        if not client_name:
            _logger.warning("Telemetry client name is not configured.")
            return

        # Get ALL installed modules (no author filtering)
        mods = self.env['ir.module.module'].search([('state', '=', 'installed')])
        modules_data = {m.name: self._get_module_version_info(m) for m in mods}
        
        payload = {
            'params': {
                'client_name': client_name,
                'modules': modules_data
            }
        }

        try:
            # Send the report
            response = requests.post(url + '/api/v1/report_versions', json=payload, timeout=10)
            response.raise_for_status()
            _logger.info("Telemetry report sent successfully to %s for client '%s' (%d modules)", 
                        url, client_name, len(modules_data))
        except Exception as e:
            _logger.error("Failed to send telemetry report: %s", e)


