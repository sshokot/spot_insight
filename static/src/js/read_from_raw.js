odoo.define('read_from_raw_action_button', function(require) {
 "use strict;"
 var core = require('web.core');
 var ListController = require('web.ListController');
 var rpc = require('web.rpc');
 var session = require('web.session');
 var _t = core._t;
// var thePopup = window.open("url", "Read From RAW", "menubar=0,location=0,height=700,width=700" );
//    thePopup.print();
 //   var $btnReadRaw = $(qweb.render('read_raw_button'));
//   $btnReadRaw.on('click', this._read_from_raw_def.bind(this));
//   this.$buttons.prepend($btnReadRaw)
//  },
//  _read_from_raw_def:function(){
//   var self = this;
//   var user = session.uid;
//   var res = rpc.query({
//     model:'spot.storage.data',
//     method: 'read_from_raw_data',
//     args:[[]]
//   }).then(function(){console.log('read from raw');});
//   },
//  });
// return ListController;

 ListController.include({
    renderButtons: function($node){
       this._super.apply(this, arguments);
       if (this.$buttons){
          this.$buttons.find('.o_list_read_raw_button').click(this.proxy('action_def'));
        }
     },
    action_def: function(e){
       var self = this;
       this._rpc({
          model: 'spot.storage.data',
          method: 'read_from_raw_data',
          args:[""],
         }).then(function (result){
            self.do_action(result);
        });
     },
});
});
