from odoo import http, _, fields
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from dateutil.relativedelta import relativedelta
from babel.dates import format_date

class PodiumCustomerPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id
        
        # Athletes where the user is the representative OR the user is the athlete themselves
        domain = ['|', ('representative_id', '=', partner.id), ('partner_id', '=', partner.id)]
        values['athlete_count'] = request.env['podium.athlete'].search_count(domain)
        
        # Payments for athletes related to this user
        athletes = request.env['podium.athlete'].search(['|', ('representative_id', '=', partner.id), ('partner_id', '=', partner.id)])
        values['payment_count'] = request.env['podium.payment'].search_count([('athlete_id', 'in', athletes.ids)])
        
        # Attendance lines for athletes related to this user
        values['attendance_count'] = request.env['podium.attendance.line'].search_count([('athlete_id', 'in', athletes.ids)])
            
        return values

    @http.route(['/my/athletes', '/my/athletes/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_athletes(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        PodiumAthlete = request.env['podium.athlete']
        
        domain = ['|', ('representative_id', '=', partner.id), ('partner_id', '=', partner.id)]

        athlete_count = PodiumAthlete.search_count(domain)
        pager = portal_pager(
            url="/my/athletes",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=athlete_count,
            page=page,
            step=self._items_per_page
        )
        
        athletes = PodiumAthlete.search(domain, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'athletes': athletes,
            'page_name': 'athlete',
            'default_url': '/my/athletes',
            'pager': pager,
        })
        return request.render("ag_podium_base.portal_my_athletes", values)

    @http.route(['/my/payments', '/my/payments/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_payments(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        PodiumPayment = request.env['podium.payment']
        
        athletes = request.env['podium.athlete'].search(['|', ('representative_id', '=', partner.id), ('partner_id', '=', partner.id)])
        domain = [('athlete_id', 'in', athletes.ids)]

        payment_count = PodiumPayment.search_count(domain)
        pager = portal_pager(
            url="/my/payments",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=payment_count,
            page=page,
            step=self._items_per_page
        )
        
        payments = PodiumPayment.search(domain, limit=self._items_per_page, offset=pager['offset'])
        
        values.update({
            'payments': payments,
            'page_name': 'payment',
            'default_url': '/my/payments',
            'pager': pager,
        })
        return request.render("ag_podium_base.portal_my_payments", values)

    @http.route(['/my/attendances', '/my/attendances/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_attendances(self, page=1, date_begin=None, date_end=None, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        PodiumAttendanceLine = request.env['podium.attendance.line']
        
        athletes = request.env['podium.athlete'].search(['|', ('representative_id', '=', partner.id), ('partner_id', '=', partner.id)])
        domain = [('athlete_id', 'in', athletes.ids)]

        attendance_count = PodiumAttendanceLine.search_count(domain)
        pager = portal_pager(
            url="/my/attendances",
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
            total=attendance_count,
            page=page,
            step=self._items_per_page
        )
        
        attendances = PodiumAttendanceLine.search(domain, limit=self._items_per_page, offset=pager['offset'], order='date desc')
        
        values.update({
            'attendances': attendances,
            'page_name': 'attendance',
            'default_url': '/my/attendances',
            'pager': pager,
        })
        return request.render("ag_podium_base.portal_my_attendances", values)

    @http.route(['/club/dashboard'], type='http', auth="user", website=True)
    def club_dashboard(self, **kw):
        partner = request.env.user.partner_id
        
        # Get Athletes
        athletes = request.env['podium.athlete'].sudo().search(['|', ('representative_id', '=', partner.id), ('partner_id', '=', partner.id)])
        
        # Recent Payments (last 5)
        payments = request.env['podium.payment'].sudo().search([('athlete_id', 'in', athletes.ids)], order='date desc', limit=5)
        
        # Financial Status Calculation
        today = fields.Date.today()
        missing_payments = []
        
        for athlete in athletes:
            # Start from creation date (first of that month)
            if not athlete.create_date:
                continue
                
            start_date = athlete.create_date.date().replace(day=1)
            current_check_date = start_date
            
            # Iterate months until today
            while current_check_date <= today:
                month_str = current_check_date.strftime('%m')
                year_int = current_check_date.year
                
                # Check if PAID payment exists for this month/year
                payment_exists = request.env['podium.payment'].sudo().search_count([
                    ('athlete_id', '=', athlete.id),
                    ('month', '=', month_str),
                    ('year', '=', year_int),
                    ('state', '=', 'paid')
                ])
                
                if not payment_exists:
                    is_current = (current_check_date.year == today.year and current_check_date.month == today.month)
                    month_name = format_date(current_check_date, format='MMMM Y', locale=request.env.context.get('lang') or 'es_ES')
                    
                    missing_payments.append({
                        'athlete_name': athlete.name,
                        'date': current_check_date,
                        'month_name': month_name.capitalize(),
                        'is_current': is_current
                    })
                
                current_check_date += relativedelta(months=1)
        
        # Upcoming Payments (Draft payments in future)
        upcoming_payments = request.env['podium.payment'].sudo().search([
            ('athlete_id', 'in', athletes.ids),
            ('state', '=', 'draft'),
            ('date', '>=', today)
        ], order='date asc', limit=3)
        
        # Recent Attendance (last 5)
        attendances = request.env['podium.attendance.line'].sudo().search([('athlete_id', 'in', athletes.ids)], order='date desc', limit=5)
        
        values = {
            'partner': partner,
            'athletes': athletes,
            'payments': payments,
            'missing_payments': missing_payments,
            'upcoming_payments': upcoming_payments,
            'attendances': attendances,
            'athlete_count': len(athletes),
        }
        return request.render("ag_podium_base.club_dashboard", values)
