from odoo import http
from odoo.http import request
import json

class MecatecController(http.Controller):

    def _response(self, data, status=200):
        return request.make_response(
            json.dumps(data),
            headers=[('Content-Type', 'application/json')],
            status=status
        )

    # --- Inventory Endpoints (Product Template) ---

    @http.route('/mecatec/api/inventory', type='http', auth='user', methods=['GET'], csrf=False)
    def get_inventory(self, **kwargs):
        # Using product.template
        inventory = request.env['product.template'].search([])
        data = [{
            'id': item.id,
            'name': item.name,
            'quantity': item.qty_available, # Standard field for quantity on hand
            'description': item.description_sale or '',
            'serial_number': item.default_code or '', # Using internal reference as serial for simplicity
            'price': item.list_price,
        } for item in inventory]
        return self._response({'status': 'success', 'data': data})

    @http.route('/mecatec/api/inventory', type='http', auth='user', methods=['POST'], csrf=False)
    def create_inventory(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            # Map custom fields to standard fields
            create_data = {
                'name': data.get('name'),
                'list_price': data.get('price'),
                'default_code': data.get('serial_number'),
                'type': 'product', # Storable product
            }
            new_item = request.env['product.template'].create(create_data)
            return self._response({'status': 'success', 'id': new_item.id}, status=201)
        except Exception as e:
            return self._response({'status': 'error', 'message': str(e)}, status=400)

    @http.route('/mecatec/api/inventory/<int:item_id>', type='http', auth='user', methods=['PUT'], csrf=False)
    def update_inventory(self, item_id, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            item = request.env['product.template'].browse(item_id)
            if not item.exists():
                return self._response({'status': 'error', 'message': 'Item not found'}, status=404)
            
            write_data = {}
            if 'name' in data: write_data['name'] = data['name']
            if 'price' in data: write_data['list_price'] = data['price']
            if 'serial_number' in data: write_data['default_code'] = data['serial_number']
            
            item.write(write_data)
            return self._response({'status': 'success', 'message': 'Item updated'})
        except Exception as e:
            return self._response({'status': 'error', 'message': str(e)}, status=400)

    @http.route('/mecatec/api/inventory/<int:item_id>', type='http', auth='user', methods=['DELETE'], csrf=False)
    def delete_inventory(self, item_id, **kwargs):
        try:
            item = request.env['product.template'].browse(item_id)
            if not item.exists():
                return self._response({'status': 'error', 'message': 'Item not found'}, status=404)
            item.unlink()
            return self._response({'status': 'success', 'message': 'Item deleted'})
        except Exception as e:
            return self._response({'status': 'error', 'message': str(e)}, status=400)

    # --- Maintenance Endpoints (Maintenance Request) ---

    @http.route('/mecatec/api/maintenance', type='http', auth='user', methods=['GET'], csrf=False)
    def get_maintenance(self, **kwargs):
        maintenance = request.env['maintenance.request'].search([])
        data = [{
            'id': m.id,
            'title': m.name, # Standard field
            'description': m.description,
            'date': str(m.request_date), # Standard field
            'status': m.stage_id.name if m.stage_id else 'New', # Using Stage name
            'mechanic_id': m.user_id.id if m.user_id else False, # Standard field
            'client_id': m.client_id.id if m.client_id else False, # Custom field
            'vehicle_id': m.vehicle_id.id if m.vehicle_id else False, # Custom field
        } for m in maintenance]
        return self._response({'status': 'success', 'data': data})

    @http.route('/mecatec/api/maintenance', type='http', auth='user', methods=['POST'], csrf=False)
    def create_maintenance(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            create_data = {
                'name': data.get('title'),
                'description': data.get('description'),
                'request_date': data.get('date'),
                'client_id': data.get('client_id'),
                'vehicle_id': data.get('vehicle_id'),
                'user_id': data.get('mechanic_id'),
            }
            new_m = request.env['maintenance.request'].create(create_data)
            return self._response({'status': 'success', 'id': new_m.id}, status=201)
        except Exception as e:
            return self._response({'status': 'error', 'message': str(e)}, status=400)

    @http.route('/mecatec/api/maintenance/<int:m_id>', type='http', auth='user', methods=['PUT'], csrf=False)
    def update_maintenance(self, m_id, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            m = request.env['maintenance.request'].browse(m_id)
            if not m.exists():
                return self._response({'status': 'error', 'message': 'Maintenance not found'}, status=404)
            
            write_data = {}
            if 'title' in data: write_data['name'] = data['title']
            if 'description' in data: write_data['description'] = data['description']
            if 'date' in data: write_data['request_date'] = data['date']
            if 'client_id' in data: write_data['client_id'] = data['client_id']
            if 'vehicle_id' in data: write_data['vehicle_id'] = data['vehicle_id']
            if 'mechanic_id' in data: write_data['user_id'] = data['mechanic_id']

            m.write(write_data)
            return self._response({'status': 'success', 'message': 'Maintenance updated'})
        except Exception as e:
            return self._response({'status': 'error', 'message': str(e)}, status=400)

    @http.route('/mecatec/api/maintenance/<int:m_id>', type='http', auth='user', methods=['DELETE'], csrf=False)
    def delete_maintenance(self, m_id, **kwargs):
        try:
            m = request.env['maintenance.request'].browse(m_id)
            if not m.exists():
                return self._response({'status': 'error', 'message': 'Maintenance not found'}, status=404)
            m.unlink()
            return self._response({'status': 'success', 'message': 'Maintenance deleted'})
        except Exception as e:
            return self._response({'status': 'error', 'message': str(e)}, status=400)

    # --- Vehicle Endpoints (Fleet Vehicle) ---

    @http.route('/mecatec/api/vehicle', type='http', auth='user', methods=['GET'], csrf=False)
    def get_vehicle(self, **kwargs):
        vehicles = request.env['fleet.vehicle'].search([])
        data = [{
            'id': v.id,
            'brand': v.brand_id.name if v.brand_id else '',
            'model': v.model_id.name if v.model_id else '',
            'year': v.model_year,
            'license_plate': v.license_plate,
            'vin': v.vin_sn,
            'owner_id': v.owner_id.id if v.owner_id else False,
        } for v in vehicles]
        return self._response({'status': 'success', 'data': data})

    @http.route('/mecatec/api/vehicle', type='http', auth='user', methods=['POST'], csrf=False)
    def create_vehicle(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            # Note: Brand and Model are relations in Fleet, simplified here for brevity
            # In a real app, you'd need to find/create brand_id and model_id
            create_data = {
                'license_plate': data.get('license_plate'),
                'vin_sn': data.get('vin'),
                'model_year': data.get('year'),
                'owner_id': data.get('owner_id'),
            }
            new_v = request.env['fleet.vehicle'].create(create_data)
            return self._response({'status': 'success', 'id': new_v.id}, status=201)
        except Exception as e:
            return self._response({'status': 'error', 'message': str(e)}, status=400)

    @http.route('/mecatec/api/vehicle/<int:v_id>', type='http', auth='user', methods=['PUT'], csrf=False)
    def update_vehicle(self, v_id, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            v = request.env['fleet.vehicle'].browse(v_id)
            if not v.exists():
                return self._response({'status': 'error', 'message': 'Vehicle not found'}, status=404)
            
            write_data = {}
            if 'license_plate' in data: write_data['license_plate'] = data['license_plate']
            if 'vin' in data: write_data['vin_sn'] = data['vin']
            if 'year' in data: write_data['model_year'] = data['year']
            if 'owner_id' in data: write_data['owner_id'] = data['owner_id']

            v.write(write_data)
            return self._response({'status': 'success', 'message': 'Vehicle updated'})
        except Exception as e:
            return self._response({'status': 'error', 'message': str(e)}, status=400)

    @http.route('/mecatec/api/vehicle/<int:v_id>', type='http', auth='user', methods=['DELETE'], csrf=False)
    def delete_vehicle(self, v_id, **kwargs):
        try:
            v = request.env['fleet.vehicle'].browse(v_id)
            if not v.exists():
                return self._response({'status': 'error', 'message': 'Vehicle not found'}, status=404)
            v.unlink()
            return self._response({'status': 'success', 'message': 'Vehicle deleted'})
        except Exception as e:
            return self._response({'status': 'error', 'message': str(e)}, status=400)

    # --- Appointment Endpoints (Custom Model) ---

    @http.route('/mecatec/api/appointment', type='http', auth='user', methods=['GET'], csrf=False)
    def get_appointment(self, **kwargs):
        appointments = request.env['mecatec.appointment'].search([])
        data = [{
            'id': a.id,
            'date': str(a.date),
            'client_id': a.client_id.id if a.client_id else False,
            'vehicle_id': a.vehicle_id.id if a.vehicle_id else False,
            'reason': a.reason,
            'status': a.status,
        } for a in appointments]
        return self._response({'status': 'success', 'data': data})

    @http.route('/mecatec/api/appointment', type='http', auth='user', methods=['POST'], csrf=False)
    def create_appointment(self, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            new_a = request.env['mecatec.appointment'].create(data)
            return self._response({'status': 'success', 'id': new_a.id}, status=201)
        except Exception as e:
            return self._response({'status': 'error', 'message': str(e)}, status=400)

    @http.route('/mecatec/api/appointment/<int:a_id>', type='http', auth='user', methods=['PUT'], csrf=False)
    def update_appointment(self, a_id, **kwargs):
        try:
            data = json.loads(request.httprequest.data)
            a = request.env['mecatec.appointment'].browse(a_id)
            if not a.exists():
                return self._response({'status': 'error', 'message': 'Appointment not found'}, status=404)
            a.write(data)
            return self._response({'status': 'success', 'message': 'Appointment updated'})
        except Exception as e:
            return self._response({'status': 'error', 'message': str(e)}, status=400)

    @http.route('/mecatec/api/appointment/<int:a_id>', type='http', auth='user', methods=['DELETE'], csrf=False)
    def delete_appointment(self, a_id, **kwargs):
        try:
            a = request.env['mecatec.appointment'].browse(a_id)
            if not a.exists():
                return self._response({'status': 'error', 'message': 'Appointment not found'}, status=404)
            a.unlink()
            return self._response({'status': 'success', 'message': 'Appointment deleted'})
        except Exception as e:
            return self._response({'status': 'error', 'message': str(e)}, status=400)
