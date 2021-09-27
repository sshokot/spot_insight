from odoo import api, models, fields
from threading import Thread
import datetime
import pdb
import json
import pytz
from threading import Thread

class EtlSpotRawData(models.Model):
    _name = 'etl.spot.raw.data'
    _description = 'Model for ETL spot raw data to spot storage data'

    record_amount = fields.Integer(string='Records amount')
    tv_media_list = fields.Char('List of TV media')
    read_time = fields.Char()

    def get_raw_data_for_etl(self, model_name,check_field, filter_by_media=''):
        with api.Environment.manage():
            new_cur = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cur))
            rawModel = self.env[model_name]
            search_domain = [(check_field,'=',False)]
            if filter_by_media:
                search_domain = ['&',(check_field,'=',False),('spot_tv_company','ilike',filter_by_media.encode('utf-8'))]

            raw_recs = rawModel.search(search_domain)
            new_cur.commit()
            new_cur.close()
            return raw_recs

    def convert_to_user_tz(self, utc_datetime):
        fmt = '%Y-%m-%d %H:%M:%S'
        #pdb.set_trace()
        user_tz = pytz.timezone(self.env.user.tz)
        #return pytz.utc.localize(utc_datetime,is_dst=None).astimezone(user_tz).strftime(fmt)
        return utc_datetime.astimezone(user_tz)

    def check_raw_records(self):
        #pdb.set_trace()

#        raw_recs = self.get_raw_data_for_etl('spot.raw.data','spot_storage_id')
        rawModel = self.env['spot.raw.data']
        search_domain = [('spot_storage_id','=',False)]
        raw_recs = rawModel.search(search_domain)

        self.record_amount = len(raw_recs)
        self.tv_media_list = list(set(raw_recs.mapped('spot_tv_company')))

    def get_model_record(self, model_name, search_val):
        search_model = self.env[model_name]
        recs = search_model.search([('name','ilike',search_val)])
        if not recs:
            recs = search_model.create({'name':search_val})
        return recs[0].id

    def etl_spot_raw_data(self, tv_company):
  # spot.raw.model: spot_tv_company - [model_name,field_in_storage], release_date, spot_start_time,
  #     spot_end_time, spot_duration, advertiser, brand, model_name, article_level, clip_description, program ,
  #     spot_cost, break_title, spot_position, spots_count, total_ind, all_18, all_6_54
  #  and find budget data and add to storagge_data
        with api.Environment.manage():
            new_cr = self.pool.cursor()
            self = self.with_env(self.env(cr=new_cr))
            import_raw_m = self.env['import.raw.data.wizard']
            record_setting = {'spot_tv_company':['spot.tv.company','tv_company'], 'release_date':['date','release_date'], 'spot_start_time':['string','spot_start_time'],
                'spot_end_time':['string','spot_end_time'],'spot_duration':['number','duration'], 'spot_cost':['number','spot_cost'], 'break_title':['inner.block.type','inner_block_type'],
                'spot_position':['number','spot_position'], 'spots_count':['number','spot_count']}
            prime_type = ['string', 'number', 'date']
            storage_model = self.env['spot.storage.data']
            a_holding = 'advertise_holding'
            a_mbagency = 'media_buying_agency'
