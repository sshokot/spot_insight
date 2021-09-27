from odoo import fields, api, models

class SpotRawData(models.Model):
    _name = 'spot.raw.data'
    _description = 'model for spot raw data'

    spot_storage_id = fields.One2many('spot.storage.data','spot_raw_id', string='spot storage id')
    spot_tv_company = fields.Char(string='Spot TV Company')
    release_date = fields.Date(string='Release Date')
    spot_start_time = fields.Datetime(string='Spot start time')
    spot_end_time = fields.Datetime(string='Spot end time')
    spot_duration = fields.Char(string='Spot duration')
    advertiser = fields.Char()
    brand = fields.Char()
    model_name = fields.Char(string="Model")
    article_level = fields.Char(string='Article level')
    clip_description = fields.Char(string="Clip Description")
    program = fields.Char()
    spot_cost = fields.Float(string='Spot Cost', digits=(7, 2))
    break_title = fields.Char(string='Break Title')
    spot_position = fields.Float(string='Spot Position', digits=(7, 2))
    spots_count = fields.Float(string='Spots Count', digits=(7, 2))
    total_ind  = fields.Float(string='TotalInd', digits=(7, 3))
    all_18 = fields.Float(string='All 18+', digits=(7, 3))
    all_6_54 = fields.Float(string='All 6-54', digits=(7, 3))


class BudgetRawData(models.Model):
    _name = 'budget.raw.data'
    _description = 'model for budget raw data'

    release_date = fields.Date(string='Release Date')
    spot_tv_company = fields.Char(string='Spot TV Company')
    time_keeping = fields.Float(string='Timekeeping', digits=(7, 2))
    budget_vat_less = fields.Float(string='Budget VAT less', digits=(12,2))
    fact_start_time = fields.Datetime(string='Fact Start Time')


class AudienceIndicatorRawData(models.Model):
    _name = 'audience.indicator.raw.data'
    _description = 'model for audience indicators raw data'

    data_date = fields.Date(string='Date')
    spot_tv_company = fields.Char(string='Spot TV Company')
    rtg6 = fields.Float(string='Rtg% 6+', digits=(7, 3))
    rtg6_54 = fields.Float(string='Rtg% 6-54', digits=(7, 3))
    rtg18 = fields.Float(string='Rtg% 18+', digits=(7, 3))
    share6 = fields.Float(string='Share% 6+', digits=(7, 3))
    share6_54 = fields.Float(string='Share% 6-54', digits=(7, 3))
    share18 = fields.Float(string='Share% 18+', digits=(7, 3))


class OpenInventoryRawData(models.Model):
    _name = 'open.inventory.raw.data'
    _description = 'model for open inventory raw data'

    data_date = fields.Date(string='Date')
    spot_tv_company = fields.Char(string='Spot TV Company')
    start_time = fields.Char(string='Start Time')
    end_time = fields.Char(string='End Time')
    total_ind  = fields.Float(string='TotalInd', digits=(7, 3))
    all_18 = fields.Float(string='All 18+', digits=(7, 3))
    all_6_54 = fields.Float(string='All 6-54', digits=(7, 3))
