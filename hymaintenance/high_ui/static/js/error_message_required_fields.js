var ERROR_MESSAGE_REQUIRED_FIELDS = ERROR_MESSAGE_REQUIRED_FIELDS || (function(){
    var _args = {}; // private

    return {
        init : function(Args) {
            _args = Args;
        },
        ErrorMessageRequiredFields : function() {
            var RequiredFields = document.querySelectorAll("[required]");
            for (var j = 0; j < RequiredFields.length; ++j) {
                RequiredFields[j].oninvalid = function(event){
                    this.setCustomValidity(_args[0])
                };
                RequiredFields[j].onchange = function(event){
                    this.setCustomValidity("")
                };
            }
        }
    };
}());