#            print('SEARCH in ',tv_company)
            map_model = self.env['spot.map.adv.brand.procat']
            rawModel = self.env['spot.raw.data']
            spot_tv_model = self.env['spot.tv.company']
            search_domain = ['&',('spot_storage_id','=',False),('spot_tv_company','ilike',tv_company)]
            raw_recs = rawModel.search(search_domain)
            grp_model = self.env['spot.overall.rating.grp']
            spot_audience_model_name = 'spot.audience'
            audience_6 = self.get_model_record(spot_audience_model_name, '6+')
            audience_18 = self.get_model_record(spot_audience_model_name, '18+')
            audience_6_54 = self.get_model_record(spot_audience_model_name, '6-54')

 #           print('', tv_company,' recs = ',len(raw_recs))
            i = 0; vals = []; str_error = ''
            for raw_rec in raw_recs:
                i+=1;
                rec_vals = {'spot_raw_id':raw_rec.id}
                for k, v in record_setting.items():
                    cur_val = raw_rec[k]
                    type_name = v[0]
                    field_name = v[1]
                    if type_name in prime_type:
                        rec_vals[field_name] = cur_val
                    else:
                        rec_vals[field_name] = self.get_model_record(type_name, cur_val)
                rec_vals['budget_vat_less'] = self.get_budget_for_spot(raw_rec.spot_tv_company, raw_rec.release_date, raw_rec.spot_start_time, raw_rec.spot_end_time)
                standart = map_model.get_standart(raw_rec.advertiser, raw_rec.brand, raw_rec.article_level)
                if standart:
                    rec_vals['advertiser'] = standart[0].advertiser.id
                    rec_vals['brand'] = standart[0].brand.id
                    rec_vals['product_category'] = standart[0].product_category.id
                import_raw_m.check_records(storage_model, rec_vals, vals, str_error)
                rec_tv_company = spot_tv_model.browse(rec_vals['tv_company'])
                rec_vals['media_seller'] = rec_tv_company.media_seller.id
                rec_vals['into_prime_time'] = rec_tv_company.check_in_prime_time(rec_vals['spot_start_time'])
                rec_vals['budget_vat'] = rec_tv_company.get_budget_vat(rec_vals['budget_vat_less'])
                if rec_vals['advertiser']:
                    advert_id = rec_vals['advertiser']
                    release_date = rec_vals['release_date']
                    advertiser_m = self.env['spot.advertiser']
                    rec_vals[a_holding] = advertiser_m.get_advertise_holding(release_date, advert_id)
                    rec_vals[a_mbagency] = advertiser_m.get_media_buying_agency(release_date, advert_id)
#                if raw_rec['advertise_holding']:
#                    adver_holding = self.get_model_record('spot.advertise.holding', raw_rec[a_holding])
#                    if adver_holding and adver_holding <> rec_vals[a_holding]:
#                        rec_vals[a_holding] = advertiser_m.set_advertise_holding(release_date, advert_id, adver_holding)
#            import_raw_m.check_records(storage_model, rec_vals, vals, str_error)
#                if i>3:break
            if vals:
                new_recs = storage_model.create(vals)
                for new_rec in new_recs:
                    storage_id = new_rec.id
                    raw_recs = rawModel.search([('id','=',new_rec.spot_raw_id.id)])
                    for raw_rec in raw_recs:
#                       pdb.set_trace()
                        grp_model.set_grp_rating(storage_id, audience_6, raw_rec.total_ind)
                        grp_model.set_grp_rating(storage_id, audience_18, raw_rec.all_18)
                        grp_model.set_grp_rating(storage_id, audience_6_54, raw_rec.all_6_54)
            new_cr.commit()
            new_cr.close()

    def get_budget_for_spot(self, tv_company, release_date, start_time, end_time):
        budget_cost = 0
#        pdb.set_trace()
        budget_model = self.env['budget.raw.data']
        raw_imp_model = self.env['import.raw.data.wizard']
        what_budget = ['&',('spot_tv_company', 'ilike', tv_company),('release_date','=', release_date)]
        what_budget.append(('fact_start_time', '>=', start_time))
        what_budget.append(('fact_start_time', '<', end_time))
        find_budget = budget_model.search(what_budget)
#        print('FIND v1',what_budget,find_budget)
        if find_budget:
            budget_cost = find_budget[0].budget_vat_less
        return budget_cost

    def etl_by_media(self):
        self.ensure_one()
        full_read_time = 'START '+fields.Datetime.now().strftime("%d/%m/%Y,%H:%M:%S")
#        pdb.set_trace()
        list_media = []
        if self.tv_media_list:
            list_media = json.loads(self.tv_media_list.replace('\'','\"'))
        allThread = []
        print(list_media)
        for media in list_media:
            new_thr = Thread(target=self.etl_spot_raw_data,args=(media,))
            new_thr.start()
            allThread.append(new_thr)
        if allThread:
            for thr in allThread:
                thr.join()
        full_read_time += ' - END '+fields.Datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
        self.write({'read_time': full_read_time})

    def test_read(self):
        self.ensure_one()
        full_read_time = 'START '+fields.Datetime.now().strftime("%d/%m/%Y,%H:%M:%S")
#        pdb.set_trace()
        list_media = []
        if self.tv_media_list:
            list_media = json.loads(self.tv_media_list.replace('\'','\"'))
        print(list_media)
        for media in list_media:
            self.etl_spot_raw_data(media)
            break
        full_read_time += ' - END '+fields.Datetime.now().strftime('%d/%m/%Y, %H:%M:%S')
        print(full_read_time)

    def clear_env_caches(self):
        self.invalidate_cache()
