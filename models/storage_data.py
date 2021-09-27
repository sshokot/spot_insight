from odoo import api, models, fields
import logging

_loger = logging.getLogger(__name__)

class SpotStorageData(models.Model):
    _name = 'spot.storage.data'
    _description = 'Model for spot storage data'

    release_date = fields.Date(string='Release date')
    tv_company = fields.Many2one('spot.tv.company', string='TV Company')
    spot_start_time = fields.Char('Spot Start Time')
    spot_end_time = fields.Char('Spot End Time')
    duration = fields.Char(string='Duration')
    advertiser = fields.Many2one('spot.advertiser', string='Advertiser')
    brand = fields.Many2one('spot.brand', string='Brand')
    product_category = fields.Many2one('spot.product.category',string='Product Category')
    is_zero_budget = fields.Boolean(string='Is zero budget?')
    advertise_holding = fields.Many2one('spot.advertise.holding', string='Advertise Holding')
    media_buying_agency = fields.Many2one('spot.media.buying.agency', string='Media Buying Agency')
    media_seller = fields.Many2one('spot.media.seller', string='Media Seller')
    inner_block_type = fields.Many2one('inner.block.type', string='Inner Block Type')
    into_prime_time = fields.Boolean(string='Into Prime Time')
    spot_cost = fields.Float(string='Spot Cost')
    spot_position = fields.Float(string='Spot Position', digits=(7, 2))
    spot_count = fields.Float(string='Spots Count', digits=(7, 2))
    budget_vat_less = fields.Float(string='Budget VAT less', digits=(12, 2))
    budget_vat = fields.Float(string='Budget VAT', digits=(12, 2))
    spot_raw_id = fields.Many2one('spot.raw.data', string='spot raw id', ondelete='set null')

    def read_from_raw_data(self):
        _loger.info('HERE WILL BE READING FROM RAW DATA')


class SpotOverallRatingGRP(models.Model):
    _name = 'spot.overall.rating.grp'
    _description = 'Model for Over Rating GRP'

    id_storage_data = fields.Many2one('spot.storage.data', string='ID Storage Data')
    audience = fields.Many2one('spot.audience', string='Audience')
    rating_grp = fields.Float(string='GRP', digits=(7,4))

    @api.model
    def set_grp_rating(self, storage_id, audience, rating):
        grp_model = self.env['spot.overall.rating.grp']
        import_raw_m = self.env['import.raw.data.wizard']
        vals = []; str_error = ''
        rec_val = {'id_storage_data':storage_id, 'audience':audience, 'rating_grp': rating}
        import_raw_m.check_records(grp_model, rec_val, vals, str_error)
        if vals:
            grp_model.create(vals)


class SpotOpenInventoryValue(models.Model):
    _name = 'spot.open.inventory.value'
    _description = 'Model for Open Inventory Values'

    date_month = fields.Date('Month')
    tv_company = fields.Many2one('spot.tv.company', string='TV Company')
    audience = fields.Many2one('spot.audience', string='Audience')
    value = fields.Float(string='Value', digits=(7, 3))
