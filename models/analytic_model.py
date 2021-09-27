from odoo import api,models,fields
from odoo import tools

class BudgetVolume(models.Model):
    _name = 'spot.budget.volume'
    _description = 'Model for Budget Volume Analytic report'
    _auto = False
    _auto_search = False

#    period_month = fields.Many2one('period.month', readonly=True)
#    period_year = fields.Many2one('period.year', readonly=True)
    period_month = fields.Many2one('period.month', readonly=True)
    period_year = fields.Many2one('period.year', readonly=True)
    tv_company = fields.Many2one('spot.tv.company', readonly=True)
   # month_status = fields.Char(string='Month status', readonly=True)
    budget_volume = fields.Float(string='Budget Volume (vat less)', readonly=True, digits=(15,2))
    volume_dynamic = fields.Float(string='Volume Dynamic', readonly=True, digits=(5,2))

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        query = """
        CREATE OR REPLACE VIEW spot_budget_volume AS (
        SELECT
            coalesce(min(vlm_data.id)) as id,
            vlm_data.tv_company as tv_company,
            years.id as period_year,
            months.id as period_month,
            sum(vlm_data.budget_vat_less) as budget_volume,
            sum(0) as volume_dynamic
        FROM spot_storage_data as  vlm_data
            LEFT JOIN period_year AS years ON  date_trunc('year', vlm_data.release_date) = years.begin_date
            LEFT JOIN period_month AS months ON date_part('month',vlm_data.release_date) = months.number_in_year
        GROUP BY vlm_data.tv_company, period_year, period_month
        );
        """
        self.env.cr.execute(query)
