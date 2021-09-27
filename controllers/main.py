from odoo import http
from odoo.http import request

class Main(http.Controller):

    @http.route('/brands', type='http', autho='user', website=True)
    def brands(self):
        return request.render('spot_insight.brands', {'brands': request.env['spot.brand'].search([])})
