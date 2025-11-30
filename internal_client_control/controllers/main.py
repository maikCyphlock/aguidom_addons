from odoo import http, fields
import logging

_logger = logging.getLogger(__name__)


class ClientVersionController(http.Controller):

    @http.route("/api/v1/report_versions", type="json", auth="public", methods=['POST'])
    def report(self, client_name, modules, **kwargs):
        """
        Receive module version reports from client instances.
        """
        env = http.request.env
        
        if not client_name:
            return {'error': 'client_name is required'}
        
        # Find or create the client instance
        instance = env['client.instance'].sudo().search([('name', '=', client_name)], limit=1)
        
        if not instance:
            instance = env['client.instance'].sudo().create({'name': client_name})
        
        # Update last report timestamp
        instance.write({'last_report': fields.Datetime.now()})
        
        # Get GitHub Token
        github_token = env['ir.config_parameter'].sudo().get_param('internal_client_control.github_api_token')
        headers = {}
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        
        # Process each module
        for module_name, version_info in modules.items():
            # Extract version info
            if isinstance(version_info, dict):
                vals = {
                    'manifest_version': version_info.get('manifest_version'),
                    'content_hash': version_info.get('content_hash'),
                    'git_branch': version_info.get('git_branch'),
                    'git_commit': version_info.get('git_commit'),
                }
            else:
                vals = {
                    'manifest_version': version_info,
                    'content_hash': None,
                    'git_branch': None,
                    'git_commit': None,
                }

            # Find Repo Configuration
            repo_config = env['telemetry.module.repo'].sudo().search([('name', '=', module_name)], limit=1)
            
            state = 'untracked'
            if repo_config:
                # Check if we need to refresh GitHub info (simple cache: 5 min)
                # For now, we'll fetch every time or rely on a stored field if we wanted to optimize
                # Let's fetch every time for simplicity as requested
                
                try:
                    api_url = f"https://api.github.com/repos/{repo_config.github_repo}/commits/{repo_config.github_branch}"
                    # Use standard python requests if available, or urllib
                    import requests
                    response = requests.get(api_url, headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        latest_commit = data.get('sha', '')[:7] # Short hash
                        
                        repo_config.sudo().write({
                            'latest_commit_hash': latest_commit,
                            'last_checked': fields.Datetime.now()
                        })
                        
                        # Compare
                        if vals['git_commit'] == latest_commit:
                            # Check for manual changes (hash)
                            # We need to store the "official" hash for this commit to know if it changed
                            # But we don't have the official hash from GitHub easily without downloading
                            # So we rely on: if commit matches, it SHOULD be clean. 
                            # If user says "manual changes", we might need a flag from the agent saying "dirty"
                            # For now, let's assume if commit matches, it's latest.
                            # UNLESS we want to track "manual" state.
                            # If the agent sent a content_hash, and we had a history of "official hash for this commit"...
                            # Let's simplify:
                            state = 'latest'
                        else:
                            state = 'outdated'
                    else:
                        _logger.warning(f"GitHub API Error for {module_name}: {response.status_code}")
                        # Keep previous state or unknown?
                        pass
                except Exception as e:
                    _logger.error(f"Failed to query GitHub for {module_name}: {e}")

            vals['state'] = state

            # Update/Create Status
            module_status = env['client.module.status'].sudo().search([
                ('instance_id', '=', instance.id),
                ('module_name', '=', module_name)
            ], limit=1)
            
            if module_status:
                module_status.write(vals)
            else:
                vals.update({
                    'instance_id': instance.id,
                    'module_name': module_name,
                })
                env['client.module.status'].sudo().create(vals)
        
        return {'success': True, 'message': 'Report processed successfully', 'client': client_name}
